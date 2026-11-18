"""
Reproducible Parameter Sensitivity Analysis & Monte Carlo Risk Simulation
for ICBAR 2026: Scenario-Risk Safe Harbor under China's PIPL
Version: v1.1.0 (Refined with precision boundary check, decoupled legal criteria, and stress testing)
Repository: https://github.com/jhuang-edu/icbar-2026-safe-harbor-simulation
License: MIT License
"""

import os
import csv
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import matplotlib.pyplot as plt

# Output directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)


@dataclass
class SimulationConfig:
    """Centralized configuration for baseline values, grids, distributions, and seeds."""
    # Research baseline prior hypotheses
    k_base: int = 10
    alpha_base: float = 0.25
    gamma_base: float = 0.72
    tau_safe: float = 0.04
    k_min_threshold: int = 10  # Statutory baseline requirement per Table 2

    # Random generation settings
    random_seed: int = 42
    n_simulations: int = 10000
    distribution_type: str = "clipped_normal"  # Options: 'clipped_normal' or 'truncated_normal'

    # Multi-parameter sensitivity grid bounds
    k_vals: list = field(default_factory=lambda: [4, 5, 8, 10, 12, 15, 20])
    alpha_vals: list = field(default_factory=lambda: [0.15, 0.20, 0.25, 0.35, 0.50, 0.55, 0.60, 0.75, 1.00])
    gamma_vals: list = field(default_factory=lambda: [0.50, 0.60, 0.72, 0.85, 1.00])


def calculate_risk(k_min, alpha_env, gamma_org):
    """Calculates composite residual risk R_res = (1 / k_min) * alpha_env * gamma_org."""
    return (1.0 / float(k_min)) * float(alpha_env) * float(gamma_org)


def calculate_risk_decimal(k_min, alpha_env, gamma_org):
    """Exact decimal calculation for residual risk to eliminate binary floating-point roundoff errors."""
    d_k = Decimal(str(k_min))
    d_alpha = Decimal(str(alpha_env))
    d_gamma = Decimal(str(gamma_org))
    return (d_alpha * d_gamma) / d_k


def meets_risk_threshold(k_min, alpha_env, gamma_org, tau_safe=0.04):
    """
    Evaluates pure numeric threshold: alpha * gamma <= tau * k using exact Decimal comparison.
    Eliminates IEEE 754 precision artifacts (e.g. k=5, alpha=0.20, gamma=1.00 equals exactly 0.04).
    """
    d_k = Decimal(str(k_min))
    d_alpha = Decimal(str(alpha_env))
    d_gamma = Decimal(str(gamma_org))
    d_tau = Decimal(str(tau_safe))
    return (d_alpha * d_gamma) <= (d_tau * d_k)


def meets_minimum_k(k_min, threshold=10):
    """Evaluates whether equivalence class size satisfies Element 1 baseline threshold (k_min >= 10)."""
    return int(k_min) >= int(threshold)


def evaluate_framework_requirements(k_min, has_l_diversity=None, has_sandbox=None, has_covenants=None, has_pia_irb=None, config=None):
    """
    Decoupled legal governance criteria evaluation per Table 2:
    - Fails if k_min < k_min_threshold (k >= 10 is mandatory for safe harbor).
    - If qualitative controls (l-diversity, zero-egress sandbox, cascade covenants, PIA/IRB) are not specified, returns 'not_assessed'.
    - If all required controls are verified, returns 'passed'.
    - If any required control explicitly fails, returns 'failed'.
    """
    k_min_req = config.k_min_threshold if config else 10
    if k_min < k_min_req:
        return "failed"
    
    qualitative_checks = [has_l_diversity, has_sandbox, has_covenants, has_pia_irb]
    if any(c is False for c in qualitative_checks):
        return "failed"
    if any(c is None for c in qualitative_checks):
        return "not_assessed"
    return "passed"


def calculate_critical_alpha(k_min, gamma_org, tau_safe=0.04):
    """Calculates theoretical critical threshold boundary: alpha_crit = (tau_safe * k_min) / gamma_org."""
    return (float(tau_safe) * float(k_min)) / float(gamma_org)


