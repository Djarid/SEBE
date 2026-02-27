# SEBE Evasion Vectors and Enforcement Framework

**Author:** Jason Huxley
**Version:** 1.0
**Date:** February 2026
**Status:** Working document
**Target audience:** Policy Development Committee, technical reviewers

---

## 1. Purpose

SEBE taxes two physical constraints of automated production: energy
consumption (SEE) and cross-border commercial data (DCD). Both operate
at physical chokepoints that are harder to evade than accounting
constructs like declared profit. They are not, however, impossible to
evade.

This document catalogues the known evasion vectors, assesses each for
severity and feasibility, and specifies the enforcement controls that
close them. The goal is not zero leakage (which would require
surveillance infrastructure incompatible with civil liberties). The
goal is to make evasion more expensive than compliance for any operator
at a scale that matters to the revenue base.

Reference documents:

- Revenue derivation: `revenue_model.md` (source of truth for all figures)
- Technical specification: `green_party_submission.md` Section 2
- Rate structures: `revenue_model.md` Sections 3-4

---

## 2. Design Principles

Before cataloguing threats, five enforcement principles constrain the
design space. Any proposed control that violates these is rejected
regardless of technical merit.

1. **No payload inspection.** DCD enforcement operates on metadata
   (packet timing, size, flow duration, BGP routing, SNI headers). The
   content of encrypted traffic is never examined. This is a red line,
   not a preference.

2. **Consumer exemption is absolute.** Residential users do not pay
   SEBE. Enforcement controls that degrade residential internet service
   or monitor individual household activity are excluded.

3. **Net Neutrality is maintained.** Traffic is not shaped, throttled
   or degraded based on content, source or commercial classification.
   Enforcement operates through billing and compliance obligations, not
   network manipulation.

4. **Physical measurement over accounting.** Energy meters read
   kilowatt-hours. Packet counters read bytes. Neither requires the
   taxpayer to self-report accurately. Where possible, the enforcement
   mechanism is a physical instrument, not a declaration.

5. **Proportionate enforcement.** Sub-threshold evasion that costs more
   to detect than the revenue it yields is accepted as leakage. The
   500kW SEE threshold and DCD's commercial-only scope already concede
   small-scale operations.

---

## 3. SEE Evasion Vectors

### 3.1 Threshold Splitting

**Threat:** An operator distributes compute across multiple sub-500kW
sites to stay below the SEE threshold at each location.

**Severity:** Medium. Splitting a 5MW workload across 10 sites of 500kW
each is operationally expensive (redundant networking, cooling, staffing,
latency penalties). It is economically rational only if the SEE liability
at 5MW (£0.20/kWh on approximately 40 GWh/year = £8M) exceeds the cost
premium of distributed operation. For most workloads, it does not.

**Enforcement:**

- **Aggregated metering.** SEE liability is assessed on the
  consolidated energy consumption of all facilities under common
  ownership or control, not per-site. This is the same principle as
  group relief in corporation tax: related entities cannot claim
  independent treatment to exploit thresholds.
- **Beneficial ownership register.** Facilities must declare their
  ultimate beneficial owner. Shell structures that obscure common
  ownership for the purpose of threshold avoidance constitute tax
  evasion under existing law (Taxes Management Act 1970, as amended).
- **Anti-fragmentation rule.** Where two or more facilities under
  common control collectively exceed 500kW and are located within the
  same network region (BGP autonomous system or shared power
  distribution), they are treated as a single facility for SEE purposes.

### 3.2 Off-Grid Generation (Dark Compute)

**Threat:** An operator installs private generation (solar, diesel, small
modular reactor) and runs compute without connecting to the metered grid.

**Severity:** High for large-scale operations; negligible for small.
Building a 10MW private power plant is a major capital project that
requires planning permission, environmental assessment and grid
connection agreements even if the operator does not draw grid power. It
is not covert.

**Enforcement:**

