# SEBE Revenue Model

## Derivation from First Principles

**Author:** Jason Huxley
**Version:** 2.0
**Date:** February 2026
**Status:** Working document (replaces placeholder estimates in prior documents)

---

## 1. Purpose

This document derives SEBE revenue estimates from real data: UK energy
consumption statistics, data centre capacity figures, wholesale and retail
bandwidth pricing, and LLM token economics. It replaces the placeholder
£200-500B estimates used in earlier documents, which were never calculated
from the stated rates.

The earlier estimates implied energy consumption of 1,000-1,600 TWh at
the stated SEE rates. UK total electricity generation is approximately
300 TWh. The error is acknowledged and corrected here.

---

## 2. Data Sources

| Source | Data | Date |
|---|---|---|
| DESNZ (formerly BEIS) | UK electricity consumption by sector | 2023 |
| Ofgem | Commercial and domestic electricity prices | 2025/26 |
| IEA | Global data centre electricity demand projections | 2024 |
| LINX | London Internet Exchange peak throughput (~7 Tbps) | 2024 |
| Ofcom Connected Nations | UK broadband and mobile traffic | 2024 |
| Cloudflare/drPeering | Wholesale IP transit pricing trends | 2024 |
| Google Cloud | Egress pricing (europe-west2, London) | Feb 2026 |
| AWS | EC2 data transfer pricing | Feb 2026 |
| OpenAI | API token pricing (GPT-5.2, GPT-5 mini) | Feb 2026 |
| Anthropic | API token pricing (Opus 4.6, Sonnet 4.5, Haiku 4.5) | Feb 2026 |
| ONS | UK population mid-2023 estimate | 2024 |

---

## 3. SEE Revenue Derivation

### 3.1 UK Electricity Consumption

Total UK electricity consumption: approximately **300 TWh/year**.

| Sector | TWh | Notes |
|---|---|---|
| Households | ~105 | Always exempt from SEE |
| Commercial (>500kW facilities) | ~45 | Subject to SEE |
| Industrial (>500kW facilities) | ~25 | Subject to SEE |
| Commercial (<500kW) | ~65 | Below current threshold |
| Industrial (<500kW) | ~15 | Below current threshold |
| Transport and other | ~45 | Not applicable |
| **Total** | **~300** | |

**Current SEE tax base: ~70 TWh** (facilities exceeding 500kW IT/operational load).

Not all 150 TWh of commercial/industrial electricity is consumed in
facilities above the 500kW threshold. Most commercial electricity is used
by small and medium enterprises (shops, offices, restaurants) that fall
below 500kW. The 500kW threshold targets data centres, large industrial
operations, automated warehouses, and similar facilities.

### 3.2 SEE Rate Structure

| Consumption Bracket | Rate (£/kWh) |
|---|---|
| 0-500kW | Exempt (small business protection) |
| 500kW-5MW | £0.05 |
| 5MW-50MW | £0.15 |
| >50MW | £0.30 |

### 3.3 Distribution Across Tiers

Estimated distribution of the 70 TWh tax base:

| Tier | Estimated TWh | Rate | Revenue |
|---|---|---|---|
| 500kW-5MW | 25 | £0.05/kWh | £1.2B |
| 5MW-50MW | 25 | £0.15/kWh | £3.8B |
| >50MW | 20 | £0.30/kWh | £6.0B |
| **Total SEE** | **70** | | **£11.0B** |

**Weighted average SEE rate: ~£0.16/kWh** (across the 70 TWh base).

### 3.4 Rate Adjustment

The rates above are conservative. To provide a meaningful revenue base
while remaining within the range commercial operators can absorb, a
moderate rate adjustment is proposed:

| Tier | Current Rate | Adjusted Rate | Rationale |
|---|---|---|---|
| 500kW-5MW | £0.05 | £0.08 | Still below commercial electricity price |
| 5MW-50MW | £0.15 | £0.20 | Approximately doubles energy cost for mid-tier |
| >50MW | £0.30 | £0.45 | Significant but absorbable for hyperscalers |

