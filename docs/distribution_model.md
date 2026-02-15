# SEBE Distribution Model

## What SEBE Revenue Could Fund

**Author:** Jason Huxley
**Version:** 1.0
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
| Ofgem Price Cap | Typical household energy: £1,758/year | Q1 2026 | Reviewed quarterly |
| HMRC | Income tax and NI rates | 2025/26 tax year | Stale after April 2026 |
| ORR Rail Finance | Rail fares income: £11.5B, govt funding: £11.9B | 2024/25 | Annual (Nov) |
| OBR EFO | Welfare spending by category | Nov 2023 | Stale after Nov 2025 EFO |
| DWP PIP Statistics | PIP caseload by disabling condition (3.9M claims) | Oct 2025 | Quarterly (next Mar 2026) |

---

## 3. Population Breakdown

UK population (mid-2023 estimate): **68.3 million**

| Group | Estimated count | Notes |
|---|---|---|
| Adults (18+) | ~55 million | ONS age structure |
| Children 0-2 | ~2 million | ~650k births/year x 3 cohorts |
| Children 3-11 | ~6 million | ~650k/year x 9 cohorts |
| Children 12-17 | ~4 million | ~650k/year x 6 cohorts |
| **Total children** | **~12 million** | |
| **Total population** | **~67 million** | Rounded for modelling |

---

## 4. Median Income and ULI Derivation

### 4.1 Gross Median Earnings

**ONS ASHE April 2025 (full-time employees):**
- Median gross annual: **£39,039**
- Median gross weekly: **£766.60**

### 4.2 Tax and NI on Median Earnings

| Component | Calculation | Amount |
|---|---|---|
| Gross salary | | £39,039 |
| Personal allowance | First £12,570 tax-free | £0 |
| Income tax (basic rate 20%) | (£39,039 - £12,570) x 0.20 | £5,294 |
| Employee NI (8%) | (£39,039 - £12,570) x 0.08 | £2,118 |
| **Total deductions** | | **£7,412** |
| **Take-home pay** | | **£31,627** |

### 4.3 ULI Target

ULI is tax-free. To match the spending power of a median earner:

| Component | Amount |
|---|---|
| Median take-home pay | £31,627 |
| Minus UBS value | -£2,500 |
| **ULI rate** | **£29,000** (rounded) |
| ULI + UBS combined | **£31,500** |

This is the **Stage 2 target**: equivalent to a median full-time salary.

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

Per capita: £14B / 67M = **£209/person/year**

Free public transport increases demand. Evidence from Luxembourg (free
since 2020), Tallinn (free since 2013), and city-level schemes shows
20-50% usage increases. Applying a 30% factor:

- Adjusted total: £14B x 1.3 = **£18.2B**
- Per capita: £18.2B / 67M = **£272/person/year** (rounded to £280)

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

| Component | Count | Rate | Annual cost |
|---|---|---|---|
| Adult UBI | 55M | £2,500 | £137.5B |
| Children 0-2 | 2M | £5,000 | £10B |
| Children 3-11 | 6M | £3,500 | £21B |
| Children 12-17 | 4M | £4,000 | £16B |
| **UBI subtotal** | | | **£184.5B** |
| UBS provision | 67M | £2,500 | £167.5B |
| **Stage 1 total** | | | **£352B** |

**SEBE at launch funds ~£31-38B.** Stage 1 at full rate requires multiple
revenue sources or years of SEBE growth. See Section 7 for the ramp model.

### 6.3 Stage 2: Universal Living Income (ULI)

**Target: £29,000/adult/year (tax-free)**

| Component | Count | Rate | Annual cost |
|---|---|---|---|
| Adult ULI | 55M | £29,000 | £1.595T |
| Children 0-2 | 2M | £5,000 | £10B |
| Children 3-11 | 6M | £3,500 | £21B |
| Children 12-17 | 4M | £4,000 | £16B |
| **ULI subtotal** | | | **£1.642T** |
| UBS provision | 67M | £2,500 | £167.5B |
| **Stage 2 total** | | | **£1.810T** |

Stage 2 requires SEBE plus wealth tax (£50-80B), Land Value Tax
(£50-100B), Financial Transaction Tax (£20-50B), and expanded fiscal
space as automation increases productive capacity.

---

## 7. Ramp Model and Feedback Loop

SEBE cannot fund full Stage 1 from day one. UBI and UBS ramp together
as revenue allows.

### 7.1 Illustrative Trajectory

| Year | SEBE Revenue | Adult UBI | UBS Status | Notes |
|---|---|---|---|---|
| 2027 (launch) | ~£31B | ~£400/yr | Launching | SEBE funds UBI immediately |
| 2030 | ~£45B | ~£400/yr | Transport free | Revenue absorbed by UBS expansion |
| 2035 | ~£62B | ~£150/yr | Full UBS | UBI dips as energy provision phases in |
| 2040 | ~£101B | ~£550/yr | Full UBS | UBI recovering, automation scaling |
| 2045 | ~£187B | ~£1,750/yr | Full UBS | Significant supplementary income |
| 2050+ | ~£350B+ | ~£5,000+/yr | Full UBS | Approaching original Stage 1 target |

Note: UBI dips when new UBS components launch (they compete for the
same revenue), but each household is better off because UBS provides
direct cash-equivalent value.

### 7.2 The Feedback Loop

1. SEBE generates £31-38B from automation infrastructure (year 1)
2. UBI distributed at ~£400/adult/year (55M adults)
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

**Net Stage 1 cost: ~£337.5B** (gross £352B minus £14.5B offset)

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

**Net Stage 2 cost: ~£1.57-1.59T** (gross £1.810T minus ~£230B offset)

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

## 9. Sensitivity Analysis

### 9.1 Population Changes

Each additional million adults at Stage 1 adds ~£2.5B to costs. More
people also means more economic activity and more SEBE-taxable automation.

### 9.2 Inflation Risk

Stage 1 is anti-inflationary: SEBE withdraws revenue from corporations,
UBI at £400/year is minimal, UBS directly reduces household costs.

Stage 2 inflation risk is real and requires MMT-informed fiscal management.
This is acknowledged as requiring specialist modelling.

### 9.3 CPI Indexation

All UBI/ULI/UBS values and SEBE rates must be pegged to CPI (or a
comparable index) to maintain real value. Without indexation, the same
erosion that hollowed out Child Benefit applies.

---

## 10. Comparison to Previous Model

| Parameter | Previous (v1) | Current (v2) |
|---|---|---|
| UBI/ULI rate | £30,000 (single stage) | £2,500 rising to £29,000 (two stage) |
| UBS value | £2,000 | £2,500 |
| Children's rate | Not specified | Banded: £3,500-5,000 by age |
| Gross total requirement | £2.144 trillion | Stage 1: £352B, Stage 2: £1.810T |
| Existing welfare offset | Not considered | Stage 1: ~£14.5B, Stage 2: ~£230B |
| Median basis | £32,890 (outdated, gross) | £39,039 (ASHE 2025, take-home adjusted) |
| CPI indexation | Not specified | All values pegged to CPI |

---

## 11. Outstanding Questions

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
