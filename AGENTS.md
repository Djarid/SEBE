# SEBE Project - AI Agent Interaction Guide

## Repository Overview

**Project:** Sovereign Energy & Bandwidth Excise (SEBE)
**Author:** Jason Huxley
**Type:** Policy proposal + automation framework
**License:** CC-BY 4.0
**Status:** Active development, targeting Green Party policy adoption

UK policy proposal for taxing automation infrastructure (energy consumption
and data throughput) to fund a two-stage transition from Universal Basic
Income (£2,500/adult/year) to Universal Living Income (£29,000/adult/year).
Revenue estimate: £200-500 billion/year. Stage 1 is fully fundable from
SEBE alone.

## Session Start Protocol

**At the start of every session, run:**

```bash
source .venv/bin/activate
python -m tools.memory.reader
```

Run from `automation_framework/`. This loads MEMORY.md, recent daily logs,
pending tasks, and contacts awaiting follow-up.

If the venv doesn't exist: `python3 -m venv .venv && pip install -r requirements.txt`

**Then read these context files:**
- `automation_framework/context/project_context.md` — SEBE policy details (always)
- `automation_framework/context/author_context.md` — Author preferences (when available)

## Context Files

| File | Contents | Git Status |
|---|---|---|
| `context/project_context.md` | SEBE technical details, revenue model, arguments/rebuttals, political strategy | **Tracked** |
| `context/author_context.md` | Author background, communication style, key positions | **Gitignored** |
| `context/convo_summary.md` | Conversation development history | **Gitignored** |

## Repository Structure

```
SEBE/
├── AGENTS.md                              # This file
├── LICENCE                                # CC-BY 4.0
├── .gitignore                             # Excludes: .env, .venv/
├── docs/
│   ├── green_party_submission.md          # Green Party policy submission
│   ├── academic_brief.md                  # Academic/think-tank version
│   ├── public_explainer.md                # Plain-language public version
│   ├── cost_model.md                      # Full cost workings, two-stage model
│   └── glossary.md                        # Terminology definitions
├── technical/                             # Future specs/code
└── automation_framework/
    ├── goals/                             # Process definitions
    │   └── manifest.md                    # Index of goals
    ├── tools/                             # Deterministic scripts
    │   ├── git_remote.py                  # Git remote ops (push/pull/status)
    │   ├── pdf_reader.py                  # PDF text extraction (local/URL)
    │   ├── fiscal_calc.py                 # Fiscal calculator (tax/distribution/offsets)
    │   └── memory/                        # Memory system (Python)
    │       ├── config.py, db.py, reader.py, writer.py, export.py
    │       └── __init__.py
    ├── context/                           # Domain knowledge
    │   ├── project_context.md             # SEBE policy context (tracked)
    │   ├── author_context.md              # Author context (gitignored)
    │   └── convo_summary.md               # History (gitignored)
    ├── services/                           # Daemon orchestration (containerised)
    │   ├── __init__.py
    │   ├── config.py                      # Daemon config, .env loader
    │   ├── llm_client.py                  # LLM client + model swap manager
    │   ├── orchestrator.py                # Main polling loop + approval queue
    │   ├── Containerfile                  # Orchestrator container image
    │   ├── podman-compose.yml             # Full pod (orchestrator + bridge + signal)
    │   ├── .env.template                  # Credential template (safe to commit)
    │   └── channels/                      # Channel adapters
    │       ├── __init__.py
    │       ├── base.py                    # Base channel interface
    │       ├── email_channel.py           # Proton Bridge IMAP/SMTP
    │       └── signal_channel.py          # signal-cli REST adapter
    ├── hardprompts/                        # Reusable prompt templates
    ├── args/                              # Behaviour settings
    │   └── defaults.yaml
    ├── memory/                            # Human-readable memory files
    │   ├── MEMORY.md                      # Curated persistent facts
    │   └── logs/                          # Daily session logs
    ├── data/                              # SQLite databases (gitignored)
    ├── requirements.txt
    └── .gitignore
```

## Build / Lint / Test Commands

**Memory system (run from `automation_framework/`):**

```bash
# Activate venv
source .venv/bin/activate

# Load session context
python -m tools.memory.reader

# Write a memory entry (dual-write: log + SQLite)
python -m tools.memory.writer --content "fact here" --type fact --importance 7

# Add a task
python -m tools.memory.db --action add-task --title "Email IPPR" --priority high

# Add a contact
python -m tools.memory.db --action add-contact --name "Bedford Chair" --org "Green Party"

# Log an interaction
python -m tools.memory.db --action log-interaction --contact-id 1 --channel email --direction outbound --subject "SEBE submission"

# Search memory
python -m tools.memory.db --action search --query "Green Party"

# List pending tasks
python -m tools.memory.db --action list-tasks --status pending

# Export for backup
python -m tools.memory.export
python -m tools.memory.export --format markdown

# Stats
python -m tools.memory.db --action stats
```

