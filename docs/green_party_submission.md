# Sovereign Energy & Bandwidth Excise (SEBE)

## Policy Submission to Green Party Policy Development Committee

**Author:** Jason Huxley
**Date:** February 2026
**Version:** 3.0
**Target:** Policy Development Committee / Economy Working Group

---

## Executive Summary

The Sovereign Energy and Bandwidth Excise (SEBE) represents a fundamental
restructuring of the UK fiscal model for the post-employment economy. As
automation achieves parity with human capability, the tax base must pivot
from taxing human labour to taxing the physical infrastructure of automated
production: **energy consumption (kWh)** and **data throughput (Mbps)**.

**SEBE generates £26-33 billion at launch, growing to approximately £93 billion
by 2040** as automation infrastructure expands. Revenue automatically scales with
automation deployment, making SEBE the first self-scaling fiscal mechanism
aligned with the post-employment transition.

This paper proposes a **two-stage distribution model**:

- **Stage 1 (immediate): Universal Basic Income at £2,500/adult/year**,
  a universal supplement alongside existing benefits. UBI and UBS ramp together
  as SEBE revenue grows (~£352B/year full Stage 1 cost, reached as automation
  increases). Children receive age-banded supplements of £3,500-5,000/year.

- **Stage 2 (transition): Universal Living Income at £29,000/adult/year**
  (tax-free), matching the take-home pay of a median full-time earner. UBI
  ratchets upward as automation grows and SEBE revenue increases.

Both stages include **Universal Basic Services (UBS) at £2,500/person/year**:
free energy, all public transport (bus and national rail), broadband, and
mobile, free at point of use.

SEBE directly supports:
- **EC730** (Universal Basic Income funding)
- **EC100/EC310** (moving beyond GDP/labour indicators)
- **EC200** (ecological sustainability through energy taxation)
- **EC650** (corporate accountability)
- **EC661** (money as common resource)

---

## 1. The Automation Crisis and Tax Base Collapse

### 1.1 The Employment Decay

Current UK tax system depends on employment:
- **Income Tax:** £250B (25% of revenue)
- **National Insurance:** £170B (17% of revenue)
- **Combined:** £420B (42% of total revenue)

As automation eliminates employment:
- **Tax revenue falls** (fewer wages to tax)
- **Welfare costs rise** (more unemployed)
- **Fiscal crisis** (revenue collapse meets expenditure explosion)

### 1.2 The Value Migration

Economic value is shifting from:
- **Human labour** to **Machine computation**
- **Taxed (income tax)** to **Untaxed (corporate profits, offshore)**

Result: **Productive capacity increases while tax revenue decreases**

### 1.3 The SEBE Solution

Tax the **actual inputs** to production:
- **Energy (kWh):** Powers all computation and manufacturing
- **Bandwidth (Mbps):** Enables all digital economic activity

These are:
- **Measurable** (hardware infrastructure)
- **Unavoidable** (physical bottlenecks)
- **Fair** (scales with actual resource consumption)
- **Future-proof** (captures automation dividend)

---

## 2. Technical Implementation

### 2.1 Sovereign Energy Excise (SEE)

**Coverage:** Commercial facilities with IT load >500kW

**Metering Architecture (Hardware Root of Trust):**

Three measurement points:
1. **Point of Generation (PoG):** Captures all incoming energy (grid, private SMRs, renewables)
2. **Point of Storage (PoS):** Monitors battery systems (prevents temporal arbitrage)
3. **Point of Load (PoL):** Measures actual consumption at compute infrastructure

**Reconciliation Formula:**
```
SEE Liability = PoL - (PoS_final - PoS_initial) x RTE_allowance
```

Where RTE (Round-Trip Efficiency) allowance = 5% variance for battery losses

**Purpose:** Prevents "dark compute" powered by unmetered generation

**Alignment:** EC513/EC654 (environmental auditing), EC200 (ecological sustainability)

### 2.2 Digital Customs Duty (DCD)

**Coverage:** Corporate data throughput (Net Neutrality protected for individuals)

**Implementation at Internet Exchange Points:**

**Role Margin Protocol:**
- Baseline quota per Standard Industrial Classification (SIC) code
- Flag throughput >1.5x standard deviation for sector
- Tax excess as "imported labour" (offshore AI/compute services)