def run_grid_sensitivity(config: SimulationConfig):
    """Evaluates multi-parameter sensitivity grid across key operational bounds with decoupled criteria."""
    print("=" * 80)
    print("1. RUNNING MULTI-DIMENSIONAL PARAMETER SENSITIVITY GRID EVALUATION (v1.1.0)")
    print("=" * 80)

    r_base = calculate_risk(config.k_base, config.alpha_base, config.gamma_base)
    base_numeric_pass = meets_risk_threshold(config.k_base, config.alpha_base, config.gamma_base, config.tau_safe)
    base_framework_status = evaluate_framework_requirements(config.k_base, True, True, True, True, config)

    print(f"Research Baseline Hypotheses: k_min={config.k_base}, alpha_env={config.alpha_base}, gamma_org={config.gamma_base}")
    print(f"Baseline R_res: {r_base:.4f} ({r_base*100:.2f}%)")
    print(f"Meets Risk Threshold (<= {config.tau_safe:.2%}): {base_numeric_pass}")
    print(f"Framework Requirements Status (Full controls verified): {base_framework_status}\n")

    csv_path = os.path.join(DATA_DIR, "sensitivity_grid.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "k_min", "meets_minimum_k", "p_link", "alpha_env", "gamma_org",
            "R_res", "R_res_pct", "meets_risk_threshold",
            "framework_requirements_status", "alpha_critical", "boundary_margin"
        ])

        for k in config.k_vals:
            for a in config.alpha_vals:
                for g in config.gamma_vals:
                    r = calculate_risk(k, a, g)
                    min_k_met = meets_minimum_k(k, config.k_min_threshold)
                    numeric_pass = meets_risk_threshold(k, a, g, config.tau_safe)
                    # When assessing raw grid points, auxiliary controls are not evaluated
                    fw_status = evaluate_framework_requirements(k, None, None, None, None, config)
                    alpha_crit = calculate_critical_alpha(k, g, config.tau_safe)
                    margin = alpha_crit - a

                    writer.writerow([
                        k, min_k_met, f"{1.0/k:.4f}", a, g,
                        f"{r:.6f}", f"{r*100:.2f}%", numeric_pass,
                        fw_status, f"{alpha_crit:.4f}", f"{margin:.4f}"
                    ])

    total_points = len(config.k_vals) * len(config.alpha_vals) * len(config.gamma_vals)
    print(f"Exported refined sensitivity grid ({total_points} points) -> {csv_path}")

    # Display key operational scenarios with decoupled status
    print("\n--- Key Operational Scenarios with Decoupled Status ---")
    scenarios = [
        ("Baseline Full Safe Harbor", 10, 0.25, 0.72, True, True, True, True),
        ("Element 1 Alone (k=10, raw export)", 10, 1.00, 1.00, False, False, False, False),
        ("Elements 1 & 2 (No covenant deterrence)", 10, 0.25, 1.00, True, True, False, True),
        ("Environmental Degradation (+120% exposure)", 10, 0.55, 0.72, True, True, True, True),
        ("Critical Environment Breakdown (alpha=0.60)", 10, 0.60, 0.72, True, True, True, True),
        ("Rare Disease Cohort (Small class k=5)", 5, 0.25, 0.72, True, True, True, True),
        ("Precision Boundary Edge Case (k=5, a=0.20, g=1.0)", 5, 0.20, 1.00, None, None, None, None),
        ("Sub-Threshold Rare Cohort (k=4)", 4, 0.25, 0.72, True, True, True, True),
        ("Ultra-Secure Sandbox (k=15, DP epsilon=1.0)", 15, 0.15, 0.72, True, True, True, True),
    ]

    header = f"{'Scenario Name':<42} | {'k':<3} | {'Min k?':<7} | {'alpha':<5} | {'gamma':<5} | {'R_res':<7} | {'Risk Met?':<9} | {'Framework Status'}"
    print(header)
    print("-" * len(header))
    for name, k, a, g, has_l, has_sb, has_cov, has_pia in scenarios:
        r = calculate_risk(k, a, g)
        min_k_met = meets_minimum_k(k, config.k_min_threshold)
        r_met = meets_risk_threshold(k, a, g, config.tau_safe)
        fw_status = evaluate_framework_requirements(k, has_l, has_sb, has_cov, has_pia, config)
        print(f"{name:<42} | {k:<3} | {str(min_k_met):<7} | {a:<5.2f} | {g:<5.2f} | {r*100:>5.2f}% | {str(r_met):<9} | {fw_status}")


