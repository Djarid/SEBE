"""
PDF text extraction tool for the SEBE automation framework.

Extracts text from PDF files (local or URL) for analysis. Useful for
processing government reports, ORR statistics, ONS publications, etc.

Requires: pymupdf (pip install pymupdf)

Run from automation_framework/:
    python -m tools.pdf_reader --file <path_or_url> [options]

Actions:
    text        Extract all text (default)
    pages       Extract text from specific pages
    search      Search for text within the PDF
    info        Show PDF metadata and page count
"""

import argparse
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    import pymupdf
except ImportError:
    print("ERROR: pymupdf not installed. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


# ── Helpers ────────────────────────────────────────────────────────────

def fetch_pdf(url: str) -> Path:
    """Download a PDF from a URL to a temp file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SEBE/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            tmp.write(resp.read())
        tmp.close()
        return Path(tmp.name)
    except Exception as e:
        tmp.close()
        raise RuntimeError(f"Failed to download PDF: {e}")


def open_pdf(file_path: str) -> tuple:
    """Open a PDF from a local path or URL. Returns (doc, temp_path_or_none)."""
    temp_path = None
    if file_path.startswith("http://") or file_path.startswith("https://"):
        temp_path = fetch_pdf(file_path)
        doc = pymupdf.open(str(temp_path))
    else:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        doc = pymupdf.open(str(path))
    return doc, temp_path


def cleanup(temp_path):
    """Remove temp file if it exists."""
    if temp_path and temp_path.exists():
        temp_path.unlink()


# ── Actions ────────────────────────────────────────────────────────────

def action_info(file_path: str) -> dict:
    """Show PDF metadata and page count."""
    doc, temp = open_pdf(file_path)
    try:
        meta = doc.metadata
        return {
            "success": True,
            "pages": len(doc),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
            "creation_date": meta.get("creationDate", ""),
        }
    finally:
        doc.close()
        cleanup(temp)


def action_text(file_path: str, max_pages: int = 0) -> dict:
    """Extract all text from the PDF."""
    doc, temp = open_pdf(file_path)
    try:
        pages = []
        limit = len(doc) if max_pages == 0 else min(max_pages, len(doc))
        for i in range(limit):
            page = doc[i]
            text = page.get_text()
            if text.strip():
                pages.append({
                    "page": i + 1,
                    "text": text.strip(),
                })
        return {
            "success": True,
            "total_pages": len(doc),
            "extracted_pages": len(pages),
            "pages": pages,
        }
    finally:
        doc.close()
        cleanup(temp)


def action_pages(file_path: str, page_nums: list) -> dict:
    """Extract text from specific pages (1-indexed)."""
    doc, temp = open_pdf(file_path)
    try:
        pages = []
        for num in page_nums:
            idx = num - 1
            if 0 <= idx < len(doc):
                page = doc[idx]
                text = page.get_text()
                pages.append({
                    "page": num,
                    "text": text.strip(),
                })
            else:
                pages.append({
                    "page": num,
                    "error": f"Page {num} out of range (1-{len(doc)})",
                })
        return {
            "success": True,
            "total_pages": len(doc),
            "pages": pages,
        }
    finally:
        doc.close()
        cleanup(temp)


def action_search(file_path: str, query: str) -> dict:
    """Search for text within the PDF."""
    doc, temp = open_pdf(file_path)
    try:
        results = []
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text()
            if query.lower() in text.lower():
                # Find surrounding context for each match
                lines = text.split("\n")
                for j, line in enumerate(lines):
                    if query.lower() in line.lower():
                        context_start = max(0, j - 1)
                        context_end = min(len(lines), j + 2)
                        context = "\n".join(lines[context_start:context_end])
                        results.append({
                            "page": i + 1,
                            "line": j + 1,
                            "context": context.strip(),
                        })
        return {
            "success": True,
            "query": query,
            "matches": len(results),
            "results": results,
        }
    finally:
        doc.close()
        cleanup(temp)


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PDF text extraction for SEBE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  info        Show PDF metadata and page count
  text        Extract all text (default)
  pages       Extract text from specific pages
  search      Search for text within the PDF

Examples:
  python -m tools.pdf_reader --file report.pdf --action info
  python -m tools.pdf_reader --file report.pdf --action text --max-pages 5
  python -m tools.pdf_reader --file report.pdf --action pages --page-nums 1 3 5
  python -m tools.pdf_reader --file report.pdf --action search --query "revenue"
  python -m tools.pdf_reader --file https://example.com/report.pdf --action text
        """,
    )
    parser.add_argument(
        "--file", required=True,
        help="Path to PDF file or URL",
    )
    parser.add_argument(
        "--action", default="text",
        choices=["info", "text", "pages", "search"],
        help="Operation to perform (default: text)",
    )
    parser.add_argument(
        "--max-pages", type=int, default=0,
        help="Maximum pages to extract (0 = all, default: 0)",
    )
    parser.add_argument(
        "--page-nums", type=int, nargs="+",
        help="Specific page numbers to extract (1-indexed)",
    )
    parser.add_argument(
        "--query",
        help="Search query (for search action)",
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Output raw text only (no JSON wrapper)",
    )
    args = parser.parse_args()

    try:
        if args.action == "info":
            result = action_info(args.file)
        elif args.action == "text":
            result = action_text(args.file, max_pages=args.max_pages)
        elif args.action == "pages":
            if not args.page_nums:
                print("ERROR: --page-nums required for pages action", file=sys.stderr)
                sys.exit(1)
            result = action_pages(args.file, args.page_nums)
        elif args.action == "search":
            if not args.query:
                print("ERROR: --query required for search action", file=sys.stderr)
                sys.exit(1)
            result = action_search(args.file, args.query)
        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}

        if args.raw and args.action in ("text", "pages"):
            # Output just the text, no JSON
            for page in result.get("pages", []):
                if "text" in page:
                    print(f"\n--- Page {page['page']} ---\n")
                    print(page["text"])
        else:
            status = "OK" if result.get("success") else "ERROR"
            print(f"{status}", file=sys.stderr)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
