# Levels of Autonomy for AI Coding Agents

**Author:** Jason Huxley
**Version:** 1.0
**Date:** March 2026
**Audience:** Engineering team

This document explains L4 and L5 agent autonomy, where the concepts come
from, and how the scaffolding in AETOS and Hades implements them.

---

## 1. The Framework

The Knight First Amendment Institute published a framework (Feng, McDonald
& Zhang, July 2025) defining five levels of AI agent autonomy. The levels
are built around a single question: what role does the human take when
interacting with the agent?

| Level | Human Role | What the Agent Does | Human Involvement | Empirical Signal |
|-------|-----------|---------------------|-------------------|------------------|
| **L1** | Operator | Assists on demand; human drives planning and execution | Continuous | -19% (METR 2025) |
| **L2** | Collaborator | Plans and executes alongside the human | Active, bidirectional | — |
| **L3** | Consultant | Drives planning and execution; consults the human for feedback | Periodic, advisory | 75–93% saving (internal, 2025–26) |
| **L4** | Approver | Runs autonomously; human intervenes only for blockers or sign-off | Gate-based | 90–99% saving (internal, 2025–26) |
| **L5** | Observer | Fully autonomous; human can monitor but not steer | Monitoring only | — |

The central point: **autonomy is a design decision, not a capability
consequence.** A capable agent can be constrained to L2 by the scaffolding
around it. A simpler agent can be given L5 autonomy over a well-scoped task.
The level is set by what you build around the agent, not by what the model
can do on its own.

Source: https://knightcolumbia.org/content/levels-of-autonomy-for-ai-agents-1

### Empirical context: what "AI assistance" actually produces without scaffolding

A July 2025 randomised controlled trial by METR (Becker, Rush, Barnes & Rein)
assigned 246 real issues from 16 experienced open-source developers either to
an AI-allowed condition (Cursor Pro with Claude 3.5 and 3.7 Sonnet) or an
AI-disallowed condition. **Developers in the AI-allowed condition took 19%
longer.** Before the study, those same developers had forecast a 24% speedup.
After experiencing the slowdown, they still believed AI had sped them up by 20%.

The study's scope is specific: experienced developers, high-quality codebases,
standard chat and autocomplete at L1. The scaffolding was a chat window. At
that level, the AI adds verification overhead and context-switching cost that
outweighs raw generation speed for developers who already know their codebase
well. The model is capable. The missing ingredient is how it is deployed.
Moving to L3, L4 or L5 is not just a matter of giving the agent more freedom;
it requires building the scaffolding that makes greater autonomy safe and
productive. That scaffolding is what converts the 19% slowdown into a net gain.

Source (RCT): https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
Paper: https://arxiv.org/abs/2507.09089

---

## 2. Huntley's Practitioner Continuum

Geoff Huntley (ghuntley.com) describes a related progression grounded in
how engineers actually work with AI agents. He does not use L1 through L5
labels. Instead he describes a continuum from consumer to factory:

