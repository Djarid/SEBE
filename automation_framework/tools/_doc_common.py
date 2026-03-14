"""
Shared document preprocessing for PDF and DOCX generation tools.

Contains metadata extraction, header stripping, content cleanup, and
utility functions used by both pdf_writer.py and docx_writer.py.

This module owns no CLI and no output format logic. It is a pure
preprocessing library. Format-specific logic (LaTeX preamble, pandoc
invocation, reference templates) belongs in the format-specific writer.
"""

import re


# Fields to extract from bold **Field: value** lines in the header area.
_HEADER_FIELDS = (
    "Author",
    "Date",
    "Updated",
    "Prepared",
    "Version",
    "Status",
    "Target",
    "Reference",
    "Methodology",
)


# --- Metadata extraction ---


def extract_metadata(text: str) -> dict:
    """Extract metadata from markdown header area.

    Handles multiple header patterns found across the SEBE repo:
      # Title / ## Subtitle / **Field: value** lines / BRIEFING NOTES

    Searches the first 800 characters to accommodate longer headers
    (e.g. documents with Status, Target, Reference, Methodology fields).
    """
    meta: dict[str, str] = {}
    header_text = text[:800]

    # H1 title
    m = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        meta["title"] = m.group(1).strip()

    # H2 subtitle: must appear BEFORE the first --- separator to be
    # considered a subtitle rather than a section heading. Documents
    # like glossary.md have their first H2 after the separator.
    separator_pos = header_text.find("\n---")
    subtitle_area = header_text[:separator_pos] if separator_pos > 0 else header_text
    m = re.search(r"^##\s+(.+)$", subtitle_area, re.MULTILINE)
    if m:
        meta["subtitle"] = m.group(1).strip()

    # Bold field extraction (generalised across all known header fields)
    for field in _HEADER_FIELDS:
        m = re.search(rf"\*\*{field}:\s*(.+?)\*\*", header_text)
        if m:
            meta[field.lower()] = m.group(1).strip()

    # BRIEFING NOTES as date (specific to nhs_palantir style)
    if "date" not in meta and "updated" not in meta:
        m = re.search(r"\*\*(BRIEFING NOTES[^*]*)\*\*", header_text, re.IGNORECASE)
        if m:
            meta["date"] = m.group(1).strip()

    # Merge alternative date fields into canonical "date" key
    if "date" not in meta:
        meta["date"] = meta.get("updated", meta.get("prepared", ""))

    return meta


# --- Header stripping ---


def strip_header_block(text: str) -> str:
    """Remove the markdown title block since YAML front matter renders it.

    Handles multiple header patterns found across the SEBE repo:
      # Title -> ## Subtitle -> **fields** -> ---
      # Title -> **fields** -> ## Subtitle -> italic text -> ---
      # Title -> **fields** -> plain text preamble -> ---
      # Title -> **fields** -> ---

    Strategy: walk lines from the top, consuming known header elements
    (H1, H2, bold fields, italic lines, plain text continuations) until
    we hit a horizontal rule (---) or a section heading that starts body
    content. This is more robust than a single regex pattern.
    """
    lines = text.split("\n")
    i = 0
    n = len(lines)

    # Skip leading blank lines
    while i < n and lines[i].strip() == "":
        i += 1

    # Must start with H1
    if i >= n or not lines[i].startswith("# "):
        return text
    i += 1

    # Track what we have consumed so we can distinguish a subtitle H2
    # from a body-section H2.
    subtitle_consumed = False
    in_header = True

    while i < n and in_header:
        line = lines[i]
        stripped = line.strip()

        # Blank line: skip
        if stripped == "":
            i += 1
            continue

        # Horizontal rule: consume it and stop (end of header)
        if stripped == "---":
            i += 1
            break

        # H2 subtitle (consume at most one; the first H2 in the header)
        if stripped.startswith("## ") and not subtitle_consumed:
            subtitle_consumed = True
            i += 1
            continue

        # H2 that looks like a section start (second H2, or after
        # separator-like content): stop consuming
        if stripped.startswith("## ") and subtitle_consumed:
            break

        # H1 that is not the title (shouldn't happen, but be safe)
        if stripped.startswith("# "):
            break

        # Bold field line: **Something:** value or **SOMETHING**
        if stripped.startswith("**"):
            i += 1
            continue

        # Italic line (often a tagline or preamble below the title)
        if stripped.startswith("*") and not stripped.startswith("**"):
            i += 1
            continue

        # Plain text that continues a previous bold field (multi-line
        # **Purpose:** text that wraps across lines without a blank line).
        # Only consume if the previous non-blank line was a bold field
        # or another continuation line, not a heading.
        prev = i - 1
        while prev >= 0 and lines[prev].strip() == "":
            prev -= 1
        if prev >= 0:
            prev_stripped = lines[prev].strip()
            if prev_stripped.startswith("**") or (
                prev_stripped
                and not prev_stripped.startswith("#")
                and not prev_stripped == "---"
            ):
                i += 1
                continue

        # Anything else: stop consuming (body content starts here)
        break

    # Skip trailing blank lines after header
    while i < n and lines[i].strip() == "":
        i += 1

    return "\n".join(lines[i:])


