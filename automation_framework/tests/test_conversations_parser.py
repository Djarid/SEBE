"""
Tests for tools.conversations.parser — Platform-specific chat parsers.

Pure function tests for parsing chat export formats.
No database dependencies.
"""

import pytest
from pathlib import Path
from datetime import datetime

from tools.conversations.parser import (
    parse,
    parse_whatsapp,
    ParsedMessage,
    PARSERS,
)


# ═══════════════════════════════════════════════════════════════════════════
# Basic Parsing Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_parse_whatsapp_basic():
    """Test parsing a simple 3-line WhatsApp conversation."""
    text = """[10:00, 01/01/2026] Alice: Hello everyone
[10:01, 01/01/2026] Bob: Hi Alice!
[10:02, 01/01/2026] Alice: How are you?"""

    messages = parse("whatsapp", text)

    assert len(messages) == 3
    assert messages[0].sender_raw == "Alice"
    assert messages[0].content == "Hello everyone"
    assert messages[0].timestamp == datetime(2026, 1, 1, 10, 0)
    assert messages[0].is_system is False

    assert messages[1].sender_raw == "Bob"
    assert messages[1].content == "Hi Alice!"

    assert messages[2].sender_raw == "Alice"
    assert messages[2].content == "How are you?"


def test_parse_whatsapp_multiline():
    """Test parsing a message spanning multiple lines."""
    text = """[10:00, 01/01/2026] Alice: This is a long message
that continues on the next line
and even a third line
[10:01, 01/01/2026] Bob: Got it"""

    messages = parse("whatsapp", text)

    assert len(messages) == 2
    assert messages[0].sender_raw == "Alice"
    assert (
        messages[0].content
        == "This is a long message\nthat continues on the next line\nand even a third line"
    )
    assert messages[1].sender_raw == "Bob"
    assert messages[1].content == "Got it"


def test_parse_whatsapp_phone_sender():
    """Test parsing with phone number as sender."""
    text = """[10:00, 01/01/2026] +44 7700 900123: Hello
[10:01, 01/01/2026] +44 7977 490410: Hi there"""

    messages = parse("whatsapp", text)

    assert len(messages) == 2
    assert messages[0].sender_raw == "+44 7700 900123"
    assert messages[0].content == "Hello"
    assert messages[1].sender_raw == "+44 7977 490410"
    assert messages[1].content == "Hi there"


def test_parse_whatsapp_named_sender():
    """Test parsing with display name as sender."""
    text = """[10:00, 01/01/2026] Jason Huxley: SEBE is brilliant
[10:01, 01/01/2026] Alice Smith: Agreed!"""

    messages = parse("whatsapp", text)

    assert len(messages) == 2
    assert messages[0].sender_raw == "Jason Huxley"
    assert messages[0].content == "SEBE is brilliant"
    assert messages[1].sender_raw == "Alice Smith"


def test_parse_whatsapp_system_message():
    """Test detection of system messages like '<Media omitted>'."""
    text = """[10:00, 01/01/2026] Alice: Here's a photo
[10:01, 01/01/2026] Alice: <Media omitted>
[10:02, 01/01/2026] Bob: Thanks!
[10:03, 01/01/2026] Bob: This message was deleted"""

    messages = parse("whatsapp", text)

    assert len(messages) == 4
    assert messages[0].is_system is False
    assert messages[1].is_system is True
    assert messages[1].content == "<Media omitted>"
    assert messages[2].is_system is False
    assert messages[3].is_system is True
    assert messages[3].content == "This message was deleted"


def test_parse_whatsapp_preamble():
    """Test handling of lines before first timestamp."""
    text = """Messages and calls are end-to-end encrypted. No one outside of this chat can read or listen to them.
Some other preamble text
[10:00, 01/01/2026] Alice: First real message
[10:01, 01/01/2026] Bob: Second message"""

    messages = parse("whatsapp", text)

    # Should have preamble message + 2 real messages
    assert len(messages) == 3

    # First message should be the preamble (marked as system)
    assert messages[0].sender_raw == "Unknown"
    assert messages[0].is_system is True
    assert "end-to-end encrypted" in messages[0].content
    assert messages[0].timestamp == datetime(
        2026, 1, 1, 0, 0
    )  # Midnight on first message date

    # Real messages follow
    assert messages[1].sender_raw == "Alice"
    assert messages[1].content == "First real message"
    assert messages[2].sender_raw == "Bob"


