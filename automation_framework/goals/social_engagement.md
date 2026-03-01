# Goal: Social Engagement

## Objective

Manage SEBE's social media presence across Reddit, Bluesky, Mastodon
and future platforms. Build organic credibility, engage with UBI and
policy communities, and introduce SEBE where appropriate, subject to
mandatory review gates.

## Review Gates (mandatory, no exceptions)

This process has two mandatory review layers. Skipping either is a
protocol violation.

### Layer 1: Session Plan

Before any engagement session, the primary agent drafts a session plan
and submits it for adversarial review.

**Plan template:**

```markdown
## Social Engagement Plan — [date]

### Platform: [Reddit/Bluesky/Mastodon]
### Account: [username]
### Account state:
- Age: [days since creation]
- Karma/followers: [current count]
- Last SEBE comment: [date, platform, thread]
- SEBE comments this week: [count]
- Link drops this week: [count]

### Goal:
[karma building / general presence / SEBE engagement / reply to thread]

### Proposed actions:
1. [thread URL or description] — [general comment / SEBE reply / link]
2. ...

### Constraints:
- Max SEBE comments this session: [0-2]
- Links allowed: [yes/no, max 1]
- Tone: [conversational / technical / political]
```

**Review process:**
1. Primary agent drafts the plan
2. Plan is reviewed using `hardprompts/social_review.md` criteria
3. Reviewer returns APPROVED, MODIFIED, or REJECTED
4. If MODIFIED, primary agent adjusts plan and proceeds
5. If REJECTED, no engagement this session

### Layer 2: Per-Action Review

During the session, any proposed comment that contains any of:
- The word "SEBE" or "Sovereign Energy"
- A URL or link
- Revenue figures (£ amounts)
- A policy pitch or technical description of the mechanism

...must be individually reviewed before the user posts it.

**Review process:**
1. Primary agent drafts the comment
2. Comment is reviewed using `hardprompts/social_review.md` scoring
3. Reviewer returns PASS, AMEND, or VETO
4. If AMEND, reviewer specifies changes, agent redrafts, re-review
5. If VETO, comment is not posted

**Exempt from per-action review:**
- General political commentary (no SEBE content)
- Questions to other users
- Upvoting, following, subscribing
- Reading notifications and threads

### Override Protocol

The user can override a veto. When this happens:
1. The reviewer's reasoning is read aloud
2. The user explicitly acknowledges the veto and states why they
   are overriding
3. The override is logged to memory with both the reviewer's reasoning
   and the user's justification
4. The comment is posted

Overrides should be rare. If overrides become frequent, the review
criteria need tightening.

## Account Strategy

### u/SEBEPolicy (Reddit, official)
- Purpose: SEBE policy engagement only
- Tone: technically confident, conversational, not promotional
- Never used for general political commentary unrelated to SEBE
- Subject to all review gates

### u/West_Jellyfish_4860 (Reddit, personal)
- Purpose: general political commentary, community participation
- Can discuss SEBE but subject to same review gates when doing so
- Primary use: karma building, general engagement

### jasonhuxley.bsky.social (Bluesky)
- Purpose: SEBE and general political engagement
- Subject to review gates for SEBE content

## Volume Limits (hard, non-negotiable)

| Metric | Limit |
|--------|-------|
| SEBE comments per day (per platform) | 2 |
| SEBE comments per week (per platform) | 5 |
| Link drops per day (all platforms) | 1 |
| Link drops per week (all platforms) | 3 |
| SEBE comments per thread per day | 1 |
| Total comments per day (new account, <30d) | 5 |
| Total comments per day (established, >30d) | 10 |

## Engagement Principles

### Phase 1: Listening (account age 0-30 days)
- Primary activity: read, upvote, comment on others' posts
- No SEBE links
- SEBE mentions only when directly relevant and invited
- Maximum 1 SEBE mention per week
- Goal: build karma to 100+, establish presence as a person

### Phase 2: Participating (account age 30-90 days)
- Begin introducing SEBE where relevant
- Maximum 2 SEBE mentions per week with links
- Engage in debates when invited
- Reply to challenges substantively
- Goal: become a recognised contributor

### Phase 3: Advocating (account age 90+ days)
- Full engagement within volume limits
- Create original posts if karma allows
- Cross-post between relevant subs
- Build relationships with key contacts
- Goal: SEBE is known in the UBI/policy community

### Current Phase: 1 (Listening)

Account u/SEBEPolicy was created 2026-03-01. Phase 1 constraints apply
until 2026-04-01 at earliest.

**Note:** Phase 1 was violated on day 1 (12 comments, multiple links,
multiple SEBE pitches). The review gate exists to prevent this
recurring. The week of 2026-03-02 to 2026-03-08 should be SEBE-silent
on Reddit to recover.

## Memory Integration

### Before each session:
```bash
# Check recent SEBE engagement
python -m tools.memory.db --action search --query "Reddit engagement"
```

### After each session:
```bash
# Log all SEBE-mentioning comments
python -m tools.memory.writer --content "[details]" --type fact --importance 6
```

### After each review:
```bash
# Log review decisions (especially vetoes and overrides)
python -m tools.memory.writer --content "[review decision]" --type fact --importance 7
```

## Contact Protocols

| Contact | Platform | Approach | Constraints |
|---------|----------|----------|-------------|
| Scott Santens (u/2noame) | Reddit | Ally, engage on UBI funding | No pitching, respond when engaged |
| Jamie Smith (u/jgs952) | Reddit | Potential ally, fiscal sovereignty common ground | Do NOT discuss Job Guarantee |
| Xeke2338 | Reddit | Sparring partner, complementary project | One reply per exchange, wait for his responses |

## Files

- Review hardprompt: `hardprompts/social_review.md`
- ATLAS design: `goals/social_review_gate.md`
- Social agent (MCP): `goals/social_agent.md`
- Reddit post drafts: `hardprompts/reddit_post.md`
