# Tools Manifest

> Index of deterministic tools available in the automation framework.
> Each tool is a standalone Python module with a CLI interface.
> Run from `automation_framework/` with the venv active.

## Available Tools

### fiscal_calc

Tax and distribution calculator. Verifies SEBE revenue figures, models
tax burdens, distribution costs, welfare offsets and ULI derivation.

```bash
python -m tools.fiscal_calc                        # Full model summary
python -m tools.fiscal_calc --action tax --gross 45000
python -m tools.fiscal_calc --action distribute --adult-rate 10000
python -m tools.fiscal_calc --action uli
python -m tools.fiscal_calc --action full --json
```

### git_remote

Git remote operations (push, pull, status, sync). Reads credentials
from `.env` at repo root. Never displays tokens in output.

```bash
python -m tools.git_remote --action status
python -m tools.git_remote --action push
python -m tools.git_remote --action sync
```

### memory

Persistent memory system (SQLite + Markdown dual-write). Manages facts,
tasks, contacts, interactions and session logs.

```bash
python -m tools.memory.reader                      # Load session context
python -m tools.memory.writer --content "fact" --type fact --importance 7
python -m tools.memory.db --action list-tasks --status pending
python -m tools.memory.db --action search --query "Green Party"
python -m tools.memory.export --format markdown
```

### pdf_reader

PDF text extraction and search. Works with local files and URLs.
Requires pymupdf.

```bash
python -m tools.pdf_reader --file report.pdf --action info
python -m tools.pdf_reader --file report.pdf --action text
python -m tools.pdf_reader --file report.pdf --action search --query "revenue"
```

### social

Sandboxed social network agent. Runs as a subprocess with credential
isolation (credentials never cross the process boundary). Supports
Bluesky, Mastodon and Reddit.

```bash
echo '{"command":"auth_test","platform":"bsky"}' | python -m tools.social
echo '{"command":"post","platform":"bsky","text":"Hello"}' | python -m tools.social
echo '{"command":"get_profile","platform":"bsky"}' | python -m tools.social
echo '{"command":"get_notifications","platform":"bsky"}' | python -m tools.social
echo '{"command":"get_post_metrics","platform":"bsky","post_id":"at://..."}' | python -m tools.social
echo '{"command":"delete_post","platform":"bsky","post_id":"at://..."}' | python -m tools.social
```

Commands: `auth_test`, `post`, `get_profile`, `get_notifications`,
`get_post_metrics`, `delete_post`. Platforms: `bsky`, `mastodon`, `reddit`.
Full documentation: `goals/social_agent.md`.

### web_search

SearXNG search client. Requires SearXNG running on localhost:8888
(`podman start sebe-searxng`).

```bash
python -m tools.web_search "Green Party policy working groups"
python -m tools.web_search "SEBE tax" --limit 5 --json
python -m tools.web_search "automation jobs UK" --categories news
```

---

*Update this file when adding or retiring tools.*
