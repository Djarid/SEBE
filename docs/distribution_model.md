# SEBE Distribution Model

## What SEBE Revenue Could Fund

**Author:** Jason Huxley
**Version:** 2.0
**Date:** February 2026
**Status:** Working document (illustrative, not prescriptive)

---

## 1. Purpose

This document explores what SEBE revenue could fund. It is deliberately
separated from the core SEBE proposal because **SEBE is a tax mechanism,
not a welfare design**. The revenue could fund UBI, deficit reduction,
NHS expansion, or any combination. The distribution model below is one
illustrative option, worked through in detail to demonstrate fiscal
plausibility.

The core SEBE argument stands regardless of how the revenue is spent:
automation is eroding the income tax base, and SEBE replaces it.

---

## 2. Data Sources

| Source | Data | Date | Staleness |
|---|---|---|---|
| ONS ASHE 2025 | Median gross annual earnings (full-time): £39,039 | April 2025 (provisional) | Stale after Oct 2026 |
| ONS Mid-Year Population Estimates | UK population: 68.3 million | Mid-2023 | Stale after mid-2024 release |
| ONS 2022-based NPPs | UK population projections to 2047 | Jan 2025 | Stale after next NPP release (~2027) |
| Ofgem Price Cap | Typical household energy: £1,758/year | Q1 2026 | Reviewed quarterly |
| HMRC | Income tax and NI rates | 2025/26 tax year | Stale after April 2026 |
| ORR Rail Finance | Rail fares income: £11.5B, govt funding: £11.9B | 2024/25 | Annual (Nov) |
| OBR EFO | Welfare spending by category | Nov 2023 | Stale after Nov 2025 EFO |
| DWP PIP Statistics | PIP caseload by disabling condition (3.9M claims) | Oct 2025 | Quarterly (next Mar 2026) |

---

## 3. Population Breakdown

### 3.1 Current Estimate (Baseline)

UK population (mid-2023 estimate): **68.3 million**

| Group | Estimated count | Notes |
|---|---|---|
| Adults (18+) | ~55 million | ONS age structure |
| Children 0-2 | ~2 million | ~650k births/year x 3 cohorts |
| Children 3-11 | ~6 million | ~650k/year x 9 cohorts |
| Children 12-17 | ~4 million | ~650k/year x 6 cohorts |
| **Total children** | **~12 million** | |
| **Total population** | **~67 million** | Rounded for modelling |

### 3.2 Population Projections (ONS 2022-based NPPs)

SEBE launches in 2030 and revenue grows through 2045+. Distribution
costs must account for population growth over that period. The ONS
2022-based national population projections (published January 2025)
provide the best available estimates.

**Key ONS assumptions:**
- Long-term net international migration: 340,000/year (from mid-2028)
- Total fertility rate: 1.45 children per woman
- Deaths exceed births from 2029 onwards; all growth is migration-driven

**Projected UK population by milestone year:**

| Year | Total Pop | Adults (18+) | Children (0-17) | Source |
|---|---|---|---|---|
| 2023 (base) | 68.3M | 55.0M | 12.0M | ONS mid-year estimate |
| 2030 (launch) | 71.7M | 58.8M | 12.9M | ONS 2022-based NPP |
| 2035 | 73.3M | 60.1M | 13.2M | ONS 2022-based NPP |
| 2040 | 74.7M | 61.3M | 13.4M | ONS 2022-based NPP |
| 2045 | 76.0M | 62.3M | 13.7M | ONS 2022-based NPP |

**Children by age band (estimated from ONS age structure):**

| Year | 0-2 | 3-11 | 12-17 | Total children |
|---|---|---|---|---|
| 2030 | 1.9M | 5.7M | 4.0M | 11.6M |
| 2035 | 1.8M | 5.5M | 4.1M | 11.4M |
| 2040 | 1.8M | 5.4M | 4.1M | 11.3M |
| 2045 | 1.8M | 5.4M | 4.0M | 11.2M |

Notes:
- ONS projects 0-15 population declining from 12.4M (2022) to 11.6M
  (2032), reflecting low fertility (TFR 1.45). Child population
  stabilises thereafter.
- Adult population grows from net migration (predominantly working-age).
- The adult/child split used above (82%/18%) is derived from ONS age
  structure data. The adult share increases slightly over time as
  migration adds working-age adults and fertility stays below replacement.
