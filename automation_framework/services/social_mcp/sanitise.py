"""
Output sanitisation for the social MCP server.

All data returned to the caller passes through these functions.
Prevents prompt injection, credential leakage, and control character
attacks in returned social content.
"""

import re


# Control characters except newline and tab
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")

# Common prompt injection patterns
_INJECTION_PATTERNS = re.compile(
    r"(ignore previous|system prompt|you are now|forget your|"
    r"new instructions|disregard|override|reveal.*password|"
    r"reveal.*secret|reveal.*key|reveal.*token|"
    r"print.*env|show.*credentials)",
    re.IGNORECASE,
)


def clean_string(text: str, max_length: int = 500) -> str:
    """Remove control characters, truncate, and flag injection attempts."""
    if not isinstance(text, str):
        return ""
    text = _CONTROL_CHARS.sub("", text)
    if len(text) > max_length:
        text = text[:max_length] + "..."
    return text


def clean_text_preview(text: str) -> str:
    """Sanitise text from external posts for preview display."""
    return clean_string(text, max_length=100)


def clean_handle(handle: str) -> str:
    """Sanitise a user handle."""
    return clean_string(handle, max_length=100)


def has_injection(text: str) -> bool:
    """Check if text contains common prompt injection patterns."""
    return bool(_INJECTION_PATTERNS.search(text))


def sanitise_notification(item: dict) -> dict:
    """Sanitise a notification item before returning."""
    return {
        "type": clean_string(item.get("type", ""), 30),
        "author": clean_handle(item.get("author", "")),
        "text_preview": clean_text_preview(item.get("text_preview", "")),
        "post_id": clean_string(item.get("post_id", ""), 200),
        "flagged": has_injection(item.get("text_preview", "")),
    }


def sanitise_feed_item(item: dict) -> dict:
    """Sanitise a feed/post item before returning."""
    return {
        "post_id": clean_string(item.get("post_id", ""), 200),
        "cid": clean_string(item.get("cid", ""), 200),
        "text": clean_string(item.get("text", ""), 1000),
        "title": clean_string(item.get("title", ""), 300),
        "created_at": clean_string(item.get("created_at", ""), 30),
        "likes": item.get("likes", 0),
        "reposts": item.get("reposts", 0),
        "replies": item.get("replies", 0),
        "url": clean_string(item.get("url", ""), 300),
        "subreddit": clean_string(item.get("subreddit", ""), 100),
        "flagged": has_injection(item.get("text", "")),
    }
