"""
Tests for tools.memory.writer — Memory entry writing.

All tests use temporary directories to avoid touching real memory files.
Tests cover daily log appending, dual-write mode, and MEMORY.md updates.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

from tools.memory.writer import (
    _ensure_dirs,
    _today_log_path,
    append_to_daily_log,
    write_to_memory,
    append_to_memory_file,
)


# ═══════════════════════════════════════════════════════════════════════════
# Helper Function Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestHelpers:
    """Test helper functions."""

    def test_ensure_dirs_creates_directories(self, tmp_memory_dirs):
        """Ensure directories are created if missing."""
        from tools.memory import config
        # Remove the created dirs
        logs_dir = config.LOGS_DIR
        if logs_dir.exists():
            import shutil
            shutil.rmtree(logs_dir)
        
        _ensure_dirs()
        
        # Should be recreated
        assert logs_dir.exists()

    def test_today_log_path_format(self, tmp_memory_dirs):
        """Today's log path has correct format."""
        path = _today_log_path()
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in str(path)
        assert path.suffix == ".md"


# ═══════════════════════════════════════════════════════════════════════════
# Daily Log Appending Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestAppendToDailyLog:
    """Test daily log appending."""

    def test_append_to_daily_log_creates_new_file(self, tmp_memory_dirs):
        """Appending to non-existent log creates file with header."""
        result = append_to_daily_log("First entry")
        assert result["success"] is True
        
        log_path = _today_log_path()
        assert log_path.exists()
        
        content = log_path.read_text(encoding="utf-8")
        assert "# Session Log:" in content
        assert "First entry" in content

    def test_append_to_daily_log_appends_to_existing(self, tmp_memory_dirs):
        """Appending to existing log file."""
        # Create initial entry
        append_to_daily_log("First entry")
        
        # Append second entry
        result = append_to_daily_log("Second entry")
        assert result["success"] is True
        
        content = _today_log_path().read_text(encoding="utf-8")
        assert "First entry" in content
        assert "Second entry" in content

    def test_append_to_daily_log_with_timestamp(self, tmp_memory_dirs):
        """Entry includes timestamp by default."""
        result = append_to_daily_log("Event with timestamp")
        
        content = _today_log_path().read_text(encoding="utf-8")
        # Should have HH:MM format
        assert "Event with timestamp" in content
        # Check for time pattern (e.g., "14:30")
        import re
        assert re.search(r"\d{2}:\d{2}", content)

    def test_append_to_daily_log_without_timestamp(self, tmp_memory_dirs):
        """Entry can be created without timestamp."""
        result = append_to_daily_log("Event without timestamp", timestamp=False)
        
        content = _today_log_path().read_text(encoding="utf-8")
        # Should not have leading time
        lines = content.strip().split("\n")
        event_line = [l for l in lines if "Event without timestamp" in l][0]
        assert not event_line.strip().startswith("- [0-9]")

    def test_append_to_daily_log_with_type(self, tmp_memory_dirs):
        """Entry includes type tag."""
        result = append_to_daily_log("Important fact", entry_type="fact")
        
        content = _today_log_path().read_text(encoding="utf-8")
        assert "[fact]" in content
        assert "Important fact" in content

    def test_append_to_daily_log_with_category(self, tmp_memory_dirs):
        """Entry includes category hashtag."""
        result = append_to_daily_log(
            "ONS data",
            entry_type="fact",
            category="ons"
        )
        
        content = _today_log_path().read_text(encoding="utf-8")
        assert "#ons" in content

    def test_append_to_daily_log_return_value(self, tmp_memory_dirs):
        """Return dict contains expected fields."""
        result = append_to_daily_log("Test entry")
        
        assert result["success"] is True
        assert "path" in result
        assert "date" in result
        assert "entry" in result
        assert "message" in result