- These projections carry uncertainty. ONS provides variant projections
  (high/low migration, high/low fertility) which produce a range of
  ±3M by 2045. The principal projection is used here.

**Cost implications of population growth:**

Using static 2023 figures (55M adults) understates the cost of UBI/ULI
at each future milestone. The tables in Sections 6 and 7 use projected
populations for the relevant year.

---

## 4. Median Income and ULI Derivation

### 4.1 Gross Median Earnings

**ONS ASHE April 2025 (full-time employees):**
- Median gross annual: **£39,039**
- Median gross weekly: **£766.60**

### 4.2 Why Median, Not Mean

Wage distributions have a long right tail (senior managers, partners,
professionals earning £100-300k+). Mean wages are inflated by this tail
and do not reflect what an ordinary worker takes home. Median answers
the relevant question directly: half of full-time workers earn more,
half earn less.

For ASHE data specifically, the skew from extreme wealth is minimal:
ASHE covers *employees* only (not self-employed, not capital income,
not investment returns). Billionaire wealth is capital, not salary,
and does not appear in ASHE. The difference between median and mean on
ASHE data is typically £3-5k (10-15%), not the orders of magnitude
seen in total income distributions.

A MAD-filtered mean (median ± 2 median absolute deviations, outliers
excluded) would give a marginally higher figure but adds methodological
complexity without meaningful policy benefit. Median is intuitive,
defensible, and standard for income policy analysis.

### 4.3 Tax and NI on Median Earnings

| Component | Calculation | Amount |
|---|---|---|
| Gross salary | | £39,039 |
| Personal allowance | First £12,570 tax-free | £0 |
| Income tax (basic rate 20%) | (£39,039 - £12,570) x 0.20 | £5,294 |
| Employee NI (8%) | (£39,039 - £12,570) x 0.08 | £2,118 |
| **Total deductions** | | **£7,412** |
| **Take-home pay** | | **£31,627** |

### 4.4 ULI Target Definition

ULI is defined as **the median full-time take-home pay at the point of
implementation**, minus UBS value. It is not a fixed nominal figure.

**Current derivation (ASHE 2025):**

| Component | Amount |
|---|---|
| Median take-home pay | £31,627 |
| Minus UBS value | -£2,500 |
| **ULI rate** | **£29,000** (rounded) |
| ULI + UBS combined | **£31,500** |

This is the **Stage 2 target**: equivalent to the living standard of a
median full-time earner at the date of implementation.

### 4.5 Indexation After Implementation

Once set, ULI is adjusted annually by CPI (or a successor cost-of-living
index). The £29,000 figure is illustrative of the *current* equivalent,
not a permanent fixed target.

**Why not track ongoing median wages?** As automation shrinks formal
employment, "median full-time wage" represents an increasingly
unrepresentative subset of the population. If only 30% of adults work
by 2045, the median wage of that 30% is meaningless as a living
standard benchmark. Anchoring to the implementation-date value and
CPI-adjusting avoids this problem.

**CPI behaviour under automation:** If automation substantially reduces
production costs (as argued in the academic brief, Section 6.2.1), CPI
growth may slow or turn negative. In a deflationary environment,
CPI-indexed ULI barely rises in nominal terms but purchasing power
*increases* because goods and services cost less. The real value of
£29,000 in a low-CPI environment is higher than today's £29,000.

This creates a favourable fiscal dynamic: SEBE revenue grows (driven
by compute base expansion, not inflation) while ULI costs grow slowly
(driven by CPI, which is dampened by automation). The gap widens in
the exchequer's favour. See `academic_brief.md` Section 6.5 for
further analysis.

---

## 5. Universal Basic Services (UBS)

UBS provides essential services free at point of use, up to a reasonable
threshold. Costs are estimated per person (averaged across household sizes).

### 5.1 Component Costs

| Component | Per person/year | Source/basis |
|---|---|---|
| Energy (gas + electricity) | £1,200 | Ofgem cap £1,758/household, averaged across household sizes |
| All public transport (bus + rail) | £280 | See 5.2 for derivation |
| Broadband (basic) | £330 | ~£27.50/month, shared household basis |
| Mobile + basic device | £200 | SIM-only ~£10/month + handset amortised over 3 years |
| Margin/contingency | £490 | Covers demand growth, regional variation |
| **UBS total** | **£2,500** | |

