# SEBE Project Context

**Version:** 3.0
**Updated:** February 15, 2026

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
- Rates: £0.08-0.45/kWh (tiered by consumption)

**2. Digital Customs Duty (DCD):** Border tariff on commercial cross-border data
- Implementation at Internet Exchange Points (IXP level)
- BGP Community Tagging (identifies commercial traffic at Tier-1 gateways)
- SNI-based metadata filtering (distinguishes commercial from personal)
- Applies to data crossing UK digital border (both directions)
- Consumers exempt, domestic DC-to-DC traffic exempt (pays SEE on energy)
- Incentivises compute repatriation to UK (where operators pay SEE instead)
- Rates: £200-800/TB tiered by annual volume

### Revenue Model

**Year 1 (2030 launch): £34-46 billion** (2026 prices, SEE £26-34B, DCD £8-12B)
**Growth trajectory:** £93B by 2040, £159B by 2045 (mid-scenario, 2026 prices)
All SEBE rates are CPI-indexed annually.

Revenue grows automatically with automation deployment. Every new data centre,
automated warehouse, or AI inference cluster increases the tax base.

Scale comparison (year 1):
- Inheritance Tax + Stamp Duty + CCL + Tobacco: ~£34B (SEBE comparable)
- Corporation Tax: £100B (SEBE reaches this by ~2038)
- National Insurance: £170B (SEBE reaches this by ~2043)

**SEBE becomes a major revenue source within 10-15 years, tracking automation growth.**

### Two-Stage Distribution Model (Illustrative)

SEBE funds a two-stage transition from Universal Basic Income (UBI) to
Universal Living Income (ULI). Full working in `docs/distribution_model.md`.
Cost model context in `docs/cost_model.md`.

**Stage 1: Universal Basic Income (UBI) - Ramp Model**
- Starts at ~£690/adult/year (~£58/month) at launch (2030)
- Grows automatically as SEBE revenue increases with automation deployment
- Existing benefits (JSA, UC, PIP) continue unchanged
- Children's supplements phase in alongside UBI growth (age-banded):
  - 0-2: £5,000/year (equipment, nappies, formula, high parental demand)
  - 3-11: £3,500/year (food, clothing, school costs, activities)
  - 12-17: £4,000/year (higher food costs, social participation, technology)
- UBI is tax-free and unconditional
- **Stage 1 ramps with SEBE growth: ~£690/yr (2030) rising to ~£2,330/yr (2045)**

**Stage 2: Universal Living Income (ULI)**
- £29,000/adult/year (tax-free), matching median take-home pay
- Derived from ONS ASHE 2025: median gross £39,039, take-home ~£31,627,
  minus UBS £2,500 = ULI £29,000 (rounded)
- Children's supplements remain age-banded (same rates as Stage 1)
- **Stage 2 cost: ~£1.810T/year (requires SEBE plus progressive taxation)**

**Universal Basic Services (UBS):** £2,500/person/year value
- Energy (gas + electricity): ~£1,200/person
- All public transport (bus + national rail, free at point of use): ~£280/person
- Broadband (basic): ~£330/person
- Mobile + basic device: ~£200/person
- Margin/contingency: ~£490/person

**Effective living standard (Stage 2):**

| Component | Amount |
|---|---|
| ULI payment (adult) | £29,000 |
| UBS value | £2,500 |
| **Combined** | **£31,500** |
| Equivalent gross salary | ~£39,000 |

### Stage 1 Ramp and Feedback Loop

1. SEBE launches at £34-46B from automation infrastructure (2030)
2. UBI starts at ~£690/adult/year (55M adults = ~£38B)
3. UBS phases in over 9 years (transport 2032, energy 2036, broadband 2039)
4. Consumer spending increases (especially in deprived areas)
5. Economic activity generates additional conventional tax revenue
6. SEBE base grows as automation deployment increases
7. Combined revenue growth allows UBI to increase year-on-year
8. As automation displaces more jobs, SEBE revenue grows faster
9. UBI ratchets upward automatically toward ULI target (£29,000)

### Funding the Full Package

Stage 1 ramps with SEBE growth. At launch (£34-46B, 2030), SEBE funds
modest UBI (~£690/adult/year) plus initial UBS rollout. By 2040 (£93B),
combined with conventional tax feedback, SEBE supports significantly
higher UBI. All figures in 2026 real prices; rates CPI-indexed annually.

Stage 2 (full ULI at £29,000/adult) requires mature SEBE (£150B+) plus:
- Wealth tax: £50-80B
- Land Value Tax: £50-100B
- Financial Transaction Tax: £20-50B
- MMT framework: Sovereign currency flexibility as automation increases
  productivity

The transition from Stage 1 to Stage 2 is not a fixed date. UBI increases
incrementally as automation (and therefore SEBE revenue) grows.

**Note on hypothecation:** The Green Party opposes ring-fenced taxation.
SEBE generates revenue; government allocates it. Do not propose ring-fencing
SEBE revenue for specific purposes (including defence).

---

## Technical Feasibility

