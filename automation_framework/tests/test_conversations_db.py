"""
Tests for tools.conversations.db — SQLite CRUD operations.

All tests use in-memory databases to avoid touching the real database.
Tests cover participants, identities, conversations, messages, and search.
"""

import pytest
import sqlite3
from unittest.mock import patch

from tools.conversations.db import (
    _ensure_tables,
    _row_to_dict,
    _content_hash,
    add_participant,
    add_identity,
    resolve_participant,
    update_participant,
    create_conversation,
    add_message,
    tag_message,
    search_messages,
    list_conversations,
    list_messages,
    get_conversation_participants,
    get_stats,
)


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
# Schema & Setup Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_ensure_tables(memory_conn):
    """Verify all 5 tables + FTS5 exist with correct schema."""
    cur = memory_conn.cursor()

    # Check main tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]

    assert "participants" in tables
    assert "participant_identities" in tables
    assert "conversations" in tables
    assert "messages" in tables
    assert "message_tags" in tables
    assert "message_search" in tables  # FTS5 virtual table

    # Verify participants schema
    cur.execute("PRAGMA table_info(participants)")
    columns = {row[1] for row in cur.fetchall()}
    assert "id" in columns
    assert "display_name" in columns
    assert "organisation" in columns
    assert "canonical_contact_id" in columns
    assert "notes" in columns
    assert "created_at" in columns
    assert "updated_at" in columns

    # Verify FTS5 table exists and has correct columns
    cur.execute("PRAGMA table_info(message_search)")
    fts_columns = {row[1] for row in cur.fetchall()}
    assert "content" in fts_columns
    assert "participant_name" in fts_columns
    assert "conversation_subject" in fts_columns
    assert "campaign" in fts_columns


# ═══════════════════════════════════════════════════════════════════════════
# Participant Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_add_participant(mock_get_connection):
    """Test basic participant creation."""
    result = add_participant(
        display_name="Alice Smith",
        organisation="Green Party",
        notes="Met at conference",
    )

    assert result["success"] is True
    assert result["participant"]["display_name"] == "Alice Smith"
    assert result["participant"]["organisation"] == "Green Party"
    assert result["participant"]["notes"] == "Met at conference"
    assert result["participant"]["id"] == 1


def test_add_participant_with_contact_link(mock_get_connection):
    """Test participant creation with canonical_contact_id."""
    result = add_participant(display_name="Bob Jones", canonical_contact_id=42)

    assert result["success"] is True
    assert result["participant"]["canonical_contact_id"] == 42
    assert result["participant"]["display_name"] == "Bob Jones"


def test_add_identity(mock_get_connection):
    """Test adding a platform identity to a participant."""
    # Create participant first
    p_result = add_participant(display_name="Charlie Brown")
    participant_id = p_result["participant"]["id"]

    # Add identity
    result = add_identity(
        participant_id=participant_id,
        platform="whatsapp",
        platform_user_id="+44 7700 900123",
        display_name="Charlie",
    )

    assert result["success"] is True
    assert result["identity"]["participant_id"] == participant_id
    assert result["identity"]["platform"] == "whatsapp"
    assert result["identity"]["platform_user_id"] == "+44 7700 900123"
    assert result["identity"]["display_name"] == "Charlie"


def test_add_identity_unique_constraint(mock_get_connection):
    """Test that duplicate platform+user_id fails gracefully."""
    # Create participant and identity
    p_result = add_participant(display_name="Dave")
    participant_id = p_result["participant"]["id"]

    i_result = add_identity(
        participant_id=participant_id,
        platform="whatsapp",
        platform_user_id="+44 7700 900456",
    )
    assert i_result["success"] is True

    # Try to add same identity again (should fail)
    i_result2 = add_identity(
        participant_id=participant_id,
        platform="whatsapp",
        platform_user_id="+44 7700 900456",
    )

    assert i_result2["success"] is False
    assert "already exists" in i_result2["error"]


