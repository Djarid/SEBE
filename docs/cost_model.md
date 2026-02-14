# SEBE Cost Model

## Revenue, Distribution, and Transition Framework

**Author:** Jason Huxley
**Version:** 1.0
**Date:** February 2026
**Status:** Working document (figures subject to revision as data updates)

---

## 1. Overview

This document shows the working behind SEBE's revenue estimates, distribution
costs, and the two-stage transition from Universal Basic Income (UBI) to
Universal Living Income (ULI). All sources are cited. All assumptions are
stated explicitly.

---

## 2. Data Sources

| Source | Data | Date | Staleness |
|---|---|---|---|
| ONS ASHE 2025 | Median gross annual earnings (full-time): £39,039 | April 2025 (provisional) | Stale after Oct 2026 |
| ONS Mid-Year Population Estimates | UK population: 68.3 million | Mid-2023 | Stale after mid-2024 release |
| Ofgem Price Cap | Typical household energy: £1,758/year | Q1 2026 | Reviewed quarterly |
| HMRC | Income tax and NI rates | 2025/26 tax year | Stale after April 2026 |
| ONS AWE | Average weekly earnings (total pay): £741 | November 2025 | Monthly updates |
| ORR Rail Finance | Rail fares income: £11.5B, govt funding: £11.9B | 2024/25 | Annual (Nov) |

**ONS ASHE reference:**
ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/bulletins/annualsurveyofhoursandearnings/2025

**ONS Population reference:**
ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/bulletins/annualmidyearpopulationestimates/mid2023

---

## 3. Population Breakdown

UK population (mid-2023 estimate): **68.3 million**

| Group | Estimated count | Notes |
|---|---|---|
| Adults (18+) | ~55 million | ONS age structure |
| Children 0-2 | ~2 million | ~650k births/year × 3 cohorts |
| Children 3-11 | ~6 million | ~650k/year × 9 cohorts |
| Children 12-17 | ~4 million | ~650k/year × 6 cohorts |
| **Total children** | **~12 million** | |
| **Total population** | **~67 million** | Rounded for modelling |

Note: The 68.3M ONS figure includes the entire usually resident population.
For modelling, 67M is used (rounding, and excluding non-eligible residents).
Exact eligibility criteria are a policy design question.

---

## 4. Median Income and Tax Burden

### 4.1 Gross Median Earnings

**ONS ASHE April 2025 (full-time employees):**
- Median gross annual: **£39,039**
- Median gross weekly: **£766.60**

Full-time median is used as the reference point because it represents the
earnings of a person in sustained employment. This is the standard of living
that ULI (Stage 2) aims to match on a tax-free basis.

### 4.2 Tax and National Insurance on Median Earnings

Calculated using 2025/26 HMRC rates:

| Component | Calculation | Amount |
|---|---|---|
| Gross salary | | £39,039 |
| Personal allowance | First £12,570 tax-free | £0 |
| Income tax (basic rate 20%) | (£39,039 - £12,570) × 0.20 | £5,294 |
| Employee NI (8%) | (£39,039 - £12,570) × 0.08 | £2,118 |
| **Total deductions** | | **£7,412** |
| **Take-home pay** | | **£31,627** |

### 4.3 Effective Living Standard Target

ULI is tax-free. To match the spending power of a median earner:

| Component | Amount |
|---|---|
| Median take-home pay | £31,627 |
| Rounded for modelling | **£31,500** |

This is the **Stage 2 target**: ULI + UBS = £31,500 effective.

---

## 5. Universal Basic Services (UBS)

UBS provides essential services free at point of use, up to a reasonable
threshold. Costs are estimated per person (averaged across household sizes).

### 5.1 UBS Component Costs

| Component | Per person/year | Source/basis |
|---|---|---|
| Energy (gas + electricity) | £1,200 | Ofgem cap £1,758/household, averaged across household sizes |
| All public transport (bus + rail) | £280 | See 5.2 for derivation |
| Broadband (basic) | £330 | ~£27.50/month, shared household basis |
| Mobile + basic device | £200 | SIM-only ~£10/month + handset amortised over 3 years |
| Margin/contingency | £490 | Covers demand growth, regional variation |
| **UBS total** | **£2,500** | |

