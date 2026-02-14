"""
SEBE Memory Export — Backup database to JSON/markdown.

Dumps all SQLite tables to a dated JSON file for backup and portability.
Designed so backup destination can be configured later without changing
the export logic.

Usage (CLI):
    python -m tools.memory.export                         # Export to data/exports/
    python -m tools.memory.export --output /path/to/file  # Export to specific path
    python -m tools.memory.export --format markdown       # Markdown summary
    python -m tools.memory.export --tables tasks contacts  # Export specific tables
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import DATA_DIR
from .db import (
    get_connection, list_memory, list_tasks, list_contacts, list_interactions, get_stats,
)


EXPORT_DIR = DATA_DIR / "exports"


def export_all(output_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Export all database tables to a JSON file.

    Args:
        output_path: Where to write. Defaults to data/exports/YYYY-MM-DD_HHMMSS.json

    Returns:
        dict with export metadata
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = EXPORT_DIR / f"memory_export_{timestamp}.json"

    # Gather all data
    data = {
        "exported_at": datetime.now().isoformat(),
        "version": "1.0",
        "memory_entries": list_memory(min_importance=1, limit=10000).get("entries", []),
        "tasks": list_tasks(limit=10000).get("tasks", []),
        "contacts": list_contacts(limit=10000).get("contacts", []),
        "interactions": list_interactions(limit=10000).get("interactions", []),
        "stats": get_stats().get("stats"),
    }

    output_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    return {
        "success": True,
        "path": str(output_path),
        "counts": {
            "memory_entries": len(data["memory_entries"]),
            "tasks": len(data["tasks"]),
            "contacts": len(data["contacts"]),
            "interactions": len(data["interactions"]),
        },
        "message": f"Exported to {output_path}",
    }


def export_as_markdown(output_path: Optional[Path] = None) -> Dict[str, Any]:
    """Export a human-readable markdown summary of all data."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_path = EXPORT_DIR / f"memory_export_{timestamp}.md"

    parts = [f"# SEBE Memory Export — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]

    # Memory entries
    entries = list_memory(min_importance=1, limit=10000).get("entries", [])
    if entries:
        parts.append("## Memory Entries\n")
        for e in entries:
            parts.append(f"- **[{e['type']}]** (importance: {e['importance']}) {e['content']}")
        parts.append("")

    # Tasks
    tasks = list_tasks(limit=10000).get("tasks", [])
    if tasks:
        parts.append("## Tasks\n")
        for t in tasks:
            status_icon = {
                "completed": "✅", "in_progress": "🔄", "pending": "⏳",
                "blocked": "🚫", "cancelled": "✗",
            }.get(t["status"], "•")
            due = f" (due {t['due_date']})" if t.get("due_date") else ""
            parts.append(f"- {status_icon} **{t['title']}** [{t['priority']}]{due} — {t['status']}")
            if t.get("description"):
                parts.append(f"  {t['description']}")
        parts.append("")

    # Contacts
    contacts = list_contacts(limit=10000).get("contacts", [])
    if contacts:
        parts.append("## Contacts\n")
        for c in contacts:
            org = f" — {c['organisation']}" if c.get("organisation") else ""
            role = f" ({c['role']})" if c.get("role") else ""
            parts.append(f"- **{c['name']}**{role}{org} [{c['status']}]")
            if c.get("email"):
                parts.append(f"  Email: {c['email']}")
            if c.get("notes"):
                parts.append(f"  Notes: {c['notes']}")
        parts.append("")

    # Interactions
    interactions = list_interactions(limit=10000).get("interactions", [])
    if interactions:
        parts.append("## Interactions\n")
        for ix in interactions:
            name = ix.get("contact_name", f"Contact #{ix['contact_id']}")
            parts.append(f"- {ix['sent_at']} | {ix['direction']} {ix['channel']} | {name}")
            if ix.get("subject"):
                parts.append(f"  Subject: {ix['subject']}")
        parts.append("")

    parts.append(f"\n---\n*Exported {datetime.now().isoformat()}*\n")

    output_path.write_text("\n".join(parts), encoding="utf-8")
    return {
        "success": True,
        "path": str(output_path),
        "message": f"Markdown export to {output_path}",
    }


def main():
    parser = argparse.ArgumentParser(description="SEBE Memory Export — Backup to file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")

    args = parser.parse_args()
    output_path = Path(args.output) if args.output else None

    if args.format == "markdown":
        result = export_as_markdown(output_path)
    else:
        result = export_all(output_path)

    if result.get("success"):
        print(f"OK {result.get('message')}")
    else:
        print(f"ERROR {result.get('error')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