**Traffic Analysis:**
- Layer 4-7 inspection (SNI, flow symmetry)
- BGP Community Tagging at Tier-1 gateways
- Distinguishes commercial vs personal traffic

**Rate Structure:**
- **Domestic compute:** Base rate
- **Offshore compute:** 1.5-2x base rate (incentivises UK datacenter investment)

**Purpose:** Capture value from offshore computation serving UK market

**Alignment:** EC921/EC947 (digital sovereignty), EC1052 (preventing profit extraction)

---

## 3. Revenue Modelling

### 3.1 Energy Component

**UK commercial/industrial electricity:** ~150 TWh/year total, but only
approximately **70 TWh in facilities above the 500kW threshold**. Most
commercial electricity is used by small and medium enterprises (shops, offices,
restaurants) that fall below 500kW. The threshold targets data centres, large
industrial operations, and automated warehouses.

**Proposed rate tiers:**

| Consumption Bracket | Rate | Rationale |
|---|---|---|
| 0-500 kW | Exempt | Small business protection |
| 500 kW - 5 MW | £0.05/kWh | Progressive ramp |
| 5 MW - 50 MW | £0.15/kWh | Standard commercial |
| >50 MW | £0.30/kWh | Datacenter/heavy industrial |

**Year 1 revenue estimate:** £19-23 billion/year at launch, growing to £83
billion by 2040 as automation infrastructure expands (data centres, automated
warehouses, robotic manufacturing).

**Notes:**
- Drives energy efficiency (EC200)
- Incentivises renewable transition
- Larger operations pay proportionally more
- Revenue automatically scales with automation deployment

### 3.2 Bandwidth Component (Digital Customs Duty)

**DCD is a border tariff only**, taxing commercial data crossing the UK digital
border in either direction. Consumers are exempt. Domestic data centre traffic
is exempt (pays SEE on energy instead).

**Who pays:**
- UK businesses using offshore cloud providers (AWS Ireland, Azure Netherlands)
- UK businesses calling offshore APIs (OpenAI, Anthropic, etc.)
- UK companies using offshore SaaS platforms
- Any UK commercial entity whose data crosses the digital border

**Proposed tiered rate structure:**

| Annual border traffic | DCD Rate | Target |
|---|---|---|
| < 10 PB | £200/TB | Small/medium offshore use |
| 10-100 PB | £400/TB | Large enterprise offshore |
| > 100 PB | £800/TB | Hyperscaler-equivalent |

**Year 1 revenue estimate:** £7-10 billion/year at launch. Revenue remains
roughly stable (repatriation offsets volume growth) as the deterrent effect
drives compute back to UK facilities where SEE applies.

**Notes:**
- Captures value from offshore computation serving UK market
- DCD rate set above SEE-equivalent to incentivise domestic data centre investment
- Creates genuine economic advantage for UK-based compute infrastructure
- Revenue secondary to SEE but critical as enforcement mechanism

### 3.3 Total SEBE Revenue

**Year 1 (launch):** **£26-33 billion/year**

**Growth trajectory:**
- 2030: £38 billion
- 2035: £57 billion
- 2040: £93 billion
- 2045: £159 billion (mid scenario)

**As proportion of current tax revenue (£1 trillion):** 2.6-3.3% at launch,
growing to approximately 9% by 2040.

**Comparison to existing taxes at launch:**
- Comparable to Inheritance Tax (£7B) + Stamp Duty (£15B) + Climate Change Levy (£2B) + Tobacco Duty (£10B) combined
- Smaller than Corporation Tax (£100B) or VAT (£160B)
- Becomes a major revenue source as automation grows

**Key characteristic: SEBE is self-scaling.** Revenue automatically tracks
automation deployment. As machines replace workers, the tax on machine
infrastructure funds workers' replacement income. This is the only UK tax
that grows with the thing that causes the employment crisis it addresses.

---

## 4. Distribution Framework: Two-Stage Model

### 4.1 Rationale

SEBE's launch revenue (£26-33B/year) cannot fund full Stage 1 (£352B/year
for UBI at £2,500 + UBS) from day one. However, SEBE provides a foundation
that grows automatically with automation. As automation infrastructure expands,
SEBE revenue increases, allowing UBI and UBS to ramp together.

