---
layout: doc
title: "Appendix A: Metering, Enforcement and Billing"
description: Technical feasibility of SEE and DCD metering, enforcement and billing
doc_author: Jason Huxley
permalink: /docs/green_party_submission_appendix_a.html
version: 1.0
doc_date: March 2026
---
## Purpose

This appendix demonstrates that the two components of SEBE (the
Sovereign Energy Excise and the Digital Customs Duty) can be metered,
enforced and billed using infrastructure that largely already exists.

The policy proposal (parent document) sets out the "why." This appendix
sets out the "how" in sufficient technical detail to assess feasibility.
The specific rates, thresholds and institutional arrangements described
here are worked examples, not fixed policy. They are intended as a
starting point for expert consultation.

---

## A1. Sovereign Energy Excise: Metering

### A1.1 The Tax Base

SEE taxes commercial electricity consumption at facilities with IT
load above 500kW. The tax is levied on the entity that consumes the
energy, not the entity that generates it. This distinction is critical:
energy generators are not liable. Renewable energy projects, community
energy schemes and private wire operators are not taxed. The facility
drawing the power is.

### A1.2 Existing Metering Infrastructure

The UK already meters commercial electricity consumption at the
precision SEBE requires.

**Balancing and Settlement Code (BSC) Profile Class 5-8:** All
commercial facilities consuming above 100kW have been required to
install half-hourly (HH) settlement meters since 2001. These meters
report consumption data to Elexon (the BSC administrator) every 30
minutes. Elexon settles approximately £40 billion per year through
this data. The metering infrastructure is 24 years old, fully
deployed and operationally proven.

**Accuracy standard:** These meters are certified to MID (Measuring
Instruments Directive) Class 0.5S, providing ±0.5% accuracy. For a
5MW facility consuming approximately 40 GWh per year, this represents
a measurement uncertainty of ±200 MWh, or approximately ±£16,000 at
the £0.08/kWh rate. This is well within acceptable fiscal tolerance.

**Implication:** For every grid-connected facility above 500kW (the
vast majority of the target population), no new metering hardware is
needed. SEBE can be administered using existing BSC settlement data
from day one.

### A1.3 How Many Facilities?

SEBE targets approximately **1,500-3,000 facilities** nationally.
This includes:
- ~500 data centres (Cushman & Wakefield UK Data Centre Market 2025)
- ~200-400 automated warehouses and fulfilment centres
- ~500-1,500 large manufacturing facilities above 500kW IT load
- ~100-200 AI training and inference clusters

For comparison: the UK smart meter programme deployed 53 million
residential meters at a cost of £13.2 billion (BEIS 2019 CBA). SEBE
meters 0.003%-0.006% as many sites. The infrastructure challenge is
not comparable.

### A1.4 Hardware Root of Trust: Self-Generating Facilities

The one gap in existing metering is facilities that generate their
own electricity and never connect to the grid. A data centre running
on private solar, diesel backup or a small modular reactor would not
appear in BSC settlement data.

For these facilities, SEBE requires Hardware Root of Trust (HRoT)
metering at three points:

**Point of Generation (PoG):** Meters installed at the output of
every generation source (grid connection, solar array, diesel
generator, battery inverter). Measures total energy entering the
facility.

**Point of Storage (PoS):** Meters installed at battery systems.
Prevents temporal arbitrage (charging during off-peak and consuming
during peak to misrepresent consumption timing). Records charge and
discharge cycles.

**Point of Load (PoL):** Meters installed at the IT distribution
board. Measures actual energy consumed by computing infrastructure,
excluding cooling, lighting and ancillary systems.

**Liability formula:**

```
SEE Liability = PoL reading - (PoS_final - PoS_initial) × RTE allowance
```

Where RTE (Round-Trip Efficiency) allowance = 5% variance for battery
losses.

