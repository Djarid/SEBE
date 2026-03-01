"""
Response validation for the social MCP server.

Validates adapter responses against per-command schemas before they
reach the caller. Items that fail validation are dropped (not the
entire response). This prevents malformed API data from propagating
and makes fabrication structurally detectable.

All validation is deterministic. No LLM involvement.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Platform-specific patterns for structural validation
# ---------------------------------------------------------------------------

# Valid post_id patterns per platform
_POST_ID_PATTERNS: dict[str, re.Pattern] = {
    "bsky": re.compile(r"^at://did:plc:[a-z0-9]+/app\.bsky\.\w+\.\w+/[a-z0-9]+$"),
    "mastodon": re.compile(r"^\d+$"),
    "reddit": re.compile(r"^t[13]_[a-z0-9]+$"),
}

# Valid URL patterns per platform
_URL_PATTERNS: dict[str, re.Pattern] = {
    "bsky": re.compile(r"^https://bsky\.app/profile/[^/]+/post/[a-z0-9]+$"),
    "mastodon": re.compile(r"^https?://"),  # Instance domain varies
    "reddit": re.compile(r"^https?://(www\.)?reddit\.com/"),
}


# ---------------------------------------------------------------------------
# Field validators
# ---------------------------------------------------------------------------


def _is_non_empty_str(val: Any) -> bool:
    return isinstance(val, str) and len(val.strip()) > 0


def _is_non_negative_int(val: Any) -> bool:
    return isinstance(val, int) and val >= 0


def _valid_post_id(val: Any, platform: str) -> bool:
    """Check post_id matches expected pattern for the platform."""
    if not _is_non_empty_str(val):
        return False
    pattern = _POST_ID_PATTERNS.get(platform)
    if pattern is None:
        return True  # Unknown platform, skip pattern check
    return bool(pattern.match(val))


def _valid_url(val: Any, platform: str) -> bool:
    """Check URL matches expected pattern for the platform."""
    if not isinstance(val, str) or not val:
        return False
    pattern = _URL_PATTERNS.get(platform)
    if pattern is None:
        return True
    return bool(pattern.match(val))


# ---------------------------------------------------------------------------
# Per-command validators
# ---------------------------------------------------------------------------


def validate_notification(item: dict, platform: str) -> bool:
    """Validate a single notification item."""
    if not isinstance(item, dict):
        return False
    if not _is_non_empty_str(item.get("type")):
        return False
    if not _is_non_empty_str(item.get("author")):
        return False
    # post_id can be empty for follow notifications
    return True


def validate_feed_item(item: dict, platform: str) -> bool:
    """Validate a single feed/post item."""
    if not isinstance(item, dict):
        return False
    if not _valid_post_id(item.get("post_id"), platform):
        return False
    # At least text or title must be present
    if not _is_non_empty_str(item.get("text")) and not _is_non_empty_str(
        item.get("title")
    ):
        return False
    if not _is_non_empty_str(item.get("created_at")):
        return False
    return True


def validate_profile(data: dict, platform: str) -> bool:
    """Validate a profile response."""
    if not isinstance(data, dict):
        return False
    if not _is_non_empty_str(data.get("handle")):
        return False
    return True


def validate_post_result(data: dict, platform: str) -> bool:
    """Validate a post creation result."""
    if not isinstance(data, dict):
        return False
    if not data.get("success"):
        return True  # Error responses are valid
    if not _is_non_empty_str(data.get("post_id")):
        return False
    return True


def validate_metrics(data: dict, platform: str) -> bool:
    """Validate post metrics."""
    if not isinstance(data, dict):
        return False
    if not data.get("success"):
        return True  # Error responses are valid
    for field in ("likes", "reposts", "replies"):
        if not _is_non_negative_int(data.get(field, -1)):
            return False
    return True


# ---------------------------------------------------------------------------
# List filtering
# ---------------------------------------------------------------------------


def filter_items(
    items: list[dict],
    validator: Callable[[dict, str], bool],
    platform: str,
    command: str,
) -> tuple[list[dict], int]:
    """
    Filter a list of items through a validator.

    Returns (valid_items, dropped_count).
    """
    valid = []
    dropped = 0
    for item in items:
        if validator(item, platform):
            valid.append(item)
        else:
            dropped += 1
            logger.warning(
                "Dropped invalid %s item from %s: %s",
                command,
                platform,
                _safe_preview(item),
            )
    return valid, dropped


def _safe_preview(item: Any) -> str:
    """Safe preview of an item for logging (no credentials, truncated)."""
    if isinstance(item, dict):
        preview = {k: str(v)[:50] for k, v in list(item.items())[:5]}
        return str(preview)
    return str(item)[:100]