def test_resolve_participant_creates_new(mock_get_connection):
    """Test resolve_participant creates new participant on first call."""
    result = resolve_participant(
        platform="whatsapp", platform_user_id="+44 7700 900789"
    )

    assert result["success"] is True
    assert result["created"] is True
    assert result["participant_id"] == 1
    assert result["identity"]["platform"] == "whatsapp"
    assert result["identity"]["platform_user_id"] == "+44 7700 900789"


def test_resolve_participant_returns_existing(mock_get_connection):
    """Test resolve_participant returns existing participant on second call."""
    # First call creates
    result1 = resolve_participant(
        platform="whatsapp", platform_user_id="+44 7700 900999"
    )
    participant_id = result1["participant_id"]

    # Second call returns same
    result2 = resolve_participant(
        platform="whatsapp", platform_user_id="+44 7700 900999"
    )

    assert result2["success"] is True
    assert result2["created"] is False
    assert result2["participant_id"] == participant_id


# ═══════════════════════════════════════════════════════════════════════════
# Conversation Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_create_conversation(mock_get_connection):
    """Test basic conversation creation."""
    result = create_conversation(
        platform="whatsapp", conversation_type="group", subject="SEBE Policy Discussion"
    )

    assert result["success"] is True
    assert result["conversation"]["platform"] == "whatsapp"
    assert result["conversation"]["conversation_type"] == "group"
    assert result["conversation"]["subject"] == "SEBE Policy Discussion"
    assert result["conversation"]["id"] == 1


def test_create_conversation_with_campaign(mock_get_connection):
    """Test conversation creation with campaign field."""
    result = create_conversation(
        platform="whatsapp",
        conversation_type="group",
        subject="Tech Review",
        campaign="Sci Tech SEBE Review",
    )

    assert result["success"] is True
    assert result["conversation"]["campaign"] == "Sci Tech SEBE Review"
    assert result["conversation"]["subject"] == "Tech Review"


# ═══════════════════════════════════════════════════════════════════════════
# Message Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_add_message(mock_get_connection):
    """Test basic message creation."""
    # Create conversation and participant
    conv = create_conversation(platform="whatsapp", conversation_type="group")
    conv_id = conv["conversation"]["id"]

    part = add_participant(display_name="Alice")
    part_id = part["participant"]["id"]

    # Add message
    result = add_message(
        conversation_id=conv_id,
        participant_id=part_id,
        content_text="SEBE is a brilliant policy idea",
        platform_timestamp="2026-03-12 10:30:00",
    )

    assert result["success"] is True
    assert result["message"]["content_text"] == "SEBE is a brilliant policy idea"
    assert result["message"]["conversation_id"] == conv_id
    assert result["message"]["participant_id"] == part_id


def test_add_message_updates_fts(mock_get_connection):
    """Test that adding a message updates FTS5 search index."""
    # Create conversation and participant
    conv = create_conversation(
        platform="whatsapp",
        conversation_type="group",
        subject="Policy Chat",
        campaign="SEBE Review",
    )
    conv_id = conv["conversation"]["id"]

    part = add_participant(display_name="Bob")
    part_id = part["participant"]["id"]

    # Add message
    add_message(
        conversation_id=conv_id,
        participant_id=part_id,
        content_text="The automation tax revenue model is solid",
        platform_timestamp="2026-03-12 10:45:00",
    )

    # Verify FTS5 search works
    cur = mock_get_connection.cursor()
    cur.execute("""
        SELECT rowid FROM message_search WHERE message_search MATCH 'automation'
    """)
    results = cur.fetchall()

    assert len(results) == 1


