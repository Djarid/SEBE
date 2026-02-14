# SEBE — Sovereign Energy & Bandwidth Excise

**A UK policy proposal to tax automation infrastructure and fund Universal Living Income.**

Author: Jason Huxley | Licence: [CC-BY 4.0](LICENCE) | Status: Active, targeting Green Party Autumn 2026 conference

---

## The Problem

The UK raises £420 billion/year from taxing workers' wages. As automation replaces jobs, that revenue disappears, but the need for public spending doesn't. The tax base is collapsing precisely when society is most productive.

## The Proposal

Tax the physical infrastructure of automation instead of human labour:

- **Sovereign Energy Excise (SEE):** £0.05-0.30/kWh on commercial facilities over 500kW IT load
- **Digital Customs Duty (DCD):** £25-50/Mbps sustained commercial bandwidth, with a 2x offshore penalty

**Estimated revenue: £200-500 billion/year**, comparable to Income Tax, larger than National Insurance or VAT.

## Two-Stage Distribution

| Stage | Payment | UBS | Total | Fundable From |
|---|---|---|---|---|
| Stage 1: UBI (immediate) | £2,500/adult/year | £2,500/person/year | £352B/year | **SEBE alone** |
| Stage 2: ULI (transition) | £29,000/adult/year | £2,500/person/year | £1.810T/year | SEBE + progressive taxation |

**Stage 1** is a universal supplement alongside existing benefits. Children receive age-banded supplements (£3,500-5,000/year based on actual costs). Fully fundable from SEBE revenue at midpoint estimates.

**Stage 2** matches the take-home pay of a median full-time earner (ONS ASHE 2025: £39,039 gross = ~£31,500 take-home). UBI ratchets toward ULI as automation grows and SEBE revenue increases.

**Universal Basic Services (UBS)** at £2,500/person/year: free energy, all public transport (bus and national rail), broadband, and mobile.

SEBE is the major component of a broader progressive tax package (alongside wealth tax, land value tax, and financial transaction tax), not the complete solution. Honest framing matters.

## Why It Works

- **You can't offshore a datacenter.** Physical infrastructure is immobile, unlike capital or people.
- **VPNs don't help.** ISPs see total throughput regardless of encryption.
- **Hardware Root of Trust metering** at point of generation, storage, and load prevents evasion.
- **Offshore compute taxed at 2x.** Cheaper to build in the UK than route around it.

## Documents

| Document | Audience | Link |
|---|---|---|
| Green Party Policy Submission | Policy Development Committee, Economy Working Group | [green_party_submission.md](docs/green_party_submission.md) |
| Academic/Think Tank Brief | IPPR, NEF, economics researchers | [academic_brief.md](docs/academic_brief.md) |
| Public Explainer | General public, media, campaign use | [public_explainer.md](docs/public_explainer.md) |
| Cost Model | Revenue, distribution, and transition working | [cost_model.md](docs/cost_model.md) |
| Glossary | Term definitions and technical context | [glossary.md](docs/glossary.md) |

## Repository Structure

```
docs/               Policy documents (three versions + cost model + glossary)
automation_framework/
  tools/            Memory system, git remote ops, PDF reader
  context/          Project and author context
  goals/            Campaign task definitions
  memory/           Session logs and persistent facts
```

The `automation_framework/` directory contains tooling for AI-assisted campaign management: persistent memory across sessions, task tracking, contact management, and git operations. See [AGENTS.md](AGENTS.md) for details.

## Attribution

This work has been in development since 2019. If you use, adapt, or build upon this framework, please credit the original author as required by the CC-BY 4.0 licence.

**Suggested citation:** Huxley, J. (2026). Sovereign Energy and Bandwidth Excise (SEBE): Infrastructure-Based Taxation for the Post-Employment Economy.

## Contact

Contributions, critique, and collaboration welcome. Open an issue or contact the author directly.

---

© 2026 Jason Huxley. Licensed under [CC-BY 4.0](LICENCE).
