"""
DOCX to SEBE-format markdown converter for the SEBE automation framework.

Converts .docx files to clean markdown that pdf_writer.py can consume directly.
Uses pandoc for raw conversion, then runs a cleanup pipeline to produce markdown
matching the exact header format expected by pdf_writer.

This is a deterministic TOOL (no LLM reasoning). One job: DOCX → clean markdown.

Requires: pandoc (system binary)

Run from automation_framework/:
    python -m tools.docx_reader --file <docx_file> [options]

Actions:
    convert     Convert DOCX to SEBE-format markdown (default)
    info        Show detected metadata without converting

Examples:
    python -m tools.docx_reader --file document.docx
    python -m tools.docx_reader --file document.docx -o output.md
    python -m tools.docx_reader --file document.docx --action info
    python -m tools.docx_reader --file document.docx --raw
    python -m tools.docx_reader --file document.docx --author "A. Person" --version 1.0
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# ── Dependency checks ──────────────────────────────────────────────────


def check_dependencies() -> list[str]:
    """Check that pandoc is available."""
    missing = []
    if shutil.which("pandoc") is None:
        missing.append("pandoc")
    return missing


# ── Pandoc conversion ──────────────────────────────────────────────────


def pandoc_convert(file_path: Path, extract_media: bool = True) -> str:
    """Run pandoc to convert DOCX to raw markdown.

    Args:
        file_path: Path to the input .docx file
        extract_media: Whether to extract embedded images

    Returns:
        The raw markdown string from pandoc
    """
    cmd = [
        "pandoc",
        str(file_path),
        "-t",
        "gfm",  # GitHub Flavored Markdown (produces pipe tables)
        "--wrap=none",  # Don't wrap lines
    ]

    if extract_media:
        # Extract images to media/ directory next to the output
        media_dir = file_path.parent / "media"
        cmd.extend(["--extract-media", str(file_path.parent)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")


# ── Transform pipeline ─────────────────────────────────────────────────


def clean_escapes(text: str) -> str:
    r"""Fix pandoc escape artifacts: \' → ', \" → ", \| → |, \# → #, \[ → [, \] → ]"""
    text = text.replace("\\'", "'")
    text = text.replace('\\"', '"')
    # Only replace \| when NOT in a table context (not between pipes)
    # Simple heuristic: replace \| in prose, but tables usually have | on both sides
    # More robust: only fix \| that appears outside of pipe-delimited contexts
    text = re.sub(r"(?<!\|)\\\|(?!\|)", "|", text)
    text = text.replace("\\#", "#")
    text = text.replace("\\[", "[")
    text = text.replace("\\]", "]")
    return text


def normalise_rules(text: str) -> str:
    """Convert long dash sequences (72+ dashes or --------...) to ---"""
    # Match lines that are only dashes (8 or more)
    text = re.sub(r"^-{8,}$", "---", text, flags=re.MULTILINE)
    return text


