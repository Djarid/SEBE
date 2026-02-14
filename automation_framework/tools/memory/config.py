"""
Configuration for the SEBE memory system.

All path constants and settings in one place. Paths resolve relative to the
automation_framework/ directory (two levels up from this file).
"""

from pathlib import Path

# Root of automation_framework/
FRAMEWORK_ROOT = Path(__file__).parent.parent.parent

# Human-readable memory files
MEMORY_DIR = FRAMEWORK_ROOT / "memory"
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
LOGS_DIR = MEMORY_DIR / "logs"

# SQLite database
DATA_DIR = FRAMEWORK_ROOT / "data"
DB_PATH = DATA_DIR / "memory.db"

# Context files
CONTEXT_DIR = FRAMEWORK_ROOT / "context"
PROJECT_CONTEXT = CONTEXT_DIR / "project_context.md"
AUTHOR_CONTEXT = CONTEXT_DIR / "author_context.md"
CONVO_SUMMARY = CONTEXT_DIR / "convo_summary.md"

# Valid entry types for memory_entries table
VALID_MEMORY_TYPES = ["fact", "preference", "event", "insight"]

# Valid task statuses
VALID_TASK_STATUSES = ["pending", "in_progress", "completed", "blocked", "cancelled"]

# Valid task priorities
VALID_TASK_PRIORITIES = ["low", "medium", "high", "critical"]

# Valid contact statuses
VALID_CONTACT_STATUSES = [
    "not_contacted", "contacted", "responded",
    "meeting_scheduled", "active", "dormant"
]

# Valid interaction channels
VALID_CHANNELS = ["email", "signal", "phone", "social", "in_person", "letter", "other"]

# Valid interaction directions
VALID_DIRECTIONS = ["inbound", "outbound"]

# Default number of days of logs to load at session start
DEFAULT_LOG_DAYS = 2

# Default minimum importance for DB entries loaded at session start
DEFAULT_MIN_IMPORTANCE = 5
