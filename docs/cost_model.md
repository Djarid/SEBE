# SEBE Cost Model

## Revenue, Distribution, and Transition Framework

**Author:** Jason Huxley
**Version:** 1.1
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
| OBR EFO | Welfare spending by category (pensioner, UC, disability, child) | Nov 2023 | Stale after Nov 2025 EFO |
| DWP PIP Statistics | PIP caseload by disabling condition (3.9M claims) | Oct 2025 | Quarterly (next Mar 2026) |
| DWP Benefit Expenditure Tables | Benefit expenditure and caseload data | 2025 (Jan 2026) | Annual |

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

SEBE's estimated revenue at launch (~£31-38B/year, see `revenue_model.md`
for full derivation) cannot fund full Stage 1 from day one. However, SEBE
revenue grows automatically with automation, reaching £93-159B/year by 2040
and £159-260B/year by 2045 (mid-to-high scenarios). UBI and UBS therefore
ramp up together as revenue allows.

This approach:
- Starts Stage 1 **immediately** at a level SEBE can fund
- Removes the "people will stop working" objection (Stage 1 is a supplement)
- Creates a **self-reinforcing feedback loop** (more spending, more tax revenue)
- Allows organic transition as the economy shifts
- Is **self-scaling**: the tax grows with the thing that replaces workers

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
| UBS provision | 67M | £2,500 | £167.5B |
| **Stage 1 total** | | | **£352B** |

**SEBE revenue at launch (derived): £31-38 billion/year**
(See `revenue_model.md` for full derivation from first principles.)

SEBE does not fund full Stage 1 from day one. Instead, UBI starts at
approximately £400/adult/year and ramps upward as automation (and
therefore SEBE revenue) grows. UBS phases in component by component:
free public transport (2028), free energy to threshold (2032), free
broadband and mobile (2035).

By 2040, SEBE revenue is projected at £93-135B/year. By 2045,
£159-260B/year. Stage 1 at full rate (£352B) is reached through
SEBE growth combined with the broader progressive tax package and
the UBI economic feedback loop.

### 6.4 Stage 1 Ramp and Economic Feedback Loop

**Year-by-year projection (see `revenue_model.md` Section 6 for detail):**

| Year | Total SEBE | UBS Active | Adult UBI | Family of 4 (combined) |
|---|---|---|---|---|
| 2027 (launch) | £31B | None | £400/yr | £1,900/yr |
| 2030 | £45B | Transport | £400/yr | £2,736/yr |
| 2035 | £62B | Transport + Energy + Broadband | £150/yr | £3,745/yr |
| 2040 | £101B | Full UBS | £550/yr | £6,122/yr |
| 2045 | £187B | Full UBS | £1,750/yr | £11,922/yr |

Note: UBI dips when new UBS components launch (they compete for the
same revenue), but the family is better off overall because UBS provides
direct cash-equivalent value (free transport, energy, broadband).

**Feedback loop:**

1. SEBE generates £31-38B from automation infrastructure (year 1)
2. UBI distributed at ~£400/adult/year (55M adults)
3. Consumer spending increases (especially in deprived areas)
4. High street, hospitality, local services recover
5. Increased economic activity generates additional conventional tax revenue
   (income tax, VAT, corporation tax, business rates all rise)
6. Combined revenue (SEBE + conventional) allows UBI to increase
7. As automation displaces more jobs, SEBE revenue grows further
8. UBI ratchets upward; UBS components phase in
9. By 2040, SEBE alone reaches £93-135B; with broader taxes, Stage 1 is funded

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
| UBS provision | 67M | £2,500 | £167.5B |
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
- Complementary progressive taxes (LVT, wealth tax, FTT)
- Inflation dynamics and productive capacity

The two stages are endpoints. In practice, UBI increases incrementally as
revenue allows. The trajectory is derived from compute growth projections
(see `revenue_model.md` Section 5):

| Year | SEBE Revenue | Adult UBI | UBS Status | Notes |
|---|---|---|---|---|
| 2027 | ~£31B | ~£400/yr | Launching | SEBE funds UBI immediately |
| 2030 | ~£45B | ~£400/yr | Transport free | Revenue absorbed by UBS expansion |
| 2035 | ~£62B | ~£150/yr | Full UBS | UBI dips as energy provision phases in |
| 2040 | ~£101B | ~£550/yr | Full UBS | UBI recovering, automation scaling |
| 2045 | ~£187B | ~£1,750/yr | Full UBS | Significant supplementary income |
| 2050+ | ~£350B+ | ~£5,000+/yr | Full UBS | Approaching original Stage 1 target |

