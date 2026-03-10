"""Document sync tool: generates site/docs/ from docs/ source files.

Reads the doc_sync_map.yaml mapping, strips markdown headers from docs/
source files, prepends Jekyll front matter, transforms backtick .md
references to HTML links, and generates the documents index page with
grouped tags and JS filtering.

Usage:
    python -m tools.doc_sync --sync    # generate site/docs/ from docs/
    python -m tools.doc_sync --check   # dry-run, exit non-zero if stale

Run from automation_framework/.
"""

import re
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


def find_paths() -> tuple[Path, Path]:
    """Find docs/ and site/docs/ directories."""
    repo_root = Path(__file__).parent.parent.parent
    docs_dir = repo_root / "docs"
    site_docs_dir = repo_root / "site" / "docs"
    if not docs_dir.is_dir():
        print(f"FAIL: docs/ not found at {docs_dir}")
        sys.exit(1)
    if not site_docs_dir.is_dir():
        print(f"FAIL: site/docs/ not found at {site_docs_dir}")
        sys.exit(1)
    return docs_dir, site_docs_dir


def strip_header(content: str) -> str:
    """Strip the markdown header block (everything up to and including
    the first --- separator and any immediately following blank line)."""
    lines = content.splitlines(keepends=True)

    separator_idx = None
    for i, line in enumerate(lines):
        if i == 0:
            continue  # Skip title line
        if line.strip() == "---":
            separator_idx = i
            break

    if separator_idx is None:
        # No separator found, return content as-is (linter should catch this)
        return content

    # Start from the line after the separator
    start = separator_idx + 1

    # Skip any immediately following blank lines
    while start < len(lines) and lines[start].strip() == "":
        start += 1

    return "".join(lines[start:])


def extract_metadata(content: str) -> dict:
    """Extract version and date from the markdown header block."""
    metadata = {}
    lines = content.splitlines()

    for line in lines:
        if line.strip() == "---":
            break
        if line.startswith("**Version:**"):
            metadata["version"] = line.replace("**Version:**", "").strip()
        if line.startswith("**Date:**"):
            metadata["date"] = line.replace("**Date:**", "").strip()

    return metadata


def build_link_lookup(documents: dict) -> dict:
    """Build a mapping from filename stem to (title, html_filename)."""
    lookup = {}
    for stem, doc in documents.items():
        lookup[stem] = (doc["title"], f"{stem}.html")
    return lookup


def transform_links(content: str, lookup: dict) -> tuple[str, list[str]]:
    """Transform backtick .md references to HTML links.

    Handles patterns like:
        `revenue_model.md`
        `revenue_model.md` Section 4
        `distribution_model.md` Sections 8.1-8.3

    Returns (transformed_content, list_of_warnings).
    """
    warnings = []

    def replace_ref(match: re.Match) -> str:
        stem = match.group(1)
        if stem in lookup:
            title, html_file = lookup[stem]
            return f"[{title}]({html_file})"
        warnings.append(f"unresolved reference: `{stem}.md`")
        return match.group(0)  # Leave as-is

    # Match `stem.md` (backtick-wrapped .md references)
    transformed = re.sub(r"`([a-zA-Z_]+)\.md`", replace_ref, content)

    return transformed, warnings