def run_stress_testing(config: SimulationConfig):
    """
    Evaluates operational degradation stress scenarios and analytical boundary margins:
    Reports threshold breaches, distance to failure (alpha <= tau*k / gamma), and sensitivity headroom.
    """
    print("\n" + "=" * 80)
    print("2. REPRODUCIBLE STRESS TESTING & MARGIN-TO-FAILURE ANALYSIS")
    print("=" * 80)

    stress_scenarios = [
        ("Moderate Environment Exposure (alpha=0.50, gamma=0.72)", 10, 0.50, 0.72),
        ("Organizational Control Erosion (alpha=0.25, gamma=0.85)", 10, 0.25, 0.85),
        ("Dual Stress Failure (alpha=0.50, gamma=0.85)", 10, 0.50, 0.85),
        ("Adversarial Extreme Scenario (alpha=0.75, gamma=1.00)", 10, 0.75, 1.00),
    ]

    print(f"{'Stress Scenario':<55} | {'R_res':<7} | {'Threshold':<9} | {'alpha_crit':<10} | {'Safety Margin'}")
    print("-" * 100)
    breaches = 0
    for name, k, a, g in stress_scenarios:
        r = calculate_risk(k, a, g)
        met = meets_risk_threshold(k, a, g, config.tau_safe)
        if not met:
            breaches += 1
        alpha_crit = calculate_critical_alpha(k, g, config.tau_safe)
        margin = alpha_crit - a
        status_str = "SAFE" if met else "BREACH"
        print(f"{name:<55} | {r*100:>5.2f}% | {status_str:<9} | {alpha_crit:>10.4f} | {margin:>+12.4f}")

    print(f"\nStress Testing Summary: {breaches} of {len(stress_scenarios)} scenarios breached the 4.0% model threshold.")


def run_monte_carlo_simulation(config: SimulationConfig):
    """
    Performs 10,000 Monte Carlo perturbation draws with explicitly documented distribution.
    Supports default 'clipped_normal' and optional 'truncated_normal'.
    """
    print("\n" + "=" * 80)
    print(f"3. RUNNING MONTE CARLO STOCHASTIC SIMULATION (N={config.n_simulations}, Dist={config.distribution_type})")
    print("=" * 80)

    np.random.seed(config.random_seed)

    # Equivalence class draws: discrete uniform [8, 15]
    k_sim = np.random.randint(8, 16, size=config.n_simulations)

    # Environment factor draws: Beta(2, 5) scaled to [0.15, 0.45]
    alpha_sim = np.random.beta(a=2, b=5, size=config.n_simulations) * (0.45 - 0.15) + 0.15

    # Organizational control factor draws
    if config.distribution_type == "truncated_normal":
        try:
            from scipy.stats import truncnorm
            a_bound, b_bound = (0.55 - 0.72) / 0.08, (0.95 - 0.72) / 0.08
            gamma_sim = truncnorm.rvs(a_bound, b_bound, loc=0.72, scale=0.08, size=config.n_simulations)
            print("Sampling gamma_org from SciPy Truncated Normal distribution [0.55, 0.95].")
        except ImportError:
            gamma_sim = np.clip(np.random.normal(loc=0.72, scale=0.08, size=config.n_simulations), 0.55, 0.95)
            print("SciPy not found. Falling back to NumPy clipped normal distribution [0.55, 0.95].")
    else:
        # Default verified baseline: NumPy clipped normal distribution
        gamma_sim = np.clip(np.random.normal(loc=0.72, scale=0.08, size=config.n_simulations), 0.55, 0.95)
        print("Sampling gamma_org from NumPy Clipped Normal distribution [0.55, 0.95].")

    r_sim = (1.0 / k_sim) * alpha_sim * gamma_sim
    risk_mask = [
        meets_risk_threshold(k_sim[i], alpha_sim[i], gamma_sim[i], config.tau_safe)
        for i in range(config.n_simulations)
    ]
    k_mask = [
        meets_minimum_k(k_sim[i], config.k_min_threshold)
        for i in range(config.n_simulations)
    ]
    dual_mask = [risk_mask[i] and k_mask[i] for i in range(config.n_simulations)]

    risk_pass_rate = float(np.mean(risk_mask) * 100.0)
    k_pass_rate = float(np.mean(k_mask) * 100.0)
    pass_rate = float(np.mean(dual_mask) * 100.0)

    print(f"Mean R_res: {np.mean(r_sim)*100:.2f}% (Std: {np.std(r_sim)*100:.2f}%)")
    print(f"5th Percentile: {np.percentile(r_sim, 5)*100:.2f}% | 95th Percentile: {np.percentile(r_sim, 95)*100:.2f}%")
    print(f"Numeric Threshold Rate (R_res <= {config.tau_safe:.2%}): {risk_pass_rate:.2f}%")
    print(f"Minimum Equivalence Class Rate (k_min >= {config.k_min_threshold}): {k_pass_rate:.2f}%")
    print(
        f"Empirical Safe Harbor Conjunctive Rate "
        f"(k_min >= {config.k_min_threshold} AND R_res <= {config.tau_safe:.2%}): {pass_rate:.2f}%"
    )

    # Export Monte Carlo summary (preserving existing 7 columns in place + appending conjunctive columns)
    mc_csv_path = os.path.join(DATA_DIR, "monte_carlo_results.csv")
    with open(mc_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sim_id", "k_min", "alpha_env", "gamma_org", "R_res",
            "meets_risk_threshold", "sampling_distribution",
            "meets_minimum_k", "passes_safe_harbor"
        ])
        for idx in range(config.n_simulations):
            writer.writerow([
                idx + 1, k_sim[idx], f"{alpha_sim[idx]:.4f}", f"{gamma_sim[idx]:.4f}",
                f"{r_sim[idx]:.6f}", risk_mask[idx], config.distribution_type,
                k_mask[idx], dual_mask[idx]
            ])
    print(f"Exported Monte Carlo draws -> {mc_csv_path}")

    return r_sim, pass_rate


