"""
SEBE Memory Writer — Append to daily logs and write to DB.

Dual-write by default: entries go to both the daily markdown log
and the SQLite database.

Usage (CLI):
    python -m tools.memory.writer --content "Emailed IPPR with academic brief" --type event
    python -m tools.memory.writer --content "Jason prefers ULI not UBI" --type preference --importance 8
    python -m tools.memory.writer --content "Quick note" --log-only
    python -m tools.memory.writer --content "Structured fact" --db-only
    python -m tools.memory.writer --update-memory --section key_facts --content "New persistent fact"
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import MEMORY_FILE, MEMORY_DIR, LOGS_DIR, VALID_MEMORY_TYPES
from .db import add_memory


def _ensure_dirs() -> None:
    """Create memory directories if they don't exist."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _today_log_path() -> Path:
    """Path to today's daily log file."""
    return LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"


def append_to_daily_log(
    content: str,
    entry_type: str = "note",
    timestamp: bool = True,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Append an entry to today's daily log file."""
    _ensure_dirs()
    log_path = _today_log_path()
    today = datetime.now().strftime("%Y-%m-%d")

    if not log_path.exists():
        header = (
            f"# Session Log: {today}\n\n"
            f"> {datetime.now().strftime('%A, %B %d, %Y')}\n\n"
            f"---\n\n"
        )
        log_path.write_text(header, encoding="utf-8")

    time_str = datetime.now().strftime("%H:%M") if timestamp else ""
    type_tag = f"[{entry_type}] " if entry_type != "note" else ""
    cat_tag = f" #{category}" if category else ""

    line = f"- {time_str} {type_tag}{content}{cat_tag}\n" if timestamp else f"- {type_tag}{content}{cat_tag}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)

    return {
        "success": True,
        "path": str(log_path),
        "date": today,
        "entry": line.strip(),
        "message": f"Logged to {today}",
    }


def write_to_memory(
    content: str,
    entry_type: str = "fact",
    importance: int = 5,
    tags: Optional[List[str]] = None,
    context: Optional[str] = None,
    log_to_file: bool = True,
    add_to_db: bool = True,
) -> Dict[str, Any]:
    """
    Dual-write: append to daily log AND add to SQLite.

    Use log_to_file=False for DB-only, add_to_db=False for log-only.
    """
    results: Dict[str, Any] = {"success": True, "log_result": None, "db_result": None}

    if log_to_file:
        log_result = append_to_daily_log(
            content=content,
            entry_type=entry_type,
            category=tags[0] if tags else None,
        )
        results["log_result"] = log_result
        if not log_result.get("success"):
            results["success"] = False

    if add_to_db and entry_type in VALID_MEMORY_TYPES:
        db_result = add_memory(
            content=content,
            entry_type=entry_type,
            importance=importance,
            tags=tags,
            context=context,
        )
        results["db_result"] = db_result
        # Don't fail on duplicate — that's expected
        if not db_result.get("success") and "Duplicate" not in db_result.get("error", ""):
            results["success"] = False

    return results


def append_to_memory_file(content: str, section: str = "key_facts") -> Dict[str, Any]:
    """
    Append a line to a section in MEMORY.md.

    Use for truly persistent facts that should always be loaded at session start.
    """
    if not MEMORY_FILE.exists():
        return {"success": False, "error": "MEMORY.md does not exist"}

    full_content = MEMORY_FILE.read_text(encoding="utf-8")
    section_header = f"## {section.replace('_', ' ').title()}"
    lines = full_content.split("\n")
    new_lines = []
    found_section = False
    inserted = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        if line.strip().lower() == section_header.lower():
            found_section = True
            continue

        if found_section and not inserted:
            # Insert before next section, horizontal rule, or end of file
            if line.startswith("## ") or line.strip() == "---":
                new_lines.insert(-1, f"- {content}")
                inserted = True

    if found_section and not inserted:
        new_lines.append(f"- {content}")
        inserted = True

    if not found_section:
        return {"success": False, "error": f"Section '{section}' not found in MEMORY.md"}

    # Update last-modified line if present
    for i, line in enumerate(new_lines):
        if line.startswith("*Last updated:"):
            new_lines[i] = f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*"
            break

    MEMORY_FILE.write_text("\n".join(new_lines), encoding="utf-8")
    return {
        "success": True,
        "section": section,
        "content": content,
        "message": f"Appended to {section} in MEMORY.md",
    }


def main():
    parser = argparse.ArgumentParser(description="SEBE Memory Writer")
    parser.add_argument("--content", required=True, help="Content to write")
    parser.add_argument("--type", default="fact",
                        choices=VALID_MEMORY_TYPES + ["note"],
                        help="Entry type")
    parser.add_argument("--importance", type=int, default=5, help="Importance 1-10")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--context", help="Context note")
    parser.add_argument("--log-only", action="store_true", help="Only write to daily log")
    parser.add_argument("--db-only", action="store_true", help="Only write to SQLite")
    parser.add_argument("--update-memory", action="store_true", help="Append to MEMORY.md")
    parser.add_argument("--section", default="key_facts", help="MEMORY.md section")

    args = parser.parse_args()
    tags = args.tags.split(",") if args.tags else None

    if args.update_memory:
        result = append_to_memory_file(args.content, args.section)
    elif args.type == "note":
        result = append_to_daily_log(content=args.content, entry_type="note",
                                      category=tags[0] if tags else None)
    else:
        result = write_to_memory(
            content=args.content,
            entry_type=args.type,
            importance=args.importance,
            tags=tags,
            context=args.context,
            log_to_file=not args.db_only,
            add_to_db=not args.log_only,
        )

    if result.get("success"):
        print(f"OK {result.get('message', 'Written')}")
    else:
        print(f"ERROR {result.get('error')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