| Stage | What It Means | Approximate Level |
|-------|---------------|-------------------|
| **Consumer** | Using Copilot or Cursor to speed up manual coding. Human types, AI assists. | L1 to L2 |
| **Multi-boxer** | Running several agent sessions at once on different tasks. Human supervises each. | L2 to L3 |
| **Ralph Looper** | Agent runs in a `while true` loop doing one bounded task per iteration. Human designs the loop. | L3 to L4 |
| **Orchestrator** | Multiple agents coordinated by an orchestrator. Spinning plates. (Steve Yegge's "Level 8") | L4 |
| **Software Factory** | Self-evolving, self-healing autonomous loops that ship, test and optimise. (Huntley's "Level 9") | L5 |

His anchor principle, from the Latent Patterns site:

> **"Humans on the loop, agents in the loop."** Software development is now
> automated. What is not, and cannot be, is taste, responsibility,
> accountability and customer satisfaction. These are irreducibly human. No
> agent has skin in the game. No model cares whether the customer is happy.
> Humans design the loops. Agents execute within them.

That is the idea connecting the academic framework to daily practice. At L4
and above, the engineer's job shifts from writing code to designing loops,
setting guardrails and exercising taste. The agent handles execution. The
human handles responsibility.

---

## 3. What L4 Looks Like (User as Approver)

At L4 the agent runs autonomously through execution, but the plan that
drives it is not purely the agent's creation. The plan comes from one of two
places: either the human writes a spec and hands it to the agent, or (more
commonly and more productively) the human and the agent develop the plan
together through discussion. The human brings taste, context and priorities.
The agent brings codebase knowledge, feasibility checks and structured
thinking. Once the plan is agreed, execution is the agent's job. It makes
lower-stakes decisions without asking. The human is only involved when the
agent hits something it cannot resolve: a failure state, missing credentials
or a consequential action that needs sign-off.

Before the agent starts executing, the human configures which actions need
approval. The agent proceeds unless it runs into a gate.

The risk at L4 is rubber-stamping. The human approves without reading. The
scaffolding must prevent that, not just hope for the best.

---

## 4. What L5 Looks Like (User as Observer)

At L5 the agent is fully autonomous. It plans, executes, iterates on
failures and delivers results. The human can read activity logs but does not
steer. The only direct control is an emergency off-switch.

The scaffolding at L4 exists to build toward L5. Every plugin, hook and
permission described in this document is infrastructure that replaces a human
gate with a structural one. As each layer proves it catches what the human
would have caught, the corresponding gate becomes redundant and gets removed.

Our systems currently operate at L4. The work is to progressively remove
human gates as the structural layers beneath them prove sufficient.

---

## 5. How Our Projects Implement L4

AETOS (the framework) and its consumer projects (Hades being the primary
example) implement L4 through layered scaffolding. No single mechanism is
enough. The safety comes from defence in depth across six enforcement
layers.

### 5.1 The Stack

```
Human (taste, accountability, approval gates)
  |
  +-- AGENTS.md (rules loaded into every session)
  |
  +-- OpenCode Plugins (deterministic enforcement at platform level)
  |     +-- guardrail-enforcer.ts    (blocks force-push, main commits, .env reads)
  |     +-- compaction-survival.ts   (re-injects critical rules on context reset)
  |     +-- session-observer.ts      (telemetry, failure detection, lifecycle)
  |     +-- pivot-notify.ts          (domain-specific post-action hooks)
  |
  +-- Git Hooks (pre-commit, commit-msg, pre-push)
  |     +-- Branch protection        (no commits to main)
  |     +-- Secrets scanning         (detect-secrets)
  |     +-- Conventional commits     (commit message format)
  |     +-- Test gate                (tests must pass before push)
  |     +-- Data file blocking       (no .db, .env, .jsonl in repo)
  |
  +-- Task-Centric Agent Hierarchy
  |     |
  |     +-- @aetos (orchestrator)
  |     |     tools: task, read, skill, question
  |     |     denied: edit, bash, all MCP servers
  |     |     delegates to: plan, test, code, git-ops, project-mgr, notify
  |     |
  |     +-- @aetos-plan (spec writer, Opus)
  |     |     tools: read, write, edit, bash, skill, question, webfetch
  |     |     denied: git MCP, PM MCP, notify MCP
  |     |
  |     +-- @aetos-test (TDD test writer, Sonnet)
  |     |     tools: read, write, edit, question
  |     |     bash: test runners only (pytest, npm test)
  |     |     denied: git MCP, PM MCP, notify MCP
  |     |
  |     +-- @aetos-code (implementation, Sonnet)
  |     |     tools: read, write, edit, bash, question
  |     |     edit denied: tests/*, test_*, *.test.*, *.spec.*
  |     |     bash denied: git *, gh *, curl *github*, curl *gitlab*
  |     |     denied: git MCP, PM MCP, notify MCP
  |     |
  |     +-- @git-ops (git porcelain, Haiku)
  |     |     tools: read, bash, question
  |     |     read denied: .git/*, .git/**
  |     |     bash: git status/log/diff/branch/add/commit/push only
  |     |     bash denied: git push --force, git push -f
  |     |     denied: memory MCP, PM MCP, notify MCP
  |     |
  |     +-- @project-mgr (issue lifecycle, Haiku)
  |     |     tools: read, question
  |     |     no bash, no edit, no write
  |     |     MCP: aetos-pm only
  |     |     denied: memory MCP, git MCP, notify MCP
  |     |
  |     +-- @notify (Slack/email/webhook, Haiku)
  |           tools: read, question
  |           no bash, no edit, no write, no glob, no grep
  |           MCP: aetos-notify only
  |           denied: memory MCP, git MCP, PM MCP
  |
  +-- MCP Servers (domain tools with embedded guards)
  |     +-- aetos-git     (12 tools: branch protection, PR-only merge)
  |     +-- aetos-pm      (21 tools: comment-before-close, one-in-Doing WIP limit)
  |     +-- aetos-notify  (4 tools: Slack ID validation)
  |     +-- aetos-memory  (8 tools: session memory)
  |     +-- aetos-codegraph (4 tools: function-level dependency graph)
  |
  +-- Skills (on-demand loaded workflows)
        +-- GOTCHA       (6-layer operating discipline)
        +-- ATLAS        (5-step build workflow, mandatory gate for 3+ file changes)
        +-- github-flow  (branch, PR and issue lifecycle)
```

### 5.2 Layer 1: AGENTS.md

`AGENTS.md` is loaded into every agent session automatically. It contains
build and test commands, git workflow rules, code style guidelines, mandatory
pre-flight checklists (ATLAS) and lessons learned from past failures.

This is **instructional** enforcement. The agent is told what to do. It works
most of the time, but instructions can be forgotten after context compaction
or ignored by a misbehaving model. AGENTS.md alone is not enough for L4. It
must be backed by structural enforcement.

OpenCode features used:

- **Rules** (`AGENTS.md`): loaded at session start (see https://opencode.ai/docs/rules/)
- **Instructions** (`opencode.json`, `instructions` field): additional rule files loaded alongside AGENTS.md

### 5.3 Layer 2: OpenCode Plugins

Plugins run at the OpenCode platform level. They intercept tool calls before
or after execution and can block, modify or extend behaviour. They are
TypeScript modules that subscribe to events.

This is **structural** enforcement. The agent cannot perform the blocked
action. No amount of prompt injection or model confusion can bypass a plugin
that throws an error before the tool executes.

**guardrail-enforcer.ts** fires on `tool.execute.before` and blocks:

| Blocked Action | Reason |
|----------------|--------|
| `git push --force` | Prevents history rewriting |
| Push, commit or merge to main/master | Branch protection; PR-only |
| `--no-verify` flag | Prevents git hook bypass |
| `git reset --hard` on protected branches | Prevents data loss |
| Reading `.env` files | Secrets must not enter the context window |
| Writing `"env"` instead of `"environment"` in opencode.json | Catches a config bug that silently breaks MCP token passthrough |
| `stage_and_commit` or `push_branch` on protected branches | Same protection extended to MCP git tools |

An agent that tries to force-push receives:

```
BLOCKED: Force push is prohibited by policy.
Use regular push or resolve conflicts with merge/rebase.
```

It sees the error and must comply. There is no workaround.

**compaction-survival.ts** fires on `experimental.session.compacting`. When
the context window fills and OpenCode compacts the conversation, rules can be
lost. This plugin scans agent templates, skill files and rules for
`compaction_survival` YAML frontmatter, extracts the critical strings and
injects them into the compacted context.

The AETOS orchestrator agent declares its survival rules like this:

```yaml
compaction_survival:
  - "### Hard Rules\n- AFTER EVERY PR: call question tool immediately...
     DO NOT skip. Has been skipped twice.\n- Run full test suite before
     committing..."
```

Without this plugin, long sessions forget hard rules. The MR Gate (section
6) was skipped twice before compaction survival was added.

**session-observer.ts** fires on `tool.execute.after`, `message.updated` and
`session.idle`. It tracks every tool call, detects failure patterns in agent
messages ("sorry", "I apologise", "my mistake"), records MCP guard triggers
and writes session telemetry to `.aetos/tracker/session-signals.jsonl`. It
also manages a context review lifecycle, triggering a review prompt after a
configurable number of sessions or days.

This is L4's monitoring layer. The human reviews session signals to see what
the agent did, what failed and whether guardrails fired.

**pivot-notify.ts** (Hades, ACP containers only) fires on
`tool.execute.after` for `hades_add_pivot`. After a pivot is recorded in the
database (success is already guaranteed by that point), the plugin dispatches
Slack notifications to collaborators. The agent is unaware this happened. If
notifications fail, the pivot is still safe.

This pattern matters for L4: the agent adds a pivot. The platform ensures
stakeholders are notified. The agent cannot forget or skip the notification
because it never had that responsibility.

Docs: https://opencode.ai/docs/plugins/

### 5.4 Layer 3: Git Hooks

Git hooks enforce constraints at the version control level. They fire for all
committers (human and agent) and do not depend on the agent's context or
instructions.

AETOS uses the `pre-commit` framework (`.pre-commit-config.yaml`) with hooks
across three stages:

**Pre-commit:**
- `no-commit-to-branch` blocks commits to main/master
- `check-added-large-files` blocks files over 500KB
- `detect-secrets` scans for leaked credentials against a baseline
- `no-data-files` blocks .db, .sqlite, .jsonl, .pyc, .env, venv/ and node_modules/
- `lint-opencode-json` catches the "env" vs "environment" config bug

**Commit-msg:**
- `conventional-pre-commit` enforces conventional commit format (feat, fix, refactor, docs, test, chore, release, ci, perf)

**Pre-push:**
- `branch-naming` enforces feature/\*, fix/\*, release/\* naming
- `pytest-check` runs the full test suite before push

Hades uses a custom pre-commit script (`scripts/pre-commit`) that
auto-increments the VERSION file and updates cache-busting query strings in
index.html.

The layering matters here. The guardrail-enforcer plugin blocks
`--no-verify`, which prevents the agent from bypassing git hooks. The hooks
then enforce their own constraints. Neither layer works on its own.

### 5.5 Layer 4: Agent Hierarchy (Task-Centric Agents)

AETOS agents are **task-centric**, not general-purpose. Each agent exists to
do one thing in a pipeline. It has access to the tools that thing requires
and nothing else. The agents are:

| Agent | Task | Model | Writes Code | Runs Bash | MCP Access |
|-------|------|-------|-------------|-----------|------------|
| **aetos** (orchestrator) | Decomposes work, delegates | Sonnet | No | No | None |
| **aetos-plan** | Writes specs from requirements | Opus | Yes (specs only) | Yes | None |
| **aetos-test** | Writes failing tests from spec | Sonnet | Yes (tests only) | Test runners only | None |
| **aetos-code** | Makes tests pass | Sonnet | Yes (not tests) | Yes (not git) | None |
| **git-ops** | Branch, commit, push, PR | Haiku | No | Git commands only | aetos-git |
| **project-mgr** | Issues, milestones, time | Haiku | No | No | aetos-pm |
| **notify** | Slack DMs, email, webhooks | Haiku | No | No | aetos-notify |

The orchestrator (`aetos.md`) cannot write code, run commands or call MCP
tools. It can only delegate to scoped subagents:

```yaml
tools:
  task: true       # Can delegate
  read: true       # Can read plans
  skill: true      # Can load skills
  edit: "deny"     # Cannot edit files
  bash: "deny"     # Cannot run commands
  aetos-git_*: false    # Cannot use git MCP directly
  aetos-pm_*: false     # Cannot use PM MCP directly
  aetos-notify_*: false # Cannot use notify MCP directly
permission:
  task:
    "*": "deny"           # Cannot invoke arbitrary agents
    "aetos-plan": "allow" # Can invoke the plan agent
    "aetos-test": "allow" # Can invoke the test agent
    "aetos-code": "allow" # Can invoke the code agent
    "git-ops": "allow"    # Can invoke the git agent
    "project-mgr": "allow"
    "notify": "allow"
    "explore": "allow"
```

#### Permission isolation in practice

Permissions do not just control which tools an agent can call. They control
what each tool can do, down to file paths, command patterns and MCP server
namespaces.

**aetos-code** (the implementation agent) can edit any file except tests:

```yaml
permission:
  edit:
    "*": "allow"
    "tests/*": "deny"
    "test/*": "deny"
    "test_*": "deny"
    "*_test.*": "deny"
    "*.test.*": "deny"
    "*.spec.*": "deny"
  bash:
    "*": "allow"
    "git *": "deny"
    "gh *": "deny"
    "curl *https://api.github*": "deny"
    "curl *https://gitlab*": "deny"
  aetos-git_*: "deny"
  aetos-pm_*: "deny"
  aetos-notify_*: "deny"
```

This means the code agent cannot modify test files (enforced structurally,
not by instruction), cannot run git commands, cannot call the GitHub/GitLab
APIs and cannot touch the PM or notification MCP servers. The TDD contract
is maintained by the runtime, not by the agent's good behaviour.

**aetos-test** (the test writer) can only run test runners:

```yaml
permission:
  bash:
    "*": "deny"
    "python *": "allow"
    "pytest *": "allow"
    "npm test*": "allow"
    "npx *": "allow"
    "venv/bin/pytest *": "allow"
  aetos-git_*: "deny"
  aetos-pm_*: "deny"
  aetos-notify_*: "deny"
```

It has no git access, no PM access, no notification access. It writes tests
and runs them. That is all.

**git-ops** can run a curated set of git commands and nothing else:

```yaml
permission:
  read:
    "*": "allow"
    ".git/*": "deny"
    ".git/**": "deny"
  bash:
    "*": "deny"
    "git status*": "allow"
    "git log*": "allow"
    "git diff*": "allow"
    "git branch*": "allow"
    "git checkout*": "allow"
    "git switch*": "allow"
    "git add*": "allow"
    "git commit*": "allow"
    "git push --force*": "deny"
    "git push -f *": "deny"
    "git push * --force*": "deny"
    "git push * -f *": "deny"
    "git push*": "allow"
    "git fetch*": "allow"
    "git pull*": "allow"
    "git stash*": "allow"
  aetos-memory_*: "deny"
  aetos-pm_*: "deny"
  aetos-notify_*: "deny"
```

It cannot read `.git/` (which may contain embedded tokens). It cannot run
non-git bash commands. Force-push patterns are denied explicitly even though
the guardrail-enforcer plugin also blocks them. The `.git/` directory deny
prevents the agent from reading `.git/config` where credentials may be
stored.

**project-mgr** and **notify** have no bash, no edit, no write. They
interact with the outside world exclusively through their respective MCP
servers. They cannot see each other's MCP tools.

#### Cross-MCP isolation

Every subagent explicitly denies access to MCP servers outside its remit.
The git-ops agent cannot create issues. The PM agent cannot send Slack
messages. The notify agent cannot commit code. This is declared in both the
agent markdown frontmatter and in `opencode.json`, providing two independent
enforcement points.

#### The pipeline

A typical significant task flows through the agents in sequence:

1. `@aetos` classifies the task and delegates to `@aetos-plan`
2. `@aetos-plan` explores the codebase, asks the user questions, writes a spec
3. `@aetos` delegates to `@project-mgr` to create issues from the spec
4. `@aetos` delegates to `@git-ops` to create a feature branch
5. `@aetos` delegates to `@aetos-test` to write failing tests from the spec
6. `@aetos` delegates to `@git-ops` to commit the tests (atomic)
7. For each code issue: `@aetos` delegates to `@aetos-code` to make tests pass
8. `@aetos` delegates to `@git-ops` to commit, push and create a PR
9. `@aetos` delegates to `@project-mgr` to close issues with comments
10. `@aetos` delegates to `@notify` to send the PR notification
11. `@aetos` calls the `question` tool to wait for merge confirmation

Each step is performed by an agent that can only do that step's work. The
orchestrator holds the pipeline together but cannot shortcut it.

Docs: https://opencode.ai/docs/agents/

### 5.6 Layer 5: MCP Servers

MCP (Model Context Protocol) servers provide domain-specific tools to agents.
AETOS ships five:

| Server | Tools | Guards |
|--------|-------|--------|
| aetos-memory | 8 | None |
| aetos-notify | 4 | Slack ID validation (rejects invalid contacts) |
| aetos-git | 12 | Branch protection, PR-only merge |
| aetos-pm | 21 | Comment-before-close, one-issue-in-Doing WIP limit |
| aetos-codegraph | 4 | None |

Guards are embedded in the tool implementations. When an agent tries to close
an issue without a comment, the MCP server returns:

```json
{"success": false, "error": "Cannot close issue without a comment"}
```

The agent must comply. It cannot reach around the MCP server to manipulate
the database directly because its bash access is denied by the permission
model.

Docs: https://opencode.ai/docs/mcp-servers/

### 5.7 Layer 6: Skills

Skills are markdown documents loaded via the `skill` tool when an agent needs
workflow guidance. They define structured processes:

- **GOTCHA** is a 6-layer operating discipline (Goals, Operations, Tools, Context, Hardprompts, Args) that defines how agents structure their work.
- **ATLAS** is a 5-step build workflow (Architect, Trace, Link, Assemble, Ship) and serves as a mandatory gate for any change touching three or more files.
- **github-flow** defines the branch, PR and issue lifecycle.

Skills are instructional, not structural. But they are backed by structural
enforcement. ATLAS is required by AGENTS.md, and the orchestrator's
compaction survival rules preserve the ATLAS requirement across context
resets.

Docs: https://opencode.ai/docs/skills/

---

## 6. The Approval Gates

The defining feature of L4 is that the human retains approval authority over
consequential actions. In our systems the gates are:

| Gate | Mechanism | When It Fires |
|------|-----------|---------------|
| **PR/MR review** | GitHub/GitLab PR workflow | Before any code reaches main |
| **MR Gate question** | `question` tool call from orchestrator | After every PR creation (hard rule, preserved by compaction survival) |
| **Permission prompts** | OpenCode permission system (`"ask"`) | Configurable per tool per agent |
| **Credentials** | Agent requests from human | When API keys or passwords are needed |
| **Scope expansion** | Slack notification plus human decision | When investigation scope could expand significantly |

The MR Gate deserves attention. The AETOS orchestrator has a hard rule,
preserved across compaction, that after creating a PR it must call the
`question` tool and wait for the human to confirm the merge. The workflow is
not complete until the human responds. This prevents the agent from creating
PRs and moving on without review.

Remove all the gates today and the system would be L5 without the
scaffolding to support it. The gates are what keep it at L4 until the
underlying enforcement layers are strong enough to make the gates redundant.
The goal is to reach the point where each gate can be removed because the
structural layers beneath it already catch everything the human would have
caught.

---

## 7. Defence in Depth

No single layer is enough. The table below shows which layers catch which
threats:

| Threat | AGENTS.md | Plugin | Git Hook | Agent Scope | MCP Guard |
|--------|-----------|--------|----------|-------------|-----------|
| Agent pushes to main | Instructed not to | Blocks push | Blocks commit | git-ops scoped | git MCP blocks |
| Agent commits secrets | Instructed not to | Blocks .env read | detect-secrets | | |
| Agent bypasses hooks | Instructed not to | Blocks --no-verify | | bash denied | |
| Agent forgets rules after compaction | | compaction-survival | | | |
| Agent closes issue without comment | | | | | MCP rejects |
| Agent force-pushes | Instructed not to | Blocks --force | | bash denied | git MCP blocks |
| Agent runs too long without review | | session-observer | | | |

Most threats are caught by two or three layers. That is the L4 contract: if
one mechanism fails, others catch it.

---

## 8. OpenCode Features Reference

Every OpenCode feature used in this scaffolding. Docs for all features:
https://opencode.ai/docs/

| Feature | What It Does for L4 |
|---------|---------------------|
| **Rules** (AGENTS.md) | Instructional constraints loaded every session |
| **Agents** | Scoped delegation with tool and permission restrictions |
| **Permissions** | Granular deny/ask/allow per tool per agent |
| **Plugins** | Deterministic enforcement via tool.execute.before/after hooks |
| **Skills** | On-demand workflow loading with compaction survival |
| **MCP Servers** | Domain tools with embedded business logic guards |
| **ACP** | Agent Client Protocol for IDE and container integration |
| **Compaction hooks** | Preserve critical rules when context is compacted |
| **Custom tools** | Extend agent capabilities with controlled tools |

---

## 9. What Changes for Engineers

Moving from L1/L2 (human writes code, AI assists) to L4 (agent writes code,
human approves) changes what engineering work looks like:

| | L1/L2 (Copilot era) | L4 (Orchestrated agents) |
|---|---|---|
| **What you write** | Application code | AGENTS.md, plugins, hooks, agent configs, MCP servers |
| **What you review** | AI suggestions inline | PRs, session telemetry, guard trigger logs |
| **What you design** | Features | Loops, guardrails, approval gates, delegation hierarchies |
| **What you debug** | Runtime errors | Agent behaviour, missed guardrails, compaction amnesia |
| **Where time goes** | Writing code | Designing scaffolding, reviewing output, refining constraints |

This is Huntley's principle in practice. The engineer's job becomes designing
the system that produces correct code, not writing the code directly.

---

## 10. The Adversarial Reviewer Pattern

The AETOS agent hierarchy in section 5.5 is built around task isolation: each
agent does one thing and cannot do another agent's thing. Every agent in the
pipeline is cooperative. It exists to produce. There is no structural voice
for restraint. The adversarial reviewer pattern adds one.

### 10.1 The Problem It Solves

LLM agents have an eagerness bias. The primary agent reflects the user's
enthusiasm back instead of checking it. In a cooperative pipeline where every
agent exists to produce output, this bias compounds at each step.

Two concrete failure modes in our projects:

**AETOS: spec inflation.** The plan agent (`@aetos-plan`, Opus) adds features
the user did not ask for. It overspecifies edge cases, proposes abstractions
for single-use code and inflates scope. The test agent writes tests for all
of it. The code agent implements all of it. Nobody in the pipeline said "this
was not requested." The human sees a spec that looks thorough and approves it
without noticing the scope drift.

**Hades: investigation scope creep.** An investigation agent proposes
expanding scope into a tangentially related area. The findings look
interesting. The human approves. The expansion produces noise that dilutes
the original findings and consumes time that should have gone to the primary
line of inquiry. The agent chased a tangent because it was interesting, not
because it was warranted.

In both cases the agent is doing its job. The problem is that no agent in the
pipeline has the job of saying "stop."

### 10.2 The Design

The reviewer is a subagent with three structural properties:

1. **Read-only.** It cannot write files, edit files, run commands or call
   external APIs. It can only read documents and return judgement. It cannot
   act on its own recommendations.

2. **Adversarial by instruction.** Its system prompt assumes the user and
   primary agent are too eager. Its default bias is toward restraint. "Do
   less" is always a valid recommendation. It has explicit veto power.

3. **Scoring-based.** It evaluates proposed output against weighted criteria
   specific to the domain, each scored 1 to 5. Any score of 1 is an
   automatic veto. Total below a configured threshold is a veto. This makes
   the decision process auditable and consistent.

```yaml
# Reviewer agent definition (OpenCode subagent)
mode: subagent
model: anthropic/claude-sonnet-4-6
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
  webfetch: false
```

The low temperature (0.1) reduces variance in scoring. The tool denials are
structural: the reviewer cannot bypass them regardless of what its prompt
says.

### 10.3 Scoring Rubrics

The criteria change depending on what is being reviewed.

**AETOS spec review** (after `@aetos-plan`, before PM setup):

| Criterion | What It Measures |
|-----------|-----------------|
| Scope fidelity | Does the spec match what the user asked for, or has the plan agent added unrequested features? |
| Testability | Can `@aetos-test` write failing tests from this spec alone, without seeing implementation? |
| Complexity | Is the change proportionate to the request? |
| Risk awareness | Does the spec acknowledge high-risk areas (schemas, auth, public API surface)? |
| Completeness | Are edge cases and error paths specified? |

Veto threshold: any criterion scoring 1, or total below 15/25.

**Hades investigation review** (before scope expansion or direction change):

| Criterion | What It Measures |
|-----------|-----------------|
| Evidential basis | Is the proposed action supported by findings so far? |
| Scope discipline | Does the action stay within the investigation brief? |
| Proportionality | Is the effort justified by the expected value? |
| Risk | Does the action risk alerting the subject, burning a source or triggering a dead end? |
| Redundancy | Has this ground already been covered? |

Veto threshold: any criterion scoring 1, or total below 15/25.

### 10.4 Where It Fits in the Pipeline

**AETOS:** The reviewer gates step 2.5 in the TDD pipeline, after plan and
before PM setup. The orchestrator delegates to `@aetos-review` with the spec
file path and the user's original request.

- On **PASS**: continue to step 3 (PM setup).
- On **AMEND**: re-delegate to `@aetos-plan` with the reviewer's specific
  feedback. Re-run the review. Maximum two review cycles before surfacing to
  the user.
- On **VETO**: surface the reviewer's reasoning to the user via the `question`
  tool. The user decides whether to override, revise or abandon.

**Hades:** The reviewer gates scope expansion and direction-changing pivots.
Before the investigation agent records a pivot or proposes broadening the
scope, the orchestrator delegates to the reviewer with the current brief, the
evidence collected so far and the proposed action.

The human can override a veto in both cases. When this happens, the
reviewer's reasoning and the user's justification are both logged to the
memory system. This creates an audit trail. If overrides become frequent, the
review criteria need tightening.

### 10.5 How This Differs From Task-Centric Agents

AETOS agents are task-centric: plan, test, code, git-ops, PM, notify. Each
does a job in a pipeline. The reviewer is not task-centric. It is
judgement-centric. It exists to oppose, not to produce.

| | AETOS Subagent | Adversarial Reviewer |
|---|---|---|
| **Purpose** | Produce output (code, tests, commits) | Evaluate and constrain output |
| **Relationship to primary** | Cooperative, delegated | Adversarial, structurally opposed |
| **Tool access** | Scoped to task (edit, bash, MCP) | Read-only, no action tools |
| **Bias** | Toward completion | Toward restraint |
| **Output** | Artifacts (files, PRs, issues) | Judgement (pass/amend/veto with scores) |

Any point where the pipeline's cooperative momentum might override good
judgement is a candidate for an adversarial gate.

### 10.6 Structural Properties

The reviewer pattern has three properties that make it useful for L4
scaffolding:

1. **It cannot rubber-stamp.** The scoring rubric forces evaluation of each
   criterion. A reviewer that returns "PASS" with all 5s is visibly not
   doing its job. The structured output makes lazy approval detectable.

2. **It cannot act.** Even if the reviewer's instructions were corrupted by
   prompt injection (via content in a document it was asked to evaluate), it
   has no tools to cause harm. Read-only is a hard constraint.

3. **The human retains override.** The reviewer is not a blocker that halts
   the pipeline permanently. The human can override, but must do so
   explicitly and on the record. This preserves L4's defining property
   (human as approver) while adding a structural check that the human must
   actively dismiss rather than passively ignore.

### 10.7 Origin and Validation

The pattern originated in a separate public advocacy project where an agent
assisted with social media engagement. The specific failure: 12 posts from a
new account in a single day, including repeated project link drops and
promotional pitches. The agent drafted all of them and never recommended
restraint. Neither the human nor the agent could be trusted to self-regulate
when receiving positive engagement signals.

The review criteria were retrospectively applied to the 12 posts. Result:
3 PASS, 2 AMEND, 7 VETO. The reviewer would have allowed the three general
commentary posts, required modifications to two borderline posts and blocked
seven outright (volume breaches, pattern repetition, uninvited project
promotion, account age risk). That is the correct outcome and validated the
pattern for adoption into AETOS and Hades.

---

## 11. Takeaways

1. **Autonomy is a dial, not a switch.** The same agent runs at different
   levels depending on the scaffolding around it.

2. **Instructions are necessary but not sufficient.** AGENTS.md tells the
   agent what to do. Plugins, hooks and permissions ensure it actually does
   it.

3. **Defence in depth is not optional at L4.** Any single enforcement
   mechanism will eventually fail. Layer them.

4. **Compaction is the quiet failure mode.** Long sessions lose context.
   The compaction-survival plugin exists because this was observed in
   practice: the MR Gate was skipped twice before survival rules were added.

5. **The orchestrator pattern creates accountability.** An orchestrator that
   cannot write code (only delegate) produces scoped, auditable workflows
   by construction.

6. **Post-action hooks beat pre-action instructions.** The pivot-notify
   plugin is more reliable than telling the agent to remember to send a
   Slack notification after adding a pivot.

7. **Git hooks catch what agents miss.** They fire for everyone, need no
   context and cannot be forgotten.

8. **Start at L2, earn L4.** Add autonomy incrementally as you build
   confidence in your guardrails. Each layer you add lets you safely hand
   the agent more rope.
