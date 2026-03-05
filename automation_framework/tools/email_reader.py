"""
SEBE Email Reader — Read sent and received email from Proton Bridge.

Standalone CLI tool that connects to Proton Bridge IMAP and displays
messages from a configurable date range. Read-only: does not mark
messages as seen or modify any flags.

Usage (from automation_framework/):
    python -m tools.email_reader                  # Last 2 days
    python -m tools.email_reader --days 4         # Last 4 days
    python -m tools.email_reader --sent-only      # Sent only
    python -m tools.email_reader --received-only  # Received only
    python -m tools.email_reader --skip-system    # Hide system emails
    python -m tools.email_reader --json           # JSON output
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from email.header import decode_header as _decode_header
from html import unescape
from html.parser import HTMLParser

from services.config import DaemonConfig
from services.channels.email_channel import EmailChannel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _HTMLStripper(HTMLParser):
    """Minimal HTML-to-text converter using stdlib."""

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        # Skip content inside <style> and <script> tags
        if tag in ("style", "script"):
            self._skip = True
        # Insert a newline for block-level elements
        if tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts)


def strip_html(text: str) -> str:
    """Strip HTML tags, decode entities, return plain text."""
    stripper = _HTMLStripper()
    stripper.feed(unescape(text))
    return stripper.get_text()


def decode_subject(raw: str) -> str:
    """Decode MIME-encoded subject headers into readable text."""
    if not raw:
        return "(no subject)"
    parts = []
    for fragment, charset in _decode_header(raw):
        if isinstance(fragment, bytes):
            parts.append(fragment.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(fragment)
    return " ".join(parts)


def collapse_whitespace(text: str) -> str:
    """Collapse runs of blank lines to a single blank line and strip edges."""
    # Strip lines that are only whitespace
    text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


SYSTEM_SENDERS = frozenset(
    {
        "no-reply@",
        "noreply@",
        "mailer-daemon@",
        "postmaster@",
        "notify.proton",
        "proton.me",
    }
)


def is_system_message(sender: str) -> bool:
    """Return True if the sender looks like a system/automated address."""
    sender_lower = sender.lower()
    return any(token in sender_lower for token in SYSTEM_SENDERS)


def clean_body(raw_body: str) -> str:
    """Strip HTML, truncate quoted replies, and collapse whitespace."""
    if not raw_body:
        return "(empty)"
    # If the body looks like HTML, strip tags
    if "<" in raw_body and (
        "</div>" in raw_body or "</p>" in raw_body or "</html>" in raw_body
    ):
        text = strip_html(raw_body)
    else:
        text = raw_body
    # Truncate at quoted reply markers
    for marker in ("\n-------- Original Message --------", "\nOn ", "\n> "):
        idx = text.find(marker)
        if idx > 0 and marker == "\nOn ":
            # Only truncate "On " if it looks like a reply header (contains "wrote:")
            rest = text[idx : idx + 200]
            if "wrote:" not in rest:
                continue
        if idx > 0:
            text = text[:idx] + "\n\n[... quoted reply trimmed ...]"
            break
    return collapse_whitespace(text)


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def format_message_markdown(msg, direction: str) -> str:
    """Format a single message as readable markdown for terminal output."""
    parts = []
    timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M") if msg.timestamp else "unknown"
    subject = decode_subject(msg.subject)

    if direction == "received":
        parts.append(f"### {timestamp} — From: {msg.sender}")
    else:
        to_addr = msg.raw.get("to", "unknown") if msg.raw else "unknown"
        parts.append(f"### {timestamp} — To: {to_addr}")

    parts.append(f"**Subject:** {subject}")
    parts.append("")

    body = clean_body(msg.body)
    # Truncate very long bodies for readability
    if len(body) > 2000:
        body = body[:2000] + "\n\n[... truncated ...]"
    parts.append(body)
    parts.append("")
    parts.append("---")
    parts.append("")

    return "\n".join(parts)


def format_message_dict(msg, direction: str) -> dict:
    """Format a single message as a dict for JSON output."""
    return {
        "direction": direction,
        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
        "sender": msg.sender,
        "to": msg.raw.get("to", "") if msg.raw else "",
        "subject": decode_subject(msg.subject),
        "body": clean_body(msg.body),
        "message_id": msg.message_id,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="SEBE Email Reader — Read sent/received email from Proton Bridge"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=2,
        help="Number of days to look back (default: 2)",
    )
    parser.add_argument(
        "--sent-only",
        action="store_true",
        help="Only show sent messages",
    )
    parser.add_argument(
        "--received-only",
        action="store_true",
        help="Only show received messages",
    )
    parser.add_argument(
        "--skip-system",
        action="store_true",
        help="Hide system/automated emails (Proton, MAILER-DAEMON, etc.)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of markdown",
    )

    args = parser.parse_args()

    # Load config from .env
    cfg = DaemonConfig.from_env()

    if not cfg.email.username or not cfg.email.password:
        print(
            "Error: PROTON_USERNAME and PROTON_BRIDGE_PASSWORD must be set in .env",
            file=sys.stderr,
        )
        sys.exit(1)

    # Instantiate channel
    channel = EmailChannel(cfg.email)

    # Check connection
    if not channel.is_available():
        print(
            "Error: Cannot connect to Proton Bridge IMAP. Is it running?",
            file=sys.stderr,
        )
        sys.exit(1)

    since_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    received = []
    sent = []

    if not args.sent_only:
        received = channel.search_by_date("INBOX", since_date)

    if not args.received_only:
        sent = channel.search_by_date("Sent", since_date)

    # Filter system messages if requested
    if args.skip_system:
        received = [m for m in received if not is_system_message(m.sender)]
        sent = [m for m in sent if not is_system_message(m.sender)]

    if args.json:
        output = {
            "since": since_date,
            "received": [format_message_dict(m, "received") for m in received],
            "sent": [format_message_dict(m, "sent") for m in sent],
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        if not received and not sent:
            print(f"No messages found since {since_date}.")
            return

        if received:
            print(f"## Received ({len(received)} messages)\n")
            for msg in received:
                print(format_message_markdown(msg, "received"))

        if sent:
            print(f"## Sent ({len(sent)} messages)\n")
            for msg in sent:
                print(format_message_markdown(msg, "sent"))


if __name__ == "__main__":
    main()
