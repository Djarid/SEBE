"""
SEBE Conversation Archive Database — SQLite CRUD operations.

Five tables:
    participants            — people in conversations (deduplicated across platforms)
    participant_identities  — platform-specific identifiers for participants
    conversations           — conversation metadata
    messages                — message content with attribution
    message_tags            — semantic tags on messages

Plus FTS5 virtual table for full-text search.

Usage (CLI):
    python -m tools.conversations.db --action add-participant --display-name "John Smith" --org "Green Party"
    python -m tools.conversations.db --action add-identity --participant-id 1 --platform whatsapp --platform-user-id "+44123456789"
    python -m tools.conversations.db --action create-conversation --platform whatsapp --conversation-type group --subject "SEBE Discussion"
    python -m tools.conversations.db --action add-message --conversation-id 1 --participant-id 1 --content "SEBE is brilliant" --platform-timestamp "2026-03-12 10:30:00"
    python -m tools.conversations.db --action search --query "SEBE revenue"
    python -m tools.conversations.db --action stats
"""

import json
import sys
import hashlib
import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .config import (
    CONVERSATIONS_DB_PATH,
    CONVERSATIONS_DATA_DIR,
    VALID_PLATFORMS,
    VALID_CONVERSATION_TYPES,
    VALID_ATTRIBUTION_LEVELS,
    VALID_TAG_TYPES,
    HASH_SALT,
)


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    path = db_path or CONVERSATIONS_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "PRAGMA synchronous=NORMAL"
    )  # Reduce fsync calls (Mac Mini portability)
    conn.execute("PRAGMA foreign_keys=ON")
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes if they don't exist."""
    c = conn.cursor()

    # Participants — deduplicated people across platforms
    c.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT NOT NULL,
            organisation TEXT,
            canonical_contact_id INTEGER,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Participant identities — platform-specific user IDs
    c.execute("""
        CREATE TABLE IF NOT EXISTS participant_identities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            platform_user_id TEXT NOT NULL,
            display_name TEXT,
            verified INTEGER DEFAULT 0,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME,
            FOREIGN KEY (participant_id) REFERENCES participants(id),
            UNIQUE(platform, platform_user_id)
        )
    """)

    # Conversations — message containers
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            conversation_type TEXT NOT NULL DEFAULT 'group',
            subject TEXT,
            campaign TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_message_at DATETIME,
            default_attribution TEXT DEFAULT 'full',
            metadata_json TEXT
        )
    """)

    # Messages — content with attribution
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            participant_id INTEGER NOT NULL,
            content_text TEXT NOT NULL,
            in_reply_to_id INTEGER,
            platform_timestamp DATETIME NOT NULL,
            ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            attribution_level TEXT DEFAULT 'full',
            metadata_json TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id),
            FOREIGN KEY (participant_id) REFERENCES participants(id),
            FOREIGN KEY (in_reply_to_id) REFERENCES messages(id)
        )
    """)

    # Message tags — semantic annotation
    c.execute("""
        CREATE TABLE IF NOT EXISTS message_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            tag_type TEXT NOT NULL,
            tag_value TEXT,
            tagged_by TEXT NOT NULL DEFAULT 'human',
            confidence REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
    """)

    # FTS5 for full-text search
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS message_search USING fts5(
            content,
            participant_name,
            conversation_subject,
            campaign,
            content=messages,
            content_rowid=id,
            tokenize='porter unicode61'
        )
    """)

    # Indexes
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_participants_contact ON participants(canonical_contact_id)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_identities_participant ON participant_identities(participant_id)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_identities_platform ON participant_identities(platform, platform_user_id)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversations_platform ON conversations(platform)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversations_campaign ON conversations(campaign)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_participant ON messages(participant_id)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(platform_timestamp)"
    )
    c.execute("CREATE INDEX IF NOT EXISTS idx_tags_message ON message_tags(message_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tags_type ON message_tags(tag_type)")

    conn.commit()


def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convert sqlite3.Row to dictionary, or None."""
    return dict(row) if row else None