- **Three-point HRoT metering.** The Hardware Root of Trust metering
  architecture (PoG, PoS, PoL) is designed for this vector. Every
  energy source entering a commercial facility, including on-site
  generation, is metered at Point of Generation. The SEE liability is
  calculated from actual consumption (PoL), reconciled against
  generation (PoG) and storage (PoS). The formula:

  ```
  SEE Liability = PoL - (PoS_final - PoS_initial) x RTE_allowance
  ```

  Where RTE (Round-Trip Efficiency) allowance = 5% variance for battery
  losses.

- **Mandatory metering for all commercial generation.** Any commercial
  premises generating electricity above 100kW (regardless of whether it
  exports to grid) must install HRoT metering. This is enforced through
  existing planning and building regulations: generation equipment
  requires installation certification, and HRoT metering becomes a
  condition of that certification.

- **Reconciliation audits.** Discrepancy between a facility's declared
  IT load and its metered energy consumption triggers automatic audit.
  A facility declaring 400kW IT load but consuming 2MW has 1.6MW
  unaccounted for. The audit determines whether the discrepancy is
  legitimate (cooling, lighting, ancillary systems) or evasion.

### 3.3 Temporal Arbitrage (Storage Gaming)

**Threat:** An operator charges batteries during low-demand periods
(when metering or pricing is lower) and discharges during high-demand
compute operations, attempting to reduce the metered consumption
attributed to peak activity.

**Severity:** Low under SEBE's current design. SEE taxes total energy
consumption, not peak demand. Temporal arbitrage reduces grid demand
charges (an existing commercial concern) but does not reduce SEE
liability because PoS metering tracks all energy through storage. The
kilowatt-hours consumed are the same regardless of when they were
generated or stored.

**Enforcement:**

- **PoS (Point of Storage) metering.** All battery systems in SEE-liable
  facilities are metered bidirectionally. Energy entering storage is
  logged. Energy leaving storage is logged. The difference (accounting
  for RTE losses) must reconcile with PoL consumption.

### 3.4 Efficiency as Evasion

**Threat:** An operator invests in extreme energy efficiency (advanced
cooling, purpose-built ASICs, optimised software) to reduce energy
consumption per unit of economic output, thereby reducing SEE liability
while maintaining or increasing revenue.

**Severity:** Not a threat. This is the intended behaviour. SEE
deliberately rewards efficiency. A company that produces the same
economic output with half the energy pays half the SEE. This incentivises
exactly the kind of engineering innovation that reduces the environmental
footprint of automation. The revenue model accounts for this: aggregate
energy consumption still grows because the total volume of automation
grows faster than per-unit efficiency improves (Jevons paradox at the
sector level).

### 3.5 Distributed Residential Compute

**Threat:** An operator distributes workloads across many residential
endpoints (employee homes, gig-economy compute providers, peer-to-peer
networks) to avoid the 500kW facility threshold entirely.

**Severity:** Low for enterprise workloads; moderate for specific use
cases. Enterprise operations require SLAs, uptime guarantees, hardware
security modules and data sovereignty compliance that residential
environments cannot provide. A bank cannot run its trading engine across
200 home broadband connections. A hospital cannot process patient data on
unvetted domestic hardware.

The threat is real for workloads without these constraints: distributed
AI training, cryptocurrency mining, certain scientific computing tasks.

**Enforcement:**

- **Smart meter load profiling.** UK smart meters report half-hourly
  consumption data. Residential power consumption follows a diurnal
  pattern (peaks morning and evening, low overnight). A residential
  connection running sustained flat-baseload compute generates a
  distinct consumption profile: continuous, non-cyclical, with minimal
  diurnal variation. This signature is detectable without inspecting
  what the electricity is being used for.

- **Commercial reclassification.** When a residential meter exhibits a
  sustained commercial-pattern baseload (defined as continuous
  consumption above a threshold, provisionally 2kW sustained average
  over 30 days, with a variance coefficient below 0.15), the supply is
  automatically reclassified for commercial tariff assessment. The
  occupant is notified and given 30 days to demonstrate that the
  consumption is domestic (electric vehicle charging, electric heating,
  home workshop). If the consumption is commercial compute, SEE applies.

