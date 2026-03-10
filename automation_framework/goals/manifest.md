# Goals Manifest

> Index of process definitions. Each goal describes a repeatable workflow.
> Add new goals as campaign activities are formalised.

## Active Goals

- **Social agent** (`goals/social_agent.md`) — Sandboxed social network interface for posting, metrics and notifications across Bluesky, Mastodon and Reddit. Runs as a containerised MCP server (`services/social_mcp/`).
- **Social engagement** (`goals/social_engagement.md`) — Process for managing SEBE social media presence with mandatory adversarial review gates. Two-layer review: session plans and per-action scoring for SEBE-mentioning content. Uses `hardprompts/social_review.md`.
- **Blog tagging** (`goals/blog_tagging.md`) — Tag blog posts by topic and difficulty level with visual badges. Pure CSS, no JavaScript.

- **Document sync** (`goals/doc_sync.md`) — Single source of truth for docs/. Build script generates site/docs/ with Jekyll front matter, HTML links, grouped index page. Pre-commit hook enforces header conformance and freshness.

## Planned

- Green Party submission workflow
- Think tank outreach process
- Conference motion campaign
- Media/press engagement process

---

*Update this file when creating or retiring goals.*
