"""
SEBE Web Search — SearXNG JSON API client.

Searches the web via a local SearXNG instance. Returns structured results
for use by agents and the orchestrator daemon.

Usage (CLI):
    python -m tools.web_search "query here"
    python -m tools.web_search --query "query" --engines google,duckduckgo
    python -m tools.web_search --query "query" --limit 5 --json

Usage (library):
    from tools.web_search import search
    results = search("Green Party policy working groups", limit=10)

Requires: SearXNG running at http://localhost:8888 (see services/searxng/)
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from typing import Optional


SEARXNG_URL = "http://localhost:8888/search"


def search(
    query: str,
    engines: Optional[str] = None,
    categories: Optional[str] = None,
    language: str = "en-GB",
    limit: int = 10,
) -> dict:
    """Search the web via local SearXNG instance.

    Args:
        query: Search query string.
        engines: Comma-separated engine names (e.g. "google,duckduckgo").
        categories: Comma-separated categories (e.g. "general,news,science").
        language: Search language (default en-GB).
        limit: Maximum number of results to return.

    Returns:
        dict with "success", "query", "results" (list of dicts with
        title, url, content), and "count".
    """
    params = {
        "q": query,
        "format": "json",
        "language": language,
    }
    if engines:
        params["engines"] = engines
    if categories:
        params["categories"] = categories

    url = f"{SEARXNG_URL}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "results": [],
            "count": 0,
        }

    results = []
    for r in data.get("results", [])[:limit]:
        results.append(
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "engine": r.get("engine", ""),
            }
        )

    return {
        "success": True,
        "query": query,
        "results": results,
        "count": len(results),
    }


def main():
    parser = argparse.ArgumentParser(description="SEBE Web Search (SearXNG)")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument(
        "--query", "-q", dest="query_flag", help="Search query (alternative)"
    )
    parser.add_argument("--engines", "-e", help="Comma-separated engines")
    parser.add_argument("--categories", "-c", help="Comma-separated categories")
    parser.add_argument(
        "--language", "-l", default="en-GB", help="Language (default: en-GB)"
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=10, help="Max results (default: 10)"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    query = args.query or args.query_flag

    if not query:
        parser.error("query required")

    result = search(query, args.engines, args.categories, args.language, args.limit)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if not result["success"]:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

        print(f"Results for: {result['query']} ({result['count']})")
        print()
        for i, r in enumerate(result["results"], 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            if r["content"]:
                print(f"   {r['content'][:200]}")
            print()


if __name__ == "__main__":
    main()