This two-stage approach:
- Starts immediately at a modest level (UBI £400/adult/year from SEBE alone)
- Removes the "people will stop working" objection (Stage 1 is a supplement)
- Creates a **self-reinforcing feedback loop** (more spending, more tax revenue)
- Allows organic transition as the economy shifts
- Reaches full Stage 1 funding as automation grows over 10-15 years

### 4.2 Stage 1: Universal Basic Income (UBI)

**UBI at £2,500/adult/year (£208/month)**

A universal supplement to existing income. Not a replacement.

- Existing benefits (JSA, UC, PIP, etc.) continue unchanged
- Unemployed receive existing benefits PLUS UBI
- Employed receive wages PLUS UBI
- Pensioners receive state pension PLUS UBI
- UBI is tax-free and unconditional

**Children's supplement (paid to parent/guardian in child's name):**

| Age Band | Annual Supplement | Rationale |
|---|---|---|
| 0-2 (infant) | £5,000 | Equipment, nappies, formula/food, high parental demand |
| 3-11 | £3,500 | Food, clothing, school costs, activities |
| 12-17 | £4,000 | Higher food costs, social participation, technology |

Children's rates reflect actual incremental costs of a child in an existing
household. They are not a percentage of adult UBI. Children share housing,
heating, and most infrastructure with their parent(s).

### 4.3 Stage 1 Cost

| Component | Count | Rate | Annual Cost |
|---|---|---|---|
| Adult UBI | 55M | £2,500 | £137.5B |
| Children 0-2 | 2M | £5,000 | £10B |
| Children 3-11 | 6M | £3,500 | £21B |
| Children 12-17 | 4M | £4,000 | £16B |
| **UBI subtotal** | | | **£184.5B** |
| UBS provision | 67M | £2,500 | £168B |
| **Stage 1 total** | | | **£352.5B** |

**SEBE revenue:** £26-33 billion/year at launch, growing to £93 billion by 2040.

**Ramp model:** UBI and UBS phase in together as SEBE revenue grows. At launch
(2027), SEBE funds UBI at approximately £400/adult/year. As automation expands
and SEBE revenue increases, UBI ratchets upward (£400 → £2,500 over 10-15 years)
while UBS components phase in (free public transport first, then energy, then
broadband/mobile). Full Stage 1 (UBI £2,500 + UBS) is reached as SEBE grows
with automation.

**Alignment:** EC730 (UBI as right), EC201 (zero/negative growth compatible)

### 4.4 Universal Basic Services (UBS)

**Free at point of use:**
- Energy (gas + electricity, to household threshold)
- All public transport (buses, trains, trams, free at point of use)
- Broadband (basic tier)
- Mobile + basic device

**Annual cost:** £168 billion (£2,500/person)

UBS does not replace housing, food, or clothing. These are funded from
UBI/ULI cash payments.

### 4.5 Stage 1 Feedback Loop

1. SEBE generates £26-33B from automation infrastructure at launch
2. Initial UBI distributed at £400/adult/year (55M adults)
3. UBS phases in (free public transport first, then energy, then broadband/mobile)
4. UBI payments hit millions of bank accounts
5. Consumer spending surges (especially in deprived areas)
6. High street, hospitality, local services recover
7. Increased economic activity generates additional conventional tax revenue
   (income tax, VAT, corporation tax, business rates all rise)
8. As automation displaces more jobs, SEBE revenue grows (more data centres,
   automated warehouses, robotic manufacturing all increase SEE base)
9. Combined revenue (SEBE + conventional + feedback) allows UBI to increase
10. UBI ratchets upward from £400 toward £2,500, then toward ULI

### 4.6 Stage 2: Universal Living Income (ULI)

**ULI target: £29,000/adult/year (tax-free)**

Stage 2 is the endgame, reached when automation has displaced enough
employment that UBI must transition from supplement to primary income.

**Derivation:**
- ONS ASHE 2025 median gross annual earnings (full-time): £39,039
- Tax and NI on £39,039 (2025/26 rates): ~£7,412
- Take-home pay: ~£31,627
- UBS value: £2,500
- ULI = take-home minus UBS = **£29,000** (rounded)

