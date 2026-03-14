"""
Conversation import orchestrator.

Parses raw chat exports and imports them into the conversations database.
Handles participant resolution, contact linking, and deduplication.

Usage:
    python -m tools.conversations.importer --platform whatsapp --file chat.txt --campaign "Sci Tech SEBE Review"
    python -m tools.conversations.importer --platform whatsapp --file chat.txt --campaign "Name" --subject "SEBE Policy Review"
    python -m tools.conversations.importer --platform whatsapp --file chat.txt --campaign "Name" --contact-map '{"Jason Huxley": 1, "+44 7977 490410": 5}'
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

from . import parser, db
from .config import CONVERSATIONS_DB_PATH


def import_conversation(
    file_path: str,
    platform: str,
    campaign: str,
    subject: Optional[str] = None,
    conversation_type: str = "group",
    contact_map: Optional[Dict[str, int]] = None,
    db_path: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Import a conversation from a chat export file.

    Args:
        file_path: Path to the chat export file
        platform: Platform name (whatsapp, discord, etc.)
        campaign: Campaign/topic name for this conversation
        subject: Optional subject line
        conversation_type: Type of conversation (group, dm, thread, etc.)
        contact_map: Optional mapping of sender_raw -> memory.db contact_id
        db_path: Optional custom database path
        force: If True, delete existing conversation with same campaign before importing

    Returns:
        Dictionary with success status, conversation_id, and import statistics
    """
    # Read the file
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}",
        }

    try:
        text = file_path_obj.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read file: {e}",
        }

    # Parse the messages
    try:
        messages = parser.parse(platform, text)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse {platform} format: {e}",
        }

    if not messages:
        return {
            "success": False,
            "error": "No messages found in file",
        }

    # Check for existing conversation with same campaign
    existing_convs = db.list_conversations(platform=platform, campaign=campaign)
    if existing_convs["success"] and existing_convs["conversations"]:
        if not force:
            return {
                "success": False,
                "error": f"Conversation with campaign '{campaign}' already exists (use --force to reimport)",
                "existing_conversation_id": existing_convs["conversations"][0]["id"],
            }
        else:
            # Delete existing conversation and its messages
            # SQLite will cascade delete messages due to foreign key constraint
            existing_id = existing_convs["conversations"][0]["id"]
            conn = db.get_connection(Path(db_path) if db_path else None)
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM messages WHERE conversation_id = ?", (existing_id,)
            )
            cur.execute("DELETE FROM conversations WHERE id = ?", (existing_id,))
            conn.commit()
            conn.close()

    # Create the conversation
    conv_result = db.create_conversation(
        platform=platform,
        conversation_type=conversation_type,
        subject=subject,
        campaign=campaign,
    )

    if not conv_result["success"]:
        return {
            "success": False,
            "error": f"Failed to create conversation: {conv_result.get('error')}",
        }

    conversation_id = conv_result["conversation"]["id"]

    # Resolve all unique participants
    unique_senders = set(m.sender_raw for m in messages if not m.is_system)
    participant_map = {}  # sender_raw -> participant_id
    participant_stats = {}  # participant_id -> {"name": str, "message_count": int}

    for sender_raw in unique_senders:
        resolve_result = db.resolve_participant(platform, sender_raw)
        if not resolve_result["success"]:
            return {
                "success": False,
                "error": f"Failed to resolve participant '{sender_raw}': {resolve_result.get('error')}",
            }

        participant_id = resolve_result["participant_id"]
        participant_map[sender_raw] = participant_id
        participant_stats[participant_id] = {
            "name": sender_raw,
            "message_count": 0,
        }

        # Link to canonical contact if mapping provided
        if contact_map and sender_raw in contact_map:
            contact_id = contact_map[sender_raw]
            update_result = db.update_participant(
                participant_id,
                canonical_contact_id=contact_id,
            )
            if not update_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to link participant '{sender_raw}' to contact {contact_id}: {update_result.get('error')}",
                }

    # Create a "system" participant for system messages
    system_participant_id = None
    system_messages = [m for m in messages if m.is_system]
    if system_messages:
        system_resolve = db.resolve_participant(platform, "__system__")
        if system_resolve["success"]:
            system_participant_id = system_resolve["participant_id"]
            # Update display name to "System"
            db.update_participant(system_participant_id, display_name="System")

    # Import messages in chronological order
    messages_imported = 0
    messages_skipped = 0

    for msg in sorted(messages, key=lambda m: m.timestamp):
        if msg.is_system:
            if system_participant_id:
                # Import system messages with special participant
                msg_result = db.add_message(
                    conversation_id=conversation_id,
                    participant_id=system_participant_id,
                    content_text=msg.content,
                    platform_timestamp=msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    attribution_level="anonymous",
                )
                if msg_result["success"]:
                    messages_imported += 1
                else:
                    messages_skipped += 1
            else:
                messages_skipped += 1
            continue

        # Regular message
        participant_id = participant_map.get(msg.sender_raw)
        if not participant_id:
            messages_skipped += 1
            continue

        msg_result = db.add_message(
            conversation_id=conversation_id,
            participant_id=participant_id,
            content_text=msg.content,
            platform_timestamp=msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        )

        if msg_result["success"]:
            messages_imported += 1
            participant_stats[participant_id]["message_count"] += 1
        else:
            messages_skipped += 1

    # Build participants summary
    participants_summary = [
        {
            "id": pid,
            "name": stats["name"],
            "messages": stats["message_count"],
        }
        for pid, stats in participant_stats.items()
    ]
    participants_summary.sort(key=lambda p: p["messages"], reverse=True)

    return {
        "success": True,
        "message": f"Imported {messages_imported} messages from {len(participants_summary)} participants",
        "conversation_id": conversation_id,
        "messages_imported": messages_imported,
        "messages_skipped": messages_skipped,
        "participants": participants_summary,
        "campaign": campaign,
        "file": file_path,
    }


