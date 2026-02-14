"""
Tests for tools.fiscal_calc — UK fiscal policy calculator.

Comprehensive tests for dataclasses, tax calculations, distribution costs,
welfare offsets, SEBE coverage, and full model integration.
"""

import pytest
from tools.fiscal_calc import (
    TaxParams,
    PopulationParams,
    DistributionParams,
    UBSComponents,
    WelfareOffsets,
    calc_tax,
    calc_distribution,
    calc_pip_offset,
    calc_offsets,
    calc_coverage,
    calc_uli_derivation,
    full_model,
)


# ═══════════════════════════════════════════════════════════════════════════
# Dataclass Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestTaxParams:
    """Test TaxParams dataclass defaults and construction."""

    def test_defaults(self):
        """Verify default UK tax parameters (2025/26)."""
        tax = TaxParams()
        assert tax.personal_allowance == 12_570
        assert tax.basic_rate == 0.20
        assert tax.basic_band_upper == 50_270
        assert tax.higher_rate == 0.40
        assert tax.higher_band_upper == 125_140
        assert tax.additional_rate == 0.45
        assert tax.ni_threshold == 12_570
        assert tax.ni_rate == 0.08
        assert tax.ni_upper == 50_270
        assert tax.ni_upper_rate == 0.02
        assert tax.tax_year == "2025/26"


class TestPopulationParams:
    """Test PopulationParams dataclass and growth calculations."""

    def test_defaults(self):
        """Verify default UK population figures."""
        pop = PopulationParams()
        assert pop.adults == 55_000_000
        assert pop.children_0_2 == 2_000_000
        assert pop.children_3_11 == 6_000_000
        assert pop.children_12_17 == 4_000_000
        assert pop.source == "ONS mid-2023"

    def test_total_children(self):
        """Verify total_children property sums correctly."""
        pop = PopulationParams()
        assert pop.total_children == 12_000_000

    def test_total_population(self):
        """Verify total property includes adults and children."""
        pop = PopulationParams()
        assert pop.total == 67_000_000

    def test_with_growth_zero(self):
        """Zero growth returns same values."""
        pop = PopulationParams()
        grown = pop.with_growth(0)
        assert grown.adults == pop.adults
        assert grown.total_children == pop.total_children
        assert grown.source == "ONS mid-2023 + 0% growth"

    def test_with_growth_positive(self):
        """2% growth increases all figures by 2%."""
        pop = PopulationParams()
        grown = pop.with_growth(2)
        assert grown.adults == int(55_000_000 * 1.02)
        assert grown.children_0_2 == int(2_000_000 * 1.02)
        assert grown.children_3_11 == int(6_000_000 * 1.02)
        assert grown.children_12_17 == int(4_000_000 * 1.02)
        assert "2% growth" in grown.source

    def test_with_growth_negative(self):
        """Negative growth decreases population."""
        pop = PopulationParams()
        grown = pop.with_growth(-1.5)
        assert grown.adults < pop.adults
        assert grown.total < pop.total
        assert "-1.5% growth" in grown.source


class TestDistributionParams:
    """Test DistributionParams dataclass defaults."""

    def test_defaults(self):
        """Verify default Stage 1 payment rates."""
        dist = DistributionParams()
        assert dist.adult_rate == 2_500
        assert dist.child_0_2_rate == 5_000
        assert dist.child_3_11_rate == 3_500
        assert dist.child_12_17_rate == 4_000
        assert dist.ubs_rate == 2_500


class TestUBSComponents:
    """Test UBS component breakdown."""

    def test_defaults(self):
        """Verify UBS component costs."""
        ubs = UBSComponents()
        assert ubs.energy == 1_200
        assert ubs.transport == 280
        assert ubs.broadband == 330
        assert ubs.mobile == 200
        assert ubs.margin == 490

    def test_total_property(self):
        """Verify components sum to total."""
        ubs = UBSComponents()
        expected = 1_200 + 280 + 330 + 200 + 490
        assert ubs.total == expected
        assert ubs.total == 2_500