This matches the spending power of a current median full-time earner.

| Component | Amount |
|---|---|
| ULI payment (adult) | £29,000 |
| UBS value | £2,500 |
| **Effective living standard** | **£31,500** |
| Equivalent gross salary | ~£39,000 |

**Stage 2 full cost:**

| Component | Count | Rate | Annual Cost |
|---|---|---|---|
| Adult ULI | 55M | £29,000 | £1.595T |
| Children 0-2 | 2M | £5,000 | £10B |
| Children 3-11 | 6M | £3,500 | £21B |
| Children 12-17 | 4M | £4,000 | £16B |
| **ULI subtotal** | | | **£1.642T** |
| UBS provision | 67M | £2,500 | £168B |
| **Stage 2 total** | | | **£1.810T** |

Stage 2 requires SEBE plus additional progressive taxation (wealth tax, LVT,
FTT) and expanded fiscal space under MMT as automation increases productive
capacity.

### 4.7 Transition Timeline

The transition from Stage 1 to Stage 2 is not a fixed date. It is driven by:
- Growth in automation (and therefore SEBE revenue)
- Decline in employment (and therefore need for higher UBI)
- Conventional tax revenue from the UBI stimulus effect
- Inflation dynamics and productive capacity

A plausible (illustrative, not predictive) trajectory:

| Year | Adult UBI | Approximate Cost | Notes |
|---|---|---|---|
| Year 1 | £2,500 | £185B | Stage 1 launch, SEBE funded |
| Year 3 | £5,000 | £275B + children | Stimulus revenue reinvested |
| Year 5 | £10,000 | £550B + children | Automation displacement accelerating |
| Year 10 | £20,000 | £1.1T + children | Significant employment decline |
| Year 15+ | £29,000 | £1.6T + children | Stage 2 (ULI), full transition |

---

## 5. Enforcement Framework

### 5.1 Tiered Compliance System

**Tier 1: Technical Remediation**
- Discrepancies <10% from metering variance
- Mandatory audit by National Telemetry Agency
- Administrative penalties for late adjustment
- **Standard tax collection procedure**

**Tier 2: Systematic Evasion**
- HRoT tampering or unmetered compute nodes
- Commercial bandwidth permit suspension
- Court-ordered receivership (like bankruptcy proceedings)
- Asset liquidation to cover liability

**Tier 3: Capital Flight Prevention**
- Exit tax on realised gains (standard practice)
- Strategic de-listing from UK digital infrastructure
- Asset seizure under existing fraud/tax evasion law

**Alignment:** EC650 (corporate accountability), EC981 (preventing capital flight), EC797 (tax haven prevention)

### 5.2 Progressive Revenue Protection

**Problem:** Companies relocate to low-tax jurisdictions

**Solutions:**
- **Offshore compute tax** (2x domestic rate) = penalises relocation
- **Digital border enforcement** (BGP/SNI at IXPs)
- **International coordination** (EU/OECD minimum rates)

**This prevents race to bottom while maintaining UK competitiveness**

---

## 6. Implementation Roadmap

### Phase 1: Infrastructure (2027-2028)
- National Telemetry API development
- Sovereign Metering Standard (open-source, TPM-secured)
- Pilot with 10-20 largest datacenters
- Legal framework enacted

### Phase 2: Rollout (2028-2029)
- Mandatory installation for >50MW facilities
- Digital border infrastructure at major IXPs
- Initial UBI payments at Stage 1 rate (£2,500/adult/year)
- UBS rollout begins (free public transport first)
- Revenue validation

### Phase 3: Expansion (2029-2030)
- Extension to >5MW facilities
- Full UBS implementation
- UBI increased as revenue allows (target £5,000-10,000/year)
- International coordination (EU alignment)

### Phase 4: Maturity (2030+)
- >500kW facilities included
- Full SEBE coverage operational
- UBI continuing to ratchet toward ULI as automation grows
- Complete UBS coverage

**Total timeline:** 3-5 years from legislation to full SEBE coverage.
UBI-to-ULI transition is ongoing, driven by automation growth.

---

## 7. Why SEBE Enables Green Coalition Government