**Tamper evidence:** HRoT meters are cryptographically attested.
Each meter signs its readings with a hardware-bound private key
(similar to TPM attestation in computing hardware). A tampered meter
produces readings that fail cryptographic verification. The meter
reads what it reads.

**Deployment cost:** HRoT metering applies only to self-generating
facilities (estimated 100-300 sites nationally). At an estimated
£10,000-50,000 per installation (three meter points plus
communications), total capital cost is £3-15 million. This is borne
by the operator (precedent: HMRC Notice 179 requires fuel duty
taxpayers to install and maintain approved metering at their own
cost).

### A1.5 The 500kW Threshold

**Definition:** IT load specifically, not total facility energy
consumption. A data centre with 400kW of IT load and 200kW of
cooling is below the threshold (400kW IT load). A warehouse with
600kW of robotic systems and 100kW of lighting is above it (600kW
operational load).

**What it exempts:** Every household, every small business, every
shop, every restaurant, every office, every school, every GP surgery.
The median UK household consumes approximately 3,700 kWh per year
(Ofgem, 2025), equivalent to an average load of ~0.4kW. The 500kW
threshold is 1,250 times larger than average household consumption.

**Anti-fragmentation:** SEE liability is assessed on consolidated
energy consumption across all facilities under common ownership or
control. An operator cannot split a 2MW workload across four 500kW
sites to avoid the threshold. This follows the same principle as
group relief in Corporation Tax: related entities cannot claim
independent treatment. A beneficial ownership register ensures shell
structures cannot obscure common control.

---

## A2. Sovereign Energy Excise: Billing

### A2.1 Rate Structure

All rates in 2026 prices, CPI-indexed annually.

| IT Load Bracket | Rate (£/kWh) | Approximate Annual Liability (at 85% utilisation) |
|---|---|---|
| 0-500kW | Exempt | £0 |
| 500kW-5MW | £0.08 | £300K-2.4M |
| 5MW-50MW | £0.20 | £7.5M-75M |
| >50MW | £0.45 | £168M+ |

### A2.2 Billing Mechanism

**Supplier-reported model.** The energy supplier (or BSC settlement
agent for HH-metered sites) reports consumption data to HMRC monthly.
HMRC calculates the SEE liability and invoices the facility operator.
This is the same model used for the Climate Change Levy (CCL), which
has operated since 2001 with annual revenue of approximately £2
billion.

**Monthly invoicing.** Operators receive a monthly invoice based on
metered consumption. Payment terms are 30 days from invoice date.
Late payment interest accrues at the Bank of England base rate plus
2.5% (standard HMRC terms).

**For self-generating facilities with HRoT:** The facility operator
submits meter readings monthly via the National Telemetry Agency
(NTA) digital portal. Readings are cryptographically verified against
the HRoT attestation chain. Discrepancies trigger automatic audit.

### A2.3 Administrative Cost

SEBE is administratively simpler than income tax. There are no
deductions, no allowances, no exemptions to negotiate, no corporate
structures to interpret. The liability is a function of meter
readings and a published rate table.

**Estimated administrative cost:** Less than 1% of revenue.

For comparison:
- Income Tax administrative cost: approximately 1.1% of revenue
  (HMRC Annual Report 2024-25)
- VAT administrative cost: approximately 0.8% of revenue
- Corporation Tax administrative cost: approximately 1.5% of revenue

SEBE is simpler than all three because the measurement is physical,
not declarative.

### A2.4 Context: SEE Rates Relative to Existing Energy Costs

SEE does not replace existing electricity costs. It is levied on top
of the commercial electricity price.

| Cost Component | Approximate Rate |
|---|---|
| UK commercial electricity (wholesale + network) | £0.22-0.28/kWh |
| Climate Change Levy | £0.00775/kWh |
| **SEE Tier 1 (500kW-5MW)** | **£0.08/kWh** |
| **SEE Tier 2 (5MW-50MW)** | **£0.20/kWh** |
| **SEE Tier 3 (>50MW)** | **£0.45/kWh** |

