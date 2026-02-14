"""
SEBE Daemon Orchestrator.

Main polling loop that:
1. Ensures the default LLM (Qwen3) is running
2. Polls all configured channels for inbound messages
3. Classifies each message via the active LLM
4. For actionable messages, drafts a response and queues for approval
5. Listens for owner commands via Signal (APPROVE/DENY/STATUS/etc.)
6. Sends approved actions, logs everything to memory DB

The orchestrator never auto-swaps models. gpt-oss-120b is only used
when explicitly requested via a SWAP command or a batch job.

Run as: python -m services.orchestrator
"""

import logging
import signal
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional

from .config import DaemonConfig, get_config
from .llm_client import LLMClient, ModelManager
from .channels.base import (
    ChannelType,
    InboundMessage,
    OutboundMessage,
    PendingAction,
    Urgency,
)
from .channels.email_channel import EmailChannel
from .channels.signal_channel import SignalChannel

logger = logging.getLogger(__name__)

# System prompt for message classification
CLASSIFY_PROMPT = """You are a message triage assistant for the SEBE campaign
(Sovereign Energy and Bandwidth Excise), a UK policy proposal for taxing
automation infrastructure to fund Universal Basic Income.

Classify the following message. Respond with ONLY a JSON object:
{
  "urgency": "low|normal|high|critical",
  "classification": "one of: policy_response, personal, spam, newsletter, automated, campaign_reply, think_tank, green_party, unknown",
  "needs_response": true/false,
  "summary": "one sentence summary",
  "suggested_action": "brief description of recommended action or null"
}

Context: Messages may come from Green Party members, think tanks (IPPR, NEF),
local party chairs, the Policy Development Committee, Reddit users, or
general public. Campaign emails were sent from the address configured in EMAIL_SENDER."""

# System prompt for drafting responses
DRAFT_PROMPT = """You are a drafting assistant for Jason Huxley, who runs the
SEBE campaign (Sovereign Energy and Bandwidth Excise). Draft a response to
the message below.

Style guidelines:
- British English (labour, defence, realise, colour)
- No em dashes in prose; use parentheses or commas for asides
- Professional but not stiff; technically precise
- If policy-related, reference specific SEBE mechanisms and figures
- Keep it concise; Jason will review before sending
- Sign off as "Jason Huxley" (do not invent titles or credentials)

Provide ONLY the response text, ready to send. No preamble."""