def main():
    parser_cli = argparse.ArgumentParser(
        description="Import conversations from chat exports"
    )
    parser_cli.add_argument(
        "--platform",
        required=True,
        choices=["whatsapp", "discord"],
        help="Platform name",
    )
    parser_cli.add_argument(
        "--file",
        required=True,
        help="Path to chat export file",
    )
    parser_cli.add_argument(
        "--campaign",
        required=True,
        help="Campaign/topic name",
    )
    parser_cli.add_argument(
        "--subject",
        help="Conversation subject line",
    )
    parser_cli.add_argument(
        "--type",
        default="group",
        choices=["group", "dm", "thread", "channel", "email_thread"],
        help="Conversation type",
    )
    parser_cli.add_argument(
        "--contact-map",
        help="JSON string mapping sender names to contact IDs",
    )
    parser_cli.add_argument(
        "--force",
        action="store_true",
        help="Reimport (delete existing conversation with same campaign)",
    )
    parser_cli.add_argument(
        "--db-path",
        help="Custom database path",
    )

    args = parser_cli.parse_args()

    # Parse contact map if provided
    contact_map = None
    if args.contact_map:
        try:
            contact_map = json.loads(args.contact_map)
            if not isinstance(contact_map, dict):
                print("ERROR Contact map must be a JSON object", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR Invalid JSON in contact-map: {e}", file=sys.stderr)
            sys.exit(1)

    # Import the conversation
    result = import_conversation(
        file_path=args.file,
        platform=args.platform,
        campaign=args.campaign,
        subject=args.subject,
        conversation_type=args.type,
        contact_map=contact_map,
        db_path=args.db_path,
        force=args.force,
    )

    # Output result
    if result.get("success"):
        print(f"OK {result.get('message', 'Import complete')}")
    else:
        print(f"ERROR {result.get('error')}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
