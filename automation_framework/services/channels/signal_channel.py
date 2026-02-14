"""
Signal channel adapter via signal-cli.

signal-cli can run in JSON-RPC daemon mode over a socket or in HTTP
REST mode. This adapter uses the JSON-RPC stdio mode via subprocess
for simplicity, with plans to migrate to the daemon mode once
signal-cli is set up as a systemd service.

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
import subprocess
from datetime import datetime
from typing import Optional

from .base import (
    BaseChannel,
    ChannelType,
    InboundMessage,
    OutboundMessage,
)
from ..config import SignalConfig

logger = logging.getLogger(__name__)


class SignalChannel(BaseChannel):
    """Signal adapter using signal-cli."""

    channel_type = ChannelType.SIGNAL

    def __init__(self, config: SignalConfig):
        self.config = config

    def _run_signal_cli(self, *args: str, timeout: int = 30) -> Optional[str]:
        """
        Run a signal-cli command and return stdout.

        Returns None on failure.
        """
        cmd = [
            self.config.binary,
            "-u", self.config.account,
            "--output=json",
            *args,
        ]
        logger.debug("Running: %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            if result.returncode != 0:
                logger.error(
                    "signal-cli failed (rc=%d): %s",
                    result.returncode, result.stderr.strip()
                )
                return None
            return result.stdout
        except FileNotFoundError:
            logger.error("signal-cli not found at: %s", self.config.binary)
            return None
        except subprocess.TimeoutExpired:
            logger.error("signal-cli command timed out")
            return None

    def poll(self) -> list[InboundMessage]:
        """
        Receive pending messages from Signal.

        Uses `signal-cli receive` which downloads and returns any
        queued messages from the Signal server.
        """
        output = self._run_signal_cli("receive", "--timeout", "1")
        if not output:
            return []

        messages = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                msg = self._parse_message(data)
                if msg is not None:
                    messages.append(msg)
            except json.JSONDecodeError:
                logger.warning("Could not parse signal-cli output: %s", line)

        if messages:
            logger.info("Received %d Signal messages", len(messages))
        return messages

    def _parse_message(self, data: dict) -> Optional[InboundMessage]:
        """Parse a signal-cli JSON message envelope."""
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
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000) if timestamp_ms else datetime.now()

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
        """Send a Signal message."""
        args = ["send", "-m", message.body, message.recipient]
        output = self._run_signal_cli(*args)
        if output is not None:
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
        """Check if signal-cli is installed and the account is configured."""
        if not self.config.account:
            return False
        # Quick check: can we list contacts?
        output = self._run_signal_cli("listContacts", timeout=10)
        return output is not None

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