def promote_bold_headers(text: str) -> str:
    """Convert standalone bold lines that look like section headers to ATX headers.

    Rules:
    - A line that is ONLY bold text (starts with ** and ends with **) AND
    - Is preceded by a blank line AND
    - Followed by blank line or content (not another bold line in sequence)
    - Contains patterns that indicate it's a header

    Heuristics for header level:
    - Numbered sections like "**1. Title**" → ## (H2)
    - Sub-sections like "**The Fix:**" or "**Why It Works:**" → ### (H3)
    - Major sections like "**The Solution: ...**" → ## (H2)
    - Lines with "Key Assumptions", "Key Insights", "Revenue Breakdown" etc → ### (H3)

    Be careful NOT to promote:
    - Bold text within paragraphs (mixed content)
    - Bold list items (lines starting with -)
    - Bold text that's part of a larger line
    """
    lines = text.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a standalone bold line
        stripped = line.strip()
        # Exclude bold+italic (***text***) - keep that as emphasis, not a header
        if (
            stripped.startswith("**")
            and stripped.endswith("**")
            and len(stripped) > 4
            and not (stripped.startswith("***") and stripped.endswith("***"))
        ):
            # Check it's not a list item
            if not re.match(r"^\s*[-*+]\s+\*\*", line):
                # Check it's preceded by blank line (or is first line)
                preceded_by_blank = i == 0 or not lines[i - 1].strip()

                # Check it's followed by blank or content (not consecutive bold lines)
                followed_ok = (
                    i == len(lines) - 1
                    or not lines[i + 1].strip()
                    or not (
                        lines[i + 1].strip().startswith("**")
                        and lines[i + 1].strip().endswith("**")
                    )
                )

                if preceded_by_blank and followed_ok:
                    # Extract the text without bold markers
                    header_text = stripped[2:-2].strip()

                    # Determine header level
                    # H2: Numbered sections, "The Solution:", major sections
                    # H3: "The Fix:", "Why It Works:", "Key X:", subsections
                    is_h2 = (
                        re.match(r"^\d+\.?\s+", header_text)  # "1. Title" or "1 Title"
                        or re.match(r"^The Solution:", header_text, re.IGNORECASE)
                        or re.match(r"^The Problem:", header_text, re.IGNORECASE)
                        or re.match(r"^The Challenge:", header_text, re.IGNORECASE)
                        or re.match(r"^Background:", header_text, re.IGNORECASE)
                        or re.match(r"^Introduction:", header_text, re.IGNORECASE)
                        or re.match(r"^Conclusion:", header_text, re.IGNORECASE)
                        or re.match(r"^Summary:", header_text, re.IGNORECASE)
                        or re.match(r"^Overview:", header_text, re.IGNORECASE)
                    )

                    is_h3 = re.search(
                        r"^(The Fix|Why It Works|Key Assumptions|Key Insights|"
                        r"Revenue Breakdown|Implementation|Timeline|Costs|"
                        r"Benefits|Risks|Challenges|Opportunities):",
                        header_text,
                        re.IGNORECASE,
                    )

                    if is_h2:
                        result.append(f"## {header_text}")
                    elif is_h3:
                        result.append(f"### {header_text}")
                    else:
                        # Default to H2 for other standalone bold lines
                        # that made it through the filters
                        result.append(f"## {header_text}")
                    i += 1
                    continue

        result.append(line)
        i += 1

    return "\n".join(result)


def extract_metadata(text: str) -> tuple[dict, str]:
    """Extract title, subtitle, author, date from the top of the document.

    Returns (metadata_dict, remaining_body_text).

    Detection heuristics:
    - Title: First bold-only line or first H1
    - Subtitle: First non-bold, non-empty line after title (if it's plain text, not a section)
    - Author: Look for "Contributors" or "Author" bold field, then extract the value
    - Date/Version: Look for standard bold field patterns

    The metadata dict has keys: title, subtitle, author, date, version (all optional except title)
    """
    meta = {}
    lines = text.split("\n")

    # Track where the body starts
    body_start_idx = 0
    title_found = False
    subtitle_found = False

    for i, line in enumerate(lines[:50]):  # Only check first 50 lines
        stripped = line.strip()

        # Skip blank lines
        if not stripped:
            continue

        # Title detection: First H1 or first bold-only line
        if not title_found:
            if stripped.startswith("# "):
                meta["title"] = stripped[2:].strip()
                title_found = True
                body_start_idx = i + 1
                continue
            elif (
                stripped.startswith("**")
                and stripped.endswith("**")
                and len(stripped) > 4
                and not stripped.startswith("**Author:")
                and not stripped.startswith("**Date:")
                and not stripped.startswith("**Contributors")
            ):
                # First bold line is title (but not a field label)
                meta["title"] = stripped[2:-2].strip()
                title_found = True
                body_start_idx = i + 1
                continue

        # Subtitle detection: After title, look for plain text line or H2
        if title_found and not subtitle_found:
            if stripped.startswith("## "):
                meta["subtitle"] = stripped[3:].strip()
                subtitle_found = True
                body_start_idx = i + 1
                continue
            elif (
                stripped
                and not stripped.startswith("**")
                and not stripped.startswith("-")
                and not stripped.startswith("*")  # Don't treat italic lines as subtitle
            ):
                # Plain text line after title (not starting with bold/italic/list)
                meta["subtitle"] = stripped
                subtitle_found = True
                body_start_idx = i + 1
                continue

        # Contributors/Author field: Look for "**Contributors**" or "**Author:**"
        if re.match(r"\*\*Contributors?\*\*", stripped, re.IGNORECASE):
            # Next non-blank line contains author names
            if ":" in stripped:
                # Same line: "**Contributors:** Name"
                author_text = stripped.split(":", 1)[1].strip()
                if author_text.startswith("*") and author_text.endswith("*"):
                    # Italic: "*Name | Name*"
                    meta["author"] = author_text[1:-1].strip()
                else:
                    meta["author"] = author_text
                body_start_idx = max(body_start_idx, i + 1)
            else:
                # Look for next non-blank line
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line:
                        if next_line.startswith("*") and next_line.endswith("*"):
                            # Italic author line
                            meta["author"] = next_line[1:-1].strip()
                        else:
                            meta["author"] = next_line
                        body_start_idx = max(body_start_idx, j + 1)
                        break
            continue

        # Standard bold field patterns: **Field:** value
        match = re.match(
            r"\*\*(Author|Date|Updated|Version|Status|Target):\*\*\s*(.+)",
            stripped,
            re.IGNORECASE,
        )
        if match:
            field_name = match.group(1).lower()
            field_value = match.group(2).strip()
            meta[field_name] = field_value
            body_start_idx = max(body_start_idx, i + 1)
            continue

        # If we hit the separator, stop looking for metadata
        if stripped == "---" or re.match(r"^-{8,}$", stripped):
            body_start_idx = i + 1
            break

    # Default title if none found
    if "title" not in meta:
        meta["title"] = "Untitled Document"

    # Body text starts after metadata
    body = "\n".join(lines[body_start_idx:])

    return meta, body


