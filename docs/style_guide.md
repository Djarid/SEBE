# SEBE Writing Style Guide

**Author:** Jason Huxley
**Version:** 1.0
**Date:** February 2026

This guide applies to all SEBE documents (policy submissions, academic
briefs, public explainers, campaign materials) and to AI-generated drafts
including daemon email responses. Every agent session should enforce these
rules.

---

## 1. Language and Spelling

- **British English throughout:** labour, defence, realise, colour, programme,
  analyse, centre, metre (but meter for measuring devices), licence (noun),
  license (verb)
- **No Americanisms:** "gotten", "math", "oftentimes", "utilize" are all wrong.
  Use "got", "maths", "often", "use".
- **Oxford comma:** Do not use. Write "energy, bandwidth and data" not
  "energy, bandwidth, and data".
- **Numbers:** Spell out one to nine in prose. Use figures for 10 and above,
  all monetary amounts, all percentages, and all technical quantities.
  Write "three components" but "£31 billion" and "12 TWh".

---

## 2. Punctuation

- **No em dashes in prose.** Do not use `---`, `—`, or ` - ` as
  parenthetical separators. Ever.
- **Use parentheses** (like this) or **commas** for asides and interjections.
- **Hyphens** only for:
  - Compound modifiers before a noun: "post-employment economy",
    "age-banded supplements", "self-scaling mechanism"
  - List markers in markdown (`- item`)
  - Ranges in tables or technical contexts: "£200-800/TB"
- **Colons** to introduce lists, explanations, or elaborations. Lowercase
  after a colon unless the next word is a proper noun.
- **Semicolons** sparingly, to join closely related independent clauses.
  If in doubt, use a full stop instead.

---

## 3. Tone and Register

### 3.1 General Principles

- **Direct and precise.** Say what you mean. Do not hedge with "perhaps",
  "it could be argued that", or "some might say".
- **Technically confident.** SEBE is a worked proposal with sourced figures,
  not a speculative think-piece. Write accordingly.
- **No sycophancy.** Do not praise the reader, flatter institutions, or
  express gratitude for being allowed to submit. State the case.
- **No waffle.** Every sentence must carry information. If you can delete a
  sentence without losing meaning, delete it.

### 3.2 By Document Type

| Document | Register | Audience |
|---|---|---|
| Green Party submission | Formal policy language, references to PSS | PDC, Economy Working Group |
| Academic brief | Academic but accessible, sourced claims | Think tanks (IPPR, NEF), researchers |
| Public explainer | Plain English, short sentences, no jargon | General public, press |
| Daemon email drafts | Professional but not stiff, concise | Varies (party members, researchers, public) |
| Cost model / revenue model | Technical, precise, show all workings | Internal reference, reviewers |

### 3.3 Words and Phrases to Avoid

| Avoid | Use Instead | Reason |
|---|---|---|
| comprehensive | thorough, detailed, full | AI writing tell |
| robust | strong, solid, resilient | AI writing tell |
| utilize | use | Americanism and pompous |
| leverage (as verb) | use, exploit, apply | Corporate jargon |
| stakeholders | people affected, parties involved | Vague corporate-speak |
| going forward | from now, henceforth, (or delete) | Filler |
| in terms of | (rephrase the sentence) | Filler |
| it should be noted that | (delete; just state the thing) | Throat-clearing |
| it is important to | (delete; just state the thing) | Throat-clearing |
| comprehensive analysis | analysis (it's either analysis or it isn't) | Redundant modifier |
| holistic | (delete or rephrase) | Meaningless buzzword |
| ecosystem | system, network, sector | Unless referring to actual ecology |
| synergy | (rephrase) | Corporate jargon |
| paradigm shift | change, transformation | Overused to the point of emptiness |

---

## 4. AI Writing Tells

AI-generated text has recognisable patterns. All drafts (daemon emails,
document sections, briefs) must be checked for these before publication.

### 4.1 Structural Tells