- **De minimis acceptance.** A single residential node running a GPU
  for hobbyist ML training consumes perhaps 500W sustained. At domestic
  electricity prices this costs the operator more than any SEE liability
  would. The enforcement system does not target hobbyists. It targets
  organised distributed compute operations where hundreds of nodes are
  coordinated by a commercial entity.

### 3.6 The SLA and Compliance Barrier (Passive Control)

This is not an active enforcement mechanism. It is a structural reality
that limits the scope of evasion without any state action.

Major commercial operations are bound by:

- **Service Level Agreements (SLAs):** contractual uptime, latency and
  throughput guarantees that cannot be met on residential infrastructure
- **Hardware Security Modules (HSMs):** cryptographic key management
  required for financial services, healthcare and government contracts
- **Data sovereignty and GDPR compliance:** legal requirements for data
  residency, processing location and audit trails
- **Insurance and liability:** professional indemnity insurers require
  auditable, certified infrastructure
- **Regulatory obligations:** Financial Conduct Authority (FCA), Care
  Quality Commission (CQC), Information Commissioner's Office (ICO) and
  sector-specific regulators mandate specific infrastructure standards

The combined effect is that the vast majority of commercial compute
(by revenue value) is structurally locked into data centres and
dedicated facilities that fall within SEE metering. The entities that
can operate outside this envelope are, by definition, operating at a
scale too small to affect the revenue base materially.

---

## 4. DCD Evasion Vectors

### 4.1 Compute Offshoring (the Primary DCD Target)

**Threat:** UK businesses route compute workloads to offshore data
centres (AWS Ireland, Azure Netherlands, GCP Belgium) to avoid SEE on
domestic energy consumption.

**Severity:** This is the scenario DCD exists to address. It is not
evasion; it is the primary taxable activity.

**Enforcement:**

- **IXP-level metering.** DCD is assessed at Internet Exchange Points
  (LINX, LONAP, etc.) and at submarine cable landing stations where
  commercial traffic crosses the UK digital border.
- **BGP Community Tagging.** Tier-1 ISPs tag traffic with BGP community
  attributes identifying the originating autonomous system. Commercial
  AS numbers are mapped to registered entities.
- **SNI-based classification.** The Server Name Indication field in TLS
  handshakes reveals the destination hostname (e.g. `api.openai.com`,
  `eu-west-1.compute.amazonaws.com`). This distinguishes commercial API
  traffic from personal browsing without inspecting payload content.
  ECH (Encrypted Client Hello) adoption is addressed in Section 4.4.
- **Tiered DCD rates.** Rates scale with border traffic volume
  (£200/TB below 10 PB/year, £400/TB for 10-100 PB, £800/TB above
  100 PB), ensuring that hyperscaler-equivalent offshore operations
  face DCD rates that exceed the SEE they would pay domestically.

Full rate derivation and SEE-equivalence analysis in `revenue_model.md`
Section 4.2.

### 4.2 Encrypted Tunnel Evasion

**Threat:** A corporation routes commercial cross-border traffic through
an encrypted tunnel (WireGuard, IPsec, or similar VPN) over an
unclassified broadband connection. The traffic appears as a single
encrypted stream. It does not transit identifiable commercial peering
links and is invisible to IXP-level DCD metering. BGP tagging identifies
the ISP's AS, not the corporate endpoint. SNI is hidden inside the
tunnel.

**Severity:** High. This is the most challenging DCD evasion vector. It
exploits the gap between IXP-level enforcement (which sees aggregate ISP
traffic) and the actual commercial entity generating it.

**Enforcement (three layers):**

**Layer 1: Compliance obligation (primary).**

Every UK business using offshore compute services must register its
cross-border data flows with HMRC's Digital Customs Division. This
includes cloud provider contracts, API subscriptions and any regular
data transfer to non-UK endpoints. Failure to register is tax evasion,
subject to the same penalties as failure to declare income.

This flips the enforcement burden. The state does not need to detect
every tunnel. The business must declare its traffic. The detection
mechanisms below serve as audit tools, not primary enforcement.