# --- Content preprocessing ---


def strip_backtick_tags(text: str) -> str:
    """Remove inline backtick tags like `FINANCIAL`, `TECHNICAL` etc."""
    return re.sub(
        r"\s*`(?:FINANCIAL|TECHNICAL|GOVERNANCE|SOVEREIGNTY|LEGAL|TRUST|"
        r"POLITICAL|ECONOMIC|MILITARY|SOCIAL|CULTURAL|ENVIRONMENTAL|"
        r"OPERATIONAL|STRATEGIC|TACTICAL)`",
        "",
        text,
    )


def clean_editorial_notes(text: str) -> str:
    """Clean up editorial note bracket markers for rendering.

    Converts **[NOTE:** ... **]** to **NOTE:** ...
    """
    # Strip opening bracket from note labels
    text = re.sub(
        r"\*\*\[(NOTE|CORRECTION|EDITORIAL NOTE):\*\*",
        r"**\1:**",
        text,
    )
    # Strip closing bracket markers
    text = re.sub(r"\*\*\]\*\*", "", text)
    return text


def strip_editorial_notes(text: str) -> str:
    """Remove all blockquote editorial notes entirely."""
    lines = text.split("\n")
    result = []
    in_blockquote = False
    for line in lines:
        if line.startswith("> "):
            in_blockquote = True
            continue
        if in_blockquote and line.strip() == "":
            in_blockquote = False
            continue
        if not in_blockquote:
            result.append(line)
    return "\n".join(result)


# --- Utility functions ---


def convert_landscape_markers(text: str, fmt: str = "latex") -> str:
    """Convert HTML comment landscape markers to format-specific commands.

    Authors mark landscape sections in markdown with:
        <!-- landscape -->
        ... wide content (tables, etc.) ...
        <!-- /landscape -->

    These HTML comments are invisible in any markdown renderer and
    self-documenting in the source file.

    For LaTeX output, markers become pdflscape environment commands with
    page breaks to ensure clean orientation transitions.  For other
    formats, text is returned unchanged (future extension point for DOCX
    section breaks).

    Args:
        text: Preprocessed markdown text.
        fmt: Target format — "latex" inserts LaTeX commands, anything
             else returns text unchanged.

    Returns:
        Text with markers replaced (or unchanged if fmt is not "latex").
    """
    if fmt != "latex":
        return text

    # Use pandoc raw-block fenced syntax so that markdown content
    # (headings, tables, lists) between the markers is still processed
    # normally by pandoc, while the LaTeX environment commands pass
    # through verbatim to pdflatex.
    _LANDSCAPE_OPEN = "```{=latex}\n\\newpage\n\\begin{landscape}\n```"
    _LANDSCAPE_CLOSE = "```{=latex}\n\\end{landscape}\n\\newpage\n```"

    # Use lambda replacements to avoid re.sub interpreting backslashes
    # in the replacement strings (\b, \e, \n would be mangled).
    text = re.sub(
        r"<!--\s*landscape\s*-->",
        lambda _: _LANDSCAPE_OPEN,
        text,
    )
    text = re.sub(
        r"<!--\s*/landscape\s*-->",
        lambda _: _LANDSCAPE_CLOSE,
        text,
    )
    return text


def yaml_safe(text: str) -> str:
    """Escape a string for safe inclusion as a YAML double-quoted value.

    Handles embedded double quotes and backslashes which break YAML
    parsing (e.g. glossary.md subtitle: 'A Note on "Robots"').
    """
    return text.replace("\\", "\\\\").replace('"', '\\"')


def infer_header_right(meta: dict) -> str:
    """Infer a sensible running header right text from document metadata.

    Heuristics:
      1. If date contains 'briefing notes', use 'Briefing Notes'
      2. If subtitle exists, truncate to 50 chars
      3. Fall back to truncated title
    """
    date_str = meta.get("date", "")
    if "briefing notes" in date_str.lower():
        return "Briefing Notes"

    subtitle = meta.get("subtitle", "")
    if subtitle:
        return subtitle[:50]

    title = meta.get("title", "Document")
    return title[:50]