class TestWelfareOffsets:
    """Test WelfareOffsets dataclass defaults."""

    def test_defaults(self):
        """Verify default OBR welfare spending figures."""
        offsets = WelfareOffsets()
        assert offsets.state_pension == 125
        assert offsets.pension_credit == 5
        assert offsets.winter_fuel == 2
        assert offsets.child_benefit == 12.5
        assert offsets.pip_total == 28
        assert offsets.source == "OBR Nov 2023 EFO, DWP PIP Stats Oct 2025"


# ═══════════════════════════════════════════════════════════════════════════
# Tax Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalcTax:
    """Test UK income tax and NI calculations."""

    def test_zero_income(self):
        """Zero income results in zero tax and NI."""
        result = calc_tax(0)
        assert result["gross"] == 0
        assert result["income_tax"] == 0
        assert result["employee_ni"] == 0
        assert result["total_deductions"] == 0
        assert result["take_home"] == 0
        assert result["effective_rate_pct"] == 0

    def test_below_personal_allowance(self):
        """Income below PA incurs no income tax."""
        result = calc_tax(10_000)
        assert result["income_tax"] == 0
        assert result["employee_ni"] == 0
        assert result["take_home"] == 10_000

    def test_at_personal_allowance(self):
        """Income exactly at PA (£12,570) incurs no income tax."""
        result = calc_tax(12_570)
        assert result["income_tax"] == 0
        assert result["employee_ni"] == 0
        assert result["take_home"] == 12_570

    def test_basic_rate_only(self):
        """£25,000 income triggers basic rate tax and NI."""
        result = calc_tax(25_000)
        taxable = 25_000 - 12_570
        expected_tax = taxable * 0.20
        expected_ni = taxable * 0.08
        assert result["income_tax"] == pytest.approx(expected_tax, abs=0.01)
        assert result["employee_ni"] == pytest.approx(expected_ni, abs=0.01)
        assert result["take_home"] == pytest.approx(25_000 - expected_tax - expected_ni, abs=0.01)

    def test_median_earnings(self):
        """ONS ASHE 2025 median (£39,039)."""
        result = calc_tax(39_039)
        taxable = 39_039 - 12_570
        expected_tax = taxable * 0.20
        expected_ni = taxable * 0.08
        assert result["income_tax"] == pytest.approx(expected_tax, abs=0.01)
        assert result["take_home"] == pytest.approx(31_627.68, abs=2)

    def test_at_basic_rate_ceiling(self):
        """£50,270 is at the basic rate ceiling."""
        result = calc_tax(50_270)
        taxable = 50_270 - 12_570
        expected_tax = taxable * 0.20
        expected_ni = taxable * 0.08
        assert result["income_tax"] == pytest.approx(expected_tax, abs=0.01)
        assert result["employee_ni"] == pytest.approx(expected_ni, abs=0.01)

    def test_higher_rate_kicks_in(self):
        """£75,000 income triggers higher rate (40%)."""
        result = calc_tax(75_000)
        basic_tax = (50_270 - 12_570) * 0.20
        higher_tax = (75_000 - 50_270) * 0.40
        expected_tax = basic_tax + higher_tax
        ni_lower = (50_270 - 12_570) * 0.08
        ni_upper = (75_000 - 50_270) * 0.02
        expected_ni = ni_lower + ni_upper
        assert result["income_tax"] == pytest.approx(expected_tax, abs=0.01)
        assert result["employee_ni"] == pytest.approx(expected_ni, abs=0.01)

    def test_additional_rate_threshold(self):
        """£125,140 is the additional rate threshold (PA fully tapered)."""
        result = calc_tax(125_140)
        # Note: calc_tax doesn't implement PA taper, simplified model
        basic_tax = (50_270 - 12_570) * 0.20
        higher_tax = (125_140 - 50_270) * 0.40
        expected_tax = basic_tax + higher_tax
        assert result["income_tax"] == pytest.approx(expected_tax, abs=0.01)

    def test_additional_rate(self):
        """£150,000 income triggers additional rate (45%)."""
        result = calc_tax(150_000)
        basic_tax = (50_270 - 12_570) * 0.20
        higher_tax = (125_140 - 50_270) * 0.40
        additional_tax = (150_000 - 125_140) * 0.45
        expected_tax = basic_tax + higher_tax + additional_tax
        assert result["income_tax"] == pytest.approx(expected_tax, abs=0.01)

    def test_very_high_income(self):
        """£1,000,000 income calculation."""
        result = calc_tax(1_000_000)
        assert result["gross"] == 1_000_000
        assert result["income_tax"] > 400_000
        assert result["effective_rate_pct"] > 40

    def test_return_structure(self):
        """Verify return dict contains all expected keys."""
        result = calc_tax(30_000)
        required_keys = {
            "gross", "personal_allowance", "income_tax", "employee_ni",
            "total_deductions", "take_home", "effective_rate_pct", "tax_year"
        }
        assert set(result.keys()) == required_keys

    def test_custom_tax_params(self):
        """Can use custom tax parameters."""
        custom = TaxParams(personal_allowance=15_000)
        result = calc_tax(20_000, custom)
        assert result["personal_allowance"] == 15_000
        taxable = 20_000 - 15_000
        assert result["income_tax"] == pytest.approx(taxable * 0.20, abs=0.01)


