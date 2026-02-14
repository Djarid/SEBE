"""
Tests for services/orchestrator.py.

Tests orchestrator message handling, classification, approval workflow, and owner commands.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from services.channels.base import ChannelType, InboundMessage, Urgency
from services.orchestrator import Orchestrator


def test_orchestrator_init_with_credentials(daemon_config):
    """Test orchestrator initializes channels when credentials present."""
    orch = Orchestrator(daemon_config)
    
    assert ChannelType.EMAIL in orch.channels
    assert ChannelType.SIGNAL in orch.channels
    assert orch.pending == {}


def test_orchestrator_init_no_credentials():
    """Test orchestrator skips channels without credentials."""
    from services.config import DaemonConfig, EmailConfig, SignalConfig
    
    config = DaemonConfig(
        email=EmailConfig(username="", password=""),
        signal=SignalConfig(account=""),
    )
    
    orch = Orchestrator(config)
    assert len(orch.channels) == 0


def test_handle_owner_command_approve(daemon_config, sample_inbound_signal, sample_pending_action):
    """Test APPROVE command approves and sends action."""
    with patch("signal.signal"):  # Mock signal handler registration
        orch = Orchestrator(daemon_config)
    
    # Add pending action
    orch.pending["abc123"] = sample_pending_action
    
    # Mock the email channel
    mock_email_channel = Mock()
    mock_email_channel.send.return_value = True
    orch.channels[ChannelType.EMAIL] = mock_email_channel
    
    # Mock signal channel methods
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("APPROVE", ["abc123"])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    # Create APPROVE command
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="APPROVE abc123",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    assert sample_pending_action.status == "approved"
    mock_email_channel.send.assert_called_once()
    mock_signal.send_to_owner.assert_called()


def test_handle_owner_command_approve_nonexistent(daemon_config):
    """Test APPROVE with nonexistent action ID."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("APPROVE", ["nonexistent"])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="APPROVE nonexistent",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    # Should notify owner
    call_args = mock_signal.send_to_owner.call_args[0][0]
    assert "No pending action" in call_args


def test_handle_owner_command_deny(daemon_config, sample_pending_action):
    """Test DENY command."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    orch.pending["abc123"] = sample_pending_action
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("DENY", ["abc123"])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="DENY abc123",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    assert sample_pending_action.status == "denied"
    mock_signal.send_to_owner.assert_called()


def test_handle_owner_command_status(daemon_config):
    """Test STATUS command."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("STATUS", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    # Mock model manager status
    orch.model_manager.status = Mock(return_value={
        "active_model": "qwen3",
        "api_available": True,
        "default_model": "qwen3"
    })
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="STATUS",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    call_args = mock_signal.send_to_owner.call_args[0][0]
    assert "qwen3" in call_args
    assert "online" in call_args.lower()


def test_handle_owner_command_tasks_empty(daemon_config):
    """Test TASKS command with no pending actions."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("TASKS", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="TASKS",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    call_args = mock_signal.send_to_owner.call_args[0][0]
    assert "No pending" in call_args


def test_handle_owner_command_tasks_with_pending(daemon_config, sample_pending_action):
    """Test TASKS command with pending actions."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    # Add two pending actions
    orch.pending["abc123"] = sample_pending_action
    
    from services.channels.base import PendingAction, OutboundMessage
    from services.channels.signal_channel import SignalChannel
    action2 = PendingAction(
        action_id="xyz789",
        action_type="reply_email",
        description="Another action",
        outbound=OutboundMessage(
            channel=ChannelType.EMAIL,
            recipient="test@example.com",
            subject="Test",
            body="Body",
        ),
    )
    orch.pending["xyz789"] = action2
    
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("TASKS", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="TASKS",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    call_args = mock_signal.send_to_owner.call_args[0][0]
    assert "abc123" in call_args
    assert "xyz789" in call_args


def test_handle_owner_command_swap(daemon_config):
    """Test SWAP command."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("SWAP", ["oss120"])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch.model_manager.ensure_model = Mock(return_value=True)
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="SWAP oss120",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    orch.model_manager.ensure_model.assert_called_once_with("oss120")
    # Should send two messages: swapping... and ready
    assert mock_signal.send_to_owner.call_count == 2


def test_handle_owner_command_help(daemon_config):
    """Test HELP command."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("HELP", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="HELP",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    call_args = mock_signal.send_to_owner.call_args[0][0]
    assert "APPROVE" in call_args
    assert "DENY" in call_args
    assert "STATUS" in call_args


def test_handle_owner_command_unknown(daemon_config):
    """Test unknown command."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.parse_command.return_value = ("FOOBAR", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="FOOBAR",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_owner_command(msg)
    
    call_args = mock_signal.send_to_owner.call_args[0][0]
    assert "Unknown command" in call_args


def test_classify_message(daemon_config, sample_inbound_email):
    """Test message classification."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    classification_json = {
        "urgency": "high",
        "classification": "green_party",
        "needs_response": True,
        "summary": "PDC reply",
        "suggested_action": "respond"
    }
    
    orch.llm_client.chat_simple = Mock(return_value=json.dumps(classification_json))
    
    result = orch._classify_message(sample_inbound_email)
    
    assert result is not None
    assert sample_inbound_email.urgency == Urgency.HIGH
    assert sample_inbound_email.classification == "green_party"
    assert result["needs_response"] is True


