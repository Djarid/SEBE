"""
Tests for services/channels/signal_channel.py.

Tests Signal channel adapter with mocked HTTP calls to the
signal-cli REST API container.
"""

import json
import pytest
from datetime import datetime
from email.message import Message as HTTPMessage
from io import BytesIO
from unittest.mock import Mock, patch, MagicMock
from urllib.error import HTTPError, URLError

from services.channels.base import ChannelType, InboundMessage, OutboundMessage
from services.channels.signal_channel import SignalChannel


# ── Helpers ────────────────────────────────────────────────────────────────

def _mock_response(data, status=200):
    """Create a mock HTTP response for urlopen."""
    body = json.dumps(data).encode("utf-8") if data is not None else b""
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__ = Mock(return_value=resp)
    resp.__exit__ = Mock(return_value=False)
    return resp


# ── Basic tests ────────────────────────────────────────────────────────────

def test_signal_channel_type(signal_config):
    """Test channel type is SIGNAL."""
    channel = SignalChannel(signal_config)
    assert channel.channel_type == ChannelType.SIGNAL


def test_base_url_strips_trailing_slash(signal_config):
    """Test that trailing slash is stripped from api_url."""
    signal_config.api_url = "http://localhost:8082/"
    channel = SignalChannel(signal_config)
    assert channel._base_url == "http://localhost:8082"


# ── HTTP helper tests ──────────────────────────────────────────────────────

def test_get_success(signal_config):
    """Test successful GET request."""
    mock_resp = _mock_response({"version": "0.97"})

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        result = channel._get("/v1/about")

    assert result == {"version": "0.97"}


def test_get_http_error(signal_config):
    """Test GET with HTTP error returns None."""
    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=HTTPError("http://x", 500, "Server Error", HTTPMessage(), None),
    ):
        channel = SignalChannel(signal_config)
        result = channel._get("/v1/about")

    assert result is None


def test_get_url_error(signal_config):
    """Test GET with connection error returns None."""
    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=URLError("Connection refused"),
    ):
        channel = SignalChannel(signal_config)
        result = channel._get("/v1/about")

    assert result is None


def test_post_success(signal_config):
    """Test successful POST request."""
    mock_resp = _mock_response({"timestamp": "12345"})

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        result = channel._post("/v2/send", {"message": "test"})

    assert result == {"timestamp": "12345"}


def test_post_http_error(signal_config):
    """Test POST with HTTP error returns None."""
    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=HTTPError("http://x", 400, "Bad Request", HTTPMessage(), None),
    ):
        channel = SignalChannel(signal_config)
        result = channel._post("/v2/send", {"message": "test"})

    assert result is None


def test_post_url_error(signal_config):
    """Test POST with connection error returns None."""
    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=URLError("Connection refused"),
    ):
        channel = SignalChannel(signal_config)
        result = channel._post("/v2/send", {"message": "test"})

    assert result is None


# ── Poll tests ─────────────────────────────────────────────────────────────

def test_poll_parses_messages(signal_config):
    """Test poll parses signal-cli REST API JSON output."""
    api_response = [
        {
            "envelope": {
                "source": "+447000000002",
                "timestamp": 1708000000000,
                "dataMessage": {
                    "message": "Hello from Signal",
                },
            }
        }
    ]
    mock_resp = _mock_response(api_response)

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert messages[0].sender == "+447000000002"
    assert messages[0].body == "Hello from Signal"
    assert messages[0].channel == ChannelType.SIGNAL
    assert isinstance(messages[0].timestamp, datetime)


def test_poll_skips_receipts(signal_config):
    """Test poll skips non-data messages (receipts, typing, etc.)."""
    api_response = [
        {
            "envelope": {
                "source": "+447000000002",
                "timestamp": 1708000000000,
                "receiptMessage": {"type": "READ"},
            }
        }
    ]
    mock_resp = _mock_response(api_response)

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert messages == []


