# PDF Generation

> GOTCHA goal: convert markdown documents to styled A4 PDFs.

## Purpose

Produce professionally formatted PDFs from any SEBE markdown document.
Output matches the house style established with `drafts/nhs_palantir_v2.pdf`:
EB Garamond serif font, dark blue section headings, running headers/footers,
tinted editorial note boxes with left border, CC-BY 4.0 copyright footer.

## When to Use

- Before distributing any document externally (email, print, upload)
- When preparing briefing notes, policy submissions, or academic briefs
- After finishing edits to a document that will be shared as PDF
- When regenerating all PDFs after a style change

## Tool

`tools/pdf_writer.py` (deterministic, no LLM involvement)

## How to Run

From `automation_framework/`:

```bash
# Single file
python -m tools.pdf_writer --file /path/to/document.md

# With table of contents (recommended for docs over 10 pages)
python -m tools.pdf_writer --file /path/to/document.md --toc

# Custom output path
python -m tools.pdf_writer --file /path/to/document.md -o /path/to/output.pdf

# Batch: all files in a directory
python -m tools.pdf_writer --batch /path/to/docs/

# Dry run: show what would be generated
python -m tools.pdf_writer --batch /path/to/docs/ --dry-run

# Override metadata
python -m tools.pdf_writer --file doc.md --title "Custom Title" --author "Name"

# Skip copyright footer (drafts not for external distribution)
python -m tools.pdf_writer --file doc.md --no-copyright

# Strip editorial notes from output
python -m tools.pdf_writer --file doc.md --no-notes
```

## Inputs

Any markdown file with a standard SEBE header. The tool handles multiple
header patterns:

- `# Title` / `## Subtitle` / `**Field: value**` lines / `---`
- `# Title` / `**Field: value**` / `## Subtitle` / `---`
- `# Title` / `**Field: value**` / `---` (no subtitle)

Recognised header fields: Author, Date, Updated, Prepared, Version, Status,
Target, Reference, Methodology.

## Outputs

A4 PDF with:
- EB Garamond serif font at 11pt
- Dark blue (#1B3A5C) section headings
- Running header: document title (left), inferred subtitle (right)
- Page numbers (centre footer)
- CC-BY 4.0 copyright notice (left footer, unless `--no-copyright`)
- Mixed portrait/landscape orientation via `<!-- landscape -->` markers
- Editorial notes rendered as tinted boxes with left border
- Inline backtick tags (FINANCIAL, TECHNICAL, etc.) stripped automatically
- Editorial bracket markers cleaned for clean rendering
- Version number appended to date line if present in header

## Dependencies

- `pandoc` (3.5+)
- `pdflatex` (TeX Live 2026)
- LaTeX packages: ebgaramond, titlesec, fancyhdr, mdframed, microtype,
  enumitem, xcolor, titling, etoolbox, newunicodechar, fontenc, inputenc,
  textcomp, pdflscape

If `soul.sty` is not available (needed for `~~strikethrough~~`), the tool
automatically disables the strikeout extension and continues.

## Quality Criteria

1. Every markdown file in `docs/` and `drafts/` must generate without error
2. Baseline: `drafts/nhs_palantir_v2.pdf` must be visually identical to the
   original 9-page PDF produced in the March 2026 session
3. Tables, lists, blockquotes, bold/italic text must render correctly
4. Unicode characters (pounds, arrows, approximation signs, ballot boxes)
   must render without LaTeX errors
5. YAML front matter must not break on titles containing quotes or ampersands

## Edge Cases

| Case | Handling |
|---|---|
| Title contains `&` | Escaped in LaTeX headers automatically |
| Title contains `"` | Escaped in YAML front matter automatically |
| No H2 subtitle | Subtitle field omitted, header-right inferred from title |
| `Updated:` instead of `Date:` | Recognised and merged into date field |
| Multi-line bold fields | Consumed by header stripper (continuation lines) |
| `~~strikethrough~~` without soul.sty | Strikeout extension disabled automatically |
| `<!-- landscape -->` / `<!-- /landscape -->` markers | Sections between markers render in landscape orientation (pdflscape) |
| No landscape markers in document | No change to output (backward compatible) |
| Unicode `≈`, `→`, `—`, `☐` | Mapped to LaTeX equivalents via newunicodechar |
| H2 after bold fields (not before) | Handled by line-walking header stripper |
| H2 after `---` separator | Treated as section heading, not subtitle |

## Programmatic API

For use by other tools or the daemon orchestrator:

```python
from tools.pdf_writer import generate_pdf, extract_metadata
from pathlib import Path

# Generate a single PDF
result = generate_pdf(
    Path("docs/academic_brief.md"),
    Path("docs/academic_brief.pdf"),
    toc=True,
)

# Extract metadata without generating
meta = extract_metadata(Path("docs/academic_brief.md").read_text())
# Returns: {'title': '...', 'subtitle': '...', 'author': '...', ...}
```
