# The Evolution of SEE: From Automation Levy to Universal Energy Tax

## A Thought Exercise

**Author:** Jason Huxley
**Version:** 0.1 (draft)
**Date:** February 2026
**Status:** Exploratory, not policy-ready

---

## 1. The Premise

SEBE as currently proposed taxes commercial facilities above 500kW.
This is the right starting point: it targets the automation
infrastructure that is actively eroding the employment tax base,
it is politically defensible (ordinary people and small businesses are
exempt), and it generates £34-46B at launch.

But the 500kW threshold is a pragmatic boundary, not a principled one.
The underlying logic of SEE (tax physical resource consumption because
it cannot be offshored, restructured or declared away) applies to all
commercial energy consumption, not just large-scale automation.

This document explores where that logic leads if SEE expands over time
to replace Corporation Tax (CT) entirely.

---

## 2. Why Corporation Tax Fails

CT taxes declared profit. Declared profit is an accounting construct
that the taxpayer controls. The tools are well known:

- **Transfer pricing:** Charge your UK subsidiary inflated licence fees
  from your Irish IP holding company. UK profit shrinks. Irish profit
  (taxed at 12.5%) grows.
- **Debt loading:** Borrow from an offshore affiliate. Interest payments
  are tax-deductible in the UK. The "lender" collects interest in a
  low-tax jurisdiction.
- **Cost allocation:** Attribute R&D costs, management fees and shared
  services to whichever jurisdiction produces the best tax outcome.
- **Profit shifting through intangibles:** Assign IP ownership to a
  subsidiary in Luxembourg. The UK operation "licences" the IP at a
  price set by the company itself.

The OECD's Pillar Two (15% global minimum) attempts to close these gaps.
It is already being gamed through qualified domestic minimum top-up
taxes and substance carve-outs. The structural problem remains: if the
tax base is an accounting construct, the taxpayer will construct it
favourably.

SEE taxes kilowatt-hours. A kilowatt-hour is a physical event. It
happens at a physical location. It is measured by a physical instrument.
You cannot transfer-price a kilowatt-hour to Dublin.

---

## 3. The Geometric Rate Curve

Current SEBE uses banded tiers (£0.08, £0.20, £0.45 per kWh at the
three thresholds). This creates cliff edges: an operator at 4.9MW has a
strong incentive to stay below 5MW to avoid the jump from £0.08 to
£0.20.

A universal SEE (no threshold, all commercial consumption) needs a
continuous rate curve that eliminates cliff edges and scales
progressively across the full range of consumption.

### 3.1 The Principle

Each consumed kilowatt-hour is more expensive than the previous one.
Not banded (where kWh 1 to kWh N within a band all cost the same), but
individually progressive. The first kWh a business consumes in a billing
period costs nearly nothing. The millionth costs significantly more. The
billionth costs far more again.

The simplest mathematical form is a power function:

```
Rate(n) = base_rate x (n / scale_factor) ^ exponent
```

Where `n` is the cumulative kWh consumed in the billing period,
`scale_factor` sets the inflection point, and `exponent` controls
how aggressively the curve accelerates. The `base_rate` is the minimum
per-kWh charge.

### 3.2 Illustrative Numbers

For illustration only. These are not modelled rates.

| Annual consumption | Approximate effective rate | Approximate annual SEE | Current CT on typical profit |
|---|---|---|---|
| 10 MWh (small shop) | £0.003/kWh | £30 | £2,500-5,000 |
| 100 MWh (medium office) | £0.01/kWh | £1,000 | £12,500-25,000 |
| 1 GWh (large office/factory) | £0.05/kWh | £50,000 | £125,000-500,000 |
| 10 GWh (small DC/large factory) | £0.15/kWh | £1.5M | £1-5M |
| 100 GWh (mid DC) | £0.35/kWh | £35M | £10-50M |
| 1 TWh (hyperscaler) | £0.80/kWh | £800M | £100M-1B |

The curve produces two outcomes:

1. **Small businesses pay less than current CT.** A shop using 10 MWh
   pays £30 in SEE versus thousands in CT. This is a genuine tax cut
   for the majority of UK businesses.
2. **Large consumers pay more, and cannot avoid it.** A hyperscaler
   consuming 1 TWh pays £800M. There is no accounting structure that
   reduces this. The meter reads what it reads.

