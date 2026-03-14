"""
Conversation export module.

Exports conversations from the database to various formats.
Supports full, anonymised (Chatham House Rule), and summary exports.

Usage:
    python -m tools.conversations.exporter --conversation-id 1 --format markdown
    python -m tools.conversations.exporter --conversation-id 1 --format anonymised
    python -m tools.conversations.exporter --conversation-id 1 --format summary
    python -m tools.conversations.exporter --campaign "Sci Tech SEBE Review" --format markdown
    python -m tools.conversations.exporter --conversation-id 1 --format markdown --output export.md
"""

import sys
import re
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from .config import HASH_SALT
from .db import (
    get_connection,
    list_conversations,
    list_messages,
    get_conversation_participants,
)


def _anonymise_name(name: str, salt: str) -> str:
    """Pseudonymise a participant name using salted hash. Returns 'Participant_XXXX'."""
    h = hashlib.sha256(f"{name}{salt}".encode()).hexdigest()[:6]
    return f"Participant_{h.upper()}"


def _redact_phone_numbers(text: str) -> str:
    """Replace phone numbers in text with [phone redacted]."""
    # Pattern for UK phone numbers in common formats
    patterns = [
        r"\+44\s?\d{4}\s?\d{6}",  # +44 1234 567890 or +441234567890
        r"\+44\s?\d{3}\s?\d{3}\s?\d{4}",  # +44 123 456 7890
        r"0\d{4}\s?\d{6}",  # 01234 567890
        r"0\d{3}\s?\d{3}\s?\d{4}",  # 0123 456 7890
    ]

    result = text
    for pattern in patterns:
        result = re.sub(pattern, "[phone redacted]", result)

    return result


def _is_phone_number(text: str) -> bool:
    """Check if a string looks like a phone number."""
    # Check for common phone number patterns
    patterns = [
        r"^\+\d{10,15}$",  # International format
        r"^0\d{9,10}$",  # UK format
        r"^\+44\s?\d{4}\s?\d{6}$",  # +44 with spaces
    ]

    for pattern in patterns:
        if re.match(pattern, text.strip()):
            return True

    return False


