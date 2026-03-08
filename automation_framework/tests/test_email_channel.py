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

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
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

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
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

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
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

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert "HTML body" in messages[0].body
    assert "<html>" not in messages[0].body


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

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
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

    with (
        patch("smtplib.SMTP", return_value=mock_smtp),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        result = channel.send(outbound)

    assert result is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once_with(
        email_config.username, email_config.password
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

    with (
        patch("smtplib.SMTP", return_value=mock_smtp),
        patch("ssl.create_default_context"),
    ):
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

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        assert channel.is_available() is True


def test_is_available_false(email_config):
    """Test is_available returns False on connection failure."""
    with patch("imaplib.IMAP4", side_effect=Exception("Connection failed")):
        channel = EmailChannel(email_config)
        assert channel.is_available() is False


# ── save_draft tests ──────────────────────────────────────────────────────


def test_save_draft_success(email_config):
    """Test save_draft APPENDs to Drafts folder."""
    mock_imap = MagicMock()
    mock_imap.append.return_value = ("OK", [b"APPEND completed"])

    outbound = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="recipient@example.com",
        subject="Re: Test",
        body="Draft reply body",
        reply_to="<original-msg-id>",
    )

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        result = channel.save_draft(outbound)

    assert result is True
    mock_imap.append.assert_called_once()
    call_args = mock_imap.append.call_args
    assert call_args[0][0] == "Drafts"
    assert "\\Draft" in call_args[0][1]
    assert "\\Seen" in call_args[0][1]
    # Parse the appended MIME message and verify content
    raw_msg = call_args[0][3]
    parsed = email.message_from_bytes(raw_msg)
    assert parsed["To"] == "recipient@example.com"
    assert parsed["Subject"] == "Re: Test"
    assert parsed["In-Reply-To"] == "<original-msg-id>"
    assert parsed["X-SEBE-Draft"] == "true"
    # Extract plain text body from MIME
    body = ""
    for part in parsed.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode()
            break
    assert body == "Draft reply body"


def test_save_draft_failure(email_config):
    """Test save_draft returns False on IMAP APPEND failure."""
    mock_imap = MagicMock()
    mock_imap.append.return_value = ("NO", [b"APPEND failed"])

    outbound = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="recipient@example.com",
        subject="Re: Test",
        body="Draft body",
    )

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        result = channel.save_draft(outbound)

    assert result is False


def test_save_draft_connection_error(email_config):
    """Test save_draft handles connection errors gracefully."""
    with patch("imaplib.IMAP4", side_effect=Exception("Connection failed")):
        channel = EmailChannel(email_config)
        outbound = OutboundMessage(
            channel=ChannelType.EMAIL,
            recipient="recipient@example.com",
            subject="Re: Test",
            body="Draft body",
        )
        result = channel.save_draft(outbound)

    assert result is False


def test_save_draft_no_reply_to(email_config):
    """Test save_draft works without reply_to header."""
    mock_imap = MagicMock()
    mock_imap.append.return_value = ("OK", [b"APPEND completed"])

    outbound = OutboundMessage(
        channel=ChannelType.EMAIL,
        recipient="recipient@example.com",
        subject="New message",
        body="Draft body",
    )

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        result = channel.save_draft(outbound)

    assert result is True
    raw_msg = mock_imap.append.call_args[0][3]
    assert b"In-Reply-To" not in raw_msg


# ── _html_to_text unit tests ─────────────────────────────────────────────


from services.channels.email_channel import _html_to_text


def test_html_to_text_strips_tags():
    """Test basic HTML tag stripping."""
    html = "<html><body><p>Hello world</p></body></html>"
    result = _html_to_text(html)
    assert "Hello world" in result
    assert "<html>" not in result
    assert "<body>" not in result
    assert "<p>" not in result


def test_html_to_text_preserves_structure():
    """Test that block tags produce newlines."""
    html = "<div>Line one</div><div>Line two</div><br>Line three"
    result = _html_to_text(html)
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    assert lines == ["Line one", "Line two", "Line three"]


def test_html_to_text_strips_style_script():
    """Test that style and script content is removed."""
    html = (
        "<html><head><style>body { color: red; }</style></head>"
        "<body><script>alert('xss')</script>"
        "<p>Visible text</p></body></html>"
    )
    result = _html_to_text(html)
    assert "Visible text" in result
    assert "color: red" not in result
    assert "alert" not in result


def test_html_to_text_collapses_whitespace():
    """Test that excessive whitespace and blank lines are collapsed."""
    html = "<p>  First  </p><br><br><br><br><p>  Second  </p>"
    result = _html_to_text(html)
    # Should not have more than 2 consecutive newlines
    assert "\n\n\n" not in result
    assert "First" in result
    assert "Second" in result