### 5.2 Notes on UBS Costing

**Energy** is the largest component. Single-person households pay the full
Ofgem cap (~£1,758). Multi-person households share. £1,200 averaged is
conservative.

**Transport** includes all public transport: local bus, regional rail, and
national rail, free at point of use.

Current fares revenue (ORR 2024/25, orr.gov.uk):
- National rail fares: £11.5B/year
- Bus fares (estimated): ~£2.5B/year
- Total fares to replace: ~£14B

Per capita: £14B ÷ 67M = **£209/person/year**

However, free public transport increases demand. Evidence from Luxembourg
(free since 2020), Tallinn (free since 2013), and numerous city-level
schemes consistently shows 20-50% usage increases. Applying a 30% demand
growth factor:

- Adjusted total: £14B × 1.3 = **£18.2B**
- Per capita: £18.2B ÷ 67M = **£272/person/year** (rounded to £280)

The marginal cost of additional passengers is low in the short term (trains
and buses are already running, many services run below capacity off-peak).
Medium-term costs include additional rolling stock and frequency. These are
capital investments that create jobs and reduce road congestion and emissions,
aligning with Green Party transport and climate policy.

Note: government already funds £11.9B/year in rail subsidy (ORR 2024/25).
The net new cost of making rail free is the fares revenue replacement
(£11.5B), not the total industry cost.

**Broadband and mobile** are basic tiers, not unlimited premium services.

**UBS does not replace** housing costs, food, or clothing. These are funded
from UBI/ULI cash payments.

### 5.3 Rail Rent Extraction: Where the Money Currently Goes

Public ownership of rail infrastructure would eliminate significant private
rent extraction, reducing the effective cost of free rail. The following data
is from ORR's Rail Industry Finance report (April 2024 to March 2025).

**Rolling Stock Companies (ROSCOs):**

Six companies (Angel Trains, Beacon Rail Finance, Eversholt Rail Leasing,
Porterbrook Leasing Company, VTG Rail UK, Corelink Rail Infrastructure) own
virtually all UK rolling stock and lease it to operators.

| Metric (2024/25) | Value | 5-year change |
|---|---|---|
| Total ROSCO income | £1.3B | Down 29.2% |
| Total ROSCO expenditure | £1.0B | Down 36.7% |
| Net profit margin | 18.5% | **Up 10 percentage points** |
| Dividends to shareholders | £275M | **Up 59.1%** |

The pattern is clear: income down, expenditure down further, but profit
margins and dividends both increasing sharply. Less service, more extraction.

Of the £4.1B spent on rolling stock by train operators, £2.7B (66.3%) goes
to ROSCO lease payments. These are rents on assets that were publicly owned
before the 1990s privatisation, sold off cheaply, and now leased back to
the public railway at enormous margins.

**Train Operator Dividends:**

| Metric (2024/25) | Value |
|---|---|
| Franchised operator dividends | £164M |
| Of which: publicly owned operators (returned to govt) | ~£20M |
| Private operator dividend extraction | ~£144M |

**Network Rail Executive Costs:**

| Metric (2024/25) | Value |
|---|---|
| NR staff "allowances, bonuses and overtime" | £500M |

**Total visible private extraction: ~£920M/year**

This figure understates the true extraction because it excludes parent
company management fees, intercompany loans, and other profit-shifting
mechanisms commonly used by multinational rail operators.

**Policy implication:** Public ownership of rolling stock alone would
eliminate £275M/year in ROSCO dividends and redirect the £2.7B in lease
payments toward actual rolling stock investment. Combined with ending
private operator dividends (£144M), public ownership recovers over
**£400M/year** in pure rent extraction before any operational efficiencies.

This does not fund free rail by itself (that requires SEBE), but it
significantly reduces the cost and eliminates the perverse incentive
structure where operators profit from underinvestment.