# ═══════════════════════════════════════════════════════════════════════════
# Distribution Cost Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalcDistribution:
    """Test UBI/ULI distribution cost calculations."""

    def test_default_params_stage1(self):
        """Stage 1 defaults: £2,500 adult, £2,500 UBS."""
        result = calc_distribution()
        assert result["adult_rate"] == 2_500
        assert result["adults"] == 55_000_000
        assert result["adult_cost_B"] == pytest.approx(137.5, abs=0.1)
        assert result["ubs_rate"] == 2_500
        assert result["ubs_pop"] == 67_000_000
        assert result["ubs_cost_B"] == pytest.approx(167.5, abs=0.1)
        # Total = adults + children + UBS
        assert result["total_B"] > 300

    def test_custom_adult_rate(self):
        """Custom adult rate (Stage 2: £29,000)."""
        dist = DistributionParams(adult_rate=29_000)
        result = calc_distribution(dist)
        assert result["adult_rate"] == 29_000
        assert result["adult_cost_B"] == pytest.approx(1_595, abs=1)

    def test_children_supplements(self):
        """Verify children's supplements are calculated."""
        result = calc_distribution()
        assert result["child_0_2_rate"] == 5_000
        assert result["child_3_11_rate"] == 3_500
        assert result["child_12_17_rate"] == 4_000
        assert result["child_0_2_cost_B"] > 0
        assert result["child_3_11_cost_B"] > 0
        assert result["child_12_17_cost_B"] > 0

    def test_income_subtotal(self):
        """Income subtotal excludes UBS."""
        result = calc_distribution()
        expected_subtotal = (
            result["adult_cost_B"] + result["child_0_2_cost_B"]
            + result["child_3_11_cost_B"] + result["child_12_17_cost_B"]
        )
        assert result["income_subtotal_B"] == pytest.approx(expected_subtotal, abs=0.1)

    def test_population_growth(self):
        """2% population growth increases costs by ~2%."""
        base = calc_distribution()
        pop_grown = PopulationParams().with_growth(2)
        grown = calc_distribution(pop=pop_grown)
        assert grown["total_B"] > base["total_B"]
        growth_ratio = grown["total_B"] / base["total_B"]
        assert growth_ratio == pytest.approx(1.02, abs=0.001)

    def test_return_structure(self):
        """Verify return dict structure."""
        result = calc_distribution()
        required_keys = {
            "adult_rate", "adults", "adult_cost_B",
            "child_0_2_rate", "child_0_2_cost_B",
            "child_3_11_rate", "child_3_11_cost_B",
            "child_12_17_rate", "child_12_17_cost_B",
            "income_subtotal_B", "ubs_rate", "ubs_pop", "ubs_cost_B",
            "total_B", "total_T", "population_source"
        }
        assert required_keys.issubset(set(result.keys()))


