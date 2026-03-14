"""
Tests for tools.conversations.importer — Conversation import orchestrator.

Tests import workflow: parse -> resolve participants -> create messages.
Uses in-memory database (same fixture pattern as other tests).
"""

import pytest
import sqlite3
from pathlib import Path
from unittest.mock import patch
from tempfile import NamedTemporaryFile

from tools.conversations.db import (
    _ensure_tables,
    list_conversations,
    list_messages,
    get_conversation_participants,
)
from tools.conversations.importer import import_conversation


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


class NonClosingConnection:
    """Wrapper that prevents close() from actually closing the connection."""

    def __init__(self, conn):
        self._conn = conn
        self._closed = False

    def close(self):
        # Don't actually close
        pass

    def __getattr__(self, name):
        return getattr(self._conn, name)


@pytest.fixture
def memory_conn():
    """In-memory SQLite connection with tables created."""
    real_conn = sqlite3.connect(":memory:")
    real_conn.row_factory = sqlite3.Row
    real_conn.execute("PRAGMA foreign_keys=ON")
    _ensure_tables(real_conn)

    # Wrap to prevent closing
    conn = NonClosingConnection(real_conn)

    yield conn

    # Actually close it at the end
    real_conn.close()


@pytest.fixture
def mock_get_connection(memory_conn):
    """Mock get_connection to return in-memory database - always returns same conn."""
    with patch("tools.conversations.db.get_connection") as mock:
        # Return the same connection object every time
        mock.return_value = memory_conn
        yield memory_conn


# ═══════════════════════════════════════════════════════════════════════════
# Test Data
# ═══════════════════════════════════════════════════════════════════════════


SAMPLE_WHATSAPP = """[10:00, 01/01/2026] Alice: Hello everyone
[10:01, 01/01/2026] +44 7700 900123: Hi Alice!
[10:02, 01/01/2026] Alice: This is a multi-line
message that continues here
[10:03, 01/01/2026] +44 7700 900123: Got it
[10:04, 01/01/2026] Bob: I'm Bob
[10:05, 01/01/2026] Alice: <Media omitted>"""


# ═══════════════════════════════════════════════════════════════════════════
# Basic Import Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_import_whatsapp_basic(mock_get_connection):
    """Test importing a small synthetic WhatsApp conversation."""
    # Create temporary file with sample data
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Test Campaign"
        )

        assert result["success"] is True
        assert result["messages_imported"] == 6  # Including system message
        assert result["campaign"] == "Test Campaign"
        assert result["conversation_id"] == 1

        # Should have 3 unique participants: Alice, phone number, Bob
        assert len(result["participants"]) == 3

        # Verify messages in database
        messages = list_messages(conversation_id=1)
        assert messages["success"] is True
        assert messages["count"] == 6

        # Verify participants (includes System participant for system messages)
        participants = get_conversation_participants(1)
        assert participants["success"] is True
        assert participants["count"] == 4  # Alice, phone, Bob, + System

    finally:
        Path(temp_path).unlink()


def test_import_with_contact_map(mock_get_connection):
    """Test that canonical_contact_id is set when contact_map provided."""
    # Create temporary file
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        # Import with contact mapping
        contact_map = {
            "Alice": 42,
            "+44 7700 900123": 99,
        }

        result = import_conversation(
            file_path=temp_path,
            platform="whatsapp",
            campaign="Test Campaign",
            contact_map=contact_map,
        )

        assert result["success"] is True

        # Check that participants have canonical_contact_id set
        cur = mock_get_connection.cursor()

        # Find Alice's participant
        cur.execute("""
            SELECT p.canonical_contact_id 
            FROM participants p
            JOIN participant_identities pi ON p.id = pi.participant_id
            WHERE pi.platform_user_id = 'Alice'
        """)
        alice = cur.fetchone()
        assert alice is not None
        assert alice[0] == 42

        # Find phone number participant
        cur.execute("""
            SELECT p.canonical_contact_id 
            FROM participants p
            JOIN participant_identities pi ON p.id = pi.participant_id
            WHERE pi.platform_user_id = '+44 7700 900123'
        """)
        phone = cur.fetchone()
        assert phone is not None
        assert phone[0] == 99

    finally:
        Path(temp_path).unlink()


def test_import_duplicate_detection(mock_get_connection):
    """Test that second import of same campaign fails without force flag."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        # First import
        result1 = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Duplicate Test"
        )
        assert result1["success"] is True

        # Second import without force (should fail)
        result2 = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Duplicate Test"
        )

        assert result2["success"] is False
        assert "already exists" in result2["error"]
        assert "force" in result2["error"]
        assert "existing_conversation_id" in result2

    finally:
        Path(temp_path).unlink()


def test_import_force_reimport(mock_get_connection):
    """Test that force=True allows reimporting over existing conversation."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        # First import
        result1 = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Force Test"
        )
        assert result1["success"] is True
        conv_id_1 = result1["conversation_id"]

        # Second import with force=True (should succeed)
        result2 = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Force Test", force=True
        )

        assert result2["success"] is True

        # Should have created new conversation (old one deleted)
        conv_id_2 = result2["conversation_id"]

        # Check that only one conversation exists for this campaign
        convs = list_conversations(campaign="Force Test")
        assert convs["count"] == 1
        assert convs["conversations"][0]["id"] == conv_id_2

        # Old conversation should be gone
        cur = mock_get_connection.cursor()
        cur.execute("SELECT id FROM conversations WHERE id = ?", (conv_id_1,))
        assert cur.fetchone() is None

    finally:
        Path(temp_path).unlink()


