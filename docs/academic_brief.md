# Infrastructure-Based Taxation for the Post-Employment Economy

## The Sovereign Energy and Bandwidth Excise (SEBE) Framework

**Author:** Jason Huxley
**Date:** February 2026
**Version:** 3.0
**Status:** Working Paper

---

## Abstract

As automation achieves parity with human productive capacity,
employment-based tax systems face structural collapse. This paper proposes
the Sovereign Energy and Bandwidth Excise (SEBE), a novel fiscal framework
that taxes the physical infrastructure of automated production: energy
consumption (kWh) and data throughput (Mbps). SEBE generates £31-38
billion at launch (comparable to Inheritance Tax + Stamp Duty + CCL +
Tobacco combined), growing automatically with automation to £93 billion
by 2040 and £159 billion by 2045. This paper presents SEBE as a
general-purpose revenue mechanism that addresses the fiscal crisis of
technological unemployment; an accompanying working paper details one
illustrative distribution model (two-stage UBI to Universal Living Income).

**Keywords:** Automation, taxation, Universal Basic Income, fiscal policy,
energy economics, digital economy, post-employment

---

## 1. Introduction

### 1.1 The Automation Paradox

Advanced economies face a fundamental contradiction:
- **Productive capacity** increasing (automation, AI, robotics)
- **Tax revenue** decreasing (fewer employed workers)
- **Social spending** increasing (displaced workers need support)

**Result:** Fiscal crisis precisely when society is most productive.

### 1.2 The Employment Tax Dependency

UK fiscal model depends critically on employment taxation:

| Tax Source | Revenue (£B) | % of Total | Employment-Linked |
|---|---|---|---|
| Income Tax | 250 | 25% | Yes |
| National Insurance | 170 | 17% | Yes |
| Corporation Tax | 100 | 10% | Partially |
| VAT | 160 | 16% | Indirectly |
| **Total Employment-Linked** | **420+** | **42%+** | **Direct dependency** |

As employment decreases, this revenue base erodes.

### 1.3 Research Question

**Can infrastructure-based taxation replace employment taxation in a
post-labour economy, and what transition mechanism enables a credible path
from current fiscal arrangements to universal income provision?**

This paper proposes and analyses one such mechanism: the Sovereign Energy
and Bandwidth Excise, with a two-stage distribution model that addresses
the sequencing problem.

---

## 2. Theoretical Framework

### 2.1 Value Creation in Automated Production

**Classical economics:** Value = Labour + Capital
**Automated economics:** Value = Energy + Capital + Information

**Implications:**
- Labour becomes marginal input
- Energy and computation become primary inputs
- Tax base must shift accordingly

### 2.2 Physical Infrastructure as Tax Base

**Advantages of infrastructure taxation:**

