---
layout: post
title: "Tax Robots, Fund People"
date: 2026-02-25
description: "A new tax on automation infrastructure that starts at £34-46 billion and grows every year machines replace workers."
---

The UK government raises £420 billion a year from taxing workers' wages. Income Tax brings in £250 billion. National Insurance adds another £170 billion. Together, that is 42% of all government revenue. Every pound of it depends on people having jobs.

Automation is destroying those jobs. Not in some distant future. Now. Machine learning systems already outperform human diagnosticians, human traders, human translators and human customer service agents. Large language models handle legal research, code review, financial analysis and content production at a fraction of the cost of a salaried employee. Every AI system deployed is a salary that disappears from the tax base.

The fiscal arithmetic is simple and brutal. As employment falls, income tax and National Insurance revenue fall with it. Meanwhile, the people who lost those jobs need more support, not less. Revenue shrinks. Costs grow. The scissors close.

No existing UK tax solves this. Corporation Tax is an accounting fiction: multinationals structure their affairs to declare minimal profit in the UK regardless of how much economic activity they conduct here. VAT falls with consumer spending, which falls with unemployment. Capital Gains Tax is volatile. None of them track the physical infrastructure of automated production.

## The insight

Here is what I noticed while working as an infrastructure engineer: every computation consumes electricity. Every GPU cycle, every model inference, every automated warehouse robot, every algorithmic trade. A processor is, in thermodynamic terms, a nearly perfect heater. The energy it consumes is physical, measurable and unavoidable. You cannot transfer-price a kilowatt-hour to Dublin. You cannot restructure electrons through a subsidiary in Luxembourg. The meter reads what it reads.

And every offshore AI service crosses a physical border. When a UK business calls the OpenAI API, that data crosses an undersea cable. When a UK bank runs its models on AWS Ireland, the traffic is measurable at the Internet Exchange Point. These are not abstract flows. They are bits on fibre, countable at the point where the cable meets UK jurisdiction.

Tax those two things. Energy consumption and cross-border commercial data. The physical inputs to automated production. That is the Sovereign Energy and Bandwidth Excise (SEBE).

## How it works

SEBE has two components.

The **Sovereign Energy Excise (SEE)** taxes commercial electricity consumption in facilities above 500kW. That threshold exempts every small business, every shop, every restaurant. It targets data centres, automated warehouses, large-scale manufacturing and AI training facilities. The rate is tiered: £0.08/kWh for smaller facilities, rising to £0.45/kWh for hyperscalers. Metering uses a Hardware Root of Trust at three points (generation, storage and load) to prevent evasion.

The **Digital Customs Duty (DCD)** is a border tariff on commercial data crossing the UK digital border. Consumers are exempt. Domestic data centre traffic is exempt (it pays SEE on energy instead). DCD targets UK businesses using offshore cloud providers, calling offshore APIs or running compute workloads abroad. The rate is set so that offshoring is always more expensive than operating domestically. This incentivises building data centres in the UK rather than routing around the tax.

## The numbers

SEBE generates **£34-46 billion at launch** (2030, in 2026 prices). That is larger than Inheritance Tax, Stamp Duty, Climate Change Levy and Tobacco Duty combined.

Revenue grows automatically with automation:

- 2030: £38 billion
- 2035: £57 billion
- 2040: £93 billion
- 2045: £159 billion

All figures in 2026 real prices, CPI-indexed. These are derived from first principles using DESNZ energy consumption data, Ofcom bandwidth figures and current cloud provider pricing. The full revenue model, with sensitivity analysis, is open-source.

By 2040, SEBE approaches Corporation Tax scale. By 2045, it approaches National Insurance. It is the only UK tax whose revenue grows with the thing that is destroying the income tax base.

## Why it cannot be gamed

SEBE taxes physical resource consumption, not accounting constructs. That is the decisive difference from every other tax on business activity.

A multinational can declare zero profit in the UK by routing intellectual property through Ireland and royalty payments through the Netherlands. It cannot route its electricity consumption through Ireland. The data centre in Slough draws power from the grid and the meter records it. The cloud workload processed in Dublin generates data that crosses the UK border at a measurable exchange point.

Hardware Root of Trust metering (tamper-evident, cryptographically attested, bidirectional for battery storage) prevents dark compute. The three-point measurement system (generation, storage, load) closes the gaps that make energy theft possible. This is simpler to enforce than the current tax system, not harder. One physical measurement replaces thousands of pages of corporate accounting.

## Why not tax FLOPs?

Some people suggest taxing compute operations directly. It sounds logical but fails in practice.

There is no standard "FLOP." FP64, FP32, FP16 and INT8 all count differently. A GPU rated at 1,000 TFLOPS in FP16 gives a completely different number in FP32. There is no unit of computation that maps to a unit of economic work.

There is no meter for FLOPs. Energy has physical meters that cannot be faked. FLOPs has nothing except software-readable hardware counters (trivially spoofable) or self-declaration (obvious gaming incentive).

And you cannot meter FLOPs in a Virginia data centre from London. SEBE's DCD taxes the data crossing the border instead, which is measurable at the exchange point.

Energy is the correct proxy. Every computation, regardless of architecture (GPU, TPU, ASIC, quantum, neuromorphic), consumes electricity. Energy metering is deployed, tamper-resistant, architecture-neutral and rewards efficiency. Tax the energy.

## What the money is for

SEBE is a revenue mechanism, not a welfare design. The money could fund anything: Universal Basic Income, National Insurance reductions, NHS expansion, deficit reduction, or a combination. That is a political choice, not a technical constraint.

One illustrative use: a modest Universal Basic Income starting at roughly £650 per adult per year at launch, growing automatically as SEBE revenue increases with automation. Not life-changing in year one. But self-scaling. As machines replace workers, the payment grows. By the time automation has displaced most employment, the revenue exists to fund a Universal Living Income matching median take-home pay.

The mechanism tracks the problem. That is the point.

## What happens next

I have submitted SEBE as a policy proposal to the Green Party, which is the only UK party whose fiscal philosophy (MMT-informed, anti-austerity, pro-investment) is compatible with this kind of structural tax reform. The full proposal, including revenue model, cost model, distribution model and academic brief, is open-source and available for anyone to read, critique or build upon:

**[github.com/djarid/SEBE](https://github.com/djarid/SEBE)**

This needs challenge. It needs economists to stress-test the revenue projections. It needs network engineers to probe the DCD enforcement model. It needs fiscal conservatives to make the competitiveness argument so it can be properly answered. It needs people who disagree with it, not just people who like it.

The work is open. The licence is CC-BY 4.0. Use it, adapt it, argue with it.

Automation is coming whether we tax it or not. The question is whether we let the income tax base collapse while corporations capture the entire productivity gain, or whether we build a fiscal mechanism that ensures the wealth created by machines is shared with the people those machines replace.

SEBE is one answer. It starts at £38 billion and grows every year. The full workings are on the table. Tell me where I am wrong.
