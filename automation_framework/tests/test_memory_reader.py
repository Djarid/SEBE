"""
Tests for tools.memory.reader — Session context loader.

All tests use temporary directories to avoid touching real memory files.
Tests cover MEMORY.md reading, daily log parsing, and context assembly.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

from tools.memory.reader import (
    read_memory_file,
    read_daily_log,
    read_recent_logs,
    load_session_context,
    format_as_markdown,
)


# ═══════════════════════════════════════════════════════════════════════════
# MEMORY.md Reading Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestReadMemoryFile:
    """Test MEMORY.md file reading and parsing."""

    def test_read_memory_file_normal(self, tmp_memory_dirs):
        """Read a normal MEMORY.md file."""
        memory_file = tmp_memory_dirs["memory_dir"] / "MEMORY.md"
        content = """# Persistent Memory

## User Preferences

- Author: Jason Huxley
- Communication: Direct, technical

## Key Facts

- SEBE = Sovereign Energy & Bandwidth Excise
- Revenue target: £200-500 billion/year
"""
        memory_file.write_text(content, encoding="utf-8")
        
        result = read_memory_file()
        assert result["success"] is True
        assert "content" in result
        assert "sections" in result
        assert "user_preferences" in result["sections"]
        assert "key_facts" in result["sections"]

    def test_read_memory_file_missing(self, tmp_memory_dirs):
        """Missing MEMORY.md returns error."""
        # File doesn't exist in tmp_path
        result = read_memory_file()
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_read_memory_file_empty(self, tmp_memory_dirs):
        """Empty MEMORY.md file."""
        from tools.memory import config
        memory_file = config.MEMORY_FILE
        memory_file.write_text("", encoding="utf-8")
        
        result = read_memory_file()
        assert result["success"] is True
        assert result["content"] == ""

    def test_read_memory_file_last_modified(self, tmp_memory_dirs):
        """Last modified timestamp is included."""
        memory_file = tmp_memory_dirs["memory_dir"] / "MEMORY.md"
        memory_file.write_text("# Memory\n", encoding="utf-8")
        
        result = read_memory_file()
        assert result["success"] is True
        assert "last_modified" in result
        assert isinstance(result["last_modified"], str)


# ═══════════════════════════════════════════════════════════════════════════
# Daily Log Reading Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestReadDailyLog:
    """Test daily log file reading."""

    def test_read_daily_log_exists(self, tmp_memory_dirs):
        """Read existing daily log."""
        from tools.memory import config
        log_file = config.LOGS_DIR / "2026-02-14.md"
        content = """# Session Log: 2026-02-14

