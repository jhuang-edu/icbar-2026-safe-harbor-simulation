<div align="center">

# Scenario-Risk Safe Harbor Simulation & Sensitivity Analysis
### Open-Source Reproducibility Suite for Academic Research

[![Release](https://img.shields.io/badge/Release-v1.2.0-blue.svg?style=flat-square)](#version-history)
[![Target Venue](https://img.shields.io/badge/Target%20Venue-ICBAR%202026-1f6feb.svg?style=flat-square)](https://www.ais.cn/attendees/index/2ER6F3)
[![Status](https://img.shields.io/badge/Status-Under%20Revision-success.svg?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg?style=flat-square)](https://creativecommons.org/licenses/by/4.0/)

<p align="center">
  <a href="#english">English</a> •
  <a href="#中文说明">中文说明</a> •
  <a href="#日本語案内">日本語案内</a> •
  <a href="#version-history">Version History</a> •
  <a href="REFERENCES.md"><strong>📚 Reference List / 参考文献清单</strong></a>
</p>

---

</div>

<a name="version-history"></a>
## 🚀 Version History & Academic Release Notes

This repository strictly adheres to reproducible research principles. Versions correspond directly to manuscript iterations:

| Version | Status | Key Characteristics & Methodology |
|:---:|:---:|:---|
| [**v1.0.0**](https://github.com/jhuang-edu/icbar-2026-safe-harbor-simulation/releases/tag/v1.0.0) | Archived Snapshot | **Official reproducible baseline snapshot for Paper v2 (submitted).** Matches all numerical and graphical results in the initial revision manuscript. |
| [**v1.1.0**](https://github.com/jhuang-edu/icbar-2026-safe-harbor-simulation/releases/tag/v1.1.0) | Archived Snapshot | **Methodological hardening & decoupled criteria release:**<br>1. **IEEE 754 Precision Fix**: Implemented exact decimal evaluation for $\alpha \times \gamma \le \tau \times k$. In the 315-point grid, only **one single edge-case** (`k=5, alpha=0.20, gamma=1.00`) changes evaluation from `False` to `True` (exactly equals 4.00%).<br>2. **Decoupled Governance Evaluation**: Disentangled pure numeric threshold (`meets_risk_threshold`) from statutory triad criteria (`framework_requirements_status`). For example, $k=5$ yields $3.60\% \le 4.0\%$ (numeric pass), but fails statutory criteria because $k < 10$.<br>3. **Reproducible Stress Testing**: Introduced environmental degradation and organizational erosion stress scenarios with analytical safety margins $\alpha_{\mathrm{crit}} = \frac{\tau \cdot k}{\gamma}$.<br>4. **Statistical Rigor**: Explicitly documented sampling distribution as Clipped Normal with optional Truncated Normal support; updated visualizations to reflect research-defined thresholds. |
| [**v1.2.0**](https://github.com/jhuang-edu/icbar-2026-safe-harbor-simulation/releases/tag/v1.2.0) | Current Release | **Official reproducible release for Paper v4 (ICBAR 2026 Revised Submission):**<br>1. **UCI Diabetes 130-US Empirical Benchmark (`benchmark_uci_diabetes.py`)**: End-to-end leakage-free 5-seed (`GroupShuffleSplit`, seeds 42 to 46) evaluation on 101,766 encounters / 71,518 patients covering E1 (6-QI Mondrian $(k, l)$-anonymity) and E2 (per-sample L2-clipped DP-SGD with log-domain RDP accounting + Yeom MIA defense), exporting `data/uci_diabetes_benchmark.csv` and `figures/figure2_uci_benchmark.png`.<br>2. **Conjunctive Monte Carlo Compliance Fix**: Fixed `sensitivity_analysis.py` (`config.gamma_vals` scope & dual conjunctive $k_{\min} \ge 10 \land R_{\mathrm{res}} \le 0.04$ evaluation yielding `75.08%`, exported with `meets_minimum_k` and `passes_safe_harbor` columns).<br>3. **Reference & Figure Hygiene**: Retired obsolete synthetic diagram, corrected Ref. [12] GDPR official EUR-Lex ELI link, and aligned all Table 3 / Figure 2 metrics 100% programmatically from CSV. |

---

<a name="english"></a>
## English

### 1. Research Overview & Methodological Scope
- **Paper Title**: *A Computational Scenario-Risk Safe Harbor for Privacy-Preserving Health Data Governance and AI Training under China's Personal Information Protection Law*
- **Current Status**: Under Revision / Peer Review (Target Venue: ICBAR 2026, proceedings scheduled with IOS Press *FAIA*).
- **Core Focus**: Addressing the operational challenges of sensitive personal data "separate consent" requirements under Articles 28 and 29 of China's PIPL for retrospective clinical research and medical AI training, proposing a three-element scenario-risk safe harbor framework.
- **Methodological Scope & Scenario Assumptions**:
  - The parameter $\alpha_{\mathrm{env}}=0.25$ is stipulated as an illustrative low-exposure scenario for zero-egress federated sandboxes; estimating combined real-world exposure requires empirical data on attack pathway frequency and overlap.
  - The parameter $\gamma_{\mathrm{org}}=0.72$ assumes covenants and audit tracking reduce unauthorized linkage attempts by 28% relative to a no-control reference. Both values are scenario assumptions pending prospective multi-center calibration.
  - Parameter sensitivity analysis explores outcome variations across alternative input combinations rather than validating the baseline priors themselves.
  - Safe harbor protection operates as a **dual conjunctive test**: datasets must satisfy both all three structural elements ($k_{\min} \ge 10$, DP sandbox, covenants/PIA-IRB) AND composite risk $R_{\mathrm{res}} \le 0.04$.
  - The utility falsification cutoff is defined as an **absolute decrease of more than 0.05 in macro ROC-AUC** against unprotected baselines on identical evaluation sets.
- **Academic Contact**: `3588@duck.com` (for research questions and simulation inquiries).

### 2. Architecture & Governance Diagrams

<div align="center">

#### Figure 1: Three-Element Safe Harbor & PIA-IRB Co-Governance Architecture
<img src="figures/figure1_safe_harbor_architecture.png" alt="Figure 1 Safe Harbor Architecture" width="850"/>

<br><br>

#### Figure 2: Empirical Evaluation on UCI Diabetes 130-US (Mondrian (k, l) Generalization & DP-SGD/MIA Defense)
<img src="figures/figure2_uci_benchmark.png" alt="Figure 2 UCI Diabetes Empirical Benchmark" width="850"/>

> *Automated Reproducibility Note*: Figure 2 is generated automatically by `benchmark_uci_diabetes.py` from `data/uci_diabetes_benchmark.csv` on the UCI Diabetes 130-US dataset (ID=296; 101,766 encounters across 71,518 unique patients, patient-grouped 80/20 splits over 5 seeds `42..46`). All quantitative metrics reported in the manuscript are parsed directly from `data/uci_diabetes_benchmark.csv` without manual transcription.

| Experiment | Setting | $k_{\min}$ | $l_{\min}$ | $\mathrm{NCP}$ (mean $\pm$ std) | $R_{\mathrm{res}}$ | Main ROC-AUC | Local ROC-AUC ($N=2\text{k}$) | Local MIA $\mathrm{Adv}_{\max}$ | Local Yeom Mean Adv | Safe Harbor Gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| E1 | `Raw` | 1 | 1 | 0.0000 | 18.00% | - | - | - | - | False |
| E1 | `Mondrian_k5_l3` | 5 | 3 | 0.0083 $\pm$ 0.0004 | 3.60% | - | - | - | - | False ($k<10$) |
| E1 | `Mondrian_k10_l3` | 10 | 3 | 0.0152 $\pm$ 0.0005 | 1.80% | - | - | - | - | **True** |
| E1 | `Mondrian_k20_l3` | 20 | 3 | 0.0249 $\pm$ 0.0009 | 0.90% | - | - | - | - | **True** |
| E2 | `DPSGD_eps_inf` | 10 | 3 | 0.0152 $\pm$ 0.0005 | 1.80% | 0.6951 $\pm$ 0.0026 | 0.6359 $\pm$ 0.0240 | 0.1749 $\pm$ 0.0440 | 0.1566 | True |
| E2 | `DPSGD_eps_4.0` | 10 | 3 | 0.0152 $\pm$ 0.0005 | 1.80% | 0.6774 $\pm$ 0.0027 | 0.6123 $\pm$ 0.0197 | 0.0873 $\pm$ 0.0142 | 0.0694 | True |
| E2 | `DPSGD_eps_2.0` | 10 | 3 | 0.0152 $\pm$ 0.0005 | 1.80% | 0.6775 $\pm$ 0.0031 | 0.5673 $\pm$ 0.0163 | 0.0716 $\pm$ 0.0177 | 0.0575 | True |
| E2 | `DPSGD_eps_1.0` | 10 | 3 | 0.0152 $\pm$ 0.0005 | 1.80% | 0.6774 $\pm$ 0.0032 | 0.5647 $\pm$ 0.0174 | 0.0458 $\pm$ 0.0157 | 0.0297 | True |
| E2 | `DPSGD_eps_0.5` | 10 | 3 | 0.0152 $\pm$ 0.0005 | 1.80% | 0.6774 $\pm$ 0.0029 | 0.5239 $\pm$ 0.0363 | 0.0500 $\pm$ 0.0262 | 0.0187 | True |

> *Statistical Mechanism Note*: On the full cohort ($N = 101{,}766$), per-sample $L_2$ gradient clipping ($C = 1.5$) accounts for the initial `0.0176` ROC-AUC shift while large-batch averaging smooths zero-mean Gaussian noise across $\varepsilon \in [0.5, 4.0]$ (raw unprotected baseline ROC-AUC = `0.6990`, maximum absolute drop = `0.0216 <= 0.05`). On the realistic hospital-scale subcohort ($N = 2{,}000$), stricter DP noise produces monotonic privacy-utility regularization: local ROC-AUC moves from `0.6359` to `0.5239` while Yeom training-mean MIA advantage drops monotonically at every step from `0.1566` down to `0.0187`.

</div>

### 3. Theoretical Risk Formulation (Equation 1)
Under a defense-in-depth architecture, re-identification requires the conjunctive occurrence of three sequential failure events: (i) organizational deterrence failure $P(E_{\mathrm{org}}) = \gamma_{\mathrm{org}}$, (ii) environment containment failure $P(E_{\mathrm{env}} \mid E_{\mathrm{org}}) = \alpha_{\mathrm{env}}$, and (iii) quasi-identifier linkage $P(E_{\mathrm{ID}} \mid E_{\mathrm{env}}, E_{\mathrm{org}}) = 1 / k_{\min}$. By the chain rule of conditional probability:

$$R_{\mathrm{res}} = \left(\frac{1}{k_{\min}}\right) \cdot \alpha_{\mathrm{env}} \cdot \gamma_{\mathrm{org}} \le \tau_{\mathrm{safe}}\ (0.04)$$

Where:
- $k_{\min} \ge 10$: Quasi-identifier equivalence class minimum size ($p_{\mathrm{link}} = 1 / k_{\min}$);
- $\alpha_{\mathrm{env}} = 0.25$: Zero-egress federated computation sandbox with DP-SGD noise ($\varepsilon \le 2.0$);
- $\gamma_{\mathrm{org}} = 0.72$: Binding anti-reidentification covenants and immutable audit logging.
- $\tau_{\mathrm{safe}} = 0.04$ (4.0%): Stricter than EMA Policy 0070 (0.09) and conservative for PIPL due care presumption. Baseline risk yields $R_{\mathrm{res}} = 0.10 \times 0.25 \times 0.72 = 1.80\% \le 4.0\%$.

### 4. Decoupled Operational Scenarios & Stress Testing

| Scenario ID | Operational Scenario Description | $k_{\min}$ | Min $k \ge 10$? | $\alpha_{\mathrm{env}}$ | $\gamma_{\mathrm{org}}$ | $R_{\mathrm{res}}$ | Numeric Pass ($\le 4\%$) | Framework Status (Triad Gate) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **S1** | **Baseline Full Safe Harbor** | **10** | **True** | **0.25** | **0.72** | **1.80%** | **True** | **passed** |
| S2 | Element 1 Alone (Raw export, no covenant) | 10 | True | 1.00 | 1.00 | 10.00% | False | failed |
| S3 | Elements 1 & 2 (Sandbox, no covenant) | 10 | True | 0.25 | 1.00 | 2.50% | True | failed |
| S4 | Environmental Degradation (+120% exposure) | 10 | True | 0.55 | 0.72 | 3.96% | True | passed |
| S5 | Critical Environment Breakdown ($\alpha=0.60$) | 10 | True | 0.60 | 0.72 | 4.32% | False | passed |
| S6 | Rare Disease Cohort (Small class $k=5$) | 5 | False | 0.25 | 0.72 | 3.60% | True | **failed ($k < 10$)** |
| S7 | Boundary Edge Case ($k=5, \alpha=0.20, \gamma=1.0$) | 5 | False | 0.20 | 1.00 | 4.00% | **True (Exact 4%)** | **failed ($k < 10$)** |
| S8 | Sub-Threshold Rare Cohort ($k=4$) | 4 | False | 0.25 | 0.72 | 4.50% | False | failed |
| S9 | Ultra-Secure Sandbox ($k=15, \varepsilon=1.0$) | 15 | True | 0.15 | 0.72 | 0.72% | True | passed |

#### Stress Testing & Distance-to-Failure Analysis
The analytical critical exposure threshold is defined by $\alpha_{\mathrm{crit}} = \frac{\tau_{\mathrm{safe}} \cdot k_{\min}}{\gamma_{\mathrm{org}}}$:
- **Moderate Exposure** ($\alpha=0.50, \gamma=0.72$): $R_{\mathrm{res}} = 3.60\%$, $\alpha_{\mathrm{crit}} = 0.5556$, Safety Margin = $+0.0556$ (Safe).
- **Organizational Erosion** ($\alpha=0.25, \gamma=0.85$): $R_{\mathrm{res}} = 2.12\%$, $\alpha_{\mathrm{crit}} = 0.4706$, Safety Margin = $+0.2206$ (Safe).
- **Dual Stress Breakdown** ($\alpha=0.50, \gamma=0.85$): $R_{\mathrm{res}} = 4.25\%$, $\alpha_{\mathrm{crit}} = 0.4706$, Safety Margin = $-0.0294$ (**Breached**).
- **Adversarial Extreme** ($\alpha=0.75, \gamma=1.00$): $R_{\mathrm{res}} = 7.50\%$, $\alpha_{\mathrm{crit}} = 0.4000$, Safety Margin = $-0.3500$ (**Breached**).

<div align="center">

#### Figure 3: Parameter Sensitivity Surface & Monte Carlo Distribution
<img src="figures/figure_sensitivity_surface.png" alt="Figure 3 Sensitivity Surface" width="750"/>

</div>

### 5. Quick Start & Verification
```bash
# Clone the repository
git clone https://github.com/jhuang-edu/icbar-2026-safe-harbor-simulation.git
cd icbar-2026-safe-harbor-simulation

# Install requirements
pip install -r requirements.txt

# Run automated regression & assertion test suite
python test_sensitivity.py

# Run full parameter sensitivity evaluation, stress testing & Monte Carlo simulation
python sensitivity_analysis.py

# Run UCI Diabetes 130-US empirical benchmark (caches dataset under data/cache/)
python benchmark_uci_diabetes.py
```

---

<a name="中文说明"></a>
## 中文说明

### 1. 论文与研究背景
- **论文题目**：《个人信息保护法》下隐私保护健康数据治理与AI训练的可计算场景风险安全港研究
- **当前状态**：审稿返修中（拟投递 ICBAR 2026，拟收录于 IOS Press *FAIA* 论文集）。
- **学术定位**：针对我国《个人信息保护法》第 28、29 条敏感个人信息“单独同意”在回顾性医学科研与医疗大模型训练中的实务困境，构建基于国标 GB/T 39725-2020（附录 G）、受控联邦差分隐私沙箱与法律级联承诺的三要件场景风险安全港。
- **先验假设与场景设定声明**：
  - 环境暴露系数（$\alpha_{\mathrm{env}}=0.25$）与组织控制系数（$\gamma_{\mathrm{org}}=0.72$）属于用于模拟受控零出域沙箱的情景假设（Scenario Assumptions），精确量化有赖于后续对泄漏路径重叠度与发生频次的实证数据；
  - 敏感性分析用于探索在替代输入组合下输出的变动规律，而非验证先验假设本身的客观真实性；
  - 安全港的确立采用**双重合取判定机制（Dual Conjunctive Test）**：必须同时满足三要件（$k_{\min} \ge 10$、差分隐私沙箱、级联承诺与PIA-IRB联审）**且**残余风险满足 $R_{\mathrm{res}} \le 0.04$；
  - 临床效用证伪标准严格定义为：在相同评估集上下游 macro ROC-AUC 相比无扰动基线**绝对下降超过 0.05**。
- **联系邮箱**：`3588@duck.com`（学术交流、仿真代码复现咨询）。

### 2. 双轨解耦治理判定与 v1.2.0 实证闭环更新
安全港不是单一数值计算器，而是“法定三要件 + 残余风险门槛”的双轨闭环：
1. **纯数值风险门槛（`meets_risk_threshold`）**：严格十进制评估 $\alpha \times \gamma \le \tau \times k$。消除浮点截断误差，恰好 $4.00\%$ 时判定达标；
2. **要件合规状态（`framework_requirements_status`）**：严格依凭表 2 准入要件。当小等价类样本（如罕见病 $k=5$）算得 $3.60\% \le 4.0\%$ 时，虽然数值通过，但要件状态明确返回 `failed`（因其违背了 $k_{\min} \ge 10$ 的法定最低泛化要求）；
3. **v1.2.0 核心更新（蒙特卡洛双重合取 + UCI 101,766 条实测闭环）**：
   - **蒙特卡洛双重合取修复**：在 10,000 次蒙特卡洛抽样中同时检验 $k_{\min} \ge 10$ 与 $R_{\mathrm{res}} \le 0.04$，真实双重合取达标率为 `75.08%`（见 `data/monte_carlo_results.csv`）；
   - **UCI Diabetes 130-US 真实临床实测（`benchmark_uci_diabetes.py`）**：接入 101,766 条就诊记录 / 71,518 名患者（5 折患者分组防泄露），完成 **E1**（6 准标识符 Mondrian $(k, l)$ 泛化，$k=10, l=3$ 精确复现 `1.80%` 基线）与 **E2**（逐样本 L2 裁剪 DP-SGD 与 Yeom 成员推理攻防，全队列最大绝对 AUC 降幅 `0.0177` 远低于 `0.05` 红线，局部高维子队列 $N=2,000$ 上局部 AUC 从 `0.6359` 降至 `0.5239` 且 Yeom 均值攻击优势从 `0.1566` 严格单调降至 `0.0187`）；
   - **文献与自动化质检**：清理旧版废弃示意图表，修正 GDPR 官方 EUR-Lex 链接，`test_sensitivity.py` 8/8 单元测试全绿。

---

<a name="日本語案内"></a>
## 日本語案内

### 1. 論文情報と研究概要
- **論文題目**: 中国個人情報保護法下におけるプライバシー保護医療健康データガバナンスおよびAI訓練のための計算可能なシナリオリスク・セーフハーバー研究
- **現在のステータス**: 査読改訂中（ICBAR 2026 投稿予定、IOS Press *FAIA* 収録予定）。
- **目的**: プライバシー保護工学と法解釈論を融合させた「シナリオリスク・セーフハーバー」の数理解析シミュレーションです。
- **連絡先**: `3588@duck.com`

---

## Repository Structure & Reproducibility Assets

```
icbar-2026-safe-harbor-simulation/
├── README.md                          # Trilingual comprehensive documentation (EN / ZH / JA)
├── REFERENCES.md                      # Complete annotated bibliography (25 core regulatory & academic works + dataset citation)
├── LICENSE                            # MIT License for source code
├── requirements.txt                   # Minimal Python runtime dependencies (numpy, pandas, scipy, scikit-learn, matplotlib, requests)
├── sensitivity_analysis.py            # Executable parameter grid sweep, stress testing & Monte Carlo
├── test_sensitivity.py                # Automated regression & assertion test suite (8 assertions)
├── benchmark_uci_diabetes.py          # UCI Diabetes 130-US empirical benchmark (E1 Mondrian + E2 DP-SGD & MIA)
├── data/
│   ├── cache/                         # Local git-ignored UCI 296 ZIP cache
│   ├── sensitivity_grid.csv           # 315-point multi-parameter grid with decoupled evaluation
│   ├── monte_carlo_results.csv        # 10,000-draw stochastic simulation logs (with conjunctive flags)
│   └── uci_diabetes_benchmark.csv     # Empirical E1 & E2 5-seed benchmark results
└── figures/
    ├── figure1_safe_harbor_architecture.png   # Tripartite safe harbor architecture & PIA-IRB co-governance
    ├── figure2_uci_benchmark.png              # Empirical E1 Mondrian (k, l) & E2 DP-SGD/MIA benchmark
    └── figure_sensitivity_surface.png         # Refined 3D response surface and density chart (Research Threshold)
```

## Citation, License & Contact
- Code: [MIT License](LICENSE)
- Data and Documentation: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- Citation: Please cite as "Simulation and Sensitivity Suite for Scenario-Risk Safe Harbor (Under Review)".
- Research Inquiries: `3588@duck.com`