### 7.1 The Coalition Arithmetic (Post-2028 Election)

**Likely scenario:**
- Reform UK plurality (not majority)
- Labour-Green-Lib Dem coalition possible
- **Green demands:** Wealth tax, PR, **UBI funding**

**Current problem:** UBI unfunded (no viable mechanism)

**SEBE solution:**
- £26-33B revenue at launch, growing to £93B by 2040 (proven mechanism)
- Stage 1 ramps with SEBE growth, fully costed
- Politically viable (taxes corporations not workers)
- Technically feasible (infrastructure exists)
- Self-scaling (revenue tracks automation)

### 7.2 Cross-Party Appeal

**Greens:** Environmental + social justice + UBI
**Labour left:** Post-neoliberal economics + worker protection
**Lib Dems:** Evidence-based, technocratic implementation

**SEBE bridges:**
- Environmental sustainability (EC200)
- Economic justice (EC730)
- Fiscal sustainability (replaces failing employment tax)

### 7.3 Political Timing

**Green Party membership:** 195,000 (Feb 2026)
**Polling:** 14% (potentially 9+ seats)
**Coalition probability:** 20-30% by 2029

**If Greens in coalition:**
- Need **deliverable** UBI policy (not aspiration)
- Need **costed** mechanism (not theory)
- **SEBE provides both** (Stage 1 ramps with automation, reaching full funding
  as SEBE grows)

**This paper positions Green Party** with implementable flagship policy
for coalition negotiations.

---

## 8. Comparison to Alternative Revenue Sources

### 8.1 Why Not Just Wealth Tax?

**Wealth tax potential:** £50-80B/year (on top 1%)

**Problems:**
- Capital flight (wealthy relocate)
- Valuation disputes (illiquid assets)
- One-time gain (wealth depletes)
- Political opposition (property owners)

**SEBE advantages:**
- Infrastructure can't relocate (datacenters are physical)
- Objective measurement (kWh/Mbps are quantifiable)
- Recurring revenue (ongoing consumption)
- Taxes corporate activity not personal wealth

**Both needed:** Wealth tax + SEBE = complementary

### 8.2 Why Not Just Corporation Tax?

**Current corp tax:** £100B at 25% rate

**Problems:**
- Profit shifting (Ireland, Luxembourg)
- Gaming via transfer pricing
- Penalises domestic companies
- Race to bottom (international competition)

**SEBE advantages:**
- Can't offshore physical energy consumption
- Bandwidth tax captures offshore compute
- Based on real activity not accounting profits
- 2x rate on offshore = competitive advantage to UK datacenters

### 8.3 Why Not Just Carbon Tax?

**Carbon tax:** Captures emissions, not full energy

**Problems:**
- Only covers fossil fuels
- Misses renewable-powered compute
- Environmental focus not fiscal

**SEBE advantages:**
- Captures ALL energy (renewable or fossil)
- Fiscal + environmental benefits
- Bandwidth component captures digital activity carbon tax misses

**Complementary:** Carbon tax on emissions + SEBE on energy = good coverage

---

## 9. Fiscal Sustainability Analysis

### 9.1 Stage 1 Requirement

**Stage 1 (ramps with SEBE growth):**
- UBI: £184.5B (55M adults at £2,500 + 12M children age-banded)
- UBS: £168B (67M people at £2,500)
- **Total: £352.5B/year**

**SEBE revenue:** £26-33B/year at launch, growing to £93B by 2040.
**Coverage:** 7-9% of full Stage 1 costs at launch. UBI and UBS ramp together
as SEBE revenue grows, reaching full Stage 1 funding within 10-15 years as
automation expands.

### 9.2 Stage 2 Requirement

**Stage 2 (SEBE plus progressive taxation):**
- ULI: £1.642T (55M adults at £29,000 + 12M children)
- UBS: £168B (67M people at £2,500)
- **Total: £1.810T/year**

**Revenue sources (combined):**
- SEBE: £26-93B (launch to 2040, continuing to grow)
- Wealth tax: £50-80B
- Land Value Tax: £50-100B
- Financial Transaction Tax: £20-50B
- Conventional tax (boosted by UBI stimulus): growing
- MMT framework: Sovereign currency flexibility

