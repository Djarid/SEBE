# SEBE — Sovereign Energy & Bandwidth Excise

**A UK policy proposal to tax automation infrastructure and replace eroding employment-based tax revenue.**

Author: Jason Huxley | Licence: [CC-BY 4.0](LICENCE) | Status: Active, targeting Green Party Autumn 2026 conference

---

## The Problem

The UK raises £420 billion/year from taxing workers' wages. As automation replaces jobs, that revenue disappears, but the need for public spending doesn't. The tax base is collapsing precisely when society is most productive.

## The Proposal

Tax the physical infrastructure of automation instead of human labour:

- **Sovereign Energy Excise (SEE):** £0.08-0.45/kWh (tiered) on commercial facilities over 500kW IT load
- **Digital Customs Duty (DCD):** £200-800/TB tiered border tariff on commercial data crossing the UK digital border. Consumers exempt. Domestic traffic exempt.

**Revenue at launch: £31-38 billion/year**, comparable to Inheritance Tax + Stamp Duty + CCL + Tobacco combined. Self-scaling with automation: £93B by 2040, £159B by 2045.

## What The Revenue Is For

SEBE is a tax mechanism. Distribution of revenue is a political choice.

The same revenue could fund universal income, NI reductions, NHS expansion, deficit reduction, or a combination. An illustrative two-stage distribution model (UBI ramping to Universal Living Income) is provided in [`distribution_model.md`](docs/distribution_model.md).

SEBE is the major new revenue component of a broader progressive tax package, not the complete solution. Honest framing matters.

## Why It Works

- **You can't offshore a datacenter.** Physical infrastructure is immobile, unlike capital or people.
- **VPNs don't help.** ISPs see total throughput regardless of encryption.
- **Hardware Root of Trust metering** at point of generation, storage, and load prevents evasion.
- **Offshore compute taxed at 2x.** Cheaper to build in the UK than route around it.
- **Revenue grows automatically.** More automation = more energy + bandwidth = more tax.

## Documents

| Document | Audience | Link |
|---|---|---|
| Green Party Policy Submission | Policy Development Committee, Economy Working Group | [green_party_submission.md](docs/green_party_submission.md) |
| Academic/Think Tank Brief | IPPR, NEF, economics researchers | [academic_brief.md](docs/academic_brief.md) |
| Public Explainer | General public, media, campaign use | [public_explainer.md](docs/public_explainer.md) |
| Revenue Model | Source of truth for all SEBE revenue figures | [revenue_model.md](docs/revenue_model.md) |
| Cost Model | Revenue scale and economic context | [cost_model.md](docs/cost_model.md) |
| Distribution Model | Illustrative UBI/ULI/UBS workings | [distribution_model.md](docs/distribution_model.md) |
| Style Guide | Writing standards for SEBE documents | [style_guide.md](docs/style_guide.md) |
| Glossary | Term definitions and technical context | [glossary.md](docs/glossary.md) |

## Repository Structure

```
docs/               Policy documents, reference models, style guide, glossary
automation_framework/
  tools/            Memory system, git remote ops, fiscal calculator, PDF reader
  context/          Project and author context
  goals/            Campaign task definitions
  services/         Daemon orchestration (Podman pod)
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
