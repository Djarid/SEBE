"""
SEBE Memory Reader — Session-start context loader.

Loads all persistent context for an agent session:
    1. MEMORY.md (curated persistent facts)
    2. Recent daily logs (today + yesterday)
    3. High-importance DB entries
    4. Pending tasks
    5. Contacts awaiting follow-up

Usage (CLI):
    python -m tools.memory.reader                     # Full context load
    python -m tools.memory.reader --memory-only       # Just MEMORY.md
    python -m tools.memory.reader --tasks-only        # Just pending tasks
    python -m tools.memory.reader --format json       # JSON output
    python -m tools.memory.reader --days 3            # 3 days of logs
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import (
    MEMORY_FILE, LOGS_DIR, PROJECT_CONTEXT, AUTHOR_CONTEXT,
    DEFAULT_LOG_DAYS, DEFAULT_MIN_IMPORTANCE,
)
from .db import list_memory, list_tasks, list_contacts, get_stats


def read_memory_file() -> Dict[str, Any]:
    """Read MEMORY.md and parse sections."""
    if not MEMORY_FILE.exists():
        return {"success": False, "error": f"MEMORY.md not found at {MEMORY_FILE}"}

    content = MEMORY_FILE.read_text(encoding="utf-8")
    sections = {}
    current = "preamble"
    lines: list = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if lines:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip().lower().replace(" ", "_")
            lines = []
        else:
            lines.append(line)
    if lines:
        sections[current] = "\n".join(lines).strip()

    return {
        "success": True,
        "content": content,
        "sections": list(sections.keys()),
        "last_modified": datetime.fromtimestamp(MEMORY_FILE.stat().st_mtime).isoformat(),
    }


def read_daily_log(date: str) -> Dict[str, Any]:
    """Read a daily log file by date (YYYY-MM-DD)."""
    log_file = LOGS_DIR / f"{date}.md"
    if not log_file.exists():
        return {"success": False, "date": date, "error": f"No log for {date}"}

    content = log_file.read_text(encoding="utf-8")
    events = [
        line.strip()[2:]
        for line in content.split("\n")
        if line.strip().startswith("- ") or line.strip().startswith("* ")
    ]
    return {"success": True, "date": date, "content": content, "events": events}


def read_recent_logs(days: int = DEFAULT_LOG_DAYS) -> List[Dict[str, Any]]:
    """Read the most recent daily logs."""
    today = datetime.now().date()
    return [read_daily_log((today - timedelta(days=i)).isoformat()) for i in range(days)]


def load_session_context(
    include_memory: bool = True,
    include_logs: bool = True,
    include_db: bool = True,
    include_tasks: bool = True,
    include_contacts: bool = True,
    log_days: int = DEFAULT_LOG_DAYS,
    min_importance: int = DEFAULT_MIN_IMPORTANCE,
) -> Dict[str, Any]:
    """
    Load all context for a new agent session.

    Returns a structured dict with all available context.
    """
    result: Dict[str, Any] = {
        "loaded_at": datetime.now().isoformat(),
        "memory_file": None,
        "daily_logs": [],
        "db_entries": [],
        "pending_tasks": [],
        "active_contacts": [],
        "stats": None,
    }

    if include_memory:
        result["memory_file"] = read_memory_file()

    if include_logs:
        result["daily_logs"] = read_recent_logs(days=log_days)

    if include_db:
        db_result = list_memory(min_importance=min_importance, limit=50)
        result["db_entries"] = db_result.get("entries", []) if db_result.get("success") else []

    if include_tasks:
        # Get all non-completed tasks
        for status in ("in_progress", "pending", "blocked"):
            task_result = list_tasks(status=status)
            if task_result.get("success"):
                result["pending_tasks"].extend(task_result.get("tasks", []))

    if include_contacts:
        # Contacts awaiting follow-up
        contact_result = list_contacts(status="contacted")
        if contact_result.get("success"):
            result["active_contacts"] = contact_result.get("contacts", [])

    result["stats"] = get_stats().get("stats")

    return result


def format_as_markdown(ctx: Dict[str, Any]) -> str:
    """Format session context as markdown for agent injection."""
    parts = []

    # MEMORY.md
    mem = ctx.get("memory_file")
    if mem and mem.get("success"):
        parts.append(mem["content"])
        parts.append("\n---\n")

    # Daily logs
    for log in ctx.get("daily_logs", []):
        if log.get("success"):
            parts.append(f"## Session Log: {log['date']}\n")
            parts.append(log["content"])
            parts.append("")

    # Pending tasks
    tasks = ctx.get("pending_tasks", [])
    if tasks:
        parts.append("## Pending Tasks\n")
        for t in tasks:
            status_icon = {"in_progress": "🔄", "pending": "⏳", "blocked": "🚫"}.get(t["status"], "•")
            priority_tag = f" [{t['priority']}]" if t["priority"] != "medium" else ""
            due = f" (due {t['due_date']})" if t.get("due_date") else ""
            parts.append(f"- {status_icon} {t['title']}{priority_tag}{due}")
            if t.get("description"):
                parts.append(f"  {t['description']}")
        parts.append("")

    # Contacts awaiting follow-up
    contacts = ctx.get("active_contacts", [])
    if contacts:
        parts.append("## Contacts Awaiting Follow-up\n")
        for c in contacts:
            org = f" ({c['organisation']})" if c.get("organisation") else ""
            last = f" — last contacted {c['last_contacted']}" if c.get("last_contacted") else ""
            parts.append(f"- {c['name']}{org}{last}")
        parts.append("")

    # DB entries (high importance)
    entries = ctx.get("db_entries", [])
    if entries:
        parts.append("## Key Facts\n")
        for e in entries:
            parts.append(f"- [{e['type']}] {e['content']}")
        parts.append("")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="SEBE Memory Reader — Load session context")
    parser.add_argument("--memory-only", action="store_true", help="Only load MEMORY.md")
    parser.add_argument("--tasks-only", action="store_true", help="Only load pending tasks")
    parser.add_argument("--logs-only", action="store_true", help="Only load daily logs")
    parser.add_argument("--days", type=int, default=DEFAULT_LOG_DAYS, help="Days of logs to include")
    parser.add_argument("--min-importance", type=int, default=DEFAULT_MIN_IMPORTANCE)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args()

    if args.memory_only:
        ctx = load_session_context(
            include_logs=False, include_db=False,
            include_tasks=False, include_contacts=False,
        )
    elif args.tasks_only:
        ctx = load_session_context(
            include_memory=False, include_logs=False,
            include_db=False, include_contacts=False,
        )
    elif args.logs_only:
        ctx = load_session_context(
            include_memory=False, include_db=False,
            include_tasks=False, include_contacts=False,
            log_days=args.days,
        )
    else:
        ctx = load_session_context(
            log_days=args.days, min_importance=args.min_importance,
        )

    if args.format == "markdown":
        print(format_as_markdown(ctx))
    else:
        print(json.dumps(ctx, indent=2, default=str))


if __name__ == "__main__":
    main()