### 9.3 MMT Framework

**Key insight (EC661):** Sovereign currency issuer (UK has pound) faces
**inflation constraint** not **financing constraint**

**As automation increases productivity:**
- Real output increases (goods/services produced)
- Labour costs fall (automation)
- **Productive capacity** expands

**SEBE's role in MMT:**
- **Withdraws purchasing power** from corporations (anti-inflationary)
- **Distributes to population** as UBI/ULI (maintains demand)
- **Balance** prevents inflation while ensuring full use of productive capacity

---

## 10. International Coordination

### 10.1 Preventing Tax Havens

**Problem:** Ireland/Luxembourg offer low corporate rates

**SEBE prevents:**
- **Energy consumption** physically located in UK (can't offshore datacenters completely)
- **Bandwidth tax** at 2x rate for offshore compute (penalises relocation)
- **Digital border** enforcement (BGP tagging at IXPs)

### 10.2 EU Coordination Opportunity

**Propose SEBE as EU-wide framework:**
- Harmonised energy tax (prevents race to bottom)
- Coordinated digital borders (prevents haven shopping)
- **EU SEBE revenue:** £600B-1.5T (EU-wide UBI)

**UK leadership:** First mover advantage in post-employment fiscal policy

### 10.3 OECD Minimum Standards

**Similar to:** OECD minimum corporate tax (15%)

**Propose:** OECD minimum energy/bandwidth tax
- Prevents international competition undermining UBI/ULI
- Establishes UK as policy leader
- Protects domestic revenue base

---

## 11. Transition from Current System

### 11.1 Phase-In Without Economic Shock

**Year 1-2 (2027-2028):**
- Pilot with largest 50 datacenters
- UBI payments begin: £400/adult/year from SEBE
- Free public transport phased in
- Revenue: £26-33B at launch

**Year 3-4 (2028-2030):**
- Expand to all >5MW facilities
- UBI increased as revenue grows (from £400 toward £2,500)
- UBS expansion continues
- Revenue: £38-45B

**Year 5+ (2030+):**
- Full coverage >500kW
- UBI continuing toward ULI
- Revenue: £57B (2035), £93B (2040), £159B (2045)
- Transition pace set by automation growth

### 11.2 Interaction with Existing Taxes

**SEBE does NOT replace immediately:**
- Income tax (remains for high earners)
- VAT (consumption tax)
- Council tax (local funding)

**SEBE reduces over time:**
- National Insurance (employment-linked)
- Means-tested benefits (ULI eventually replaces)
- Unemployment support (ULI eventually provides)

**Net effect:** Simpler, more efficient tax system aligned with
post-employment reality

---

## 12. Political Viability and Coalition Strategy

### 12.1 Green Party Positioning

**Current challenge:** UBI in manifesto but unfunded

**SEBE provides:**
- £26-33B/year at launch, growing to £93B by 2040
- Stage 1 fully costed (£352B, reached as SEBE grows with automation)
- Technically feasible
- Environmentally beneficial
- Self-scaling revenue mechanism

**Coalition negotiation strength:**
- "We have UBI funding mechanism ready to implement"
- "Not aspiration, detailed technical specification"
- "Stage 1 UBI launches immediately, grows automatically with automation"

### 12.2 Potential Allies

**Labour progressives:** Post-neoliberal economics, MMT-aware
**Tech sector:** Prefer automation tax to income tax (aligns with transition)
**Energy companies:** Predictable framework for renewable transition
**Unions:** Protects workers during automation transition

### 12.3 Opposition

**Neoliberals:** "Kills competitiveness" (counter: offshore rate addresses)
**Tech monopolies:** "Stifles innovation" (counter: UK companies benefit from onshore advantage)
**Conservatives:** "Big government" (counter: replaces welfare bureaucracy with simple UBI)

**Victory condition:** Coalition with 40%+ vote share, Green Party holding balance

---

## 13. Addressing Anticipated Critiques

### 13.1 "Companies will relocate offshore"

**Response:**
- Datacenters physically located in UK (can't just move them)
- Offshore compute taxed at 2x (cheaper to stay)
- UK becomes attractive for datacenter investment (clear tax framework)
- Energy cost + SEBE still competitive vs relocating

### 13.2 "Measurement is impossible"

**Response:**
- UK already meters commercial energy (smart meters deployed)
- ISPs already measure bandwidth (peering agreements, CDN contracts)
- Hardware Root of Trust prevents tampering
- Simpler than current tax system (single physical measurement vs complex accounting)

### 13.3 "Inflation will eat UBI"

**Response:**
- Stage 1 UBI is £2,500/year (minimal demand shock)
- SEBE is inflation-indexed (kWh/Mbps rates adjust)
- SEBE withdraws purchasing power from corporations (anti-inflationary)
- UBS directly reduces household costs (deflationary for recipients)
- Real constraint is productive capacity not money supply

### 13.4 "Creates surveillance state"

**Response:**
- Meters measure total consumption only (not individual behaviour)
- Net Neutrality protected (individual traffic never inspected)
- Commercial traffic metadata only (encrypted content not examined)
- Less intrusive than current tax system (HMRC monitors all transactions)

---

## 14. Recommendations

### 14.1 Immediate Actions (Policy Development Committee)

1. **Adopt SEBE** as core UBI funding mechanism for next manifesto
2. **Commission economic modelling** (partner with academic institution)
3. **Engage technical experts** (infrastructure, energy, networking)
4. **Draft legislation** (work with parliamentary researchers)
5. **Public consultation** (build support among tech workers, unions)

### 14.2 Coalition Preparation

**Position SEBE as:**
- Non-negotiable for Green coalition participation
- "Funded UBI or no deal"
- Technical specification ready for immediate implementation
- Stage 1 deliverable within first parliament

### 14.3 Timeline to Implementation

**2026:** Policy adoption, economic modelling
**2027:** Manifesto inclusion, public campaign
**2028-2029:** Election, coalition negotiation
**2029:** Legislation passed
**2030-2032:** Phased implementation (Stage 1 UBI from day one of SEBE revenue)
**2032+:** UBI ratchets toward ULI as automation grows

---

## 15. Conclusion

The Sovereign Energy and Bandwidth Excise represents the fiscal foundation
for a post-employment society. By taxing the physical infrastructure of
automated production rather than human labour, SEBE:

- Generates £26-33 billion/year at launch, growing to £93 billion by 2040
- Funds Stage 1 UBI launch at £400/adult/year, ramping to £2,500 as automation grows
- Provides a clear transition path to full ULI (£29,000/adult, matching median take-home pay)
- Enables Universal Basic Services (free energy, transport, broadband, mobile)
- Aligns with Green values (environmental, social justice, democracy)
- Provides implementable policy for coalition government
- **Self-scales:** Revenue automatically tracks automation deployment

**SEBE transforms Green Party from protest movement to government-ready**
with detailed, costed, technically feasible flagship policy.

As automation eliminates employment, the state must choose:
- **Neoliberal path:** Tax base collapses, austerity, social breakdown
- **SEBE path:** New revenue from automation, universal income, thriving society

**The choice defines the next decade of British politics.**

This paper provides the technical and political framework for the SEBE path.

---

## Appendices

### Appendix A: Technical Specifications
- Hardware Root of Trust meter specifications
- BGP Community Tag implementation
- SNI filtering protocols
- National Telemetry API architecture
- (Full technical specs available on request)

### Appendix B: EC Policy Concordance
[Full mapping of SEBE to existing Green Party policy codes EC100-EC1053]

### Appendix C: Cost Model
Full working for all figures used in this submission is available in the
accompanying cost model document (`docs/cost_model.md`), including:
- ONS data sources and staleness dates
- Population breakdown and assumptions
- Median income and tax burden calculations
- UBS component costing (including transport demand elasticity)
- Rail rent extraction analysis (ROSCO data)
- Two-stage cost breakdown with sensitivity analysis

### Appendix D: International Examples
- Norway: Energy-based sovereign wealth fund
- Luxembourg: Free public transport (since 2020)
- Singapore: Digital services tax
- EU: Digital Services Act precedent

---

**Contact:** [Your details]
**Further information:** Available to present to Policy Development Committee or Economy Working Group

© 2026 Jason Huxley
Licensed under CC-BY 4.0
You may use, adapt, and distribute this work
provided you credit the original author.