# ═══════════════════════════════════════════════════════════════════════════
# Welfare Offset Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalcPipOffset:
    """Test PIP/DLA condition-weighted offset calculation."""

    def test_default_offsets(self):
        """Verify default PIP offset calculation."""
        result = calc_pip_offset()
        assert result["pip_total_B"] == 28
        assert result["weighted_offset_low_pct"] > 0
        assert result["weighted_offset_high_pct"] > result["weighted_offset_low_pct"]
        assert result["offset_low_B"] > 0
        assert result["offset_high_B"] > result["offset_low_B"]

    def test_weighted_calculation(self):
        """Verify condition weighting logic."""
        offsets = WelfareOffsets()
        result = calc_pip_offset(offsets)
        # Psychiatric 39% at 60-70% offset should be largest component
        assert offsets.pip_psychiatric_pct == 0.39
        weighted_low = result["weighted_offset_low_pct"]
        weighted_high = result["weighted_offset_high_pct"]
        assert 30 < weighted_low < 50
        assert 40 < weighted_high < 60


class TestCalcOffsets:
    """Test welfare offset calculations for Stage 1 and Stage 2."""

    def test_stage1_offsets(self):
        """Stage 1 offsets child benefit and winter fuel only."""
        result = calc_offsets(stage=1)
        assert result["stage"] == 1
        assert result["total_low_B"] == result["total_high_B"]  # Same in Stage 1
        expected = 12.5 + 2  # child benefit + winter fuel
        assert result["total_low_B"] == pytest.approx(expected, abs=0.1)
        assert "child_benefit" in result["items_B"]
        assert "winter_fuel" in result["items_B"]

    def test_stage2_offsets(self):
        """Stage 2 offsets are substantially larger."""
        result = calc_offsets(stage=2)
        assert result["stage"] == 2
        assert result["total_low_B"] > 200
        assert result["total_high_B"] > result["total_low_B"]
        # Verify key items present
        items = result["items_B"]
        assert "state_pension" in items
        assert "uc_income" in items
        assert "housing" in items
        assert "pip_dla" in items

    def test_stage2_includes_pip_detail(self):
        """Stage 2 includes PIP condition breakdown."""
        result = calc_offsets(stage=2)
        assert "pip_detail" in result
        pip = result["pip_detail"]
        assert "pip_total_B" in pip
        assert "weighted_offset_low_pct" in pip

    def test_range_values(self):
        """Stage 2 offsets have low/high ranges for uncertainty."""
        result = calc_offsets(stage=2)
        assert result["total_low_B"] < result["total_high_B"]
        # UC and housing have ranges
        assert "-" in result["items_B"]["uc_income"]
        assert "-" in result["items_B"]["housing"]


# ═══════════════════════════════════════════════════════════════════════════
# Coverage Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalcCoverage:
    """Test SEBE revenue coverage calculations."""

    def test_basic_coverage(self):
        """Basic coverage calculation with defaults."""
        result = calc_coverage(
            gross_cost_B=350,
            offset_low_B=10,
            offset_high_B=15,
            sebe_low_B=200,
            sebe_high_B=500,
        )
        assert result["gross_cost_B"] == 350
        assert result["net_cost_low_B"] == pytest.approx(335, abs=0.1)  # 350 - 15
        assert result["net_cost_high_B"] == pytest.approx(340, abs=0.1)  # 350 - 10
        assert result["coverage_low_pct"] > 0
        assert result["coverage_high_pct"] > result["coverage_low_pct"]

    def test_full_coverage(self):
        """SEBE revenue exceeds net cost."""
        result = calc_coverage(
            gross_cost_B=200,
            offset_low_B=50,
            offset_high_B=60,
            sebe_low_B=300,
            sebe_high_B=400,
        )
        assert result["coverage_low_pct"] > 100
        assert result["coverage_high_pct"] > 200

    def test_zero_sebe_revenue(self):
        """Zero SEBE revenue gives 0% coverage."""
        result = calc_coverage(
            gross_cost_B=100,
            offset_low_B=10,
            offset_high_B=10,
            sebe_low_B=0,
            sebe_high_B=0,
        )
        assert result["coverage_low_pct"] == 0
        assert result["coverage_high_pct"] == 0

    def test_return_structure(self):
        """Verify return dict keys."""
        result = calc_coverage(100, 10, 15, 50, 80)
        required_keys = {
            "gross_cost_B", "offset_low_B", "offset_high_B",
            "net_cost_low_B", "net_cost_high_B",
            "sebe_low_B", "sebe_high_B",
            "coverage_low_pct", "coverage_high_pct"
        }
        assert set(result.keys()) == required_keys


