# SEBE Project - AI Agent Interaction Guide

## Repository Overview

**Project:** Sovereign Energy & Bandwidth Excise (SEBE)
**Author:** Jason Huxley
**Type:** Policy proposal + automation framework
**License:** CC-BY 4.0
**Status:** Active development, targeting Green Party policy adoption

UK policy proposal for taxing automation infrastructure (energy consumption
and data throughput) to fund Universal Basic Income at £30,000/year for all
UK citizens. Revenue estimate: £200-500 billion/year.

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
│   └── public_explainer.md                # Plain-language public version
├── technical/                             # Future specs/code
└── automation_framework/
    ├── goals/                             # Process definitions
    │   └── manifest.md                    # Index of goals
    ├── tools/                             # Deterministic scripts
    │   ├── git_remote.py                  # Git remote ops (push/pull/status)
    │   └── memory/                        # Memory system (Python)
    │       ├── config.py, db.py, reader.py, writer.py, export.py
    │       └── __init__.py
    ├── context/                           # Domain knowledge
    │   ├── project_context.md             # SEBE policy context (tracked)
    │   ├── author_context.md              # Author context (gitignored)
    │   └── convo_summary.md               # History (gitignored)
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

### Document Metadata
Every formal document: Title, Author, Date, Version, Target audience.
Every formal document ends with CC-BY 4.0 copyright notice.

### Content Standards
- Include revenue estimates in all policy documents
- Be specific: numbers, sources, mechanisms
- Version control explicitly (v1.0, v1.1)

## Git Conventions

- **Branch:** `main`
- **No remote configured** — local-only currently
- **Never commit:** `.env`, `author_context.md`, `convo_summary.md`, `data/`, `memory/logs/`, `MEMORY.md`
- **Do commit:** Policy documents, `project_context.md`, tools code, this file

## Key SEBE Parameters

| Parameter | Value |
|---|---|
| ULI payment | £30,000/person/year |
| UBS value | £2,000/person/year |
| Combined living standard | £32,000/person/year |
| Total requirement (67M) | £2.144 trillion/year |
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
