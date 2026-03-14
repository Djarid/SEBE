# Goals Manifest

> Index of process definitions. Each goal describes a repeatable workflow.
> Add new goals as campaign activities are formalised.

## Active Goals

- **Social agent** (`goals/social_agent.md`) — Sandboxed social network interface for posting, metrics and notifications across Bluesky, Mastodon and Reddit. Runs as a containerised MCP server (`services/social_mcp/`).
- **Social engagement** (`goals/social_engagement.md`) — Process for managing SEBE social media presence with mandatory adversarial review gates. Two-layer review: session plans and per-action scoring for SEBE-mentioning content. Uses `hardprompts/social_review.md`.
- **Blog tagging** (`goals/blog_tagging.md`) — Tag blog posts by topic and difficulty level with visual badges. Pure CSS, no JavaScript.

- **Conversation archive** (`goals/conversation_archive.md`) — Import, search, tag, and export multi-platform conversation logs. WhatsApp parser, full-text search, Chatham House Rule anonymisation.
- **Document sync** (`goals/doc_sync.md`) — Single source of truth for docs/. Build script generates site/docs/ with Jekyll front matter, HTML links, grouped index page. Pre-commit hook enforces header conformance and freshness.
- **PDF generation** (`goals/pdf_generation.md`) — Convert markdown documents to styled A4 PDFs using pandoc + pdflatex. EB Garamond, dark blue headings, running headers, editorial note boxes, CC-BY 4.0 footer. Single file or batch mode.
- **DOCX generation** (`goals/docx_generation.md`) — Convert markdown documents to styled A4 DOCX using pandoc + reference template. Dark blue headings, Cambria font, clean tables. For review, commenting, and distribution to external stakeholders. Single file or batch mode.

## Planned

- Green Party submission workflow
- Think tank outreach process
- Conference motion campaign
- Media/press engagement process

---

*Update this file when creating or retiring goals.*