# ═══════════════════════════════════════════════════════════════════════════
# ULI Derivation Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalcUliDerivation:
    """Test ULI derivation from median earnings."""

    def test_default_derivation(self):
        """Default uses ONS ASHE 2025 median (£39,039)."""
        result = calc_uli_derivation()
        assert result["median_gross"] == 39_039
        assert result["ubs_rate"] == 2_500
        assert result["take_home"] == pytest.approx(31_627.68, abs=2)
        assert result["uli_exact"] == pytest.approx(29_127.68, abs=2)
        assert result["uli_rounded"] == 29_000  # Rounded to nearest £1k
        assert result["combined_living_standard"] == 31_500

    def test_custom_median(self):
        """Custom median gross earnings."""
        result = calc_uli_derivation(gross=50_000, ubs_rate=3_000)
        assert result["median_gross"] == 50_000
        assert result["ubs_rate"] == 3_000
        assert result["uli_rounded"] % 1000 == 0  # Rounded to nearest £1k

    def test_return_structure(self):
        """Verify return dict structure."""
        result = calc_uli_derivation()
        required_keys = {
            "median_gross", "take_home", "total_deductions", "ubs_rate",
            "uli_exact", "uli_rounded", "combined_living_standard"
        }
        assert set(result.keys()) == required_keys


# ═══════════════════════════════════════════════════════════════════════════
# Full Model Integration Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestFullModel:
    """Test complete SEBE fiscal model integration."""

    def test_default_stage1_model(self):
        """Default parameters run Stage 1 model."""
        result = full_model()
        assert result["parameters"]["stage"] == 1
        assert result["parameters"]["adult_rate"] == 2_500
        assert result["parameters"]["ubs_rate"] == 2_500
        assert "uli_derivation" in result
        assert "ubs_components" in result
        assert "distribution" in result
        assert "offsets" in result
        assert "coverage" in result

    def test_stage2_model(self):
        """Adult rate > £10,000 triggers Stage 2."""
        result = full_model(adult_rate=29_000)
        assert result["parameters"]["stage"] == 2
        assert result["offsets"]["stage"] == 2
        assert result["offsets"]["total_low_B"] > 200

    def test_custom_parameters(self):
        """Full model with custom parameters."""
        result = full_model(
            adult_rate=15_000,
            ubs_rate=3_000,
            pop_growth=2,
            sebe_low=300,
            sebe_high=600,
        )
        assert result["parameters"]["adult_rate"] == 15_000
        assert result["parameters"]["ubs_rate"] == 3_000
        assert result["parameters"]["pop_growth_pct"] == 2
        assert "300-600" in result["parameters"]["sebe_range_B"]

    def test_ubs_components_check(self):
        """UBS components validation."""
        result = full_model(ubs_rate=2_500)
        ubs = result["ubs_components"]
        assert ubs["total"] == 2_500
        assert "PASS" in ubs["check"]

    def test_ubs_components_mismatch(self):
        """UBS rate mismatch is flagged."""
        result = full_model(ubs_rate=3_000)
        ubs = result["ubs_components"]
        assert ubs["total"] == 2_500  # Components unchanged
        assert "FAIL" in ubs["check"]

    def test_population_growth_applied(self):
        """Population growth is applied throughout."""
        base = full_model(pop_growth=0)
        grown = full_model(pop_growth=2)
        assert grown["distribution"]["total_B"] > base["distribution"]["total_B"]

    def test_all_sections_present(self):
        """Verify all expected sections in full model output."""
        result = full_model()
        required_sections = {
            "parameters", "uli_derivation", "ubs_components",
            "distribution", "offsets", "coverage"
        }
        assert set(result.keys()) == required_sections
