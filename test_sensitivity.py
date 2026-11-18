"""
Regression and Quality Assertion Test Suite for ICBAR 2026 Simulation (v1.1.0)
Validates:
1. Baseline reproducibility (R_res = 1.80%)
2. Exact boundary threshold condition (k=5, alpha=0.20, gamma=1.00 equals exactly 4.00% -> True)
3. Decoupling of risk threshold (meets_risk_threshold) and framework requirements (k>=10 failed for k=5)
4. Stress testing breach calculation (k=10, alpha=0.50, gamma=0.85 -> 4.25% breach)
5. Analytical critical boundary consistency (alpha_crit = tau * k / gamma)
"""

import sys
import os
import unittest
from decimal import Decimal

# Ensure open_repo is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from sensitivity_analysis import (
    SimulationConfig,
    calculate_risk,
    calculate_risk_decimal,
    meets_risk_threshold,
    evaluate_framework_requirements,
    calculate_critical_alpha,
)


class TestSensitivityAnalysis(unittest.TestCase):
    def setUp(self):
        self.config = SimulationConfig()

    def test_baseline_reproducibility(self):
        """Assertion 1: Default baseline must reproduce R_res = 1.80% exactly."""
        r = calculate_risk(self.config.k_base, self.config.alpha_base, self.config.gamma_base)
        self.assertAlmostEqual(r, 0.0180, places=4, msg="Baseline R_res must be 0.0180 (1.80%).")

        r_dec = calculate_risk_decimal(self.config.k_base, self.config.alpha_base, self.config.gamma_base)
        self.assertEqual(r_dec, Decimal("0.0180"), msg="Decimal baseline risk must be exactly 0.0180.")

        meets_thresh = meets_risk_threshold(self.config.k_base, self.config.alpha_base, self.config.gamma_base, self.config.tau_safe)
        self.assertTrue(meets_thresh, "Baseline must meet risk threshold <= 4.0%.")

        fw_status = evaluate_framework_requirements(self.config.k_base, True, True, True, True, self.config)
        self.assertEqual(fw_status, "passed", "Baseline with all verified controls must return 'passed'.")

    def test_exact_boundary_condition(self):
        """Assertion 2: Exactly 4.00% threshold must pass (k=5, alpha=0.20, gamma=1.00)."""
        # (1/5) * 0.20 * 1.00 = 0.0400 exactly
        meets_thresh = meets_risk_threshold(5, 0.20, 1.00, tau_safe=0.04)
        self.assertTrue(
            meets_thresh,
            "Edge case k=5, alpha=0.20, gamma=1.00 equals exactly 4.00% and must evaluate to True (fixed from v1.0.0)."
        )

    def test_decoupled_criteria_for_sub_k_cohort(self):
        """Assertion 3: k=5 yields 3.60% (numeric pass), but fails statutory framework requirement (k >= 10)."""
        k = 5
        alpha = 0.25
        gamma = 0.72
        r = calculate_risk(k, alpha, gamma)
        self.assertAlmostEqual(r, 0.0360, places=4, msg="k=5 risk must be 0.0360 (3.60%).")

        # Numeric check: 3.60% <= 4.00% -> True
        meets_thresh = meets_risk_threshold(k, alpha, gamma, tau_safe=0.04)
        self.assertTrue(meets_thresh, "Numeric risk 3.60% is <= 4.00% and must pass.")

        # Framework check: k=5 < 10 -> MUST fail framework requirements
        fw_status = evaluate_framework_requirements(k, True, True, True, True, self.config)
        self.assertEqual(
            fw_status,
            "failed",
            "Framework requirements status must be 'failed' because k=5 violates k_min >= 10."
        )

        # Unassessed qualitative controls
        fw_unassessed = evaluate_framework_requirements(10, None, None, None, None, self.config)
        self.assertEqual(
            fw_unassessed,
            "not_assessed",
            "Framework requirements without qualitative check data must return 'not_assessed'."
        )

    def test_stress_testing_breach(self):
        """Assertion 4: Dual stress test (k=10, alpha=0.50, gamma=0.85) yields 4.25% and reports breach."""
        k = 10
        alpha = 0.50
        gamma = 0.85
        r = calculate_risk(k, alpha, gamma)
        self.assertAlmostEqual(r, 0.0425, places=4, msg="Dual stress risk must be 4.25%.")

        meets_thresh = meets_risk_threshold(k, alpha, gamma, tau_safe=0.04)
        self.assertFalse(meets_thresh, "Dual stress risk 4.25% must breach the 4.0% threshold.")

        alpha_crit = calculate_critical_alpha(k, gamma, tau_safe=0.04)
        # alpha_crit = (0.04 * 10) / 0.85 = 0.40 / 0.85 ≈ 0.4706
        self.assertAlmostEqual(alpha_crit, 0.470588, places=4)
        margin = alpha_crit - alpha
        self.assertLess(margin, 0, "Safety margin must be negative under breach.")

    def test_grid_size_and_critical_alpha(self):
        """Assertion 5: Grid points and analytical threshold equation."""
        total_grid = len(self.config.k_vals) * len(self.config.alpha_vals) * len(self.config.gamma_vals)
        self.assertEqual(total_grid, 315, "Sensitivity grid must maintain 315 points.")

        # Analytical threshold check: at alpha_crit, risk equals tau_safe exactly
        alpha_crit = calculate_critical_alpha(10, 0.72, 0.04)
        r_at_crit = calculate_risk(10, alpha_crit, 0.72)
        self.assertAlmostEqual(r_at_crit, 0.04, places=6)


if __name__ == "__main__":
    unittest.main()