### 3.3 The Cliff-Edge Problem Resolved

With a continuous curve there are no thresholds to game. Reducing
consumption by 1 kWh saves the marginal rate on that kWh, not a
band-wide rate change. The incentive is always to use less energy
(correct environmental signal) rather than to structure around an
arbitrary boundary.

---

## 4. The Public Ownership Prerequisite

Geometric SEE billing only works if the base cost of energy is
separated from the tax component. Under the current privatised
energy market, consumers pay:

```
Total cost = wholesale cost + network charges + supplier margin
             + green levies + VAT + (proposed SEE)
```

The supplier margin and shareholder extraction add approximately
£0.08-0.10/kWh to electricity costs. If SEE is layered on top of
commercial energy prices, the combined burden at the low end (small
businesses, households) is politically unacceptable.

The solution: public ownership of energy generation and distribution,
operated at cost. This removes the profit layer entirely.

```
Total cost = generation cost + network cost + SEE
```

At publicly owned generation cost (approximately £0.04-0.06/kWh for
a renewables-dominated grid with nuclear baseload), the combined price
for a small business under geometric SEE looks like:

```
10 MWh: £0.05/kWh base + £0.003/kWh SEE = £0.053/kWh total
```

This is less than half the current commercial electricity price
(£0.12-0.15/kWh after all charges). The small business pays less for
energy and less in tax. The large consumer pays more in SEE, but on a
lower base cost, and the SEE is doing the work that CT currently fails
to do.

---

## 5. The CT Delta (Alternative Minimum Tax)

Geometric SEE catches most commercial activity because most commercial
activity consumes energy in rough proportion to its economic scale. But
not all.

The gap: businesses whose economic footprint is primarily intellectual
or financial rather than physical. An IP holding company in Mayfair
consuming 50kW while extracting £500M in licensing revenue. A boutique
hedge fund running optimised inference on a single rack, generating
billions from minimal power draw.

These entities have a low energy-to-profit ratio. Geometric SEE
undercharges them relative to their economic weight.

### 5.1 The Mechanism

```
Tax owed = max(SEE, 25% of declared profit)
```

If your geometric SEE liability exceeds 25% of declared profit, you
pay SEE. If your declared profit vastly exceeds your energy footprint,
you pay the delta (the difference between 25% of profit and your SEE).

This is functionally an Alternative Minimum Tax (AMT), similar to the
US model. The 25% rate is illustrative, not modelled.

### 5.2 Limitations

CT Delta still relies on declared profit for the backstop calculation.
This reintroduces the accounting surface that SEE exists to avoid. The
mitigation: CT Delta is a backstop, not a primary mechanism. An entity
trying to game it must simultaneously suppress declared profit (reducing
CT Delta) and suppress energy consumption (reducing SEE). Doing both
limits actual economic activity.

The entities caught by CT Delta are, by definition, high-profit and
low-energy. They have limited room to manipulate energy consumption
further downward (they are already efficient). Suppressing declared
profit works against their other interests (debt covenants, share price,
investor reporting).

### 5.3 Companion Taxes

CT Delta is one tool for closing the low-energy high-profit gap. Others:

- **Land Value Tax (LVT):** Catches real estate rent extraction. The
  Mayfair IP company sits on expensive land. LVT bills them for it.
- **Financial Transaction Tax (FTT):** Catches high-frequency financial
  activity that is compute-light but trade-heavy.
- **DCD:** Catches offshore compute usage. The hedge fund calling US-based
  inference APIs pays DCD on the cross-border data.

Together, the companion taxes close the gaps that a physical-consumption-only primary tax inherently has. No single tax captures everything.
The design is a mesh, not a monolith.

---

## 6. Revenue Implications

This section is deliberately vague. The evolution from threshold-based
SEBE to universal geometric SEE is a structural change that requires
formal economic modelling before revenue estimates are credible.

### 6.1 Directional Observations

- **The tax base expands dramatically.** Current SEBE taxes approximately
  70 TWh (facilities above 500kW). Universal SEE taxes all 150 TWh of
  commercial and industrial electricity, plus whatever additional
  consumption the geometric curve captures from smaller operations.