1. **Measurable:** Physical infrastructure (power lines, fibre optics) provides objective data
2. **Unavoidable:** Production requires energy and data (can't offshore completely)
3. **Progressive:** Large-scale operations use more, pay proportionally more
4. **Future-proof:** Captures automation dividend as technology advances

### 2.3 Pigouvian Benefits

SEBE functions as **double dividend tax:**
- **Revenue** for universal income (primary purpose)
- **Environmental** benefit (energy efficiency incentive)
- **Industrial policy** (onshore compute investment)

### 2.4 The Sequencing Problem

Previous universal income proposals face a credibility gap: full universal
income (matching median living standards) requires revenues far exceeding
any single tax instrument. This paper addresses the sequencing problem
through a two-stage model where Stage 1 ramps with a single new revenue
source (starting modestly and growing with automation), creating an
economic feedback loop that funds the transition to Stage 2.

---

## 3. The SEBE Mechanism

### 3.1 Component 1: Sovereign Energy Excise (SEE)

**Tax base:** Commercial electricity consumption above threshold

**Coverage:** Facilities with IT load >500kW

**Measurement infrastructure:**

Three-point metering (Hardware Root of Trust):
- **Point of Generation (PoG):** Grid ingress, private generation
- **Point of Storage (PoS):** Battery systems (prevents temporal arbitrage)
- **Point of Load (PoL):** Actual consumption at infrastructure

**Liability calculation:**
```
SEE = PoL - (PoS_final - PoS_initial) x Efficiency_Allowance
```

**Prevents evasion:**
- Dark compute nodes (unmetered generation)
- Storage gaming (charging off-peak, using on-peak without metering)

### 3.2 Component 2: Digital Customs Duty (DCD)

**Tax base:** Commercial data crossing the UK digital border (both directions)

**Implementation:** Internet Exchange Point (IXP) level enforcement

**Who pays DCD:**
- UK businesses using offshore cloud (AWS Ireland, Azure Netherlands, GCP Belgium)
- UK businesses calling offshore APIs (OpenAI US, Anthropic US)
- UK financial firms with offshore compute facilities
- Any UK commercial entity whose data crosses the UK digital border

**Who does not pay DCD:**
- UK consumers (exempt)
- UK businesses using UK-based data centres (pay SEE instead)
- Educational and research institutions (JANET, exempt)
- NHS and emergency services (exempt)

**Technical enforcement:**
- **BGP Community Tagging:** Identifies commercial traffic at Tier-1 gateways
- **SNI analysis:** Distinguishes commercial API calls from personal use
- **Flow symmetry:** Detects compute workload patterns

**DCD rate rationale:**
DCD is set so that offshoring compute is always more expensive than
operating domestically (where the operator pays SEE). This incentivises
building UK data centres. The rate is derived from the SEE-equivalent
cost per unit of border-crossing data (see `revenue_model.md` Section 4
for full derivation).

### 3.3 Rate Structures

**Energy (derived from DESNZ consumption data, see `revenue_model.md`):**

| Bracket | Rate (£/kWh) | Taxable TWh | Annual Revenue |
|---|---|---|---|
| 500kW-5MW | 0.08 | ~25 | £2.0B |
| 5MW-50MW | 0.20 | ~25 | £5.0B |
| >50MW | 0.45 | ~20 | £9.0B |
| Non-compute commercial | weighted | ~60 | £8-12B |
| **Total SEE** | | **~130** | **£24-28B** |

Note: Total UK commercial/industrial electricity is ~150 TWh, but only
~70 TWh is consumed in facilities above the 500kW threshold. The
remainder falls below the exemption. Non-compute commercial energy
(manufacturing, logistics, automated warehouses) contributes a further
~60 TWh at lower weighted rates. Revenue grows with automation (see
growth projections below).

**Bandwidth (derived from data centre economics, see `revenue_model.md`):**

| Type | Rate | Annual Revenue |
|---|---|---|
| Domestic traffic | Exempt | £0 (pays SEE instead) |
| Cross-border (< 10 PB/yr) | £200/TB | |
| Cross-border (10-100 PB/yr) | £400/TB | |
| Cross-border (> 100 PB/yr) | £800/TB | |
| **Total DCD** | | **£7-10B** |

**Combined SEBE at launch: £31-38 billion/year**

**Growth trajectory (automation-driven):**

| Year | SEE | DCD | Total SEBE |
|---|---|---|---|
| 2027 (launch) | £24B | £7B | £31B |
| 2030 | £30B | £8B | £38B |
| 2035 | £50B | £7B | £57B |
| 2040 | £83B | £10B | £93B |
| 2045 | £140B | £19B | £159B |

SEBE revenue is self-scaling: as automation replaces human labour,
the tax on automation infrastructure grows automatically.

---

## 4. Revenue Analysis

### 4.1 Scale Comparison

**SEBE at launch (£31-38B) is comparable to:**
- Inheritance Tax + Stamp Duty + CCL + Tobacco combined (~£34B)
- One-third of Corporation Tax (£100B)
- Growing to Corporation Tax scale (~£100B) by ~2038

**SEBE becomes a major revenue source within 10-15 years, tracking
automation growth.** By 2040, SEBE reaches £93B (mid-scenario); by 2045,
£159B (approaching National Insurance scale).

### 4.2 Tax Incidence

**Who actually pays?**

**Short-term:** Corporations (direct liability)

**Medium-term:** Mixed incidence
- **Consumer prices increase** (some pass-through)
- **Corporate profits decrease** (some absorbed)
- **Equilibrium:** Depends on market structure, elasticity

**Long-term:** Efficiency gains
- Companies invest in energy efficiency
- Datacenters relocate to UK (cheaper than offshore + 2x tax)
- **Net effect:** Lower energy consumption, higher UK investment

### 4.3 Economic Efficiency

**Distortions:**
- Penalises energy-intensive industries
- May favour labour over automation (if rates too high)

**Efficiencies:**
- Corrects automation externality (unemployment)
- Pigouvian environmental benefit
- Simpler than income/corporate tax (reduces compliance costs)

**Net assessment:** More efficient than current system if rates calibrated
correctly

---

## 5. Revenue Application

### 5.1 The Income Tax Replacement Argument

SEBE's primary function is replacing the employment-linked tax revenue
that automation erodes. This is not a welfare proposal; it is a fiscal
sustainability mechanism.

| Year | SEBE Revenue | As % of Income Tax (£250B) |
|---|---|---|
| 2027 | £31-38B | 12-15% |
| 2035 | £57-80B | 23-32% |
| 2040 | £93-135B | 37-54% |
| 2045 | £159B+ | 64%+ |

SEBE does not need to replace income tax immediately. It needs to grow
faster than income tax shrinks. At projected growth rates (10-15% per
annum, tracking compute capacity), the crossover occurs in the 2040s.

### 5.2 Illustrative Distribution Model

One possible use of SEBE revenue is universal income provision. An
accompanying working paper (`distribution_model.md`) details a two-stage
model:

- **Stage 1:** UBI starting at ~£400/adult/year from launch revenue,
  ramping with SEBE growth. Universal Basic Services (free transport,
  energy, broadband) phase in as revenue permits. Target rate
  £2,500/adult/year.
- **Stage 2:** UBI ratchets toward Universal Living Income
  (£29,000/adult/year, matching median take-home pay of £31,627 minus
  £2,500 UBS value). Requires SEBE plus complementary progressive
  taxation. Total Stage 2 cost ~£1.810T/year.

This is illustrative. SEBE revenue could equally fund NI reductions,
deficit reduction, NHS expansion, or a combination. The mechanism is
the contribution; the distribution is a political choice.

### 5.3 Economic Feedback Loop

If SEBE revenue is redistributed (as UBI or public services), a
self-reinforcing cycle emerges: redistribution increases consumer
spending, which generates additional conventional tax revenue (income
tax, VAT, business rates), which funds further redistribution. The
magnitude of this feedback loop is an empirical question requiring
formal macroeconomic modelling.

---

## 6. Macroeconomic Effects

### 6.1 Aggregate Demand Maintenance

**Problem:** Automation leads to unemployment, demand collapse, recession

**SEBE + UBI solution:**
- Corporations pay SEBE (withdraws purchasing power)
- Population receives UBI/ULI (restores purchasing power)
- **Net effect:** Demand maintained despite employment loss

**Prevents:** Technological deflation spiral

### 6.2 Inflation Management

**Concern:** Universal income payments cause inflation

**Stage 1 response:**
- UBI starts at £400/year (minimal relative to existing incomes)
- SEBE withdraws £31-38B from corporate sector (anti-inflationary)
- UBS directly reduces household costs (deflationary for recipients)
- **Stage 1 inflation risk is low**

**Stage 2 response:**
- Full ULI at £1.810T is a significant fiscal expansion
- **Depends critically** on productivity gains from automation
- If automation increases output 2-3x (plausible): sustainable
- If productivity gains are modest: inflationary
- Requires MMT-informed fiscal management

**Key insight:** The two-stage approach allows inflation dynamics to be
observed and managed incrementally, rather than requiring a single large
fiscal expansion.

### 6.3 Labour Market Effects

**Concern:** Universal income destroys work incentive

**Stage 1 response:**
- £2,500/year is a supplement, not a replacement
- No rational person leaves employment for £208/month
- Evidence from existing programmes confirms this:
  - Alaska Permanent Fund: No employment reduction
  - Finland UBI pilot: Slight employment increase
  - Kenya GiveDirectly: Increased entrepreneurship

**Stage 2 response:**
- By Stage 2, automation has displaced much employment anyway
- ULI enables voluntary work, entrepreneurship, care work, creative pursuits
- **Automation** destroys jobs, not ULI

---

## 7. Technical Feasibility

### 7.1 Metering Infrastructure

**Current UK capability:**
- Smart meters: 50M+ deployed (residential)
- Commercial metering: Standard for large consumers
- **Required:** Hardware Root of Trust upgrade (tamper-proof)

**Cost:** £2-5 billion (metering infrastructure deployment)
**Timeline:** 3-5 years

**Precedent:** UK successfully deployed smart meters nationwide (2010-2025)

### 7.2 Digital Border Implementation

**Current UK capability:**
- Deep Packet Inspection (DPI): Used for copyright enforcement
- BGP routing: UK controls major IXPs (LINX, etc.)
- SNI inspection: Standard TLS handshake analysis

**Required additions:**
- Traffic classification algorithms (commercial vs personal)
- Automated quota management systems
- Tier-1 ISP integration

**Cost:** £500M-1 billion
**Timeline:** 2-3 years

### 7.3 Administrative Overhead

**SEBE collection:**
- Automated (meters to central database)
- Monthly corporate invoicing
- **Simpler** than current tax system (no complex deductions, allowances, exemptions)

**Administrative cost:** <1% of revenue (£2-5B)

**Compare to:** Income tax collection (HMRC budget £4.5B for much more complex system)

---

## 8. International Implications

### 8.1 Competitive Dynamics

**UK implements SEBE unilaterally:**

**Risks:**
- Companies threaten relocation
- "Competitive disadvantage" rhetoric

**Mitigations:**
- Offshore compute 2x tax (cheaper to stay in UK)
- EU coordination (prevent haven shopping)
- First-mover advantage (UK becomes global leader)

### 8.2 Digital Sovereignty

**SEBE enables:**
- UK datacenter investment (tax advantage)
- Domestic AI/cloud infrastructure
- **Reduced dependence** on US tech (AWS, Azure, Google)

**Strategic benefit:** Compute sovereignty (like energy independence)

### 8.3 Export Potential

**Other nations face same crisis:**
- Automation unemployment
- Tax base erosion
- Fiscal sustainability

**UK SEBE model:**
- Proven technical feasibility
- Demonstrated revenue generation
- **Exportable framework** (bilateral/EU coordination)

**UK positions as:** Policy innovator in post-employment economics

---

## 9. Comparison to Alternative Approaches

### 9.1 Robot Tax / FLOPS Tax (Direct Compute Tax)

Several proposals tax automation directly: per robot, per AI model, or
per unit of computation (FLOPS). All share fundamental problems that
SEBE avoids.

**9.1.1 The "Robot Tax" variant**

**Proposal:** Tax robots or AI systems per unit deployed.

**Problems:**
- **Definition:** What counts as a "robot"? A warehouse arm? A chatbot?
  A spreadsheet macro? An algorithm trading stocks? The boundary between
  "automation" and "software" is undefined.
- **Measurement:** How do you count them? Self-reporting is unverifiable.
  Inspection is impractical.
- **Evasion:** Trivial. Relabel, modularise, offshore.

**9.1.2 The "FLOPS Tax" variant**

**Proposal:** Tax floating-point operations per second (FLOPS) as a
proxy for compute work. This is the most technically sophisticated
variant and deserves detailed rebuttal.

**Problem 1: FLOPS is not a well-defined unit.**

A floating-point operation varies by precision: FP64 (double), FP32
(single), FP16 (half), BF16 (brain float), INT8, INT4. Modern AI
inference runs predominantly at INT8 or INT4. A GPU rated at 1,000
TFLOPS in FP16 produces a different number for FP32 and is not
meaningfully comparable to a TPU running INT8 matrix multiplications.
There is no standard "FLOP" that maps to a unit of economic work.

**Problem 2: No physical measurement point.**

Energy has meters. Bandwidth has packet counters. FLOPS has nothing.
The only way to measure FLOPS is through hardware performance counters
(software-readable, trivially spoofable) or self-declaration (obvious
gaming incentive). There is no equivalent of a power meter that can be
installed at a facility boundary and trusted.

**Problem 3: Evasion is architectural.**

To reduce FLOPS liability:
- Switch from GPU to ASIC (TPUs, custom silicon report differently)
- Use lower-precision formats (INT4 inference does fewer "FLOPS" per
  unit of useful work than FP32)
- Use neuromorphic or analog compute (no floating-point operations at all)
- Run workloads that are I/O-bound rather than compute-bound (database
  queries, network routing, storage operations are high-value but low-FLOPS)

Each of these is a legitimate engineering choice. Taxing FLOPS creates
perverse incentives to adopt them purely for tax avoidance, not
efficiency.

**Problem 4: Punishes efficiency, rewards waste.**

A newer GPU that completes a task in 100 TFLOPS pays less FLOPS tax
than an older GPU that takes 500 TFLOPS for the same task. This
incentivises keeping old, power-hungry hardware running (fewer FLOPS
per watt) rather than upgrading to efficient silicon. The environmental
effect is the opposite of what any green tax should achieve.

**Problem 5: International enforcement is impossible.**

How do you tax FLOPS consumed offshore? You cannot meter a GPU in
Virginia from London. SEBE solves this with DCD (border tariff on
cross-border data), which is measurable at Internet Exchange Points.
FLOPS consumed offshore are invisible to the taxing authority.

**Why energy is the correct proxy:**

Every computation, regardless of architecture, precision, instruction
set, or physical location, consumes energy. A TPU doing INT8 inference
uses watts. A neuromorphic chip uses watts. A quantum processor uses
watts. Energy is:

- **Architecture-neutral:** works for GPUs, ASICs, TPUs, FPGAs, future hardware
- **Physically measurable:** power meters exist, are deployed, and are tamper-resistant (Hardware Root of Trust)
- **Unavoidable:** you cannot do useful work without consuming energy
- **Efficiency-rewarding:** more efficient hardware uses less energy per unit of work, paying less SEE (the right incentive)

**SEBE taxes the universal physical input to all computation.** A FLOPS
tax taxes one particular arithmetic operation on one class of hardware.

### 9.2 Negative Income Tax

**Proposal:** Integrate welfare into tax system

**Problems:**
- Still depends on employment tax base
- Complex phase-out (high marginal rates)
- Requires employment to receive (excludes non-workers)

**SEBE advantage:** Independent of employment, simple universal payment

### 9.3 Land Value Tax

**Proposal:** Tax unimproved land value

**Strengths:** Economic efficiency, hard to evade

**Problems:**
- Revenue insufficient (£50-100B estimate)
- Politically difficult (homeowner opposition)
- Doesn't address automation directly

**Complementary:** LVT + SEBE together cover both land and automation

### 9.4 Financial Transaction Tax

**Proposal:** Tax stock trades, currency transactions

**Strengths:** Large potential base

**Problems:**
- Trading relocates offshore (London loses to Paris/Amsterdam)
- Revenue unstable (volume drops when markets fall)
- Doesn't tax real economy automation

**SEBE advantage:** Taxes real production (energy/compute) not financial transactions

### 9.5 Job Guarantee

**Proposal:** Government guarantees employment for all

**Problems:**
- Coercive (compels labour in exchange for income)
- Administratively complex (what jobs? who decides?)
- Fights automation rather than adapting to it
- Does not address the fiscal crisis (still depends on employment taxation)

**SEBE advantage:** Adapts fiscal system to automation rather than resisting it.
UBI/ULI is unconditional, not coerced.

---

## 10. Limitations and Further Research

### 10.1 Acknowledged Gaps

This paper provides:
- Technical specification for SEBE mechanism
- Two-stage distribution model with costings
- Order-of-magnitude revenue estimates
- Cited data sources with staleness dates

This paper does **not** provide:
- Detailed CGE (Computable General Equilibrium) model
- Behavioural elasticity measurements
- Optimal rate calculations
- Formal macroeconomic simulation of the feedback loop

**Required next steps:**
- Econometric modelling of tax incidence
- Industry-specific impact studies
- Pilot programme data collection
- International coordination feasibility analysis
- Formal modelling of the Stage 1 feedback loop dynamics

### 10.2 Key Uncertainties

**Energy component:**
- Actual commercial consumption data (estimates vary)
- Elasticity of demand (how much usage falls when taxed)
- Technical evasion potential (off-grid generation)

**Bandwidth component:**
- Precise UK commercial throughput unknown
- Offshore vs domestic compute split unclear
- Gaming potential (VPN, encryption, CDN caching)

**Distribution model:**
- Inflation impact at Stage 2 uncertain (depends on productivity gains)
- Feedback loop magnitude (how much does Stage 1 UBI boost conventional tax?)
- Transition timeline (how fast does automation displace employment?)
- Labour market effects debated (employment elasticity)

### 10.3 Research Agenda

**Phase 1: Data Collection (6 months)**
- Survey major energy consumers
- ISP commercial throughput study
- Estimate current SEBE tax base

**Phase 2: Modelling (12 months)**
- CGE model of SEBE implementation
- Behavioural response estimation
- Optimal rate calculation
- Feedback loop simulation

**Phase 3: Pilot (24 months)**
- Voluntary trial with 10-20 companies
- Measure compliance costs
- Validate revenue projections

**Timeline:** 3-4 years to full economic model and pilot validation

---

## 11. Policy Implications

### 11.1 Short-Term (2027-2030)

**If SEBE implemented:**
- New £31-38B revenue source at launch, self-scaling with automation
- Immediate fiscal headroom for redistribution (general revenue, not ring-fenced)
- Reduces income tax dependency from year one
- Drives energy efficiency and UK datacenter investment

### 11.2 Medium-Term (2030-2035)

**As automation accelerates:**
- SEBE revenue grows (more compute = more tax)
- Income tax revenue shrinks (fewer employed)
- **SEBE becomes a dominant revenue source**
- Government gains fiscal flexibility to expand redistribution as revenue permits

### 11.3 Long-Term (2035+)

**Post-employment transition:**
- SEBE revenue approaches National Insurance scale (£159B by 2045)
- Taxation divorced from labour (SEBE + wealth/land taxes)
- Fiscal foundation for universal income provision at meaningful levels
- UK demonstrates feasibility for other nations

See `distribution_model.md` for one detailed illustrative model of how
SEBE revenue could fund a two-stage universal income transition.

---

## 12. Implementation Considerations

### 12.1 Legal Framework

**Required legislation:**
- Energy Act amendments (commercial metering requirements)
- Telecommunications Act amendments (bandwidth monitoring)
- Finance Act (new tax schedules)
- Competition law (prevent monopoly gaming)

**Constitutional issues:**
- Privacy protections (individual traffic never inspected)
- Net Neutrality (maintained for personal use)
- Data protection (aggregate data only, GDPR-compliant)

### 12.2 Administrative Capacity

**New institutional requirements:**
- National Telemetry Agency (metering oversight)
- Digital Customs Division (bandwidth enforcement)
- UBI/ULI Payment Authority (distribution)

**Staffing:** 5,000-10,000 civil servants (compare to HMRC's 65,000)

**IT systems:** Central database, automated invoicing, fraud detection

### 12.3 International Coordination

**Bilateral agreements:**
- EU: Harmonised digital taxation
- OECD: Minimum standards (like 15% corporate tax)
- Commonwealth: Shared SEBE framework

**Without coordination:**
- Tax haven competition
- Regulatory arbitrage
- Reduced effectiveness

**Recommendation:** UK proposes SEBE as international standard (G20, OECD)

---

## 13. Risk Analysis

### 13.1 Implementation Risks

**Technical:**
- Metering failures (hardware malfunction)
- Evasion techniques (spoofing, dark generation)
- Gaming (companies split to stay under thresholds)

**Mitigation:** Hardware Root of Trust, regular audits, graduated thresholds

**Economic:**
- Companies relocate (capital flight)
- Prices increase (consumer impact)
- Innovation stifled (high compute costs)

**Mitigation:** Offshore penalty (2x rate), phased implementation,
competitive analysis

**Political:**
- Opposition from affected industries
- Public concern over "big government"
- Coalition instability (policy reversal)

**Mitigation:** Broad coalition building, clear public benefits (UBI),
constitutional protection

### 13.2 Macroeconomic Risks

**Inflation (Stage 2):**
- Full ULI at £1.810T is a significant fiscal expansion
- **Depends critically** on productivity gains from automation
- **If productivity 2-3x:** Sustainable
- **If productivity <1.5x:** Inflationary

**Recommended:** Two-stage approach allows gradual phase-in with
inflation monitoring at each step

**Competitiveness:**
- Higher energy costs for UK businesses
- **But:** Offset by 2x offshore penalty (encourages UK investment)
- **Net effect:** Unclear, requires modelling

**Financial markets:**
- Stage 1 launch is modest (£31-38B, comparable to existing small taxes)
- Stage 2 requires careful sequencing
- **Sterling volatility** possible at Stage 2

**Recommended:** Coordinate with Bank of England, gradual rollout,
international credibility building

---

## 14. Conclusion

The Sovereign Energy and Bandwidth Excise represents a viable fiscal
framework for post-employment economics. By taxing the physical
infrastructure of automated production (energy and data), SEBE:

- **Generates £31-38 billion at launch**, growing to £93B by 2040 and £159B
  by 2045 (self-scaling with automation)
- **Progressively replaces failing employment taxation** as automation advances
- **Creates immediate fiscal headroom** for redistribution from year one
- **Scales organically** with the problem it addresses (more automation =
  more revenue = more capacity for redistribution)
- **Drives economic efficiency** (energy conservation, UK datacenter investment)
- **Provides environmental co-benefits** (energy taxation incentivises efficiency)

**Key advantages over alternatives:**
- Objective measurement (kWh, Mbps)
- Difficult evasion (physical infrastructure)
- Future-proof (grows with automation)
- Progressive incidence (large operations pay more)
- **Revenue grows with the problem** (solves the sequencing problem)

**Critical uncertainties:**
- Precise revenue potential (requires detailed modelling)
- Inflation effects at Stage 2 (depends on productivity gains)
- Feedback loop dynamics (Stage 1 stimulus effects)
- International coordination (prevents tax haven competition)

**Recommended research priorities:**
1. Detailed econometric modelling (CGE analysis)
2. Industry consultation (compliance cost assessment)
3. Pilot programme (voluntary participation, data validation)
4. Feedback loop simulation (Stage 1 stimulus multiplier)
5. International feasibility study (EU/OECD coordination)

**SEBE provides the technical and economic foundation for transitioning to
a post-employment economy.** Revenue starts modestly and scales organically
with automation, providing increasing fiscal capacity for redistribution
without requiring politically impossible fiscal expansions at launch.
Further research is essential to refine parameters and validate assumptions,
but the core mechanism is sound and implementable. An accompanying working
paper (`distribution_model.md`) presents one detailed illustrative model
for how SEBE revenue could fund universal income provision.

---

## References

| Source | Data | Date |
|---|---|---|
| ONS ASHE 2025 | Median gross annual earnings (full-time): £39,039 | April 2025 (provisional) |
| ONS Mid-Year Population Estimates | UK population: 68.3 million | Mid-2023 |
| Ofgem Price Cap | Typical household energy: £1,758/year | Q1 2026 |
| HMRC | Income tax and NI rates 2025/26 | 2025/26 tax year |
| ORR Rail Finance | Rail fares income: £11.5B, govt funding: £11.9B | 2024/25 |

Full data sources, staleness dates, and detailed cost workings are
available in the accompanying cost model document.

**Additional references (to be expanded):**
- ONS energy consumption statistics
- Ofcom bandwidth data
- HMRC tax revenue reports
- Academic literature on UBI, automation taxation, fiscal policy
- International examples (Norway sovereign wealth fund, Luxembourg free
  transport, Singapore digital tax)

---

## Author Bio

Jason Huxley is an infrastructure and automation engineer with extensive
experience in large-scale enterprise systems and network architecture.
Background includes defence sector experience (Royal Corps of Signals)
and current work in quantitative research infrastructure.

**Contact:** [To be added]

---

## Appendices

### Appendix A: Technical Specifications
**Hardware Root of Trust Metering:**
- TPM-secured energy meters (tamper-evident)
- Bidirectional storage metering (battery systems)
- Cryptographic attestation (prevents spoofing)
- Real-time telemetry (immediate discrepancy detection)

**Digital Border Infrastructure:**
- BGP community tagging protocol
- SNI-based traffic classification
- Flow analysis algorithms
- Quota management systems

### Appendix B: Revenue Sensitivity Analysis

**Variables:**
- Energy tax rate (£0.08-0.45/kWh tiered)
- Bandwidth tax rate (£200-800/TB tiered, border tariff only)
- Threshold levels (500kW vs 5MW vs 50MW)
- Offshore multiplier (1.5x vs 2x vs 3x)
- Compliance rate (70% vs 85% vs 95%)

**Year 1 range:** £26B (pessimistic) to £45B (optimistic)
**Central estimate:** £31-38B
**2040 range:** £60B (low growth) to £135B (high growth)

Full derivation in `revenue_model.md`.

### Appendix C: Cost Model Summary

Full working available in `cost_model.md`, including:
- Population breakdown and assumptions
- Tax burden calculations on median earnings
- UBS component costing with transport demand elasticity
- Rail rent extraction analysis (ROSCO data from ORR 2024/25)
- Stage 1 and Stage 2 cost breakdowns
- Sensitivity analysis

### Appendix D: International Case Studies

**Norway Energy Taxation:**
- High energy costs
- Sovereign wealth fund model
- No emigration crisis (quality of life maintained)

**Luxembourg Free Public Transport (2020):**
- All public transport free at point of use since March 2020
- 20-30% increase in ridership
- Funded from general taxation
- Demonstrates feasibility of UBS transport component

**Singapore Digital Services Tax:**
- 7% on digital services
- Enforced at ISP level
- Demonstrates feasibility of digital taxation

**Estonia Digital Infrastructure:**
- Government digital backbone
- E-residency system
- Technical precedent for national telemetry

---

**This is a working paper. Comments and critiques welcome.**

**Suggested citation:** Huxley, J. (2026). Infrastructure-Based Taxation
for the Post-Employment Economy: The Sovereign Energy and Bandwidth Excise
Framework. Working Paper, v3.0.

© 2026 Jason Huxley
Licensed under CC-BY 4.0
You may use, adapt, and distribute this work
provided you credit the original author.
