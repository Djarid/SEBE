# SEBE Project Context

**Version:** 1.0
**Updated:** February 14, 2026

This file provides agents with full SEBE policy context, technical details,
strategic positioning, arguments/rebuttals, and current project status.

---

## The SEBE Proposal

### Core Concept

**Sovereign Energy & Bandwidth Excise (SEBE):** Tax automation infrastructure
instead of human labour. Two components:

**1. Sovereign Energy Excise (SEE):** Tax commercial electricity consumption
- Coverage: Facilities >500kW IT load
- Hardware Root of Trust (HRoT) metering at three points:
  - Point of Generation (PoG): Grid/private generation ingress
  - Point of Storage (PoS): Battery systems (prevents temporal arbitrage)
  - Point of Load (PoL): Actual consumption at infrastructure
- Reconciliation prevents "dark compute"
- Rates: £0.05-0.30/kWh (tiered by consumption)

**2. Digital Customs Duty (DCD):** Tax corporate data throughput
- Implementation at Internet Exchange Points (IXP level)
- BGP Community Tagging (identifies commercial traffic at Tier-1 gateways)
- SNI-based metadata filtering (distinguishes commercial from personal)
- Role Margin Protocol: Baseline quota per SIC code, tax excess
- Offshore compute penalty: 2x domestic rate (incentivises UK datacenter investment)
- Rates: £25-50/Mbps sustained (offshore 2x)

### Revenue Model

**Estimated: £200-500 billion/year** (20-50% of current UK tax revenue)

Scale comparison:
- Income Tax: £250B — SEBE comparable
- National Insurance: £170B — SEBE exceeds
- VAT: £160B — SEBE exceeds
- Corporation Tax: £100B — SEBE exceeds

**SEBE becomes UK's largest or second-largest revenue source.**

### Distribution: UBI + UBS

**Universal Living Income (ULI):** £30,000/person/year
- Based on: Median wage (£32,890) minus personal UBS costs (£2,000)
- Just below median = "generous but believable"
- 67 million people: £2.010 trillion/year

**Universal Basic Services (UBS):** £2,000/person/year value
- Free public transit, utilities (to threshold), communications (to threshold)
- Infrastructure cost: £134 billion/year

**Combined living standard: £32,000/year equivalent**
**Total requirement: £2.144 trillion/year**

### Funding the Full Package

SEBE alone (£200-500B) covers 9-23% of requirement. Full UBI requires:
- SEBE: £200-500B (major component)
- Wealth tax: £50-80B
- Land Value Tax: £50-100B
- Financial Transaction Tax: £20-50B
- MMT framework: Sovereign currency flexibility as automation increases productivity

**Optional defence ring-fence:** 20% of SEBE (£40-100B) for strategic autonomy.
Reduces ULI to £28-29k but funds complete UK defence independence.

---

## Technical Feasibility

