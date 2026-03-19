# Tax Robots, Fund People

## SEBE Summary

**Author:** Jason Huxley
**Date:** February 2026
**Version:** 1.0

---

The UK government raises £534 billion a year from taxing workers' wages. Income Tax brings in £329 billion. National Insurance adds another £205 billion. Together, that is 42% of all government revenue. Every pound of it depends on people having jobs.

Automation is destroying those jobs. Not in some distant future. Now. Machine learning systems already outperform human diagnosticians, human traders, human translators and human customer service agents. Large language models handle legal research, code review, financial analysis and content production at a fraction of the cost of a salaried employee. Every AI system deployed is a salary that disappears from the tax base.

The fiscal arithmetic is simple and brutal. As employment falls, income tax and National Insurance revenue fall with it. Meanwhile, the people who lost those jobs need more support, not less. Revenue shrinks. Costs grow. The scissors close.

No existing UK tax solves this. Corporation Tax is an accounting fiction: multinationals structure their affairs to declare minimal profit in the UK regardless of how much economic activity they conduct here. VAT falls with consumer spending, which falls with unemployment. Capital Gains Tax is volatile. None of them track the physical infrastructure of automated production.

## The insight

Here is what I noticed while working as an infrastructure engineer: every computation consumes electricity. Every GPU cycle, every model inference, every automated warehouse robot, every algorithmic trade. A processor is, in thermodynamic terms, a nearly perfect heater. The energy it consumes is physical, measurable and unavoidable. You cannot transfer-price a kilowatt-hour to Dublin. You cannot restructure electrons through a subsidiary in Luxembourg. The meter reads what it reads.

And every offshore AI service crosses a physical border. When a UK business calls the OpenAI API, that data crosses an undersea cable. When a UK bank runs its models on AWS Ireland, the traffic is measurable at the Internet Exchange Point. These are not abstract flows. They are bits on fibre, countable at the point where the cable meets UK jurisdiction.

**Tax those two things. Energy consumption and cross-border commercial data. The physical inputs to automated production. That is the Sovereign Energy and Bandwidth Excise (SEBE).**

## How it works

SEBE has two components.

The **Sovereign Energy Excise (SEE)** taxes commercial electricity consumption in facilities above 500kW. That threshold exempts every small business, every shop, every restaurant. It targets data centres, automated warehouses, large-scale manufacturing and AI training facilities. Metering uses a Hardware Root of Trust at three points (generation, storage and load) to prevent evasion.

**SEE rate structure:**

| Consumption Bracket | Rate (£/kWh) |
|---|---|
| 0-500kW | Exempt |
| 500kW-5MW | £0.08 |
| 5MW-50MW | £0.20 |
| >50MW | £0.45 |

**SEE revenue at launch** (70 TWh taxable base plus ~60 TWh non-compute commercial): **£24-28 billion** (2026 prices). For context: the Climate Change Levy raises £2 billion at £0.00775/kWh. SEE at a weighted average of £0.16/kWh is a step change, but comparable in scale to fuel duty (£25 billion).

The **Digital Customs Duty (DCD)** is a border tariff on commercial data crossing the UK digital border. Consumers are exempt. Domestic data centre traffic is exempt (it pays SEE on energy instead). DCD targets UK businesses using offshore cloud providers, calling offshore APIs or running compute workloads abroad.

**DCD rate structure:**

| Annual Border Traffic | Rate |
|---|---|
| < 10 PB/year | £200/TB |
| 10-100 PB/year | £400/TB |
| > 100 PB/year | £800/TB |

**DCD revenue at launch: £7-10 billion** (2026 prices). Revenue remains roughly stable as the deterrent effect repatriates compute to UK facilities where SEE applies instead.

## The numbers

**Combined SEBE at launch (2030): £34-46 billion/year (2026 prices, CPI-indexed rates).**

**Revenue growth trajectory** (all figures 2026 real prices):

| Year | SEE | DCD | Total SEBE |
|---|---|---|---|
| 2030 (launch) | £30B | £8B | £38B |
| 2033 | £40B | £8B | £48B |
| 2035 | £50B | £7B | £57B |
| 2040 | £83B | £10B | £93B |
| 2045 | £140B | £19B | £159B |

**SEBE vs existing UK taxes:**

| Tax | Revenue (£B) | SEBE equivalent year |
|---|---|---|
| Inheritance Tax | 7 | Exceeds at launch |
| Stamp Duty | 15 | Exceeds at launch |
| IHT + SD + CCL + Tobacco | ~34 | Comparable at launch |
| Corporation Tax | 100 | ~2038 |
| National Insurance | 205 | ~2047 |

Revenue is self-scaling: as automation replaces human labour, the tax on automation infrastructure grows automatically.

**Sensitivity (launch year):**

| Scenario | SEE | DCD | Total |
|---|---|---|---|
| Conservative | £16B | £4B | £20B |
| Mid | £24B | £8B | £32B |
| High | £35B | £15B | £50B |

Even at half the projected rate, SEBE at launch is larger than Inheritance Tax and growing.

## Why it cannot be gamed

SEBE taxes physical resource consumption, not accounting constructs. A multinational can declare zero profit in the UK by routing intellectual property through Ireland. It cannot route its electricity consumption through Ireland. The data centre in Slough draws power from the grid and the meter records it.

Hardware Root of Trust metering (tamper-evident, cryptographically attested, bidirectional for battery storage) prevents dark compute. One physical measurement replaces thousands of pages of corporate accounting.

## The income tax replacement argument

Current employment-linked revenue (£534 billion) represents 42% of government revenue. As automation erodes employment, this shrinks. SEBE grows in the opposite direction.

| Year | SEBE | As % of Income Tax (£329B) |
|---|---|---|
| 2030 | £38B | 12% |
| 2035 | £57B | 17% |
| 2040 | £93B | 28% |
| 2045 | £159B | 48% |

SEBE does not need to replace all of income tax immediately. It needs to grow faster than income tax shrinks. If automation erodes income tax at 2-3% per year and SEBE grows at 10-15% per year (tracking compute capacity growth), the crossover occurs in the 2040s.

## What the money is for

SEBE is a revenue mechanism, not a welfare design. The money could fund anything: Universal Basic Income, National Insurance reductions, NHS expansion, deficit reduction, or a combination. That is a political choice, not a technical constraint.

One illustrative use: a modest UBI starting at roughly £650 per adult per year at launch (58.8 million adults, ONS 2030 projection), growing automatically as SEBE revenue increases. Not life-changing in year one. But self-scaling. As machines replace workers, the payment grows.

## Full proposal

The full proposal, including `revenue_model.md` derived from first principles, `cost_model.md`, `distribution_model.md` and `academic_brief.md`, is open-source:

**[github.com/djarid/SEBE](https://github.com/djarid/SEBE)**

This needs challenge. It needs economists to stress-test the revenue projections, the behavioural elasticity assumptions and the feedback loop dynamics. The revenue model has been through four rounds of adversarial review but has not had professional fiscal scrutiny. That is what I am asking for.

The work is open. The licence is CC-BY 4.0. I would welcome your critique.
