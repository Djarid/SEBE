# Sovereign Energy & Bandwidth Excise (SEBE)

## Policy Submission to Green Party Policy Development Committee

**Author:** Jason Huxley
**Date:** February 2026
**Version:** 4.0
**Target:** Policy Development Committee / Economy Working Group

---

## Executive Summary

Automation is eroding the UK income tax base. Income Tax (£250B) and
National Insurance (£170B) together provide 42% of government revenue,
and both depend on employment. As automation displaces workers, this
revenue shrinks while welfare costs grow. No existing tax replaces it.

The Sovereign Energy and Bandwidth Excise (SEBE) does. SEBE taxes the
physical infrastructure of automated production: **energy consumption
(kWh)** and **cross-border commercial data (TB)**. It is the only UK tax
that grows with the thing causing the employment crisis.

**SEBE generates £34-46 billion at launch (2030, in 2026 real prices),
growing to £93 billion by 2040 and £159 billion by 2045.** Revenue is
self-scaling: every new data centre, automated warehouse, or AI cluster
increases the tax base. All rates are CPI-indexed annually.

The revenue is general-purpose. It could fund UBI (as proposed in EC730),
reduce the deficit, replace National Insurance, expand the NHS, or any
combination. An illustrative distribution model (UBI starting at
~£650/adult/year at 2030 launch, ramping with automation) is included as an appendix,
but SEBE's value is the revenue mechanism itself.

SEBE directly supports:
- **EC730** (Universal Basic Income funding mechanism)
- **EC100/EC310** (moving beyond GDP/labour-dependent indicators)
- **EC200** (ecological sustainability through energy taxation)
- **EC650** (corporate accountability for automation externalities)
- **EC661** (money as common resource, MMT-compatible fiscal expansion)

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
| 500 kW - 5 MW | £0.08/kWh | Progressive ramp |
| 5 MW - 50 MW | £0.20/kWh | Standard commercial |
| >50 MW | £0.45/kWh | Datacenter/heavy industrial |

**Year 1 revenue estimate:** £24-28 billion/year at launch, growing to £83
billion by 2040 as automation infrastructure expands (data centres, automated
warehouses, robotic manufacturing). Full derivation in `revenue_model.md`.

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

**Year 1 (2030 launch):** **£34-46 billion/year** (2026 prices)

**Growth trajectory:**
- 2030: £38 billion
- 2035: £57 billion
- 2040: £93 billion
- 2045: £159 billion (mid scenario)

**As proportion of current tax revenue (£1 trillion):** 3.4-4.6% at launch,
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

## 4. What SEBE Revenue Could Fund

SEBE revenue is general-purpose. How it is spent is a political decision.
The following illustrates scale, not prescriptive policy.

### 4.1 At Launch (£34-46B, 2030)

| Use | Cost | Notes |
|---|---|---|
| Modest UBI (~£650/adult/year) | ~£38B | Universal supplement (EC730) |
| Free public transport | ~£14B | Fares replacement (ORR 2024/25) |
| NHS waiting list reduction | ~£10-15B | Capital + staffing |
| National Insurance cut | £38B = ~2p off NI | Pro-employment option |

### 4.2 At Maturity (£93B by 2040)

| Use | Cost | Notes |
|---|---|---|
| UBI at £1,000/adult/year | ~£55B | Meaningful supplement |
| Full NI replacement | £170B | Achievable by ~2043 |
| Deficit elimination | £93B | More than covers current borrowing |

### 4.3 Illustrative Distribution Model

One detailed scenario is worked through in the accompanying
`distribution_model.md`. In summary:

- **Stage 1:** UBI starting at ~£650/adult/year (2030 launch), ramping with SEBE
  growth. Universal Basic Services (free transport, energy, broadband)
  phase in over years. Children's supplements at £3,500-5,000/year.
- **Stage 2:** UBI ratchets toward Universal Living Income
  (£29,000/adult/year, matching median take-home pay) as automation
  displaces employment.

This is one option. SEBE works regardless of distribution model.

**Alignment:** EC730 (UBI as right), EC201 (zero/negative growth compatible)

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

### Phase 1: Legislation and Infrastructure (2029-2030)
- SEBE legislation enacted following election
- National Telemetry API development
- Sovereign Metering Standard (open-source, TPM-secured)
- Pilot with 10-20 largest datacenters

### Phase 2: Rollout (2030-2031)
- Mandatory installation for >50MW facilities
- Digital border infrastructure at major IXPs
- Revenue collection begins (£34-46B at launch, 2026 prices)
- Revenue allocation decision (UBI, NI reduction, or combination)

