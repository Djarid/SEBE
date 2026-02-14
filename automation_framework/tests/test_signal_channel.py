"""
Tests for services/channels/signal_channel.py.

Tests Signal channel adapter with mocked subprocess calls.
"""

import json
import pytest
import subprocess
from datetime import datetime
from unittest.mock import Mock, patch

from services.channels.base import ChannelType, InboundMessage, OutboundMessage
from services.channels.signal_channel import SignalChannel


def test_signal_channel_type(signal_config):
    """Test channel type is SIGNAL."""
    channel = SignalChannel(signal_config)
    assert channel.channel_type == ChannelType.SIGNAL


def test_run_signal_cli_success(signal_config):
    """Test successful signal-cli command."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = '{"ok":true}'
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        output = channel._run_signal_cli("receive")
    
    assert output == '{"ok":true}'


def test_run_signal_cli_failure(signal_config):
    """Test signal-cli command failure."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stderr = "error"
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        output = channel._run_signal_cli("receive")
    
    assert output is None


def test_run_signal_cli_not_found(signal_config):
    """Test signal-cli not found."""
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        channel = SignalChannel(signal_config)
        output = channel._run_signal_cli("receive")
    
    assert output is None


def test_run_signal_cli_timeout(signal_config):
    """Test signal-cli timeout."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)):
        channel = SignalChannel(signal_config)
        output = channel._run_signal_cli("receive")
    
    assert output is None


def test_poll_parses_messages(signal_config):
    """Test poll parses signal-cli JSON output."""
    json_output = json.dumps({
        "envelope": {
            "source": "+447000000002",
            "timestamp": 1708000000000,
            "dataMessage": {
                "message": "Hello from Signal",
            }
        }
    })
    
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = json_output
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        messages = channel.poll()
    
    assert len(messages) == 1
    assert messages[0].sender == "+447000000002"
    assert messages[0].body == "Hello from Signal"
    assert messages[0].channel == ChannelType.SIGNAL
    assert isinstance(messages[0].timestamp, datetime)


def test_poll_skips_receipts(signal_config):
    """Test poll skips non-data messages (receipts, typing, etc.)."""
    json_output = json.dumps({
        "envelope": {
            "source": "+447000000002",
            "timestamp": 1708000000000,
            "receiptMessage": {
                "type": "READ"
            }
        }
    })
    
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = json_output
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        messages = channel.poll()
    
    assert messages == []


def test_poll_empty(signal_config):
    """Test poll with empty output."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        messages = channel.poll()
    
    assert messages == []


def test_send_success(signal_config):
    """Test successful message send."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "success"
    
    outbound = OutboundMessage(
        channel=ChannelType.SIGNAL,
        recipient="+447000000002",
        subject="",
        body="Test message",
    )
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        result = channel.send(outbound)
    
    assert result is True


def test_send_failure(signal_config):
    """Test send failure."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stderr = "send failed"
    
    outbound = OutboundMessage(
        channel=ChannelType.SIGNAL,
        recipient="+447000000002",
        subject="",
        body="Test message",
    )
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        result = channel.send(outbound)
    
    assert result is False


def test_send_to_owner(signal_config):
    """Test send_to_owner convenience method."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "success"
    
    with patch("subprocess.run", return_value=mock_result):
        channel = SignalChannel(signal_config)
        result = channel.send_to_owner("Test notification")
    
    assert result is True


def test_send_to_owner_no_number(signal_config):
    """Test send_to_owner fails when no owner number configured."""
    signal_config.owner_number = ""
    
    channel = SignalChannel(signal_config)
    result = channel.send_to_owner("Test")
    
    assert result is False


def test_notify_with_action_id(signal_config):
    """Test notify includes approval commands."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "success"
    
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        channel = SignalChannel(signal_config)
        result = channel.notify("New message arrived", action_id="abc123")
    
    assert result is True
    
    # Check the message includes approval commands
    call_args = mock_run.call_args[0][0]
    message_text = call_args[call_args.index("-m") + 1]
    assert "APPROVE abc123" in message_text
    assert "DENY abc123" in message_text


def test_notify_without_action_id(signal_config):
    """Test notify without action ID (informational only)."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "success"
    
    with patch("subprocess.run", return_value=mock_result) as mock_run:
        channel = SignalChannel(signal_config)
        result = channel.notify("Informational message")
    
    assert result is True
    
    # Check the message does NOT include approval commands
    call_args = mock_run.call_args[0][0]
    message_text = call_args[call_args.index("-m") + 1]
    assert "APPROVE" not in message_text
    assert "DENY" not in message_text


def test_is_owner_message(signal_config):
    """Test is_owner_message checks sender."""
    channel = SignalChannel(signal_config)
    
    owner_msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender=signal_config.owner_number,
        subject="",
        body="APPROVE abc123",
        timestamp=datetime.now(),
        message_id="signal-123",
    )
    
    other_msg = InboundMessage(
        channel=ChannelType.SIGNAL,
        sender="+447000000999",
        subject="",
        body="Hello",
        timestamp=datetime.now(),
        message_id="signal-124",
    )
    
    assert channel.is_owner_message(owner_msg) is True
    assert channel.is_owner_message(other_msg) is False


def test_parse_command(signal_config):
    """Test command parsing."""
    channel = SignalChannel(signal_config)
    
    # Test various command formats
    assert channel.parse_command("APPROVE abc123") == ("APPROVE", ["abc123"])
    assert channel.parse_command("status") == ("STATUS", [])
    assert channel.parse_command("  deny  xyz  ") == ("DENY", ["xyz"])
    assert channel.parse_command("") == ("", [])
    assert channel.parse_command("SWAP qwen3") == ("SWAP", ["qwen3"])
    assert channel.parse_command("HELP") == ("HELP", [])


def test_is_available_no_account(signal_config):
    """Test is_available returns False when no account configured."""
    signal_config.account = ""
    
    channel = SignalChannel(signal_config)
    assert channel.is_available() is False