def format_sebe_header(meta: dict) -> str:
    """Format extracted metadata into the pdf_writer-compatible header block.

    Output format:
    # Title

    ## Subtitle (if present)

    **Author:** value
    **Date:** value (if present)
    **Version:** value (if present)

    ---
    """
    parts = []

    # Title (required)
    parts.append(f"# {meta.get('title', 'Untitled Document')}")
    parts.append("")

    # Subtitle (optional)
    if "subtitle" in meta:
        parts.append(f"## {meta['subtitle']}")
        parts.append("")

    # Metadata fields
    field_order = ["author", "date", "updated", "version", "status", "target"]
    for field in field_order:
        if field in meta:
            field_label = field.capitalize()
            parts.append(f"**{field_label}:** {meta[field]}")

    # Separator
    if any(field in meta for field in field_order):
        parts.append("")
    parts.append("---")

    return "\n".join(parts)


def collapse_blanks(text: str) -> str:
    """Reduce consecutive blank lines to maximum 2."""
    # Replace 3 or more consecutive newlines with exactly 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def clean_grid_tables(text: str) -> str:
    """Convert pandoc grid tables (+---+---+) to pipe tables if needed.

    Since we're using gfm output format, pandoc should already produce pipe tables.
    This is a safety check in case any grid tables slip through.
    """
    # Grid tables start with +---+ patterns
    # If we find any, warn that they need manual conversion
    if re.search(r"^\+[-+]+\+", text, re.MULTILINE):
        print(
            "WARNING: Grid tables detected. May need manual conversion.",
            file=sys.stderr,
        )
    return text


def reassemble(header: str, body: str) -> str:
    """Join header block and body with proper spacing."""
    # Ensure exactly one blank line after the header separator
    body = body.lstrip("\n")
    return f"{header}\n\n{body}"


def convert_docx_to_markdown(
    file_path: Path,
    author_override: str | None = None,
    date_override: str | None = None,
    version_override: str | None = None,
) -> str:
    """Full conversion pipeline: DOCX → clean SEBE-format markdown.

    Args:
        file_path: Path to input .docx file
        author_override: Override detected author
        date_override: Override detected date
        version_override: Override/set version

    Returns:
        Clean markdown string ready for pdf_writer.py
    """
    # Step 1: Pandoc conversion
    raw_md = pandoc_convert(file_path, extract_media=True)

    # Step 2: Clean escapes and rules first
    cleaned = clean_escapes(raw_md)
    cleaned = normalise_rules(cleaned)

    # Step 3: Extract metadata BEFORE promoting headers
    # (metadata detection works on bold lines)
    meta, body = extract_metadata(cleaned)

    # Step 4: Apply overrides
    if author_override:
        meta["author"] = author_override
    if date_override:
        meta["date"] = date_override
    if version_override:
        meta["version"] = version_override

    # Step 5: NOW promote bold headers in the body
    body = promote_bold_headers(body)

    # Step 6: Format header
    header = format_sebe_header(meta)

    # Step 7: Clean body
    body = collapse_blanks(body)
    body = clean_grid_tables(body)

    # Step 8: Reassemble
    final_md = reassemble(header, body)

    return final_md


