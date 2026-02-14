"""
SEBE Memory Database — SQLite CRUD operations.

Four tables:
    memory_entries  — facts, preferences, insights, events
    tasks           — campaign action items with status tracking
    contacts        — people and organisations
    interactions    — log of all communications

Usage (CLI):
    python -m tools.memory.db --action add-memory --type fact --content "SEBE targets £200-500B"
    python -m tools.memory.db --action search --query "Green Party"
    python -m tools.memory.db --action add-task --title "Email IPPR" --priority high
    python -m tools.memory.db --action list-tasks --status pending
    python -m tools.memory.db --action add-contact --name "Bedford Chair" --org "Green Party"
    python -m tools.memory.db --action log-interaction --contact-id 1 --channel email --direction outbound --subject "SEBE submission"
    python -m tools.memory.db --action stats
"""

import json
import sys
import hashlib
import argparse
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import (
    DB_PATH, DATA_DIR,
    VALID_MEMORY_TYPES, VALID_TASK_STATUSES, VALID_TASK_PRIORITIES,
    VALID_CONTACT_STATUSES, VALID_CHANNELS, VALID_DIRECTIONS,
)


def get_connection() -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes if they don't exist."""
    c = conn.cursor()

    # Memory entries — general knowledge store
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT UNIQUE,
            importance INTEGER DEFAULT 5 CHECK(importance BETWEEN 1 AND 10),
            tags TEXT,
            context TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Tasks — campaign action tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            assigned_to TEXT,
            due_date DATE,
            related_contact_id INTEGER,
            completed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (related_contact_id) REFERENCES contacts(id)
        )
    ''')

    # Contacts — people and organisations
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organisation TEXT,
            role TEXT,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'not_contacted',
            notes TEXT,
            last_contacted DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Interactions — communication log
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            channel TEXT NOT NULL,
            direction TEXT NOT NULL,
            subject TEXT,
            content TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            response_received INTEGER DEFAULT 0,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    ''')

    # Indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_mem_type ON memory_entries(type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_mem_active ON memory_entries(is_active)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_mem_importance ON memory_entries(importance)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_task_priority ON tasks(priority)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_contact_status ON contacts(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_interaction_contact ON interactions(contact_id)')

    conn.commit()


