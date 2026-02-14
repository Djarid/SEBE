"""
LLM client for local llama-server with model swapping.

Only one model runs at a time on port 8080. The ModelManager handles
stopping/starting systemd user services to swap between Qwen3 (triage)
and gpt-oss-120b (substance).

No dependency on the openai library; uses urllib from stdlib.
"""

import json
import logging
import subprocess
import time
import urllib.request
import urllib.error
from typing import Optional

from .config import LLMConfig, LLMModel

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for the local llama-server endpoint."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._cached_model_id: Optional[str] = None

    def _detect_model_id(self) -> str:
        """Query /v1/models to get the currently loaded model ID."""
        url = f"{self.config.base_url}/models"
        try:
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {self.config.api_key}")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                models = data.get("data", [])
                if models:
                    return models[0]["id"]
        except Exception as e:
            logger.warning("Could not detect model from %s: %s", url, e)
        return "unknown"

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """
        Send a chat completion request to the active model.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            system_prompt: Optional system prompt (prepended to messages).

        Returns:
            Full API response as a dict.
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        model_id = self._detect_model_id()

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        url = f"{self.config.base_url}/chat/completions"
        body = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.config.api_key}")

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            logger.error(
                "LLM request failed: %s %s - %s", e.code, e.reason, error_body
            )
            raise
        except urllib.error.URLError as e:
            logger.error("LLM connection failed (%s): %s", url, e.reason)
            raise

    def chat_simple(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Send a single user message, return the assistant's text."""
        messages = [{"role": "user", "content": user_message}]
        response = self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )
        choices = response.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    def is_available(self) -> bool:
        """Check if the llama-server endpoint is reachable."""
        url = f"{self.config.base_url}/models"
        try:
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {self.config.api_key}")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False


class ModelManager:
    """
    Manages model swapping via systemd user services.

    Only one model runs at a time. The default model (Qwen3) is the
    always-on triage model. When substance work is needed, the manager:
      1. Stops the triage model
      2. Starts the substance model
      3. Waits for the API to become ready
      4. Yields control for the LLM request
      5. Stops the substance model
      6. Restarts the triage model

    This is exposed as a context manager for clean usage:

        with model_manager.use("oss120"):
            response = client.chat_simple("draft a policy response")

    In container environments where systemctl is unavailable, the manager
    operates in passthrough mode: it skips systemd commands and just
    checks whether the external LLM API is reachable. Model swapping is
    not supported in passthrough mode (the host manages the model).
    """

    def __init__(self, config: LLMConfig, client: LLMClient):
        self.config = config
        self.client = client
        self._active_model: Optional[str] = None
        self._has_systemctl = self._check_systemctl()
        if not self._has_systemctl:
            logger.info(
                "systemctl not available; model manager running in "
                "passthrough mode (LLM managed externally)"
            )

    @staticmethod
    def _check_systemctl() -> bool:
        """Return True if systemctl is available on this system."""
        import shutil
        return shutil.which("systemctl") is not None

    @property
    def active_model(self) -> Optional[str]:
        """Return the key of the currently active model, or None."""
        return self._active_model

    def _systemctl(self, action: str, unit: str) -> bool:
        """Run systemctl --user <action> <unit>. Returns True on success."""
        if not self._has_systemctl:
            logger.debug(
                "Skipping systemctl %s %s (passthrough mode)", action, unit
            )
            return True
        cmd = ["systemctl", "--user", action, unit]
        logger.info("Running: %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                logger.error(
                    "systemctl %s %s failed (rc=%d): %s",
                    action, unit, result.returncode, result.stderr.strip()
                )
                return False
            return True
        except subprocess.TimeoutExpired:
            logger.error("systemctl %s %s timed out", action, unit)
            return False

    def _wait_for_ready(self, timeout: Optional[float] = None) -> bool:
        """Poll the API until it responds or timeout is reached."""
        timeout = timeout or self.config.swap_timeout
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if self.client.is_available():
                return True
            time.sleep(1.0)
        return False

    def _wait_for_stopped(self, timeout: float = 15.0) -> bool:
        """Wait until the API stops responding."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            if not self.client.is_available():
                return True
            time.sleep(0.5)
        return False

    def ensure_model(self, model_key: str) -> bool:
        """
        Ensure the specified model is running.

        If it's already the active model and the API is responding, no-op.
        Otherwise, stop whatever is running and start the requested model.

        In passthrough mode (no systemctl), just verify the API is reachable.
        Model swapping is not supported in passthrough mode.

        Returns True if the model is ready, False on failure.
        """
        model = self.config.models.get(model_key)
        if model is None:
            logger.error("Unknown model key: %s", model_key)
            return False

        # Passthrough mode: skip systemd, just check API
        if not self._has_systemctl:
            if self.client.is_available():
                self._active_model = model_key
                logger.info(
                    "Model %s assumed active (passthrough mode, API reachable)",
                    model_key,
                )
                return True
            else:
                logger.warning(
                    "LLM API not reachable at %s (passthrough mode)",
                    self.config.base_url,
                )
                return False

        # Already running the right model?
        if self._active_model == model_key and self.client.is_available():
            logger.debug("Model %s already active", model_key)
            return True

        # Stop whatever is currently running
        if self._active_model is not None:
            current = self.config.models[self._active_model]
            logger.info(
                "Stopping %s (%s) to swap to %s",
                self._active_model, current.systemd_unit, model_key
            )
            self._systemctl("stop", current.systemd_unit)
            self._wait_for_stopped()
        else:
            # Nothing tracked as active, but something might be running.
            # Stop all known models to be safe.
            for key, m in self.config.models.items():
                self._systemctl("stop", m.systemd_unit)
            self._wait_for_stopped(timeout=10.0)

        # Start the requested model
        self._active_model = None
        logger.info("Starting %s (%s)", model_key, model.systemd_unit)
        if not self._systemctl("start", model.systemd_unit):
            return False

        # Wait for initial startup
        time.sleep(model.startup_wait)

        # Wait for API readiness
        if self._wait_for_ready():
            self._active_model = model_key
            logger.info("Model %s is ready", model_key)
            return True
        else:
            logger.error(
                "Model %s did not become ready within %.0fs",
                model_key, self.config.swap_timeout
            )
            return False

    def ensure_default(self) -> bool:
        """Ensure the default (triage) model is running."""
        return self.ensure_model(self.config.default_model)

    def use(self, model_key: str) -> "_ModelContext":
        """
        Context manager for temporarily using a specific model.

        Usage:
            with manager.use("oss120"):
                response = client.chat_simple("draft something")
            # Default model is automatically restored after the block.
        """
        return _ModelContext(self, model_key)

    def status(self) -> dict:
        """Return current model status."""
        return {
            "active_model": self._active_model,
            "api_available": self.client.is_available(),
            "default_model": self.config.default_model,
        }


class _ModelContext:
    """Context manager for temporary model swaps."""

    def __init__(self, manager: ModelManager, model_key: str):
        self.manager = manager
        self.model_key = model_key
        self._previous_model: Optional[str] = None

    def __enter__(self):
        self._previous_model = self.manager.active_model
        if not self.manager.ensure_model(self.model_key):
            raise RuntimeError(
                f"Failed to start model: {self.model_key}"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous model (or default)
        restore_to = self._previous_model or self.manager.config.default_model
        if restore_to != self.model_key:
            self.manager.ensure_model(restore_to)
        return False  # Don't suppress exceptions