**Layer 2: ISP egress flow analysis (audit).**

ISPs are required to report aggregate flow metadata on traffic crossing
international links. This operates at the ISP's international peering
and transit egress points (not at the residential BNG, and not on
individual household connections).

The analysis uses IPFIX/NetFlow data to identify flow signatures
characteristic of commercial automation:

- **Sustained symmetric flows.** Human browsing is asymmetric (small
  requests, large responses). Commercial compute traffic (API calls,
  database synchronisation, distributed consensus) generates sustained
  bidirectional flows with near-symmetric packet rates.
- **Machine-timed packet intervals.** Human-driven traffic has variable
  inter-packet timing reflecting reading, typing and decision-making.
  Automated traffic exhibits regular, sub-millisecond intervals
  characteristic of programmatic operation.
- **Connection persistence.** Commercial tunnels maintain long-lived
  connections (hours to days). Human browsing generates many short-lived
  connections to diverse endpoints.
- **Volume-to-endpoint ratio.** A residential connection sending 500GB
  to a single offshore IP address in a month is not someone watching
  Netflix.

When flow analysis at ISP egress identifies traffic patterns consistent
with undeclared commercial compute, the ISP flags the source IP range
for investigation. HMRC's Digital Customs Division cross-references
against the compliance register. Registered traffic is reconciled
against declared volumes. Unregistered traffic triggers an audit of
the account holder.

This operates on aggregate ISP egress flows, not individual household
connections. The ISP reports flow statistics; HMRC investigates
discrepancies. No residential traffic is inspected, shaped or degraded.

**Layer 3: Financial and contractual audit (existing powers).**

HMRC already has powers to audit business expenditure. A company
paying AWS or Azure thousands of pounds per month for offshore compute
has an auditable financial trail. The DCD assessment can be derived from
cloud provider invoices (which detail data transfer volumes) as easily
as from network metering. Companies that route traffic through tunnels
to avoid DCD still receive invoices from their cloud providers. The
financial audit trail catches what the network audit misses.

### 4.3 CDN and Edge Caching

**Threat:** An operator uses a Content Delivery Network (CDN) with UK
edge nodes to cache content domestically, reducing cross-border data
transfer and therefore DCD liability.

**Severity:** Not a threat for the same reason as efficiency in SEE
(Section 3.4). CDN caching that reduces cross-border traffic is the
intended behaviour. DCD incentivises compute repatriation. A CDN edge
node in London serving cached content to UK users is domestic
infrastructure paying SEE on its energy consumption rather than
cross-border traffic paying DCD. The revenue shifts from DCD to SEE,
which is the policy objective.

If the CDN merely caches static content while the underlying compute
(inference, processing, database queries) remains offshore, the dynamic
API traffic still crosses the border and pays DCD. Only static asset
delivery is cached; the commercial logic generating those assets is not.

### 4.4 ECH (Encrypted Client Hello) and SNI Obfuscation

**Threat:** Encrypted Client Hello (ECH) is a TLS 1.3 extension that
encrypts the SNI field, preventing intermediaries from seeing the
destination hostname. As ECH adoption grows, SNI-based traffic
classification becomes less effective.

**Severity:** Medium-term concern. ECH is not yet widely deployed
(as of early 2026, support is limited to Cloudflare and Firefox in
specific configurations). Deployment will grow. The enforcement response
must not depend on SNI alone.

**Enforcement:**

- **BGP routing remains visible.** ECH encrypts the hostname, not the
  destination IP address or the BGP route. Traffic to
  `52.95.100.0/24` (an AWS Ireland prefix) is identifiable from BGP
  regardless of whether the SNI is encrypted. IP-to-operator mapping
  databases (maintained by Regional Internet Registries) provide the
  commercial entity.
- **Volume-based classification.** At scale, the distinction between
  commercial and personal traffic is a volume question. A single
  endpoint transferring 10TB per month to AWS prefixes is commercial
  regardless of what the SNI says.
