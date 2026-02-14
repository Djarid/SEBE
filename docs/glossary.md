# SEBE Glossary

**Version:** 1.0
**Updated:** February 2026

Terms and definitions used across SEBE documentation. This glossary exists
because many of these terms carry assumptions that don't match how SEBE
uses them.

---

## A Note on "Robots"

When most people hear "robot" they picture a humanoid machine (Boston Dynamics,
science fiction, factory arms). In the context of SEBE, "robot" means any
automated system that displaces human labour: a rack of GPUs running medical
diagnostics, an AI model processing insurance claims, a warehouse management
system, or a cloud platform serving millions of API calls. The common factor
is that these systems consume **electricity** and **bandwidth**, and that
consumption is what SEBE taxes.

"Tax robots, fund people" is a useful shorthand. But the robots in question
are mostly invisible, running in datacenters, not walking around factories.

---

## Core Terms

**SEBE (Sovereign Energy & Bandwidth Excise)**
The overall tax framework. Two components (SEE and DCD) that tax the physical
infrastructure of automation rather than human labour.

**SEE (Sovereign Energy Excise)**
The energy component of SEBE. A tiered tax on commercial electricity
consumption for facilities exceeding 500kW IT load. Rates: £0.05-0.30/kWh
depending on consumption bracket.

**DCD (Digital Customs Duty)**
The bandwidth component of SEBE. A tax on sustained commercial data throughput,
implemented at Internet Exchange Points. Offshore compute is taxed at 2x the
domestic rate to incentivise UK datacenter investment. Rates: £25-50/Mbps
sustained.

**UBI (Universal Basic Income)**
Stage 1 of the SEBE distribution model. A tax-free, unconditional supplement
of £2,500/adult/year paid to every UK citizen alongside existing benefits.
Not a replacement for wages or welfare. Fully fundable from SEBE alone.

**ULI (Universal Living Income)**
Stage 2 of the SEBE distribution model. A tax-free stipend of £29,000/adult/year
paid unconditionally to every UK citizen. Set so that the combined value of
ULI plus UBS (£31,500) equals the effective take-home pay of the current
median full-time earner (ONS ASHE 2025: £39,039 gross). UBI ratchets toward
ULI as automation grows and SEBE revenue increases.

**UBS (Universal Basic Services)**
Free public services worth approximately £2,500/person/year: energy, all
public transport (bus and national rail, free at point of use), broadband,
and mobile. UBS value is factored into the ULI calculation so the combined
package matches median take-home pay.

---

## Technical Terms

**Automation**
Any system that performs work previously done by humans. This includes AI/ML
inference, robotic process automation, autonomous logistics, cloud computing
services, and industrial robotics. SEBE does not distinguish between "good"
and "bad" automation; it taxes the physical resources consumed.

**Datacenter**
A facility housing computing infrastructure. Datacenters are the primary
target of SEE because they concentrate massive electricity consumption in
measurable, immobile locations. They cannot be offshored without triggering
the DCD offshore penalty.

**Dark Compute**
Undeclared computing activity that attempts to evade SEBE. Prevented by
three-point HRoT metering reconciliation: if energy enters a facility (PoG),
it must be accounted for at storage (PoS) and load (PoL). Discrepancies
flag evasion.

**HRoT (Hardware Root of Trust)**
Tamper-resistant metering hardware installed at three points in the energy
supply chain. Provides cryptographically verifiable consumption data that
cannot be spoofed by software. The three measurement points:

- **PoG (Point of Generation):** Grid or private generation ingress
- **PoS (Point of Storage):** Battery systems (prevents temporal arbitrage)
- **PoL (Point of Load):** Actual consumption at the computing infrastructure

**Offshore Compute**
Computing performed outside the UK but serving the UK market. Taxed at 2x
the domestic DCD rate. This makes it cheaper for companies to build UK
datacenters than to route around the tax from abroad.

**Temporal Arbitrage**
Storing energy during low-rate periods and consuming it during high-rate
periods to reduce tax liability. Prevented by PoS (Point of Storage)
metering, which tracks energy through battery systems.

---

## Network Terms

**BGP (Border Gateway Protocol)**
The routing protocol that directs internet traffic between networks. BGP
Community Tagging at Tier-1 gateways identifies whether traffic originates
from or terminates at commercial entities, enabling DCD assessment.

**SNI (Server Name Indication)**
A TLS extension that reveals the destination hostname during connection
setup (before encryption begins). Used alongside BGP data to distinguish
commercial traffic from personal traffic for DCD purposes. Does not require
decrypting content.

**IXP (Internet Exchange Point)**
Physical locations where internet networks interconnect. DCD is implemented
at the IXP level, providing natural chokepoints for measuring commercial
bandwidth without intercepting individual communications.

**Role Margin Protocol**
A SEBE mechanism that assigns each company a baseline bandwidth quota based
on its SIC code (industry classification) and size. Throughput exceeding the
baseline is taxed as excess, on the basis that it represents automation
displacing labour beyond what is typical for that sector.

---

## Political and Economic Terms

**Post-Employment Economy**
The economic condition where automation has displaced enough human labour
that traditional employment can no longer serve as the primary mechanism
for income distribution. SEBE is designed for this transition.

**MMT (Modern Monetary Theory)**
A macroeconomic framework recognising that sovereign currency issuers are
constrained by inflation (productive capacity), not by revenue. Relevant
to SEBE because automation increases productive capacity, which expands
the fiscal space available to a sovereign government.

**Defence Ring-Fence**
An optional allocation of 20% of SEBE revenue (£40-100 billion/year) for
UK strategic defence autonomy. Reduces ULI slightly but funds complete
independence from alliance dependencies.

---

© 2026 Jason Huxley. Licensed under CC-BY 4.0.