- **Tricolon habit:** AI loves groups of three ("efficient, effective, and
  equitable"). Break up or reduce to two where three is gratuitous.
- **Mirrored sentence openings:** AI tends to start consecutive paragraphs
  with the same structure. Vary your openings.
- **Excessive hedging:** "This could potentially help to address some of
  the challenges" instead of "This addresses the problem". Be direct.
- **Summary-then-detail pattern:** AI always gives a summary sentence then
  elaborates. Real writers sometimes lead with the detail.

### 4.2 Lexical Tells

- Overuse of "comprehensive", "robust", "holistic", "leverage", "ecosystem"
- "Importantly" or "crucially" at sentence start (just state the importance)
- "It is worth noting that" (delete it; note it by saying it)
- "This is particularly relevant because" (just explain why)
- "In this context" (usually deletable)

### 4.3 The Test

Read the text aloud. If it sounds like a management consultant's slide
deck, rewrite it. If it sounds like a human being explaining something
they understand and care about, it's probably fine.

---

## 5. Formatting

### 5.1 Markdown Conventions

- **Headers:** ATX-style (`#`, `##`, `###`) with clear hierarchy. Never
  skip levels (no `##` followed immediately by `####`).
- **Section numbering:** Decimal system (1.1, 1.2, 2.1) in formal
  documents (submission, academic brief). No numbering in the public
  explainer.
- **Bold** for key terms on first use, amounts, and conclusions.
- **Italic** for emphasis (sparingly) and publication titles.
- **Lists:** Bullet (`-`) for unordered lists, numbered (`1.`) for
  sequences or ranked items.
- **Tables:** Pipe-delimited, with header row. Use for structured
  comparisons and data.
- **Separators:** `---` between major sections.
- **Line length:** No hard wrap in markdown source. Let the renderer
  handle line breaks.

### 5.2 Document Metadata

Every formal document must include at the top:
- Title
- Author
- Date
- Version number
- Target audience

Every formal document must end with:
```
---
*Copyright 2026 Jason Huxley. Licensed under CC-BY 4.0.*
```

### 5.3 File Naming

- `snake_case.md` for all files
- Policy documents in `docs/`
- Technical specs in `technical/`
- No spaces in filenames

---

## 6. SEBE-Specific Terminology

### 6.1 Correct Terms

| Term | Definition | Notes |
|---|---|---|
| SEBE | Sovereign Energy & Bandwidth Excise | Always expand on first use per document |
| SEE | Sovereign Energy Excise | The energy component |
| DCD | Digital Customs Duty | The bandwidth component (border tariff) |
| UBI | Universal Basic Income | Stage 1 payment |
| ULI | Universal Living Income | Stage 2 payment (preferred over "UBI" when discussing Stage 2) |
| UBS | Universal Basic Services | Free energy, transport, broadband, mobile |
| HRoT | Hardware Root of Trust | Metering system for SEE |

### 6.2 Revenue Figures

**Always use the corrected figures from `docs/revenue_model.md`:**

- SEBE launch (2030): **£34-46 billion** (2026 prices, CPI-indexed rates)
- SEE component: £26-34B
- DCD component: £8-12B
- Growth: £93B by 2040, £159B by 2045 (2026 prices)
- All projections in **2026 real prices**; nominal will be higher
- Stage 1 UBI launch: **~£690/adult/year** (not £2,500 from day one)
- Stage 1 UBI target: **£2,500/adult/year** (reached as revenue grows)
- Stage 2 ULI: **£29,000/adult/year**

If you are unsure of a figure, check `revenue_model.md` or run
`python -m tools.fiscal_calc`. Do not guess.

### 6.3 What DCD Is and Is Not

- DCD **is** a border tariff on commercial cross-border data
- DCD **is not** a general bandwidth tax on all internet traffic
- Consumers **are exempt** from DCD (and all SEBE)
- Domestic data centre traffic **is exempt** from DCD (it pays SEE instead)
- DCD incentivises compute repatriation to the UK

Get this wrong and the proposal becomes politically indefensible. Every
document must be clear that ordinary people do not pay SEBE.

---

## 7. Citation and Sources

- Cite sources inline: "(ONS ASHE 2025)" or "(OBR Nov 2023 EFO)"
- For revenue figures, reference `revenue_model.md` with section numbers
- For cost/distribution figures, reference `distribution_model.md` or `cost_model.md`
- Never invent statistics. If a figure is not sourced, flag it as
  "[source needed]" rather than fabricating a citation
- Stale data should be noted: "Stale after [date] when [new release]
  publishes"

---

## 8. Checklist Before Publication

Before any document is submitted, emailed, or published:

1. [ ] British English throughout (no Americanisms)
2. [ ] No em dashes in prose
3. [ ] No AI writing tells (Section 4)
4. [ ] All revenue figures match `revenue_model.md`
5. [ ] DCD correctly described as border tariff (not bandwidth tax)
6. [ ] Consumer exemption stated clearly
7. [ ] Stage 1 ramp described (not £2,500 from day one)
8. [ ] Sources cited for all statistics
9. [ ] CC-BY 4.0 notice at end (formal documents)
10. [ ] Version number incremented if document was previously published

---

*Copyright 2026 Jason Huxley. Licensed under CC-BY 4.0.*