### 5.2 Transport Cost Derivation

Current fares revenue (ORR 2024/25):
- National rail fares: £11.5B/year
- Bus fares (estimated): ~£2.5B/year
- Total fares to replace: ~£14B

Per capita (2023): £14B / 67M = **£209/person/year**

Free public transport increases demand. Evidence from Luxembourg (free
since 2020), Tallinn (free since 2013), and city-level schemes shows
20-50% usage increases. Applying a 30% factor:

- Adjusted total: £14B x 1.3 = **£18.2B**
- Per capita (2023): £18.2B / 67M = **£272/person/year** (rounded to £280)
- Per capita (2040): £18.2B / 74.7M = **£244/person/year** (lower per-capita
  as population grows, but total cost rises with demand)

Note: government already funds £11.9B/year in rail subsidy (ORR 2024/25).
The net new cost is the fares revenue replacement (£11.5B), not the total
industry cost.

### 5.3 Rail Rent Extraction

Public ownership of rail infrastructure would eliminate significant private
rent extraction:

| Metric (2024/25) | Value |
|---|---|
| ROSCO dividends to shareholders | £275M (up 59.1% over 5 years) |
| Private operator dividend extraction | ~£144M |
| NR "allowances, bonuses and overtime" | £500M |
| **Total visible extraction** | **~£920M/year** |

Of £4.1B spent on rolling stock, £2.7B (66.3%) goes to ROSCO lease
payments. These are rents on publicly-built assets sold off in the 1990s.

Source: ORR Rail Industry Finance 2024/25.

---

## 6. Two-Stage Distribution Model

### 6.1 Stage 1: Universal Basic Income (UBI)

**Target rate: £2,500/adult/year (£208/month)**

A universal supplement. Existing benefits continue unchanged.

**Children's supplement (age-banded by incremental costs):**

| Age band | Annual supplement | Rationale |
|---|---|---|
| 0-2 (infant) | £5,000 | Equipment, nappies, formula/food, high parental demand |
| 3-11 | £3,500 | Food, clothing, school costs, activities |
| 12-17 | £4,000 | Higher food costs, social participation, technology |

Children's rates reflect actual costs, not a percentage of adult UBI.

### 6.2 Stage 1 Cost

Stage 1 at full target rate is reached some years after launch as SEBE
revenue grows. The table below uses ONS-projected 2040 population (the
earliest plausible date for approaching full Stage 1 with complementary
taxes). All figures in 2026 real prices.

| Component | Count (2040) | Rate | Annual cost |
|---|---|---|---|
| Adult UBI | 61.3M | £2,500 | £153.3B |
| Children 0-2 | 1.8M | £5,000 | £9.0B |
| Children 3-11 | 5.4M | £3,500 | £18.9B |
| Children 12-17 | 4.1M | £4,000 | £16.4B |
| **UBI subtotal** | | | **£197.6B** |
| UBS provision | 74.7M | £2,500 | £186.8B |
| **Stage 1 total** | | | **£384B** |

For comparison, the same calculation at 2023 static population (55M
adults, 67M total) gives £352B. Population growth adds ~£32B to the
full Stage 1 cost by 2040.

**SEBE at launch (2030) funds ~£34-46B (2026 prices).** Stage 1 at full
rate requires multiple revenue sources or years of SEBE growth. See
Section 7 for the ramp model.

### 6.3 Stage 2: Universal Living Income (ULI)

**Target: £29,000/adult/year (tax-free)**

Stage 2 is reached when automation has substantially replaced
employment and SEBE revenue (plus complementary taxes) can fund full
ULI. The table below uses ONS-projected 2045 population. All figures
in 2026 real prices.

| Component | Count (2045) | Rate | Annual cost |
|---|---|---|---|
| Adult ULI | 62.3M | £29,000 | £1.807T |
| Children 0-2 | 1.8M | £5,000 | £9.0B |
| Children 3-11 | 5.4M | £3,500 | £18.9B |
| Children 12-17 | 4.0M | £4,000 | £16.0B |
| **ULI subtotal** | | | **£1.851T** |
| UBS provision | 76.0M | £2,500 | £190.0B |
| **Stage 2 total** | | | **£2.041T** |

For comparison, the same calculation at 2023 static population gives
£1.810T. Population growth adds ~£231B to the full Stage 2 cost by 2045.