**VPN/Encryption does NOT hide bandwidth consumption:**
- ISP sees total throughput at border regardless of encryption
- BGP routing reveals destination country
- Non-UK endpoint = 2x tax applies
- Gaming is harder than current tax evasion (can't hide physical infrastructure)

**Wealth exit is irrelevant:**
- SEBE taxes fixed assets (datacenters, infrastructure) that CAN'T leave
- Rich person leaves, datacenter stays, revenue continues
- Tax the physical layer (immobile) not people (mobile)
- This is why SEBE works where wealth taxes don't

---

## Arguments & Rebuttals

**"Stifles innovation / companies will flee!"**
- Physical datacenters can't easily move
- Offshore compute taxed at 2x (cheaper to stay in UK)
- UK market access valuable (67M consumers with rising purchasing power)
- "Welcome to leave. We'll tax their products when they sell here"

**"Economically illiterate / unaffordable!"**
- £34-46B at 2030 launch (2026 prices), growing to £93-159B by 2040-2045
- Real revenue from measurable physical activity (energy, data throughput)
- Current system (taxing vanishing workers) is the illiterate approach
- SEBE is self-scaling: revenue grows with the problem (automation)
- MMT: Constraint is inflation (productivity) not money supply

**"People will stop working!"**
- Stage 1 starts at ~£690/year (2030), ramps gradually (supplement, not replacement)
- Even at full Stage 1 target (£2,500/yr), this is £208/month
- Evidence shows otherwise (Alaska PFD, Finland/Kenya pilots)
- Meaningful work increases when survival not at stake
- Job Guarantee alternative = coercive state labour

**"Inflation will destroy it!"**
- SEBE withdraws £34-46B from corporations (anti-inflationary)
- Stage 1 UBI starts small (~£690/yr) and ramps gradually (minimal demand shock)
- UBS directly reduces household costs (deflationary for recipients)
- Real constraint is production capacity
- Automation increases capacity, no inflation if productivity gains realised

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
- Greens demand UBI in coalition, need credible funding mechanism
- SEBE provides it (£34-46B at 2030 launch, self-scaling to £93-159B by 2040-2045)
- Stage 1 ramp model is fully costed with realistic growth projections
- Positions Greens as serious party with implementable, honest policy

### UK Strategic Context
- US instability creates defence funding pressure
- UK may need 4-5% GDP (£120-150B) for defence independence
- SEBE revenue contributes to general taxation, not ring-fenced
- Government can allocate revenue as needed (including defence)

---

## Documents

### Public-Facing (tax mechanism focus, distribution is illustrative)

**1. Green Party Policy Submission** (`docs/green_party_submission.md`)
- SEBE mechanism, EC code alignment, coalition strategy
- Distribution referenced as illustrative, not prescriptive
- Target: Policy Development Committee, Economy Working Group, Autumn 2026

**2. Academic/Think Tank Brief** (`docs/academic_brief.md`)
- No party political framing, economic analysis focus
- Technical feasibility, research agenda (acknowledges gaps)
- Target: IPPR, NEF, economics journals

**3. Public Explainer** (`docs/public_explainer.md`)
- "Tax robots, fund people" (simple language)
- Common questions, call to action
- Target: General public, media, campaign literature

### Reference Documents

**4. Revenue Model** (`docs/revenue_model.md`)
- Source of truth for all SEBE revenue figures
- First-principles derivation from DESNZ/Ofcom data
- Growth projections and sensitivity analysis

**5. Cost Model** (`docs/cost_model.md`)
- Lightweight bridge: SEBE revenue scale in context of existing taxes
- Not a distribution cost model (that's in distribution_model.md)

**6. Distribution Model** (`docs/distribution_model.md`)
- Illustrative two-stage UBI-to-ULI model
- Full costing: UBI/ULI/UBS, children's supplements, welfare offsets
- Sensitivity analysis, outstanding questions
- Referenced by public documents as "one possible use of SEBE revenue"

**7. Style Guide** (`docs/style_guide.md`)
- Writing standards for all SEBE documents
- AI writing tell avoidance, revenue figure enforcement

**8. Glossary** (`docs/glossary.md`)
- Term definitions used across all SEBE documentation

All public documents focus on the tax mechanism. Distribution detail is
in `distribution_model.md` and referenced as illustrative. Revenue
figures: £34-46B at 2030 launch (2026 prices) growing to £93-159B by
2040-2045. All rates CPI-indexed annually.

---

## Current Status

### Completed
- Technical specification (HRoT metering, BGP/SNI enforcement)
- Green Party aligned version (EC codes, coalition strategy)
- Three publication versions (party, academic, public)
- Cost model with full working and cited sources
- Earlier version submitted to Bedford Green Party chair and policy working group
- Git remote configured, repository public on GitHub

### In Progress
- Updating all documents to reflect two-stage model
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
1. Provide complete, publication-ready output (not drafts or fragments)
2. Include specific numbers and mechanisms, not vague generalities
3. Acknowledge uncertainties honestly
4. Mark document versions explicitly (v1.0, v1.1, etc.)
5. End formal documents with CC-BY 4.0 notice
6. Provide actionable next steps with each deliverable

---

**The role is to help execute, not educate. Certa Cito.**