For a Tier 1 facility, SEE adds approximately 29-36% to the energy
bill. For a Tier 3 hyperscaler, SEE approximately doubles it.

For context: energy is 15-25% of data centre operating costs
(Uptime Institute, 2024). Hyperscaler operating margins are 28-42%
(Microsoft Azure 42%, AWS 37%, GCP 28%, as reported in FY2025
earnings). The SEE liability is material but absorbable, particularly
at the lower tiers.

---

## A3. Digital Customs Duty: Metering

### A3.1 The Tax Base

DCD taxes commercial data crossing the UK digital border. It applies
to UK businesses using offshore compute (cloud providers, API
services, offshore processing). It does not apply to consumers,
educational institutions (JANET network), NHS or emergency services.

### A3.2 Where the Measurement Happens

Commercial internet traffic enters and leaves the UK through a small
number of physical chokepoints:

**Internet Exchange Points (IXPs):** LINX (London Internet Exchange,
peak throughput ~7 Tbps), LONAP (London Network Access Point),
IXLeeds. These are the physical locations where UK internet networks
interconnect with each other and with international carriers.

**Submarine cable landing stations:** All intercontinental fibre
enters the UK at a submarine cable landing station. These are
fixed physical locations.

**Satellite ground stations:** Satellite internet providers
(Starlink, OneWeb) operate licensed ground stations in the UK. They
are subject to the same DCD obligations as terrestrial carriers.

All three are existing infrastructure. DCD does not require building
new measurement points. It requires reporting obligations at points
where traffic is already counted for commercial purposes (ISPs
already meter aggregate throughput for billing, peering and capacity
planning).

### A3.3 Three-Layer Classification

DCD must distinguish commercial cross-border traffic from consumer
traffic without inspecting the content of any communication. Three
layers of metadata analysis achieve this:

**Layer 1: BGP Community Tagging.** Tier-1 ISPs tag traffic with
BGP (Border Gateway Protocol) community attributes identifying the
originating autonomous system (AS). Commercial AS numbers are mapped
to registered entities. Traffic destined for specific IP prefixes
(e.g., `52.95.100.0/24` for AWS Ireland, `104.44.0.0/16` for Azure
Netherlands) is identifiable regardless of encryption. BGP routing
is public infrastructure data, not private communication.

**Layer 2: SNI-Based Classification.** The Server Name Indication
(SNI) field in TLS handshakes reveals the destination hostname
(e.g., `api.openai.com`, `eu-west-1.compute.amazonaws.com`). This
distinguishes commercial API traffic from personal browsing. SNI
operates during the TLS handshake, before encryption begins. No
payload content is examined.

**Layer 3: Flow Metadata Analysis.** ISPs report aggregate flow
metadata using IPFIX/NetFlow data to identify commercial patterns:

- **Sustained symmetric flows.** Human browsing is asymmetric (small
  requests, large responses). Commercial compute generates sustained
  bidirectional flows with near-symmetric packet rates.
- **Machine-timed packet intervals.** Human traffic has variable
  inter-packet timing. Automated traffic exhibits regular,
  sub-millisecond intervals.
- **Connection persistence.** Commercial tunnels maintain long-lived
  connections (hours to days). Human browsing generates many
  short-lived connections.
- **Volume-to-endpoint ratio.** A single endpoint transferring 500GB+
  to a single offshore IP in a month is flagged for investigation.

### A3.4 Design Principles

**No payload inspection.** DCD enforcement operates on metadata only:
packet timing, size, flow duration, BGP routing, SNI headers. The
content of encrypted traffic is never examined. This is a design
constraint, not a preference.

**Consumer exemption is absolute.** Residential users do not pay DCD.
Enforcement controls that degrade residential internet service or
monitor individual household activity are excluded.

