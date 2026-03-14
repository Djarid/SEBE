"""
PDF generation tool for the SEBE automation framework.

Converts markdown files to professionally styled PDFs using pandoc and
pdflatex. Produces A4 documents with EB Garamond serif font, dark blue
section headings, running headers/footers, and tinted editorial note
boxes.

Requires: pandoc, pdflatex, texlive (with ebgaramond, titlesec, fancyhdr,
          mdframed, microtype, enumitem, xcolor, titling, etoolbox)

Run from automation_framework/:
    python -m tools.pdf_writer --file <markdown_file> [options]

Options:
    --output, -o      Output PDF path (default: same name, .pdf extension)
    --title           Override document title
    --author          Override author (default: Jason Huxley)
    --date            Override date line
    --subtitle        Override subtitle
    --header-left     Running header left text
    --header-right    Running header right text (default: inferred from doc)
    --toc             Include table of contents
    --no-notes        Strip editorial notes (blockquotes) from output
    --no-copyright    Omit CC-BY 4.0 copyright footer
    --raw             No preprocessing (skip tag stripping, note cleanup)
    --batch DIR       Process all .md files in directory
    --dry-run         Show what would be generated without doing it

Examples:
    python -m tools.pdf_writer --file ../../docs/academic_brief.md
    python -m tools.pdf_writer --file ../../drafts/nhs_palantir_v2.md -o out.pdf
    python -m tools.pdf_writer --file doc.md --title "Custom Title" --author "A. Person"
    python -m tools.pdf_writer --file ../../docs/academic_brief.md --toc
    python -m tools.pdf_writer --batch ../../docs/
    python -m tools.pdf_writer --batch ../../docs/ --dry-run
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tools._doc_common import (
    clean_editorial_notes,
    convert_landscape_markers,
    extract_metadata,
    infer_header_right,
    strip_backtick_tags,
    strip_editorial_notes,
    strip_header_block,
    yaml_safe,
)


# --- Dependency checks ---


def check_dependencies() -> list[str]:
    """Check that pandoc and pdflatex are available."""
    missing = []
    for cmd in ("pandoc", "pdflatex"):
        if shutil.which(cmd) is None:
            missing.append(cmd)
    return missing


# --- LaTeX preamble and YAML front matter ---


def _escape_latex_header(text: str) -> str:
    """Escape characters that break LaTeX in running headers."""
    return text.replace("&", r"\&")


def build_yaml_front_matter(
    title: str = "Document",
    subtitle: str = "",
    author: str = "Jason Huxley",
    date: str = "",
    version: str = "",
    header_left: str | None = None,
    header_right: str | None = None,
    copyright_notice: bool = True,
    toc: bool = False,
) -> str:
    """Build pandoc YAML front matter with full LaTeX preamble.

    Generates the YAML block that pandoc reads to configure document
    metadata, geometry, font, colours, headers/footers, and the
    editorial-note blockquote style.
    """
    # Escape ampersands for LaTeX in running headers
    hl = _escape_latex_header(header_left if header_left else title)
    hr = _escape_latex_header(header_right if header_right else "Document")

    # Append version to date line if present
    date_line = date
    if version:
        if date_line:
            date_line = f"{date_line} — Version {version}"
        else:
            date_line = f"Version {version}"

    # Copyright footer LaTeX (conditional)
    copyright_line = ""
    if copyright_notice:
        copyright_line = (
            "  \\fancyfoot[L]{\\tiny\\color{midgrey}"
            "\\textcopyright\\ 2026 Jason Huxley. CC-BY 4.0.}\n"
        )

    yaml = f'---\ntitle: "{yaml_safe(title)}"\n'
    if subtitle:
        yaml += f'subtitle: "{yaml_safe(subtitle)}"\n'
    yaml += f'author: "{yaml_safe(author)}"\n'
    yaml += f'date: "{yaml_safe(date_line)}"\n'
    yaml += "documentclass: article\n"
    yaml += "classoption:\n"
    yaml += "  - a4paper\n"
    yaml += "  - 11pt\n"
    yaml += "geometry:\n"
    yaml += "  - margin=2.5cm\n"
    yaml += "  - top=3cm\n"
    yaml += "  - bottom=3cm\n"
    yaml += "fontfamily: ebgaramond\n"
    yaml += "fontfamilyoptions:\n"
    yaml += "  - lining\n"
    if toc:
        yaml += "toc: true\n"
        yaml += "toc-depth: 2\n"
    yaml += "header-includes: |\n"
    yaml += "  \\usepackage[T1]{fontenc}\n"
    yaml += "  \\usepackage[utf8]{inputenc}\n"
    yaml += "  \\usepackage{textcomp}\n"
    yaml += "  \\usepackage{microtype}\n"
    yaml += "  \\usepackage{titlesec}\n"
    yaml += "  \\usepackage{titling}\n"
    yaml += "  \\usepackage{fancyhdr}\n"
    yaml += "  \\usepackage{xcolor}\n"
    yaml += "  \\usepackage{enumitem}\n"
    yaml += "  \\usepackage{mdframed}\n"
    yaml += "  \\usepackage{pdflscape}\n"
    yaml += "  \\usepackage{newunicodechar}\n"
    yaml += "  \\newunicodechar{≈}{\\ensuremath{\\approx}}\n"
    yaml += "  \\newunicodechar{≥}{\\ensuremath{\\geq}}\n"
    yaml += "  \\newunicodechar{≤}{\\ensuremath{\\leq}}\n"
    yaml += "  \\newunicodechar{→}{\\ensuremath{\\rightarrow}}\n"
    yaml += "  \\newunicodechar{—}{---}\n"
    yaml += "  \\newunicodechar{–}{--}\n"
    yaml += "  \\newunicodechar{☐}{$\\square$}\n"
    yaml += "  \\newunicodechar{☑}{$\\boxtimes$}\n"
    yaml += "  \\definecolor{darkblue}{HTML}{1B3A5C}\n"
    yaml += "  \\definecolor{midgrey}{HTML}{555555}\n"
    yaml += "  \\definecolor{rulered}{HTML}{8B2500}\n"
    yaml += "  \\definecolor{notebg}{HTML}{FFFFF0}\n"
    yaml += "  \\definecolor{noteborder}{HTML}{CCCCAA}\n"
    yaml += "  \\pretitle{\\begin{center}\\LARGE\\bfseries\\color{darkblue}}\n"
    yaml += "  \\posttitle{\\par\\end{center}\\vskip 0.5em}\n"
    yaml += "  \\preauthor{\\begin{center}\\large\\color{midgrey}}\n"
    yaml += "  \\postauthor{\\par\\end{center}}\n"
    yaml += "  \\predate{\\begin{center}\\color{midgrey}}\n"
    yaml += "  \\postdate{\\par\\end{center}}\n"
    yaml += "  \\titleformat{\\section}{\\large\\bfseries\\color{darkblue}}{}{0em}{}\n"
    yaml += (
        "  \\titleformat{\\subsection}"
        "{\\normalsize\\bfseries\\color{darkblue}}{}{0em}{}\n"
    )
    yaml += "  \\titlespacing*{\\section}{0pt}{1.5em}{0.8em}\n"
    yaml += "  \\titlespacing*{\\subsection}{0pt}{1em}{0.4em}\n"
    yaml += "  \\pagestyle{fancy}\n"
    yaml += "  \\fancyhf{}\n"
    yaml += f"  \\fancyhead[L]{{\\small\\color{{midgrey}}\\textit{{{hl}}}}}\n"
    yaml += f"  \\fancyhead[R]{{\\small\\color{{midgrey}}\\textit{{{hr}}}}}\n"
    yaml += "  \\fancyfoot[C]{\\small\\color{midgrey}\\thepage}\n"
    yaml += copyright_line
    yaml += "  \\renewcommand{\\headrulewidth}{0.4pt}\n"
    yaml += "  \\renewcommand{\\footrulewidth}{0pt}\n"
    yaml += (
        "  \\AtBeginDocument{\\fancypagestyle{plain}"
        "{\\fancyhf{}\\fancyfoot[C]{\\small\\color{midgrey}\\thepage}"
    )
    if copyright_notice:
        yaml += (
            "\\fancyfoot[L]{\\tiny\\color{midgrey}"
            "\\textcopyright\\ 2026 Jason Huxley. CC-BY 4.0.}"
        )
    yaml += "}}\n"
    yaml += (
        "  \\renewenvironment{quote}"
        "{\\begin{mdframed}[backgroundcolor=notebg,linecolor=noteborder,"
        "linewidth=1pt,leftline=true,rightline=false,topline=false,"
        "bottomline=false,innerleftmargin=10pt,innerrightmargin=10pt,"
        "innertopmargin=8pt,innerbottommargin=8pt]\\small\\color{midgrey}}"
        "{\\end{mdframed}}\n"
    )
    yaml += "  \\setlist[itemize]{leftmargin=1.5em,itemsep=0.3em}\n"
    yaml += "  \\setlist[enumerate]{leftmargin=1.5em,itemsep=0.3em}\n"
    yaml += "  \\setlength{\\parskip}{0.6em}\n"
    yaml += "  \\setlength{\\parindent}{0em}\n"
    yaml += "---\n\n"
    return yaml


# --- Main preprocessing pipeline ---


def preprocess(
    text: str,
    title: str | None = None,
    subtitle: str | None = None,
    author: str | None = None,
    date: str | None = None,
    header_left: str | None = None,
    header_right: str | None = None,
    no_notes: bool = False,
    no_copyright: bool = False,
    toc: bool = False,
    raw: bool = False,
) -> str:
    """Preprocess markdown text for pandoc PDF generation.

    Pipeline:
      1. Extract metadata from header
      2. Strip header block (replaced by YAML front matter)
      3. Strip backtick tags (FINANCIAL, TECHNICAL, etc.)
      4. Clean or strip editorial notes
      5. Build YAML front matter with LaTeX preamble
      6. Concatenate front matter + processed body
    """
    meta = extract_metadata(text)

    if raw:
        fm = build_yaml_front_matter(
            title=title or meta.get("title", "Document"),
            subtitle=subtitle or meta.get("subtitle", ""),
            author=author or meta.get("author", "Jason Huxley"),
            date=date or meta.get("date", ""),
            version=meta.get("version", ""),
            header_left=header_left,
            header_right=header_right or infer_header_right(meta),
            copyright_notice=not no_copyright,
            toc=toc,
        )
        return fm + text

    # Strip header block (will be replaced by YAML front matter)
    text = strip_header_block(text)

    # Strip backtick tags
    text = strip_backtick_tags(text)

    # Handle editorial notes
    if no_notes:
        text = strip_editorial_notes(text)
    else:
        text = clean_editorial_notes(text)

    # Convert landscape section markers to LaTeX commands
    text = convert_landscape_markers(text, fmt="latex")

    # Build front matter
    fm = build_yaml_front_matter(
        title=title or meta.get("title", "Document"),
        subtitle=subtitle or meta.get("subtitle", ""),
        author=author or meta.get("author", "Jason Huxley"),
        date=date or meta.get("date", ""),
        version=meta.get("version", ""),
        header_left=header_left,
        header_right=header_right or infer_header_right(meta),
        copyright_notice=not no_copyright,
        toc=toc,
    )

    return fm + text


# --- PDF generation ---


def generate_pdf(md_path: Path, output_path: Path, **kwargs) -> Path:
    """Generate a styled PDF from a markdown file.

    Args:
        md_path: Path to the input markdown file.
        output_path: Path for the output PDF.
        **kwargs: Passed to preprocess() (title, author, date, etc.)

    Returns:
        Path to the generated PDF.

    Raises:
        RuntimeError: If pandoc or pdflatex fails.
        FileNotFoundError: If input file doesn't exist.
    """
    if not md_path.exists():
        raise FileNotFoundError(f"Input file not found: {md_path}")

    missing = check_dependencies()
    if missing:
        raise RuntimeError(
            f"Missing dependencies: {', '.join(missing)}. Install pandoc and texlive."
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
            "--pdf-engine=pdflatex",
            "-V",
            "colorlinks=true",
            "-V",
            "urlcolor=NavyBlue",
        ]
        if toc:
            cmd.extend(["--toc", "--toc-depth=2"])

        # Check if soul.sty is available (needed for ~~strikethrough~~).
        # If missing, disable the strikeout extension to avoid LaTeX errors.
        _has_soul = (
            shutil.which("kpsewhich")
            and subprocess.run(
                ["kpsewhich", "soul.sty"],
                capture_output=True,
                timeout=10,
            ).returncode
            == 0
        )
        if not _has_soul:
            cmd.extend(["--from", "markdown-strikeout"])

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
    """Generate PDFs for all markdown files in a directory.

    Args:
        directory: Path to directory containing .md files.
        dry_run: If True, print what would be done without generating.
        **kwargs: Passed to generate_pdf() for each file.

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
        output = md_file.with_suffix(".pdf")

        if dry_run:
            print(f"  WOULD: {md_file.name} -> {output.name}")
            continue

        try:
            result = generate_pdf(md_file, output, **kwargs)
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
        description="Generate styled PDF from markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m tools.pdf_writer --file ../../docs/academic_brief.md\n"
            "  python -m tools.pdf_writer --file doc.md -o output.pdf\n"
            '  python -m tools.pdf_writer --file doc.md --title "My Title"\n'
            "  python -m tools.pdf_writer --file doc.md --toc\n"
            "  python -m tools.pdf_writer --batch ../../docs/\n"
            "  python -m tools.pdf_writer --batch ../../docs/ --dry-run\n"
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
        "--output", "-o", help="Output PDF path (default: same name with .pdf)"
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
    parser.add_argument("--header-left", help="Running header left text")
    parser.add_argument(
        "--header-right",
        default=None,
        help="Running header right text (default: inferred from document)",
    )
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
    parser.add_argument(
        "--raw",
        action="store_true",
        help="No preprocessing (skip tag stripping, note cleanup)",
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

    # Common kwargs for generate_pdf / batch_generate
    gen_kwargs = dict(
        title=args.title,
        subtitle=args.subtitle,
        author=args.author,
        date=args.date,
        header_left=args.header_left,
        header_right=args.header_right,
        no_notes=args.no_notes,
        no_copyright=args.no_copyright,
        toc=args.toc,
        raw=args.raw,
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
        output_path = Path(args.output) if args.output else md_path.with_suffix(".pdf")
        print(f"WOULD: {md_path} -> {output_path}")
        return

    output_path = Path(args.output) if args.output else md_path.with_suffix(".pdf")

    try:
        result = generate_pdf(md_path, output_path, **gen_kwargs)
        print(f"OK {result} ({result.stat().st_size:,} bytes)")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