**Impact on data centre operating costs:**

Energy represents 30-40% of total data centre operating costs. Current
large DC electricity price (long-term PPA): £0.06-0.12/kWh.

| SEE Rate | Total energy cost | Energy increase | Total cost impact |
|---|---|---|---|
| £0.05/kWh | £0.15/kWh | 1.5x | +18% total costs |
| £0.20/kWh | £0.30/kWh | 3.0x | +70% total costs |
| £0.45/kWh | £0.55/kWh | 5.5x | +158% total costs |

At £0.45/kWh (top tier), a hyperscaler's total operating costs increase
by approximately 160%. This is severe but not fatal: all domestic
competitors face the same rate (no competitive distortion within the UK),
and the DCD ensures offshoring is more expensive (see Section 4).

**Adjusted SEE revenue (current base):**

| Tier | TWh | Adjusted Rate | Revenue |
|---|---|---|---|
| 500kW-5MW | 25 | £0.08/kWh | £2.0B |
| 5MW-50MW | 25 | £0.20/kWh | £5.0B |
| >50MW | 20 | £0.45/kWh | £9.0B |
| **Total SEE** | **70** | | **£16.0B** |

Non-compute commercial energy (manufacturing, logistics, automated
warehouses) adds a further ~60 TWh at lower weighted rates, contributing
approximately £8-12B. **Total SEE at launch: approximately £24-28B**
(2026 prices, see Section 3.6).

### 3.5 Context: Existing Energy Taxes

| Tax | Rate | Revenue |
|---|---|---|
| Climate Change Levy (CCL) | £0.00775/kWh | ~£2B |
| UK ETS (carbon trading) | Variable (~£50/tonne) | ~£5B |
| Fuel duty | £0.5298/litre | ~£25B |
| **Total energy/environment taxes** | | **~£50B** |

SEE at £24-28B would be the largest single energy tax, approximately 3x
the CCL but comparable to fuel duty. It is a step change, not without
precedent in UK fiscal policy.

### 3.6 CPI-Indexation

All SEBE rates (SEE and DCD) are CPI-indexed annually, rising
automatically with inflation. This follows the precedent of alcohol
duty, tobacco duty, and air passenger duty escalators.

Without indexation, SEBE rates erode in real value over time: at 3%
annual inflation, the £0.45/kWh top rate would be worth £0.33/kWh
in 2040 real terms. CPI-indexation prevents this.

**All revenue projections in this document are stated in 2026 real
prices.** Nominal revenue will be higher due to CPI adjustment of
rates. For example, at 3% annual CPI, the nominal £93B mid-scenario
for 2040 would be approximately £136B in nominal terms. The real
purchasing power is what matters for policy analysis.

---

## 4. DCD Revenue Derivation

### 4.1 DCD Design: Digital Customs Duty

DCD is a border tariff on commercial data crossing the UK digital border,
in either direction. It is not a general bandwidth tax.

**Who pays:**
- UK businesses using offshore cloud providers (AWS Ireland, Azure
  Netherlands, GCP Belgium)
- UK businesses calling offshore APIs (OpenAI US, Anthropic US)
- UK financial firms with offshore compute facilities
- UK companies using offshore SaaS platforms
- Any UK commercial entity whose data crosses the border

**Who does not pay:**
- UK consumers (exempt)
- UK businesses using UK-based data centres (pay SEE instead)
- Educational and research institutions (JANET, exempt)
- NHS and emergency services (exempt)
- Domestic DC-to-DC traffic (internal, pays SEE on energy)

### 4.2 DCD Rate Derivation

The DCD rate must make offshoring compute more expensive than operating
domestically (where the operator pays SEE). If DCD is cheaper than SEE
for the same workload, rational actors move offshore, which is the
opposite of the intended behaviour.