def test_search_messages(mock_get_connection):
    """Test full-text search across messages."""
    # Create conversation and participants
    conv = create_conversation(
        platform="whatsapp", conversation_type="group", campaign="SEBE Review"
    )
    conv_id = conv["conversation"]["id"]

    p1 = add_participant(display_name="Alice")
    p2 = add_participant(display_name="Bob")

    # Add messages
    add_message(
        conversation_id=conv_id,
        participant_id=p1["participant"]["id"],
        content_text="SEBE targets energy consumption",
        platform_timestamp="2026-03-12 10:00:00",
    )
    add_message(
        conversation_id=conv_id,
        participant_id=p2["participant"]["id"],
        content_text="The revenue projections are conservative",
        platform_timestamp="2026-03-12 10:05:00",
    )

    # Search for "energy"
    result = search_messages(query="energy")

    assert result["success"] is True
    assert result["count"] == 1
    assert "energy consumption" in result["messages"][0]["content_text"]


def test_search_messages_by_campaign(mock_get_connection):
    """Test search filtered by campaign."""
    # Create two conversations with different campaigns
    conv1 = create_conversation(
        platform="whatsapp", conversation_type="group", campaign="SEBE Review"
    )
    conv2 = create_conversation(
        platform="whatsapp", conversation_type="group", campaign="Other Topic"
    )

    p = add_participant(display_name="Alice")
    p_id = p["participant"]["id"]

    # Add messages to both
    add_message(
        conversation_id=conv1["conversation"]["id"],
        participant_id=p_id,
        content_text="SEBE automation taxation",
        platform_timestamp="2026-03-12 10:00:00",
    )
    add_message(
        conversation_id=conv2["conversation"]["id"],
        participant_id=p_id,
        content_text="automation in general",
        platform_timestamp="2026-03-12 10:05:00",
    )

    # Search for "automation" filtered by campaign
    result = search_messages(query="automation", campaign="SEBE Review")

    assert result["success"] is True
    assert result["count"] == 1
    assert result["messages"][0]["campaign"] == "SEBE Review"


def test_tag_message(mock_get_connection):
    """Test adding a tag to a message."""
    # Create message
    conv = create_conversation(platform="whatsapp", conversation_type="group")
    part = add_participant(display_name="Alice")

    msg = add_message(
        conversation_id=conv["conversation"]["id"],
        participant_id=part["participant"]["id"],
        content_text="This is important",
        platform_timestamp="2026-03-12 10:00:00",
    )
    msg_id = msg["message"]["id"]

    # Add tag
    result = tag_message(
        message_id=msg_id,
        tag_type="claim",
        tag_value="policy argument",
        tagged_by="human",
        confidence=1.0,
    )

    assert result["success"] is True
    assert result["tag"]["message_id"] == msg_id
    assert result["tag"]["tag_type"] == "claim"
    assert result["tag"]["tag_value"] == "policy argument"


def test_tag_message_invalid_type(mock_get_connection):
    """Test that invalid tag type is rejected."""
    # Create message
    conv = create_conversation(platform="whatsapp", conversation_type="group")
    part = add_participant(display_name="Alice")

    msg = add_message(
        conversation_id=conv["conversation"]["id"],
        participant_id=part["participant"]["id"],
        content_text="Test",
        platform_timestamp="2026-03-12 10:00:00",
    )

    # Try to add invalid tag type
    result = tag_message(
        message_id=msg["message"]["id"], tag_type="invalid_tag_type", tag_value="test"
    )

    assert result["success"] is False
    assert "Invalid tag type" in result["error"]


# ═══════════════════════════════════════════════════════════════════════════
# List and Query Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_list_conversations(mock_get_connection):
    """Test listing conversations with and without filters."""
    # Create multiple conversations
    create_conversation(
        platform="whatsapp", conversation_type="group", campaign="Campaign A"
    )
    create_conversation(
        platform="whatsapp", conversation_type="group", campaign="Campaign B"
    )
    create_conversation(
        platform="discord", conversation_type="channel", campaign="Campaign A"
    )

    # List all
    result_all = list_conversations()
    assert result_all["success"] is True
    assert result_all["count"] == 3

    # Filter by platform
    result_wa = list_conversations(platform="whatsapp")
    assert result_wa["count"] == 2

    # Filter by campaign
    result_camp_a = list_conversations(campaign="Campaign A")
    assert result_camp_a["count"] == 2