def test_parse_empty_text():
    """Test parsing empty string returns empty list."""
    messages = parse("whatsapp", "")
    assert messages == []


def test_parse_unknown_platform():
    """Test that unknown platform raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        parse("unknown_platform", "some text")

    assert "No parser for platform 'unknown_platform'" in str(exc_info.value)


def test_parser_registry():
    """Test that 'whatsapp' is registered in PARSERS."""
    assert "whatsapp" in PARSERS
    assert callable(PARSERS["whatsapp"])
    assert PARSERS["whatsapp"] == parse_whatsapp


# ═══════════════════════════════════════════════════════════════════════════
# Real File Test (Optional)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.skipif(
    not Path("../../drafts/thread.txt").exists(), reason="thread.txt not available"
)
def test_parse_whatsapp_real_file():
    """Test parsing the actual WhatsApp thread.txt file."""
    text = Path("../../drafts/thread.txt").read_text()
    messages = parse("whatsapp", text)

    # We know it has ~160 messages
    assert len(messages) > 100

    # Check we have at least 5 real senders (not system)
    senders = set(m.sender_raw for m in messages if not m.is_system)
    assert "Jason Huxley" in senders
    assert len(senders) >= 5

    # Check timestamps are parsed correctly
    assert all(isinstance(m.timestamp, datetime) for m in messages)

    # Check we have some system messages
    system_messages = [m for m in messages if m.is_system]
    assert len(system_messages) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


def test_parse_whatsapp_colons_in_content():
    """Test that colons within message content don't break parsing."""
    text = """[10:00, 01/01/2026] Alice: The time is 10:00 and the ratio is 3:1
[10:01, 01/01/2026] Bob: URL: https://example.com"""

    messages = parse("whatsapp", text)

    assert len(messages) == 2
    assert messages[0].content == "The time is 10:00 and the ratio is 3:1"
    assert messages[1].content == "URL: https://example.com"


def test_parse_whatsapp_empty_lines():
    """Test that empty lines are handled correctly."""
    text = """[10:00, 01/01/2026] Alice: Message one

[10:01, 01/01/2026] Bob: Message two"""

    messages = parse("whatsapp", text)

    # Empty lines should not create messages
    assert len(messages) == 2
    assert messages[0].content == "Message one"
    assert messages[1].content == "Message two"


def test_parse_whatsapp_sender_with_special_chars():
    """Test parsing sender names with special characters."""
    text = """[10:00, 01/01/2026] O'Brien: Hello
[10:01, 01/01/2026] José García: Hola
[10:02, 01/01/2026] 李明: 你好"""

    messages = parse("whatsapp", text)

    assert len(messages) == 3
    assert messages[0].sender_raw == "O'Brien"
    assert messages[1].sender_raw == "José García"
    assert messages[2].sender_raw == "李明"


def test_parse_whatsapp_joined_left_messages():
    """Test system messages within regular messages."""
    # WhatsApp join/leave events appear in message content, not as separate timestamp lines
    text = """[10:00, 01/01/2026] System: Alice joined using this group's invite link
[10:01, 01/01/2026] Bob: Welcome Alice!
[10:02, 01/01/2026] System: Charlie left"""

    messages = parse("whatsapp", text)

    assert len(messages) == 3
    assert messages[0].is_system is True
    assert "joined" in messages[0].content
    assert messages[1].is_system is False
    assert messages[2].is_system is True
    assert "left" in messages[2].content


def test_parsed_message_line_numbers():
    """Test that line numbers are tracked correctly."""
    text = """[10:00, 01/01/2026] Alice: Line 1
[10:01, 01/01/2026] Bob: Line 2
[10:02, 01/01/2026] Charlie: Line 3"""

    messages = parse("whatsapp", text)

    assert messages[0].line_number == 1
    assert messages[1].line_number == 2
    assert messages[2].line_number == 3


def test_parsed_message_multiline_line_numbers():
    """Test line numbers for multi-line messages."""
    text = """[10:00, 01/01/2026] Alice: First line
continues here
and here
[10:01, 01/01/2026] Bob: Single line"""

    messages = parse("whatsapp", text)

    # First message starts at line 1
    assert messages[0].line_number == 1
    # Second message starts at line 4
    assert messages[1].line_number == 4