**Matching DCD to SEE-equivalent:**

For a given workload, the offshore operator avoids SEE by not being in
the UK. DCD must capture at least the same revenue from the data that
workload sends and receives across the border.

The ratio of energy consumed to data transferred varies by workload type:

| Workload Type | Energy per TB | Bandwidth per MW per year |
|---|---|---|
| AI inference (LLM) | Very high | ~200 TB/MW/year |
| Web/SaaS/database | Moderate | ~2,000 TB/MW/year |
| CDN/streaming | Low | ~20,000 TB/MW/year |

AI inference is energy-heavy and bandwidth-light. A 50K token input plus
2K token output (typical code review request) transfers approximately
1.6 MB but consumes significant GPU compute. This asymmetry is critical:
LLM workloads use far more energy per byte transferred than streaming or
web serving.

**Breakeven DCD rates by SEE tier:**

| SEE Tier | SEE Cost (per MW/yr) | Border Data (per MW/yr) | DCD Breakeven |
|---|---|---|---|
| 500kW-5MW (£0.08/kWh) | £0.8M | ~7,000 TB | £110/TB |
| 5MW-50MW (£0.20/kWh) | £2.0M | ~7,000 TB | £280/TB |
| >50MW (£0.45/kWh) | £4.3M | ~7,000 TB | £620/TB |

The bandwidth per MW figure uses a balanced workload mix (20% AI, 50%
web/SaaS, 30% CDN). This gives approximately 7,000 TB per MW per year
of sustained operation (at 85% utilisation, PUE 1.3).

**Proposed DCD rate: £300/TB**

At £300/TB:

| SEE Tier | Domestic cost (SEE) | Offshore cost (DCD) | Ratio |
|---|---|---|---|
| 500kW-5MW | £0.8M/MW/yr | £2.1M/MW/yr | Offshore 2.6x more expensive |
| 5MW-50MW | £2.0M/MW/yr | £2.1M/MW/yr | Roughly equal |
| >50MW | £4.3M/MW/yr | £2.1M/MW/yr | Domestic 2.0x more expensive |

This reveals a problem at the top tier: at £300/TB, the largest
facilities (>50MW at £0.45/kWh) would find offshoring cheaper than
domestic operation. The DCD rate must be higher, or the top SEE tier
lower, or both. Two options:

**Option A: Higher DCD rate (£500/TB)**

| SEE Tier | Domestic (SEE) | Offshore (DCD @£500) | Ratio |
|---|---|---|---|
| 500kW-5MW | £0.8M/MW/yr | £3.5M/MW/yr | Offshore 4.4x more expensive |
| 5MW-50MW | £2.0M/MW/yr | £3.5M/MW/yr | Offshore 1.8x more expensive |
| >50MW | £4.3M/MW/yr | £3.5M/MW/yr | Domestic 1.2x more expensive |

Still problematic at the top tier.

**Option B: Adjusted SEE top rate (£0.35/kWh) with DCD at £400/TB**

| SEE Tier | Domestic (SEE) | Offshore (DCD @£400) | Ratio |
|---|---|---|---|
| 500kW-5MW (£0.08) | £0.8M/MW/yr | £2.8M/MW/yr | Offshore 3.5x more |
| 5MW-50MW (£0.20) | £2.0M/MW/yr | £2.8M/MW/yr | Offshore 1.4x more |
| >50MW (£0.35) | £3.4M/MW/yr | £2.8M/MW/yr | Domestic 1.2x more |

The top tier remains marginal. This is inherent to the problem: the
largest facilities have the highest SEE rates, and DCD is a flat per-TB
rate that cannot be tier-matched without knowing the operator's energy
profile.

**Resolution: Tiered DCD**

DCD should be tiered by the offshore operator's scale (estimated from
traffic volume, which correlates with facility size):

| Annual border traffic | DCD Rate | Target |
|---|---|---|
| < 10 PB | £200/TB | Small/medium offshore use |
| 10-100 PB | £400/TB | Large enterprise offshore |
| > 100 PB | £800/TB | Hyperscaler-equivalent |

