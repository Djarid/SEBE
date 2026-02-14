"""
Tests for services/channels/email_channel.py.

Tests email channel adapter with mocked IMAP/SMTP.
"""

import email
import pytest
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import MagicMock, Mock, patch

from services.channels.base import ChannelType, OutboundMessage
from services.channels.email_channel import EmailChannel


def test_email_channel_type(email_config):
    """Test channel type is EMAIL."""
    channel = EmailChannel(email_config)
    assert channel.channel_type == ChannelType.EMAIL


def test_poll_no_unseen(email_config):
    """Test poll with no unseen messages."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b""])
    
    with patch("imaplib.IMAP4", return_value=mock_imap), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        messages = channel.poll()
    
    assert messages == []


def test_poll_with_messages(email_config):
    """Test poll with unseen messages."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1 2"])
    
    # Build minimal email
    email1 = (
        b"From: test1@example.com\r\n"
        b"Subject: Test 1\r\n"
        b"Date: Thu, 14 Feb 2026 12:00:00 +0000\r\n"
        b"\r\n"
        b"Body text 1"
    )
    email2 = (
        b"From: test2@example.com\r\n"
        b"Subject: Test 2\r\n"
        b"Date: Thu, 14 Feb 2026 12:00:00 +0000\r\n"
        b"\r\n"
        b"Body text 2"
    )
    
    mock_imap.fetch.side_effect = [
        ("OK", [(None, email1)]),
        ("OK", [(None, email2)]),
    ]
    
    with patch("imaplib.IMAP4", return_value=mock_imap), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        messages = channel.poll()
    
    assert len(messages) == 2
    assert messages[0].sender == "test1@example.com"
    assert messages[0].subject == "Test 1"
    assert messages[0].body == "Body text 1"
    assert messages[1].sender == "test2@example.com"


def test_poll_multipart_email(email_config):
    """Test poll with multipart email."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1"])
    
    # Build multipart email
    msg = MIMEMultipart("alternative")
    msg["From"] = "sender@example.com"
    msg["Subject"] = "Multipart Test"
    msg["Date"] = "Thu, 14 Feb 2026 12:00:00 +0000"
    msg.attach(MIMEText("Plain text body", "plain"))
    msg.attach(MIMEText("<html><body>HTML body</body></html>", "html"))
    
    email_bytes = msg.as_bytes()
    mock_imap.fetch.return_value = ("OK", [(None, email_bytes)])
    
    with patch("imaplib.IMAP4", return_value=mock_imap), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        messages = channel.poll()
    
    assert len(messages) == 1
    assert messages[0].body == "Plain text body"


def test_poll_html_only_email(email_config):
    """Test poll with HTML-only email."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1"])
    
    # Build HTML-only email
    msg = MIMEMultipart("alternative")
    msg["From"] = "sender@example.com"
    msg["Subject"] = "HTML Test"
    msg["Date"] = "Thu, 14 Feb 2026 12:00:00 +0000"
    msg.attach(MIMEText("<html><body>HTML body</body></html>", "html"))
    
    email_bytes = msg.as_bytes()
    mock_imap.fetch.return_value = ("OK", [(None, email_bytes)])
    
    with patch("imaplib.IMAP4", return_value=mock_imap), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        messages = channel.poll()
    
    assert len(messages) == 1
    assert "<html>" in messages[0].body


def test_poll_connection_failure(email_config):
    """Test poll handles connection failure gracefully."""
    with patch("imaplib.IMAP4", side_effect=Exception("Connection failed")):
        channel = EmailChannel(email_config)
        messages = channel.poll()
    
    assert messages == []


def test_poll_fetch_error(email_config):
    """Test poll handles fetch error for individual messages."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1 2"])
    
    # First fetch fails, second succeeds
    email2 = (
        b"From: test2@example.com\r\n"
        b"Subject: Test 2\r\n"
        b"Date: Thu, 14 Feb 2026 12:00:00 +0000\r\n"
        b"\r\n"
        b"Body text 2"
    )
    
    mock_imap.fetch.side_effect = [
        Exception("Fetch failed"),
        ("OK", [(None, email2)]),
    ]
    
    with patch("imaplib.IMAP4", return_value=mock_imap), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        messages = channel.poll()
    
    # Should get the second message only
    assert len(messages) == 1
    assert messages[0].sender == "test2@example.com"


def test_send_success(email_config):
    """Test successful email send."""
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = Mock(return_value=mock_smtp)
    mock_smtp.__exit__ = Mock(return_value=False)
    
    outbound = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="recipient@example.com",
        subject="Test Subject",
        body="Test body",
    )
    
    with patch("smtplib.SMTP", return_value=mock_smtp), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        result = channel.send(outbound)
    
    assert result is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once_with(
        email_config.username,
        email_config.password
    )
    mock_smtp.send_message.assert_called_once()


def test_send_with_reply_headers(email_config):
    """Test send includes reply headers."""
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = Mock(return_value=mock_smtp)
    mock_smtp.__exit__ = Mock(return_value=False)
    
    outbound = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="recipient@example.com",
        subject="Re: Test",
        body="Reply body",
        reply_to="<original-message-id>",
    )
    
    with patch("smtplib.SMTP", return_value=mock_smtp), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        channel.send(outbound)
    
    # Get the sent message
    sent_msg = mock_smtp.send_message.call_args[0][0]
    assert sent_msg["In-Reply-To"] == "<original-message-id>"
    assert sent_msg["References"] == "<original-message-id>"


def test_send_failure(email_config):
    """Test send handles SMTP exception."""
    import smtplib
    
    with patch("smtplib.SMTP", side_effect=smtplib.SMTPException("Send failed")):
        channel = EmailChannel(email_config)
        outbound = OutboundMessage(
            channel=ChannelType.EMAIL,
            recipient="recipient@example.com",
            subject="Test",
            body="Body",
        )
        result = channel.send(outbound)
    
    assert result is False


def test_is_available_true(email_config):
    """Test is_available returns True when IMAP connects."""
    mock_imap = MagicMock()
    mock_imap.noop.return_value = ("OK", [])
    
    with patch("imaplib.IMAP4", return_value=mock_imap), \
         patch("ssl.create_default_context"):
        channel = EmailChannel(email_config)
        assert channel.is_available() is True


def test_is_available_false(email_config):
    """Test is_available returns False on connection failure."""
    with patch("imaplib.IMAP4", side_effect=Exception("Connection failed")):
        channel = EmailChannel(email_config)
        assert channel.is_available() is False
