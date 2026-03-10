# Document Sync

> GOTCHA goal: keep site/docs/ generated from docs/ source files.

## Purpose

Single source of truth for all SEBE documents. Humans edit `docs/`.
The build script generates `site/docs/` with Jekyll front matter, HTML
links, grouped index page with tag filtering and difficulty badges.

## When to Run

- After editing any file in `docs/`
- Before committing changes to `docs/*.md` (pre-commit hook enforces this)
- When adding a new document to the site

## How to Run

From `automation_framework/`:

```bash
# Validate doc headers
python -m tools.doc_lint

# Generate site/docs/ from docs/
python -m tools.doc_sync --sync

# Check if site/docs/ is stale (used by pre-commit hook)
python -m tools.doc_sync --check
```

## Adding a New Document

1. Create the file in `docs/` with a conforming header:
   ```
   # Title

   **Author:** Jason Huxley
   **Date:** Month Year
   **Version:** X.Y

   ---

   ## First section
   ```

2. Add an entry to `tools/doc_sync_map.yaml` with title, description,
   group, difficulty, index_description, and order.

3. Run `python -m tools.doc_sync --sync`.

4. Commit both `docs/new_file.md` and `site/docs/new_file.md`.

## Cross-References

Use backtick references in `docs/` source files:

```markdown
See `revenue_model.md` for derivation.
```

The build script transforms these to HTML links:

```markdown
See [SEBE Revenue Model](revenue_model.html) for derivation.
```

Only filenames listed in `doc_sync_map.yaml` are transformed.
Unresolved references produce a warning.

## Pre-commit Hook

Installed at `.git/hooks/pre-commit`. Runs automatically when any
`docs/*.md` file is staged. Two checks:

1. `doc_lint` validates header conformance
2. `doc_sync --check` verifies site/docs/ is fresh

If either fails, the commit is blocked with instructions.

## Document Header Standard

Every `docs/*.md` file in the mapping must have:

- Line 1: `# Title`
- `**Author:**` line before `---`
- `**Date:**` line before `---`
- `**Version:**` line before `---`
- `---` separator before content

Optional: `## Subtitle` (line 3), `**Status:**`, `**Target audience:**`.

## Status

- [x] Plan and spec
- [x] YAML mapping
- [x] Linter tool
- [x] Sync tool
- [x] Index generation with groups and JS filter
- [x] CSS for filter pills and difficulty badges
- [x] Pre-commit hook
- [x] Source file fixes (public_explainer, SEBE_summary)
- [x] Goal file and manifest update