This ensures the DCD rate scales with the operator's likely energy
profile. A hyperscaler pushing >100 PB/year across the border is
almost certainly running a large offshore facility that would be in
the >50MW SEE tier if domestic.

### 4.3 Per-Unit Impact

At the proposed working rate of £300/TB (mid-tier):

| Activity | Data | DCD Cost | Notes |
|---|---|---|---|
| Single LLM request (50K+2K tokens) | 1.6 MB | 0.05p | Invisible |
| 1,000 LLM requests | 1.6 GB | 48p | Negligible |
| ChatGPT query (1.5K tokens) | 45 KB | 0.001p | Invisible |
| Web page load | 2 MB | 0.06p | Invisible |
| Email + 5MB attachment | 5 MB | 0.15p | Invisible |
| Video call (1 hour) | 1.5 GB | 45p | Noticeable over time |
| Software update (500 MB) | 500 MB | 15p | Negligible |
| Cloud backup (100 GB) | 100 GB | £30 | Material |
| Enterprise cloud (10 TB/month) | 10 TB | £3,000/month | Significant |

DCD is invisible to consumers (who are exempt anyway) and to individual
knowledge workers. It becomes material only at enterprise scale, where
it creates a genuine incentive to use UK-based providers.

### 4.4 DCD Revenue Estimate

**UK commercial cross-border data flows:**

| Category | Sustained Tbps (est.) |
|---|---|
| Enterprise cloud (IaaS/PaaS from IE/NL/DE) | 3-8 |
| SaaS platforms (US-hosted) | 1-4 |
| AI inference APIs (US-hosted) | 0.5-2 |
| Financial services offshore compute | 2-6 |
| B2B media/conferencing (offshore servers) | 1-3 |
| Ad tech / analytics | 0.5-2 |
| DevOps / code repos / CI/CD | 0.5-1.5 |
| Cloud backup / disaster recovery | 1-3 |
| **Total** | **9.5-29.5** |

1 Tbps sustained for 1 year = approximately 3,942,000 TB.

At the mid-estimate (19.5 Tbps) and weighted average DCD rate (~£300/TB):

- Annual cross-border data: ~76.9 million TB
- Gross DCD revenue: ~£23B

However, this declines over time as the deterrent effect works and
workloads repatriate to UK facilities (where they pay SEE instead).

**Realistic DCD revenue:**

The offshore share of compute serving the UK market is estimated at
approximately 38% (2025). As DCD incentivises domestic location:

| Year | Offshore share | DCD Revenue | Notes |
|---|---|---|---|
| 2030 (launch) | 35% | £8-12B | Initial, before repatriation |
| 2033 | 29% | £7-10B | Early movers repatriate |
| 2035 | 23% | £7-9B | Significant shift domestic |
| 2040 | 14% | £8-10B | Most compute domestic |
| 2045 | 10% | £10-19B | Floor (some always offshore), offset by volume growth |

DCD revenue is roughly stable in the early years (repatriation offsets
volume growth) then slowly grows as total compute demand overwhelms the
declining offshore share. But it is always secondary to SEE.

---

## 5. Combined SEBE Revenue

### 5.1 Year 1 (Launch, 2030)

| Component | Revenue (2026 prices) |
|---|---|
| SEE (~90 TWh taxable by 2030, adjusted rates) | £26-34B |
| DCD (cross-border, £300/TB avg) | £8-12B |
| **Total SEBE** | **£34-46B** |

The tax base is larger than the 2026 baseline (70 TWh) because 3-4
years of compute growth adds approximately 20 TWh of new taxable
capacity by 2030 (IEA projections). The mid-scenario estimate is £38B.

### 5.2 Growth Trajectory