The original Stage 1 rate (£2,500/adult/year) is reached when SEBE revenue
grows sufficiently, estimated around 2050 in the mid-growth scenario. With
the broader progressive tax package, this could be accelerated to 2040-2045.

These figures are derived from automation growth projections, not arbitrary.
Actual trajectory depends on automation adoption rates, AI scaling, sovereign
compute investment, and macroeconomic conditions.

---

## 7. Existing Benefit Offsets

### 7.1 Overview

The gross cost figures in Section 6 represent total UBI/ULI + UBS spending.
However, SEBE distribution displaces significant existing welfare
expenditure. The net new cost is substantially lower than the gross figures
suggest, because benefits that UBI/ULI replaces no longer need to be funded.

This section quantifies the offsets. All figures are from OBR (November
2023 Economic and Fiscal Outlook) unless otherwise stated. The OBR data
covers Great Britain (excluding Northern Ireland social security, which
operates separately but at similar per-capita rates). Figures are for
2023-24 and will be higher by the time SEBE is implemented due to uprating.

**All UBI/ULI/UBS values and SEBE rates must be pegged to CPI (or a
comparable index) to maintain real value over time.** Without indexation,
the same erosion that hollowed out Child Benefit (frozen 2016-2020,
consistently uprated below earnings growth) would undermine ULI. CPI
pegging applies to both payments and tax rates.

**Source:** OBR, obr.uk/forecasts-in-depth/tax-by-tax-spend-by-spend/

### 7.2 Current UK Welfare Spending

Total welfare spending in 2023-24: approximately **£290 billion** (GB).

