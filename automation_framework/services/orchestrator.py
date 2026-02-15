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
from typing import Any, Optional

from .config import DaemonConfig, get_config
from .llm_client import LLMClient, ModelManager
from .channels.base import (
    BaseChannel,
    ChannelType,
    InboundMessage,
    OutboundMessage,
    PendingAction,
    Urgency,
)
from .channels.email_channel import EmailChannel
from .channels.signal_channel import SignalChannel

# Memory system imports (optional — daemon must not crash if unavailable)
try:
    from tools.memory.db import (
        add_contact,
        list_contacts,
        log_interaction,
    )
    from tools.memory.writer import write_to_memory
    _MEMORY_AVAILABLE = True
except ImportError:
    _MEMORY_AVAILABLE = False

    # Type stubs so the checker knows these names exist in both branches.
    # These are never called at runtime (_MEMORY_AVAILABLE guards all usage).
    def write_to_memory(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    def list_contacts(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    def add_contact(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    def log_interaction(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

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

CRITICAL RULES (violation = unusable draft):
- NEVER invent URLs, links, or web addresses. No SEBE website exists.
- NEVER fabricate statistics, figures, or revenue numbers. Use ONLY the
  reference figures provided below.
- NEVER claim attachments are included unless explicitly instructed.
- If you are unsure of a fact, say "I will confirm and follow up" rather
  than guessing.

SEBE policy reference (use these figures, not invented ones):
- SEBE = Sovereign Energy & Bandwidth Excise
- Targets: commercial data centres and automation facilities >500kW IT load
- Energy excise (SEE): £0.08-0.45/kWh (tiered by consumption)
- Bandwidth excise (DCD): £200-800/TB tiered, border tariff on commercial
  data crossing UK digital border (both directions). Consumers exempt.
  Domestic DC traffic exempt (pays SEE instead).
- Revenue at launch: £31-38 billion/year, self-scaling with automation
  (grows to ~£93B by 2040, ~£159B by 2045)
- Stage 1: UBI starts at ~£400/adult/year and ramps with SEBE revenue.
  Target rate £2,500/adult/year reached as automation scales. UBS phases
  in (free transport 2028, free energy 2032, free broadband 2035).
  Children's supplements £3,500-5,000/year (age-banded).
- Stage 2: UBI ratchets toward Universal Living Income (£29,000/adult/year)
  as automation displaces employment. Total cost ~£1.81T.
- Domestic consumers and SMEs are NOT taxed. Only large-scale automation
  infrastructure pays. DCD only on cross-border commercial data.
- GitHub repository: https://github.com/Djarid/SEBE (the ONLY valid link)

Style guidelines:
- British English (labour, defence, realise, colour)
- No em dashes in prose; use parentheses or commas for asides
- Professional but not stiff; technically precise
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
        self.channels: dict[ChannelType, BaseChannel] = {}
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

    # ------------------------------------------------------------------
    # Memory integration helpers
    # ------------------------------------------------------------------

    def _log_event(self, content: str, importance: int = 5, tags: Optional[list[str]] = None) -> None:
        """Log an event to the memory system. Fire-and-forget."""
        if not _MEMORY_AVAILABLE:
            return
        try:
            write_to_memory(
                content=content,
                entry_type="event",
                importance=importance,
                tags=tags,
            )
        except Exception as e:
            logger.warning("Memory write failed (event): %s", e)

    def _find_or_create_contact(self, sender: str, channel: ChannelType) -> Optional[int]:
        """
        Look up a contact by sender address, creating one if not found.

        Returns the contact_id or None if the memory system is unavailable.
        """
        if not _MEMORY_AVAILABLE:
            return None

        try:
            # Search existing contacts by email or phone
            existing = list_contacts(limit=500)
            if existing.get("success"):
                for contact in existing["contacts"]:
                    if channel == ChannelType.EMAIL and contact.get("email") == sender:
                        return contact["id"]
                    if channel == ChannelType.SIGNAL and contact.get("phone") == sender:
                        return contact["id"]

            # Not found — create a new contact
            if channel == ChannelType.EMAIL:
                # Derive name from email local part
                name = sender.split("@")[0].replace(".", " ").replace("_", " ").title()
                result = add_contact(name=name, email=sender, notes=f"Auto-created from inbound {channel.value}")
            elif channel == ChannelType.SIGNAL:
                name = f"Signal {sender}"
                result = add_contact(name=name, phone=sender, notes=f"Auto-created from inbound {channel.value}")
            else:
                name = f"Unknown ({sender})"
                result = add_contact(name=name, notes=f"Auto-created from inbound {channel.value}: {sender}")

            if result.get("success"):
                contact_id = result["contact"]["id"]
                logger.info("Created new contact #%d for %s", contact_id, sender)
                return contact_id
            else:
                logger.warning("Failed to create contact for %s: %s", sender, result.get("error"))
                return None

        except Exception as e:
            logger.warning("Memory lookup/create failed for %s: %s", sender, e)
            return None

    def _log_interaction_safe(
        self,
        contact_id: int,
        channel: ChannelType,
        direction: str,
        subject: Optional[str] = None,
        content: Optional[str] = None,
    ) -> None:
        """Log an interaction to the memory DB. Fire-and-forget."""
        if not _MEMORY_AVAILABLE:
            return
        try:
            log_interaction(
                contact_id=contact_id,
                channel=channel.value,
                direction=direction,
                subject=subject,
                content=content[:2000] if content else None,
            )
        except Exception as e:
            logger.warning("Memory write failed (interaction): %s", e)

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
        self._log_event("SEBE daemon started, default model ready", importance=6, tags=["daemon"])
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
        self._log_event("SEBE daemon stopped", importance=6, tags=["daemon"])
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

        # Signal messages from the owner with the /sebe prefix are commands
        if (
            msg.channel == ChannelType.SIGNAL
            and self.signal
            and self.signal.is_owner_message(msg)
        ):
            if self.signal.is_command(msg):
                self._handle_owner_command(msg)
            # Non-prefixed owner messages are silently ignored (other bots)
            return

        # Classify the message via LLM
        classification = self._classify_message(msg)
        if classification is None:
            logger.warning("Classification failed for message %s", msg.message_id)
            return

        # Log inbound message to memory DB
        contact_id = self._find_or_create_contact(msg.sender, msg.channel)
        if contact_id is not None:
            self._log_interaction_safe(
                contact_id=contact_id,
                channel=msg.channel,
                direction="inbound",
                subject=msg.subject,
                content=f"[{msg.classification or 'unknown'}] {classification.get('summary', '')}\n\n{msg.body[:1000]}",
            )

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

                    # Save draft to Proton Drafts folder for email messages
                    if msg.channel == ChannelType.EMAIL:
                        self._save_email_draft(msg, draft, action_id)

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

    def _save_email_draft(
        self, original: InboundMessage, draft_body: str, action_id: str
    ) -> None:
        """
        Save a draft reply to the Proton Bridge Drafts folder.

        The draft appears in the Proton client ready for review and manual
        sending. The action_id is included in an X-SEBE-Action header for
        traceability. This is fire-and-forget: failure is logged but does
        not block the notification flow.
        """
        raw_channel = self.channels.get(ChannelType.EMAIL)
        if raw_channel is None:
            return

        # save_draft is EmailChannel-specific; cast for the type checker
        email_channel: EmailChannel = raw_channel  # type: ignore[assignment]

        outbound = OutboundMessage(
            channel=ChannelType.EMAIL,
            recipient=original.sender,
            subject=f"Re: {original.subject}" if original.subject else "",
            body=draft_body,
            reply_to=original.message_id,
            thread_id=original.thread_id,
        )

        try:
            saved = email_channel.save_draft(outbound)
            if saved:
                logger.info(
                    "Draft saved to Proton Drafts (%s) for %s",
                    action_id, original.sender,
                )
            else:
                logger.warning(
                    "Failed to save draft to Proton Drafts (%s)", action_id
                )
        except Exception as e:
            logger.warning("Draft save error (%s): %s", action_id, e)

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
            pfx = self.signal.COMMAND_PREFIX
            self.signal.send_to_owner(
                f"Commands (prefix: {pfx}):\n"
                f"{pfx} APPROVE <id> - approve pending action\n"
                f"{pfx} DENY <id> - deny pending action\n"
                f"{pfx} STATUS - daemon and model status\n"
                f"{pfx} TASKS - list pending actions\n"
                f"{pfx} SWAP <model> - swap LLM (qwen3|oss120)\n"
                f"{pfx} HELP - this message"
            )
        else:
            self.signal.send_to_owner(
                f"Unknown command: {command}\n"
                f"Send {self.signal.COMMAND_PREFIX} HELP for available commands."
            )

    def _approve_action(self, action_id: str) -> None:
        """Approve and execute a pending action."""
        assert self.signal is not None  # Only called from _handle_owner_command
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

            # Log outbound interaction to memory
            contact_id = self._find_or_create_contact(
                action.outbound.recipient, action.outbound.channel
            )
            if contact_id is not None:
                self._log_interaction_safe(
                    contact_id=contact_id,
                    channel=action.outbound.channel,
                    direction="outbound",
                    subject=action.outbound.subject,
                    content=action.outbound.body[:2000],
                )
            self._log_event(
                f"Approved and sent {action.action_type} to {action.outbound.recipient}: {action.outbound.subject}",
                importance=6,
                tags=["approval"],
            )
        else:
            self.signal.send_to_owner(f"Action {action_id} send FAILED.")
            logger.error("Action %s send failed", action_id)
            self._log_event(
                f"Send FAILED for {action.action_type} to {action.outbound.recipient}",
                importance=7,
                tags=["error"],
            )

    def _deny_action(self, action_id: str) -> None:
        """Deny a pending action."""
        assert self.signal is not None  # Only called from _handle_owner_command
        action = self.pending.get(action_id)
        if not action:
            self.signal.send_to_owner(f"No pending action with ID: {action_id}")
            return

        action.status = "denied"
        self.signal.send_to_owner(f"Action {action_id} denied.")
        logger.info("Action %s denied", action_id)
        self._log_event(
            f"Denied {action.action_type} to {action.outbound.recipient}: {action.description}",
            importance=5,
            tags=["denial"],
        )

    def _send_status(self) -> None:
        """Send daemon status to owner."""
        assert self.signal is not None  # Only called from _handle_owner_command
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
        assert self.signal is not None  # Only called from _handle_owner_command
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
        assert self.signal is not None  # Only called from _handle_owner_command
        if model_key not in self.config.llm.models:
            self.signal.send_to_owner(
                f"Unknown model: {model_key}. "
                f"Available: {', '.join(self.config.llm.models.keys())}"
            )
            return

        self.signal.send_to_owner(f"Swapping to {model_key}...")
        if self.model_manager.ensure_model(model_key):
            self.signal.send_to_owner(f"Model {model_key} is ready.")
            self._log_event(f"Model swapped to {model_key}", importance=5, tags=["model"])
        else:
            self.signal.send_to_owner(f"FAILED to start {model_key}.")
            self._log_event(f"Model swap to {model_key} FAILED", importance=7, tags=["model", "error"])

    def _expire_actions(self) -> None:
        """Expire pending actions that have timed out."""
        cutoff = datetime.now() - timedelta(seconds=self.config.approval_timeout)
        for action in self.pending.values():
            if action.status == "pending" and action.created_at < cutoff:
                action.status = "expired"
                logger.info("Action %s expired", action.action_id)
                self._log_event(
                    f"Action {action.action_id} expired: {action.description}",
                    importance=4,
                    tags=["expiry"],
                )
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