def test_poll_empty(signal_config):
    """Test poll with empty response."""
    mock_resp = _mock_response([])

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert messages == []


def test_poll_api_failure(signal_config):
    """Test poll returns empty list on API failure."""
    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=URLError("Connection refused"),
    ):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert messages == []


def test_poll_multiple_messages(signal_config):
    """Test poll handles multiple messages correctly."""
    api_response = [
        {
            "envelope": {
                "source": "+447000000002",
                "timestamp": 1708000000000,
                "dataMessage": {"message": "First message"},
            }
        },
        {
            "envelope": {
                "source": "+447000000003",
                "timestamp": 1708000001000,
                "dataMessage": {"message": "Second message"},
            }
        },
        {
            "envelope": {
                "source": "+447000000002",
                "timestamp": 1708000002000,
                "receiptMessage": {"type": "DELIVERY"},
            }
        },
    ]
    mock_resp = _mock_response(api_response)

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert len(messages) == 2
    assert messages[0].body == "First message"
    assert messages[1].body == "Second message"


def test_poll_group_message(signal_config):
    """Test poll handles group messages with thread_id."""
    api_response = [
        {
            "envelope": {
                "source": "+447000000002",
                "timestamp": 1708000000000,
                "dataMessage": {
                    "message": "Group msg",
                    "groupInfo": {"groupId": "group-abc123"},
                },
            }
        }
    ]
    mock_resp = _mock_response(api_response)

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert messages[0].thread_id == "group-abc123"


# ── Send tests ─────────────────────────────────────────────────────────────

def test_send_success(signal_config):
    """Test successful message send."""
    mock_resp = _mock_response({"timestamp": "12345"})

    outbound = OutboundMessage(
        channel=ChannelType.SIGNAL,
        recipient="+447000000002",
        subject="",
        body="Test message",
    )

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp) as mock_urlopen:
        channel = SignalChannel(signal_config)
        result = channel.send(outbound)

    assert result is True

    # Verify the POST payload
    call_args = mock_urlopen.call_args
    req = call_args[0][0]
    payload = json.loads(req.data.decode("utf-8"))
    assert payload["message"] == "Test message"
    assert payload["number"] == "+447000000000"
    assert payload["recipients"] == ["+447000000002"]


def test_send_failure(signal_config):
    """Test send failure."""
    outbound = OutboundMessage(
        channel=ChannelType.SIGNAL,
        recipient="+447000000002",
        subject="",
        body="Test message",
    )

    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=HTTPError("http://x", 500, "Error", HTTPMessage(), None),
    ):
        channel = SignalChannel(signal_config)
        result = channel.send(outbound)

    assert result is False


def test_send_to_owner(signal_config):
    """Test send_to_owner convenience method."""
    mock_resp = _mock_response({"timestamp": "12345"})

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        result = channel.send_to_owner("Test notification")

    assert result is True


def test_send_to_owner_no_number(signal_config):
    """Test send_to_owner fails when no owner number configured."""
    signal_config.owner_number = ""

    channel = SignalChannel(signal_config)
    result = channel.send_to_owner("Test")

    assert result is False


# ── Notify tests ───────────────────────────────────────────────────────────

def test_notify_with_action_id(signal_config):
    """Test notify includes approval commands."""
    mock_resp = _mock_response({"timestamp": "12345"})

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp) as mock_urlopen:
        channel = SignalChannel(signal_config)
        result = channel.notify("New message arrived", action_id="abc123")

    assert result is True

    # Check the message includes approval commands
    req = mock_urlopen.call_args[0][0]
    payload = json.loads(req.data.decode("utf-8"))
    assert "APPROVE abc123" in payload["message"]
    assert "DENY abc123" in payload["message"]


def test_notify_without_action_id(signal_config):
    """Test notify without action ID (informational only)."""
    mock_resp = _mock_response({"timestamp": "12345"})

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp) as mock_urlopen:
        channel = SignalChannel(signal_config)
        result = channel.notify("Informational message")

    assert result is True

    # Check the message does NOT include approval commands
    req = mock_urlopen.call_args[0][0]
    payload = json.loads(req.data.decode("utf-8"))
    assert "APPROVE" not in payload["message"]
    assert "DENY" not in payload["message"]


