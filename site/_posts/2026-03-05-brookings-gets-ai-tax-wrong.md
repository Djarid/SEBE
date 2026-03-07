---
layout: post
title: "Why Brookings Gets AI Taxation Wrong"
date: 2026-03-05
description: "The most prestigious think tank in Washington published a framework for taxing AI. It has a hole in it you could drive a data centre through."
image: /assets/images/brookings_header.jpeg
tags: [policy, economics, rebuttal, intermediate]
---

*The most prestigious think tank in Washington published a framework for taxing AI. It has a hole in it you could drive a data centre through.*

![Why Brookings Gets AI Taxation Wrong]({{ site.baseurl }}/assets/images/brookings_header.jpeg)

In January 2026, Anton Korinek and Lee Lockwood published "The Future of Tax Policy: A Public Finance Framework for the Age of AI" through the Brookings Institution. It is a careful, well-argued paper. It diagnoses the right problem: AI-driven automation will erode employment-linked taxation, which accounts for over 42% of UK tax receipts and roughly three quarters of US federal revenue. On the diagnosis, they are correct.

On the prescription, they are wrong in ways that matter.

Their answer is to shift from taxing labour to taxing consumption, while protecting AI capital from all taxation in the near term. They compare compute taxes to "taxing steel during the industrial revolution." They propose sovereign wealth funds and voluntary corporate windfall clauses as fiscal insurance.

