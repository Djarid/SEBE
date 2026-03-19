"""
DOCX generation tool for the SEBE automation framework.

Converts markdown files to styled DOCX documents using pandoc with a
custom reference template. Produces A4 documents with dark blue section
headings, Cambria font, and clean table formatting matching the PDF
house style.

Requires: pandoc (3.0+)

Run from automation_framework/:
    python -m tools.docx_writer --file <markdown_file> [options]

Options:
    --output, -o      Output DOCX path (default: same name, .docx extension)
    --title           Override document title
    --author          Override author (default: Jason Huxley)
    --date            Override date line
    --subtitle        Override subtitle
    --toc             Include table of contents
    --no-notes        Strip editorial notes (blockquotes) from output
    --no-copyright    Omit CC-BY 4.0 copyright footer paragraph
    --batch DIR       Process all .md files in directory
    --dry-run         Show what would be generated without doing it

Examples:
    python -m tools.docx_writer --file ../../docs/academic_brief.md
    python -m tools.docx_writer --file ../../drafts/gpew_platform_dpia.md -o dpia.docx
    python -m tools.docx_writer --file doc.md --title "Custom Title" --author "A. Person"
    python -m tools.docx_writer --file ../../docs/academic_brief.md --toc
    python -m tools.docx_writer --batch ../../docs/
    python -m tools.docx_writer --batch ../../docs/ --dry-run
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools._doc_common import (
    clean_editorial_notes,
    extract_metadata,
    infer_header_right,
    strip_backtick_tags,
    strip_editorial_notes,
    strip_header_block,
    yaml_safe,
)


# Path to the custom reference.docx template (lives alongside this module)
_REFERENCE_DOCX = Path(__file__).resolve().parent / "reference.docx"


# --- Dependency checks ---


def check_dependencies() -> list[str]:
    """Check that pandoc is available."""
    missing = []
    if shutil.which("pandoc") is None:
        missing.append("pandoc")
    return missing


# --- YAML front matter for DOCX ---


def build_docx_yaml_front_matter(
    title: str = "Document",
    subtitle: str = "",
    author: str = "Jason Huxley",
    date: str = "",
    version: str = "",
    toc: bool = False,
) -> str:
    """Build pandoc YAML front matter for DOCX output.

    Much simpler than the PDF equivalent: no LaTeX preamble needed.
    Pandoc uses the YAML metadata to populate DOCX document properties
    and the title page.
    """
    # Append version to date line if present
    date_line = date
    if version:
        if date_line:
            date_line = f"{date_line} — Version {version}"
        else:
            date_line = f"Version {version}"

    yaml = f'---\ntitle: "{yaml_safe(title)}"\n'
    if subtitle:
        yaml += f'subtitle: "{yaml_safe(subtitle)}"\n'
    yaml += f'author: "{yaml_safe(author)}"\n'
    yaml += f'date: "{yaml_safe(date_line)}"\n'
    if toc:
        yaml += "toc: true\n"
        yaml += "toc-depth: 2\n"
    yaml += "---\n\n"
    return yaml


# --- Copyright footer ---


_COPYRIGHT_BLOCK = "\n\n---\n\n*© 2026 Jason Huxley. Licensed under CC-BY 4.0.*\n"


# --- Main preprocessing pipeline ---


def preprocess(
    text: str,
    title: str | None = None,
    subtitle: str | None = None,
    author: str | None = None,
    date: str | None = None,
    no_notes: bool = False,
    no_copyright: bool = False,
    toc: bool = False,
) -> str:
    """Preprocess markdown text for pandoc DOCX generation.

    Pipeline:
      1. Extract metadata from header
      2. Strip header block (replaced by YAML front matter)
      3. Strip backtick tags (FINANCIAL, TECHNICAL, etc.)
      4. Clean or strip editorial notes
      5. Build YAML front matter (DOCX-specific, no LaTeX)
      6. Append copyright footer if requested
      7. Concatenate front matter + processed body
    """
    meta = extract_metadata(text)

    # Strip header block (will be replaced by YAML front matter)
    text = strip_header_block(text)

    # Strip backtick tags
    text = strip_backtick_tags(text)

    # Handle editorial notes
    if no_notes:
        text = strip_editorial_notes(text)
    else:
        text = clean_editorial_notes(text)

    # Append copyright footer as a markdown paragraph
    if not no_copyright:
        text += _COPYRIGHT_BLOCK

    # Build front matter
    fm = build_docx_yaml_front_matter(
        title=title or meta.get("title", "Document"),
        subtitle=subtitle or meta.get("subtitle", ""),
        author=author or meta.get("author", "Jason Huxley"),
        date=date or meta.get("date", ""),
        version=meta.get("version", ""),
        toc=toc,
    )

    return fm + text


# --- DOCX generation ---


def generate_docx(md_path: Path, output_path: Path, **kwargs) -> Path:
    """Generate a styled DOCX from a markdown file.

    Args:
        md_path: Path to the input markdown file.
        output_path: Path for the output DOCX.
        **kwargs: Passed to preprocess() (title, author, date, etc.)

    Returns:
        Path to the generated DOCX.

    Raises:
        RuntimeError: If pandoc fails.
        FileNotFoundError: If input file or reference template doesn't exist.
    """
    if not md_path.exists():
        raise FileNotFoundError(f"Input file not found: {md_path}")

    if not _REFERENCE_DOCX.exists():
        raise FileNotFoundError(
            f"Reference template not found: {_REFERENCE_DOCX}. "
            "Run: pandoc --print-default-data-file reference.docx > tools/reference.docx"
        )

    missing = check_dependencies()
    if missing:
        raise RuntimeError(
            f"Missing dependencies: {', '.join(missing)}. Install pandoc."
        )

    text = md_path.read_text(encoding="utf-8")

    # Extract toc flag from kwargs for pandoc args (also passed to preprocess)
    toc = kwargs.get("toc", False)

    processed = preprocess(text, **kwargs)

    # Write to temp file and run pandoc
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(processed)
        tmp_path = Path(tmp.name)

    try:
        cmd = [
            "pandoc",
            str(tmp_path),
            "-o",
            str(output_path),
            "--to",
            "docx",
            f"--reference-doc={_REFERENCE_DOCX}",
        ]
        if toc:
            cmd.extend(["--toc", "--toc-depth=2"])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"pandoc failed (exit {result.returncode}):\n{result.stderr}"
            )
    finally:
        tmp_path.unlink(missing_ok=True)

    return output_path


# --- Batch processing ---


def batch_generate(
    directory: Path,
    dry_run: bool = False,
    **kwargs,
) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Generate DOCX files for all markdown files in a directory.

    Args:
        directory: Path to directory containing .md files.
        dry_run: If True, print what would be done without generating.
        **kwargs: Passed to generate_docx() for each file.

    Returns:
        Tuple of (successes, failures) where failures is list of
        (path, error_message) pairs.
    """
    successes: list[Path] = []
    failures: list[tuple[Path, str]] = []

    md_files = sorted(directory.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {directory}", file=sys.stderr)
        return successes, failures

    for md_file in md_files:
        output = md_file.with_suffix(".docx")

        if dry_run:
            print(f"  WOULD: {md_file.name} -> {output.name}")
            continue

        try:
            result = generate_docx(md_file, output, **kwargs)
            size = result.stat().st_size
            print(f"  OK {result.name} ({size:,} bytes)")
            successes.append(result)
        except (RuntimeError, FileNotFoundError) as e:
            msg = str(e).split("\n")[0]  # First line of error only
            print(f"  FAIL {md_file.name}: {msg}", file=sys.stderr)
            failures.append((md_file, str(e)))

    return successes, failures


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        description="Generate styled DOCX from markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m tools.docx_writer --file ../../docs/academic_brief.md\n"
            "  python -m tools.docx_writer --file doc.md -o output.docx\n"
            '  python -m tools.docx_writer --file doc.md --title "My Title"\n'
            "  python -m tools.docx_writer --file doc.md --toc\n"
            "  python -m tools.docx_writer --batch ../../docs/\n"
            "  python -m tools.docx_writer --batch ../../docs/ --dry-run\n"
        ),
    )

    # Input source (mutually exclusive: single file or batch directory)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", "-f", help="Input markdown file path")
    source.add_argument(
        "--batch", metavar="DIR", help="Process all .md files in directory"
    )

    # Output
    parser.add_argument(
        "--output", "-o", help="Output DOCX path (default: same name with .docx)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without doing it",
    )

    # Metadata overrides
    parser.add_argument("--title", help="Override document title")
    parser.add_argument("--subtitle", help="Override subtitle")
    parser.add_argument(
        "--author",
        help="Override author (default: extracted or Jason Huxley)",
    )
    parser.add_argument("--date", help="Override date line")

    # Layout options
    parser.add_argument(
        "--toc",
        action="store_true",
        help="Include table of contents",
    )
    parser.add_argument(
        "--no-copyright",
        action="store_true",
        help="Omit CC-BY 4.0 copyright footer",
    )
    parser.add_argument(
        "--no-notes",
        action="store_true",
        help="Strip editorial notes (blockquotes) from output",
    )
    args = parser.parse_args()

    # Check dependencies once
    missing = check_dependencies()
    if missing:
        print(
            f"ERROR: Missing dependencies: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Common kwargs for generate_docx / batch_generate
    gen_kwargs = dict(
        title=args.title,
        subtitle=args.subtitle,
        author=args.author,
        date=args.date,
        no_notes=args.no_notes,
        no_copyright=args.no_copyright,
        toc=args.toc,
    )

    # Batch mode
    if args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.is_dir():
            print(f"ERROR: Not a directory: {batch_dir}", file=sys.stderr)
            sys.exit(1)

        print(f"Processing {batch_dir}/ ...")
        successes, failures = batch_generate(
            batch_dir, dry_run=args.dry_run, **gen_kwargs
        )

        if not args.dry_run:
            print(f"\nDone: {len(successes)} succeeded, {len(failures)} failed")
        if failures:
            sys.exit(1)
        return

    # Single file mode
    md_path = Path(args.file)
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        output_path = Path(args.output) if args.output else md_path.with_suffix(".docx")
        print(f"WOULD: {md_path} -> {output_path}")
        return

    output_path = Path(args.output) if args.output else md_path.with_suffix(".docx")

    try:
        result = generate_docx(md_path, output_path, **gen_kwargs)
        print(f"OK {result} ({result.stat().st_size:,} bytes)")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