| Category | Spending (2023-24) | % of Total | OBR Source |
|---|---|---|---|
| Pensioner benefits | £138B | 48% | Pensioner benefits page |
| UC and legacy benefits | £81B | 28% | Universal credit page |
| Disability benefits | ~£42B | ~15% | Disability benefits page |
| Child Benefit | £12.5B | 4% | Child benefit page |
| Other (Carer's, Maternity, etc.) | ~£17B | ~6% | Supplementary table 3.7 |
| **Total welfare** | **~£290B** | **100%** | |

Pensioner benefits alone are nearly half the welfare bill. This is the
single largest offset when ULI replaces state pension.

### 7.3 Stage 1 Offsets (UBI at £2,500/adult)

At Stage 1, UBI is a supplement. Existing benefits continue unchanged.
The direct welfare offsets are therefore minimal:

| Benefit | Offset at Stage 1 | Rationale |
|---|---|---|
| Child Benefit | **£12.5B** | Replaced by SEBE children's supplements (which are more generous at every age band) |
| Winter Fuel Payment | **~£2B** | Replaced by UBS energy provision (free energy to threshold) |
| **Stage 1 total offset** | **~£14.5B** | |

**Child Benefit comparison:**

| Age | Current Child Benefit | SEBE Supplement | Difference |
|---|---|---|---|
| Eldest child | £1,355/year | £3,500-5,000 | +£2,145 to +£3,645 |
| Additional child | £897/year | £3,500-5,000 | +£2,603 to +£4,103 |

SEBE children's supplements are 2.6x to 3.7x more generous than current
Child Benefit. The distinction between eldest and additional children
(a relic of means-testing) is eliminated: each child receives based on
age, not birth order.

Note: Child Benefit is currently subject to the High Income Child Benefit
Charge (clawback above income threshold). SEBE supplements are universal
and unconditional, with no means-testing or clawback.

**Winter Fuel Payment** (£100-300/year for pensioners) is rendered redundant
by UBS energy provision, which covers energy costs for all citizens, not
just pensioners.

**Net Stage 1 cost:**

| Component | Amount |
|---|---|
| Gross Stage 1 cost | £352B |
| Child Benefit offset | -£12.5B |
| Winter Fuel Payment offset | -£2B |
| **Net Stage 1 cost** | **~£337.5B** |

### 7.4 Stage 2 Offsets (ULI at £29,000/adult)

At Stage 2, ULI is the primary income for most adults. It replaces almost
all existing income-replacement benefits. The offsets are transformative.

#### 7.4.1 Pensioner Benefits (~£132B offset)

State pension is the largest single welfare item (£125B in 2023-24). ULI
at £29,000/year is approximately 2.8x the full new state pension
(£10,600/year in 2023-24). ULI fully replaces:

| Benefit | Offset | Notes |
|---|---|---|
| State pension (basic and new) | ~£125B | Fully replaced by ULI |
| Pension Credit | ~£5B | Means-tested top-up, redundant at ULI level |
| Winter Fuel Payment | ~£2B | Already offset at Stage 1 via UBS energy |
| **Pensioner subtotal** | **~£132B** | |

#### 7.4.2 UC and Legacy Benefits (~£55-65B offset)

ULI at £29,000/year exceeds UC maximum awards for most household types.

| Component | Offset | Notes |
|---|---|---|
| UC standard allowance + child elements | ~£40-50B | Income replacement, fully displaced by ULI |
| UC housing element (see 7.4.4) | ~£15B | Partial offset (see housing analysis below) |
| Legacy JSA/IS (residual) | ~£2B | Fully displaced |
| **UC subtotal** | **~£55-65B** | |

#### 7.4.3 PIP/DLA (~£8-11B partial offset)

Total PIP/DLA spending: ~£28B (OBR 2023-24, growing rapidly).

PIP is not a monolithic category. DWP PIP Statistics (October 2025) show
3.9 million claims in England and Wales, broken down by primary disabling
condition:

| Condition Category | % of Caseload | ULI Impact |
|---|---|---|
| Psychiatric disorder | 39% | High |
| Musculoskeletal disease (general) | 19% | Moderate |
| Neurological disease | 13% | Low |
| Musculoskeletal disease (regional) | 12% | Moderate |
| Respiratory disease | 4% | Low |
| Other | 13% | Mixed |

**Source:** DWP, Personal Independence Payment Official Statistics to
October 2025

**Analysis:** Many PIP claims (particularly psychiatric disorders such as
depression, social anxiety, and chronic stress-related conditions) exist
because the claimant cannot sustain employment and cannot afford to exist
without disability support. The primary barrier is financial, not a need
for specialist equipment or care. ULI at £29,000/year removes the financial
pressure entirely, enabling recovery, therapy access, and time to manage
the condition without the stress of poverty.

Conditions with genuine additional costs (neurological conditions requiring
specialist equipment, physical disabilities requiring adapted environments,
conditions requiring personal care) are NOT offset. These claimants need
disability support on top of ULI.

**Estimated offset by condition type:**

| Category | ULI offset estimate | Rationale |
|---|---|---|
| Psychiatric (39%) | ~60-70% | Financial stress is primary barrier for many |
| Musculoskeletal (31%) | ~20-30% | Recovery time helps, but many have ongoing costs |
| Neurological (13%) | ~10% | Genuine additional costs (MS, Parkinson's, epilepsy) |
| Respiratory (4%) | ~10% | Equipment and medication costs |
| Other (13%) | ~20% | Mixed |
| **Weighted total** | **~34-41%** | |

Applied to ~£28B total PIP/DLA spend: **£9.5-11.5B offset**

**Caveat:** This estimate uses caseload proportions, not condition-level
spend data (which is not publicly available at the required granularity).
Average awards vary by condition and award level. Further research using
DWP Stat-Xplore data on award levels by condition is needed to refine
this estimate. The 30-40% range should be treated as indicative.

#### 7.4.4 Housing Benefit and UC Housing Element (~£20-23B offset)

Total housing-related benefit spending: ~£25B (Housing Benefit including
pensioner HB plus UC housing element).

Housing Benefit is means-tested. Under ULI, three factors dramatically
reduce the housing benefit burden:

**1. Means-testing mechanics:** ULI counts as income. At £29,000/year,
most current Housing Benefit claimants exceed the eligibility threshold.
The number of qualifying claimants falls sharply without any policy change;
the existing means-test does the work.

**2. Post-employment migration dispersal:** Employment is the primary
driver of internal migration to high-cost areas (London, SE England,
major cities). When ULI removes the employment motive, people disperse.
COVID-19 demonstrated this effect: when the requirement to physically
attend a workplace disappeared, significant population movement occurred
away from expensive urban centres toward lower-cost areas. Under full ULI,
this effect is permanent and more pronounced. Reduced demand in high-cost
areas softens housing costs, further reducing Housing Benefit claims.

**3. Lifestyle choice, not necessity:** Once employment is removed from
the equation, living in an expensive city is a lifestyle choice, not an
economic necessity. The state has no obligation to subsidise that choice.
ULI provides £29,000 (plus £2,500 UBS). If a citizen chooses to live in
central London, they manage their housing costs from that income. The
rest of the nation should not fund location preference through Housing
Benefit.

**Residual housing support:** A small number of cases may persist,
concentrated in extreme-cost areas. This residual (~£2-5B) is a housing
market problem, not an income problem, and should be addressed through
structural reform: Land Value Tax (suppresses speculative land prices),
public housing investment (increases supply), and planning reform. Housing
Benefit is a symptom of a broken housing market, not a permanent feature
of the welfare state.

**Estimated offset: £20-23B** (of ~£25B total)

#### 7.4.5 Statutory Maternity and Paternity Pay (~£3B offset)

Current statutory maternity/paternity pay costs ~£3B/year.

Under ULI, the parent already receives £29,000/year (tax-free) plus a
£5,000 child supplement for a newborn (0-2 age band). Combined: £34,000
in the year of birth, plus free energy, transport, broadband, and mobile
via UBS.

The government should not supplement above ULI. Employers may offer
enhanced maternity/paternity packages as a recruitment and retention tool,
at their discretion. This is an employer benefit, not a state obligation.

**Offset: £3B**

#### 7.4.6 Child Maintenance Service (~£0.5B administrative offset)

The Child Maintenance Service (CMS) currently costs ~£0.5B/year to
administer. CMS exists to transfer income from absent parents to the
parent with care.

Under SEBE, every child has their own supplement (£3,500-5,000/year by
age). The income-transfer justification for CMS largely evaporates.
CMS may persist as a punitive enforcement mechanism for parental
responsibility, but the administrative apparatus shrinks significantly.

**Offset: ~£0.5B** (administrative savings)

#### 7.4.7 Child Benefit (~£12.5B offset)

Already offset at Stage 1 (see 7.3). Fully replaced by SEBE children's
supplements which are more generous at every age band.

### 7.5 Summary of Stage 2 Offsets

| Benefit Displaced | Offset | Confidence |
|---|---|---|
| State pension (basic + new) | ~£125B | High (direct replacement) |
| Pension Credit | ~£5B | High (means-tested, redundant at ULI) |
| Winter Fuel Payment | ~£2B | High (replaced by UBS energy) |
| UC/legacy income replacement | ~£40-50B | High (ULI exceeds UC rates) |
| UC/legacy + pensioner housing | ~£20-23B | Medium (requires companion housing policy) |
| PIP/DLA partial | ~£9.5-11.5B | Medium (needs condition-level spend research) |
| Child Benefit | ~£12.5B | High (direct replacement, more generous) |
| Statutory Maternity/Paternity | ~£3B | High (ULI + child supplement covers it) |
| CMS administrative | ~£0.5B | Medium |
| Administrative savings | ~£5-7B | Medium (DWP means-testing apparatus) |
| **Total Stage 2 offset** | **~£222-240B** | |

**Net Stage 2 cost:**

| Component | Amount |
|---|---|
| Gross Stage 2 cost | £1.810T |
| Existing welfare offset | -£222-240B |
| **Net Stage 2 cost** | **~£1.57-1.59T** |

### 7.6 Benefits NOT Offset

Some benefits are not displaced by UBI/ULI:

- **PIP/DLA (residual ~£17-20B):** The 60-70% of PIP spending that
  addresses genuine additional costs (specialist equipment, adapted
  environments, personal care) continues. Conditions requiring physical
  adaptations, mobility aids, or care support are not addressed by income
  alone. This residual PIP is properly functioning disability support.
- **Carer's Allowance (~£4B, increasing):** Caring is a vocation and
  should be recognised as state-paid employment. The current Carer's
  Allowance (£81.90/week, £4,260/year) is inadequate for what is often
  24/7 skilled work. Under ULI, carers receive ULI as citizens (£29,000)
  plus a proper state employment salary for the caring work. Carer's
  Allowance is therefore not an offset but a future cost increase,
  partially absorbed by declining public sector employment costs from
  automation elsewhere (see 7.8).

### 7.7 What This Means

The offset is approximately **£222-240B/year** at Stage 2. That is real
money that the government currently spends and would no longer need to.

For context:
- ~£230B is larger than National Insurance revenue (~£170B)
- It is larger than VAT revenue (~£160B)
- It reduces the Stage 2 funding gap from £1.810T to ~£1.57-1.59T
- **Over three quarters of the current welfare bill (~£290B) is absorbed
  or displaced by ULI**

At Stage 1, the offset is modest (~£14.5B), because Stage 1 preserves
existing benefits. But it still reduces the net cost from £352B to
~£337.5B, improving SEBE coverage further.

### 7.8 Dynamic Effects (Not Quantified)

Two dynamic effects further improve the fiscal position but cannot be
quantified without specialist modelling:

**1. Automation reduces public sector operating costs.** As automation
handles administrative, logistical, and routine government functions,
the total public sector wage bill declines. This creates fiscal space
for new costs (such as proper carer wages) without increasing overall
expenditure. Civil service headcount falls; remaining roles (including
state-employed carers) are funded from the savings.

**2. Post-employment migration rebalances regional demand.** When
employment no longer drives internal migration, population disperses from
high-cost urban centres. This reduces housing cost pressure, reduces
regional inequality, and revitalises currently deprived areas (where ULI
spending has the highest multiplier effect). COVID-19 provided early
evidence of this effect. The long-term impact on housing costs, regional
tax revenue, and public service demand is significant but requires
detailed modelling.

These effects are noted as directionally positive. They are not included
in the offset calculations above, which are deliberately static and
conservative.

---

## 8. Comparison to Previous Model

| Parameter | Previous model | Revised model |
|---|---|---|
| UBI/ULI rate | £30,000 (single stage) | £2,500 rising to £29,000 (two stage) |
| UBS value | £2,000 | £2,500 |
| Children's rate | Not specified | Banded: £3,500-5,000 by age |
| Gross total requirement | £2.144 trillion | Stage 1: £352B, Stage 2: £1.810T |
| Existing welfare offset | Not considered | Stage 1: ~£14.5B, Stage 2: ~£230B |
| **Net total requirement** | £2.144 trillion | **Stage 1: ~£337.5B, Stage 2: ~£1.57-1.59T** |
| SEBE coverage (net, year 1) | 9-23% | **Stage 1: 9-11% (year 1), growing to 28-77% by 2040** |
| Fundable from SEBE alone | No | **Stage 1 ramps with SEBE growth (see revenue_model.md)** |
| Median basis | £32,890 (outdated, gross) | £39,039 (ASHE 2025, take-home adjusted) |
| Tax treatment | Compared to gross salary | Correctly compared to take-home pay |
| CPI indexation | Not specified | All values pegged to CPI |

Key improvement: The revenue model is now derived from first principles
(see `revenue_model.md`). SEBE starts at £31-38B/year and grows
automatically with automation. Combined with complementary progressive
taxes, Stage 1 is achievable within 10-15 years of launch.

---

## 9. Sensitivity Analysis

### 9.1 SEBE Revenue Uncertainty

SEBE revenue at launch is estimated at £31-38B/year, growing to
£93-260B/year by 2040 depending on automation growth rates. The
range reflects uncertainty in:
- Actual commercial energy consumption subject to SEE (~60-85 TWh)
- Automation growth rate (10-15% per annum compute capacity growth)
- Offshore compute share (30-45% of UK-serving compute currently offshore)
- Behavioural response (energy efficiency investment)
- Enforcement effectiveness
- Rate-setting decisions

See `revenue_model.md` Sections 8.1-8.3 for full sensitivity analysis.

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

## 10. Outstanding Questions

These are acknowledged gaps, not hidden weaknesses:

1. **SEBE revenue model:** ~~This document covers distribution costs but not
   revenue derivation.~~ **RESOLVED.** See `revenue_model.md` for full
   derivation from DESNZ energy consumption data, data centre capacity
   figures, wholesale/retail bandwidth pricing, and LLM token economics.

2. **Transition dynamics:** How fast does UBI ratchet up? What triggers
   each increase? This requires macroeconomic simulation.

3. **Green Party EC730 alignment:** The children's supplement structure
   should be checked against the Green Party's existing UBI policy for
   compatibility.

4. **Regional variation:** UBS costs (especially energy and transport)
   vary significantly by region. A flat national rate may under-serve
   rural and northern areas.

5. **Interaction with existing benefits:** Section 7 addresses the major
   benefit categories. Remaining edge cases (interaction between ULI and
   contributory benefits, transitional protection for current claimants,
   devolved benefits in Scotland/NI) need detailed policy design.

6. **Transport capacity investment:** Free public transport will increase
   demand beyond current levels. The 30% uplift factor used in UBS costing
   covers operational costs but not long-term capital investment in rolling
   stock and infrastructure. This is a net positive (jobs, emissions
   reduction) but needs explicit modelling.

---

© 2026 Jason Huxley. Licensed under CC-BY 4.0.
