"""
Tests for services/orchestrator.py.

Tests orchestrator message handling, classification, approval workflow,
owner commands, and memory integration.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch, call

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
    """Test signal messages from owner with /sebe prefix are treated as commands."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.is_owner_message.return_value = True
    mock_signal.is_command.return_value = True
    mock_signal.parse_command.return_value = ("STATUS", [])
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch._handle_owner_command = Mock()
    orch._classify_message = Mock()
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="/sebe STATUS",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    orch._handle_message(msg)
    
    orch._handle_owner_command.assert_called_once()
    orch._classify_message.assert_not_called()


def test_handle_message_signal_owner_no_prefix_ignored(daemon_config):
    """Test owner messages without /sebe prefix are silently ignored."""
    with patch("signal.signal"):
        orch = Orchestrator(daemon_config)
    
    from services.channels.signal_channel import SignalChannel
    mock_signal = Mock(spec=SignalChannel)
    mock_signal.is_owner_message.return_value = True
    mock_signal.is_command.return_value = False
    orch.channels[ChannelType.SIGNAL] = mock_signal
    
    orch._handle_owner_command = Mock()
    orch._classify_message = Mock()
    
    msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=daemon_config.signal.owner_number,
        subject="",
        body="hello other bot",
        timestamp=datetime.now(),
        message_id="signal-124",
    )
    
    orch._handle_message(msg)
    
    orch._handle_owner_command.assert_not_called()
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


# --------------------------------------------------------------------------
# Memory integration tests
# --------------------------------------------------------------------------

