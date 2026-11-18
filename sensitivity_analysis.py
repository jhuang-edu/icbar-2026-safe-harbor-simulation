"""
Reproducible Parameter Sensitivity Analysis & Monte Carlo Risk Simulation
for ICBAR 2026: Scenario-Risk Safe Harbor under China's PIPL
Author: Junjun Huang (Corresponding Author: junjun@ieee.org)
Paper: Scenario-Risk Safe Harbor for Secondary Health Data Governance and AI Training under China's Personal Information Protection Law
Repository: https://github.com/jhuang-edu/icbar-2026-safe-harbor-simulation
License: MIT License
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt

# Output directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ---------------------------------------------------------
# Core Formula Definition (Eq. 1)
# R_res = (1 / k_min) * alpha_env * gamma_org <= tau_safe (0.04)
# ---------------------------------------------------------
TAU_SAFE = 0.04  # 4.0% Safe Harbor Threshold (mirroring HIPAA expert determination & stricter than EMA 0.09)


def calculate_risk(k_min, alpha_env, gamma_org):
    """Calculates composite residual re-identification risk via conditional probability chain rule."""
    p_link = 1.0 / float(k_min)
    return p_link * float(alpha_env) * float(gamma_org)


def run_grid_sensitivity():
    """Evaluates multi-parameter sensitivity grid across key operational bounds."""
    print("=" * 70)
    print("1. RUNNING MULTI-DIMENSIONAL PARAMETER SENSITIVITY GRID EVALUATION")
    print("=" * 70)

    # Baseline configuration
    k_base = 10
    alpha_base = 0.25
    gamma_base = 0.72
    r_base = calculate_risk(k_base, alpha_base, gamma_base)
    print(f"Baseline: k_min={k_base}, alpha_env={alpha_base}, gamma_org={gamma_base}")
    print(f"Baseline R_res: {r_base:.4f} ({r_base*100:.2f}%) | Compliant (<= 0.04): {r_base <= TAU_SAFE}\n")

    # Grid ranges
    k_vals = [4, 5, 8, 10, 12, 15, 20]
    alpha_vals = [0.15, 0.20, 0.25, 0.35, 0.50, 0.55, 0.60, 0.75, 1.00]
    gamma_vals = [0.50, 0.60, 0.72, 0.85, 1.00]

    csv_path = os.path.join(DATA_DIR, "sensitivity_grid.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["k_min", "p_link", "alpha_env", "gamma_org", "R_res", "R_res_pct", "is_compliant", "margin_to_gate"])

        for k in k_vals:
            for a in alpha_vals:
                for g in gamma_vals:
                    r = calculate_risk(k, a, g)
                    margin = TAU_SAFE - r
                    compliant = r <= TAU_SAFE
                    writer.writerow([k, f"{1.0/k:.4f}", a, g, f"{r:.6f}", f"{r*100:.2f}%", compliant, f"{margin:.6f}"])

    print(f"Exported full sensitivity grid ({len(k_vals)*len(alpha_vals)*len(gamma_vals)} points) -> {csv_path}")

    # Summary table for reporting in Response Letter
    print("\n--- Key Operational Scenarios & Edge Cases ---")
    scenarios = [
        ("Baseline Full Safe Harbor", 10, 0.25, 0.72),
        ("Element 1 Alone (k=10, raw export)", 10, 1.00, 1.00),
        ("Elements 1 & 2 (No covenant deterrence)", 10, 0.25, 1.00),
        ("Environmental Degradation (+120% exposure)", 10, 0.55, 0.72),
        ("Critical Environment Breakdown (alpha=0.60)", 10, 0.60, 0.72),
        ("Rare Disease Cohort (Small equivalence class k=5)", 5, 0.25, 0.72),
        ("Sub-Threshold Rare Cohort (k=4)", 4, 0.25, 0.72),
        ("Ultra-Secure Sandbox (k=15, DP epsilon=1.0)", 15, 0.15, 0.72),
    ]

    print(f"{'Scenario Name':<42} | {'k':<3} | {'alpha':<5} | {'gamma':<5} | {'R_res':<7} | {'Compliant?'}")
    print("-" * 78)
    for name, k, a, g in scenarios:
        r = calculate_risk(k, a, g)
        comp_str = "PASS (<= 4%)" if r <= TAU_SAFE else "BREACH (> 4%)"
        print(f"{name:<42} | {k:<3} | {a:<5.2f} | {g:<5.2f} | {r*100:>5.2f}% | {comp_str}")


def run_monte_carlo_simulation(n_simulations=10000):
    """Performs 10,000 Monte Carlo perturbation runs to evaluate gate robustness under operational uncertainty."""
    print("\n" + "=" * 70)
    print(f"2. RUNNING MONTE CARLO STOCHASTIC PERTURBATION SIMULATION (N={n_simulations})")
    print("=" * 70)

    np.random.seed(42)

    # Stochastic distributions around operational parameters
    # k_min: discrete uniform between [8, 15]
    k_sim = np.random.randint(8, 16, size=n_simulations)
    # alpha_env: Beta distribution scaled to [0.15, 0.45], centered around 0.25
    alpha_sim = np.random.beta(a=2, b=5, size=n_simulations) * (0.45 - 0.15) + 0.15
    # gamma_org: Truncated normal distribution around 0.72 (std=0.08, bounds [0.55, 0.95])
    gamma_sim = np.clip(np.random.normal(loc=0.72, scale=0.08, size=n_simulations), 0.55, 0.95)

    r_sim = (1.0 / k_sim) * alpha_sim * gamma_sim
    pass_mask = r_sim <= TAU_SAFE
    pass_rate = np.mean(pass_mask) * 100.0

    print(f"Mean R_res: {np.mean(r_sim)*100:.2f}% (Std: {np.std(r_sim)*100:.2f}%)")
    print(f"5th Percentile: {np.percentile(r_sim, 5)*100:.2f}% | 95th Percentile: {np.percentile(r_sim, 95)*100:.2f}%")
    print(f"Empirical Compliance Rate (R_res <= 0.04): {pass_rate:.2f}%")

    # Export Monte Carlo summary
    mc_csv_path = os.path.join(DATA_DIR, "monte_carlo_results.csv")
    with open(mc_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sim_id", "k_min", "alpha_env", "gamma_org", "R_res", "is_compliant"])
        for idx in range(n_simulations):
            writer.writerow([idx + 1, k_sim[idx], f"{alpha_sim[idx]:.4f}", f"{gamma_sim[idx]:.4f}", f"{r_sim[idx]:.6f}", pass_mask[idx]])
    print(f"Exported Monte Carlo draws -> {mc_csv_path}")

    return r_sim, pass_rate


def generate_visualizations(r_sim):
    """Generates publication-grade sensitivity surfaces and Monte Carlo risk distribution."""
    print("\n" + "=" * 70)
    print("3. GENERATING HIGH-RESOLUTION SENSITIVITY & ROBUSTNESS FIGURES")
    print("=" * 70)

    fig = plt.figure(figsize=(14, 6), dpi=300)

    # Panel A: 3D Surface of Residual Risk vs k_min and alpha_env (gamma=0.72)
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    k_grid, alpha_grid = np.meshgrid(np.linspace(4, 20, 50), np.linspace(0.15, 0.80, 50))
    gamma_fixed = 0.72
    r_grid = (1.0 / k_grid) * alpha_grid * gamma_fixed * 100.0  # in percentage

    surf = ax1.plot_surface(k_grid, alpha_grid, r_grid, cmap='viridis_r', alpha=0.85, edgecolor='none')
    # Plot 4% threshold plane
    tau_plane = np.full_like(r_grid, TAU_SAFE * 100.0)
    ax1.plot_surface(k_grid, alpha_grid, tau_plane, color='red', alpha=0.35)

    ax1.set_xlabel('Equivalence Class ($k_{\\min}$)', labelpad=10, fontsize=10)
    ax1.set_ylabel('Environment Factor ($\\alpha_{\\mathrm{env}}$)', labelpad=10, fontsize=10)
    ax1.set_zlabel('Residual Risk $R_{\\mathrm{res}}$ (%)', labelpad=10, fontsize=10)
    ax1.set_title('(A) Response Surface vs. Safe Harbor Gate ($\\tau_{\\mathrm{safe}}=4.0\\%$)', fontsize=11, fontweight='bold', pad=15)
    ax1.view_init(elev=24, azim=-125)

    # Panel B: Monte Carlo Distribution
    ax2 = fig.add_subplot(1, 2, 2)
    counts, bins, patches = ax2.hist(r_sim * 100.0, bins=45, color='#1f77b4', edgecolor='black', alpha=0.75, density=True)
    for patch, bin_left in zip(patches, bins[:-1]):
        if bin_left > TAU_SAFE * 100.0:
            patch.set_facecolor('#d62728')  # Highlight breach in red

    ax2.axvline(TAU_SAFE * 100.0, color='red', linestyle='--', linewidth=2.0, label='Statutory Gate $\\tau_{\\mathrm{safe}}=4.0\\%$')
    ax2.axvline(0.018 * 100.0, color='green', linestyle='-', linewidth=2.0, label='Baseline Design Point ($R_{\\mathrm{res}}=1.8\\%$)')
    ax2.axvline(0.05 * 100.0, color='gray', linestyle=':', linewidth=1.8, label='HIPAA Expert Benchmark ($5.0\\%$)')

    ax2.set_xlabel('Composite Residual Risk $R_{\\mathrm{res}}$ (%)', fontsize=10)
    ax2.set_ylabel('Empirical Density', fontsize=10)
    ax2.set_title('(B) Monte Carlo Risk Distribution (N=10,000 Perturbations)', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=9)

    plt.tight_layout()
    fig_path = os.path.join(FIG_DIR, "figure_sensitivity_surface.png")
    plt.savefig(fig_path, bbox_inches='tight')
    plt.close()
    print(f"Generated sensitivity visualization figure -> {fig_path}")


def main():
    run_grid_sensitivity()
    r_sim, pass_rate = run_monte_carlo_simulation(n_simulations=10000)
    generate_visualizations(r_sim)
    print("\n[SUCCESS] Sensitivity analysis, simulation, and figures generated perfectly.")


if __name__ == "__main__":
    main()