**Net neutrality is maintained.** Traffic is not shaped, throttled or
degraded based on content, source or commercial classification.
Enforcement operates through billing and compliance obligations, not
network manipulation.

### A3.5 Compliance Obligation

Every UK business using offshore compute services must register its
cross-border data flows with HMRC's Digital Customs Division. This
includes cloud provider contracts, API subscriptions, any regular
data transfer to non-UK endpoints. Failure to register is tax
evasion.

The state does not need to detect every byte of cross-border traffic.
The business must declare its traffic. The three-layer classification
system serves as an audit tool to detect undeclared flows, not as the
primary enforcement mechanism. This is the same model as VAT: the
business declares its liability, and HMRC audits using independent
data sources.

---

## A4. Digital Customs Duty: Billing

### A4.1 Rate Structure

| Annual Border Traffic | Rate | Approximate Annual Liability |
|---|---|---|
| < 10 PB/year | £200/TB | Up to £2M |
| 10-100 PB/year | £400/TB | £4M-40M |
| > 100 PB/year | £800/TB | £80M+ |

### A4.2 Rate Rationale: SEE-Equivalence

DCD rates are calibrated so that offshoring compute is always more
expensive than operating domestically (where the operator pays SEE
instead of DCD). This creates a Pigouvian incentive for UK data
centre investment.

| SEE Tier | Domestic SEE Cost/MW/yr | Offshore DCD Cost/MW/yr (@£400/TB) | Ratio |
|---|---|---|---|
| 500kW-5MW (£0.08) | £0.8M | £2.8M | Offshore 3.5x more expensive |
| 5MW-50MW (£0.20) | £2.0M | £2.8M | Offshore 1.4x more expensive |
| >50MW (£0.45) | £4.3M | Tiered by volume | Always more expensive |

Based on approximately 7,000 TB per MW per year of sustained
operation (balanced workload mix: 20% AI, 50% web/SaaS, 30% CDN,
at 85% utilisation, PUE 1.3). Full derivation in [SEBE Revenue Model](revenue_model.html)
Section 4.

The message to operators: build in the UK and pay SEE, or build
offshore and pay more. Either way, the automated production is taxed.

### A4.3 Billing Mechanism

**Quarterly self-assessment.** UK businesses registered for DCD
submit quarterly returns declaring their cross-border commercial data
volumes, broken down by offshore destination and service type. HMRC
calculates the DCD liability from the declared volumes and the
published rate table.

**ISP flow data as audit check.** ISPs submit aggregate commercial
flow reports to the Digital Customs Division quarterly. These reports
contain no individual content, only aggregate volume by BGP community
tag and destination AS. Discrepancies between declared volumes and
ISP-reported flows trigger audit.

**Payment terms:** 30 days from quarterly assessment. Standard HMRC
late payment terms apply.

---

## A5. Enforcement Architecture

### A5.1 Four Layers

| Layer | Mechanism | Purpose |
|---|---|---|
| **Structural** | 500kW threshold, consumer exemption, anti-fragmentation rules | Defines the tax base, excludes small operators and households |
| **Physical** | Energy meters (BSC/HRoT), IXP traffic counters | Provides tamper-resistant measurement at physical chokepoints |
| **Compliance** | Registration obligation, quarterly self-assessment, beneficial ownership register | Places the reporting burden on the taxpayer |
| **Detection** | ISP flow analysis, BGP monitoring, smart meter load profiling, reconciliation audits | Identifies undeclared activity as an audit tool |

### A5.2 Institutional Requirements

**National Telemetry Agency (NTA):** A new body responsible for HRoT
meter certification and deployment, meter data collection and
reconciliation, technical standards for metering hardware and
coordination with Ofgem (energy) and Ofcom (communications).

**Digital Customs Division (DCD-D):** A new division within HMRC
responsible for DCD assessment and collection, commercial cross-border
traffic registration, ISP flow reporting oversight, audit and
investigation of suspected evasion and coordination with
international counterparts.