def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convert sqlite3.Row to dictionary, or None."""
    return dict(row) if row else None


def _content_hash(content: str) -> str:
    """SHA256 hash for deduplication (truncated to 16 chars)."""
    return hashlib.sha256(content.strip().lower().encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Memory entries
# ---------------------------------------------------------------------------

def add_memory(
    content: str,
    entry_type: str = "fact",
    importance: int = 5,
    tags: Optional[List[str]] = None,
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a memory entry. Returns dict with success status."""
    if entry_type not in VALID_MEMORY_TYPES:
        return {"success": False, "error": f"Invalid type. Must be one of: {VALID_MEMORY_TYPES}"}

    ch = _content_hash(content)
    conn = get_connection()
    cur = conn.cursor()

    # Deduplicate
    cur.execute("SELECT id, content FROM memory_entries WHERE content_hash = ?", (ch,))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return {"success": False, "error": "Duplicate content", "existing_id": existing["id"]}

    tags_json = json.dumps(tags) if tags else None
    cur.execute('''
        INSERT INTO memory_entries (type, content, content_hash, importance, tags, context)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (entry_type, content, ch, importance, tags_json, context))
    entry_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM memory_entries WHERE id = ?", (entry_id,))
    entry = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "entry": entry, "message": f"Memory #{entry_id} created"}


def search_memory(
    query: str,
    entry_type: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Search memory entries by text (SQL LIKE)."""
    conn = get_connection()
    cur = conn.cursor()
    pattern = f"%{query}%"

    if entry_type:
        cur.execute('''
            SELECT * FROM memory_entries
            WHERE is_active = 1 AND type = ?
            AND (content LIKE ? OR tags LIKE ? OR context LIKE ?)
            ORDER BY importance DESC, created_at DESC LIMIT ?
        ''', (entry_type, pattern, pattern, pattern, limit))
    else:
        cur.execute('''
            SELECT * FROM memory_entries
            WHERE is_active = 1
            AND (content LIKE ? OR tags LIKE ? OR context LIKE ?)
            ORDER BY importance DESC, created_at DESC LIMIT ?
        ''', (pattern, pattern, pattern, limit))

    entries = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "entries": entries, "query": query, "count": len(entries)}


def list_memory(
    entry_type: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 100,
) -> Dict[str, Any]:
    """List active memory entries, optionally filtered."""
    conn = get_connection()
    cur = conn.cursor()

    conditions = ["is_active = 1", "importance >= ?"]
    params: list = [min_importance]

    if entry_type:
        conditions.append("type = ?")
        params.append(entry_type)

    where = " AND ".join(conditions)
    cur.execute(f'''
        SELECT * FROM memory_entries WHERE {where}
        ORDER BY importance DESC, created_at DESC LIMIT ?
    ''', params + [limit])

    entries = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "entries": entries, "count": len(entries)}


def delete_memory(entry_id: int, hard: bool = False) -> Dict[str, Any]:
    """Soft-delete (default) or hard-delete a memory entry."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM memory_entries WHERE id = ?", (entry_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Entry {entry_id} not found"}

    if hard:
        cur.execute("DELETE FROM memory_entries WHERE id = ?", (entry_id,))
        msg = f"Entry {entry_id} permanently deleted"
    else:
        cur.execute("UPDATE memory_entries SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (entry_id,))
        msg = f"Entry {entry_id} deactivated"

    conn.commit()
    conn.close()
    return {"success": True, "message": msg}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
    related_contact_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new task."""
    if priority not in VALID_TASK_PRIORITIES:
        return {"success": False, "error": f"Invalid priority. Must be one of: {VALID_TASK_PRIORITIES}"}

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO tasks (title, description, priority, assigned_to, due_date, related_contact_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, priority, assigned_to, due_date, related_contact_id))
    task_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "task": task, "message": f"Task #{task_id} created"}


def update_task(task_id: int, **kwargs) -> Dict[str, Any]:
    """Update task fields. Pass status='completed' to mark done."""
    allowed = {"title", "description", "status", "priority", "assigned_to", "due_date", "related_contact_id"}
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Task {task_id} not found"}

    updates = []
    values = []
    for field, value in kwargs.items():
        if field not in allowed:
            continue
        if field == "status" and value not in VALID_TASK_STATUSES:
            conn.close()
            return {"success": False, "error": f"Invalid status. Must be one of: {VALID_TASK_STATUSES}"}
        if field == "priority" and value not in VALID_TASK_PRIORITIES:
            conn.close()
            return {"success": False, "error": f"Invalid priority. Must be one of: {VALID_TASK_PRIORITIES}"}
        updates.append(f"{field} = ?")
        values.append(value)
        # Auto-set completed_at when marking complete
        if field == "status" and value == "completed":
            updates.append("completed_at = CURRENT_TIMESTAMP")

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(task_id)

    cur.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()

    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "task": task, "message": f"Task #{task_id} updated"}


def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """List tasks, optionally filtered by status and/or priority."""
    conn = get_connection()
    cur = conn.cursor()

    conditions = []
    params: list = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if priority:
        conditions.append("priority = ?")
        params.append(priority)

    where = " AND ".join(conditions) if conditions else "1=1"
    cur.execute(f'''
        SELECT * FROM tasks WHERE {where}
        ORDER BY
            CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                          WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END,
            due_date ASC NULLS LAST,
            created_at DESC
        LIMIT ?
    ''', params + [limit])

    tasks = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "tasks": tasks, "count": len(tasks)}


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def add_contact(
    name: str,
    organisation: Optional[str] = None,
    role: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new contact."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO contacts (name, organisation, role, email, phone, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, organisation, role, email, phone, notes))
    contact_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    contact = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "contact": contact, "message": f"Contact #{contact_id} created"}


def update_contact(contact_id: int, **kwargs) -> Dict[str, Any]:
    """Update contact fields."""
    allowed = {"name", "organisation", "role", "email", "phone", "status", "notes"}
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM contacts WHERE id = ?", (contact_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Contact {contact_id} not found"}

    updates = []
    values = []
    for field, value in kwargs.items():
        if field not in allowed:
            continue
        if field == "status" and value not in VALID_CONTACT_STATUSES:
            conn.close()
            return {"success": False, "error": f"Invalid status. Must be one of: {VALID_CONTACT_STATUSES}"}
        updates.append(f"{field} = ?")
        values.append(value)

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(contact_id)

    cur.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()

    cur.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    contact = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "contact": contact, "message": f"Contact #{contact_id} updated"}


def list_contacts(
    status: Optional[str] = None,
    organisation: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """List contacts, optionally filtered."""
    conn = get_connection()
    cur = conn.cursor()

    conditions = []
    params: list = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if organisation:
        conditions.append("organisation LIKE ?")
        params.append(f"%{organisation}%")

    where = " AND ".join(conditions) if conditions else "1=1"
    cur.execute(f'''
        SELECT * FROM contacts WHERE {where}
        ORDER BY last_contacted DESC NULLS LAST, name ASC
        LIMIT ?
    ''', params + [limit])

    contacts = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "contacts": contacts, "count": len(contacts)}


# ---------------------------------------------------------------------------
# Interactions
# ---------------------------------------------------------------------------

def log_interaction(
    contact_id: int,
    channel: str,
    direction: str,
    subject: Optional[str] = None,
    content: Optional[str] = None,
) -> Dict[str, Any]:
    """Log an interaction with a contact."""
    if channel not in VALID_CHANNELS:
        return {"success": False, "error": f"Invalid channel. Must be one of: {VALID_CHANNELS}"}
    if direction not in VALID_DIRECTIONS:
        return {"success": False, "error": f"Invalid direction. Must be one of: {VALID_DIRECTIONS}"}

    conn = get_connection()
    cur = conn.cursor()

    # Verify contact exists
    cur.execute("SELECT id FROM contacts WHERE id = ?", (contact_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Contact {contact_id} not found"}

    cur.execute('''
        INSERT INTO interactions (contact_id, channel, direction, subject, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (contact_id, channel, direction, subject, content))
    interaction_id = cur.lastrowid

    # Update contact's last_contacted and status
    cur.execute('''
        UPDATE contacts SET last_contacted = CURRENT_TIMESTAMP,
        status = CASE WHEN status = 'not_contacted' THEN 'contacted' ELSE status END,
        updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (contact_id,))

    conn.commit()

    cur.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,))
    interaction = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "interaction": interaction, "message": f"Interaction #{interaction_id} logged"}


def list_interactions(
    contact_id: Optional[int] = None,
    channel: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """List interactions, optionally filtered by contact or channel."""
    conn = get_connection()
    cur = conn.cursor()

    conditions = []
    params: list = []

    if contact_id:
        conditions.append("i.contact_id = ?")
        params.append(contact_id)
    if channel:
        conditions.append("i.channel = ?")
        params.append(channel)

    where = " AND ".join(conditions) if conditions else "1=1"
    cur.execute(f'''
        SELECT i.*, c.name as contact_name, c.organisation as contact_org
        FROM interactions i
        JOIN contacts c ON i.contact_id = c.id
        WHERE {where}
        ORDER BY i.sent_at DESC
        LIMIT ?
    ''', params + [limit])

    interactions = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "interactions": interactions, "count": len(interactions)}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats() -> Dict[str, Any]:
    """Get summary statistics across all tables."""
    conn = get_connection()
    cur = conn.cursor()

    # Memory
    cur.execute("SELECT type, COUNT(*) as count FROM memory_entries WHERE is_active = 1 GROUP BY type")
    mem_by_type = {r["type"]: r["count"] for r in cur.fetchall()}

    # Tasks
    cur.execute("SELECT status, COUNT(*) as count FROM tasks GROUP BY status")
    tasks_by_status = {r["status"]: r["count"] for r in cur.fetchall()}

    # Contacts
    cur.execute("SELECT status, COUNT(*) as count FROM contacts GROUP BY status")
    contacts_by_status = {r["status"]: r["count"] for r in cur.fetchall()}

    # Interactions
    cur.execute("SELECT COUNT(*) as count FROM interactions")
    interaction_count = cur.fetchone()["count"]

    # Pending follow-ups (contacted but no response)
    cur.execute('''
        SELECT c.id, c.name, c.organisation, c.last_contacted
        FROM contacts c
        WHERE c.status = 'contacted'
        ORDER BY c.last_contacted ASC
        LIMIT 10
    ''')
    pending_followups = [_row_to_dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "success": True,
        "stats": {
            "memory_entries": mem_by_type,
            "tasks": tasks_by_status,
            "contacts": contacts_by_status,
            "interactions": interaction_count,
            "pending_followups": pending_followups,
        }
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SEBE Memory Database")
    parser.add_argument("--action", required=True, choices=[
        "add-memory", "search", "list-memory", "delete-memory",
        "add-task", "update-task", "list-tasks",
        "add-contact", "update-contact", "list-contacts",
        "log-interaction", "list-interactions",
        "stats",
    ])
    parser.add_argument("--id", type=int)
    parser.add_argument("--content", help="Memory content or interaction content")
    parser.add_argument("--type", help="Memory type")
    parser.add_argument("--importance", type=int, default=5)
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--context", help="Context note")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--title", help="Task title")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--status", help="Status filter or update value")
    parser.add_argument("--priority", help="Priority filter or value")
    parser.add_argument("--assigned-to", help="Task assignee")
    parser.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    parser.add_argument("--name", help="Contact name")
    parser.add_argument("--org", help="Contact organisation")
    parser.add_argument("--role", help="Contact role")
    parser.add_argument("--email", help="Contact email")
    parser.add_argument("--phone", help="Contact phone")
    parser.add_argument("--notes", help="Contact notes")
    parser.add_argument("--contact-id", type=int, help="Contact ID for interactions")
    parser.add_argument("--channel", help="Interaction channel")
    parser.add_argument("--direction", help="Interaction direction")
    parser.add_argument("--subject", help="Interaction subject")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--hard-delete", action="store_true")

    args = parser.parse_args()
    result = None

    if args.action == "add-memory":
        if not args.content:
            parser.error("--content required")
        tags = args.tags.split(",") if args.tags else None
        result = add_memory(args.content, args.type or "fact", args.importance, tags, args.context)

    elif args.action == "search":
        if not args.query:
            parser.error("--query required")
        result = search_memory(args.query, args.type, args.limit)

    elif args.action == "list-memory":
        result = list_memory(args.type, args.importance, args.limit)

    elif args.action == "delete-memory":
        if not args.id:
            parser.error("--id required")
        result = delete_memory(args.id, args.hard_delete)

    elif args.action == "add-task":
        if not args.title:
            parser.error("--title required")
        result = add_task(args.title, args.description, args.priority or "medium",
                          args.assigned_to, args.due_date, args.contact_id)

    elif args.action == "update-task":
        if not args.id:
            parser.error("--id required")
        kwargs = {}
        if args.title: kwargs["title"] = args.title
        if args.description: kwargs["description"] = args.description
        if args.status: kwargs["status"] = args.status
        if args.priority: kwargs["priority"] = args.priority
        if args.assigned_to: kwargs["assigned_to"] = args.assigned_to
        if args.due_date: kwargs["due_date"] = args.due_date
        result = update_task(args.id, **kwargs)

    elif args.action == "list-tasks":
        result = list_tasks(args.status, args.priority, args.limit)

    elif args.action == "add-contact":
        if not args.name:
            parser.error("--name required")
        result = add_contact(args.name, args.org, args.role, args.email, args.phone, args.notes)

    elif args.action == "update-contact":
        if not args.id:
            parser.error("--id required")
        kwargs = {}
        if args.name: kwargs["name"] = args.name
        if args.org: kwargs["organisation"] = args.org
        if args.role: kwargs["role"] = args.role
        if args.email: kwargs["email"] = args.email
        if args.phone: kwargs["phone"] = args.phone
        if args.status: kwargs["status"] = args.status
        if args.notes: kwargs["notes"] = args.notes
        result = update_contact(args.id, **kwargs)

    elif args.action == "list-contacts":
        result = list_contacts(args.status, args.org, args.limit)

    elif args.action == "log-interaction":
        if not args.contact_id or not args.channel or not args.direction:
            parser.error("--contact-id, --channel, and --direction required")
        result = log_interaction(args.contact_id, args.channel, args.direction,
                                 args.subject, args.content)

    elif args.action == "list-interactions":
        result = list_interactions(args.contact_id, args.channel, args.limit)

    elif args.action == "stats":
        result = get_stats()

    if result:
        if result.get("success"):
            print(f"OK {result.get('message', 'Success')}")
        else:
            print(f"ERROR {result.get('error')}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