SEBE revenue grows because the tax base grows. Automation increases
commercial energy consumption (more data centres, automated warehouses,
robotic manufacturing). The IEA projects global data centre electricity
demand growing from ~460 TWh (2022) to 1,500-2,000 TWh by 2030. UK
data centre electricity alone is projected to grow from ~10 TWh to
~30+ TWh by 2030.

For context: a single world-class hedge fund (GResearch/NMS) is
currently building a 234 MW data centre with its own power station in
Virginia. That single facility, at 85% utilisation with PUE 1.3,
consumes approximately 2.3 TWh/year. At the >50MW SEE rate of £0.30/kWh
(current), it would pay £690M/year in SEE. Several such facilities will
be built in the UK if the sovereign compute incentive works.

**Growth assumptions:**

| Factor | Rate | Basis |
|---|---|---|
| Data centre electricity growth | 15-25% pa | IEA projections, AI scaling |
| Automated industry growth | 8-12% pa | Robotics, electrification |
| Traditional commercial | 1% pa | Efficiency offsets growth |
| Taxable share of total | Rising 2pp/year | More facilities cross 500kW threshold |
| Offshore share | Declining 3pp/year | DCD deterrent effect, floor 10% |

**Projected SEBE revenue (2026 real prices, CPI-indexed rates):**

| Year | Total Compute (GW) | SEE Revenue | DCD Revenue | Total SEBE |
|---|---|---|---|---|
| 2030 (launch) | 6.9 | £30B | £8B | £38B |
| 2033 | 9.5 | £40B | £8B | £48B |
| 2035 | 12.1 | £50B | £7B | £57B |
| 2040 | 21.3 | £83B | £10B | £93B |
| 2045 | 37.6 | £140B | £19B | £159B |

The key observation: **SEE dominates and grows. DCD is the deterrent
fence that keeps compute domestic, where SEE can tax it.** DCD revenue
is secondary and roughly stable. Total SEBE grows because the thing
being taxed (automation infrastructure) is the fastest-growing sector
of the economy.

---

## 6. Stage 1 Ramp Model

### 6.1 Principle

SEBE does not fund full Stage 1 (UBI at £2,500 + UBS at £2,500 per
person) from day one. Instead, UBI and UBS ramp up together as SEBE
revenue grows. The mechanism is self-scaling: as automation replaces
workers, the tax on automation funds those workers' replacement income.

### 6.2 UBS Phasing

UBS components phase in over 5-8 years, starting with the most
impactful and cost-effective:

| Phase | Component | Net New Cost | Start Year |
|---|---|---|---|
| 1 | Free public transport | £14B (fares replacement) | Year 2 (2032) |
| 2 | Free energy (to threshold) | £8-40B (phased over 5 years) | Year 6 (2036) |
| 3 | Free broadband + mobile | £5B | Year 9 (2039) |

Existing government spending on transport subsidy (~£12B rail), energy
support (~£5B), and broadband programmes (~£1-2B) partially offsets these
costs. Net new spending is lower than gross UBS cost.

### 6.3 Year-by-Year Projection

Revenue is allocated first to UBS commitments, then the remainder funds
UBI. UBI grows automatically as revenue exceeds UBS costs.

All figures in 2026 real prices.

| Year | SEE | DCD | Feedback | Total | UBS Cost | Available | Adult UBI | Monthly |
|---|---|---|---|---|---|---|---|---|
| 2030 | £30B | £8B | £0B | £38B | £0B | £38B | £690/yr | £58/mo |
| 2032 | £37B | £8B | £8B | £53B | £14B | £39B | £700/yr | £58/mo |
| 2035 | £50B | £7B | £5B | £62B | £14B | £48B | £870/yr | £73/mo |
| 2036 | £55B | £7B | £5B | £67B | £22B | £45B | £820/yr | £68/mo |
| 2039 | £75B | £9B | £7B | £91B | £51B | £40B | £730/yr | £61/mo |
| 2040 | £83B | £10B | £8B | £101B | £59B | £42B | £760/yr | £63/mo |
| 2045 | £140B | £19B | £27B | £187B | £59B | £128B | £2,330/yr | £194/mo |

