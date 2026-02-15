# SEBE Cost Model

## Revenue Scale and Economic Context

**Author:** Jason Huxley
**Version:** 2.0
**Date:** February 2026
**Status:** Working document

---

## 1. Purpose

This document places SEBE revenue in context: how large is it relative
to the current tax system, what could it replace, and what could it fund?
It bridges the revenue model (how SEBE raises money) and the distribution
model (one illustrative use of the revenue).

- **Revenue derivation:** `revenue_model.md` (source of truth for all SEBE figures)
- **Distribution workings:** `distribution_model.md` (UBI/ULI/UBS detail)

---

## 2. SEBE Revenue Summary

From `revenue_model.md` (derived from first principles):

| Year | SEE | DCD | Total SEBE |
|---|---|---|---|
| 2027 (launch) | £24B | £7B | **£31B** |
| 2030 | £30B | £8B | **£38B** |
| 2035 | £50B | £7B | **£57B** |
| 2040 | £83B | £10B | **£93B** |
| 2045 | £140B | £19B | **£159B** |

Revenue is self-scaling: as automation replaces human labour, the tax
on automation infrastructure grows automatically.

---

## 3. Scale Comparison

### 3.1 SEBE vs Current UK Taxes

| Tax | Revenue (£B) | SEBE Equivalent Year |
|---|---|---|
| Inheritance Tax | 7 | SEBE exceeds at launch |
| Climate Change Levy | 2 | SEBE exceeds at launch |
| Stamp Duty | 15 | SEBE exceeds at launch |
| Tobacco Duty | 10 | SEBE exceeds at launch |
| IHT + SD + CCL + Tobacco combined | ~34 | SEBE comparable at launch |
| Corporation Tax | 100 | SEBE reaches by ~2038 |
| National Insurance | 170 | SEBE reaches by ~2043 |
| Income Tax | 250 | SEBE reaches by ~2050 |

**SEBE at launch is a mid-tier tax.** It becomes a major revenue source
within 10-15 years, tracking automation growth.

### 3.2 SEBE vs the Employment Tax Gap

Current employment-linked revenue:
- Income Tax: £250B
- National Insurance: £170B
- **Total: £420B (42% of government revenue)**

As automation erodes employment, this £420B shrinks. SEBE grows in the
opposite direction. By 2040, SEBE at £93B replaces approximately 22% of
the employment tax base. By 2050, at projected growth rates, SEBE could
replace 50% or more.

This is the core fiscal argument: **SEBE tracks the thing that destroys
the income tax base.**

---

## 4. What Could SEBE Fund?

SEBE revenue is general revenue. It could fund anything. The following
are illustrative uses, not prescriptive policy:

### 4.1 At Launch (£31-38B)

| Use | Cost | Notes |
|---|---|---|
| Modest UBI (~£400/adult/year) | ~£22B | 55M adults |
| Free public transport | ~£14B | Fares replacement |
| NHS waiting list reduction | ~£10-15B | Capital + staffing |
| Corporation Tax reduction | £31B = ~8p cut | Pro-business option |
| Deficit reduction | £31-38B | Directly reduces borrowing |

Any one of these, or a combination. The point is that £31-38B is real
money at a scale that moves the fiscal needle.

### 4.2 At Maturity (£93B by 2040, £159B by 2045)

| Use | Cost | Notes |
|---|---|---|
| UBI at £1,000/adult/year | ~£55B | Meaningful supplement |
| UBI at £2,500/adult/year + UBS | ~£352B | Requires complementary taxes |
| Full income tax replacement | £250B | SEBE alone insufficient; needs growth |
| Full NI replacement | £170B | Achievable by ~2043 at projected rates |

### 4.3 The Two-Stage Distribution Model (One Option)

The accompanying `distribution_model.md` works through a specific
scenario in detail:

- **Stage 1:** UBI starting at ~£400/adult/year, ramping with SEBE growth.
  UBS (free transport, energy, broadband) phases in. Children's supplements
  at £3,500-5,000/year age-banded. Total Stage 1 target: £352B.
- **Stage 2:** UBI ratchets toward Universal Living Income (£29,000/adult,
  matching median take-home pay). Total: £1.810T, requiring SEBE plus
  complementary progressive taxes.

This is illustrative. SEBE works regardless of distribution model chosen.

---

## 5. The Income Tax Replacement Argument

### 5.1 The Problem

Employment taxation (£420B) is structurally coupled to employment levels.
Automation reduces employment. Therefore automation reduces revenue.
Meanwhile, displaced workers increase welfare costs. The fiscal scissors
close.

No existing tax grows with automation. Corporation Tax is gamed through
profit shifting. VAT is consumption-linked (falls with unemployment).
Capital Gains is volatile. None of them track the physical infrastructure
of automated production.

### 5.2 Why SEBE Is Different

SEBE taxes the inputs to automated production: energy (kWh) and
cross-border data (TB). These are:

- **Physical:** can't be profit-shifted to Ireland
- **Measurable:** hardware metering, not accounting
- **Unavoidable:** every compute workload needs power and connectivity
- **Self-scaling:** more automation means more energy and data, means more tax

As a data centre replaces 500 accountants, income tax on those 500
salaries disappears. But the data centre's electricity consumption
(taxed by SEE) and its cross-border data flows (taxed by DCD) now
generate SEBE revenue instead.

### 5.3 Timeline to Income Tax Scale

| Year | SEBE | As % of Current Income Tax (£250B) |
|---|---|---|
| 2027 | £31B | 12% |
| 2030 | £38B | 15% |
| 2035 | £57B | 23% |
| 2040 | £93B | 37% |
| 2045 | £159B | 64% |

SEBE does not need to replace all of income tax immediately. It needs
to grow faster than income tax shrinks. If automation erodes income tax
at 2-3% per year and SEBE grows at 10-15% per year (tracking compute
capacity growth), the crossover occurs in the 2040s.

---

## 6. Sensitivity

### 6.1 Revenue Uncertainty

SEBE revenue range reflects uncertainty in:
- Commercial energy consumption subject to SEE (~60-85 TWh)
- Automation growth rate (10-15% per annum compute capacity growth)
- Offshore compute share (30-45% currently offshore)
- Behavioural response (efficiency investment reduces consumption)
- Enforcement effectiveness

Full sensitivity analysis in `revenue_model.md` Sections 8.1-8.3.

### 6.2 What If SEBE Underperforms?

Even at half the projected rate:
- Year 1: £15-19B (still larger than Inheritance Tax)
- 2040: £45-50B (still a significant revenue source)
- The fiscal argument still holds: this is the only tax that grows
  with automation

### 6.3 What If SEBE Overperforms?

If automation grows faster than projected (AI scaling, sovereign compute
investment, reshoring driven by DCD):
- Year 1: £40-50B
- 2040: £130-180B (approaching Income Tax scale in a decade)
- Distribution options expand rapidly

---

## 7. Outstanding Questions

1. **Precise tax base:** Actual facility-level energy consumption data
   (DESNZ publishes sector-level, not facility-level)
2. **Behavioural elasticity:** How much does energy consumption fall when
   taxed at SEE rates?
3. **Income tax erosion rate:** How fast is automation actually reducing
   employment tax revenue? (ONS RTI data could answer this)
4. **Feedback loop magnitude:** How much does redistributed SEBE revenue
   boost conventional tax receipts?

---

(c) 2026 Jason Huxley. Licensed under CC-BY 4.0.