def generate_visualizations(r_sim, config: SimulationConfig):
    """
    Generates publication-grade sensitivity surfaces and Monte Carlo risk distribution.
    Updated for v1.1.0:
    - Replaced 'Statutory Gate' with 'Research Threshold (tau=4.0%)'.
    - Removed 'HIPAA 5% Benchmark' to avoid statutory inaccuracy.
    """
    print("\n" + "=" * 80)
    print("4. GENERATING HIGH-RESOLUTION SENSITIVITY & ROBUSTNESS FIGURES")
    print("=" * 80)

    fig = plt.figure(figsize=(14, 6), dpi=300)

    # Panel A: 3D Surface of Residual Risk vs k_min and alpha_env (gamma=0.72)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    k_grid, alpha_grid = np.meshgrid(np.linspace(4, 20, 50), np.linspace(0.15, 0.80, 50))
    gamma_fixed = config.gamma_base
    r_grid = (1.0 / k_grid) * alpha_grid * gamma_fixed * 100.0  # in percentage

    surf = ax1.plot_surface(k_grid, alpha_grid, r_grid, cmap='viridis_r', alpha=0.85, edgecolor='none')
    # Plot 4% research threshold plane
    tau_plane = np.full_like(r_grid, config.tau_safe * 100.0)
    ax1.plot_surface(k_grid, alpha_grid, tau_plane, color='red', alpha=0.35)

    ax1.set_xlabel('Equivalence Class ($k_{\\min}$)', labelpad=10, fontsize=10)
    ax1.set_ylabel('Environment Factor ($\\alpha_{\\mathrm{env}}$)', labelpad=10, fontsize=10)
    ax1.set_zlabel('Residual Risk $R_{\\mathrm{res}}$ (%)', labelpad=10, fontsize=10)
    ax1.set_title('(A) Response Surface vs. Research Threshold ($\\tau_{\\mathrm{safe}}=4.0\\%$)', fontsize=11, fontweight='bold', pad=15)
    ax1.view_init(elev=24, azim=-125)

    # Panel B: Monte Carlo Distribution
    ax2 = fig.add_subplot(1, 2, 2)
    counts, bins, patches = ax2.hist(r_sim * 100.0, bins=45, color='#1f77b4', edgecolor='black', alpha=0.75, density=True)
    for patch, bin_left in zip(patches, bins[:-1]):
        if bin_left > config.tau_safe * 100.0:
            patch.set_facecolor('#d62728')  # Highlight breach in red

    ax2.axvline(config.tau_safe * 100.0, color='red', linestyle='--', linewidth=2.0, label='Research Threshold ($\\tau_{\\mathrm{safe}}=4.0\\%$)')
    ax2.axvline(0.018 * 100.0, color='green', linestyle='-', linewidth=2.0, label='Baseline Design Point ($R_{\\mathrm{res}}=1.8\\%$)')

    ax2.set_xlabel('Composite Residual Risk $R_{\\mathrm{res}}$ (%)', fontsize=10)
    ax2.set_ylabel('Empirical Density', fontsize=10)
    ax2.set_title(f'(B) Monte Carlo Risk Distribution (N={config.n_simulations:,}, Clipped Normal)', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "figure_sensitivity_surface.png")
    plt.savefig(fig_path, bbox_inches='tight')
    plt.close()
    print(f"Generated refined sensitivity visualization figure -> {fig_path}")


def main():
    config = SimulationConfig()
    run_grid_sensitivity(config)
    run_stress_testing(config)
    r_sim, pass_rate = run_monte_carlo_simulation(config)
    generate_visualizations(r_sim, config)
    print("\n[SUCCESS] Sensitivity analysis, stress testing, and figures completed cleanly.")


if __name__ == "__main__":
    main()