"Feedback" is the additional conventional tax revenue generated by UBI
spending (multiplier 0.8, marginal tax rate 33%).

Note: UBI dips in 2036 and 2039 as free energy and broadband phase in.
The family is still better off because UBS has direct cash-equivalent
value (free energy, transport, broadband worth ~£2,500/person/year at
full rollout).

### 6.4 Family Impact

Combined UBI + UBS value for a family of 4 (2 adults + 2 children):

All figures in 2026 real prices.

| Year | UBI (family) | UBS Value | Combined | Monthly |
|---|---|---|---|---|
| 2030 | £2,880 | £0 | £2,880 | £240 |
| 2032 | £2,900 | £836 | £3,736 | £311 |
| 2035 | £3,240 | £836 | £4,076 | £340 |
| 2040 | £3,020 | £3,522 | £6,542 | £545 |
| 2045 | £9,560 | £3,522 | £13,082 | £1,090 |

UBS value is the per-person cost of active UBS components multiplied
by family size. It represents the actual services received (free
transport, energy, broadband) which would otherwise cost the family
that amount.

### 6.5 Comparison to Option 1 (Broader Tax Package)

SEBE alone reaches £34-46B at launch (2030). If combined with other
progressive taxes that the Green Party already supports:

| Source | Estimated Revenue (2026 prices) |
|---|---|
| SEBE (SEE + DCD) | £34-46B |
| Land Value Tax | £40-70B |
| Wealth tax (2% on >£10M) | £20-40B |
| Financial Transaction Tax | £10-30B |
| Carbon tax (£100-200/tonne) | £15-30B |
| Corporation tax reform | £15-25B |
| Expanded Digital Services Tax | £3-8B |
| Employer NI on automation | £5-15B |
| Inheritance reform | £5-10B |
| **Total** | **£134-263B** |

With the UBI economic feedback loop (£30-95B in additional conventional
tax revenue), total available revenue reaches **£164-358B**. At the
upper end, this fully funds Stage 1 (net cost £337.5B) from year one.

SEBE's distinctive contribution is that it is the only component that
grows automatically with automation. The other taxes are largely
static or slow-growing. SEBE is the escalator; the other taxes are
the foundation.

---

## 7. Sovereign Compute Incentive

### 7.1 The Arbitrage Problem

If DCD is too low relative to SEE, rational actors offshore their
compute (avoiding SEE) and pay the lower DCD on cross-border data.
The rate structure must ensure offshoring is always more expensive
than domestic operation, at every tier.

### 7.2 Government as Compute Provider

The Amazon model: Amazon needed large-scale compute it could not buy,
so it built its own infrastructure and sold off excess capacity as
AWS. The UK government could follow the same approach:

- Build sovereign compute facilities (Bristol, Manchester, Edinburgh)
- Power with dedicated renewable generation
- Sell excess capacity to UK businesses at cost-plus
- Every workload on sovereign infrastructure pays SEE
- Reduces dependence on offshore hyperscalers

This accelerates the repatriation of compute and increases SEE revenue.
Government compute facilities would be subject to SEE like any other
operator, but the revenue flows back to the exchequer.

### 7.3 Ramp-Up Period

New data centre capacity takes 2-4 years to build. During the ramp-up
period (2030-2034), UK compute supply may not meet demand from
repatriating workloads. The DCD should include a transitional allowance:

- Year 1-2: DCD at 50% rate (reduced, acknowledging supply constraints)
- Year 3-4: DCD at 75% rate
- Year 5+: Full DCD rate

This gives the market time to build domestic capacity while signalling
the direction of travel.

---

## 8. Sensitivity Analysis

### 8.1 SEE Revenue Sensitivity