**Git remote (run from `automation_framework/`):**

```bash
# Check remote config and sync state
python -m tools.git_remote --action status

# Configure origin from .env credentials
python -m tools.git_remote --action add-remote

# Push current branch to origin
python -m tools.git_remote --action push

# Pull from origin
python -m tools.git_remote --action pull

# Push then pull (convenience)
python -m tools.git_remote --action sync
```

Credentials read from `.env` at repo root (GITHUB_TOKEN, GITHUB_USER, GITHUB_REPO).
Tokens are never displayed in output.

**Fiscal calculator (run from `automation_framework/`):**

```bash
# Full model summary with current defaults (Stage 1)
python -m tools.fiscal_calc

# Tax burden on a specific income
python -m tools.fiscal_calc --action tax --gross 45000

# Distribution cost for a specific adult rate
python -m tools.fiscal_calc --action distribute --adult-rate 10000

# What-if: UBI at £5,000 with 2% population growth
python -m tools.fiscal_calc --action distribute --adult-rate 5000 --pop-growth 2

# Full Stage 2 model
python -m tools.fiscal_calc --action full --adult-rate 29000

# Derive ULI from median earnings
python -m tools.fiscal_calc --action uli

# JSON output for piping
python -m tools.fiscal_calc --action full --json
```

LLMs are language models, not calculators. **Always verify fiscal
arithmetic with this tool before committing figures to documents.**

**PDF reader (run from `automation_framework/`):**

```bash
# Show PDF metadata and page count
python -m tools.pdf_reader --file report.pdf --action info

# Extract all text
python -m tools.pdf_reader --file report.pdf --action text

# Extract specific pages
python -m tools.pdf_reader --file report.pdf --action pages --page-nums 1 3 5

# Search within PDF
python -m tools.pdf_reader --file report.pdf --action search --query "revenue"

# Works with URLs
python -m tools.pdf_reader --file https://example.com/report.pdf --action text

# Raw text output (no JSON wrapper)
python -m tools.pdf_reader --file report.pdf --action text --raw
```

Requires pymupdf (`pip install pymupdf`). Handles local files and URLs.

No other build/lint/test tools. Policy documents are Markdown only.

## Document Style Guidelines

### File Naming
- Use `snake_case.md` for all files
- Policy documents in `docs/`, technical specs in `technical/`

### Markdown Formatting
- **Headers:** ATX-style (`#`, `##`, `###`) with clear hierarchy
- **Section numbering:** Decimal system (1.1, 1.2) in formal documents
- **Emphasis:** Bold for key terms, amounts, conclusions
- **Lists:** Bullet (`-`) unordered, numbered (`1.`) for sequences
- **Tables:** Pipe-delimited for structured data
- **Separators:** `---` between major sections
- **British English:** labour, defence, realise, colour

### Punctuation
- **No em dashes** in prose. Do not use `—` or ` - ` as parenthetical separators.
- Use **parentheses** (like this) or **commas** for asides and interjections.
- Hyphens only for compound modifiers (e.g. "post-employment") and list markers.

### Document Metadata
Every formal document: Title, Author, Date, Version, Target audience.
Every formal document ends with CC-BY 4.0 copyright notice.

### Content Standards
- Include revenue estimates in all policy documents
- Be specific: numbers, sources, mechanisms
- Version control explicitly (v1.0, v1.1)

## Git Conventions

- **Branch:** `main`
- **Remote:** `origin` on GitHub (credentials in `.env`)
- **Never commit:** `.env`, `author_context.md`, `convo_summary.md`, `data/`, `memory/logs/`, `MEMORY.md`
- **Do commit:** Policy documents, `project_context.md`, tools code, this file

## Key SEBE Parameters

| Parameter | Value |
|---|---|
| Stage 1 UBI (adult) | £2,500/adult/year |
| Stage 2 ULI (adult) | £29,000/adult/year |
| Children's supplements | £3,500-5,000/year (age-banded) |
| UBS value | £2,500/person/year |
| Combined living standard (Stage 2) | £31,500/person/year |
| Stage 1 total cost | ~£352 billion/year |
| Stage 2 total cost | ~£1.810 trillion/year |
| SEBE revenue target | £200-500 billion/year |
| Coverage threshold | Commercial facilities >500kW IT load |
| Energy rates (SEE) | £0.05-0.30/kWh (tiered) |
| Bandwidth rates (DCD) | £25-50/Mbps sustained |
| Offshore compute penalty | 2x domestic rate |

## Working With the Author — Summary

Full details in `context/author_context.md` (when available locally).

- Infrastructure/automation engineer and decorated Royal Signals veteran
- 7+ years developing SEBE — knows the subject deeply
- Values: technical precision, intellectual honesty, structured follow-through
- Needs: ADHD-compatible workflows, clear action steps, honest pushback
- Opposes: sycophancy, oversimplification, neoliberal framing, Job Guarantee

**The role is to help execute, not educate. Certa Cito.**