- **Small business revenue is modest.** The low end of the curve produces
  minimal per-entity revenue. A million small businesses paying £30-1,000
  each in SEE generates £30M-1B. This is not where the revenue comes
  from.
- **Large consumer revenue increases.** The geometric curve's acceleration
  means the top 100 consumers contribute disproportionately. This is
  by design.
- **CT abolition saves compliance costs.** Corporation tax compliance
  costs UK businesses approximately £5-8B per year (HMRC estimate).
  SEE compliance is a meter reading and an invoice. The administrative
  saving partially offsets the transition disruption.

### 6.2 What Needs Modelling

- The precise curve parameters (base rate, scale factor, exponent)
  that produce revenue equivalent to current CT (£100B) while keeping
  small business rates below current CT liability
- Behavioural response (how much do large consumers reduce consumption
  when faced with the geometric curve, and what does that do to total
  revenue?)
- CT Delta rate that captures sufficient revenue from low-energy
  high-profit entities without reintroducing the gaming surface
- Interaction effects with LVT, FTT and DCD (how much of the gap does
  each companion tax fill?)
- Transition path (you cannot abolish CT and introduce geometric SEE
  on the same day; the sequencing matters)

---

## 7. Transition Sketch

### Phase 0: SEBE as Proposed (2030-2035)

SEBE launches with the current threshold-based design. SEE applies to
facilities above 500kW. DCD applies at IXP level. Revenue: £34-46B at
launch, growing to £57B by 2035. CT continues unchanged. This phase
proves the mechanism, builds the metering infrastructure and establishes
public acceptance.

### Phase 1: Threshold Reduction (2035-2038)

SEE threshold drops from 500kW to 100kW, then 50kW. The tiered rate
structure transitions toward a continuous curve. More businesses enter
the SEE base. CT rates begin to fall (25% to 20% to 15%) as SEE revenue
replaces CT revenue. Small businesses start seeing lower combined
tax bills.

### Phase 2: Universal SEE (2038-2042)

SEE threshold drops to zero. All commercial energy consumption is taxed
on the geometric curve. CT rate drops to 10%, then 5%. The CT Delta
is introduced as a backstop for low-energy high-profit entities. Public
ownership of energy generation is a prerequisite for this phase (the
base cost must be under state control before the full geometric curve
is applied).

### Phase 3: CT Abolition (2042+)

CT is abolished. SEE (geometric curve) plus CT Delta (AMT backstop)
replace it entirely. LVT and FTT operate as companion taxes. The UK
business tax system is based on physical resource consumption, not
accounting profit. Declared profit ceases to be a tax-relevant concept
for most businesses.

---

## 8. Open Questions

This is a thought exercise, not a policy proposal. The following
questions would need answers before it became one:

1. **Is the geometric curve mathematically stable?** Does the revenue
   function behave predictably across the full range of consumption,
   or are there parameter combinations that produce absurd results at
   the extremes?

2. **Does public ownership of generation actually reduce base cost?**
   The assumption is that removing shareholder extraction drops the
   price. Historical evidence from pre-privatisation CEGB and current
   EDF France supports this, but the UK's generation mix is different.

3. **What is the transition cost?** Abolishing CT and introducing
   geometric SEE simultaneously is impossible. The phased approach
   in Section 7 spreads the disruption, but the fiscal gap during
   transition needs quantifying.

4. **Does the geometric curve create perverse incentives?** If the
   marginal rate at high consumption is extremely steep, does it push
   hyperscalers to build many small facilities rather than one large
   one? Is that bad? (Distributed compute may actually be more
   resilient, so perhaps not.)

5. **How do you meter commercial consumption separately from domestic?**
   Many commercial premises share power feeds with residential
   buildings. The metering infrastructure for universal SEE is more
   complex than for threshold-based SEBE, where only large facilities
   are metered.

6. **International competitiveness.** Geometric SEE on UK businesses,
   with no equivalent abroad, could drive relocation of energy-intensive
   industry. The DCD offshore penalty addresses compute, but physical
   manufacturing has no equivalent border tariff on goods produced with
   offshore energy. This needs thought.

---

This document is a thought exercise. It has not been through the same
rigour as the core SEBE documents. It represents a direction of travel,
not a destination.

---

*Copyright 2026 Jason Huxley. Licensed under CC-BY 4.0.*