| Variable | Low | Mid | High |
|---|---|---|---|
| Taxable energy (TWh) | 60 | 70 | 85 |
| Weighted average rate | £0.16 | £0.25 | £0.35 |
| Non-compute energy (TWh) | 50 | 60 | 70 |
| **Year 1 SEE** | **£16B** | **£24B** | **£35B** |

### 8.2 DCD Revenue Sensitivity

| Variable | Low | Mid | High |
|---|---|---|---|
| Cross-border throughput (Tbps) | 9.5 | 19.5 | 29.5 |
| Weighted DCD rate (£/TB) | £200 | £300 | £500 |
| Offshore share | 30% | 38% | 45% |
| **Year 1 DCD** | **£4B** | **£8B** | **£15B** |

### 8.3 Growth Sensitivity

All figures in 2026 real prices.

| Scenario | 2030 (launch) | 2035 | 2040 | 2045 |
|---|---|---|---|---|
| Conservative (10% compute growth) | £34B | £47B | £70B | £108B |
| Mid (12% compute growth) | £38B | £57B | £93B | £159B |
| High (15% compute growth) | £44B | £74B | £135B | £260B |

The high scenario reflects aggressive AI scaling (consistent with
current IEA projections and industry investment patterns). The
conservative scenario assumes AI growth decelerates after 2030.

---

## 9. Corrections to Prior Documents

The following documents contain revenue figures that are superseded
by this analysis:

| Document | Section | Old Figure | Corrected Figure |
|---|---|---|---|
| academic_brief.md | 3.3 | SEE: £150-250B | SEE: £16-35B (year 1) |
| academic_brief.md | 3.3 | DCD: £50-250B | DCD: £4-15B (year 1) |
| academic_brief.md | 3.3 | Combined: £200-500B | Combined: £20-50B (year 1) |
| green_party_submission.md | 3.1 | SEE: £150-250B | SEE: £16-35B (year 1) |
| green_party_submission.md | 3.2 | DCD: £50-250B | DCD: £4-15B (year 1) |
| cost_model.md | 6.3 | Stage 1 fully funded by SEBE | Stage 1 ramps with SEBE growth |
| cost_model.md | 6.4 | £200-500B SEBE revenue | £20-50B year 1, growing to £93-260B by 2040 |
| glossary.md | DCD entry | £25-50/Mbps | £200-800/TB tiered by volume |
| AGENTS.md | Key Parameters | £200-500B revenue | £20-50B year 1, self-scaling |

The DCD unit changes from £/Mbps (which was ambiguous and economically
nonsensical) to £/TB (measurable, billable, comparable to cloud egress
pricing).

The bandwidth rate of £25-50/Mbps had no defined billing period and
implied costs of £625/second for a Netflix stream. The per-TB rate
is grounded in data centre economics and produces sensible per-unit
costs at every scale.

---

## 10. What This Means

SEBE at launch (2030) generates approximately **£34-46B/year** (2026
real prices, mid-scenario £38B). This is larger than Inheritance Tax
(£7B) plus Stamp Duty (£15B) plus Climate Change Levy (£2B) plus
Tobacco Duty (£10B) combined. It is a significant new revenue source,
but it does not fund full Stage 1 from day one.

What SEBE does that no other tax does: **it grows automatically with
the thing that replaces human employment.** Every new data centre,
every automated warehouse, every AI inference cluster increases the
SEE base. The revenue tracks the problem.

By 2040, SEBE is projected at **£93-135B/year** (mid-to-high scenario,
2026 prices). By 2045, **£159-260B/year**. Combined with the broader
progressive tax package and the UBI economic feedback loop, Stage 1 is
fully funded within 10-15 years of launch, with UBI growing every year.
Nominal revenue will be higher due to CPI-indexed rates (see Section 3.6).

The honest pitch: **SEBE starts modest and grows with automation. As
machines replace workers, the tax on machines funds the workers'
income. The mechanism is self-scaling.**

---

© 2026 Jason Huxley. Licensed under CC-BY 4.0.