def build_front_matter(stem: str, doc: dict, metadata: dict) -> str:
    """Build Jekyll YAML front matter for a document."""
    fm = {
        "layout": "doc",
        "title": doc["title"],
        "description": doc["description"],
        "doc_author": "Jason Huxley",
        "permalink": f"/docs/{stem}.html",
    }

    # Version: from source metadata or mapping override
    version = metadata.get("version")
    if version:
        fm["version"] = version

    # Date: from mapping override or source metadata
    doc_date = doc.get("doc_date") or metadata.get("date")
    if doc_date:
        fm["doc_date"] = doc_date

    # Extra front matter from mapping
    extra = doc.get("extra_front_matter", {})
    if extra:
        fm.update(extra)

    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, str) and ('"' in value or ":" in value or "'" in value):
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def generate_index(mapping: dict) -> str:
    """Generate the documents index page with groups, tags and JS filter."""
    groups = mapping["groups"]
    documents = mapping["documents"]

    # Sort groups by order
    sorted_groups = sorted(groups.items(), key=lambda x: x[1]["order"])

    # Build group -> documents mapping
    group_docs = {}
    for stem, doc in documents.items():
        g = doc["group"]
        if g not in group_docs:
            group_docs[g] = []
        group_docs[g].append((stem, doc))

    # Sort documents within each group
    for g in group_docs:
        group_docs[g].sort(key=lambda x: x[1].get("order", 99))

    # Build the page
    lines = []

    # Front matter
    lines.append("---")
    lines.append("layout: default")
    lines.append("title: Documents")
    lines.append('description: "SEBE policy documents, models and analysis"')
    lines.append("permalink: /docs/")
    lines.append("---")
    lines.append("")

    # Heading
    lines.append(
        '<h1 class="prose" style="font-family: var(--serif); '
        'font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">'
        "Documents</h1>"
    )
    lines.append("")
    lines.append(
        '<p style="color: var(--muted); margin-bottom: 1.5rem;">'
        "All SEBE documents are open source under CC-BY 4.0. "
        "Use them, adapt them, argue with them.</p>"
    )
    lines.append("")

    # Filter pills
    lines.append(
        '<div class="doc-filter" role="navigation" aria-label="Filter documents">'
    )
    lines.append(
        '  <button class="doc-filter-pill active" data-filter="all">All</button>'
    )
    for group_key, group_meta in sorted_groups:
        if group_key in group_docs:
            heading = group_meta["heading"]
            lines.append(
                f'  <button class="doc-filter-pill" '
                f'data-filter="{group_key}">{heading}</button>'
            )
    lines.append("</div>")
    lines.append("")

    # Document groups
    for group_key, group_meta in sorted_groups:
        if group_key not in group_docs:
            continue

        heading = group_meta["heading"]
        lines.append(
            f'<h2 class="doc-group-heading" data-group="{group_key}">{heading}</h2>'
        )
        lines.append(f'<ul class="doc-list" data-group="{group_key}">')

        for stem, doc in group_docs[group_key]:
            difficulty = doc.get("difficulty", "")
            desc = doc.get("index_description", doc["description"])
            tag_class = f"post-tag-{difficulty}" if difficulty else ""
            badge_html = ""
            if difficulty:
                badge_html = (
                    f' <span class="post-tags">'
                    f'<span class="post-tag {tag_class}">'
                    f"{difficulty.upper()}</span></span>"
                )

            lines.append(f'  <li data-tags="{doc["group"]} {difficulty}">')
            lines.append(
                f"    <a href=\"{{{{ '/docs/{stem}.html' | relative_url }}}}\">"
                f"{doc['title']}</a>{badge_html}"
            )
            lines.append(f'    <p class="doc-desc">{desc}</p>')
            lines.append("  </li>")

        lines.append("</ul>")
        lines.append("")

    # JS filter script
    lines.append("<script>")
    lines.append(
        "document.querySelectorAll('.doc-filter-pill').forEach(function(pill) {"
    )
    lines.append("  pill.addEventListener('click', function() {")
    lines.append("    var filter = this.dataset.filter;")
    lines.append(
        "    document.querySelectorAll('.doc-filter-pill').forEach(function(p) {"
    )
    lines.append("      p.classList.remove('active');")
    lines.append("    });")
    lines.append("    this.classList.add('active');")
    lines.append(
        "    document.querySelectorAll('.doc-group-heading, .doc-list').forEach(function(el) {"
    )
    lines.append("      if (filter === 'all' || el.dataset.group === filter) {")
    lines.append("        el.style.display = '';")
    lines.append("      } else {")
    lines.append("        el.style.display = 'none';")
    lines.append("      }")
    lines.append("    });")
    lines.append("  });")
    lines.append("});")
    lines.append("</script>")
    lines.append("")

    return "\n".join(lines)


def sync(check_only: bool = False) -> int:
    """Main sync operation. Returns 0 on success, 1 if stale (check mode)."""
    mapping = load_mapping()
    docs_dir, site_docs_dir = find_paths()
    documents = mapping.get("documents", {})
    link_lookup = build_link_lookup(documents)

    stale_files = []
    all_warnings = []
    generated = {}

    # Generate each document
    for stem, doc in documents.items():
        source_path = docs_dir / f"{stem}.md"
        target_path = site_docs_dir / f"{stem}.md"

        if not source_path.exists():
            print(f"WARN: source file missing: {source_path}")
            continue

        source_content = source_path.read_text(encoding="utf-8")
        metadata = extract_metadata(source_content)
        body = strip_header(source_content)
        body, warnings = transform_links(body, link_lookup)

        for w in warnings:
            all_warnings.append(f"{stem}: {w}")

        front_matter = build_front_matter(stem, doc, metadata)
        output = front_matter + body

        generated[stem] = output

        # Check if target is stale
        if target_path.exists():
            existing = target_path.read_text(encoding="utf-8")
            if existing != output:
                stale_files.append(stem)
        else:
            stale_files.append(stem)

    # Generate index
    index_content = generate_index(mapping)
    index_path = site_docs_dir / "index.md"
    generated["index"] = index_content

    if index_path.exists():
        existing_index = index_path.read_text(encoding="utf-8")
        if existing_index != index_content:
            stale_files.append("index")
    else:
        stale_files.append("index")

    # Check for orphan files in site/docs/
    expected_files = {f"{stem}.md" for stem in documents}
    expected_files.add("index.md")
    for f in site_docs_dir.iterdir():
        if f.suffix == ".md" and f.name not in expected_files:
            all_warnings.append(f"orphan file in site/docs/: {f.name}")

    # Print warnings
    for w in all_warnings:
        print(f"WARN: {w}")

    if check_only:
        if stale_files:
            print(f"\ndoc_sync --check: {len(stale_files)} file(s) stale:")
            for f in stale_files:
                print(f"  {f}")
            print("\nRun: python -m tools.doc_sync --sync")
            return 1
        print(f"doc_sync --check: all {len(generated)} files up to date")
        return 0

    # Write files
    written = 0
    for stem, content in generated.items():
        filename = "index.md" if stem == "index" else f"{stem}.md"
        target_path = site_docs_dir / filename
        target_path.write_text(content, encoding="utf-8")
        written += 1

    print(f"doc_sync: wrote {written} files to site/docs/")
    if stale_files:
        print(f"  updated: {', '.join(stale_files)}")

    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("--sync", "--check"):
        print("Usage: python -m tools.doc_sync --sync|--check")
        return 1

    check_only = sys.argv[1] == "--check"
    return sync(check_only=check_only)


if __name__ == "__main__":
    sys.exit(main())