def test_classify_message_with_code_fence(daemon_config, sample_inbound_email):
    """Test classification handles markdown code fence."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    classification_json = {
        "urgency": "normal",
        "classification": "policy_response",
        "needs_response": False,
        "summary": "Test",
        "suggested_action": None
    }
    
    # Wrap in markdown code fence
    response = f"```json\n{json.dumps(classification_json)}\n```"
    orch.llm_client.chat_simple = Mock(return_value=response)
    
    result = orch._classify_message(sample_inbound_email)
    
    assert result is not None
    assert result["classification"] == "policy_response"


def test_classify_message_failure(daemon_config, sample_inbound_email):
    """Test classification failure handling."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    orch.llm_client.chat_simple = Mock(side_effect=Exception("LLM failed"))
    
    result = orch._classify_message(sample_inbound_email)
    
    assert result is None


def test_draft_response(daemon_config, sample_inbound_email):
    """Test response drafting."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    orch.llm_client.chat_simple = Mock(return_value="Dear PDC, thank you...")
    
    draft = orch._draft_response(sample_inbound_email)
    
    assert draft == "Dear PDC, thank you..."


def test_draft_response_failure(daemon_config, sample_inbound_email):
    """Test draft failure handling."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    orch.llm_client.chat_simple = Mock(side_effect=Exception("Draft failed"))
    
    draft = orch._draft_response(sample_inbound_email)
    
    assert draft is None


def test_queue_action(daemon_config, sample_inbound_email):
    """Test action queueing."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    action_id = orch._queue_action(sample_inbound_email, "Draft text here")
    
    assert action_id in orch.pending
    action = orch.pending[action_id]
    assert action.outbound.recipient == sample_inbound_email.sender
    assert action.outbound.body == "Draft text here"
    assert action.outbound.reply_to == sample_inbound_email.message_id


def test_expire_actions(daemon_config, sample_pending_action):
    """Test action expiry."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    # Set timeout to 1 second
    orch.config.approval_timeout = 1
    
    # Create old action
    old_time = datetime.now() - timedelta(seconds=10)
    sample_pending_action.created_at = old_time
    orch.pending["abc123"] = sample_pending_action
    
    mock_signal = Mock()
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch._expire_actions()
    
    assert sample_pending_action.status == "expired"


def test_expire_actions_leaves_recent(daemon_config, sample_pending_action):
    """Test expiry doesn't affect recent actions."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    # Recent action
    sample_pending_action.created_at = datetime.now()
    orch.pending["abc123"] = sample_pending_action
    
    orch._expire_actions()
    
    assert sample_pending_action.status == "pending"


def test_handle_message_signal_owner(daemon_config):
    """Test signal messages from owner are treated as commands."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.is_owner_message.return_value = True
    mock_signal.parse_command.return_value = ("STATUS", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch._handle_owner_command = Mock()
    orch._classify_message = Mock()
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="STATUS",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_message(msg)
    
    orch._handle_owner_command.assert_called_once()
    orch._classify_message.assert_not_called()


def test_handle_message_email_needs_response(daemon_config, sample_inbound_email):
    """Test email needing response queues action."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    classification = {
        "needs_response": True,
        "summary": "test summary",
        "urgency": "normal"
    }
    
    orch._classify_message = Mock(return_value=classification)
    orch._draft_response = Mock(return_value="Draft text")
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch._handle_message(sample_inbound_email)
    
    # Should queue an action
    assert len(orch.pending) == 1
    
    # Should notify with action_id
    mock_signal.notify.assert_called_once()
    call_args = mock_signal.notify.call_args
    assert call_args[1]["action_id"] is not None


def test_handle_message_email_no_response(daemon_config, sample_inbound_email):
    """Test email not needing response doesn't queue action."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    classification = {
        "needs_response": False,
        "summary": "newsletter",
        "urgency": "low"
    }
    
    orch._classify_message = Mock(return_value=classification)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch._handle_message(sample_inbound_email)
    
    # Should NOT queue an action
    assert len(orch.pending) == 0
    
    # Should still notify (informational)
    mock_signal.send_to_owner.assert_called_once()