# ── Actions ────────────────────────────────────────────────────────────


def action_convert(
    file_path: str,
    output_path: str | None = None,
    author: str | None = None,
    date: str | None = None,
    version: str | None = None,
    raw: bool = False,
) -> dict:
    """Convert DOCX to SEBE-format markdown.

    Args:
        file_path: Input .docx file path
        output_path: Output .md file path (default: same name with .md)
        author: Override detected author
        date: Override detected date
        version: Set version string
        raw: If True, return markdown only (don't write file)

    Returns:
        Dict with success status, output path, and metadata
    """
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if not path.suffix.lower() == ".docx":
        return {"success": False, "error": f"Not a .docx file: {file_path}"}

    try:
        markdown = convert_docx_to_markdown(
            path,
            author_override=author,
            date_override=date,
            version_override=version,
        )

        if raw:
            return {
                "success": True,
                "markdown": markdown,
            }

        # Write to file
        out_path = Path(output_path) if output_path else path.with_suffix(".md")
        out_path.write_text(markdown, encoding="utf-8")

        return {
            "success": True,
            "input": str(path),
            "output": str(out_path),
            "size": len(markdown),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def action_info(file_path: str) -> dict:
    """Show detected metadata without converting.

    Args:
        file_path: Input .docx file path

    Returns:
        Dict with success status and detected metadata
    """
    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if not path.suffix.lower() == ".docx":
        return {"success": False, "error": f"Not a .docx file: {file_path}"}

    try:
        # Run through conversion pipeline but don't write output
        raw_md = pandoc_convert(path, extract_media=False)
        cleaned = clean_escapes(raw_md)
        cleaned = normalise_rules(cleaned)

        # Extract metadata BEFORE promoting headers
        meta, _ = extract_metadata(cleaned)

        return {
            "success": True,
            "file": str(path),
            "metadata": meta,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ── CLI ────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="DOCX to SEBE-format markdown converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  convert     Convert DOCX to SEBE-format markdown (default)
  info        Show detected metadata without converting

Examples:
  python -m tools.docx_reader --file document.docx
  python -m tools.docx_reader --file document.docx -o output.md
  python -m tools.docx_reader --file document.docx --action info
  python -m tools.docx_reader --file document.docx --raw
  python -m tools.docx_reader --file document.docx --author "A. Person" --version 1.0
        """,
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Input DOCX file path",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output markdown path (default: same name with .md)",
    )
    parser.add_argument(
        "--action",
        default="convert",
        choices=["convert", "info"],
        help="Operation to perform (default: convert)",
    )
    parser.add_argument(
        "--author",
        help="Override detected author",
    )
    parser.add_argument(
        "--date",
        help="Override detected date",
    )
    parser.add_argument(
        "--version",
        help="Set version string",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Output markdown to stdout only (don't write file)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args()

    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print("Install with: sudo apt install pandoc", file=sys.stderr)
        sys.exit(1)

    try:
        if args.action == "convert":
            result = action_convert(
                args.file,
                output_path=args.output,
                author=args.author,
                date=args.date,
                version=args.version,
                raw=args.raw,
            )

            if args.raw and result.get("success"):
                # Output just the markdown
                print(result["markdown"])
            elif args.json or not args.raw:
                status = "OK" if result.get("success") else "ERROR"
                print(f"{status}", file=sys.stderr)
                print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.action == "info":
            result = action_info(args.file)
            status = "OK" if result.get("success") else "ERROR"
            print(f"{status}", file=sys.stderr)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}
            print("ERROR", file=sys.stderr)
            print(json.dumps(result, indent=2))
            sys.exit(1)

        if not result.get("success"):
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