def test_html_to_text_outlook_email():
    """Test with realistic Outlook-style HTML email."""
    html = (
        '<html><head><meta http-equiv="Content-Type" '
        'content="text/html; charset=Windows-1252">'
        '<style type="text/css" style="display:none;"> '
        "P {margin-top:0;margin-bottom:0;} </style></head>"
        '<body dir="ltr">'
        '<div style="font-family: Aptos; font-size: 12pt;">'
        "Hi Jason,</div>"
        '<div style="font-family: Aptos; font-size: 12pt;"><br></div>'
        '<div style="font-family: Aptos; font-size: 12pt;">'
        "Thanks for your email.</div>"
        "</body></html>"
    )
    result = _html_to_text(html)
    assert "Hi Jason," in result
    assert "Thanks for your email." in result
    assert "<div" not in result
    assert "font-family" not in result


# ── non-multipart HTML-only email ────────────────────────────────────────


def test_poll_non_multipart_html_email(email_config):
    """Test poll with a non-multipart HTML-only email."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1"])

    # Build a simple non-multipart HTML email
    raw = (
        b"From: sender@example.com\r\n"
        b"Subject: HTML Only\r\n"
        b"Date: Thu, 14 Feb 2026 12:00:00 +0000\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"\r\n"
        b"<html><body><p>Non-multipart HTML</p></body></html>"
    )
    mock_imap.fetch.return_value = ("OK", [(None, raw)])

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert "Non-multipart HTML" in messages[0].body
    assert "<html>" not in messages[0].body


# ── URL defanging and link extraction ────────────────────────────────────


def test_html_to_text_extracts_link_href():
    """Links with text different from the URL should append defanged href."""
    from services.channels.email_channel import _html_to_text

    html = '<p>Join via <a href="https://zoom.us/j/12345">Zoom link</a></p>'
    result = _html_to_text(html)
    assert "Zoom link" in result
    assert "hxxps://zoom[.]us/j/12345" in result
    assert "https://zoom.us" not in result


def test_html_to_text_deduplicates_url_as_link_text():
    """Links where the text IS the URL should not duplicate it."""
    from services.channels.email_channel import _html_to_text

    html = '<a href="https://example.com/path">https://example.com/path</a>'
    result = _html_to_text(html)
    assert result.count("example") == 1
    assert "hxxps://example[.]com/path" in result


def test_html_to_text_defangs_bare_urls():
    """Bare URLs not inside <a> tags should be defanged."""
    from services.channels.email_channel import _html_to_text

    html = "<p>Visit https://evil.com/phish for more</p>"
    result = _html_to_text(html)
    assert "hxxps://evil[.]com/phish" in result
    assert "https://evil.com" not in result


def test_html_to_text_no_urls_unchanged():
    """Text without URLs should pass through normally."""
    from services.channels.email_channel import _html_to_text

    html = "<p>No links here, just text.</p>"
    result = _html_to_text(html)
    assert result == "No links here, just text."


def test_html_to_text_real_email_structure():
    """Test with structure similar to a real meeting invite email."""
    from services.channels.email_channel import _html_to_text

    html = (
        "<div>Economy PWG<br>Monthly Meeting<br>"
        '<a href="https://zoom.us/j/97155298601?pwd=abc123">'
        "Zoom joining link</a><br>"
        "Meeting opens at 6:45pm</div>"
    )
    result = _html_to_text(html)
    assert "Economy PWG" in result
    assert "Zoom joining link" in result
    assert "hxxps://zoom[.]us/j/97155298601?pwd=abc123" in result
    assert "https://zoom.us" not in result
    assert "Meeting opens at 6:45pm" in result


def test_poll_plaintext_urls_defanged(email_config):
    """Plain-text email bodies should have URLs defanged."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1"])

    raw = (
        b"From: sender@example.com\r\n"
        b"Subject: Meeting Link\r\n"
        b"Date: Thu, 14 Feb 2026 12:00:00 +0000\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"\r\n"
        b"Join at https://zoom.us/j/12345 at 7pm"
    )
    mock_imap.fetch.return_value = ("OK", [(None, raw)])

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert "hxxps://zoom[.]us/j/12345" in messages[0].body
    assert "https://zoom.us" not in messages[0].body


def test_poll_html_email_urls_defanged(email_config):
    """HTML email bodies should have URLs defanged (both href and bare)."""
    mock_imap = MagicMock()
    mock_imap.select.return_value = ("OK", [])
    mock_imap.search.return_value = ("OK", [b"1"])

    msg = MIMEMultipart("alternative")
    msg["From"] = "sender@example.com"
    msg["Subject"] = "Meeting"
    msg["Date"] = "Thu, 14 Feb 2026 12:00:00 +0000"
    msg.attach(
        MIMEText(
            '<html><body><a href="https://zoom.us/j/999">Click here</a></body></html>',
            "html",
        )
    )

    mock_imap.fetch.return_value = ("OK", [(None, msg.as_bytes())])

    with (
        patch("imaplib.IMAP4", return_value=mock_imap),
        patch("ssl.create_default_context"),
    ):
        channel = EmailChannel(email_config)
        messages = channel.poll()

    assert len(messages) == 1
    assert "Click here" in messages[0].body
    assert "hxxps://zoom[.]us/j/999" in messages[0].body
    assert "https://zoom.us" not in messages[0].body