class TestMemoryIntegration:
    """Tests for orchestrator memory DB integration."""

    def _make_orchestrator(self, daemon_config):
        """Create orchestrator with signal mock."""
        with patch("signal.signal"):
            orch = Orchestrator(daemon_config)
        from services.channels.signal_channel import SignalChannel
        mock_signal = Mock(spec=SignalChannel)
        orch.channels[ChannelType.SIGNAL] = mock_signal
        return orch

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.list_contacts")
    @patch("services.orchestrator.add_contact")
    @patch("services.orchestrator.log_interaction")
    def test_handle_message_logs_inbound_interaction(
        self, mock_log_interaction, mock_add_contact, mock_list_contacts,
        daemon_config, sample_inbound_email,
    ):
        """Inbound messages are logged as interactions in the memory DB."""
        orch = self._make_orchestrator(daemon_config)

        # Contact already exists
        mock_list_contacts.return_value = {
            "success": True,
            "contacts": [{"id": 42, "email": "pdc@greenparty.org.uk", "phone": None}],
        }

        classification = {
            "needs_response": False,
            "summary": "PDC reply about economy working group",
            "urgency": "normal",
        }
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(sample_inbound_email)

        # Should have looked up contacts
        mock_list_contacts.assert_called_once_with(limit=500)

        # Should NOT have created a new contact (existing match)
        mock_add_contact.assert_not_called()

        # Should have logged the inbound interaction
        mock_log_interaction.assert_called_once()
        call_kwargs = mock_log_interaction.call_args
        assert call_kwargs[1]["contact_id"] == 42
        assert call_kwargs[1]["channel"] == "email"
        assert call_kwargs[1]["direction"] == "inbound"
        assert call_kwargs[1]["subject"] == "Re: SEBE - Policy Proposal"

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.list_contacts")
    @patch("services.orchestrator.add_contact")
    @patch("services.orchestrator.log_interaction")
    def test_handle_message_creates_new_contact(
        self, mock_log_interaction, mock_add_contact, mock_list_contacts,
        daemon_config, sample_inbound_email,
    ):
        """Unknown senders get auto-created as contacts."""
        orch = self._make_orchestrator(daemon_config)

        # No existing contacts
        mock_list_contacts.return_value = {"success": True, "contacts": []}

        # New contact creation succeeds
        mock_add_contact.return_value = {
            "success": True,
            "contact": {"id": 99},
        }

        classification = {
            "needs_response": False,
            "summary": "New sender",
            "urgency": "normal",
        }
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(sample_inbound_email)

        # Should have created a contact derived from email
        mock_add_contact.assert_called_once()
        call_kwargs = mock_add_contact.call_args[1]
        assert call_kwargs["email"] == "pdc@greenparty.org.uk"
        assert "Pdc" in call_kwargs["name"]  # Derived from local part

        # Should have logged with the new contact ID
        mock_log_interaction.assert_called_once()
        assert mock_log_interaction.call_args[1]["contact_id"] == 99

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.list_contacts")
    @patch("services.orchestrator.add_contact")
    @patch("services.orchestrator.log_interaction")
    def test_handle_message_reuses_existing_contact(
        self, mock_log_interaction, mock_add_contact, mock_list_contacts,
        daemon_config, sample_inbound_email,
    ):
        """Existing contacts are matched by email and reused."""
        orch = self._make_orchestrator(daemon_config)

        mock_list_contacts.return_value = {
            "success": True,
            "contacts": [
                {"id": 10, "email": "other@example.com", "phone": None},
                {"id": 42, "email": "pdc@greenparty.org.uk", "phone": None},
            ],
        }

        classification = {"needs_response": False, "summary": "Test", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(sample_inbound_email)

        # Should NOT create a new contact
        mock_add_contact.assert_not_called()

        # Should use existing contact 42
        assert mock_log_interaction.call_args[1]["contact_id"] == 42

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.write_to_memory")
    @patch("services.orchestrator.list_contacts")
    @patch("services.orchestrator.add_contact")
    @patch("services.orchestrator.log_interaction")
    def test_approve_action_logs_outbound(
        self, mock_log_interaction, mock_add_contact, mock_list_contacts,
        mock_write_to_memory, daemon_config, sample_pending_action,
    ):
        """Approved actions log outbound interactions and events."""
        orch = self._make_orchestrator(daemon_config)
        orch.pending["abc123"] = sample_pending_action

        # Mock email channel send success
        mock_email_channel = Mock()
        mock_email_channel.send.return_value = True
        orch.channels[ChannelType.EMAIL] = mock_email_channel

        # Contact lookup
        mock_list_contacts.return_value = {
            "success": True,
            "contacts": [{"id": 42, "email": "pdc@greenparty.org.uk", "phone": None}],
        }

        orch._approve_action("abc123")

        # Should log outbound interaction
        mock_log_interaction.assert_called_once()
        call_kwargs = mock_log_interaction.call_args[1]
        assert call_kwargs["contact_id"] == 42
        assert call_kwargs["direction"] == "outbound"

        # Should log an approval event
        mock_write_to_memory.assert_called()
        event_calls = [
            c for c in mock_write_to_memory.call_args_list
            if c[1].get("entry_type") == "event"
        ]
        assert len(event_calls) >= 1
        assert "Approved" in event_calls[0][1]["content"]

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.write_to_memory")
    def test_deny_action_logs_event(
        self, mock_write_to_memory, daemon_config, sample_pending_action,
    ):
        """Denied actions log a denial event."""
        orch = self._make_orchestrator(daemon_config)
        orch.pending["abc123"] = sample_pending_action

        orch._deny_action("abc123")

        assert sample_pending_action.status == "denied"
        mock_write_to_memory.assert_called_once()
        call_kwargs = mock_write_to_memory.call_args[1]
        assert call_kwargs["entry_type"] == "event"
        assert "Denied" in call_kwargs["content"]
        assert call_kwargs["tags"] == ["denial"]

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.write_to_memory")
    def test_expire_action_logs_event(
        self, mock_write_to_memory, daemon_config, sample_pending_action,
    ):
        """Expired actions log an expiry event."""
        orch = self._make_orchestrator(daemon_config)

        orch.config.approval_timeout = 1
        sample_pending_action.created_at = datetime.now() - timedelta(seconds=10)
        orch.pending["abc123"] = sample_pending_action

        orch._expire_actions()

        assert sample_pending_action.status == "expired"
        mock_write_to_memory.assert_called_once()
        call_kwargs = mock_write_to_memory.call_args[1]
        assert call_kwargs["entry_type"] == "event"
        assert "expired" in call_kwargs["content"]
        assert call_kwargs["tags"] == ["expiry"]

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.list_contacts")
    @patch("services.orchestrator.log_interaction")
    def test_memory_failure_doesnt_block_processing(
        self, mock_log_interaction, mock_list_contacts,
        daemon_config, sample_inbound_email,
    ):
        """Memory DB errors must not crash the orchestrator."""
        orch = self._make_orchestrator(daemon_config)

        # Memory DB raises an exception
        mock_list_contacts.side_effect = Exception("DB locked")

        classification = {"needs_response": False, "summary": "Test", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        # Should NOT raise — graceful degradation
        orch._handle_message(sample_inbound_email)

        # Message should still have been processed (Signal notification sent)
        mock_signal = orch.channels[ChannelType.SIGNAL]
        mock_signal.send_to_owner.assert_called_once()

    @patch("services.orchestrator._MEMORY_AVAILABLE", True)
    @patch("services.orchestrator.write_to_memory")
    def test_swap_model_logs_event(
        self, mock_write_to_memory, daemon_config,
    ):
        """Model swaps log events to memory."""
        orch = self._make_orchestrator(daemon_config)
        orch.model_manager.ensure_model = Mock(return_value=True)

        orch._swap_model("oss120")

        mock_write_to_memory.assert_called_once()
        call_kwargs = mock_write_to_memory.call_args[1]
        assert call_kwargs["entry_type"] == "event"
        assert "oss120" in call_kwargs["content"]
        assert "model" in call_kwargs["tags"]

    @patch("services.orchestrator._MEMORY_AVAILABLE", False)
    def test_memory_unavailable_skips_gracefully(
        self, daemon_config, sample_inbound_email,
    ):
        """When memory module is not importable, all memory calls are no-ops."""
        orch = self._make_orchestrator(daemon_config)

        classification = {"needs_response": False, "summary": "Test", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        # Should NOT raise even though memory is unavailable
        orch._handle_message(sample_inbound_email)

        # contact_id should be None (no memory), but message still processed
        mock_signal = orch.channels[ChannelType.SIGNAL]
        mock_signal.send_to_owner.assert_called_once()


# --------------------------------------------------------------------------
# Integration tests — real in-memory SQLite DB, no mocks on memory layer
# --------------------------------------------------------------------------

class TestMemoryIntegrationReal:
    """
    End-to-end tests that hit a real (in-memory) SQLite database.

    These catch schema mismatches, argument type errors, and data flow
    problems that mock-based tests cannot detect.

    Each test gets a fresh in-memory DB via the _real_db fixture pattern
    (same approach as test_memory_db.py).
    """

    @pytest.fixture(autouse=True)
    def _real_db(self, tmp_path):
        """
        Provide a fresh in-memory SQLite DB for each test.

        Patches get_connection in both tools.memory.db AND the
        orchestrator's imported references so the full call chain
        (orchestrator -> db.add_contact -> get_connection) uses
        the same in-memory connection.

        Also patches writer paths so daily log writes go to tmp_path.
        """
        import sqlite3
        from tools.memory.db import _ensure_tables

        real_conn = sqlite3.connect(":memory:")
        real_conn.row_factory = sqlite3.Row
        real_conn.execute("PRAGMA foreign_keys=ON")
        _ensure_tables(real_conn)

        # Wrapper that prevents functions from closing our shared connection
        class NonClosingConnection:
            def __init__(self, conn):
                self._conn = conn
            def close(self):
                pass
            def __getattr__(self, name):
                return getattr(self._conn, name)

        wrapped = NonClosingConnection(real_conn)

        # Patch get_connection everywhere it's used
        with patch("tools.memory.db.get_connection", return_value=wrapped), \
             patch("tools.memory.writer.LOGS_DIR", tmp_path / "logs"), \
             patch("tools.memory.writer.MEMORY_DIR", tmp_path):
            (tmp_path / "logs").mkdir(exist_ok=True)
            self._conn = real_conn
            self._logs_dir = tmp_path / "logs"
            yield

        real_conn.close()

    def _make_orchestrator(self, daemon_config):
        """Create orchestrator with signal mock."""
        with patch("signal.signal"):
            orch = Orchestrator(daemon_config)
        from services.channels.signal_channel import SignalChannel
        mock_signal = Mock(spec=SignalChannel)
        orch.channels[ChannelType.SIGNAL] = mock_signal
        return orch

    def test_inbound_email_creates_contact_and_interaction(
        self, daemon_config, sample_inbound_email,
    ):
        """Full flow: inbound email creates a contact row and an interaction row in real DB."""
        from tools.memory.db import list_contacts, list_interactions

        orch = self._make_orchestrator(daemon_config)

        classification = {
            "needs_response": False,
            "summary": "PDC reply about economy working group",
            "urgency": "normal",
        }
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(sample_inbound_email)

        # Verify contact was created in the real DB
        contacts = list_contacts()
        assert contacts["success"]
        assert contacts["count"] == 1
        contact = contacts["contacts"][0]
        assert contact["email"] == "pdc@greenparty.org.uk"
        assert "Pdc" in contact["name"]  # Derived from email local part

        # Verify interaction was logged in the real DB
        interactions = list_interactions()
        assert interactions["success"]
        assert interactions["count"] == 1
        interaction = interactions["interactions"][0]
        assert interaction["contact_id"] == contact["id"]
        assert interaction["channel"] == "email"
        assert interaction["direction"] == "inbound"
        assert interaction["subject"] == "Re: SEBE - Policy Proposal"
        assert "PDC reply" in interaction["content"]

    def test_inbound_email_reuses_existing_contact(
        self, daemon_config, sample_inbound_email,
    ):
        """Second email from the same sender reuses the existing contact, not a duplicate."""
        from tools.memory.db import add_contact, list_contacts, list_interactions

        # Pre-create the contact
        result = add_contact(
            name="Policy Dev Committee",
            email="pdc@greenparty.org.uk",
            organisation="Green Party",
        )
        assert result["success"]
        original_id = result["contact"]["id"]

        orch = self._make_orchestrator(daemon_config)
        classification = {"needs_response": False, "summary": "Test", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(sample_inbound_email)

        # Should still be only 1 contact
        contacts = list_contacts()
        assert contacts["count"] == 1
        assert contacts["contacts"][0]["id"] == original_id

        # Interaction should reference the original contact
        interactions = list_interactions()
        assert interactions["count"] == 1
        assert interactions["interactions"][0]["contact_id"] == original_id

    def test_signal_inbound_creates_contact_with_phone(
        self, daemon_config,
    ):
        """Inbound Signal messages create contacts with phone number, not email."""
        from tools.memory.db import list_contacts, list_interactions

        orch = self._make_orchestrator(daemon_config)

        # Non-owner Signal message (owner messages are commands, not content)
        msg = InboundMessage(
            channel=ChannelType.SIGNAL,
            sender="+447999888777",
            subject="",
            body="Hello, I saw your SEBE proposal",
            timestamp=datetime.now(),
            message_id="signal-test-001",
        )

        # Make sure it's NOT treated as an owner command
        mock_signal = orch.channels[ChannelType.SIGNAL]
        mock_signal.is_owner_message.return_value = False

        classification = {"needs_response": False, "summary": "Interested party", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(msg)

        # Contact should have phone, not email
        contacts = list_contacts()
        assert contacts["count"] == 1
        contact = contacts["contacts"][0]
        assert contact["phone"] == "+447999888777"
        assert contact["email"] is None
        assert "Signal" in contact["name"]

        # Interaction channel should be "signal"
        interactions = list_interactions()
        assert interactions["count"] == 1
        assert interactions["interactions"][0]["channel"] == "signal"

    def test_approve_action_logs_outbound_interaction(
        self, daemon_config, sample_pending_action,
    ):
        """Approving an action logs an outbound interaction in the real DB."""
        from tools.memory.db import list_contacts, list_interactions, list_memory

        orch = self._make_orchestrator(daemon_config)
        orch.pending["abc123"] = sample_pending_action

        # Mock email channel send success
        mock_email = Mock()
        mock_email.send.return_value = True
        orch.channels[ChannelType.EMAIL] = mock_email

        orch._approve_action("abc123")

        # Contact should have been created for the recipient
        contacts = list_contacts()
        assert contacts["count"] == 1
        assert contacts["contacts"][0]["email"] == "pdc@greenparty.org.uk"

        # Outbound interaction should be logged
        interactions = list_interactions()
        assert interactions["count"] == 1
        interaction = interactions["interactions"][0]
        assert interaction["direction"] == "outbound"
        assert interaction["subject"] == "Re: SEBE - Policy Proposal"

        # Event should be logged in memory_entries
        entries = list_memory(entry_type="event")
        assert entries["count"] >= 1
        event_contents = [e["content"] for e in entries["entries"]]
        assert any("Approved" in c for c in event_contents)

    def test_deny_action_creates_event_in_db(
        self, daemon_config, sample_pending_action,
    ):
        """Denying an action writes a real event row to the DB."""
        from tools.memory.db import list_memory

        orch = self._make_orchestrator(daemon_config)
        orch.pending["abc123"] = sample_pending_action

        orch._deny_action("abc123")

        entries = list_memory(entry_type="event")
        assert entries["count"] >= 1
        event_contents = [e["content"] for e in entries["entries"]]
        assert any("Denied" in c for c in event_contents)

    def test_expire_action_creates_event_in_db(
        self, daemon_config, sample_pending_action,
    ):
        """Expired actions write a real event row to the DB."""
        from tools.memory.db import list_memory

        orch = self._make_orchestrator(daemon_config)
        orch.config.approval_timeout = 1
        sample_pending_action.created_at = datetime.now() - timedelta(seconds=10)
        orch.pending["abc123"] = sample_pending_action

        orch._expire_actions()

        entries = list_memory(entry_type="event")
        assert entries["count"] >= 1
        event_contents = [e["content"] for e in entries["entries"]]
        assert any("expired" in c for c in event_contents)

    def test_full_message_flow_creates_daily_log(
        self, daemon_config, sample_inbound_email,
    ):
        """The dual-write memory system also writes to the daily log file."""
        orch = self._make_orchestrator(daemon_config)

        classification = {"needs_response": False, "summary": "Test message", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        # Process the message (triggers contact creation + interaction logging)
        orch._handle_message(sample_inbound_email)

        # Now deny a pending action to trigger _log_event (which dual-writes)
        from services.channels.base import PendingAction, OutboundMessage
        action = PendingAction(
            action_id="test99",
            action_type="reply_email",
            description="Test action",
            outbound=OutboundMessage(
                channel=ChannelType.EMAIL,
                recipient="test@example.com",
                subject="Test",
                body="Test body",
            ),
        )
        orch.pending["test99"] = action
        orch._deny_action("test99")

        # Check that a daily log file was created
        log_files = list(self._logs_dir.glob("*.md"))
        assert len(log_files) >= 1

        # Check that the log contains the denial event
        log_content = log_files[0].read_text()
        assert "Denied" in log_content

    def test_contact_last_contacted_updated(
        self, daemon_config, sample_inbound_email,
    ):
        """Logging an interaction updates the contact's last_contacted timestamp."""
        from tools.memory.db import add_contact, list_contacts

        # Pre-create contact with no last_contacted
        result = add_contact(name="PDC", email="pdc@greenparty.org.uk")
        assert result["success"]
        assert result["contact"]["last_contacted"] is None

        orch = self._make_orchestrator(daemon_config)
        classification = {"needs_response": False, "summary": "Test", "urgency": "normal"}
        orch._classify_message = Mock(return_value=classification)

        orch._handle_message(sample_inbound_email)

        # last_contacted should now be set
        contacts = list_contacts()
        assert contacts["contacts"][0]["last_contacted"] is not None