Source: ORR, Rail Industry Finance (UK), April 2024 to March 2025.
Published 25 November 2025.
dataportal.orr.gov.uk/statistics/finance/rail-industry-finance/

---

## 6. Two-Stage Distribution Model

### 6.1 Rationale

SEBE's estimated revenue (£200-500B/year) cannot fund full ULI (£29,000/adult)
from day one. However, it can fund a meaningful universal supplement
immediately, which grows as automation (and therefore SEBE revenue) increases.

This two-stage approach:
- Makes Stage 1 **fully fundable from SEBE alone**
- Removes the "people will stop working" objection (Stage 1 is a supplement)
- Creates a **self-reinforcing feedback loop** (more spending, more tax revenue)
- Allows organic transition as the economy shifts

### 6.2 Stage 1: Universal Basic Income (UBI)

**UBI at £2,500/adult/year (£208/month)**

A universal supplement to existing income. Not a replacement.

- Existing benefits (JSA, UC, PIP, etc.) continue unchanged
- Unemployed receive existing benefits PLUS UBI
- Employed receive wages PLUS UBI
- Pensioners receive state pension PLUS UBI
- UBI is tax-free and unconditional

**Children's supplement (paid to parent/guardian in child's name):**

| Age band | Annual supplement | Rationale |
|---|---|---|
| 0-2 (infant) | £5,000 | Equipment, nappies, formula/food, high parental demand |
| 3-11 | £3,500 | Food, clothing, school costs, activities |
| 12-17 | £4,000 | Higher food costs, social participation, technology |

Children's rates reflect actual incremental costs of a child in an existing
household. They are not a percentage of adult UBI. Children share housing,
heating, and most infrastructure with their parent(s).

### 6.3 Stage 1 Cost

| Component | Count | Rate | Annual cost |
|---|---|---|---|
| Adult UBI | 55M | £2,500 | £137.5B |
| Children 0-2 | 2M | £5,000 | £10B |
| Children 3-11 | 6M | £3,500 | £21B |
| Children 12-17 | 4M | £4,000 | £16B |
| **UBI subtotal** | | | **£184.5B** |
| UBS provision | 67M | £2,500 | £168B |
| **Stage 1 total** | | | **£352.5B** |

**SEBE revenue (estimated): £200-500 billion/year**

At the midpoint of SEBE estimates (~£350B), Stage 1 is fully funded.
At the lower bound (£200B), UBI can begin at a reduced rate while UBS
scales up progressively.

### 6.4 Stage 1 Economic Feedback Loop

1. SEBE generates £200-500B from automation infrastructure
2. £184.5B distributed as UBI (55M adults + 12M children)
3. £168B funds UBS (free energy, transport, broadband, mobile)
4. £2,500 per adult hits 55 million bank accounts
5. Consumer spending surges (especially in deprived areas)
6. High street, hospitality, local services recover
7. Increased economic activity generates additional conventional tax revenue
   (income tax, VAT, corporation tax, business rates all rise)
8. Combined revenue (SEBE + conventional) allows UBI to increase
9. As automation displaces more jobs, SEBE revenue grows further
10. UBI ratchets upward toward ULI

### 6.5 Stage 2: Universal Living Income (ULI)

**ULI target: £29,000/adult/year (tax-free)**

Stage 2 is the endgame, reached when automation has displaced enough
employment that UBI must transition from supplement to primary income.

| Component | Amount |
|---|---|
| ULI payment (adult) | £29,000 |
| UBS value | £2,500 |
| **Effective living standard** | **£31,500** |
| Equivalent gross salary | ~£39,000 |

This matches the take-home pay of the current full-time median earner.

**Stage 2 full cost:**

| Component | Count | Rate | Annual cost |
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
capacity. The exact transition trajectory is a macroeconomic question for
specialist modelling.

### 6.6 Transition Timeline

The transition from Stage 1 to Stage 2 is not a fixed date. It is driven by:

- Growth in automation (and therefore SEBE revenue)
- Decline in employment (and therefore need for higher UBI)
- Conventional tax revenue from the UBI stimulus effect
- Inflation dynamics and productive capacity

