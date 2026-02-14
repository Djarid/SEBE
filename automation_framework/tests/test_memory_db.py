"""
Tests for tools.memory.db — SQLite CRUD operations.

All tests use in-memory databases to avoid touching the real database.
Tests cover memory entries, tasks, contacts, interactions, and stats.
"""

import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from datetime import datetime

from tools.memory.db import (
    _ensure_tables,
    _content_hash,
    _row_to_dict,
    add_memory,
    search_memory,
    list_memory,
    delete_memory,
    add_task,
    update_task,
    list_tasks,
    add_contact,
    update_contact,
    list_contacts,
    log_interaction,
    list_interactions,
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
    with patch("tools.memory.db.get_connection") as mock:
        # Return the same connection object every time
        mock.return_value = memory_conn
        yield memory_conn


# ═══════════════════════════════════════════════════════════════════════════
# Schema & Setup Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestSchema:
    """Test database schema creation."""

    def test_ensure_tables_creates_all_tables(self, memory_conn):
        """All 4 tables are created."""
        cursor = memory_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "memory_entries" in tables
        assert "tasks" in tables
        assert "contacts" in tables
        assert "interactions" in tables

    def test_memory_entries_schema(self, memory_conn):
        """Memory entries table has expected columns."""
        cursor = memory_conn.cursor()
        cursor.execute("PRAGMA table_info(memory_entries)")
        columns = {row[1] for row in cursor.fetchall()}
        expected = {
            "id", "type", "content", "content_hash", "importance",
            "tags", "context", "created_at", "updated_at", "is_active"
        }
        assert expected.issubset(columns)

    def test_tasks_schema(self, memory_conn):
        """Tasks table has expected columns."""
        cursor = memory_conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        columns = {row[1] for row in cursor.fetchall()}
        expected = {
            "id", "title", "description", "status", "priority",
            "assigned_to", "due_date", "related_contact_id",
            "completed_at", "created_at", "updated_at"
        }
        assert expected.issubset(columns)

    def test_indexes_created(self, memory_conn):
        """Verify indexes are created."""
        cursor = memory_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        assert "idx_mem_type" in indexes
        assert "idx_task_status" in indexes
        assert "idx_contact_status" in indexes


# ═══════════════════════════════════════════════════════════════════════════
# Helper Function Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestHelpers:
    """Test helper functions."""

    def test_content_hash_deterministic(self):
        """Same content produces same hash."""
        hash1 = _content_hash("SEBE targets £200-500B")
        hash2 = _content_hash("SEBE targets £200-500B")
        assert hash1 == hash2
        assert len(hash1) == 16  # Truncated to 16 chars

    def test_content_hash_case_insensitive(self):
        """Hash is case-insensitive."""
        hash1 = _content_hash("Green Party")
        hash2 = _content_hash("green party")
        assert hash1 == hash2

    def test_content_hash_strips_whitespace(self):
        """Hash strips surrounding whitespace."""
        hash1 = _content_hash("  content  ")
        hash2 = _content_hash("content")
        assert hash1 == hash2

    def test_row_to_dict_converts(self, memory_conn):
        """Row conversion to dict works."""
        cursor = memory_conn.cursor()
        cursor.execute("""
            INSERT INTO memory_entries (type, content, content_hash)
            VALUES ('fact', 'test', '1234567890abcdef')
        """)
        memory_conn.commit()
        cursor.execute("SELECT * FROM memory_entries WHERE id = 1")
        row = cursor.fetchone()
        result = _row_to_dict(row)
        assert isinstance(result, dict)
        assert result["type"] == "fact"
        assert result["content"] == "test"

    def test_row_to_dict_none(self):
        """None input returns None."""
        assert _row_to_dict(None) is None


# ═══════════════════════════════════════════════════════════════════════════
# Memory CRUD Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestMemoryCRUD:
    """Test memory entry CRUD operations."""

    def test_add_memory_basic(self, mock_get_connection):
        """Basic memory add with minimal parameters."""
        result = add_memory("SEBE targets £200-500B revenue")
        assert result["success"] is True
        assert "entry" in result
        assert result["entry"]["content"] == "SEBE targets £200-500B revenue"
        assert result["entry"]["type"] == "fact"
        assert result["entry"]["importance"] == 5

    def test_add_memory_full_params(self, mock_get_connection):
        """Memory add with all parameters."""
        result = add_memory(
            content="Jason prefers ULI not UBI",
            entry_type="preference",
            importance=8,
            tags=["terminology", "author"],
            context="Author preference from session 2026-02-14",
        )
        assert result["success"] is True
        assert result["entry"]["type"] == "preference"
        assert result["entry"]["importance"] == 8
        assert result["entry"]["context"] == "Author preference from session 2026-02-14"

    def test_add_memory_invalid_type(self, mock_get_connection):
        """Invalid type is rejected."""
        result = add_memory("content", entry_type="invalid_type")
        assert result["success"] is False
        assert "Invalid type" in result["error"]

    def test_add_memory_deduplication(self, mock_get_connection):
        """Duplicate content is rejected."""
        add_memory("Duplicate content")
        result = add_memory("Duplicate content")
        assert result["success"] is False
        assert "Duplicate" in result["error"]
        assert "existing_id" in result

    def test_search_memory_basic(self, mock_get_connection):
        """Basic text search works."""
        add_memory("SEBE targets £200-500B")
        add_memory("Green Party submission")
        result = search_memory("SEBE")
        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["entries"]) == 1
        assert "SEBE" in result["entries"][0]["content"]

    def test_search_memory_no_matches(self, mock_get_connection):
        """Search with no matches returns empty list."""
        add_memory("Some content")
        result = search_memory("nonexistent")
        assert result["success"] is True
        assert result["count"] == 0
        assert result["entries"] == []

    def test_search_memory_type_filter(self, mock_get_connection):
        """Search can filter by type."""
        add_memory("Fact content", entry_type="fact")
        add_memory("Event content", entry_type="event")
        result = search_memory("content", entry_type="fact")
        assert result["count"] == 1
        assert result["entries"][0]["type"] == "fact"

    def test_search_memory_limit(self, mock_get_connection):
        """Search respects limit parameter."""
        for i in range(10):
            add_memory(f"Content {i}")
        result = search_memory("Content", limit=5)
        assert result["count"] == 5

    def test_list_memory_all(self, mock_get_connection):
        """List all active memory entries."""
        add_memory("Entry 1", importance=7)
        add_memory("Entry 2", importance=5)
        result = list_memory()
        assert result["success"] is True
        assert result["count"] == 2

    def test_list_memory_type_filter(self, mock_get_connection):
        """List can filter by type."""
        add_memory("Fact", entry_type="fact")
        add_memory("Event", entry_type="event")
        result = list_memory(entry_type="fact")
        assert result["count"] == 1
        assert result["entries"][0]["type"] == "fact"

    def test_list_memory_min_importance(self, mock_get_connection):
        """List can filter by minimum importance."""
        add_memory("High importance", importance=8)
        add_memory("Low importance", importance=3)
        result = list_memory(min_importance=7)
        assert result["count"] == 1
        assert result["entries"][0]["importance"] == 8

    def test_delete_memory_soft(self, mock_get_connection):
        """Soft delete marks entry as inactive."""
        add_result = add_memory("To be deleted")
        entry_id = add_result["entry"]["id"]
        
        result = delete_memory(entry_id, hard=False)
        assert result["success"] is True
        assert "deactivated" in result["message"]
        
        # Verify it's hidden from list
        list_result = list_memory()
        assert list_result["count"] == 0

    def test_delete_memory_hard(self, mock_get_connection):
        """Hard delete removes entry permanently."""
        add_result = add_memory("To be deleted")
        entry_id = add_result["entry"]["id"]
        
        result = delete_memory(entry_id, hard=True)
        assert result["success"] is True
        assert "permanently deleted" in result["message"]

    def test_delete_memory_nonexistent(self, mock_get_connection):
        """Deleting non-existent entry returns error."""
        result = delete_memory(99999)
        assert result["success"] is False
        assert "not found" in result["error"]