- **Compliance obligation takes priority.** Per Section 4.2 Layer 1,
  businesses must declare their offshore compute usage. SNI analysis is
  one audit tool among several; its degradation does not undermine the
  primary enforcement mechanism.

### 4.5 Traffic Laundering (Third-Country Relay)

**Threat:** An operator routes traffic through a third country to
obscure the origin or destination. UK traffic goes to a relay in
France, which forwards it to a US data centre. The UK border crossing
appears to be UK-France (potentially within a future EU coordination
framework), not UK-US.

**Severity:** Low for most operators; moderate for sophisticated actors.
The relay adds latency (20-40ms per hop), which degrades performance for
latency-sensitive workloads (trading, real-time inference). It also adds
cost (the relay infrastructure must be paid for). For bulk data
processing where latency is immaterial, it is a viable vector.

**Enforcement:**

- **Traceroute and hop analysis.** The network path is visible even
  through encrypted tunnels (TTL-based traceroute reveals intermediate
  hops). A flow from London to Paris that then appears in Virginia has
  a traceable path.
- **Bilateral agreements.** DCD enforcement benefits from international
  coordination. A bilateral agreement with France (or an EU-wide
  framework) could require relay operators to report transit traffic
  volumes, or apply equivalent duties.
- **Financial audit.** The operator pays the relay provider and the
  ultimate compute provider. Both are auditable.

### 4.6 Satellite and Non-Terrestrial Networks

**Threat:** An operator uses satellite internet (Starlink, OneWeb) to
bypass terrestrial IXP metering entirely, routing commercial traffic
through space-based infrastructure that does not pass through UK
submarine cable landing stations.

**Severity:** Low at present; increasing over time. Current satellite
bandwidth is limited (Starlink residential plans offer 50-250 Mbps,
with business plans up to 500 Mbps) and expensive relative to
terrestrial fibre. For a commercial operation requiring terabits of
sustained throughput, satellite is not viable.

As satellite capacity grows (LEO constellations scaling to multi-Tbps
aggregate), this becomes a credible vector for medium-scale operations.

**Enforcement:**

- **Satellite provider licensing.** Operators providing satellite
  internet access to UK ground stations must be licensed by Ofcom.
  Licensing conditions can require the same flow reporting obligations
  as terrestrial ISPs, including IPFIX metadata on international
  traffic.
- **Ground station metering.** Satellite ground stations are physical
  infrastructure. Traffic passing through UK ground stations (whether
  uplink or downlink) can be metered at the ground station, which
  serves the same function as a submarine cable landing station for DCD
  purposes.
- **Regulatory parity.** The principle is that any path carrying
  commercial data across the UK digital border, whether fibre, microwave
  or satellite, is subject to the same DCD obligations. The medium is
  irrelevant; the border crossing is what triggers the duty.

---

## 5. Enforcement Architecture

### 5.1 The Layered Model

SEBE enforcement operates in four layers, from structural to active:

| Layer | Mechanism | Target | Action |
|---|---|---|---|
| 1. Structural | SLA/compliance/insurance barriers | Large enterprises | No state action required |
| 2. Physical | HRoT metering (SEE), IXP metering (DCD) | All liable entities | Automated billing |
| 3. Compliance | Registration, declaration, financial audit | All liable entities | HMRC assessment |
| 4. Detection | Flow analysis, load profiling, reconciliation | Evasion suspects | Audit and investigation |

Layer 1 catches the majority of revenue (large enterprises cannot
operate outside auditable infrastructure). Layer 2 is the primary
collection mechanism. Layer 3 is the legal framework. Layer 4 is the
audit function that catches deliberate evasion.

### 5.2 Institutional Requirements

**National Telemetry Agency (NTA).** A new body responsible for:
- HRoT meter certification and deployment
- Meter data collection, reconciliation and anomaly detection
- Technical standards for metering hardware
- Coordination with Ofgem (energy) and Ofcom (communications)

**Digital Customs Division (DCD-D).** A division within HMRC responsible
for:
- DCD assessment and collection
- Commercial cross-border traffic registration
- ISP flow reporting oversight
- Audit and investigation of suspected DCD evasion
- Coordination with international counterparts