class Orchestrator:
    """Main daemon orchestrator."""

    def __init__(self, config: Optional[DaemonConfig] = None):
        self.config = config or get_config()
        self._running = False

        # LLM
        self.llm_client = LLMClient(self.config.llm)
        self.model_manager = ModelManager(self.config.llm, self.llm_client)

        # Channels
        self.channels: dict[ChannelType, object] = {}
        self._init_channels()

        # Pending actions awaiting approval
        self.pending: dict[str, PendingAction] = {}

    def _init_channels(self) -> None:
        """Initialise configured channel adapters."""
        # Email (only if credentials are set)
        if self.config.email.username and self.config.email.password:
            self.channels[ChannelType.EMAIL] = EmailChannel(self.config.email)
            logger.info("Email channel configured (%s)", self.config.email.username)
        else:
            logger.warning("Email channel disabled (no credentials)")

        # Signal (only if account is set)
        if self.config.signal.account:
            self.channels[ChannelType.SIGNAL] = SignalChannel(self.config.signal)
            logger.info("Signal channel configured (%s)", self.config.signal.account)
        else:
            logger.warning("Signal channel disabled (no account)")

    @property
    def signal(self) -> Optional[SignalChannel]:
        """Convenience accessor for the Signal channel."""
        ch = self.channels.get(ChannelType.SIGNAL)
        return ch if isinstance(ch, SignalChannel) else None

    def run(self) -> None:
        """Main daemon loop."""
        self._running = True

        # Handle graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        logger.info("SEBE daemon starting")

        # Ensure default model is running
        if not self.model_manager.ensure_default():
            logger.error("Failed to start default model, exiting")
            sys.exit(1)

        logger.info("Default model ready, entering poll loop")
        if self.signal:
            self.signal.send_to_owner("SEBE daemon started. Default model ready.")

        while self._running:
            try:
                self._poll_cycle()
            except Exception as e:
                logger.error("Error in poll cycle: %s", e, exc_info=True)

            # Expire old pending actions
            self._expire_actions()

            time.sleep(self.config.poll_interval)

        logger.info("SEBE daemon stopped")
        if self.signal:
            self.signal.send_to_owner("SEBE daemon stopped.")

    def _handle_signal(self, signum, frame) -> None:
        """Handle SIGTERM/SIGINT for graceful shutdown."""
        logger.info("Received signal %d, shutting down", signum)
        self._running = False

    def _poll_cycle(self) -> None:
        """Single iteration of the poll loop."""
        for channel_type, channel in self.channels.items():
            if not channel.is_available():
                continue

            messages = channel.poll()
            for msg in messages:
                self._handle_message(msg)

    def _handle_message(self, msg: InboundMessage) -> None:
        """Process a single inbound message."""
        logger.info(
            "[%s] From: %s | Subject: %s",
            msg.channel.value, msg.sender, msg.subject or "(none)"
        )

        # Signal messages from the owner are commands, not content
        if (
            msg.channel == ChannelType.SIGNAL
            and self.signal
            and self.signal.is_owner_message(msg)
        ):
            self._handle_owner_command(msg)
            return

        # Classify the message via LLM
        classification = self._classify_message(msg)
        if classification is None:
            logger.warning("Classification failed for message %s", msg.message_id)
            return

        # Notify owner via Signal
        if self.signal:
            notify_text = (
                f"[{msg.channel.value}] {msg.sender}\n"
                f"Subject: {msg.subject or '(none)'}\n"
                f"Urgency: {msg.urgency.value}\n"
                f"Type: {msg.classification or 'unknown'}\n"
                f"Summary: {classification.get('summary', 'N/A')}"
            )

            if classification.get("needs_response"):
                # Draft a response
                draft = self._draft_response(msg)
                if draft:
                    action_id = self._queue_action(msg, draft)
                    notify_text += (
                        f"\n\nDraft response queued ({action_id}):\n"
                        f"---\n{draft[:500]}\n---"
                    )
                    self.signal.notify(notify_text, action_id=action_id)
                else:
                    notify_text += "\n\n(Draft generation failed)"
                    self.signal.send_to_owner(notify_text)
            else:
                self.signal.send_to_owner(notify_text)

    def _classify_message(self, msg: InboundMessage) -> Optional[dict]:
        """Classify a message using the active LLM."""
        import json

        content = (
            f"Channel: {msg.channel.value}\n"
            f"From: {msg.sender}\n"
            f"Subject: {msg.subject}\n"
            f"Body:\n{msg.body[:2000]}"
        )

        try:
            response = self.llm_client.chat_simple(
                content,
                system_prompt=CLASSIFY_PROMPT,
                temperature=0.3,
                max_tokens=256,
            )
            # Parse JSON from response (handle markdown code fences)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1]
                response = response.rsplit("```", 1)[0]

            result = json.loads(response)

            # Apply classification to the message object
            urgency_str = result.get("urgency", "normal")
            try:
                msg.urgency = Urgency(urgency_str)
            except ValueError:
                msg.urgency = Urgency.NORMAL

            msg.classification = result.get("classification", "unknown")
            msg.suggested_action = result.get("suggested_action")

            return result

        except (json.JSONDecodeError, Exception) as e:
            logger.error("Classification failed: %s", e)
            return None

    def _draft_response(self, msg: InboundMessage) -> Optional[str]:
        """Draft a response to a message using the active LLM."""
        content = (
            f"Original message from {msg.sender}:\n"
            f"Subject: {msg.subject}\n"
            f"---\n{msg.body[:3000]}\n---\n\n"
            f"Classification: {msg.classification}\n"
            f"Suggested action: {msg.suggested_action or 'respond appropriately'}"
        )

        try:
            return self.llm_client.chat_simple(
                content,
                system_prompt=DRAFT_PROMPT,
                temperature=0.7,
                max_tokens=1024,
            )
        except Exception as e:
            logger.error("Draft generation failed: %s", e)
            return None

    def _queue_action(self, original: InboundMessage, draft: str) -> str:
        """Queue a drafted response for human approval."""
        action_id = uuid.uuid4().hex[:8]

        outbound = OutboundMessage(
            channel=original.channel,
            recipient=original.sender,
            subject=f"Re: {original.subject}" if original.subject else "",
            body=draft,
            reply_to=original.message_id,
            thread_id=original.thread_id,
        )

        action = PendingAction(
            action_id=action_id,
            action_type=f"reply_{original.channel.value}",
            description=f"Reply to {original.sender}: {original.subject}",
            outbound=outbound,
        )

        self.pending[action_id] = action
        logger.info("Queued action %s: %s", action_id, action.description)
        return action_id

    def _handle_owner_command(self, msg: InboundMessage) -> None:
        """Process a command from the daemon owner via Signal."""
        if not self.signal:
            return

        command, args = self.signal.parse_command(msg.body)

        if command == "APPROVE" and args:
            self._approve_action(args[0])
        elif command == "DENY" and args:
            self._deny_action(args[0])
        elif command == "STATUS":
            self._send_status()
        elif command == "TASKS":
            self._send_pending()
        elif command == "SWAP" and args:
            self._swap_model(args[0])
        elif command == "HELP":
            self.signal.send_to_owner(
                "Commands:\n"
                "APPROVE <id> - approve pending action\n"
                "DENY <id> - deny pending action\n"
                "STATUS - daemon and model status\n"
                "TASKS - list pending actions\n"
                "SWAP <model> - swap LLM (qwen3|oss120)\n"
                "HELP - this message"
            )
        else:
            self.signal.send_to_owner(
                f"Unknown command: {command}\nSend HELP for available commands."
            )

    def _approve_action(self, action_id: str) -> None:
        """Approve and execute a pending action."""
        action = self.pending.get(action_id)
        if not action:
            self.signal.send_to_owner(f"No pending action with ID: {action_id}")
            return

        if action.status != "pending":
            self.signal.send_to_owner(
                f"Action {action_id} is already {action.status}"
            )
            return

        # Find the channel and send
        channel = self.channels.get(action.outbound.channel)
        if channel is None:
            self.signal.send_to_owner(
                f"Channel {action.outbound.channel.value} not available"
            )
            return

        success = channel.send(action.outbound)
        if success:
            action.status = "approved"
            action.approved_at = datetime.now()
            self.signal.send_to_owner(f"Action {action_id} sent successfully.")
            logger.info("Action %s approved and sent", action_id)
        else:
            self.signal.send_to_owner(f"Action {action_id} send FAILED.")
            logger.error("Action %s send failed", action_id)

    def _deny_action(self, action_id: str) -> None:
        """Deny a pending action."""
        action = self.pending.get(action_id)
        if not action:
            self.signal.send_to_owner(f"No pending action with ID: {action_id}")
            return

        action.status = "denied"
        self.signal.send_to_owner(f"Action {action_id} denied.")
        logger.info("Action %s denied", action_id)

    def _send_status(self) -> None:
        """Send daemon status to owner."""
        model_status = self.model_manager.status()
        channels_status = {
            ct.value: ch.is_available()
            for ct, ch in self.channels.items()
        }
        pending_count = sum(
            1 for a in self.pending.values() if a.status == "pending"
        )

        text = (
            f"Model: {model_status['active_model'] or 'none'} "
            f"({'online' if model_status['api_available'] else 'OFFLINE'})\n"
            f"Channels: {channels_status}\n"
            f"Pending actions: {pending_count}"
        )
        self.signal.send_to_owner(text)

    def _send_pending(self) -> None:
        """Send list of pending actions to owner."""
        pending = [
            a for a in self.pending.values() if a.status == "pending"
        ]
        if not pending:
            self.signal.send_to_owner("No pending actions.")
            return

        lines = []
        for a in pending:
            age = datetime.now() - a.created_at
            lines.append(
                f"  {a.action_id}: {a.description} ({age.seconds // 60}m ago)"
            )
        self.signal.send_to_owner("Pending actions:\n" + "\n".join(lines))

    def _swap_model(self, model_key: str) -> None:
        """Swap to a different model (owner command)."""
        if model_key not in self.config.llm.models:
            self.signal.send_to_owner(
                f"Unknown model: {model_key}. "
                f"Available: {', '.join(self.config.llm.models.keys())}"
            )
            return

        self.signal.send_to_owner(f"Swapping to {model_key}...")
        if self.model_manager.ensure_model(model_key):
            self.signal.send_to_owner(f"Model {model_key} is ready.")
        else:
            self.signal.send_to_owner(f"FAILED to start {model_key}.")

    def _expire_actions(self) -> None:
        """Expire pending actions that have timed out."""
        cutoff = datetime.now() - timedelta(seconds=self.config.approval_timeout)
        for action in self.pending.values():
            if action.status == "pending" and action.created_at < cutoff:
                action.status = "expired"
                logger.info("Action %s expired", action.action_id)
                if self.signal:
                    self.signal.send_to_owner(
                        f"Action {action.action_id} expired: {action.description}"
                    )


def main():
    """Entry point for the daemon."""
    config = get_config()

    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    orchestrator = Orchestrator(config)
    orchestrator.run()


if __name__ == "__main__":
    main()
