"""Document header linter for docs/ source files.

Validates that all documents listed in doc_sync_map.yaml conform to the
standard header format required by doc_sync.py.

Standard header:
    # Title
    (blank line)
    ## Subtitle (optional)
    (blank line, if subtitle present)
    **Author:** Jason Huxley
    **Date:** Month Year
    **Version:** X.Y
    **Status/Target audience:** ... (optional)
    (blank line)
    ---
    (blank line)
    ## First content heading

Usage:
    python -m tools.doc_lint           # lint all mapped documents
    python -m tools.doc_lint --fix     # report only, no auto-fix (reserved)
"""

import sys
from pathlib import Path

import yaml


def load_mapping() -> dict:
    """Load the document sync mapping."""
    map_path = Path(__file__).parent / "doc_sync_map.yaml"
    if not map_path.exists():
        print(f"FAIL: mapping not found at {map_path}")
        sys.exit(1)
    with open(map_path) as f:
        return yaml.safe_load(f)


def find_docs_dir() -> Path:
    """Find the docs/ directory (repo root)."""
    # tools/ is in automation_framework/tools/, docs/ is at repo root
    repo_root = Path(__file__).parent.parent.parent
    docs_dir = repo_root / "docs"
    if not docs_dir.is_dir():
        print(f"FAIL: docs/ directory not found at {docs_dir}")
        sys.exit(1)
    return docs_dir


def lint_document(filepath: Path, name: str) -> list[str]:
    """Lint a single document. Returns list of violation messages."""
    violations = []

    if not filepath.exists():
        violations.append(f"{name}: file not found at {filepath}")
        return violations

    lines = filepath.read_text(encoding="utf-8").splitlines()

    if not lines:
        violations.append(f"{name}: file is empty")
        return violations

    # Rule 1: Line 1 must start with '# '
    if not lines[0].startswith("# "):
        violations.append(f"{name}:1: first line must be a level-1 heading (# Title)")

    # Rule 2: Must not start with YAML front matter
    if lines[0].strip() == "---":
        violations.append(
            f"{name}:1: file starts with YAML front matter (---). "
            "docs/ files must use markdown headers, not Jekyll front matter"
        )
        return violations  # Can't validate further

    # Find the --- separator
    separator_line = None
    for i, line in enumerate(lines):
        if i == 0:
            continue  # Skip the title line
        if line.strip() == "---":
            separator_line = i
            break

    # Rules 3-5: Required metadata before separator
    header_region = lines[:separator_line] if separator_line is not None else lines

    has_author = any(line.startswith("**Author:**") for line in header_region)
    has_date = any(line.startswith("**Date:**") for line in header_region)
    has_version = any(line.startswith("**Version:**") for line in header_region)

    if not has_author:
        violations.append(f"{name}: missing **Author:** in header (before ---)")
    if not has_date:
        violations.append(f"{name}: missing **Date:** in header (before ---)")
    if not has_version:
        violations.append(f"{name}: missing **Version:** in header (before ---)")

    # Rule 6: --- separator must exist
    if separator_line is None:
        violations.append(f"{name}: missing --- separator between header and content")

    return violations


def main() -> int:
    mapping = load_mapping()
    docs_dir = find_docs_dir()
    documents = mapping.get("documents", {})

    all_violations = []

    for name in sorted(documents.keys()):
        filepath = docs_dir / f"{name}.md"
        violations = lint_document(filepath, name)
        all_violations.extend(violations)

    if all_violations:
        print(f"doc_lint: {len(all_violations)} violation(s) found:\n")
        for v in all_violations:
            print(f"  {v}")
        print()
        return 1

    print(f"doc_lint: all {len(documents)} documents pass header validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