Stage 2 requires SEBE plus wealth tax (£50-80B), Land Value Tax
(£50-100B), Financial Transaction Tax (£20-50B), and expanded fiscal
space as automation increases productive capacity. The wage
restructuring effect (Section 9) and production cost reductions
create additional fiscal headroom not captured in these static figures.

---

## 7. Ramp Model and Feedback Loop

SEBE cannot fund full Stage 1 from day one. UBI and UBS ramp together
as revenue allows.

### 7.1 Illustrative Trajectory

All figures in 2026 real prices. All SEBE rates CPI-indexed annually.
Adult population uses ONS 2022-based projections for each year.

| Year | Adults | SEBE Revenue | UBS Cost | Available | Adult UBI | Monthly |
|---|---|---|---|---|---|---|
| 2030 (launch) | 58.8M | ~£38B | £0B | £38B | ~£650/yr | £54/mo |
| 2032 | 59.5M | ~£53B | £14B | £39B | ~£660/yr | £55/mo |
| 2035 | 60.1M | ~£62B | £14B | £48B | ~£800/yr | £67/mo |
| 2036 | 60.4M | ~£67B | £22B | £45B | ~£740/yr | £62/mo |
| 2039 | 61.0M | ~£91B | £51B | £40B | ~£660/yr | £55/mo |
| 2040 | 61.3M | ~£101B | £59B | £42B | ~£690/yr | £57/mo |
| 2045 | 62.3M | ~£187B | £59B | £128B | ~£2,050/yr | £171/mo |
| 2050+ | ~63M | ~£350B+ | £59B | £291B+ | ~£4,600+/yr | £383+/mo |

Note: UBI dips when new UBS components launch (they compete for the
same revenue), but each household is better off because UBS provides
direct cash-equivalent value. Population growth slightly reduces the
per-adult UBI compared to a static 55M figure, but overall revenue
growth more than compensates.

### 7.2 The Feedback Loop

1. SEBE generates £34-46B from automation infrastructure (2030 launch)
2. UBI distributed at ~£650/adult/year (58.8M adults, ONS 2030 projection)
3. Consumer spending increases (especially in deprived areas)
4. Increased economic activity generates additional conventional tax
   (income tax, VAT, corporation tax, business rates all rise)
5. Combined revenue allows UBI to increase
6. As automation displaces more jobs, SEBE revenue grows further
7. UBI ratchets upward; UBS components phase in

---

## 8. Existing Benefit Offsets

### 8.1 Stage 1 Offsets

At Stage 1, UBI is a supplement. Existing benefits continue. Direct
offsets are minimal:

| Benefit | Offset | Rationale |
|---|---|---|
| Child Benefit | **£12.5B** | Replaced by SEBE children's supplements (more generous) |
| Winter Fuel Payment | **~£2B** | Replaced by UBS energy provision |
| **Stage 1 total offset** | **~£14.5B** | |

**Net Stage 1 cost: ~£370B** (gross £384B minus ~£14.5B offset, at 2040
projected population)

### 8.2 Stage 2 Offsets

At Stage 2, ULI replaces most income-replacement benefits:

| Benefit Displaced | Offset | Confidence |
|---|---|---|
| State pension (basic + new) | ~£125B | High (direct replacement) |
| Pension Credit | ~£5B | High (means-tested, redundant at ULI) |
| Winter Fuel Payment | ~£2B | High (replaced by UBS energy) |
| UC/legacy income replacement | ~£40-50B | High (ULI exceeds UC rates) |
| UC/legacy + pensioner housing | ~£20-23B | Medium (requires companion housing policy) |
| PIP/DLA partial | ~£9.5-11.5B | Medium (see 8.3 for methodology) |
| Child Benefit | ~£12.5B | High (direct replacement) |
| Statutory Maternity/Paternity | ~£3B | High (ULI + child supplement covers it) |
| CMS administrative | ~£0.5B | Medium |
| Administrative savings | ~£5-7B | Medium (DWP means-testing apparatus) |
| **Total Stage 2 offset** | **~£222-240B** | |

**Net Stage 2 cost: ~£1.80-1.82T** (gross £2.041T minus ~£230B offset,
at 2045 projected population)

### 8.3 PIP/DLA Offset Methodology

