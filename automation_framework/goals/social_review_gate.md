# Social Engagement Review Gate — ATLAS Design

**Author:** Jason Huxley
**Date:** 2026-03-01
**Version:** v0.1
**Status:** Design phase

---

## A — Architect

### Problem

Eagerness bias in social media engagement. The primary agent (Claude)
reflects the user's enthusiasm back instead of checking it, leading to
overexposure, pattern detection risk, and community reputation damage.
12 comments on a brand new Reddit account in one day is the specific
failure that prompted this.

### User

Jason Huxley. Eager, ADHD, needs external braking mechanism. Will not
reliably self-regulate posting frequency or volume, especially when
receiving positive engagement signals.

### Success Criteria

1. No social media action containing a SEBE mention, link, or policy
   pitch is posted without independent review
2. No engagement session begins without a reviewed plan
3. The reviewer is adversarial by design: assumes eagerness, enforces
   patience, has veto power
4. False negatives (letting bad posts through) are worse than false
   positives (blocking good posts)

### Constraints

- Must work within the existing opencode agent architecture
- Review must be fast enough to not kill conversational flow (under
  60 seconds per review)
- Reviewer must not have access to post directly (review only, no
  action)
- Must work for Reddit, Bluesky, Mastodon, and any future platform

---

## T — Trace

### Architecture

```
User wants to engage on social media
            |
            v
    +------------------+
    | Layer 1:         |
    | Session Plan     |
    | (drafted by      |
    |  primary agent)  |
    +--------+---------+
             |
             v
    +------------------+
    | Review Agent      |
    | (adversarial)     |
    | Approves/rejects/ |
    | modifies plan     |
    +--------+---------+
             |
             v
    Approved plan governs session
             |
             v
    For each proposed action:
             |
    Is it general commentary? -----> Post without review
             |
    Contains SEBE/link/pitch? -----> Layer 2 review
             |                              |
             v                              v
    +------------------+         +------------------+
    | Draft comment     |         | Review Agent      |
    | presented to user |         | Scores against    |
    |                   |         | 7 criteria        |
    +------------------+         +--------+---------+
                                          |
                                 PASS: post it
                                 AMEND: modify and re-review
                                 VETO: do not post
```

### Review Criteria (scored 1-5 each, veto if any score is 1)

1. **Account health**
   - Account age vs platform norms
   - Current karma/follower count
   - Recent posting volume (24h, 7d, 30d)
   - Any prior flags, shadowbans, or removed posts

2. **Volume control**
   - Comments this session
   - SEBE-mentioning comments this session
   - SEBE-mentioning comments this week
   - Link drops this week
   - Maximum: 2 SEBE comments per day, 5 per week, 1 link per day

3. **Pattern detection**
   - Is the same argument appearing in multiple threads?
   - Is the same link being dropped repeatedly?
   - Are comments structurally similar (AI-generated uniformity)?
   - Would a hostile observer see astroturfing?

4. **Timing**
   - Hours since last SEBE comment on this platform
   - Hours since last comment in this specific thread
   - Has the other party had time to respond?
   - Minimum 24h between SEBE comments in same subreddit

5. **Tone and authenticity**
   - Does this read as a person with an opinion or a campaign?
   - Is the language varied from previous SEBE comments?
   - Is it responding to the specific conversation or pasting a pitch?
   - Would it pass the "new community member" test?

6. **Invitation**
   - Was SEBE's topic area explicitly raised by another commenter?
   - Is there a direct question that SEBE answers?
   - Or are we inserting SEBE into an unrelated conversation?
   - Uninvited SEBE pitches score 1 (automatic veto) unless the
     thread topic is directly about automation taxation or UBI funding

7. **Risk assessment**
   - Could this trigger spam detection?
   - Could this damage relationships with identified contacts?
   - Could this get the account banned or shadowbanned?
   - What is the worst-case interpretation of this comment?

### Session Plan Template

```markdown
## Social Engagement Plan — [date]

### Platform: [Reddit/Bluesky/Mastodon]
### Account: [username]
### Account state:
- Age: [days]
- Karma/followers: [number]
- Last SEBE comment: [date, thread]
- Comments this week: [total / SEBE-mentioning]

### Goal: [karma building / general presence / SEBE engagement / reply to existing thread]

### Proposed actions:
1. [thread/post] — [type: general comment / SEBE reply / link drop]
2. ...

### Constraints:
- Max SEBE comments this session: [number]
- Links allowed: [yes/no]
- Tone: [conversational / technical / political]

### Review decision: [APPROVED / MODIFIED / REJECTED]
### Reviewer notes: [...]
```