# ═══════════════════════════════════════════════════════════════════════════
# Dual-Write Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestWriteToMemory:
    """Test dual-write mode (log + database)."""

    @patch("tools.memory.writer.add_memory")
    def test_write_to_memory_dual_write(self, mock_add_memory, tmp_memory_dirs):
        """Dual-write mode writes to both log and DB."""
        mock_add_memory.return_value = {
            "success": True,
            "entry": {"id": 1, "content": "Test fact"}
        }
        
        result = write_to_memory(
            content="SEBE targets £200-500B",
            entry_type="fact",
            importance=7,
        )
        
        assert result["success"] is True
        assert result["log_result"] is not None
        assert result["db_result"] is not None
        mock_add_memory.assert_called_once()

    @patch("tools.memory.writer.add_memory")
    def test_write_to_memory_log_only(self, mock_add_memory, tmp_memory_dirs):
        """Log-only mode skips database."""
        result = write_to_memory(
            content="Quick note",
            entry_type="fact",
            log_to_file=True,
            add_to_db=False,
        )
        
        assert result["success"] is True
        assert result["log_result"] is not None
        assert result["db_result"] is None
        mock_add_memory.assert_not_called()

    @patch("tools.memory.writer.add_memory")
    def test_write_to_memory_db_only(self, mock_add_memory, tmp_memory_dirs):
        """DB-only mode skips log file."""
        mock_add_memory.return_value = {
            "success": True,
            "entry": {"id": 1, "content": "Test"}
        }
        
        result = write_to_memory(
            content="Structured fact",
            entry_type="fact",
            log_to_file=False,
            add_to_db=True,
        )
        
        assert result["success"] is True
        assert result["log_result"] is None
        assert result["db_result"] is not None
        mock_add_memory.assert_called_once()

    @patch("tools.memory.writer.add_memory")
    def test_write_to_memory_with_tags(self, mock_add_memory, tmp_memory_dirs):
        """Tags are passed through correctly."""
        mock_add_memory.return_value = {"success": True, "entry": {}}
        
        result = write_to_memory(
            content="Tagged entry",
            entry_type="fact",
            tags=["sebe", "revenue"],
        )
        
        assert result["success"] is True
        # Check add_memory was called with tags
        call_kwargs = mock_add_memory.call_args[1]
        assert call_kwargs["tags"] == ["sebe", "revenue"]

    @patch("tools.memory.writer.add_memory")
    def test_write_to_memory_duplicate_not_fatal(self, mock_add_memory, tmp_memory_dirs):
        """Duplicate DB entry doesn't fail the operation."""
        mock_add_memory.return_value = {
            "success": False,
            "error": "Duplicate content"
        }
        
        result = write_to_memory("Duplicate", entry_type="fact")
        
        # Should still succeed because duplicate is expected
        assert result["success"] is True
        assert result["log_result"]["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# MEMORY.md Update Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestAppendToMemoryFile:
    """Test appending to MEMORY.md sections."""

    def test_append_to_memory_file_basic(self, tmp_memory_dirs):
        """Append to existing section in MEMORY.md."""
        from tools.memory import config
        memory_file = config.MEMORY_FILE
        content = """# Persistent Memory

## Key Facts

- Existing fact

## Other Section

- Other content
"""
        memory_file.write_text(content, encoding="utf-8")
        
        result = append_to_memory_file("New fact", section="key_facts")
        assert result["success"] is True
        
        updated = memory_file.read_text(encoding="utf-8")
        assert "New fact" in updated
        assert "Existing fact" in updated

    def test_append_to_memory_file_missing_file(self, tmp_memory_dirs):
        """Error if MEMORY.md doesn't exist."""
        # File doesn't exist in tmp_path
        result = append_to_memory_file("Fact", section="key_facts")
        assert result["success"] is False
        assert "does not exist" in result["error"].lower()

    def test_append_to_memory_file_missing_section(self, tmp_memory_dirs):
        """Error if section doesn't exist."""
        memory_file = tmp_memory_dirs["memory_dir"] / "MEMORY.md"
        memory_file.write_text("# Memory\n\n## Only Section\n- Item\n", encoding="utf-8")
        
        result = append_to_memory_file("Fact", section="nonexistent_section")
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_append_to_memory_file_at_end(self, tmp_memory_dirs):
        """Append to section at end of file."""
        from tools.memory import config
        memory_file = config.MEMORY_FILE
        content = """# Memory

## Key Facts

- Existing fact
"""
        memory_file.write_text(content, encoding="utf-8")
        
        result = append_to_memory_file("New fact", section="key_facts")
        assert result["success"] is True
        
        updated = memory_file.read_text(encoding="utf-8")
        assert "New fact" in updated

    def test_append_to_memory_file_before_separator(self, tmp_memory_dirs):
        """Append before horizontal rule."""
        from tools.memory import config
        memory_file = config.MEMORY_FILE
        content = """# Memory

## Key Facts

- Existing fact

---
*Footer*
"""
        memory_file.write_text(content, encoding="utf-8")
        
        result = append_to_memory_file("New fact", section="key_facts")
        assert result["success"] is True
        
        updated = memory_file.read_text(encoding="utf-8")
        lines = updated.split("\n")
        new_fact_idx = next(i for i, line in enumerate(lines) if "New fact" in line)
        separator_idx = next(i for i, line in enumerate(lines) if line.strip() == "---")
        assert new_fact_idx < separator_idx

    def test_append_to_memory_file_updates_timestamp(self, tmp_memory_dirs):
        """Last updated timestamp is updated."""
        from tools.memory import config
        memory_file = config.MEMORY_FILE
        content = """# Memory

## Key Facts

- Existing fact

*Last updated: 2026-01-01*
"""
        memory_file.write_text(content, encoding="utf-8")
        
        result = append_to_memory_file("New fact", section="key_facts")
        assert result["success"] is True
        
        updated = memory_file.read_text(encoding="utf-8")
        today = datetime.now().strftime("%Y-%m-%d")
        assert f"*Last updated: {today}*" in updated
