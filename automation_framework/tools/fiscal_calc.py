"""
SEBE Fiscal Calculator

General-purpose fiscal arithmetic for the SEBE cost model.
LLMs are language models, not calculators. Use this tool to verify
any fiscal calculation before committing figures to documents.

Run from automation_framework/:

    # Full model summary with current defaults
    python -m tools.fiscal_calc

    # Tax burden on a specific income
    python -m tools.fiscal_calc --action tax --gross 45000

    # Distribution cost for a specific UBI/ULI rate
    python -m tools.fiscal_calc --action distribute --adult-rate 5000

    # What-if scenario: UBI at £10,000 with 2% population growth
    python -m tools.fiscal_calc --action distribute --adult-rate 10000 --pop-growth 2

    # Welfare offsets at a specific ULI rate
    python -m tools.fiscal_calc --action offsets --adult-rate 29000

    # SEBE coverage at a specific revenue estimate
    python -m tools.fiscal_calc --action coverage --sebe-revenue 350

    # Full model with all custom parameters
    python -m tools.fiscal_calc --action full --adult-rate 15000 --ubs-rate 3000

    # JSON output for piping to other tools
    python -m tools.fiscal_calc --action full --json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


# =====================================================================
# Tax parameters (HMRC 2025/26)
# =====================================================================

@dataclass
class TaxParams:
    """UK income tax and NI parameters."""
    personal_allowance: float = 12_570
    basic_rate: float = 0.20
    basic_band_upper: float = 50_270
    higher_rate: float = 0.40
    higher_band_upper: float = 125_140
    additional_rate: float = 0.45
    ni_threshold: float = 12_570
    ni_rate: float = 0.08
    ni_upper: float = 50_270
    ni_upper_rate: float = 0.02
    tax_year: str = "2025/26"


# =====================================================================
# Population parameters (ONS mid-2023)
# =====================================================================

@dataclass
class PopulationParams:
    """UK population breakdown."""
    adults: int = 55_000_000
    children_0_2: int = 2_000_000
    children_3_11: int = 6_000_000
    children_12_17: int = 4_000_000
    source: str = "ONS mid-2023"

    @property
    def total_children(self) -> int:
        return self.children_0_2 + self.children_3_11 + self.children_12_17

    @property
    def total(self) -> int:
        return self.adults + self.total_children

    def with_growth(self, pct: float) -> "PopulationParams":
        """Return new params with uniform population growth applied."""
        factor = 1 + pct / 100
        return PopulationParams(
            adults=int(self.adults * factor),
            children_0_2=int(self.children_0_2 * factor),
            children_3_11=int(self.children_3_11 * factor),
            children_12_17=int(self.children_12_17 * factor),
            source=f"{self.source} + {pct}% growth",
        )


# =====================================================================
# Distribution parameters
# =====================================================================

@dataclass
class DistributionParams:
    """UBI/ULI and UBS payment rates."""
    adult_rate: float = 2_500       # Stage 1 default
    child_0_2_rate: float = 5_000
    child_3_11_rate: float = 3_500
    child_12_17_rate: float = 4_000
    ubs_rate: float = 2_500


# =====================================================================
# UBS component breakdown
# =====================================================================

@dataclass
class UBSComponents:
    """Universal Basic Services component costs per person/year."""
    energy: float = 1_200
    transport: float = 280
    broadband: float = 330
    mobile: float = 200
    margin: float = 490

    @property
    def total(self) -> float:
        return self.energy + self.transport + self.broadband + self.mobile + self.margin


# =====================================================================
# Welfare offset parameters (OBR 2023-24)
# =====================================================================

@dataclass
class WelfareOffsets:
    """Existing benefit spending that UBI/ULI displaces."""
    state_pension: float = 125       # £B
    pension_credit: float = 5
    winter_fuel: float = 2
    uc_income_low: float = 40
    uc_income_high: float = 50
    housing_low: float = 20
    housing_high: float = 23
    child_benefit: float = 12.5
    maternity: float = 3
    cms: float = 0.5
    admin_low: float = 5
    admin_high: float = 7
    pip_total: float = 28
    # PIP condition weights (DWP Oct 2025)
    pip_psychiatric_pct: float = 0.39
    pip_musculo_pct: float = 0.31
    pip_neuro_pct: float = 0.13
    pip_resp_pct: float = 0.04
    pip_other_pct: float = 0.13
    # PIP offset estimates per condition
    pip_psych_offset_low: float = 0.60
    pip_psych_offset_high: float = 0.70
    pip_musculo_offset_low: float = 0.20
    pip_musculo_offset_high: float = 0.30
    pip_neuro_offset: float = 0.10
    pip_resp_offset: float = 0.10
    pip_other_offset: float = 0.20
    source: str = "OBR Nov 2023 EFO, DWP PIP Stats Oct 2025"


# =====================================================================
# Calculator functions
# =====================================================================

def calc_tax(gross: float, tax: Optional[TaxParams] = None) -> dict:
    """Calculate UK income tax and NI on a given gross income."""
    if tax is None:
        tax = TaxParams()

    # Income tax (simplified: doesn't handle PA taper above £100k)
    if gross <= tax.personal_allowance:
        income_tax = 0
    elif gross <= tax.basic_band_upper:
        income_tax = (gross - tax.personal_allowance) * tax.basic_rate
    elif gross <= tax.higher_band_upper:
        basic_tax = (tax.basic_band_upper - tax.personal_allowance) * tax.basic_rate
        higher_tax = (gross - tax.basic_band_upper) * tax.higher_rate
        income_tax = basic_tax + higher_tax
    else:
        basic_tax = (tax.basic_band_upper - tax.personal_allowance) * tax.basic_rate
        higher_tax = (tax.higher_band_upper - tax.basic_band_upper) * tax.higher_rate
        additional_tax = (gross - tax.higher_band_upper) * tax.additional_rate
        income_tax = basic_tax + higher_tax + additional_tax

    # Employee NI
    if gross <= tax.ni_threshold:
        employee_ni = 0
    elif gross <= tax.ni_upper:
        employee_ni = (gross - tax.ni_threshold) * tax.ni_rate
    else:
        lower_ni = (tax.ni_upper - tax.ni_threshold) * tax.ni_rate
        upper_ni = (gross - tax.ni_upper) * tax.ni_upper_rate
        employee_ni = lower_ni + upper_ni

    total_deductions = income_tax + employee_ni
    take_home = gross - total_deductions
    effective_rate = total_deductions / gross * 100 if gross > 0 else 0

    return {
        "gross": gross,
        "personal_allowance": tax.personal_allowance,
        "income_tax": round(income_tax, 2),
        "employee_ni": round(employee_ni, 2),
        "total_deductions": round(total_deductions, 2),
        "take_home": round(take_home, 2),
        "effective_rate_pct": round(effective_rate, 2),
        "tax_year": tax.tax_year,
    }


def calc_distribution(
    dist: Optional[DistributionParams] = None,
    pop: Optional[PopulationParams] = None,
) -> dict:
    """Calculate total distribution cost for given rates and population."""
    if dist is None:
        dist = DistributionParams()
    if pop is None:
        pop = PopulationParams()

    adult_cost = pop.adults * dist.adult_rate
    child_0_2_cost = pop.children_0_2 * dist.child_0_2_rate
    child_3_11_cost = pop.children_3_11 * dist.child_3_11_rate
    child_12_17_cost = pop.children_12_17 * dist.child_12_17_rate
    income_subtotal = adult_cost + child_0_2_cost + child_3_11_cost + child_12_17_cost

    ubs_cost = pop.total * dist.ubs_rate
    total = income_subtotal + ubs_cost

    return {
        "adult_rate": dist.adult_rate,
        "adults": pop.adults,
        "adult_cost_B": round(adult_cost / 1e9, 2),
        "child_0_2_rate": dist.child_0_2_rate,
        "child_0_2_cost_B": round(child_0_2_cost / 1e9, 2),
        "child_3_11_rate": dist.child_3_11_rate,
        "child_3_11_cost_B": round(child_3_11_cost / 1e9, 2),
        "child_12_17_rate": dist.child_12_17_rate,
        "child_12_17_cost_B": round(child_12_17_cost / 1e9, 2),
        "income_subtotal_B": round(income_subtotal / 1e9, 2),
        "ubs_rate": dist.ubs_rate,
        "ubs_pop": pop.total,
        "ubs_cost_B": round(ubs_cost / 1e9, 2),
        "total_B": round(total / 1e9, 2),
        "total_T": round(total / 1e12, 4),
        "population_source": pop.source,
    }


def calc_pip_offset(offsets: Optional[WelfareOffsets] = None) -> dict:
    """Calculate PIP/DLA offset using condition-weighted methodology."""
    if offsets is None:
        offsets = WelfareOffsets()

    weighted_low = (
        offsets.pip_psychiatric_pct * offsets.pip_psych_offset_low
        + offsets.pip_musculo_pct * offsets.pip_musculo_offset_low
        + offsets.pip_neuro_pct * offsets.pip_neuro_offset
        + offsets.pip_resp_pct * offsets.pip_resp_offset
        + offsets.pip_other_pct * offsets.pip_other_offset
    )
    weighted_high = (
        offsets.pip_psychiatric_pct * offsets.pip_psych_offset_high
        + offsets.pip_musculo_pct * offsets.pip_musculo_offset_high
        + offsets.pip_neuro_pct * offsets.pip_neuro_offset
        + offsets.pip_resp_pct * offsets.pip_resp_offset
        + offsets.pip_other_pct * offsets.pip_other_offset
    )

    return {
        "pip_total_B": offsets.pip_total,
        "weighted_offset_low_pct": round(weighted_low * 100, 1),
        "weighted_offset_high_pct": round(weighted_high * 100, 1),
        "offset_low_B": round(offsets.pip_total * weighted_low, 1),
        "offset_high_B": round(offsets.pip_total * weighted_high, 1),
    }


def calc_offsets(
    stage: int = 2,
    offsets: Optional[WelfareOffsets] = None,
) -> dict:
    """Calculate welfare offsets for Stage 1 or Stage 2."""
    if offsets is None:
        offsets = WelfareOffsets()

    pip = calc_pip_offset(offsets)

    if stage == 1:
        total_low = offsets.child_benefit + offsets.winter_fuel
        total_high = total_low
        items = {
            "child_benefit": offsets.child_benefit,
            "winter_fuel": offsets.winter_fuel,
        }
    else:
        total_low = (
            offsets.state_pension + offsets.pension_credit + offsets.winter_fuel
            + offsets.uc_income_low + offsets.housing_low + pip["offset_low_B"]
            + offsets.child_benefit + offsets.maternity + offsets.cms
            + offsets.admin_low
        )
        total_high = (
            offsets.state_pension + offsets.pension_credit + offsets.winter_fuel
            + offsets.uc_income_high + offsets.housing_high + pip["offset_high_B"]
            + offsets.child_benefit + offsets.maternity + offsets.cms
            + offsets.admin_high
        )
        items = {
            "state_pension": offsets.state_pension,
            "pension_credit": offsets.pension_credit,
            "winter_fuel": offsets.winter_fuel,
            "uc_income": f"{offsets.uc_income_low}-{offsets.uc_income_high}",
            "housing": f"{offsets.housing_low}-{offsets.housing_high}",
            "pip_dla": f"{pip['offset_low_B']}-{pip['offset_high_B']}",
            "child_benefit": offsets.child_benefit,
            "maternity": offsets.maternity,
            "cms": offsets.cms,
            "admin_savings": f"{offsets.admin_low}-{offsets.admin_high}",
        }

    return {
        "stage": stage,
        "items_B": items,
        "pip_detail": pip,
        "total_low_B": round(total_low, 1),
        "total_high_B": round(total_high, 1),
        "source": offsets.source,
    }


def calc_coverage(
    gross_cost_B: float,
    offset_low_B: float = 0,
    offset_high_B: float = 0,
    sebe_low_B: float = 200,
    sebe_high_B: float = 500,
) -> dict:
    """Calculate SEBE revenue coverage of net cost."""
    net_low = gross_cost_B - offset_high_B
    net_high = gross_cost_B - offset_low_B

    coverage_low_of_net_low = sebe_low_B / net_high * 100 if net_high > 0 else float("inf")
    coverage_high_of_net_low = sebe_high_B / net_high * 100 if net_high > 0 else float("inf")
    coverage_low_of_net_high = sebe_low_B / net_low * 100 if net_low > 0 else float("inf")
    coverage_high_of_net_high = sebe_high_B / net_low * 100 if net_low > 0 else float("inf")

    return {
        "gross_cost_B": gross_cost_B,
        "offset_low_B": offset_low_B,
        "offset_high_B": offset_high_B,
        "net_cost_low_B": round(net_low, 1),
        "net_cost_high_B": round(net_high, 1),
        "sebe_low_B": sebe_low_B,
        "sebe_high_B": sebe_high_B,
        "coverage_low_pct": round(coverage_low_of_net_low, 1),
        "coverage_high_pct": round(coverage_high_of_net_high, 1),
    }


def calc_uli_derivation(
    gross: float = 39_039,
    ubs_rate: float = 2_500,
    tax: Optional[TaxParams] = None,
) -> dict:
    """Derive ULI rate from median gross earnings."""
    t = calc_tax(gross, tax)
    uli_exact = t["take_home"] - ubs_rate
    uli_rounded = round(uli_exact / 1000) * 1000

    return {
        "median_gross": gross,
        "take_home": t["take_home"],
        "total_deductions": t["total_deductions"],
        "ubs_rate": ubs_rate,
        "uli_exact": round(uli_exact, 2),
        "uli_rounded": uli_rounded,
        "combined_living_standard": uli_rounded + ubs_rate,
    }


def full_model(
    adult_rate: float = 2_500,
    ubs_rate: float = 2_500,
    pop_growth: float = 0,
    sebe_low: float = 200,
    sebe_high: float = 500,
) -> dict:
    """Run the complete SEBE fiscal model with given parameters."""

    pop = PopulationParams()
    if pop_growth != 0:
        pop = pop.with_growth(pop_growth)

    dist = DistributionParams(adult_rate=adult_rate, ubs_rate=ubs_rate)
    distribution = calc_distribution(dist, pop)

    # Determine stage
    stage = 1 if adult_rate <= 10_000 else 2
    offsets = calc_offsets(stage=stage)

    coverage = calc_coverage(
        gross_cost_B=distribution["total_B"],
        offset_low_B=offsets["total_low_B"],
        offset_high_B=offsets["total_high_B"],
        sebe_low_B=sebe_low,
        sebe_high_B=sebe_high,
    )

    uli_derivation = calc_uli_derivation(ubs_rate=ubs_rate)
    ubs = UBSComponents()

    return {
        "parameters": {
            "adult_rate": adult_rate,
            "ubs_rate": ubs_rate,
            "pop_growth_pct": pop_growth,
            "sebe_range_B": f"{sebe_low}-{sebe_high}",
            "stage": stage,
        },
        "uli_derivation": uli_derivation,
        "ubs_components": {
            "energy": ubs.energy,
            "transport": ubs.transport,
            "broadband": ubs.broadband,
            "mobile": ubs.mobile,
            "margin": ubs.margin,
            "total": ubs.total,
            "check": "PASS" if ubs.total == ubs_rate else f"FAIL (components sum to {ubs.total}, rate is {ubs_rate})",
        },
        "distribution": distribution,
        "offsets": offsets,
        "coverage": coverage,
    }


# =====================================================================
# CLI
# =====================================================================

def format_currency(value: float, unit: str = "£") -> str:
    """Format a number as currency."""
    if abs(value) >= 1e12:
        return f"{unit}{value/1e12:.3f}T"
    elif abs(value) >= 1e9:
        return f"{unit}{value/1e9:.1f}B"
    else:
        return f"{unit}{value:,.2f}"


def print_tax(result: dict):
    print(f"Tax calculation ({result['tax_year']}):")
    print(f"  Gross income:        £{result['gross']:,.2f}")
    print(f"  Personal allowance:  £{result['personal_allowance']:,.2f}")
    print(f"  Income tax:          £{result['income_tax']:,.2f}")
    print(f"  Employee NI:         £{result['employee_ni']:,.2f}")
    print(f"  Total deductions:    £{result['total_deductions']:,.2f}")
    print(f"  Take-home pay:       £{result['take_home']:,.2f}")
    print(f"  Effective rate:      {result['effective_rate_pct']:.1f}%")


def print_distribution(result: dict):
    print(f"Distribution cost (adult rate: £{result['adult_rate']:,.0f}):")
    print(f"  Adults: {result['adults']:,.0f} x £{result['adult_rate']:,.0f} = £{result['adult_cost_B']}B")
    print(f"  Children 0-2:  {result['child_0_2_rate']:,.0f}/yr = £{result['child_0_2_cost_B']}B")
    print(f"  Children 3-11: {result['child_3_11_rate']:,.0f}/yr = £{result['child_3_11_cost_B']}B")
    print(f"  Children 12-17: {result['child_12_17_rate']:,.0f}/yr = £{result['child_12_17_cost_B']}B")
    print(f"  Income subtotal: £{result['income_subtotal_B']}B")
    print(f"  UBS: {result['ubs_pop']:,.0f} x £{result['ubs_rate']:,.0f} = £{result['ubs_cost_B']}B")
    print(f"  TOTAL: £{result['total_B']}B (£{result['total_T']}T)")
    print(f"  Population: {result['population_source']}")


def print_offsets(result: dict):
    print(f"Welfare offsets (Stage {result['stage']}):")
    for k, v in result["items_B"].items():
        label = k.replace("_", " ").title()
        print(f"  {label}: £{v}B")
    print(f"  TOTAL: £{result['total_low_B']}-{result['total_high_B']}B")
    if result["stage"] == 2:
        pip = result["pip_detail"]
        print(f"  PIP detail: {pip['weighted_offset_low_pct']}-{pip['weighted_offset_high_pct']}% "
              f"of £{pip['pip_total_B']}B = £{pip['offset_low_B']}-{pip['offset_high_B']}B")


def print_coverage(result: dict):
    print(f"SEBE coverage:")
    print(f"  Gross cost:   £{result['gross_cost_B']}B")
    print(f"  Offset range: £{result['offset_low_B']}-{result['offset_high_B']}B")
    print(f"  Net cost:     £{result['net_cost_low_B']}-{result['net_cost_high_B']}B")
    print(f"  SEBE revenue: £{result['sebe_low_B']}-{result['sebe_high_B']}B")
    print(f"  Coverage:     {result['coverage_low_pct']}-{result['coverage_high_pct']}%")


def print_full(result: dict):
    p = result["parameters"]
    print(f"SEBE Fiscal Model (Stage {p['stage']}, adult rate £{p['adult_rate']:,.0f})")
    print("=" * 60)

    uli = result["uli_derivation"]
    print(f"\nULI derivation (from ONS ASHE 2025 median):")
    print(f"  Median gross: £{uli['median_gross']:,.0f}")
    print(f"  Take-home:    £{uli['take_home']:,.2f}")
    print(f"  UBS value:    £{uli['ubs_rate']:,.0f}")
    print(f"  ULI (exact):  £{uli['uli_exact']:,.2f}")
    print(f"  ULI (rounded): £{uli['uli_rounded']:,.0f}")
    print(f"  Combined:     £{uli['combined_living_standard']:,.0f}")

    ubs = result["ubs_components"]
    print(f"\nUBS components: £{ubs['energy']} + £{ubs['transport']} + "
          f"£{ubs['broadband']} + £{ubs['mobile']} + £{ubs['margin']} "
          f"= £{ubs['total']} [{ubs['check']}]")

    print()
    print_distribution(result["distribution"])
    print()
    print_offsets(result["offsets"])
    print()
    print_coverage(result["coverage"])


def main():
    parser = argparse.ArgumentParser(
        description="SEBE Fiscal Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  tax         Calculate tax burden on a gross income
  distribute  Calculate distribution cost for a given adult rate
  offsets     Calculate welfare offsets (Stage 1 or 2)
  coverage    Calculate SEBE coverage of a given cost
  uli         Derive ULI from median earnings
  full        Run complete model (default)

Examples:
  python -m tools.fiscal_calc
  python -m tools.fiscal_calc --action tax --gross 45000
  python -m tools.fiscal_calc --action distribute --adult-rate 10000
  python -m tools.fiscal_calc --action full --adult-rate 29000
  python -m tools.fiscal_calc --action full --adult-rate 5000 --pop-growth 2 --json
        """,
    )
    parser.add_argument("--action", default="full",
                        choices=["tax", "distribute", "offsets", "coverage", "uli", "full"])
    parser.add_argument("--gross", type=float, default=39_039,
                        help="Gross income for tax calculation (default: 39039)")
    parser.add_argument("--adult-rate", type=float, default=2_500,
                        help="Adult UBI/ULI rate (default: 2500)")
    parser.add_argument("--ubs-rate", type=float, default=2_500,
                        help="UBS rate per person (default: 2500)")
    parser.add_argument("--pop-growth", type=float, default=0,
                        help="Population growth percentage (default: 0)")
    parser.add_argument("--sebe-low", type=float, default=31,
                        help="SEBE revenue low estimate in £B (default: 31)")
    parser.add_argument("--sebe-high", type=float, default=38,
                        help="SEBE revenue high estimate in £B (default: 38)")
    parser.add_argument("--stage", type=int, default=None,
                        help="Force stage 1 or 2 for offsets (default: auto)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--sebe-revenue", type=float, default=None,
                        help="Specific SEBE revenue for coverage calc (£B)")

    args = parser.parse_args()

    if args.action == "tax":
        result = calc_tax(args.gross)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_tax(result)

    elif args.action == "distribute":
        pop = PopulationParams()
        if args.pop_growth:
            pop = pop.with_growth(args.pop_growth)
        dist = DistributionParams(adult_rate=args.adult_rate, ubs_rate=args.ubs_rate)
        result = calc_distribution(dist, pop)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_distribution(result)

    elif args.action == "offsets":
        stage = args.stage or (1 if args.adult_rate <= 10_000 else 2)
        result = calc_offsets(stage=stage)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_offsets(result)

    elif args.action == "coverage":
        pop = PopulationParams()
        if args.pop_growth:
            pop = pop.with_growth(args.pop_growth)
        dist = DistributionParams(adult_rate=args.adult_rate, ubs_rate=args.ubs_rate)
        d = calc_distribution(dist, pop)
        stage = args.stage or (1 if args.adult_rate <= 10_000 else 2)
        o = calc_offsets(stage=stage)

        sebe_low = args.sebe_revenue or args.sebe_low
        sebe_high = args.sebe_revenue or args.sebe_high

        result = calc_coverage(
            gross_cost_B=d["total_B"],
            offset_low_B=o["total_low_B"],
            offset_high_B=o["total_high_B"],
            sebe_low_B=sebe_low,
            sebe_high_B=sebe_high,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_coverage(result)

    elif args.action == "uli":
        result = calc_uli_derivation(gross=args.gross, ubs_rate=args.ubs_rate)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"ULI derivation:")
            print(f"  Median gross: £{result['median_gross']:,.0f}")
            print(f"  Take-home:    £{result['take_home']:,.2f}")
            print(f"  UBS:          £{result['ubs_rate']:,.0f}")
            print(f"  ULI (exact):  £{result['uli_exact']:,.2f}")
            print(f"  ULI (rounded): £{result['uli_rounded']:,.0f}")
            print(f"  Combined:     £{result['combined_living_standard']:,.0f}")

    elif args.action == "full":
        result = full_model(
            adult_rate=args.adult_rate,
            ubs_rate=args.ubs_rate,
            pop_growth=args.pop_growth,
            sebe_low=args.sebe_low,
            sebe_high=args.sebe_high,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_full(result)


if __name__ == "__main__":
    main()