def test_list_messages(mock_get_connection):
    """Test listing messages by conversation."""
    # Create conversation and participants
    conv = create_conversation(platform="whatsapp", conversation_type="group")
    conv_id = conv["conversation"]["id"]

    p1 = add_participant(display_name="Alice")
    p2 = add_participant(display_name="Bob")

    # Add messages
    add_message(
        conversation_id=conv_id,
        participant_id=p1["participant"]["id"],
        content_text="Message 1",
        platform_timestamp="2026-03-12 10:00:00",
    )
    add_message(
        conversation_id=conv_id,
        participant_id=p2["participant"]["id"],
        content_text="Message 2",
        platform_timestamp="2026-03-12 10:05:00",
    )

    # List by conversation
    result = list_messages(conversation_id=conv_id)

    assert result["success"] is True
    assert result["count"] == 2
    assert all(m["conversation_id"] == conv_id for m in result["messages"])


def test_get_conversation_participants(mock_get_connection):
    """Test getting participants for a conversation."""
    # Create conversation and participants
    conv = create_conversation(platform="whatsapp", conversation_type="group")
    conv_id = conv["conversation"]["id"]

    p1 = add_participant(display_name="Alice", organisation="Green Party")
    p2 = add_participant(display_name="Bob", organisation="Think Tank")

    # Add messages from both
    add_message(
        conversation_id=conv_id,
        participant_id=p1["participant"]["id"],
        content_text="Message 1",
        platform_timestamp="2026-03-12 10:00:00",
    )
    add_message(
        conversation_id=conv_id,
        participant_id=p2["participant"]["id"],
        content_text="Message 2",
        platform_timestamp="2026-03-12 10:05:00",
    )
    add_message(
        conversation_id=conv_id,
        participant_id=p1["participant"]["id"],
        content_text="Message 3",
        platform_timestamp="2026-03-12 10:10:00",
    )

    # Get participants
    result = get_conversation_participants(conv_id)

    assert result["success"] is True
    assert result["count"] == 2

    # Check message counts (sorted by message count DESC)
    assert result["participants"][0]["display_name"] == "Alice"
    assert result["participants"][0]["message_count"] == 2
    assert result["participants"][1]["display_name"] == "Bob"
    assert result["participants"][1]["message_count"] == 1


def test_get_stats(mock_get_connection):
    """Test getting summary statistics."""
    # Create some data
    conv1 = create_conversation(platform="whatsapp", conversation_type="group")
    conv2 = create_conversation(platform="discord", conversation_type="channel")

    p1 = add_participant(display_name="Alice")
    p2 = add_participant(display_name="Bob")

    msg1 = add_message(
        conversation_id=conv1["conversation"]["id"],
        participant_id=p1["participant"]["id"],
        content_text="Test message",
        platform_timestamp="2026-03-12 10:00:00",
    )

    add_message(
        conversation_id=conv2["conversation"]["id"],
        participant_id=p2["participant"]["id"],
        content_text="Another message",
        platform_timestamp="2026-03-12 10:05:00",
    )

    # Add a tag
    tag_message(
        message_id=msg1["message"]["id"], tag_type="claim", tag_value="important"
    )

    # Get stats
    result = get_stats()

    assert result["success"] is True
    assert result["stats"]["participants"] == 2
    assert result["stats"]["total_messages"] == 2
    assert result["stats"]["conversations_by_platform"]["whatsapp"] == 1
    assert result["stats"]["conversations_by_platform"]["discord"] == 1
    assert result["stats"]["messages_by_platform"]["whatsapp"] == 1
    assert result["stats"]["messages_by_platform"]["discord"] == 1
    assert result["stats"]["tags_by_type"]["claim"] == 1