### Phase 3: Expansion (2031-2032)
- Extension to >5MW facilities
- International coordination (EU alignment)
- Revenue growing with automation deployment

### Phase 4: Maturity (2033+)
- >500kW facilities included
- Full SEBE coverage operational
- Revenue at £57B+ by 2035, £93B+ by 2040 (2026 prices)

**Total timeline:** 3-5 years from legislation to full SEBE coverage.
Revenue grows automatically thereafter.

---

## 7. Why SEBE Enables Green Coalition Government

### 7.1 The Coalition Arithmetic (Post-2028 Election)

**Likely scenario:**
- Reform UK plurality (not majority)
- Labour-Green-Lib Dem coalition possible
- **Green demands:** Wealth tax, PR, **UBI funding**

**Current problem:** UBI unfunded (no viable mechanism)

**SEBE solution:**
- £34-46B revenue at launch (2030, 2026 prices), growing to £93B by 2040
- Revenue funds EC730 UBI from day one (modest start, grows with automation)
- Politically viable (taxes corporations not workers)
- Technically feasible (infrastructure exists)
- Self-scaling: the only tax that grows with the thing replacing workers

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
- Any initial UBI is modest (~£650/year at launch, minimal demand shock)
- SEBE rates are CPI-indexed annually (like alcohol and tobacco duty)
- SEBE withdraws purchasing power from corporations (anti-inflationary)
- UBS directly reduces household costs (deflationary for recipients)
- Real constraint is productive capacity, not money supply
- **Crucially:** the automation SEBE taxes simultaneously reduces the real
  cost of producing goods and services. Unit costs of manufacturing,
  logistics, energy, and service delivery all fall as automation scales.
  The tax captures a share of productivity gains that are themselves
  deflationary

### 13.4 "Why not tax FLOPS (compute operations) directly?"

**Response:**
- **FLOPS is not a standard unit.** FP64, FP32, FP16, INT8, INT4 all
  count differently. A GPU rated at 1,000 TFLOPS in FP16 gives a
  completely different number in FP32. There is no "one FLOP" that maps
  to a unit of economic work.
- **No physical measurement point.** Energy has meters. FLOPS has nothing
  except software-readable hardware counters (trivially spoofable) or
  self-declaration (obvious gaming incentive).
- **Evasion is architectural.** Switch from GPU to ASIC, use lower
  precision, use neuromorphic compute, run I/O-bound workloads. All
  legitimate engineering choices that reduce FLOPS without reducing
  economic output.
- **Punishes efficiency.** A newer GPU that finishes a task in fewer
  FLOPS pays less than an older, power-hungry GPU. This incentivises
  keeping wasteful hardware running.
- **Can't meter offshore.** You cannot count FLOPS in a Virginia data
  centre from London. SEBE's DCD taxes the data crossing the border
  instead (measurable at IXPs).
- **Energy is the correct proxy.** Every computation (GPU, TPU, ASIC,
  quantum, neuromorphic) consumes energy. Energy metering is deployed,
  tamper-resistant, architecture-neutral, and rewards efficiency.

### 13.5 "Creates surveillance state"

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
**2027-2028:** Manifesto inclusion, public campaign
**2028-2029:** Election, coalition negotiation
**2029-2030:** Legislation passed, metering infrastructure deployed
**2030-2033:** Phased implementation (Stage 1 UBI from day one of SEBE revenue)
**2033+:** UBI ratchets toward ULI as automation grows

---

## 15. Conclusion

The Sovereign Energy and Bandwidth Excise solves the income tax
replacement problem. By taxing the physical infrastructure of automated
production rather than human labour, SEBE:

- **Replaces eroding employment tax revenue** (£34-46B at launch, £93B by 2040, £159B by 2045, CPI-indexed, 2026 prices)
- **Self-scales:** the only UK tax that grows with the thing replacing workers
- **Funds EC730 UBI** from day one of revenue collection
- **Drives energy efficiency** and UK datacenter investment (EC200)
- **Prevents offshore profit shifting** (can't move physical energy consumption)
- **Aligns with Green values** (environmental, social justice, fiscal sovereignty)

**SEBE gives the Green Party a costed, implementable, self-scaling revenue
mechanism** for the post-employment transition. The distribution question
(UBI rate, UBS scope, transition speed) is a separate political decision.
The revenue mechanism is the hard part, and this paper provides it.

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

### Appendix C: Revenue and Distribution Models
- `docs/revenue_model.md`: Full SEBE revenue derivation from first principles
- `docs/cost_model.md`: Revenue scale comparisons and economic context
- `docs/distribution_model.md`: Illustrative UBI/ULI/UBS distribution workings

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