# ── Availability tests ────────────────────────────────────────────────────

def test_is_available_true(signal_config):
    """Test is_available returns True when API responds."""
    mock_resp = _mock_response({"versions": ["v1", "v2"]})

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        assert channel.is_available() is True


def test_is_available_false_no_account(signal_config):
    """Test is_available returns False when no account configured."""
    signal_config.account = ""

    channel = SignalChannel(signal_config)
    assert channel.is_available() is False


def test_is_available_false_api_down(signal_config):
    """Test is_available returns False when API is unreachable."""
    with patch(
        "services.channels.signal_channel.urlopen",
        side_effect=URLError("Connection refused"),
    ):
        channel = SignalChannel(signal_config)
        assert channel.is_available() is False


# ── Owner/command tests ───────────────────────────────────────────────────

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
    """Test command parsing with /sebe prefix."""
    channel = SignalChannel(signal_config)

    # With prefix
    assert channel.parse_command("/sebe APPROVE abc123") == ("APPROVE", ["abc123"])
    assert channel.parse_command("/sebe status") == ("STATUS", [])
    assert channel.parse_command("  /sebe  deny  xyz  ") == ("DENY", ["xyz"])
    assert channel.parse_command("/sebe SWAP qwen3") == ("SWAP", ["qwen3"])
    assert channel.parse_command("/sebe HELP") == ("HELP", [])
    assert channel.parse_command("/SEBE STATUS") == ("STATUS", [])

    # Without prefix (still works, prefix is stripped if present)
    assert channel.parse_command("APPROVE abc123") == ("APPROVE", ["abc123"])
    assert channel.parse_command("status") == ("STATUS", [])
    assert channel.parse_command("") == ("", [])


def test_is_command(signal_config):
    """Test is_command checks for /sebe prefix."""
    channel = SignalChannel(signal_config)

    def _msg(body):
        return InboundMessage(
            channel=ChannelType.SIGNAL,
            sender="+447000000001",
            subject="",
            body=body,
            timestamp=datetime.now(),
            message_id="test",
        )

    assert channel.is_command(_msg("/sebe STATUS")) is True
    assert channel.is_command(_msg("/SEBE status")) is True
    assert channel.is_command(_msg("  /sebe HELP  ")) is True
    assert channel.is_command(_msg("STATUS")) is False
    assert channel.is_command(_msg("hello there")) is False
    assert channel.is_command(_msg("")) is False


def test_poll_sync_message(signal_config):
    """Test poll handles syncMessage.sentMessage (owner commands from phone)."""
    api_response = [
        {
            "envelope": {
                "source": "+447000000001",
                "timestamp": 1708000000000,
                "syncMessage": {
                    "sentMessage": {
                        "message": "/sebe STATUS",
                        "destination": "+447000000001",
                        "timestamp": 1708000000000,
                    }
                },
            }
        }
    ]
    mock_resp = _mock_response(api_response)

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert messages[0].body == "/sebe STATUS"
    assert messages[0].sender == "+447000000001"
    assert messages[0].channel == ChannelType.SIGNAL


def test_poll_sync_read_receipt_ignored(signal_config):
    """Test poll ignores syncMessage with only readMessages (no sentMessage)."""
    api_response = [
        {
            "envelope": {
                "source": "+447000000001",
                "timestamp": 1708000000000,
                "syncMessage": {
                    "readMessages": [
                        {
                            "sender": "+447000000001",
                            "timestamp": 1708000000000,
                        }
                    ]
                },
            }
        }
    ]
    mock_resp = _mock_response(api_response)

    with patch("services.channels.signal_channel.urlopen", return_value=mock_resp):
        channel = SignalChannel(signal_config)
        messages = channel.poll()

    assert messages == []