Total PIP/DLA spending: ~£28B (OBR 2023-24). DWP PIP Statistics
(October 2025) show 3.9M claims by primary disabling condition:

| Condition | % of Caseload | ULI Offset Estimate |
|---|---|---|
| Psychiatric disorder | 39% | ~60-70% (financial stress is primary barrier) |
| Musculoskeletal disease | 31% | ~20-30% (recovery time helps, ongoing costs remain) |
| Neurological disease | 13% | ~10% (genuine additional costs: MS, Parkinson's) |
| Respiratory disease | 4% | ~10% (equipment and medication costs) |
| Other | 13% | ~20% |
| **Weighted total** | | **~34-41%** |

Applied to ~£28B: **£9.5-11.5B offset**

**Caveat:** Uses caseload proportions, not condition-level spend data
(not publicly available). The 30-40% range is indicative.

### 8.4 Housing Benefit Offset Rationale

Three factors reduce housing benefit under ULI:

1. **Means-testing:** ULI at £29,000 exceeds most eligibility thresholds
2. **Post-employment migration:** No need to live near expensive workplaces
   (COVID-19 demonstrated this dispersal effect)
3. **Lifestyle choice:** Living in an expensive city becomes a choice, not
   a necessity. The state has no obligation to subsidise location preference.

Residual housing support (~£2-5B) is a housing market problem, best
addressed through LVT, public housing investment, and planning reform.

### 8.5 Benefits NOT Offset

- **PIP/DLA residual (~£17-20B):** Genuine additional costs (specialist
  equipment, adapted environments, personal care) are not addressed by
  income alone
- **Carer's Allowance (~£4B):** Caring is a vocation and should be
  recognised as state-paid employment, not offset

---

## 9. Wage Restructuring Under ULI

### 9.1 Employment Becomes Voluntary

Under full ULI (£29,000/adult + £2,500 UBS = £31,500 combined), nobody
works to survive. Employment provides supplementary income, social
purpose, or personal satisfaction. This fundamentally restructures the
labour market and business cost base.

### 9.2 Three Categories of Future Work

**Essential but unpleasant work (care, sanitation, construction):**
wages rise significantly. With ULI providing a comfortable floor,
employers must offer a genuine premium to attract workers to roles that
are physically demanding, emotionally taxing, or unpleasant. The worse
the conditions, the higher the premium. This inverts current wage
dynamics, where desperation forces people into poorly paid essential
work.

However, the premium is for *emotional labour and human presence*, not
physical drudge. Automation handles the heavy lifting (literally):
robotic aids for patient handling, automated waste systems, construction
robotics. The human care worker's role becomes companionship, emotional
support, and human judgment, assisted by machines. Some people are
genuinely drawn to this work, but the proportion is small, and ULI
removes the coerced majority. Wages remain high.

**Specialist roles (surgery, engineering, diagnostics):** largely
automated. AI diagnostic models already exceed human capability in
pattern recognition (radiology, pathology, dermatology). Robotic
surgery offers precision without fatigue, distraction, or bad days.
There is a near-term moral obligation to transition to automated
specialists once the technology demonstrably outperforms humans: the
alternative is knowingly subjecting patients and users to inferior,
error-prone human performance.

The residual human role is oversight and consent: "here are my findings,
proceed?" Humans may authorise or abort a procedure but will
increasingly be prohibited from overriding or taking over from a more
capable automated system. Fewer specialists are needed, and their role
is supervisory, not operational.

**Human interface work (hospitality, teaching, counselling, creative):**
this is where future voluntary employment concentrates. The product is
the human relationship itself, not the information or service delivered.
A therapist is a human presence, not a CBT delivery mechanism. A
teacher models adulthood, not just curriculum. A waiter provides a
social experience, not just food delivery.

Human service carries a premium. "Served by a human" becomes the
equivalent of "handmade" for goods: a marker of quality, authenticity,
and luxury that some people will pay for and others will not. This
creates a genuine artisanal/vocational economy with real wages,
voluntarily entered, funded by people choosing to spend their ULI
(and any supplementary income) on human experiences.

### 9.3 Business Cost Base Effects

The combined effect on the business cost base:

1. **Automation reduces per-unit production costs.** Energy per unit of
   output falls, material waste decreases, throughput increases.
2. **Total salary overhead shrinks.** Fewer employees needed. Those who
   remain are voluntary and supplementary to ULI. Employers do not need
   to fund survival (housing, food, heating) through wages, only
   attractiveness premiums for the specific role.
3. **Some individual wages rise** (essential care, unpleasant work) but
   total payroll falls because headcount drops faster than average
   wages rise.
4. **Profit margins expand.** Lower costs, same or higher output.
5. **More taxable profit = more conventional tax revenue** (corporation
   tax, business rates) even as employment falls.

This creates a second fiscal feedback loop, distinct from the consumer
spending multiplier:

- SEBE taxes automation infrastructure
- Automation reduces business costs and replaces labour
- Lower costs → higher profits → more corporation tax
- More conventional tax revenue → more fiscal space for ULI
- Higher ULI → more voluntary spending → more economic activity

### 9.4 Inequality Under ULI

ULI sets the floor, not the ceiling. Income inequality above the floor
is an intentional feature, not a defect. Enforced equality stifles
human agency and motivation (the lesson of every communist experiment).
Under ULI:

- The floor (£31,500 combined) is high enough that nobody suffers
- Premium wages for essential/unpleasant work reward genuine scarcity
- Artisanal and creative work is valued by market mechanisms
- Voluntary exchange (your painting for their chair) is genuinely free
  because neither party trades under duress
- Markets continue to function as allocation mechanisms, they just stop
  being survival mechanisms

This is closer to a genuine free market than the current system, where
most people accept employment terms under implicit threat of destitution.

---

## 10. Sensitivity Analysis

### 10.1 Population Changes

Each additional million adults at Stage 1 adds ~£2.5B to costs. More
people also means more economic activity and more SEBE-taxable automation.
ONS projections (Section 3.2) are used throughout. Variant projections
(high/low migration) produce a range of ±3M by 2045.

### 10.2 Inflation Risk

Stage 1 is anti-inflationary: SEBE withdraws revenue from corporations,
UBI at ~£650/year is minimal, UBS directly reduces household costs.
Automation simultaneously reduces production costs (see academic brief
Section 6.2.1), further dampening inflationary pressure.

Stage 2 inflation risk is real and requires MMT-informed fiscal management.
However, the wage restructuring effect (Section 9) and production cost
reductions from automation create substantial deflationary pressure that
partially offsets the demand-side stimulus of ULI.

### 10.3 CPI Indexation

All UBI/ULI/UBS values and SEBE rates must be pegged to CPI (or a
comparable index) to maintain real value. Without indexation, the same
erosion that hollowed out Child Benefit applies.

---

## 11. Comparison to Previous Model

| Parameter | Previous (v1) | Current (v2) |
|---|---|---|
| UBI/ULI rate | £30,000 (single stage) | £2,500 rising to £29,000 (two stage) |
| UBS value | £2,000 | £2,500 |
| Children's rate | Not specified | Banded: £3,500-5,000 by age |
| Gross total requirement | £2.144 trillion | Stage 1: £384B (2040 pop), Stage 2: £2.041T (2045 pop) |
| Existing welfare offset | Not considered | Stage 1: ~£14.5B, Stage 2: ~£230B |
| Population basis | Not specified | ONS 2022-based projections at each milestone year |
| Median basis | £32,890 (outdated, gross) | £39,039 (ASHE 2025, take-home adjusted) |
| CPI indexation | Not specified | All values pegged to CPI |

---

## 12. Outstanding Questions

1. **Transition dynamics:** How fast does UBI ratchet up? What triggers
   each increase? Requires macroeconomic simulation.
2. **Green Party EC730 alignment:** Children's supplement structure should
   be checked against existing Green Party UBI policy.
3. **Regional variation:** UBS costs vary by region. A flat rate may
   under-serve rural and northern areas.
4. **Interaction with existing benefits:** Edge cases (contributory
   benefits, transitional protection, devolved benefits in Scotland/NI)
   need detailed policy design.
5. **Transport capacity investment:** Free transport increases demand.
   The 30% uplift factor covers operational costs but not long-term
   capital investment.

---

*This document is illustrative. SEBE is a tax mechanism. How the revenue
is spent is a separate political decision. The workings here demonstrate
that the revenue is meaningful and that a staged approach to universal
income is fiscally plausible.*

---

(c) 2026 Jason Huxley. Licensed under CC-BY 4.0.