def _format_timestamp(timestamp_str: str) -> str:
    """Format timestamp as HH:MM, DD/MM/YYYY (WhatsApp style)."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%H:%M, %d/%m/%Y")
    except (ValueError, AttributeError):
        return timestamp_str


def _render_markdown_full(
    conversation: Dict[str, Any],
    messages: List[Dict[str, Any]],
    participants: List[Dict[str, Any]],
) -> str:
    """Render full markdown export."""
    lines = []

    # Header
    lines.append(f"# Conversation: {conversation.get('subject', 'Untitled')}")
    lines.append(f"**Campaign:** {conversation.get('campaign', 'None')}")
    lines.append(f"**Platform:** {conversation.get('platform', 'unknown')}")

    # Date range
    if messages:
        first_ts = _format_timestamp(messages[-1]["platform_timestamp"])
        last_ts = _format_timestamp(messages[0]["platform_timestamp"])
        lines.append(f"**Date range:** {first_ts} to {last_ts}")

    # Participants
    participant_names = []
    for p in participants:
        name = p["display_name"]
        # Use "Participant N" if display name is a phone number
        if _is_phone_number(name):
            idx = participants.index(p) + 1
            participant_names.append(f"Participant {idx}")
        else:
            participant_names.append(name)

    lines.append(f"**Participants:** {', '.join(participant_names)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Messages (reverse chronological to chronological)
    participant_name_map = {}
    for idx, p in enumerate(participants):
        if _is_phone_number(p["display_name"]):
            participant_name_map[p["id"]] = f"Participant {idx + 1}"
        else:
            participant_name_map[p["id"]] = p["display_name"]

    for message in reversed(messages):
        timestamp = _format_timestamp(message["platform_timestamp"])
        participant_id = message["participant_id"]
        display_name = participant_name_map.get(
            participant_id, message.get("participant_name", "Unknown")
        )
        content = message["content_text"]

        lines.append(f"**[{timestamp}] {display_name}:**")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def _render_markdown_anonymised(
    conversation: Dict[str, Any],
    messages: List[Dict[str, Any]],
    participants: List[Dict[str, Any]],
    salt: str,
) -> str:
    """Render anonymised markdown export (Chatham House Rule)."""
    lines = []

    # Chatham House Rule notice
    lines.append(
        "> This export follows Chatham House Rule. Participant identities have been anonymised."
    )
    lines.append("")

    # Header
    lines.append(f"# Conversation: {conversation.get('subject', 'Untitled')}")
    lines.append(f"**Campaign:** {conversation.get('campaign', 'None')}")
    lines.append(f"**Platform:** {conversation.get('platform', 'unknown')}")

    # Date range
    if messages:
        first_ts = _format_timestamp(messages[-1]["platform_timestamp"])
        last_ts = _format_timestamp(messages[0]["platform_timestamp"])
        lines.append(f"**Date range:** {first_ts} to {last_ts}")

    # Anonymised participants
    anon_names = [_anonymise_name(p["display_name"], salt) for p in participants]
    lines.append(f"**Participants:** {', '.join(anon_names)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Build participant ID to anonymised name map
    participant_anon_map = {}
    for p in participants:
        participant_anon_map[p["id"]] = _anonymise_name(p["display_name"], salt)

    # Messages (reverse chronological to chronological)
    for message in reversed(messages):
        timestamp = _format_timestamp(message["platform_timestamp"])
        participant_id = message["participant_id"]
        anon_name = participant_anon_map.get(
            participant_id, _anonymise_name("Unknown", salt)
        )
        content = _redact_phone_numbers(message["content_text"])

        lines.append(f"**[{timestamp}] {anon_name}:**")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def _render_summary(
    conversation: Dict[str, Any],
    messages: List[Dict[str, Any]],
    participants: List[Dict[str, Any]],
) -> str:
    """Render summary export."""
    lines = []

    # Header
    lines.append(f"# Conversation Summary: {conversation.get('subject', 'Untitled')}")
    lines.append(f"**Campaign:** {conversation.get('campaign', 'None')}")
    lines.append(f"**Platform:** {conversation.get('platform', 'unknown')}")
    lines.append(
        f"**Conversation Type:** {conversation.get('conversation_type', 'unknown')}"
    )

    # Date range
    if messages:
        first_ts = _format_timestamp(messages[-1]["platform_timestamp"])
        last_ts = _format_timestamp(messages[0]["platform_timestamp"])
        lines.append(f"**Date range:** {first_ts} to {last_ts}")

    lines.append(f"**Total messages:** {len(messages)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Participants with message counts
    lines.append("## Participants")
    lines.append("")
    for p in participants:
        name = p["display_name"]
        if _is_phone_number(name):
            idx = participants.index(p) + 1
            name = f"Participant {idx}"
        lines.append(
            f"- **{name}** ({p['organisation'] or 'No org'}): {p['message_count']} messages"
        )

    lines.append("")
    lines.append("---")
    lines.append("")

    # Check for tagged messages
    conn = get_connection()
    cur = conn.cursor()

    # Get message IDs for this conversation
    message_ids = [m["id"] for m in messages]

    if message_ids:
        placeholders = ",".join("?" * len(message_ids))
        cur.execute(
            f"""
            SELECT mt.tag_type, COUNT(*) as count
            FROM message_tags mt
            WHERE mt.message_id IN ({placeholders})
            GROUP BY mt.tag_type
        """,
            message_ids,
        )

        tag_counts = {row["tag_type"]: row["count"] for row in cur.fetchall()}

        if tag_counts:
            lines.append("## Tagged Messages")
            lines.append("")
            for tag_type, count in sorted(tag_counts.items()):
                lines.append(f"- **{tag_type}**: {count}")
            lines.append("")

    conn.close()

    return "\n".join(lines)


def export_conversation(
    conversation_id: int = None,
    campaign: str = None,
    format: str = "markdown",
    output_path: str = None,
    db_path: str = None,
) -> dict:
    """Export a conversation to the specified format.

    Args:
        conversation_id: Specific conversation to export (mutually exclusive with campaign)
        campaign: Export all conversations for a campaign
        format: 'markdown', 'anonymised', or 'summary'
        output_path: Write to file (default: stdout via return value)
        db_path: Override DB path for testing

    Returns:
        Dict with success, format, content (the rendered text), and metadata
    """
    if not conversation_id and not campaign:
        return {
            "success": False,
            "error": "Either conversation_id or campaign is required",
        }

    if conversation_id and campaign:
        return {
            "success": False,
            "error": "Cannot specify both conversation_id and campaign",
        }

    if format not in ["markdown", "anonymised", "summary"]:
        return {
            "success": False,
            "error": f"Invalid format: {format}. Must be markdown, anonymised, or summary",
        }

    try:
        # Get conversation(s)
        if campaign:
            result = list_conversations(campaign=campaign, limit=1000)
            if not result.get("success") or not result.get("conversations"):
                return {
                    "success": False,
                    "error": f"No conversations found for campaign: {campaign}",
                }

            # For campaign export, concatenate multiple conversations
            all_content = []
            for conv in result["conversations"]:
                conv_id = conv["id"]
                single_export = _export_single_conversation(conv_id, format, db_path)
                if single_export.get("success"):
                    all_content.append(single_export["content"])
                    all_content.append("\n\n" + "=" * 80 + "\n\n")

            content = "\n".join(all_content).rstrip()
            metadata = {
                "campaign": campaign,
                "conversation_count": len(result["conversations"]),
                "format": format,
            }
        else:
            single_export = _export_single_conversation(
                conversation_id, format, db_path
            )
            if not single_export.get("success"):
                return single_export

            content = single_export["content"]
            metadata = single_export["metadata"]

        # Write to file if requested
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(content, encoding="utf-8")
            metadata["output_path"] = str(output_file)

        return {
            "success": True,
            "format": format,
            "content": content,
            "metadata": metadata,
        }

    except Exception as e:
        return {"success": False, "error": f"Export failed: {str(e)}"}


def _export_single_conversation(
    conversation_id: int,
    format: str,
    db_path: str = None,
) -> dict:
    """Export a single conversation."""
    # Get conversation metadata
    conn = get_connection(db_path=Path(db_path) if db_path else None)
    cur = conn.cursor()

    cur.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
    conv_row = cur.fetchone()

    if not conv_row:
        conn.close()
        return {"success": False, "error": f"Conversation {conversation_id} not found"}

    conversation = dict(conv_row)
    conn.close()

    # Get messages
    messages_result = list_messages(conversation_id=conversation_id, limit=10000)
    if not messages_result.get("success"):
        return {"success": False, "error": "Failed to retrieve messages"}

    messages = messages_result["messages"]

    if not messages:
        # Handle conversations with no messages
        content = f"# Conversation: {conversation.get('subject', 'Untitled')}\n\n*No messages in this conversation.*"
        return {
            "success": True,
            "content": content,
            "metadata": {
                "conversation_id": conversation_id,
                "format": format,
                "message_count": 0,
            },
        }

    # Get participants
    participants_result = get_conversation_participants(conversation_id)
    if not participants_result.get("success"):
        return {"success": False, "error": "Failed to retrieve participants"}

    participants = participants_result["participants"]

    # Render based on format
    if format == "markdown":
        content = _render_markdown_full(conversation, messages, participants)
    elif format == "anonymised":
        content = _render_markdown_anonymised(
            conversation, messages, participants, HASH_SALT
        )
    elif format == "summary":
        content = _render_summary(conversation, messages, participants)
    else:
        return {"success": False, "error": f"Unknown format: {format}"}

    metadata = {
        "conversation_id": conversation_id,
        "format": format,
        "message_count": len(messages),
        "participant_count": len(participants),
        "subject": conversation.get("subject"),
        "campaign": conversation.get("campaign"),
        "platform": conversation.get("platform"),
    }

    return {
        "success": True,
        "content": content,
        "metadata": metadata,
    }


def main():
    parser = argparse.ArgumentParser(description="Export conversations")
    parser.add_argument("--conversation-id", type=int, help="Conversation ID to export")
    parser.add_argument("--campaign", help="Export all conversations for a campaign")
    parser.add_argument(
        "--format", default="markdown", choices=["markdown", "anonymised", "summary"]
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: print to stdout)"
    )

    args = parser.parse_args()

    if not args.conversation_id and not args.campaign:
        parser.error("Either --conversation-id or --campaign is required")

    result = export_conversation(
        conversation_id=args.conversation_id,
        campaign=args.campaign,
        format=args.format,
        output_path=args.output,
    )

    if result.get("success"):
        if args.output:
            print(f"OK Exported to {args.output}")
        else:
            print(result["content"])
    else:
        print(f"ERROR {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
