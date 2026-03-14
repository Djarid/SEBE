"""
Configuration for the SEBE conversation archive system.

All path constants and settings in one place. Paths resolve relative to the
automation_framework/ directory (two levels up from this file).
"""

import os
import secrets
from pathlib import Path

# Root of automation_framework/
FRAMEWORK_ROOT = Path(__file__).parent.parent.parent

# Conversations data directory (outside repo)
CONVERSATIONS_DATA_DIR = Path(
    os.getenv("CONVERSATIONS_DATA_DIR", Path.home() / "sebe-data")
)

# SQLite database
CONVERSATIONS_DB_PATH = Path(
    os.getenv("CONVERSATIONS_DB_PATH", CONVERSATIONS_DATA_DIR / "conversations.db")
)

# Imports directory
IMPORTS_DIR = CONVERSATIONS_DATA_DIR / "imports"

# Hash salt for content deduplication (fallback to random if not set)
HASH_SALT = os.getenv("CONVERSATIONS_HASH_SALT", secrets.token_hex(16))

# Valid platforms
VALID_PLATFORMS = ["whatsapp", "discord", "email", "signal", "mastodon"]

# Valid conversation types
VALID_CONVERSATION_TYPES = ["group", "dm", "thread", "channel", "email_thread"]

# Valid attribution levels
VALID_ATTRIBUTION_LEVELS = ["full", "org_only", "anonymous"]

# Valid tag types
VALID_TAG_TYPES = [
    "claim",
    "concession",
    "question",
    "answer",
    "action_item",
    "decision",
    "evidence",
    "policy_position",
    "agreement",
    "disagreement",
    "clarification",
]

# Valid follow-up types
VALID_FOLLOWUP_TYPES = [
    "needs_response",
    "awaiting_info",
    "action_required",
    "decision_needed",
]

# Valid follow-up statuses
VALID_FOLLOWUP_STATUSES = ["open", "in_progress", "completed", "cancelled"]

# Valid participant roles
VALID_ROLES = ["owner", "admin", "moderator", "member", "observer"]