The two stages are endpoints. In practice, UBI increases incrementally as
revenue allows. A plausible (illustrative, not predictive) trajectory:

| Year | Adult UBI | Approximate cost | Notes |
|---|---|---|---|
| Year 1 | £2,500 | £185B | Stage 1 launch, SEBE funded |
| Year 3 | £5,000 | £275B + children | Stimulus revenue reinvested |
| Year 5 | £10,000 | £550B + children | Automation displacement accelerating |
| Year 10 | £20,000 | £1.1T + children | Significant employment decline |
| Year 15+ | £29,000 | £1.6T + children | Stage 2 (ULI), full transition |

These figures are illustrative only. Actual trajectory depends on automation
adoption rates, SEBE revenue growth, and macroeconomic conditions.

---

## 7. Comparison to Previous Model

| Parameter | Previous model | Revised model |
|---|---|---|
| UBI/ULI rate | £30,000 (single stage) | £2,500 rising to £29,000 (two stage) |
| UBS value | £2,000 | £2,500 |
| Children's rate | Not specified | Banded: £3,500-5,000 by age |
| Total requirement | £2.144 trillion | Stage 1: £352B, Stage 2: £1.810T |
| SEBE coverage | 9-23% | Stage 1: 57-142% |
| Fundable from SEBE alone | No | **Yes (Stage 1)** |
| Median basis | £32,890 (outdated, gross) | £39,039 (ASHE 2025, take-home adjusted) |
| Tax treatment | Compared to gross salary | Correctly compared to take-home pay |

Key improvement: Stage 1 is credibly fundable from SEBE alone, without
requiring wealth tax, LVT, or other revenue sources. This makes the
immediate proposal politically achievable.

---

## 8. Sensitivity Analysis

### 9.1 SEBE Revenue Uncertainty

The £200-500B range reflects uncertainty in:
- Actual commercial energy consumption subject to SEBE
- Behavioural response (energy efficiency investment)
- Bandwidth growth rates
- Enforcement effectiveness
- Rate-setting decisions

### 9.2 Population Changes

UK population is growing (~0.5-1% per year, driven by net migration).
Each additional million adults at Stage 1 adds ~£2.5B to costs. This is
self-limiting: more people also means more economic activity and more
SEBE-taxable automation serving them.

### 9.3 Inflation Risk

UBI is anti-inflationary at Stage 1 because:
- SEBE withdraws revenue from corporations (deflationary)
- UBI is small relative to existing incomes (minimal demand shock)
- UBS directly reduces household costs (deflationary for recipients)

At Stage 2 (full ULI), inflation risk is real and requires MMT-informed
fiscal management. This is acknowledged as an area requiring specialist
economic modelling.

---

## 9. Outstanding Questions

These are acknowledged gaps, not hidden weaknesses:

1. **SEBE revenue model:** This document covers distribution costs but not
   revenue derivation. The £200-500B estimate needs a dedicated revenue
   model built from BEIS/DESNZ energy consumption data, Ofcom bandwidth
   statistics, and the proposed SEE/DCD rate schedules. This is a separate
   document (planned).

2. **Transition dynamics:** How fast does UBI ratchet up? What triggers
   each increase? This requires macroeconomic simulation.

3. **Green Party EC730 alignment:** The children's supplement structure
   should be checked against the Green Party's existing UBI policy for
   compatibility.

4. **Regional variation:** UBS costs (especially energy and transport)
   vary significantly by region. A flat national rate may under-serve
   rural and northern areas.

5. **Interaction with existing benefits:** How does UBI interact with
   UC, PIP, pension credit, housing benefit? Preserving existing benefits
   is the stated approach, but edge cases need detailed policy design.

6. **Transport capacity investment:** Free public transport will increase
   demand beyond current levels. The 30% uplift factor used in UBS costing
   covers operational costs but not long-term capital investment in rolling
   stock and infrastructure. This is a net positive (jobs, emissions
   reduction) but needs explicit modelling.

---

© 2026 Jason Huxley. Licensed under CC-BY 4.0.
