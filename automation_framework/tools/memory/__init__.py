"""
SEBE Memory System — Persistent memory for agent sessions.

Provides:
    - SQLite storage for facts, tasks, contacts, and interactions
    - Daily markdown session logs
    - MEMORY.md for curated always-loaded context
    - Session-start context loading
    - JSON/markdown export for backup

Modules:
    config  — Path constants and settings
    db      — SQLite CRUD operations
    reader  — Session-start context loader
    writer  — Dual-write to logs and database
    export  — Database backup to JSON/markdown
"""

from .db import (
    add_memory, search_memory, list_memory, delete_memory,
    add_task, update_task, list_tasks,
    add_contact, update_contact, list_contacts,
    log_interaction, list_interactions,
    get_stats,
)

from .reader import (
    read_memory_file, read_daily_log, read_recent_logs,
    load_session_context, format_as_markdown,
)

from .writer import (
    append_to_daily_log, write_to_memory, append_to_memory_file,
)

from .export import export_all, export_as_markdown

__all__ = [
    # DB
    "add_memory", "search_memory", "list_memory", "delete_memory",
    "add_task", "update_task", "list_tasks",
    "add_contact", "update_contact", "list_contacts",
    "log_interaction", "list_interactions",
    "get_stats",
    # Reader
    "read_memory_file", "read_daily_log", "read_recent_logs",
    "load_session_context", "format_as_markdown",
    # Writer
    "append_to_daily_log", "write_to_memory", "append_to_memory_file",
    # Export
    "export_all", "export_as_markdown",
]