I have spent seven years building a different answer. The Sovereign Energy and Bandwidth Excise (SEBE) taxes the physical infrastructure of automated production (energy consumption and cross-border commercial data) rather than the workers it displaces or the consumers it impoverishes. The full proposal, including revenue model and technical specification, is [open-source on GitHub](https://github.com/djarid/SEBE).

Here is where Brookings goes wrong, and why it matters.

## The consumption tax fallacy

The central pillar of the Brookings framework is consumption taxation. It does not stand up.

Consumption tax revenue requires consumers with purchasing power. If automation displaces workers (which the paper acknowledges is happening), those workers lose income. Unemployed people consume less. Consumption tax receipts fall. The revenue base erodes in lockstep with the problem it is supposed to solve.

The authors acknowledge this indirectly when they note that "government revenues from payroll taxes as a fraction of GDP will decline just as needs for retraining programs and transition support increase." They then propose consumption taxes to "bridge this gap." But the gap exists because people have less money to spend. Taxing their reduced spending does not bridge anything. It widens the gap.

This is a fiscal death spiral dressed up as tax reform: automation reduces employment, employment loss reduces consumption, reduced consumption reduces tax revenue, reduced revenue reduces the state's capacity to support displaced workers, reduced support further depresses consumption. Each turn of the cycle makes the next turn worse.

And consumption tax is regressive. This is not a contested point. It is established public finance. The authors know this and propose offsetting it through progressive design (taxing the difference between income and net savings at progressive rates). That offset requires knowing everyone's income and savings. It requires the same administrative apparatus as income taxation. They are proposing to solve the regressivity problem by rebuilding income tax inside the consumption tax. At which point: why not just build a new revenue base that does not depend on employment at all?

## "Don't tax capital" is a category error

The paper's second recommendation is to avoid taxing AI capital assets. They argue that robot taxes and compute taxes discourage investment and innovation. They compare compute taxes to "taxing steel during the industrial revolution: a self-defeating policy."

This conflates three different things, and SEBE is none of them.

A capital tax penalises ownership. A robot tax penalises the decision to deploy automation. SEBE does neither. SEBE taxes energy consumption at the point of load. The asset is irrelevant. What matters is how much electricity it draws.

A company that replaces 100 workers with one efficient server pays less SEBE than a company running a legacy data centre at twice the wattage for the same output. The incentive is to invest in better, more efficient capital. That is the opposite of discouraging investment.

The steel analogy is wrong. Taxing steel penalises the asset. SEBE taxes the coal that fires the furnace. The incentive is to build a better furnace, not to avoid building one.

By taxing energy consumption (not compute operations, not hardware ownership, not FLOPS), SEBE creates a direct financial incentive to build more efficient data centres, invest in renewable generation, optimise workloads and locate facilities where energy is cheapest and greenest. Every one of those is a productivity improvement. The tax incentive and the efficiency incentive point in the same direction.

## Voluntary commitments are not fiscal policy

The paper proposes "windfall clauses, voluntary commitments by AI companies to share gains broadly if they achieve transformative breakthroughs" as fiscal insurance.

I need to be blunt about this. Voluntary commitments are not tax policy. No government funds public services from corporate goodwill. OpenAI restructured from non-profit to capped-profit to for-profit in under five years. Anthropic's voluntary commitments exist at the pleasure of its board. Neither entity is bound by statute to share anything.

The paper also recommends sovereign wealth funds, which are a serious instrument. But they require a revenue source. Norway's Government Pension Fund Global is capitalised by petroleum taxation, which is a tax on energy production. That analogy supports SEBE, not the Brookings framework. You need a revenue mechanism to capitalise the fund. SEBE provides one. Windfall clauses do not.

## The category they cannot see

Here is the central intellectual failure of the paper. The Brookings framework offers a binary: tax consumption or tax capital. This is a false choice.

SEBE taxes neither.

It taxes the physical inputs to production: energy (kWh) and cross-border data (TB). These are not capital assets (owning a server is not taxed). They are not consumption (buying an AI service is not taxed). They are the operational footprint of automated production, measurable at physical infrastructure (power meters, internet exchange points) with existing technology. Consumers are exempt. SEBE applies only to commercial facilities above 500kW IT load. Your home, your local business, your corner shop pay nothing.

The paper cannot evaluate SEBE because its framework has no category for it. Infrastructure-based taxation sits outside the consumption-versus-capital binary that organises the entire analysis. The taxonomy is incomplete, so the best option is invisible.

## Revenue: theirs versus ours

Korinek and Lockwood do not provide revenue estimates for their consumption tax proposals. SEBE does.

SEBE generates £34-46 billion at launch in 2030 (2026 prices), growing to £93 billion by 2040 and £159 billion by 2045 as automation scales. All rates are CPI-indexed. All projections are in 2026 real prices. The full revenue model is published with source data and methodology.

The consumption tax alternative has no published revenue estimate, no rate structure, no implementation timeline and no growth model. It is a direction of travel, not a proposal.

![Revenue comparison: SEBE vs Brookings proposals]({{ site.baseurl }}/assets/images/brookings_table.png)

## What they get right

Credit where it is due. The paper correctly identifies that labour taxation is structurally doomed, that the fiscal crisis will arrive before political consensus, that international coordination is needed, and that timing matters. On all four points, SEBE agrees.

The disagreement is entirely about the mechanism. Korinek and Lockwood propose taxing displaced workers on their reduced consumption while protecting the infrastructure that displaced them. SEBE proposes taxing the infrastructure directly, at the physical layer where measurement is objective, evasion is difficult and revenue scales automatically with the problem.

## The question Brookings should be asking

The Brookings paper asks the right question: how do we fund government when AI replaces the workers whose wages fund government?

Their answer: tax what the workers buy.
SEBE's answer: tax what replaced them.

One of those shrinks as the problem grows. The other grows with it.

The full SEBE proposal (revenue model, cost model, technical specification, distribution model) is open-source at [github.com/djarid/SEBE](https://github.com/djarid/SEBE) under CC-BY 4.0. The Brookings paper is at [brookings.edu](https://www.brookings.edu/articles/future-tax-policy-a-public-finance-framework-for-the-age-of-ai/). Read both. Tell me which one has the numbers.

The full rebuttal, with detailed analysis of each Brookings recommendation, is [here]({{ site.baseurl }}/docs/brookings_rebuttal.html). The SEBE academic brief is [here]({{ site.baseurl }}/docs/academic_brief.html).

---

*Jason Huxley is an infrastructure and automation engineer (ex-Royal Corps of Signals) with 30 years' experience in large-scale enterprise systems. He is a member of the Green Party of England and Wales. His previous posts: [Tax Robots, Fund People]({{ site.baseurl }}{% post_url 2026-02-25-tax-robots-fund-people %}) and [Why I Joined the Green Party]({{ site.baseurl }}{% post_url 2026-02-28-why-i-joined-the-green-party %}).*
