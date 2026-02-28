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


def __getattr__(name: str):
    """Lazy-load submodule exports to avoid RuntimeWarning when running
    submodules directly (e.g. python -m tools.memory.db)."""

    _db_names = {
        "add_memory",
        "search_memory",
        "list_memory",
        "delete_memory",
        "add_task",
        "update_task",
        "list_tasks",
        "add_contact",
        "update_contact",
        "list_contacts",
        "log_interaction",
        "list_interactions",
        "get_stats",
    }
    _reader_names = {
        "read_memory_file",
        "read_daily_log",
        "read_recent_logs",
        "load_session_context",
        "format_as_markdown",
    }
    _writer_names = {
        "append_to_daily_log",
        "write_to_memory",
        "append_to_memory_file",
    }
    _export_names = {
        "export_all",
        "export_as_markdown",
    }

    if name in _db_names:
        from . import db

        return getattr(db, name)
    if name in _reader_names:
        from . import reader

        return getattr(reader, name)
    if name in _writer_names:
        from . import writer

        return getattr(writer, name)
    if name in _export_names:
        from . import export

        return getattr(export, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # DB
    "add_memory",
    "search_memory",
    "list_memory",
    "delete_memory",
    "add_task",
    "update_task",
    "list_tasks",
    "add_contact",
    "update_contact",
    "list_contacts",
    "log_interaction",
    "list_interactions",
    "get_stats",
    # Reader
    "read_memory_file",
    "read_daily_log",
    "read_recent_logs",
    "load_session_context",
    "format_as_markdown",
    # Writer
    "append_to_daily_log",
    "write_to_memory",
    "append_to_memory_file",
    # Export
    "export_all",
    "export_as_markdown",
]
