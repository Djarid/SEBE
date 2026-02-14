"""
Tests for services/channels/base.py.

Tests enums, dataclasses, and abstract base class.
"""

import pytest
from datetime import datetime

from services.channels.base import (
    BaseChannel,
    ChannelType,
    InboundMessage,
    MessageDirection,
    OutboundMessage,
    PendingAction,
    Urgency,
)


def test_channel_type_values():
    """Test ChannelType enum values."""
    assert ChannelType.EMAIL.value == "email"
    assert ChannelType.SIGNAL.value == "signal"
    assert ChannelType.REDDIT.value == "reddit"
    assert ChannelType.GITHUB.value == "github"


def test_urgency_values():
    """Test Urgency enum values."""
    assert Urgency.LOW.value == "low"
    assert Urgency.NORMAL.value == "normal"
    assert Urgency.HIGH.value == "high"
    assert Urgency.CRITICAL.value == "critical"


def test_inbound_message_defaults():
    """Test InboundMessage default field values."""
    msg = InboundMessage(
        channel=ChannelType.EMAIL,
        sender="test@example.com",
        subject="Test",
        body="Body text",
        timestamp=datetime.now(),
        message_id="abc123",
    )
    
    assert msg.urgency == Urgency.NORMAL
    assert msg.classification is None
    assert msg.attachments == []
    assert msg.raw is None
    assert msg.reply_to is None
    assert msg.thread_id is None


def test_outbound_message_creation():
    """Test OutboundMessage creation."""
    msg = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="recipient@example.com",
        subject="Re: Test",
        body="Response text",
        reply_to="<abc123>",
    )
    
    assert msg.channel == ChannelType.EMAIL
    assert msg.recipient == "recipient@example.com"
    assert msg.subject == "Re: Test"
    assert msg.body == "Response text"
    assert msg.reply_to == "<abc123>"


def test_pending_action_defaults():
    """Test PendingAction default values."""
    outbound = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="test@example.com",
        subject="Test",
        body="Body",
    )
    
    action = PendingAction(
        action_id="abc123",
        action_type="send_email",
        description="Test action",
        outbound=outbound,
    )
    
    assert action.status == "pending"
    assert action.approved_at is None
    assert isinstance(action.created_at, datetime)


def test_base_channel_is_abstract():
    """Test that BaseChannel cannot be instantiated."""
    with pytest.raises(TypeError):
        BaseChannel()