# ═══════════════════════════════════════════════════════════════════════════
# Task CRUD Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestTaskCRUD:
    """Test task CRUD operations."""

    def test_add_task_basic(self, mock_get_connection):
        """Basic task creation."""
        result = add_task("Email IPPR")
        assert result["success"] is True
        assert result["task"]["title"] == "Email IPPR"
        assert result["task"]["status"] == "pending"
        assert result["task"]["priority"] == "medium"

    def test_add_task_full_params(self, mock_get_connection):
        """Task with all parameters."""
        result = add_task(
            title="Submit to Green Party",
            description="Send refined policy submission",
            priority="high",
            assigned_to="Jason",
            due_date="2026-03-01",
        )
        assert result["success"] is True
        assert result["task"]["priority"] == "high"
        assert result["task"]["due_date"] == "2026-03-01"

    def test_add_task_invalid_priority(self, mock_get_connection):
        """Invalid priority is rejected."""
        result = add_task("Task", priority="invalid")
        assert result["success"] is False
        assert "Invalid priority" in result["error"]

    def test_update_task_status(self, mock_get_connection):
        """Update task status."""
        add_result = add_task("Task to complete")
        task_id = add_result["task"]["id"]
        
        result = update_task(task_id, status="completed")
        assert result["success"] is True
        assert result["task"]["status"] == "completed"
        assert result["task"]["completed_at"] is not None

    def test_update_task_multiple_fields(self, mock_get_connection):
        """Update multiple task fields."""
        add_result = add_task("Task")
        task_id = add_result["task"]["id"]
        
        result = update_task(
            task_id,
            title="Updated title",
            priority="high",
            status="in_progress",
        )
        assert result["success"] is True
        assert result["task"]["title"] == "Updated title"
        assert result["task"]["priority"] == "high"
        assert result["task"]["status"] == "in_progress"

    def test_update_task_nonexistent(self, mock_get_connection):
        """Updating non-existent task returns error."""
        result = update_task(99999, status="completed")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_update_task_invalid_status(self, mock_get_connection):
        """Invalid status is rejected."""
        add_result = add_task("Task")
        task_id = add_result["task"]["id"]
        result = update_task(task_id, status="invalid_status")
        assert result["success"] is False
        assert "Invalid status" in result["error"]

    def test_list_tasks_all(self, mock_get_connection):
        """List all tasks."""
        add_task("Task 1", priority="high")
        add_task("Task 2", priority="low")
        result = list_tasks()
        assert result["success"] is True
        assert result["count"] == 2

    def test_list_tasks_status_filter(self, mock_get_connection):
        """List tasks filtered by status."""
        add_task("Pending task")
        completed = add_task("Completed task")
        update_task(completed["task"]["id"], status="completed")
        
        result = list_tasks(status="pending")
        assert result["count"] == 1
        assert result["tasks"][0]["status"] == "pending"

    def test_list_tasks_priority_filter(self, mock_get_connection):
        """List tasks filtered by priority."""
        add_task("High priority", priority="high")
        add_task("Low priority", priority="low")
        result = list_tasks(priority="high")
        assert result["count"] == 1
        assert result["tasks"][0]["priority"] == "high"


