"""
Base channel adapter interface.

All channel adapters (email, Signal, Reddit, etc.) implement this
interface so the orchestrator can poll them uniformly.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


logger = logging.getLogger(__name__)


class ChannelType(Enum):
    EMAIL = "email"
    SIGNAL = "signal"
    REDDIT = "reddit"
    GITHUB = "github"


class MessageDirection(Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Urgency(Enum):
    """Classification urgency levels."""
    LOW = "low"          # Informational, no action needed
    NORMAL = "normal"    # Needs attention, not time-sensitive
    HIGH = "high"        # Needs prompt response
    CRITICAL = "critical"  # Requires immediate action


@dataclass
class InboundMessage:
    """A message received from any channel."""
    channel: ChannelType
    sender: str
    subject: str
    body: str
    timestamp: datetime
    message_id: str  # Channel-specific unique ID
    # Optional metadata
    reply_to: Optional[str] = None  # ID of message this replies to
    thread_id: Optional[str] = None
    attachments: list[str] = field(default_factory=list)
    raw: Optional[dict] = None  # Full raw message for channel-specific handling

    # Set by classifier
    urgency: Urgency = Urgency.NORMAL
    classification: Optional[str] = None  # e.g. "policy_response", "spam", "personal"
    suggested_action: Optional[str] = None


@dataclass
class OutboundMessage:
    """A message to send via any channel."""
    channel: ChannelType
    recipient: str
    subject: str
    body: str
    # Optional
    reply_to: Optional[str] = None  # Channel-specific ID to reply to
    thread_id: Optional[str] = None
    attachments: list[str] = field(default_factory=list)


@dataclass
class PendingAction:
    """An action awaiting human approval via Signal."""
    action_id: str
    action_type: str  # "send_email", "post_reddit", "reply_signal"
    description: str  # Human-readable summary for Signal notification
    outbound: OutboundMessage
    created_at: datetime = field(default_factory=datetime.now)
    # Set when approved/denied
    status: str = "pending"  # "pending", "approved", "denied", "expired"
    approved_at: Optional[datetime] = None


class BaseChannel(ABC):
    """
    Abstract base class for channel adapters.

    Each adapter must implement:
    - poll(): check for new messages
    - send(): send an outbound message
    - is_available(): check if the channel is operational
    """

    channel_type: ChannelType

    @abstractmethod
    def poll(self) -> list[InboundMessage]:
        """
        Check for new messages since last poll.

        Returns a list of new InboundMessage objects. The adapter is
        responsible for tracking what has already been seen (e.g. via
        IMAP flags, message IDs, timestamps).
        """
        ...

    @abstractmethod
    def send(self, message: OutboundMessage) -> bool:
        """
        Send an outbound message.

        Returns True on success, False on failure.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the channel backend is reachable and configured."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({self.channel_type.value})>"
