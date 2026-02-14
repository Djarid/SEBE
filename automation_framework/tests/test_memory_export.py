"""
Tests for tools.memory.export — Database backup to JSON/markdown.

All tests use in-memory databases and temporary directories.
Tests cover JSON export, markdown export, and default paths.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from tools.memory.export import (
    export_all,
    export_as_markdown,
)


# ═══════════════════════════════════════════════════════════════════════════
# JSON Export Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestExportAll:
    """Test JSON export functionality."""

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    @patch("tools.memory.export.get_stats")
    def test_export_all_with_data(
        self, mock_stats, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path
    ):
        """Export with sample data creates valid JSON."""
        # Setup mocks
        mock_memory.return_value = {
            "entries": [
                {"id": 1, "type": "fact", "content": "SEBE revenue £200-500B"}
            ]
        }
        mock_tasks.return_value = {
            "tasks": [{"id": 1, "title": "Email IPPR", "status": "pending"}]
        }
        mock_contacts.return_value = {
            "contacts": [{"id": 1, "name": "Test Contact"}]
        }
        mock_interactions.return_value = {
            "interactions": [{"id": 1, "channel": "email"}]
        }
        mock_stats.return_value = {"stats": {}}
        
        output_path = tmp_path / "export.json"
        result = export_all(output_path)
        
        assert result["success"] is True
        assert output_path.exists()
        assert result["counts"]["memory_entries"] == 1
        assert result["counts"]["tasks"] == 1
        
        # Verify JSON is valid
        exported_data = json.loads(output_path.read_text())
        assert "exported_at" in exported_data
        assert "version" in exported_data
        assert len(exported_data["memory_entries"]) == 1
        assert len(exported_data["tasks"]) == 1

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    @patch("tools.memory.export.get_stats")
    def test_export_all_empty_database(
        self, mock_stats, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path
    ):
        """Export empty database creates valid JSON."""
        # Setup empty mocks
        mock_memory.return_value = {"entries": []}
        mock_tasks.return_value = {"tasks": []}
        mock_contacts.return_value = {"contacts": []}
        mock_interactions.return_value = {"interactions": []}
        mock_stats.return_value = {"stats": {}}
        
        output_path = tmp_path / "empty_export.json"
        result = export_all(output_path)
        
        assert result["success"] is True
        assert output_path.exists()
        assert result["counts"]["memory_entries"] == 0
        assert result["counts"]["tasks"] == 0

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    @patch("tools.memory.export.get_stats")
    def test_export_all_default_path(
        self, mock_stats, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path, monkeypatch
    ):
        """Export without path uses default location."""
        # Mock empty data
        mock_memory.return_value = {"entries": []}
        mock_tasks.return_value = {"tasks": []}
        mock_contacts.return_value = {"contacts": []}
        mock_interactions.return_value = {"interactions": []}
        mock_stats.return_value = {"stats": {}}
        
        # Patch EXPORT_DIR
        monkeypatch.setattr("tools.memory.export.EXPORT_DIR", tmp_path)
        
        result = export_all()
        
        assert result["success"] is True
        assert "memory_export_" in result["path"]
        assert Path(result["path"]).exists()

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    @patch("tools.memory.export.get_stats")
    def test_export_all_json_keys(
        self, mock_stats, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path
    ):
        """Exported JSON contains all expected keys."""
        # Mock data
        mock_memory.return_value = {"entries": []}
        mock_tasks.return_value = {"tasks": []}
        mock_contacts.return_value = {"contacts": []}
        mock_interactions.return_value = {"interactions": []}
        mock_stats.return_value = {"stats": {}}
        
        output_path = tmp_path / "export.json"
        export_all(output_path)
        
        data = json.loads(output_path.read_text())
        expected_keys = {
            "exported_at", "version", "memory_entries",
            "tasks", "contacts", "interactions", "stats"
        }
        assert expected_keys.issubset(set(data.keys()))


# ═══════════════════════════════════════════════════════════════════════════
# Markdown Export Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestExportAsMarkdown:
    """Test markdown export functionality."""

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    def test_export_as_markdown_with_data(
        self, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path
    ):
        """Markdown export with data creates readable file."""
        # Setup mocks
        mock_memory.return_value = {
            "entries": [
                {"id": 1, "type": "fact", "content": "SEBE revenue", "importance": 8}
            ]
        }
        mock_tasks.return_value = {
            "tasks": [
                {
                    "id": 1,
                    "title": "Email IPPR",
                    "status": "pending",
                    "priority": "high",
                    "description": "Send academic brief",
                }
            ]
        }
        mock_contacts.return_value = {
            "contacts": [
                {
                    "id": 1,
                    "name": "IPPR Contact",
                    "organisation": "IPPR",
                    "role": "Policy Director",
                    "email": "policy@ippr.org",
                    "status": "contacted",
                }
            ]
        }
        mock_interactions.return_value = {
            "interactions": [
                {
                    "id": 1,
                    "contact_id": 1,
                    "contact_name": "IPPR Contact",
                    "channel": "email",
                    "direction": "outbound",
                    "sent_at": "2026-02-14 12:00:00",
                    "subject": "Policy submission",
                }
            ]
        }
        
        output_path = tmp_path / "export.md"
        result = export_as_markdown(output_path)
        
        assert result["success"] is True
        assert output_path.exists()
        
        content = output_path.read_text()
        assert "# SEBE Memory Export" in content
        assert "## Memory Entries" in content
        assert "SEBE revenue" in content
        assert "## Tasks" in content
        assert "Email IPPR" in content
        assert "## Contacts" in content
        assert "IPPR Contact" in content

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    def test_export_as_markdown_empty_database(
        self, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path
    ):
        """Markdown export of empty database."""
        # Empty mocks
        mock_memory.return_value = {"entries": []}
        mock_tasks.return_value = {"tasks": []}
        mock_contacts.return_value = {"contacts": []}
        mock_interactions.return_value = {"interactions": []}
        
        output_path = tmp_path / "empty.md"
        result = export_as_markdown(output_path)
        
        assert result["success"] is True
        assert output_path.exists()
        
        content = output_path.read_text()
        assert "# SEBE Memory Export" in content
        # Should not have section headers for empty sections
        assert "## Memory Entries" not in content

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    def test_export_as_markdown_task_formatting(
        self, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path
    ):
        """Markdown export formats tasks correctly."""
        mock_memory.return_value = {"entries": []}
        mock_tasks.return_value = {
            "tasks": [
                {
                    "id": 1,
                    "title": "Completed task",
                    "status": "completed",
                    "priority": "low",
                    "description": None,
                    "due_date": None,
                },
                {
                    "id": 2,
                    "title": "High priority task",
                    "status": "pending",
                    "priority": "high",
                    "description": "Important work",
                    "due_date": "2026-03-01",
                },
            ]
        }
        mock_contacts.return_value = {"contacts": []}
        mock_interactions.return_value = {"interactions": []}
        
        output_path = tmp_path / "tasks.md"
        export_as_markdown(output_path)
        
        content = output_path.read_text()
        assert "✅" in content  # Completed icon
        assert "⏳" in content  # Pending icon
        assert "[high]" in content
        assert "(due 2026-03-01)" in content

    @patch("tools.memory.export.list_memory")
    @patch("tools.memory.export.list_tasks")
    @patch("tools.memory.export.list_contacts")
    @patch("tools.memory.export.list_interactions")
    def test_export_as_markdown_default_path(
        self, mock_interactions, mock_contacts, mock_tasks, mock_memory, tmp_path, monkeypatch
    ):
        """Markdown export without path uses default location."""
        mock_memory.return_value = {"entries": []}
        mock_tasks.return_value = {"tasks": []}
        mock_contacts.return_value = {"contacts": []}
        mock_interactions.return_value = {"interactions": []}
        
        # Patch EXPORT_DIR
        monkeypatch.setattr("tools.memory.export.EXPORT_DIR", tmp_path)
        
        result = export_as_markdown()
        
        assert result["success"] is True
        assert "memory_export_" in result["path"]
        assert ".md" in result["path"]