**Staffing estimate:** 5,000-10,000 civil servants across NTA and DCD-D.
For comparison, HMRC employs approximately 65,000 staff to administer a
far more complex tax system.

### 5.3 Tiered Penalties

| Tier | Behaviour | Response |
|---|---|---|
| 1. Discrepancy | Metering variance <10% | Administrative correction, no penalty |
| 2. Non-compliance | Failure to register, late declaration | Fines (percentage of assessed liability) |
| 3. Systematic evasion | HRoT tampering, undeclared commercial compute | Criminal investigation, asset seizure |
| 4. Capital flight | Relocation to avoid SEBE | Exit tax on realised gains, DCD on offshore operations |

The tiered structure ensures proportionate response. Most compliance
failures are administrative, not criminal. Criminal enforcement is
reserved for deliberate fraud (meter tampering, organised tunnel
evasion at scale).

---

## 6. Accepted Leakage

No tax system achieves 100% compliance. HMRC estimates the UK tax gap
at 4.8% (2021-22). SEBE's physical measurement base should produce a
lower gap than taxes dependent on self-declaration, but some leakage is
inevitable.

**Accepted leakage categories:**

- Sub-threshold operations (below 500kW, below DCD volume floors)
- Hobbyist and personal compute (not commercially motivated)
- Small-scale encrypted tunnel usage (detection cost exceeds revenue)
- Transitional period evasion (ramp-up years before full enforcement)

**Estimated revenue impact:** 3-7% of theoretical maximum, comparable
to or better than existing tax gap rates. At £38B mid-scenario launch
revenue, this represents £1-3B in leakage, which is factored into the
revenue model's sensitivity analysis (`revenue_model.md` Section 8).

---

## 7. Comparison to Existing Tax Enforcement

| Factor | Income Tax/CT | SEBE |
|---|---|---|
| Tax base | Declared income/profit | Physical consumption (kWh, TB) |
| Measurement | Self-declaration + audit | Hardware meters + audit |
| Primary evasion | Profit shifting, deductions | Threshold splitting, tunnelling |
| Evasion complexity | Moderate (accountants) | High (infrastructure engineering) |
| Cross-border enforcement | Weak (transfer pricing) | Strong (physical border metering) |
| Gaming potential | High (legal structures) | Low (physics is not negotiable) |

The key advantage of SEBE over existing taxes is that the primary
enforcement surface is physical, not legal. You can restructure a
company's declared profits with a filing. You cannot restructure the
kilowatt-hours consumed by a data centre without physically reducing
the workload.

---

## 8. Outstanding Questions

1. **HRoT specification.** The Sovereign Metering Standard requires
   detailed technical specification (hardware, cryptographic protocols,
   certification process). This is an engineering project, not a policy
   question, but it must precede deployment.

2. **ISP flow reporting framework.** The legal and technical framework
   for ISP egress flow reporting needs development. RIPA (Regulation of
   Investigatory Powers Act 2000) and IPA (Investigatory Powers Act
   2016) provide precedent for ISP obligations, but DCD flow reporting
   is fiscal, not intelligence, and the legal basis must reflect this.

3. **International coordination.** DCD effectiveness improves with
   bilateral or multilateral agreements. Unilateral enforcement works
   (the UK controls its own border infrastructure) but coordination
   with the EU, particularly Ireland and the Netherlands (major cloud
   hosting jurisdictions), strengthens the regime.

4. **ECH deployment timeline.** The pace of ECH adoption determines how
   quickly SNI-based classification degrades as an audit tool.
   Monitoring required; replacement mechanisms (BGP-based, volume-based)
   are already specified but need testing.

5. **Satellite capacity growth.** LEO constellation capacity projections
   should be monitored. Regulatory parity (Ofcom licensing conditions)
   should be established before satellite bandwidth reaches scales that
   threaten terrestrial DCD metering.

---

*Copyright 2026 Jason Huxley. Licensed under CC-BY 4.0.*