- 11:51 [event] Session started
- 12:20 [fact] ONS ASHE April 2025 data
"""
        log_file.write_text(content, encoding="utf-8")
        
        result = read_daily_log("2026-02-14")
        assert result["success"] is True
        assert result["date"] == "2026-02-14"
        assert "content" in result
        assert len(result["events"]) == 2
        assert "Session started" in result["events"][0]

    def test_read_daily_log_missing(self, tmp_memory_dirs):
        """Missing log file returns error."""
        result = read_daily_log("2026-01-01")
        assert result["success"] is False
        assert "No log for" in result["error"]

    def test_read_daily_log_no_events(self, tmp_memory_dirs):
        """Log with no bullet points."""
        from tools.memory import config
        log_file = config.LOGS_DIR / "2026-02-14.md"
        log_file.write_text("# Session Log\n\nNo events today.\n", encoding="utf-8")
        
        result = read_daily_log("2026-02-14")
        assert result["success"] is True
        assert result["events"] == []


# ═══════════════════════════════════════════════════════════════════════════
# Recent Logs Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestReadRecentLogs:
    """Test reading multiple recent logs."""

    def test_read_recent_logs_multiple_days(self, tmp_memory_dirs):
        """Read logs from multiple days."""
        from tools.memory import config
        today = datetime.now().date()
        
        # Create today and yesterday logs
        for i in range(2):
            date = today - timedelta(days=i)
            log_file = config.LOGS_DIR / f"{date.isoformat()}.md"
            log_file.write_text(f"# Log for {date}\n- Event {i}\n", encoding="utf-8")
        
        result = read_recent_logs(days=2)
        assert len(result) == 2
        success_count = sum(1 for log in result if log.get("success"))
        assert success_count == 2

    def test_read_recent_logs_no_logs_exist(self, tmp_memory_dirs):
        """Reading logs when none exist."""
        # Logs don't exist in tmp_path
        result = read_recent_logs(days=2)
        assert len(result) == 2
        # All should return error (success=False)
        assert all(log.get("success") is False for log in result)

    def test_read_recent_logs_default_days(self, tmp_memory_dirs):
        """Default is 2 days."""
        result = read_recent_logs()
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════════════════════
# Session Context Loading Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestLoadSessionContext:
    """Test full session context loading."""

    @patch("tools.memory.reader.list_memory")
    @patch("tools.memory.reader.list_tasks")
    @patch("tools.memory.reader.list_contacts")
    @patch("tools.memory.reader.get_stats")
    def test_load_session_context_full(
        self, mock_stats, mock_contacts, mock_tasks, mock_memory, tmp_memory_dirs
    ):
        """Full context load with all components."""
        # Setup mocks
        mock_memory.return_value = {"success": True, "entries": [
            {"id": 1, "type": "fact", "content": "Test fact", "importance": 7}
        ]}
        mock_tasks.return_value = {"success": True, "tasks": [
            {"id": 1, "title": "Test task", "status": "pending"}
        ]}
        mock_contacts.return_value = {"success": True, "contacts": [
            {"id": 1, "name": "Test Contact", "status": "contacted"}
        ]}
        mock_stats.return_value = {"success": True, "stats": {}}
        
        # Create MEMORY.md
        memory_file = tmp_memory_dirs["memory_dir"] / "MEMORY.md"
        memory_file.write_text("# Memory\n## Key Facts\n- Test\n", encoding="utf-8")
        
        result = load_session_context()
        
        assert "loaded_at" in result
        assert result["memory_file"]["success"] is True
        assert len(result["db_entries"]) == 1
        assert len(result["pending_tasks"]) >= 1
        assert len(result["active_contacts"]) == 1

    @patch("tools.memory.reader.list_memory")
    @patch("tools.memory.reader.list_tasks")
    @patch("tools.memory.reader.list_contacts")
    @patch("tools.memory.reader.get_stats")
    def test_load_session_context_memory_only(
        self, mock_stats, mock_contacts, mock_tasks, mock_memory, tmp_memory_dirs
    ):
        """Load memory file only."""
        memory_file = tmp_memory_dirs["memory_dir"] / "MEMORY.md"
        memory_file.write_text("# Memory\n", encoding="utf-8")
        
        result = load_session_context(
            include_logs=False,
            include_db=False,
            include_tasks=False,
            include_contacts=False,
        )
        
        assert result["memory_file"]["success"] is True
        assert result["daily_logs"] == []
        assert result["db_entries"] == []
        assert result["pending_tasks"] == []

    @patch("tools.memory.reader.list_memory")
    @patch("tools.memory.reader.list_tasks")
    @patch("tools.memory.reader.list_contacts")
    @patch("tools.memory.reader.get_stats")
    def test_load_session_context_tasks_only(
        self, mock_stats, mock_contacts, mock_tasks, mock_memory, tmp_memory_dirs
    ):
        """Load tasks only."""
        mock_tasks.return_value = {"success": True, "tasks": [
            {"id": 1, "title": "Task", "status": "pending"}
        ]}
        mock_stats.return_value = {"success": True, "stats": {}}
        
        result = load_session_context(
            include_memory=False,
            include_logs=False,
            include_db=False,
            include_contacts=False,
        )
        
        assert result["memory_file"] is None
        assert len(result["pending_tasks"]) >= 1

    @patch("tools.memory.reader.list_memory")
    @patch("tools.memory.reader.list_tasks")
    @patch("tools.memory.reader.list_contacts")
    @patch("tools.memory.reader.get_stats")
    def test_load_session_context_logs_only(
        self, mock_stats, mock_contacts, mock_tasks, mock_memory, tmp_memory_dirs
    ):
        """Load logs only."""
        logs_dir = tmp_memory_dirs["logs_dir"]
        today = datetime.now().date()
        log_file = logs_dir / f"{today.isoformat()}.md"
        log_file.write_text("# Log\n- Event\n", encoding="utf-8")
        
        mock_stats.return_value = {"success": True, "stats": {}}
        
        result = load_session_context(
            include_memory=False,
            include_db=False,
            include_tasks=False,
            include_contacts=False,
            log_days=1,
        )
        
        assert result["memory_file"] is None
        assert len(result["daily_logs"]) == 1


# ═══════════════════════════════════════════════════════════════════════════
# Markdown Formatting Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFormatAsMarkdown:
    """Test markdown formatting of context."""

    def test_format_as_markdown_with_memory(self):
        """Format context with MEMORY.md content."""
        ctx = {
            "memory_file": {
                "success": True,
                "content": "# Memory\n\n## Key Facts\n- SEBE targets £200B\n"
            },
            "daily_logs": [],
            "pending_tasks": [],
            "active_contacts": [],
            "db_entries": [],
        }
        
        result = format_as_markdown(ctx)
        assert "# Memory" in result
        assert "SEBE targets £200B" in result

    def test_format_as_markdown_with_tasks(self):
        """Format context with pending tasks."""
        ctx = {
            "memory_file": {"success": False},
            "daily_logs": [],
            "pending_tasks": [
                {
                    "id": 1,
                    "title": "Email IPPR",
                    "status": "pending",
                    "priority": "high",
                    "due_date": "2026-03-01",
                }
            ],
            "active_contacts": [],
            "db_entries": [],
        }
        
        result = format_as_markdown(ctx)
        assert "## Pending Tasks" in result
        assert "Email IPPR" in result
        assert "[high]" in result

    def test_format_as_markdown_with_contacts(self):
        """Format context with contacts awaiting follow-up."""
        ctx = {
            "memory_file": {"success": False},
            "daily_logs": [],
            "pending_tasks": [],
            "active_contacts": [
                {
                    "id": 1,
                    "name": "Bedford Chair",
                    "organisation": "Green Party",
                    "last_contacted": "2026-02-14 12:00:00",
                }
            ],
            "db_entries": [],
        }
        
        result = format_as_markdown(ctx)
        assert "## Contacts Awaiting Follow-up" in result
        assert "Bedford Chair" in result
        assert "(Green Party)" in result

    def test_format_as_markdown_with_db_entries(self):
        """Format context with high-importance DB entries."""
        ctx = {
            "memory_file": {"success": False},
            "daily_logs": [],
            "pending_tasks": [],
            "active_contacts": [],
            "db_entries": [
                {"id": 1, "type": "fact", "content": "SEBE revenue £200-500B"},
                {"id": 2, "type": "insight", "content": "Two-stage model"},
            ],
        }
        
        result = format_as_markdown(ctx)
        assert "## Key Facts" in result
        assert "[fact]" in result
        assert "SEBE revenue £200-500B" in result

    def test_format_as_markdown_with_daily_logs(self):
        """Format context with daily logs."""
        ctx = {
            "memory_file": {"success": False},
            "daily_logs": [
                {
                    "success": True,
                    "date": "2026-02-14",
                    "content": "# Session Log: 2026-02-14\n\n- 11:51 [event] Session started\n"
                }
            ],
            "pending_tasks": [],
            "active_contacts": [],
            "db_entries": [],
        }
        
        result = format_as_markdown(ctx)
        assert "## Session Log: 2026-02-14" in result
        assert "Session started" in result

    def test_format_as_markdown_empty_context(self):
        """Format empty context gracefully."""
        ctx = {
            "memory_file": {"success": False},
            "daily_logs": [],
            "pending_tasks": [],
            "active_contacts": [],
            "db_entries": [],
        }
        
        result = format_as_markdown(ctx)
        assert isinstance(result, str)
        # Should return a minimal string, not crash