**VPN/Encryption does NOT hide bandwidth consumption:**
- ISP sees total throughput at border regardless of encryption
- BGP routing reveals destination country
- Non-UK endpoint = 2x tax applies
- Gaming is harder than current tax evasion (can't hide physical infrastructure)

**Wealth exit is irrelevant:**
- SEBE taxes fixed assets (datacenters, infrastructure) that CAN'T leave
- Rich person leaves → datacenter stays → revenue continues
- Tax the physical layer (immobile) not people (mobile)
- This is why SEBE works where wealth taxes don't

---

## Arguments & Rebuttals

**"Stifles innovation / companies will flee!"**
- Physical datacenters can't easily move
- Offshore compute taxed at 2x (cheaper to stay in UK)
- UK market access valuable (67M consumers with £30k/year)
- "Welcome to leave — we'll tax their products when they sell here"

**"Economically illiterate / unaffordable!"**
- £200-500B is real revenue from measurable physical activity
- Current system (taxing vanishing workers) is the illiterate approach
- MMT: Constraint is inflation (productivity) not money supply

**"People will stop working!"**
- Evidence shows otherwise (Alaska PFD, Finland/Kenya pilots)
- Meaningful work increases when survival not at stake
- Job Guarantee alternative = coercive state labour

**"Inflation will destroy it!"**
- SEBE withdraws £200-500B from corporations (anti-inflationary)
- Real constraint is production capacity
- Automation increases capacity → no inflation if productivity gains realised

**"Technically impossible / will be gamed!"**
- HRoT metering, physical infrastructure measurement
- Easier than chasing offshore shell companies
- Three-point reconciliation prevents dark compute

---

## Political Strategy

### Green Party Context (Feb 2026)
- Membership: 195,000 (tripled since Sept 2025, 2nd or 3rd largest)
- Polling: 14.1% nationally
- MRP projection: 9 seats (from 4)
- Leader Polanski: Most popular leader (approval -1)
- Coalition probability 2029: 20-30%

### SEBE as Coalition Tool
- Greens demand UBI in coalition → need credible funding mechanism
- SEBE provides it (£200-500B demonstrable revenue)
- Positions Greens as serious party with implementable policy

### UK Strategic Context
- US dollar collapse likely 60-70% by 2028
- UK needs 4-5% GDP defence (£120-150B) for independence
- SEBE with 20% ring-fence = £100B defence + £30k UBI
- Funds both social security AND national security

---

## Three Publication Versions

**1. Green Party Policy Submission** (`docs/green_party_submission.md`)
- 16 sections, EC code alignment, coalition strategy
- Defence ring-fence option, 5-year phased rollout
- Target: Policy Development Committee, Economy Working Group, Autumn 2026

**2. Academic/Think Tank Brief** (`docs/academic_brief.md`)
- No party political framing, economic analysis focus
- Technical feasibility, research agenda (acknowledges gaps)
- Target: IPPR, NEF, economics journals

**3. Public Explainer** (`docs/public_explainer.md`)
- "Tax robots, fund people" — simple language
- Real-world examples, common questions, call to action
- Target: General public, media, campaign literature

All three use: £30k UBI, £32k total with UBS, £200-500B revenue,
honest framing as major component of progressive tax package.

---

## Current Status

### Completed
- Technical specification (HRoT metering, BGP/SNI enforcement)
- Green Party aligned version (EC codes, coalition strategy)
- Three publication versions (party, academic, public)
- Submission to Bedford party (awaiting response)

### In Progress
- Building support within Green Party
- Academic publication (targeting IPPR, NEF)
- Public engagement (git repo, social media via proxy)

### Implementation Plan

**Week 1:** Git public commit, email Bedford party + policy@greenparty.org.uk,
submit to IPPR/NEF, local press pitch

**Week 2:** Call Green HQ (020 7272 4474), attend Bedford meeting,
start newsletter (Substack/Medium), find social media proxy

**Week 3:** Build coalition, submit working paper, media pitches,
gather conference motion signatures

**Week 4:** Consolidate support, refine on feedback, plan conference strategy

**Long-term:** Young Greens coalition (40k), conference motion Autumn 2026
(need 200+ signatures), Polanski engagement, official platform for 2028

### Attribution Strategy
1. Git repo with timestamp (permanent public record)
2. Academic working paper series (formal citable credit)
3. CC-BY-4.0 license (anyone can use, must credit)
4. "Huxley's SEBE framework" in all communications
5. Technical depth = indispensable expert positioning

---

## Agent Task Categories

**Policy Development:** Economic modelling, counter-arguments, implementation
timelines, international comparisons, revenue projections.

**Communication:** Simplify technical concepts for public/media, formalise for
academic publication, structure presentations for party meetings, draft
correspondence.

**Strategic:** Green Party navigation, media strategy, coalition building,
timeline planning.

**Technical:** Infrastructure implementation details (metering, networking),
security analysis (evasion prevention), scalability assessment.

---

## Output Standards

When producing documents or analysis:
1. Provide complete, publication-ready output — not drafts or fragments
2. Include specific numbers and mechanisms, not vague generalities
3. Acknowledge uncertainties honestly
4. Mark document versions explicitly (v1.0, v1.1, etc.)
5. End formal documents with CC-BY 4.0 notice
6. Provide actionable next steps with each deliverable

---

**The role is to help execute, not educate. Certa Cito.**
