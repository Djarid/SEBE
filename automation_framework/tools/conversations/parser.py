"""
Platform-specific chat parsers.

Each parser takes raw text and returns a list of ParsedMessage dataclass instances.
Parsers are pure functions with no database or IO dependencies.

Supported formats:
    - WhatsApp (.txt export format)
    - Discord (copy-paste from channel/thread)
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ParsedMessage:
    """A single parsed message from a chat export."""

    timestamp: datetime
    sender_raw: str  # Phone number or display name exactly as exported
    content: str  # Full message text (may be multi-line)
    is_system: bool  # True for join/leave/deleted notifications
    line_number: int  # Line number in source file (1-indexed, for traceability)


# Registry of parsers by platform name
PARSERS = {}


def register_parser(platform: str):
    """Decorator to register a parser function."""

    def decorator(func):
        PARSERS[platform] = func
        return func

    return decorator


def parse(platform: str, text: str) -> List[ParsedMessage]:
    """Parse chat text using the appropriate platform parser."""
    if platform not in PARSERS:
        raise ValueError(
            f"No parser for platform '{platform}'. Available: {list(PARSERS.keys())}"
        )
    return PARSERS[platform](text)


@register_parser("whatsapp")
def parse_whatsapp(text: str) -> List[ParsedMessage]:
    """
    Parse WhatsApp chat export format.

    Format: [HH:MM, DD/MM/YYYY] sender: message text

    Multi-line messages and continuations are handled by collecting lines
    that don't match the timestamp pattern into the previous message.

    System messages (e.g., "This message was deleted", "<Media omitted>")
    are marked with is_system=True.
    """
    # Regex pattern for timestamped lines: [HH:MM, DD/MM/YYYY] sender: content
    timestamp_pattern = re.compile(
        r"^\[(\d{2}:\d{2}),\s(\d{2}/\d{2}/\d{4})\]\s(.+?):\s(.*)$"
    )

    # System message patterns
    system_patterns = [
        r"This message was deleted",
        r"<Media omitted>",
        r".+ joined using this group\'s invite link",
        r".+ left",
        r".+ was added",
        r".+ was removed",
        r"You were added",
        r"Messages and calls are end-to-end encrypted",
    ]
    system_regex = re.compile(
        "|".join(f"({p})" for p in system_patterns), re.IGNORECASE
    )

    lines = text.split("\n")
    messages = []
    current_message = None
    first_timestamp = None
    preamble_lines = []
    preamble_start_line = None

    for line_num, line in enumerate(lines, start=1):
        line = line.rstrip()

        # Try to match timestamp pattern
        match = timestamp_pattern.match(line)

        if match:
            # Save previous message if exists
            if current_message:
                messages.append(current_message)

            # Parse timestamp
            time_str, date_str, sender, content = match.groups()
            dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")

            # Remember first timestamp for preamble
            if first_timestamp is None:
                first_timestamp = dt

                # If we collected preamble lines, create a message for them
                if preamble_lines:
                    preamble_content = "\n".join(preamble_lines)
                    is_sys = bool(system_regex.search(preamble_content))
                    preamble_msg = ParsedMessage(
                        timestamp=first_timestamp.replace(hour=0, minute=0),
                        sender_raw="Unknown",
                        content=preamble_content,
                        is_system=is_sys,
                        line_number=preamble_start_line,
                    )
                    messages.append(preamble_msg)
                    preamble_lines = []

            # Check if this is a system message
            is_sys = bool(system_regex.search(content))

            # Create new message
            current_message = ParsedMessage(
                timestamp=dt,
                sender_raw=sender,
                content=content,
                is_system=is_sys,
                line_number=line_num,
            )
        else:
            # This is either a preamble line or a continuation line
            if first_timestamp is None:
                # We're still in preamble (before first timestamped message)
                if line.strip():  # Only collect non-empty lines
                    if preamble_start_line is None:
                        preamble_start_line = line_num
                    preamble_lines.append(line)
            else:
                # This is a continuation of the current message
                if current_message and line.strip():
                    # Append to current message content
                    current_message.content += "\n" + line
                    # Update system status if line contains system message
                    if system_regex.search(line):
                        current_message.is_system = True

    # Don't forget the last message
    if current_message:
        messages.append(current_message)

    return messages


# ── Discord copy-paste parser ─────────────────────────────────────────


# Timestamp pattern for Discord copy-paste: M/DD/YY, H:MM AM/PM
# Matches: 2/25/26, 10:33 AM | 3/10/26, 3:19 PM | 12/1/26, 12:00 AM
_DISCORD_TS_RE = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s[AP]M)$")

# The em-dash separator line between sender and timestamp.
# Discord uses U+2014 (—) but copy-paste may also produce -- or spaced variants.
_DISCORD_SEP_RE = re.compile(r"^\s*[—–\-]{1,3}\s*$")

# Discord system/attachment markers
_DISCORD_SYSTEM_PATTERNS = [
    r"^Image$",
    r"^Video$",
    r"^File$",
    r"^GIF$",
    r"pinned\s+a\s+message",
    r"started\s+a\s+thread",
    r"joined\s+the\s+server",
]
_DISCORD_SYSTEM_RE = re.compile(
    "|".join(f"({p})" for p in _DISCORD_SYSTEM_PATTERNS), re.IGNORECASE
)


def _parse_discord_timestamp(date_str: str, time_str: str) -> datetime:
    """Parse Discord US-format timestamp into a datetime.

    Handles both 2-digit and 4-digit year formats.
    """
    # Normalise year: 26 -> 2026, 2026 -> 2026
    parts = date_str.split("/")
    if len(parts[2]) == 2:
        parts[2] = "20" + parts[2]
    date_normalised = "/".join(parts)
    return datetime.strptime(f"{date_normalised} {time_str}", "%m/%d/%Y %I:%M %p")


def _clean_discord_sender(raw: str) -> str:
    """Clean up Discord display name artifacts.

    Strips trailing commas and excess whitespace that appear in
    copy-pasted Discord display names (e.g. 'Jason Huxley [AZRN],').
    """
    cleaned = raw.strip().rstrip(",").strip()
    return cleaned


@register_parser("discord")
def parse_discord(text: str) -> List[ParsedMessage]:
    """
    Parse Discord copy-paste text format.

    Discord copy-paste produces a repeating 3-line message header:

        SenderName
         —
        M/DD/YY, H:MM AM/PM

    followed by message body lines until the next header.

    The em-dash separator line ( — ) is the reliable anchor for detecting
    message boundaries. The line before it is the sender, the line after
    is the timestamp.

    Preamble text before the first message (e.g. channel/thread title)
    is captured as a system message.
    """
    lines = text.split("\n")
    n = len(lines)
    messages: List[ParsedMessage] = []

    # Phase 1: Find all message boundaries.
    # A boundary is a triplet: (sender_line, sep_line, timestamp_line)
    # where sep_line matches _DISCORD_SEP_RE and timestamp_line matches
    # _DISCORD_TS_RE.
    boundaries: list[tuple[int, str, datetime]] = []  # (line_idx, sender, dt)

    i = 0
    while i < n:
        line = lines[i].rstrip()

        # Check if this line is an em-dash separator
        if _DISCORD_SEP_RE.match(line) and i > 0 and i + 1 < n:
            # Line before should be the sender (non-empty)
            sender_line = lines[i - 1].rstrip()
            # Line after should be the timestamp
            ts_line = lines[i + 1].rstrip()
            ts_match = _DISCORD_TS_RE.match(ts_line)

            if sender_line.strip() and ts_match:
                date_str, time_str = ts_match.groups()
                try:
                    dt = _parse_discord_timestamp(date_str, time_str)
                    sender = _clean_discord_sender(sender_line)
                    # i-1 is sender, i is sep, i+1 is timestamp
                    # Content starts at i+2
                    boundaries.append((i - 1, sender, dt))
                    i += 2  # Skip past timestamp line
                    continue
                except ValueError:
                    pass  # Not a valid timestamp, continue scanning

        i += 1

    if not boundaries:
        raise ValueError(
            "No Discord messages found. Expected format: "
            "SenderName / — / M/DD/YY, H:MM AM/PM"
        )

    # Phase 2: Extract message content between boundaries.
    # For boundary k, content runs from (boundary_k timestamp_line + 1)
    # to (boundary_{k+1} sender_line - 1).

    for k, (sender_idx, sender, dt) in enumerate(boundaries):
        # Content starts 2 lines after sender (sender, sep, ts, then content)
        content_start = sender_idx + 3

        # Content ends at the line before the next boundary's sender line,
        # or at end of file for the last message.
        if k + 1 < len(boundaries):
            content_end = boundaries[k + 1][0]  # Next sender_idx
        else:
            content_end = n

        # Collect content lines, preserving internal blank lines
        content_lines = []
        for j in range(content_start, content_end):
            content_lines.append(lines[j].rstrip())

        # Strip leading and trailing blank lines from content
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()

        content = "\n".join(content_lines)

        # Detect system messages (attachment markers, etc.)
        is_system = (
            bool(_DISCORD_SYSTEM_RE.match(content.strip())) or not content.strip()
        )

        # Skip truly empty messages (e.g. "." placeholder)
        if not content.strip() or content.strip() == ".":
            is_system = True

        messages.append(
            ParsedMessage(
                timestamp=dt,
                sender_raw=sender,
                content=content if content.strip() else "[empty]",
                is_system=is_system,
                line_number=sender_idx + 1,  # 1-indexed
            )
        )

    # Phase 3: Capture preamble (text before first message) as system message.
    if boundaries:
        first_sender_idx = boundaries[0][0]
        preamble_lines = []
        for j in range(0, first_sender_idx):
            line = lines[j].rstrip()
            if line.strip():
                preamble_lines.append(line)

        if preamble_lines:
            preamble_content = "\n".join(preamble_lines)
            messages.insert(
                0,
                ParsedMessage(
                    timestamp=boundaries[0][2],
                    sender_raw="__preamble__",
                    content=preamble_content,
                    is_system=True,
                    line_number=1,
                ),
            )

    return messages