### Hardprompt for Review Agent

```
You are the social engagement reviewer for the SEBE project. Your role
is adversarial. You assume the user and primary agent are too eager and
your job is to enforce patience and strategic discipline.

You are reviewing a proposed social media action. Score it against all
7 criteria (1-5 each). Any score of 1 is an automatic veto.

Your biases should be:
- LESS is more. Fewer, better comments beat volume.
- Silence is an option. "Don't post" is a valid recommendation.
- Reputation compounds slowly and collapses fast.
- A brand new account should spend its first month listening.
- Links and policy pitches are high-risk actions that need strong
  justification.
- Being invited into a conversation is 10x more valuable than
  inserting yourself.

You have veto power. Use it. The user can override you but must
acknowledge the override explicitly.

Output format:
1. Account health: [score] — [reason]
2. Volume: [score] — [reason]
3. Pattern: [score] — [reason]
4. Timing: [score] — [reason]
5. Tone: [score] — [reason]
6. Invitation: [score] — [reason]
7. Risk: [score] — [reason]

Overall: [PASS / AMEND / VETO]
Notes: [specific recommendations]
```

---

## L — Link (Validation)

```
[ ] Review agent can be invoked from primary agent session
[ ] Review agent has no write/edit/bash tools (read-only + judgement)
[ ] Hardprompt produces consistent scoring format
[ ] Session plan template captures all necessary state
[ ] Volume tracking integrates with memory system (query recent
    SEBE comments by date)
[ ] Override mechanism works (user acknowledges veto, proceeds anyway,
    override is logged)
```

---

## A — Assemble (Implementation)

### Components

1. **Hardprompt file:** `automation_framework/hardprompts/social_review.md`
   Contains the adversarial reviewer instructions and scoring criteria.

2. **Session plan goal:** `automation_framework/goals/social_engagement.md`
   Defines the process for planning and executing a social engagement
   session, including mandatory review gates.

3. **Memory integration:** Review decisions logged via memory writer.
   Volume queries use `memory.db --action search` to count recent
   SEBE comments.

4. **Override logging:** If the user overrides a veto, log it with
   the reviewer's reasoning and the user's justification. This creates
   an audit trail for learning.

### Build Order

1. Write the hardprompt (reviewer instructions)
2. Write the session plan goal
3. Test with a dry run (propose yesterday's 12 comments through the
   reviewer and see how many survive)
4. Integrate into daily workflow

---

## S — Stress-test

### Dry Run: Yesterday's Comments Through the Gate

Apply the review criteria to all 12 comments posted on 2026-03-01.
Expected outcome: 2-3 approved, 9-10 vetoed or deferred.

```
[ ] r/ukpolitics #1 (Labour captive party): PASS (general commentary,
    no SEBE, no link)
[ ] r/ukpolitics #2 (Green pivot): PASS (general commentary)
[ ] r/ukpolitics #3 (Why? question): PASS (general commentary)
[ ] Necro-post (funding ideas): VETO (necro on 4yr thread, no value)
[ ] GCCS thread #1 (initial SEBE intro): PASS (first SEBE mention of
    day, relevant thread, link included — borderline)
[ ] GCCS thread #2 (offshoring reply): VETO (second SEBE comment same
    thread same day)
[ ] GCCS thread #3 (asset tax reply): VETO (third SEBE comment same
    thread same day)
[ ] GCCS thread #4 (Santens MMT reply): VETO (fourth SEBE comment
    same thread same day)
[ ] GCCS thread #5 (natural monopolies): AMEND (good content, remove
    SEBE mention, post as political commentary)
[ ] Citi thread (full pitch): VETO (second link drop of day, account
    too new)
[ ] Block thread (Santens post): VETO (third link drop of day)
[ ] Defeatism thread (jgs952 reply): AMEND (good content but SEBE
    mention in a thread where it was not invited)
```

Result: 3 PASS, 2 AMEND, 7 VETO. That feels about right.

### Ongoing Tests

```
[ ] Reviewer correctly vetoes a comment when daily SEBE limit reached
[ ] Reviewer correctly passes general commentary without SEBE content
[ ] Reviewer catches structural similarity between two proposed comments
[ ] Reviewer vetoes uninvited SEBE insertion
[ ] Override mechanism logs correctly
[ ] Volume tracking accurately counts SEBE comments from memory
```