**Estimated staffing:** 5,000-10,000 civil servants across NTA and
DCD-D (estimated by analogy: Ofgem employs ~1,600 staff; HMRC's
Customs and Excise division ~3,000; combined metering and enforcement
scope suggests a larger body). For context: HMRC currently employs
approximately 65,000 staff.

### A5.3 Accepted Leakage

No tax achieves 100% compliance. SEBE's estimated leakage is 3-7%
of revenue (£1-3 billion at the £38 billion mid-scenario launch).
This is comparable to existing tax gap rates:

| Tax | HMRC Tax Gap (2023-24) (HMRC, *Measuring Tax Gaps 2024-25 Edition*) |
|---|---|
| Income Tax | 3.8% |
| VAT | 4.8% |
| Corporation Tax | 10.6% |
| **SEBE (estimated)** | **3-7%** |

SEBE's leakage rate is comparable to income tax (which has 80 years
of enforcement maturity) and significantly better than Corporation
Tax (which depends on self-reported accounting that multinationals
routinely optimise).

The reason: SEBE's primary enforcement surface is physical
measurement, not legal declaration. You can restructure a profit
statement. You cannot restructure a kilowatt-hour.

---

## A6. Comparison to Existing Fiscal Enforcement

| | Income Tax | Corporation Tax | VAT | **SEBE** |
|---|---|---|---|---|
| Tax base | Declared earnings | Declared profit | Declared sales | **Physical consumption (kWh, TB)** |
| Measurement | Self-declaration + audit | Self-declaration + audit | Self-declaration + audit | **Hardware meters + audit** |
| Evasion method | Undeclared income, cash economy | Transfer pricing, IP routing, jurisdictional arbitrage | Missing trader fraud, carousel fraud | **Threshold splitting, dark compute, encrypted tunnels** |
| Evasion cost | Low (cash is untraceable) | Low (legal structures are cheap) | Medium (requires fake invoicing) | **High (physical infrastructure is expensive to duplicate or conceal)** |
| HMRC Tax Gap | 3.8% | 10.6% | 4.8% | **3-7% (estimated)** |

SEBE's enforcement advantage is that its tax base is physical, not
financial. A multinational can declare zero profit in the UK through
transfer pricing. It cannot route its electricity consumption through
a subsidiary in Luxembourg. The meter reads what it reads.

---

## A7. Outstanding Technical Work

This appendix describes the enforcement framework at a level
sufficient for policy feasibility assessment. Detailed technical
specifications remain to be developed through expert consultation:

1. **HRoT hardware specification:** Cryptographic protocols, meter
   form factor, communication standards, certification process.
   Requires engagement with metrology specialists and energy metering
   manufacturers.

2. **ISP flow reporting framework:** Legal basis for ISP reporting
   obligations, data formats (IPFIX/NetFlow templates), reporting
   frequency, privacy safeguards. Requires engagement with Ofcom and
   ISP industry.

3. **NTA institutional design:** Governance structure, relationship
   to Ofgem and HMRC, staffing model, IT systems. Requires
   consultation with existing regulatory bodies.

4. **International coordination:** Bilateral agreements for DCD
   enforcement with major offshore compute jurisdictions (Ireland,
   Netherlands, US). Not required for unilateral operation but
   desirable for reducing evasion.

5. **ECH (Encrypted Client Hello) monitoring:** As TLS 1.3 ECH
   adoption increases, SNI-based classification (Layer 2) will become
   less effective. BGP and flow metadata (Layers 1 and 3) remain
   functional regardless. Timeline for ECH impact assessment: 2028-2030.

These are implementation details, not feasibility blockers. The core
measurement infrastructure (BSC settlement meters, IXP traffic
counters) exists and has operated at scale for decades.

---

*Copyright 2026 Jason Huxley. Licensed under CC-BY 4.0.*