# ═══════════════════════════════════════════════════════════════════════════
# Contact CRUD Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestContactCRUD:
    """Test contact CRUD operations."""

    def test_add_contact_basic(self, mock_get_connection):
        """Basic contact creation."""
        result = add_contact("Bedford Chair")
        assert result["success"] is True
        assert result["contact"]["name"] == "Bedford Chair"
        assert result["contact"]["status"] == "not_contacted"

    def test_add_contact_full_params(self, mock_get_connection):
        """Contact with all parameters."""
        result = add_contact(
            name="IPPR Contact",
            organisation="IPPR",
            role="Policy Director",
            email="policy@ippr.org",
            phone="+442012345678",
            notes="Think tank contact for economic policy",
        )
        assert result["success"] is True
        assert result["contact"]["organisation"] == "IPPR"
        assert result["contact"]["email"] == "policy@ippr.org"

    def test_update_contact(self, mock_get_connection):
        """Update contact fields."""
        add_result = add_contact("Contact")
        contact_id = add_result["contact"]["id"]
        
        result = update_contact(
            contact_id,
            email="new@example.com",
            status="contacted",
        )
        assert result["success"] is True
        assert result["contact"]["email"] == "new@example.com"
        assert result["contact"]["status"] == "contacted"

    def test_update_contact_nonexistent(self, mock_get_connection):
        """Updating non-existent contact returns error."""
        result = update_contact(99999, email="test@example.com")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_update_contact_invalid_status(self, mock_get_connection):
        """Invalid status is rejected."""
        add_result = add_contact("Contact")
        contact_id = add_result["contact"]["id"]
        result = update_contact(contact_id, status="invalid_status")
        assert result["success"] is False
        assert "Invalid status" in result["error"]

    def test_list_contacts_all(self, mock_get_connection):
        """List all contacts."""
        add_contact("Contact 1")
        add_contact("Contact 2")
        result = list_contacts()
        assert result["success"] is True
        assert result["count"] == 2

    def test_list_contacts_status_filter(self, mock_get_connection):
        """List contacts filtered by status."""
        add_contact("Not contacted")
        contacted = add_contact("Contacted")
        update_contact(contacted["contact"]["id"], status="contacted")
        
        result = list_contacts(status="contacted")
        assert result["count"] == 1
        assert result["contacts"][0]["status"] == "contacted"

    def test_list_contacts_org_filter(self, mock_get_connection):
        """List contacts filtered by organisation."""
        add_contact("Person 1", organisation="Green Party")
        add_contact("Person 2", organisation="IPPR")
        result = list_contacts(organisation="Green")
        assert result["count"] == 1
        assert "Green" in result["contacts"][0]["organisation"]


