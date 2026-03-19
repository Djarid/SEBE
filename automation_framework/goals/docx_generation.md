# DOCX Generation

> GOTCHA goal: convert markdown documents to styled DOCX files.

## Purpose

Produce professionally formatted DOCX files from any SEBE markdown document.
Output uses dark blue section headings, Cambria font, A4 page size, and clean
table formatting matching the PDF house style. DOCX output is suitable for
review, commenting, and distribution to external stakeholders who expect Word
format.

## When to Use

- When distributing documents for review by party committees (GPEx, AFCom)
- When recipients need to add tracked changes or comments
- When a document must be forwarded as an email attachment in editable format
- When preparing governance documents (DPIAs, TRAs, policies) for sign-off
- When regenerating all DOCX files after a style change

## Tool

`tools/docx_writer.py` (deterministic, no LLM involvement)

Shared preprocessing logic lives in `tools/_doc_common.py` (also used by
`tools/pdf_writer.py`).

## How to Run

From `automation_framework/`:

```bash
# Single file
python -m tools.docx_writer --file /path/to/document.md

# With table of contents (recommended for 10+ page docs)
python -m tools.docx_writer --file /path/to/document.md --toc

# Custom output path
python -m tools.docx_writer --file /path/to/document.md -o /path/to/output.docx

# Batch: all files in a directory
python -m tools.docx_writer --batch /path/to/docs/

# Dry run: show what would be generated
python -m tools.docx_writer --batch /path/to/docs/ --dry-run

# Override metadata
python -m tools.docx_writer --file doc.md --title "Custom Title" --author "Name"

# Skip copyright footer
python -m tools.docx_writer --file doc.md --no-copyright

# Strip editorial notes from output
python -m tools.docx_writer --file doc.md --no-notes
```

## Inputs

Any markdown file. The tool handles SEBE header patterns (H1 title, H2
subtitle, bold metadata fields, horizontal rule separator) and extracts
metadata for the DOCX document properties.

## Outputs

A4 DOCX file with:

- Dark blue (#1B3A5C) section headings in Cambria
- 11pt Cambria body text
- Clean table rendering
- Document properties populated (title, author, date)
- Optional table of contents
- Optional CC-BY 4.0 copyright footer paragraph

## Dependencies

- pandoc (3.0+)
- Reference template: `tools/reference.docx` (customised pandoc default)

No pdflatex or texlive required (unlike PDF generation).

## Relationship to PDF Generation

Both tools share preprocessing logic via `tools/_doc_common.py`:

- `extract_metadata()` — header parsing
- `strip_header_block()` — remove markdown title block
- `strip_backtick_tags()` — remove inline category tags
- `clean_editorial_notes()` / `strip_editorial_notes()` — note handling
- `yaml_safe()` — YAML escaping
- `infer_header_right()` — smart defaults for running headers

PDF-specific logic (LaTeX preamble, EB Garamond font, running headers/footers,
mdframed blockquote styling) remains in `tools/pdf_writer.py`.

DOCX-specific logic (reference template, simpler YAML front matter, copyright
as markdown paragraph) lives in `tools/docx_writer.py`.

## Edge Cases

- Documents without standard SEBE headers: title defaults to "Document",
  author to "Jason Huxley"
- Very long tables: pandoc handles these natively in DOCX output
- Unicode characters: pandoc handles these natively (no newunicodechar
  needed unlike LaTeX)
- Batch mode skips non-.md files automatically

---

*Update this goal when the tool's capabilities or reference template change.*