def test_import_nonexistent_file(mock_get_connection):
    """Test graceful error when file doesn't exist."""
    result = import_conversation(
        file_path="/tmp/definitely_does_not_exist_12345.txt",
        platform="whatsapp",
        campaign="Test",
    )

    assert result["success"] is False
    assert "not found" in result["error"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# Additional Import Features
# ═══════════════════════════════════════════════════════════════════════════


def test_import_with_subject(mock_get_connection):
    """Test that subject field is set correctly."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path,
            platform="whatsapp",
            campaign="Test",
            subject="SEBE Policy Discussion",
        )

        assert result["success"] is True

        # Check subject in database
        convs = list_conversations(campaign="Test")
        assert convs["conversations"][0]["subject"] == "SEBE Policy Discussion"

    finally:
        Path(temp_path).unlink()


def test_import_conversation_type(mock_get_connection):
    """Test that conversation_type parameter is respected."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path,
            platform="whatsapp",
            campaign="Test",
            conversation_type="dm",
        )

        assert result["success"] is True

        # Check type in database
        convs = list_conversations(campaign="Test")
        assert convs["conversations"][0]["conversation_type"] == "dm"

    finally:
        Path(temp_path).unlink()


def test_import_system_messages(mock_get_connection):
    """Test that system messages are imported with special participant."""
    system_chat = """[10:00, 01/01/2026] Alice: Hello
[10:01, 01/01/2026] Alice: <Media omitted>
[10:02, 01/01/2026] Bob: Hi"""

    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(system_chat)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="System Test"
        )

        assert result["success"] is True
        assert result["messages_imported"] == 3

        # Check that System participant was created
        participants = get_conversation_participants(result["conversation_id"])
        participant_names = [p["display_name"] for p in participants["participants"]]
        assert "System" in participant_names

        # Check message attribution
        messages = list_messages(conversation_id=result["conversation_id"])

        # Find the system message
        system_msgs = [
            m for m in messages["messages"] if "omitted" in m["content_text"]
        ]
        assert len(system_msgs) == 1
        assert system_msgs[0]["attribution_level"] == "anonymous"

    finally:
        Path(temp_path).unlink()


def test_import_participant_stats(mock_get_connection):
    """Test that participant message counts are tracked correctly."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Stats Test"
        )

        assert result["success"] is True

        # Check participant stats in result
        participants = result["participants"]

        # Alice should have most messages (3 non-system + 1 system = but system not counted)
        alice = next(p for p in participants if "Alice" in p["name"])
        assert (
            alice["messages"] == 2
        )  # 2 non-system messages (system message goes to System participant)

    finally:
        Path(temp_path).unlink()


def test_import_empty_file(mock_get_connection):
    """Test handling of empty file."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("")
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Empty Test"
        )

        assert result["success"] is False
        assert "No messages found" in result["error"]

    finally:
        Path(temp_path).unlink()


def test_import_preamble_only(mock_get_connection):
    """Test file with only preamble (no timestamped messages)."""
    preamble_only = """Messages and calls are end-to-end encrypted.
Some other text."""

    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(preamble_only)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Preamble Test"
        )

        # Parser returns empty list for preamble-only files
        assert result["success"] is False
        assert "No messages found" in result["error"]

    finally:
        Path(temp_path).unlink()


def test_import_timestamps_preserved(mock_get_connection):
    """Test that message timestamps are correctly imported."""
    with NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(SAMPLE_WHATSAPP)
        temp_path = f.name

    try:
        result = import_conversation(
            file_path=temp_path, platform="whatsapp", campaign="Timestamp Test"
        )

        assert result["success"] is True

        # Get messages and check timestamps
        messages = list_messages(conversation_id=result["conversation_id"])

        # Messages are returned in DESC order, so reverse for chronological
        sorted_messages = sorted(
            messages["messages"], key=lambda m: m["platform_timestamp"]
        )

        # First message should be 10:00
        assert "10:00:00" in sorted_messages[0]["platform_timestamp"]
        # Last non-system should be 10:04 (Bob's message)
        last_msg = [m for m in sorted_messages if "omitted" not in m["content_text"]][
            -1
        ]
        assert "10:04:00" in last_msg["platform_timestamp"]

    finally:
        Path(temp_path).unlink()