# ═══════════════════════════════════════════════════════════════════════════
# Interaction Logging Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestInteractionLogging:
    """Test interaction logging."""

    def test_log_interaction_basic(self, mock_get_connection):
        """Basic interaction log."""
        contact = add_contact("Test Contact")
        contact_id = contact["contact"]["id"]
        
        result = log_interaction(
            contact_id=contact_id,
            channel="email",
            direction="outbound",
            subject="SEBE submission",
        )
        assert result["success"] is True
        assert result["interaction"]["contact_id"] == contact_id
        assert result["interaction"]["channel"] == "email"

    def test_log_interaction_with_content(self, mock_get_connection):
        """Interaction with full content."""
        contact = add_contact("Test Contact")
        contact_id = contact["contact"]["id"]
        
        result = log_interaction(
            contact_id=contact_id,
            channel="email",
            direction="outbound",
            subject="Policy proposal",
            content="Full email body here",
        )
        assert result["success"] is True
        assert result["interaction"]["content"] == "Full email body here"

    def test_log_interaction_updates_contact_status(self, mock_get_connection):
        """Logging interaction updates contact's last_contacted."""
        contact = add_contact("Test Contact")
        contact_id = contact["contact"]["id"]
        
        log_interaction(contact_id, "email", "outbound")
        
        # Check contact was updated
        contact_result = list_contacts()
        assert contact_result["contacts"][0]["status"] == "contacted"
        assert contact_result["contacts"][0]["last_contacted"] is not None

    def test_log_interaction_invalid_channel(self, mock_get_connection):
        """Invalid channel is rejected."""
        contact = add_contact("Test Contact")
        result = log_interaction(contact["contact"]["id"], "invalid_channel", "outbound")
        assert result["success"] is False
        assert "Invalid channel" in result["error"]

    def test_log_interaction_invalid_direction(self, mock_get_connection):
        """Invalid direction is rejected."""
        contact = add_contact("Test Contact")
        result = log_interaction(contact["contact"]["id"], "email", "invalid_direction")
        assert result["success"] is False
        assert "Invalid direction" in result["error"]

    def test_log_interaction_nonexistent_contact(self, mock_get_connection):
        """Logging to non-existent contact returns error."""
        result = log_interaction(99999, "email", "outbound")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_list_interactions_all(self, mock_get_connection):
        """List all interactions."""
        contact = add_contact("Test Contact")
        contact_id = contact["contact"]["id"]
        log_interaction(contact_id, "email", "outbound")
        log_interaction(contact_id, "phone", "inbound")
        
        result = list_interactions()
        assert result["success"] is True
        assert result["count"] == 2

    def test_list_interactions_contact_filter(self, mock_get_connection):
        """List interactions filtered by contact."""
        contact1 = add_contact("Contact 1")
        contact2 = add_contact("Contact 2")
        log_interaction(contact1["contact"]["id"], "email", "outbound")
        log_interaction(contact2["contact"]["id"], "email", "outbound")
        
        result = list_interactions(contact_id=contact1["contact"]["id"])
        assert result["count"] == 1

    def test_list_interactions_channel_filter(self, mock_get_connection):
        """List interactions filtered by channel."""
        contact = add_contact("Test Contact")
        contact_id = contact["contact"]["id"]
        log_interaction(contact_id, "email", "outbound")
        log_interaction(contact_id, "phone", "outbound")
        
        result = list_interactions(channel="email")
        assert result["count"] == 1
        assert result["interactions"][0]["channel"] == "email"


# ═══════════════════════════════════════════════════════════════════════════
# Stats Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestStats:
    """Test stats aggregation."""

    def test_get_stats_empty(self, mock_get_connection):
        """Stats on empty database."""
        result = get_stats()
        assert result["success"] is True
        assert "stats" in result
        assert result["stats"]["memory_entries"] == {}
        assert result["stats"]["tasks"] == {}
        assert result["stats"]["interactions"] == 0

    def test_get_stats_with_data(self, mock_get_connection):
        """Stats with sample data."""
        add_memory("Fact 1", entry_type="fact")
        add_memory("Fact 2", entry_type="fact")
        add_memory("Event 1", entry_type="event")
        add_task("Task 1")
        add_task("Task 2")
        contact = add_contact("Contact")
        log_interaction(contact["contact"]["id"], "email", "outbound")
        
        result = get_stats()
        assert result["success"] is True
        stats = result["stats"]
        assert stats["memory_entries"]["fact"] == 2
        assert stats["memory_entries"]["event"] == 1
        assert stats["tasks"]["pending"] == 2
        assert stats["interactions"] == 1

    def test_get_stats_pending_followups(self, mock_get_connection):
        """Stats includes pending follow-ups."""
        contact = add_contact("Pending Contact")
        log_interaction(contact["contact"]["id"], "email", "outbound")
        
        result = get_stats()
        assert result["success"] is True
        assert len(result["stats"]["pending_followups"]) == 1
        assert result["stats"]["pending_followups"][0]["name"] == "Pending Contact"
