"""
Signal channel adapter via signal-cli REST API.

Communicates with the bbernhard/signal-cli-rest-api container over HTTP.
The container exposes a REST API on port 8080 (mapped to 8082 on the
host in compose.yaml). Key endpoints:

  GET  /v1/receive/<number>   — fetch queued messages
  POST /v2/send               — send a message
  GET  /v1/about              — health check / version info

This replaces the earlier subprocess-based adapter. The REST API is the
correct integration path when signal-cli runs inside the pod.

Signal serves two purposes:
1. As a notification/command channel to the owner (human-in-the-loop)
2. As a general messaging channel (future: group monitoring)

Commands from the owner:
  APPROVE <action_id>  — approve a pending action
  DENY <action_id>     — deny a pending action
  STATUS               — show daemon status
  TASKS                — list pending tasks
  HELP                 — show available commands
"""

import json
import logging
from datetime import datetime
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import (
    BaseChannel,
    ChannelType,
    InboundMessage,
    OutboundMessage,
)
from ..config import SignalConfig

logger = logging.getLogger(__name__)


class SignalChannel(BaseChannel):
    """Signal adapter using signal-cli REST API."""

    channel_type = ChannelType.SIGNAL

    def __init__(self, config: SignalConfig):
        self.config = config
        self._base_url = config.api_url.rstrip("/")

    # ── HTTP helpers ───────────────────────────────────────────────────

    def _get(self, path: str, timeout: int = 10) -> Optional[dict | list]:
        """
        HTTP GET request to the signal-cli REST API.

        Returns parsed JSON on success, None on failure.
        """
        url = f"{self._base_url}{path}"
        logger.debug("GET %s", url)
        try:
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                if not body:
                    return []
                return json.loads(body)
        except HTTPError as exc:
            logger.error("Signal API HTTP error: %s %s", exc.code, exc.reason)
            return None
        except URLError as exc:
            logger.error("Signal API connection error: %s", exc.reason)
            return None
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Signal API error: %s", exc)
            return None

    def _post(self, path: str, payload: dict, timeout: int = 10) -> Optional[dict]:
        """
        HTTP POST request to the signal-cli REST API.

        Returns parsed JSON on success, None on failure.
        """
        url = f"{self._base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        logger.debug("POST %s %s", url, payload)
        try:
            req = Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                method="POST",
            )
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                if not body:
                    return {}
                return json.loads(body)
        except HTTPError as exc:
            logger.error("Signal API HTTP error: %s %s", exc.code, exc.reason)
            return None
        except URLError as exc:
            logger.error("Signal API connection error: %s", exc.reason)
            return None
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Signal API error: %s", exc)
            return None

    # ── Channel interface ──────────────────────────────────────────────

    def poll(self) -> list[InboundMessage]:
        """
        Receive pending messages from Signal.

        Uses GET /v1/receive/<number> which downloads and returns any
        queued messages from the Signal server.
        """
        result = self._get(f"/v1/receive/{self.config.account}")
        if not result or not isinstance(result, list):
            return []

        messages = []
        for envelope_wrapper in result:
            msg = self._parse_message(envelope_wrapper)
            if msg is not None:
                messages.append(msg)

        if messages:
            logger.info("Received %d Signal messages", len(messages))
        return messages

    def _parse_message(self, data: dict) -> Optional[InboundMessage]:
        """Parse a signal-cli REST API message envelope."""
        envelope = data.get("envelope", {})
        if not envelope:
            return None

        # Only process data messages (not receipts, typing indicators, etc.)
        data_msg = envelope.get("dataMessage")
        if not data_msg:
            return None

        body = data_msg.get("message", "")
        if not body:
            return None

        sender = envelope.get("source", "")
        timestamp_ms = envelope.get("timestamp", 0)
        timestamp = (
            datetime.fromtimestamp(timestamp_ms / 1000)
            if timestamp_ms
            else datetime.now()
        )

        # Group messages
        group_info = data_msg.get("groupInfo", {})
        group_id = group_info.get("groupId", "")

        return InboundMessage(
            channel=ChannelType.SIGNAL,
            sender=sender,
            subject="",  # Signal doesn't have subjects
            body=body,
            timestamp=timestamp,
            message_id=f"signal-{timestamp_ms}",
            thread_id=group_id or None,
            raw=data,
        )

    def send(self, message: OutboundMessage) -> bool:
        """Send a Signal message via POST /v2/send."""
        payload = {
            "message": message.body,
            "number": self.config.account,
            "recipients": [message.recipient],
        }
        result = self._post("/v2/send", payload)
        if result is not None:
            logger.info("Signal message sent to %s", message.recipient)
            return True
        return False

    def send_to_owner(self, text: str) -> bool:
        """Convenience: send a message to the daemon owner."""
        if not self.config.owner_number:
            logger.error("No owner number configured for Signal")
            return False
        msg = OutboundMessage(
            channel=ChannelType.SIGNAL,
            recipient=self.config.owner_number,
            subject="",
            body=text,
        )
        return self.send(msg)

    def notify(self, summary: str, action_id: Optional[str] = None) -> bool:
        """
        Send a notification to the owner with optional action prompt.

        If action_id is provided, appends approval instructions.
        """
        text = summary
        if action_id:
            text += (
                f"\n\nReply APPROVE {action_id} or DENY {action_id}"
            )
        return self.send_to_owner(text)

    def is_available(self) -> bool:
        """Check if the signal-cli REST API is reachable and account is configured."""
        if not self.config.account:
            return False
        # Hit the about endpoint as a health check
        result = self._get("/v1/about", timeout=5)
        return result is not None

    def is_owner_message(self, msg: InboundMessage) -> bool:
        """Check if a message is from the daemon owner."""
        return msg.sender == self.config.owner_number

    def parse_command(self, body: str) -> tuple[str, list[str]]:
        """
        Parse a command from the owner.

        Returns (command, args) tuple. Command is uppercased.
        E.g. "APPROVE abc123" -> ("APPROVE", ["abc123"])
        """
        parts = body.strip().split()
        if not parts:
            return ("", [])
        return (parts[0].upper(), parts[1:])