def _content_hash(content: str) -> str:
    """SHA256 hash for deduplication (truncated to 16 chars)."""
    salted = f"{HASH_SALT}{content.strip().lower()}"
    return hashlib.sha256(salted.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Participants
# ---------------------------------------------------------------------------


def add_participant(
    display_name: str,
    organisation: Optional[str] = None,
    canonical_contact_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new participant. Returns dict with success status."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO participants (display_name, organisation, canonical_contact_id, notes)
        VALUES (?, ?, ?, ?)
    """,
        (display_name, organisation, canonical_contact_id, notes),
    )
    participant_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
    participant = _row_to_dict(cur.fetchone())
    conn.close()
    return {
        "success": True,
        "participant": participant,
        "message": f"Participant #{participant_id} created",
    }


def update_participant(participant_id: int, **kwargs) -> Dict[str, Any]:
    """Update participant fields."""
    allowed = {"display_name", "organisation", "canonical_contact_id", "notes"}
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM participants WHERE id = ?", (participant_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Participant {participant_id} not found"}

    updates = []
    values = []
    for field, value in kwargs.items():
        if field not in allowed:
            continue
        updates.append(f"{field} = ?")
        values.append(value)

    if not updates:
        conn.close()
        return {"success": False, "error": "No valid fields to update"}

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(participant_id)

    cur.execute(f"UPDATE participants SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()

    cur.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
    participant = _row_to_dict(cur.fetchone())
    conn.close()
    return {
        "success": True,
        "participant": participant,
        "message": f"Participant #{participant_id} updated",
    }


def add_identity(
    participant_id: int,
    platform: str,
    platform_user_id: str,
    display_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a platform identity to a participant."""
    if platform not in VALID_PLATFORMS:
        return {
            "success": False,
            "error": f"Invalid platform. Must be one of: {VALID_PLATFORMS}",
        }

    conn = get_connection()
    cur = conn.cursor()

    # Verify participant exists
    cur.execute("SELECT id FROM participants WHERE id = ?", (participant_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Participant {participant_id} not found"}

    # Check for duplicate
    cur.execute(
        "SELECT id FROM participant_identities WHERE platform = ? AND platform_user_id = ?",
        (platform, platform_user_id),
    )
    existing = cur.fetchone()
    if existing:
        conn.close()
        return {
            "success": False,
            "error": "Identity already exists",
            "identity_id": existing["id"],
        }

    cur.execute(
        """
        INSERT INTO participant_identities (participant_id, platform, platform_user_id, display_name)
        VALUES (?, ?, ?, ?)
    """,
        (participant_id, platform, platform_user_id, display_name),
    )
    identity_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM participant_identities WHERE id = ?", (identity_id,))
    identity = _row_to_dict(cur.fetchone())
    conn.close()
    return {
        "success": True,
        "identity": identity,
        "message": f"Identity #{identity_id} created",
    }


def resolve_participant(platform: str, platform_user_id: str) -> Dict[str, Any]:
    """Get-or-create pattern: resolve platform identity to participant."""
    if platform not in VALID_PLATFORMS:
        return {
            "success": False,
            "error": f"Invalid platform. Must be one of: {VALID_PLATFORMS}",
        }

    conn = get_connection()
    cur = conn.cursor()

    # Try to find existing identity
    cur.execute(
        """
        SELECT pi.*, p.display_name as participant_name, p.organisation
        FROM participant_identities pi
        JOIN participants p ON pi.participant_id = p.id
        WHERE pi.platform = ? AND pi.platform_user_id = ?
    """,
        (platform, platform_user_id),
    )
    identity = _row_to_dict(cur.fetchone())

    if identity:
        # Update last_seen
        cur.execute(
            "UPDATE participant_identities SET last_seen = CURRENT_TIMESTAMP WHERE id = ?",
            (identity["id"],),
        )
        conn.commit()
        conn.close()
        return {
            "success": True,
            "participant_id": identity["participant_id"],
            "identity": identity,
            "created": False,
        }

    # Create new participant and identity
    cur.execute(
        "INSERT INTO participants (display_name) VALUES (?)", (platform_user_id,)
    )
    participant_id = cur.lastrowid

    cur.execute(
        """
        INSERT INTO participant_identities (participant_id, platform, platform_user_id, display_name)
        VALUES (?, ?, ?, ?)
    """,
        (participant_id, platform, platform_user_id, platform_user_id),
    )
    identity_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM participant_identities WHERE id = ?", (identity_id,))
    identity = _row_to_dict(cur.fetchone())
    conn.close()

    return {
        "success": True,
        "participant_id": participant_id,
        "identity": identity,
        "created": True,
        "message": f"New participant #{participant_id} created",
    }


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------


def create_conversation(
    platform: str,
    conversation_type: str,
    subject: Optional[str] = None,
    campaign: Optional[str] = None,
    default_attribution: str = "full",
) -> Dict[str, Any]:
    """Create a new conversation."""
    if platform not in VALID_PLATFORMS:
        return {
            "success": False,
            "error": f"Invalid platform. Must be one of: {VALID_PLATFORMS}",
        }
    if conversation_type not in VALID_CONVERSATION_TYPES:
        return {
            "success": False,
            "error": f"Invalid type. Must be one of: {VALID_CONVERSATION_TYPES}",
        }
    if default_attribution not in VALID_ATTRIBUTION_LEVELS:
        return {
            "success": False,
            "error": f"Invalid attribution. Must be one of: {VALID_ATTRIBUTION_LEVELS}",
        }

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO conversations (platform, conversation_type, subject, campaign, default_attribution)
        VALUES (?, ?, ?, ?, ?)
    """,
        (platform, conversation_type, subject, campaign, default_attribution),
    )
    conversation_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
    conversation = _row_to_dict(cur.fetchone())
    conn.close()
    return {
        "success": True,
        "conversation": conversation,
        "message": f"Conversation #{conversation_id} created",
    }


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


def add_message(
    conversation_id: int,
    participant_id: int,
    content_text: str,
    platform_timestamp: str,
    in_reply_to_id: Optional[int] = None,
    attribution_level: str = "full",
    metadata_json: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a message to a conversation."""
    if attribution_level not in VALID_ATTRIBUTION_LEVELS:
        return {
            "success": False,
            "error": f"Invalid attribution. Must be one of: {VALID_ATTRIBUTION_LEVELS}",
        }

    conn = get_connection()
    cur = conn.cursor()

    # Verify conversation and participant exist
    cur.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Conversation {conversation_id} not found"}

    cur.execute("SELECT id FROM participants WHERE id = ?", (participant_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Participant {participant_id} not found"}

    cur.execute(
        """
        INSERT INTO messages (conversation_id, participant_id, content_text, platform_timestamp,
                             in_reply_to_id, attribution_level, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            conversation_id,
            participant_id,
            content_text,
            platform_timestamp,
            in_reply_to_id,
            attribution_level,
            metadata_json,
        ),
    )
    message_id = cur.lastrowid

    # Update conversation last_message_at
    cur.execute(
        "UPDATE conversations SET last_message_at = ? WHERE id = ?",
        (platform_timestamp, conversation_id),
    )

    # Insert into FTS5 table
    cur.execute(
        """
        INSERT INTO message_search(rowid, content, participant_name, conversation_subject, campaign)
        SELECT m.id, m.content_text, p.display_name, c.subject, c.campaign
        FROM messages m
        JOIN participants p ON m.participant_id = p.id
        JOIN conversations c ON m.conversation_id = c.id
        WHERE m.id = ?
    """,
        (message_id,),
    )

    conn.commit()

    cur.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
    message = _row_to_dict(cur.fetchone())
    conn.close()
    return {
        "success": True,
        "message": message,
        "message_text": f"Message #{message_id} added",
    }


def tag_message(
    message_id: int,
    tag_type: str,
    tag_value: Optional[str] = None,
    tagged_by: str = "human",
    confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a semantic tag to a message."""
    if tag_type not in VALID_TAG_TYPES:
        return {
            "success": False,
            "error": f"Invalid tag type. Must be one of: {VALID_TAG_TYPES}",
        }

    conn = get_connection()
    cur = conn.cursor()

    # Verify message exists
    cur.execute("SELECT id FROM messages WHERE id = ?", (message_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Message {message_id} not found"}

    cur.execute(
        """
        INSERT INTO message_tags (message_id, tag_type, tag_value, tagged_by, confidence)
        VALUES (?, ?, ?, ?, ?)
    """,
        (message_id, tag_type, tag_value, tagged_by, confidence),
    )
    tag_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM message_tags WHERE id = ?", (tag_id,))
    tag = _row_to_dict(cur.fetchone())
    conn.close()
    return {"success": True, "tag": tag, "message": f"Tag #{tag_id} added"}


# ---------------------------------------------------------------------------
# Search and List
# ---------------------------------------------------------------------------


def search_messages(
    query: str,
    campaign: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Full-text search across messages using FTS5."""
    conn = get_connection()
    cur = conn.cursor()

    # Build query with optional filters
    conditions = ["message_search MATCH ?"]
    params = [query]

    if campaign:
        conditions.append("c.campaign = ?")
        params.append(campaign)
    if platform:
        conditions.append("c.platform = ?")
        params.append(platform)

    where = " AND ".join(conditions)
    params.append(limit)

    cur.execute(
        f"""
        SELECT m.id, m.content_text, m.platform_timestamp,
               p.display_name as participant_name,
               c.subject as conversation_subject, c.campaign, c.platform
        FROM message_search ms
        JOIN messages m ON ms.rowid = m.id
        JOIN participants p ON m.participant_id = p.id
        JOIN conversations c ON m.conversation_id = c.id
        WHERE {where}
        ORDER BY m.platform_timestamp DESC LIMIT ?
    """,
        params,
    )

    messages = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {
        "success": True,
        "messages": messages,
        "query": query,
        "count": len(messages),
    }


def list_conversations(
    platform: Optional[str] = None,
    campaign: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """List conversations, optionally filtered."""
    conn = get_connection()
    cur = conn.cursor()

    conditions = []
    params: list = []

    if platform:
        conditions.append("platform = ?")
        params.append(platform)
    if campaign:
        conditions.append("campaign = ?")
        params.append(campaign)

    where = " AND ".join(conditions) if conditions else "1=1"
    cur.execute(
        f"""
        SELECT * FROM conversations WHERE {where}
        ORDER BY last_message_at DESC NULLS LAST, created_at DESC
        LIMIT ?
    """,
        params + [limit],
    )

    conversations = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {
        "success": True,
        "conversations": conversations,
        "count": len(conversations),
    }


def list_messages(
    conversation_id: Optional[int] = None,
    participant_id: Optional[int] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """List messages, optionally filtered by conversation or participant."""
    conn = get_connection()
    cur = conn.cursor()

    conditions = []
    params: list = []

    if conversation_id:
        conditions.append("m.conversation_id = ?")
        params.append(conversation_id)
    if participant_id:
        conditions.append("m.participant_id = ?")
        params.append(participant_id)

    where = " AND ".join(conditions) if conditions else "1=1"
    cur.execute(
        f"""
        SELECT m.*, p.display_name as participant_name
        FROM messages m
        JOIN participants p ON m.participant_id = p.id
        WHERE {where}
        ORDER BY m.platform_timestamp DESC
        LIMIT ?
    """,
        params + [limit],
    )

    messages = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "messages": messages, "count": len(messages)}


def get_conversation_participants(conversation_id: int) -> Dict[str, Any]:
    """Get all participants in a conversation."""
    conn = get_connection()
    cur = conn.cursor()

    # Verify conversation exists
    cur.execute("SELECT id FROM conversations WHERE id = ?", (conversation_id,))
    if not cur.fetchone():
        conn.close()
        return {"success": False, "error": f"Conversation {conversation_id} not found"}

    cur.execute(
        """
        SELECT DISTINCT p.id, p.display_name, p.organisation,
               COUNT(m.id) as message_count
        FROM participants p
        JOIN messages m ON p.id = m.participant_id
        WHERE m.conversation_id = ?
        GROUP BY p.id
        ORDER BY message_count DESC
    """,
        (conversation_id,),
    )

    participants = [_row_to_dict(r) for r in cur.fetchall()]
    conn.close()
    return {"success": True, "participants": participants, "count": len(participants)}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def get_stats() -> Dict[str, Any]:
    """Get summary statistics across all tables."""
    conn = get_connection()
    cur = conn.cursor()

    # Participants
    cur.execute("SELECT COUNT(*) as count FROM participants")
    participant_count = cur.fetchone()["count"]

    # Conversations by platform
    cur.execute(
        "SELECT platform, COUNT(*) as count FROM conversations GROUP BY platform"
    )
    conversations_by_platform = {r["platform"]: r["count"] for r in cur.fetchall()}

    # Messages by platform
    cur.execute("""
        SELECT c.platform, COUNT(m.id) as count
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        GROUP BY c.platform
    """)
    messages_by_platform = {r["platform"]: r["count"] for r in cur.fetchall()}

    # Total messages
    cur.execute("SELECT COUNT(*) as count FROM messages")
    total_messages = cur.fetchone()["count"]

    # Tags by type
    cur.execute(
        "SELECT tag_type, COUNT(*) as count FROM message_tags GROUP BY tag_type"
    )
    tags_by_type = {r["tag_type"]: r["count"] for r in cur.fetchall()}

    conn.close()
    return {
        "success": True,
        "stats": {
            "participants": participant_count,
            "conversations_by_platform": conversations_by_platform,
            "messages_by_platform": messages_by_platform,
            "total_messages": total_messages,
            "tags_by_type": tags_by_type,
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="SEBE Conversation Archive Database")
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "add-participant",
            "update-participant",
            "add-identity",
            "resolve-participant",
            "create-conversation",
            "add-message",
            "tag-message",
            "search",
            "list-conversations",
            "list-messages",
            "conversation-participants",
            "stats",
        ],
    )
    parser.add_argument("--id", type=int, help="Participant ID or message ID")
    parser.add_argument("--participant-id", type=int)
    parser.add_argument("--conversation-id", type=int)
    parser.add_argument("--message-id", type=int)
    parser.add_argument("--display-name", help="Participant display name")
    parser.add_argument("--org", help="Organisation")
    parser.add_argument("--canonical-contact-id", type=int)
    parser.add_argument("--notes", help="Notes")
    parser.add_argument("--platform", help="Platform name")
    parser.add_argument("--platform-user-id", help="Platform-specific user ID")
    parser.add_argument("--conversation-type", help="Conversation type")
    parser.add_argument("--subject", help="Conversation subject")
    parser.add_argument("--campaign", help="Campaign name")
    parser.add_argument("--attribution", help="Attribution level", default="full")
    parser.add_argument("--content", help="Message content")
    parser.add_argument(
        "--platform-timestamp", help="Message timestamp (YYYY-MM-DD HH:MM:SS)"
    )
    parser.add_argument("--in-reply-to", type=int, help="Reply to message ID")
    parser.add_argument("--metadata", help="JSON metadata")
    parser.add_argument("--tag-type", help="Tag type")
    parser.add_argument("--tag-value", help="Tag value")
    parser.add_argument("--tagged-by", default="human", help="Tagger (human/ai)")
    parser.add_argument("--confidence", type=float, help="Tag confidence (0-1)")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()
    result = None

    if args.action == "add-participant":
        if not args.display_name:
            parser.error("--display-name required")
        result = add_participant(
            args.display_name, args.org, args.canonical_contact_id, args.notes
        )

    elif args.action == "update-participant":
        if not args.id:
            parser.error("--id required")
        kwargs = {}
        if args.display_name:
            kwargs["display_name"] = args.display_name
        if args.org:
            kwargs["organisation"] = args.org
        if args.canonical_contact_id:
            kwargs["canonical_contact_id"] = args.canonical_contact_id
        if args.notes:
            kwargs["notes"] = args.notes
        result = update_participant(args.id, **kwargs)

    elif args.action == "add-identity":
        if not args.participant_id or not args.platform or not args.platform_user_id:
            parser.error(
                "--participant-id, --platform, and --platform-user-id required"
            )
        result = add_identity(
            args.participant_id, args.platform, args.platform_user_id, args.display_name
        )

    elif args.action == "resolve-participant":
        if not args.platform or not args.platform_user_id:
            parser.error("--platform and --platform-user-id required")
        result = resolve_participant(args.platform, args.platform_user_id)

    elif args.action == "create-conversation":
        if not args.platform or not args.conversation_type:
            parser.error("--platform and --conversation-type required")
        result = create_conversation(
            args.platform,
            args.conversation_type,
            args.subject,
            args.campaign,
            args.attribution,
        )

    elif args.action == "add-message":
        if (
            not args.conversation_id
            or not args.participant_id
            or not args.content
            or not args.platform_timestamp
        ):
            parser.error(
                "--conversation-id, --participant-id, --content, and --platform-timestamp required"
            )
        result = add_message(
            args.conversation_id,
            args.participant_id,
            args.content,
            args.platform_timestamp,
            args.in_reply_to,
            args.attribution,
            args.metadata,
        )

    elif args.action == "tag-message":
        if not args.message_id or not args.tag_type:
            parser.error("--message-id and --tag-type required")
        result = tag_message(
            args.message_id,
            args.tag_type,
            args.tag_value,
            args.tagged_by,
            args.confidence,
        )

    elif args.action == "search":
        if not args.query:
            parser.error("--query required")
        result = search_messages(args.query, args.campaign, args.platform, args.limit)

    elif args.action == "list-conversations":
        result = list_conversations(args.platform, args.campaign, args.limit)

    elif args.action == "list-messages":
        result = list_messages(args.conversation_id, args.participant_id, args.limit)

    elif args.action == "conversation-participants":
        if not args.conversation_id:
            parser.error("--conversation-id required")
        result = get_conversation_participants(args.conversation_id)

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
