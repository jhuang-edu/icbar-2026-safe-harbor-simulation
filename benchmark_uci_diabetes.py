"""
Empirical Benchmark on UCI Diabetes 130-US (ID=296)
for ICBAR 2026: Scenario-Risk Safe Harbor under China's PIPL
Experiments:
  E1: Multidimensional Mondrian (k, l)-anonymity generalization on 6 quasi-identifiers
      and conjunctive safe harbor gate evaluation.
  E2: Vectorized per-sample clipped DP-SGD (Goodfellow 2015 norm decomposition +
      Mironov 2019 exact log-domain SGM RDP + Balle 2020 conversion + Brentq calibration)
      and Yeom (2018) loss-threshold membership inference attack (MIA) defense.

Outputs:
  - open_repo/data/uci_diabetes_benchmark.csv
  - open_repo/figures/figure2_uci_benchmark.png
  - ../figures/figure2_uci_benchmark.png (synchronized copy for manuscript build)
"""

import csv
import hashlib
import io
import os
import re
import shutil
import time
import zipfile
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from scipy.optimize import brentq
from scipy.special import gammaln, logsumexp
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

from sensitivity_analysis import (
    SimulationConfig,
    calculate_risk,
    meets_minimum_k,
    meets_risk_threshold,
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
FIG_DIR = os.path.join(BASE_DIR, "figures")
ROOT_FIG_DIR = os.path.join(os.path.dirname(BASE_DIR), "figures")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# UCI Diabetes 130-US (ID=296) verified fingerprint constants
UCI_296_URL = (
    "https://archive.ics.uci.edu/static/public/296/"
    "diabetes+130-us+hospitals+for+years+1999-2008.zip"
)
UCI_296_ZIP_SHA256 = (
    "f82ac129da2ddd2299391ff6fbae3a6a58b3edcf59ac9d7bd480c00fe453112a"
)
UCI_296_CSV_SHA256 = (
    "0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97"
)

# Experiment protocol constants
SEEDS = [42, 43, 44, 45, 46]
QI_COLS = [
    "age",
    "gender",
    "race_clean",
    "admission_type_id",
    "discharge_disposition_id",
    "admission_source_id",
]
AGE_ORDER = [
    "[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
    "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)",
]
NUM_CLINICAL_COLS = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
]
SKEWED_COUNT_COLS = [
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
]
MED_COLS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
    "insulin", "glyburide-metformin", "glipizide-metformin",
    "glimepiride-pioglitazone", "metformin-rosiglitazone",
    "metformin-pioglitazone",
]
CLINICAL_CAT_COLS = ["A1Cresult", "max_glu_serum", "change", "diabetesMed"] + MED_COLS
DROP_COLS = ["weight", "payer_code", "medical_specialty", "examide", "citoglipton"]
ICD9_NAMES = [
    "Circulatory", "Respiratory", "Digestive", "Diabetes",
    "Injury", "Musculoskeletal", "Genitourinary", "Neoplasms", "Other",
]

EPSILONS = [float("inf"), 4.0, 2.0, 1.0, 0.5]
DELTA = 1e-5
LOCAL_COHORT_N = 2000


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_uci_diabetes_df(cache_dir: str = CACHE_DIR) -> pd.DataFrame:
    """Download (or load cached) UCI Diabetes 130-US dataset with SHA-256 verification."""
    zip_path = os.path.join(cache_dir, "diabetes_130_us.zip")
    need_download = True
    if os.path.exists(zip_path):
        if sha256_file(zip_path) == UCI_296_ZIP_SHA256:
            need_download = False
        else:
            print("[WARN] Cached zip SHA-256 mismatch; re-downloading UCI ID=296.")

    if need_download:
        print(f"Downloading UCI Diabetes 130-US (ID=296) -> {zip_path}")
        resp = requests.get(UCI_296_URL, timeout=90)
        resp.raise_for_status()
        raw_bytes = resp.content
        actual_zip_hash = sha256_bytes(raw_bytes)
        if actual_zip_hash != UCI_296_ZIP_SHA256:
            raise ValueError(
                f"ZIP SHA-256 mismatch: expected {UCI_296_ZIP_SHA256}, got {actual_zip_hash}"
            )
        tmp_path = zip_path + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(raw_bytes)
        os.replace(tmp_path, zip_path)
    else:
        print(f"Loaded verified cached UCI dataset -> {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_bytes = zf.read("diabetic_data.csv")
    actual_csv_hash = sha256_bytes(csv_bytes)
    if actual_csv_hash != UCI_296_CSV_SHA256:
        raise ValueError(
            f"CSV SHA-256 mismatch: expected {UCI_296_CSV_SHA256}, got {actual_csv_hash}"
        )

    # keep_default_na=False prevents 'None' in max_glu_serum/A1Cresult from becoming NaN
    df = pd.read_csv(io.BytesIO(csv_bytes), dtype=str, keep_default_na=False)
    assert len(df) == 101766, f"Expected 101766 records, got {len(df)}"
    assert df["patient_nbr"].nunique() == 71518, "Unexpected unique patient count"
    return df


def map_icd9_9cat(code: str) -> int:
    """Map raw ICD-9 diagnosis code to Strack et al. (2014) 9 clinical categories (0..8)."""
    s = str(code).strip()
    if not s or s == "?" or s.startswith(("V", "E", "v", "e")):
        return 8
    try:
        v = int(float(s))
    except ValueError:
        return 8
    if (390 <= v <= 459) or v == 785:
        return 0
    if (460 <= v <= 519) or v == 786:
        return 1
    if (520 <= v <= 579) or v == 787:
        return 2
    if v == 250:
        return 3
    if 800 <= v <= 999:
        return 4
    if 710 <= v <= 739:
        return 5
    if (580 <= v <= 629) or v == 788:
        return 6
    if 140 <= v <= 239:
        return 7
    return 8


def prepare_base_dataframe(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[int], list[int]]:
    """Clean fields, map ICD-9 categories, encode 6 QIs, and extract binary target and groups."""
    df = raw_df.copy()
    df["race_clean"] = df["race"].replace("?", "Missing")

    for dcol in ["diag_1", "diag_2", "diag_3"]:
        df[f"{dcol}_cat"] = df[dcol].map(map_icd9_9cat).astype(np.int64)
        df[f"{dcol}_grp"] = df[f"{dcol}_cat"].map(lambda idx: ICD9_NAMES[idx])

    # Encode 6 QIs to compact integer domain indices
    age_map = {v: i for i, v in enumerate(AGE_ORDER)}
    df["qi_0"] = df["age"].map(age_map).astype(np.int64)
    d_sizes = [len(AGE_ORDER)]

    for j, col in enumerate(QI_COLS[1:], start=1):
        cats = sorted(df[col].unique().tolist())
        cmap = {v: i for i, v in enumerate(cats)}
        df[f"qi_{j}"] = df[col].map(cmap).astype(np.int64)
        d_sizes.append(len(cats))

    assert d_sizes == [10, 3, 6, 8, 26, 17], f"Unexpected QI domain sizes: {d_sizes}"

    y = (df["readmitted"] != "NO").astype(np.int32).to_numpy()
    groups = df["patient_nbr"].to_numpy()
    sa = df["diag_1_cat"].to_numpy()
    return df, y, groups, sa, d_sizes


# ==============================================================================
# E1: Multidimensional Mondrian (k, l)-Anonymity
# ==============================================================================

@dataclass
class MondrianLeafSummary:
    leaf_id: int
    n_records: int
    l_diversity: int
    age_min: int
    age_max: int
    cat_sets: list
    cat_probs: list
    ncp: float


@dataclass
class MondrianNode:
    leaf_id: int | None = None
    split_dim: int | None = None
    split_threshold: int | None = None
    split_left_set: frozenset | None = None
    left: "MondrianNode | None" = None
    right: "MondrianNode | None" = None
    summary: MondrianLeafSummary | None = None


def compute_leaf_ncp(x_sub: np.ndarray, d_sizes: list[int]) -> float:
    """Normalized Certainty Penalty averaged across the 6 QIs."""
    span0 = float(x_sub[:, 0].max() - x_sub[:, 0].min()) / float(d_sizes[0] - 1)
    total = span0
    for j in range(1, 6):
        n_uniq = len(np.unique(x_sub[:, j]))
        total += float(n_uniq - 1) / float(d_sizes[j] - 1)
    return total / 6.0


def build_mondrian_tree(
    x_qi: np.ndarray,
    sa: np.ndarray,
    d_sizes: list[int],
    k_req: int,
    l_req: int,
) -> tuple[MondrianNode, list[MondrianLeafSummary]]:
    """Fit strict multidimensional Mondrian (k, l)-anonymous partition tree."""
    if len(x_qi) < k_req or len(np.unique(sa)) < l_req:
        raise ValueError("Root partition fails baseline (k, l) feasibility.")

    leaves: list[MondrianLeafSummary] = []

    def is_valid_sub(sub_idx: np.ndarray) -> bool:
        if len(sub_idx) < k_req:
            return False
        return len(np.unique(sa[sub_idx])) >= l_req

    def make_leaf(idx: np.ndarray) -> MondrianNode:
        sub = x_qi[idx]
        l_div = int(len(np.unique(sa[idx])))
        age_min = int(sub[:, 0].min())
        age_max = int(sub[:, 0].max())
        cat_sets = []
        cat_probs = []
        n_rec = len(idx)
        for j in range(1, 6):
            vals, counts = np.unique(sub[:, j], return_counts=True)
            cat_sets.append(set(int(v) for v in vals))
            probs = np.zeros(d_sizes[j], dtype=np.float64)
            probs[vals] = counts / float(n_rec)
            cat_probs.append(probs)
        ncp_val = compute_leaf_ncp(sub, d_sizes)
        lid = len(leaves)
        summary = MondrianLeafSummary(
            leaf_id=lid,
            n_records=n_rec,
            l_diversity=l_div,
            age_min=age_min,
            age_max=age_max,
            cat_sets=cat_sets,
            cat_probs=cat_probs,
            ncp=ncp_val,
        )
        leaves.append(summary)
        return MondrianNode(leaf_id=lid, summary=summary)

    def split_recursive(idx: np.ndarray) -> MondrianNode:
        n_cur = len(idx)
        if n_cur < 2 * k_req:
            return make_leaf(idx)

        sub = x_qi[idx]
        spans = []
        span0 = float(sub[:, 0].max() - sub[:, 0].min()) / float(d_sizes[0] - 1)
        if span0 > 0.0:
            spans.append((-span0, 0))
        for j in range(1, 6):
            n_uniq = len(np.unique(sub[:, j]))
            sp = float(n_uniq - 1) / float(d_sizes[j] - 1)
            if sp > 0.0:
                spans.append((-sp, j))
        spans.sort()

        for _, dim in spans:
            col = sub[:, dim]
            if dim == 0:
                u_vals, counts = np.unique(col, return_counts=True)
                if len(u_vals) < 2:
                    continue
                cum = np.cumsum(counts[:-1])
                target = n_cur / 2.0
                cand_order = np.argsort(np.abs(cum - target), kind="mergesort")
                for pos in cand_order:
                    thresh = int(u_vals[pos])
                    mask = col <= thresh
                    left_idx = idx[mask]
                    right_idx = idx[~mask]
                    if is_valid_sub(left_idx) and is_valid_sub(right_idx):
                        return MondrianNode(
                            split_dim=0,
                            split_threshold=thresh,
                            left=split_recursive(left_idx),
                            right=split_recursive(right_idx),
                        )
            else:
                u_vals, counts = np.unique(col, return_counts=True)
                if len(u_vals) < 2:
                    continue
                order = np.argsort(-counts, kind="mergesort")
                left_set = set()
                right_set = set()
                c_left = 0
                c_right = 0
                for pos in order:
                    val = int(u_vals[pos])
                    cnt = int(counts[pos])
                    if not left_set:
                        left_set.add(val)
                        c_left += cnt
                    elif not right_set:
                        right_set.add(val)
                        c_right += cnt
                    elif c_left <= c_right:
                        left_set.add(val)
                        c_left += cnt
                    else:
                        right_set.add(val)
                        c_right += cnt
                f_left = frozenset(left_set)
                mask = np.isin(col, list(f_left))
                left_idx = idx[mask]
                right_idx = idx[~mask]
                if is_valid_sub(left_idx) and is_valid_sub(right_idx):
                    return MondrianNode(
                        split_dim=dim,
                        split_left_set=f_left,
                        left=split_recursive(left_idx),
                        right=split_recursive(right_idx),
                    )

        return make_leaf(idx)

    root = split_recursive(np.arange(len(x_qi), dtype=np.int64))
    for lf in leaves:
        assert lf.n_records >= k_req, f"Leaf {lf.leaf_id} violates k>={k_req}"
        assert lf.l_diversity >= l_req, f"Leaf {lf.leaf_id} violates l>={l_req}"
    return root, leaves


def route_mondrian_features(
    root: MondrianNode,
    x_qi: np.ndarray,
    d_sizes: list[int],
) -> np.ndarray:
    """Deterministically route records to Mondrian leaves and emit indistinguishable QI features."""
    feat_dim = 2 + sum(d_sizes[1:])  # 2 + (3 + 6 + 8 + 26 + 17) = 62
    out = np.zeros((len(x_qi), feat_dim), dtype=np.float64)

    def _route(node: MondrianNode, idx: np.ndarray) -> None:
        if len(idx) == 0:
            return
        if node.leaf_id is not None:
            s = node.summary
            age_mid = ((s.age_min + s.age_max) / 2.0 - 4.5) / 3.0
            age_width = (s.age_max - s.age_min) / 9.0
            vec = np.concatenate([[age_mid, age_width]] + s.cat_probs)
            out[idx] = vec
            return
        col = x_qi[idx, node.split_dim]
        if node.split_dim == 0:
            mask = col <= node.split_threshold
        else:
            mask = np.isin(col, list(node.split_left_set))
        _route(node.left, idx[mask])
        _route(node.right, idx[~mask])

    _route(root, np.arange(len(x_qi), dtype=np.int64))
    return out


def evaluate_raw_partition(
    x_qi: np.ndarray,
    sa: np.ndarray,
    sim_cfg: SimulationConfig,
) -> dict:
    """Evaluate ungeneralized Raw equivalence classes defined by exact 6-QI tuples."""
    # Pack 6 columns into structured bytes for fast exact grouping
    _, inv, counts = np.unique(x_qi, axis=0, return_inverse=True, return_counts=True)
    n_total = len(x_qi)
    n_classes = len(counts)
    k_min = int(counts.min())
    # Compute l_diversity per raw equivalence class
    order = np.argsort(inv, kind="mergesort")
    sorted_inv = inv[order]
    sorted_sa = sa[order]
    split_pts = np.flatnonzero(np.diff(sorted_inv)) + 1
    sa_groups = np.split(sorted_sa, split_pts)
    l_min = int(min(len(np.unique(g)) for g in sa_groups))

    r_res = calculate_risk(k_min, sim_cfg.alpha_base, sim_cfg.gamma_base)
    passes = (
        meets_minimum_k(k_min, sim_cfg.k_min_threshold)
        and meets_risk_threshold(k_min, sim_cfg.alpha_base, sim_cfg.gamma_base, sim_cfg.tau_safe)
    )
    return {
        "k_min": k_min,
        "l_min": l_min,
        "num_classes": float(n_classes),
        "ncp": 0.0,
        "p_link_max": 1.0 / float(k_min),
        "p_link_avg": float(n_classes) / float(n_total),
        "r_res": r_res,
        "passes_gate": bool(passes),
    }


def evaluate_mondrian_partition(
    x_qi: np.ndarray,
    sa: np.ndarray,
    d_sizes: list[int],
    k_req: int,
    l_req: int,
    sim_cfg: SimulationConfig,
) -> tuple[MondrianNode, dict]:
    """Fit Mondrian (k, l) tree and evaluate risk & NCP metrics."""
    root, leaves = build_mondrian_tree(x_qi, sa, d_sizes, k_req, l_req)
    n_total = len(x_qi)
    n_classes = len(leaves)
    k_min = min(lf.n_records for lf in leaves)
    l_min = min(lf.l_diversity for lf in leaves)
    ncp_val = sum(lf.n_records * lf.ncp for lf in leaves) / float(n_total)
    r_res = calculate_risk(k_min, sim_cfg.alpha_base, sim_cfg.gamma_base)
    passes = (
        meets_minimum_k(k_min, sim_cfg.k_min_threshold)
        and meets_risk_threshold(k_min, sim_cfg.alpha_base, sim_cfg.gamma_base, sim_cfg.tau_safe)
        and (l_min >= l_req)
    )
    stats = {
        "k_min": int(k_min),
        "l_min": int(l_min),
        "num_classes": float(n_classes),
        "ncp": float(ncp_val),
        "p_link_max": 1.0 / float(k_min),
        "p_link_avg": float(n_classes) / float(n_total),
        "r_res": float(r_res),
        "passes_gate": bool(passes),
    }
    return root, stats


def run_e1_experiments(
    df: pd.DataFrame,
    sa: np.ndarray,
    groups: np.ndarray,
    d_sizes: list[int],
    sim_cfg: SimulationConfig,
) -> tuple[list[dict], dict[int, MondrianNode]]:
    """Run E1 across 5 patient-grouped training folds + full-cohort reference."""
    x_qi = df[[f"qi_{j}" for j in range(6)]].to_numpy()
    settings = [
        ("Raw", None, None),
        ("Mondrian_k5_l3", 5, 3),
        ("Mondrian_k10_l3", 10, 3),
        ("Mondrian_k20_l3", 20, 3),
    ]

    # Full-cohort reference audit
    full_ref = {}
    for name, k_req, l_req in settings:
        if k_req is None:
            full_ref[name] = evaluate_raw_partition(x_qi, sa, sim_cfg)
        else:
            _, st = evaluate_mondrian_partition(x_qi, sa, d_sizes, k_req, l_req, sim_cfg)
            full_ref[name] = st
        print(
            f"[E1 Full-Cohort Ref] {name:<16} | |Q|={full_ref[name]['num_classes']:>6.0f} | "
            f"k_min={full_ref[name]['k_min']:>2d} | l_min={full_ref[name]['l_min']} | "
            f"NCP={full_ref[name]['ncp']:.4f} | R_res={full_ref[name]['r_res']:.4f} | "
            f"passes_gate={full_ref[name]['passes_gate']}"
        )

    # 5-seed patient-grouped training folds (leakage-free)
    fold_records: dict[str, list[dict]] = {s[0]: [] for s in settings}
    k10_trees_by_seed: dict[int, MondrianNode] = {}

    for seed in SEEDS:
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        tr_idx, te_idx = next(gss.split(x_qi, groups=groups))
        assert len(set(groups[tr_idx]).intersection(set(groups[te_idx]))) == 0
        x_tr = x_qi[tr_idx]
        sa_tr = sa[tr_idx]

        for name, k_req, l_req in settings:
            if k_req is None:
                st = evaluate_raw_partition(x_tr, sa_tr, sim_cfg)
            else:
                tree, st = evaluate_mondrian_partition(
                    x_tr, sa_tr, d_sizes, k_req, l_req, sim_cfg
                )
                if k_req == 10 and l_req == 3:
                    k10_trees_by_seed[seed] = tree
                    # Verify 100% deterministic routing of test fold
                    te_feat = route_mondrian_features(tree, x_qi[te_idx], d_sizes)
                    assert np.isfinite(te_feat).all()
            fold_records[name].append(st)

    e1_rows = []
    for name, k_req, l_req in settings:
        recs = fold_records[name]
        k_min = min(r["k_min"] for r in recs)
        l_min = min(r["l_min"] for r in recs)
        num_classes = float(np.mean([r["num_classes"] for r in recs]))
        ncp_mean = float(np.mean([r["ncp"] for r in recs]))
        ncp_std = float(np.std([r["ncp"] for r in recs]))
        p_link_max = 1.0 / float(k_min)
        p_link_avg = float(np.mean([r["p_link_avg"] for r in recs]))
        r_res = calculate_risk(k_min, sim_cfg.alpha_base, sim_cfg.gamma_base)
        passes = (
            meets_minimum_k(k_min, sim_cfg.k_min_threshold)
            and meets_risk_threshold(
                k_min, sim_cfg.alpha_base, sim_cfg.gamma_base, sim_cfg.tau_safe
            )
            and (l_min >= (l_req if l_req is not None else 1))
        )
        print(
            f"[E1 5-Fold Train]    {name:<16} | |Q|={num_classes:>6.1f} | "
            f"k_min={k_min:>2d} | l_min={l_min} | NCP={ncp_mean:.4f}+-{ncp_std:.4f} | "
            f"R_res={r_res:.4f} | passes_gate={passes}"
        )
        e1_rows.append({
            "experiment": "E1",
            "setting": name,
            "dataset_records": len(df),
            "unique_patients": int(df["patient_nbr"].nunique()),
            "k_min": k_min,
            "l_min": l_min,
            "num_classes": round(num_classes, 2),
            "ncp_mean": round(ncp_mean, 6),
            "ncp_std": round(ncp_std, 6),
            "p_link_max": round(p_link_max, 6),
            "p_link_avg": round(p_link_avg, 6),
            "r_res": round(r_res, 6),
            "passes_gate": bool(passes),
            "epsilon": "",
            "delta": "",
            "auc_mean": "",
            "auc_std": "",
            "delta_auc_vs_inf": "",
            "mia_adv_mean": "",
            "mia_adv_std": "",
            "mia_local_adv_mean": "",
            "mia_local_adv_std": "",
            "seeds": ",".join(str(s) for s in SEEDS),
            "sigma_noise": "",
            "sigma_local": "",
            "clip_norm": "",
            "passes_condition2": "",
            "auc_raw_inf_mean": "",
            "delta_auc_vs_raw": "",
            "mia_yeom_mean_adv": "",
            "mia_local_yeom_mean_adv": "",
            "local_cohort_n": "",
            "local_auc_mean": "",
            "local_auc_std": "",
            "full_cohort_num_classes": int(full_ref[name]["num_classes"]),
            "full_cohort_ncp": round(full_ref[name]["ncp"], 6),
        })

    return e1_rows, k10_trees_by_seed


# ==============================================================================
# E2: Exact RDP Accountant + Vectorized Per-Sample Clipped DP-SGD + Yeom MIA
# ==============================================================================

def compute_rdp_sgm_step(q: float, sigma: float, alphas: np.ndarray) -> np.ndarray:
    """
    Exact log-domain single-step RDP for Poisson-subsampled Gaussian mechanism
    (Mironov, Talwar, Zhang, 2019, add/remove adjacency).
    """
    log_q = np.log(q)
    log_1mq = np.log1p(-q)
    inv_2s2 = 1.0 / (2.0 * sigma * sigma)
    out = np.empty(len(alphas), dtype=np.float64)
    for idx, alpha in enumerate(alphas):
        a = int(alpha)
        ks = np.arange(a + 1, dtype=np.float64)
        log_binom = gammaln(a + 1.0) - gammaln(ks + 1.0) - gammaln(a - ks + 1.0)
        log_terms = (
            log_binom
            + (a - ks) * log_1mq
            + ks * log_q
            + ks * (ks - 1.0) * inv_2s2
        )
        out[idx] = logsumexp(log_terms) / float(a - 1)
    return out


def rdp_to_dp(alphas: np.ndarray, rdp_total: np.ndarray, delta: float) -> tuple[float, int]:
    """Convert RDP curve to tightest (epsilon, delta)-DP (Balle et al., 2020)."""
    log_inv_delta = np.log(1.0 / delta)
    a_float = alphas.astype(np.float64)
    eps_arr = (
        rdp_total
        + log_inv_delta / (a_float - 1.0)
        + np.log1p(-1.0 / a_float)
        - np.log(a_float) / (a_float - 1.0)
    )
    best_idx = int(np.argmin(eps_arr))
    return float(eps_arr[best_idx]), int(alphas[best_idx])


def calibrate_noise_multiplier(
    target_eps: float,
    delta: float,
    q: float,
    total_steps: int,
) -> tuple[float, float, int]:
    """Invert exact RDP accountant via Brentq to match target (epsilon, delta)."""
    if not np.isfinite(target_eps):
        return 0.0, float("inf"), 0
    alphas = np.arange(2, 201, dtype=np.int64)

    def objective(sigma: float) -> float:
        rdp_step = compute_rdp_sgm_step(q, sigma, alphas)
        eps_spent, _ = rdp_to_dp(alphas, total_steps * rdp_step, delta)
        return eps_spent - target_eps

    lo, hi = 0.25, 10.0
    while objective(hi) > 0.0:
        hi *= 2.0
    while objective(lo) < 0.0 and lo > 0.02:
        lo *= 0.5
    sigma_sol = float(brentq(objective, lo, hi, xtol=1e-6, rtol=1e-6))
    eps_ver, best_alpha = rdp_to_dp(
        alphas, total_steps * compute_rdp_sgm_step(q, sigma_sol, alphas), delta
    )
    assert abs(eps_ver - target_eps) < 1e-3, (
        f"RDP calibration drift: target={target_eps}, verified={eps_ver}"
    )
    assert 2 < best_alpha < 200, f"Optimal alpha hit boundary: {best_alpha}"
    return sigma_sol, eps_ver, best_alpha


def train_tanh_mlp_dpsgd(
    x_tr: np.ndarray,
    y_tr: np.ndarray,
    hidden_dim: int,
    batch_size: int,
    epochs: int,
    lr: float,
    clip_norm: float,
    sigma_noise: float,
    l2_reg: float,
    seed: int,
    apply_dp: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized 1-hidden-layer tanh MLP trained via Goodfellow (2015) norm-decomposed
    per-sample clipped DP-SGD under Poisson subsampling.
    """
    rng = np.random.default_rng(seed)
    n_tr, d_in = x_tr.shape

    w1 = rng.normal(0.0, 1.0 / np.sqrt(d_in), size=(d_in, hidden_dim))
    b1 = np.zeros(hidden_dim, dtype=np.float64)
    w2 = rng.normal(0.0, 1.0 / np.sqrt(hidden_dim), size=(hidden_dim, 1))
    b2 = np.zeros(1, dtype=np.float64)

    q = float(batch_size) / float(n_tr)
    steps_per_epoch = max(1, int(round(float(n_tr) / float(batch_size))))
    total_steps = epochs * steps_per_epoch

    for _ in range(total_steps):
        mask = rng.random(n_tr) < q
        if not np.any(mask):
            continue
        xb = x_tr[mask]
        yb = y_tr[mask].reshape(-1, 1)

        # Forward pass
        a1 = xb @ w1 + b1
        h = np.tanh(a1)
        z = h @ w2 + b2
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -35.0, 35.0)))

        # Per-sample backward errors
        delta2 = p - yb  # (m, 1)
        delta1 = (delta2 @ w2.T) * (1.0 - h * h)  # (m, H)

        if apply_dp:
            # Exact per-sample L2 gradient norm via rank-1 Frobenius norm identity
            xb_sq = np.sum(xb * xb, axis=1)
            d1_sq = np.sum(delta1 * delta1, axis=1)
            h_sq = np.sum(h * h, axis=1)
            d2_sq = delta2[:, 0] ** 2
            grad_norms = np.sqrt(
                xb_sq * d1_sq + d1_sq + d2_sq * h_sq + d2_sq + 1e-18
            )
            scales = np.minimum(1.0, clip_norm / np.maximum(grad_norms, 1e-12))
            d1_scaled = delta1 * scales[:, None]
            d2_scaled = delta2 * scales[:, None]

            sum_dw1 = xb.T @ d1_scaled
            sum_db1 = np.sum(d1_scaled, axis=0)
            sum_dw2 = h.T @ d2_scaled
            sum_db2 = np.sum(d2_scaled, axis=0)

            noise_std = sigma_noise * clip_norm
            gw1 = (sum_dw1 + rng.normal(0.0, noise_std, size=w1.shape)) / float(batch_size)
            gb1 = (sum_db1 + rng.normal(0.0, noise_std, size=b1.shape)) / float(batch_size)
            gw2 = (sum_dw2 + rng.normal(0.0, noise_std, size=w2.shape)) / float(batch_size)
            gb2 = (sum_db2 + rng.normal(0.0, noise_std, size=b2.shape)) / float(batch_size)
        else:
            m_b = float(len(xb))
            gw1 = (xb.T @ delta1) / m_b
            gb1 = np.sum(delta1, axis=0) / m_b
            gw2 = (h.T @ delta2) / m_b
            gb2 = np.sum(delta2, axis=0) / m_b

        if l2_reg > 0.0:
            gw1 = gw1 + l2_reg * w1
            gw2 = gw2 + l2_reg * w2

        w1 -= lr * gw1
        b1 -= lr * gb1
        w2 -= lr * gw2
        b2 -= lr * gb2

    return w1, b1, w2, b2


def predict_logits_and_losses(
    x: np.ndarray,
    y: np.ndarray,
    params: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    """Compute predicted probabilities and per-sample BCE losses."""
    w1, b1, w2, b2 = params
    h = np.tanh(x @ w1 + b1)
    z = (h @ w2 + b2).ravel()
    probs = 1.0 / (1.0 + np.exp(-np.clip(z, -35.0, 35.0)))
    losses = np.logaddexp(0.0, z) - y.astype(np.float64) * z
    return probs, losses


def compute_yeom_mia_metrics(
    loss_tr: np.ndarray,
    loss_te: np.ndarray,
) -> tuple[float, float]:
    """
    Compute Yeom et al. (2018) loss-threshold MIA metrics:
      1. adv_max: exact max_tau (TPR(tau) - FPR(tau)) evaluated at unique loss cutoffs
      2. adv_mean: TPR(mean_tr_loss) - FPR(mean_tr_loss)
    """
    # Yeom unsupervised training-mean threshold advantage
    tau_mean = float(np.mean(loss_tr))
    tpr_mean = float(np.mean(loss_tr <= tau_mean))
    fpr_mean = float(np.mean(loss_te <= tau_mean))
    adv_mean = tpr_mean - fpr_mean

    # Exact max_tau (TPR - FPR) scanning ascending losses (equivalent to l <= tau)
    all_losses = np.concatenate([loss_tr, loss_te])
    is_member = np.concatenate([
        np.ones(len(loss_tr), dtype=np.float64),
        np.zeros(len(loss_te), dtype=np.float64),
    ])
    order = np.argsort(all_losses, kind="mergesort")
    sorted_losses = all_losses[order]
    sorted_m = is_member[order]

    cum_tp = np.cumsum(sorted_m)
    cum_fp = np.cumsum(1.0 - sorted_m)
    # Only evaluate at the end of each tied-loss block to enforce strict l <= tau
    is_block_end = np.empty(len(sorted_losses), dtype=bool)
    is_block_end[:-1] = sorted_losses[:-1] != sorted_losses[1:]
    is_block_end[-1] = True

    tprs = cum_tp[is_block_end] / float(len(loss_tr))
    fprs = cum_fp[is_block_end] / float(len(loss_te))
    adv_max = float(max(0.0, np.max(tprs - fprs)))
    return adv_max, adv_mean


def build_safe_harbor_features(
    df: pd.DataFrame,
    tr_idx: np.ndarray,
    te_idx: np.ndarray,
    mondrian_tree: MondrianNode,
    d_sizes: list[int],
    include_raw_qi: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Construct leakage-free train/test feature matrices (Safe Harbor or Raw QI)."""
    tr_df = df.iloc[tr_idx]
    te_df = df.iloc[te_idx]

    if not include_raw_qi:
        x_qi = df[[f"qi_{j}" for j in range(6)]].to_numpy()
        qi_tr = route_mondrian_features(mondrian_tree, x_qi[tr_idx], d_sizes)
        qi_te = route_mondrian_features(mondrian_tree, x_qi[te_idx], d_sizes)
    else:
        qi_raw_cols = QI_COLS
        qi_tr_df = pd.get_dummies(tr_df[qi_raw_cols].astype(str), dtype=np.float64)
        qi_te_df = pd.get_dummies(te_df[qi_raw_cols].astype(str), dtype=np.float64).reindex(
            columns=qi_tr_df.columns, fill_value=0.0
        )
        qi_tr = qi_tr_df.to_numpy()
        qi_te = qi_te_df.to_numpy()

    # 8 clinical numerical features (log1p for skewed visit counts + train Z-score)
    num_tr_df = tr_df[NUM_CLINICAL_COLS].astype(np.float64).copy()
    num_te_df = te_df[NUM_CLINICAL_COLS].astype(np.float64).copy()
    for col in SKEWED_COUNT_COLS:
        num_tr_df[col] = np.log1p(num_tr_df[col])
        num_te_df[col] = np.log1p(num_te_df[col])
    mu = num_tr_df.mean(axis=0)
    sd = num_tr_df.std(axis=0).replace(0.0, 1.0)
    num_tr = ((num_tr_df - mu) / sd).to_numpy()
    num_te = ((num_te_df - mu) / sd).to_numpy()

    # 9-category diagnoses + clinical labs/medications One-Hot (Pandas 4 warning-free)
    cat_cols = ["diag_1_grp", "diag_2_grp", "diag_3_grp"] + CLINICAL_CAT_COLS
    cat_tr_df = pd.get_dummies(tr_df[cat_cols].astype(str), dtype=np.float64)
    cat_te_df = pd.get_dummies(te_df[cat_cols].astype(str), dtype=np.float64).reindex(
        columns=cat_tr_df.columns, fill_value=0.0
    )

    x_tr = np.hstack([qi_tr, num_tr, cat_tr_df.to_numpy()])
    x_te = np.hstack([qi_te, num_te, cat_te_df.to_numpy()])
    return x_tr, x_te


def build_local_overfit_features(
    df: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Construct N=2,000 ungeneralized high-dimensional local subcohort (80/20 patient-grouped)."""
    rng = np.random.default_rng(seed)
    sub_idx = rng.choice(len(df), size=LOCAL_COHORT_N, replace=False)
    sub_df = df.iloc[sub_idx].reset_index(drop=True)
    y_sub = y[sub_idx]
    g_sub = groups[sub_idx]

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    tr_idx, te_idx = next(gss.split(sub_df, groups=g_sub))
    assert len(set(g_sub[tr_idx]).intersection(set(g_sub[te_idx]))) == 0

    tr_df = sub_df.iloc[tr_idx]
    te_df = sub_df.iloc[te_idx]

    # Numerical features: age_rank + 8 clinical numerical columns
    num_cols = ["qi_0"] + NUM_CLINICAL_COLS
    num_tr_df = tr_df[num_cols].astype(np.float64).copy()
    num_te_df = te_df[num_cols].astype(np.float64).copy()
    for col in SKEWED_COUNT_COLS:
        num_tr_df[col] = np.log1p(num_tr_df[col])
        num_te_df[col] = np.log1p(num_te_df[col])
    mu = num_tr_df.mean(axis=0)
    sd = num_tr_df.std(axis=0).replace(0.0, 1.0)
    num_tr = ((num_tr_df - mu) / sd).to_numpy()
    num_te = ((num_te_df - mu) / sd).to_numpy()

    # Ungeneralized high-cardinality categorical columns (raw QIs, diag_1/2/3, specialty, meds)
    high_cat_cols = (
        QI_COLS[1:]
        + ["medical_specialty", "diag_1", "diag_2", "diag_3"]
        + CLINICAL_CAT_COLS
    )
    cat_tr_df = pd.get_dummies(tr_df[high_cat_cols].astype(str), dtype=np.float64)
    cat_te_df = pd.get_dummies(te_df[high_cat_cols].astype(str), dtype=np.float64).reindex(
        columns=cat_tr_df.columns, fill_value=0.0
    )

    x_tr = np.hstack([num_tr, cat_tr_df.to_numpy()])
    x_te = np.hstack([num_te, cat_te_df.to_numpy()])
    return x_tr, y_sub[tr_idx], x_te, y_sub[te_idx]


def run_e2_experiments(
    df: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    d_sizes: list[int],
    k10_trees_by_seed: dict[int, MondrianNode],
    e1_k10_row: dict,
) -> list[dict]:
    """Run E2 across 5 seeds on Main Safe Harbor cohort and Local Overfit subcohort."""
    # Main cohort hyperparameters
    h_main, b_main, ep_main, lr_main, c_main, l2_main = 32, 512, 18, 0.25, 1.5, 1e-4
    # Local high-dimensional subcohort hyperparameters
    h_loc, b_loc, ep_loc, lr_loc, c_loc, l2_loc = 64, 128, 100, 0.40, 2.0, 0.0

    main_res = {eps: {"auc": [], "mia_max": [], "mia_mean": [], "sigma": []} for eps in EPSILONS}
    local_res = {eps: {"auc": [], "mia_max": [], "mia_mean": [], "sigma": []} for eps in EPSILONS}
    raw_inf_aucs = []

    for seed in SEEDS:
        t0 = time.perf_counter()
        gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        tr_idx, te_idx = next(gss.split(df, groups=groups))

        # 1. Main Safe Harbor feature space (Mondrian k=10, l=3)
        x_tr, x_te = build_safe_harbor_features(
            df, tr_idx, te_idx, k10_trees_by_seed[seed], d_sizes, include_raw_qi=False
        )
        y_tr, y_te = y[tr_idx], y[te_idx]

        # Raw QI ungeneralized eps=inf baseline for two-stage utility comparison
        x_raw_tr, x_raw_te = build_safe_harbor_features(
            df, tr_idx, te_idx, k10_trees_by_seed[seed], d_sizes, include_raw_qi=True
        )
        p_raw = train_tanh_mlp_dpsgd(
            x_raw_tr, y_tr, h_main, b_main, ep_main, lr_main, c_main, 0.0, l2_main,
            seed=seed * 100 + 99, apply_dp=False
        )
        prob_raw_te, _ = predict_logits_and_losses(x_raw_te, y_te, p_raw)
        raw_inf_aucs.append(float(roc_auc_score(y_te, prob_raw_te)))

        # 2. Local high-dimensional ungeneralized subcohort (N=2,000)
        xl_tr, yl_tr, xl_te, yl_te = build_local_overfit_features(df, y, groups, seed)

        q_main = float(b_main) / float(len(x_tr))
        steps_main = ep_main * max(1, int(round(float(len(x_tr)) / float(b_main))))
        q_loc = float(b_loc) / float(len(xl_tr))
        steps_loc = ep_loc * max(1, int(round(float(len(xl_tr)) / float(b_loc))))

        for idx_eps, eps in enumerate(EPSILONS):
            is_dp = np.isfinite(eps)
            if is_dp:
                sig_m, _, _ = calibrate_noise_multiplier(eps, DELTA, q_main, steps_main)
                sig_l, _, _ = calibrate_noise_multiplier(eps, DELTA, q_loc, steps_loc)
            else:
                sig_m, sig_l = 0.0, 0.0

            # Train & evaluate Main Safe Harbor cohort
            pm = train_tanh_mlp_dpsgd(
                x_tr, y_tr, h_main, b_main, ep_main, lr_main, c_main, sig_m, l2_main,
                seed=seed * 100 + idx_eps, apply_dp=is_dp
            )
            _, loss_m_tr = predict_logits_and_losses(x_tr, y_tr, pm)
            prob_m_te, loss_m_te = predict_logits_and_losses(x_te, y_te, pm)
            auc_m = float(roc_auc_score(y_te, prob_m_te))
            adv_m_max, adv_m_mean = compute_yeom_mia_metrics(loss_m_tr, loss_m_te)
            main_res[eps]["auc"].append(auc_m)
            main_res[eps]["mia_max"].append(adv_m_max)
            main_res[eps]["mia_mean"].append(adv_m_mean)
            main_res[eps]["sigma"].append(sig_m)

            # Train & evaluate Local Overfit subcohort
            pl = train_tanh_mlp_dpsgd(
                xl_tr, yl_tr, h_loc, b_loc, ep_loc, lr_loc, c_loc, sig_l, l2_loc,
                seed=seed * 1000 + idx_eps, apply_dp=is_dp
            )
            _, loss_l_tr = predict_logits_and_losses(xl_tr, yl_tr, pl)
            prob_l_te, loss_l_te = predict_logits_and_losses(xl_te, yl_te, pl)
            auc_l = float(roc_auc_score(yl_te, prob_l_te))
            adv_l_max, adv_l_mean = compute_yeom_mia_metrics(loss_l_tr, loss_l_te)
            local_res[eps]["auc"].append(auc_l)
            local_res[eps]["mia_max"].append(adv_l_max)
            local_res[eps]["mia_mean"].append(adv_l_mean)
            local_res[eps]["sigma"].append(sig_l)

        dt = time.perf_counter() - t0
        print(
            f"[E2 Seed {seed}] d_main={x_tr.shape[1]}, d_local={xl_tr.shape[1]} | "
            f"Raw_inf AUC={raw_inf_aucs[-1]:.4f} | "
            f"SafeHarbor(inf->0.5) AUC={main_res[float('inf')]['auc'][-1]:.4f}->"
            f"{main_res[0.5]['auc'][-1]:.4f} | "
            f"Local MIA(inf->0.5)={local_res[float('inf')]['mia_max'][-1]:.4f}->"
            f"{local_res[0.5]['mia_max'][-1]:.4f} ({dt:.1f}s)"
        )

    auc_inf_mean = float(np.mean(main_res[float("inf")]["auc"]))
    auc_raw_inf_mean = float(np.mean(raw_inf_aucs))

    e2_rows = []
    for eps in EPSILONS:
        is_dp = np.isfinite(eps)
        setting_name = f"DPSGD_eps_{eps:.1f}" if is_dp else "DPSGD_eps_inf"
        eps_val = f"{eps:.1f}" if is_dp else "inf"
        auc_mean = float(np.mean(main_res[eps]["auc"]))
        auc_std = float(np.std(main_res[eps]["auc"]))
        delta_auc = auc_inf_mean - auc_mean if is_dp else 0.0
        delta_auc_raw = auc_raw_inf_mean - auc_mean
        mia_adv_mean = float(np.mean(main_res[eps]["mia_max"]))
        mia_adv_std = float(np.std(main_res[eps]["mia_max"]))
        mia_local_adv_mean = float(np.mean(local_res[eps]["mia_max"]))
        mia_local_adv_std = float(np.std(local_res[eps]["mia_max"]))
        sig_m_mean = float(np.mean(main_res[eps]["sigma"]))
        sig_l_mean = float(np.mean(local_res[eps]["sigma"]))
        passes_c2 = abs(delta_auc) <= 0.05

        print(
            f"[E2 Summary] {setting_name:<14} | AUC={auc_mean:.4f}+-{auc_std:.4f} | "
            f"dAUC={delta_auc:+.4f} | MIA_main={mia_adv_mean:.4f}+-{mia_adv_std:.4f} | "
            f"MIA_local={mia_local_adv_mean:.4f}+-{mia_local_adv_std:.4f} | C2={passes_c2}"
        )

        e2_rows.append({
            "experiment": "E2",
            "setting": setting_name,
            "dataset_records": e1_k10_row["dataset_records"],
            "unique_patients": e1_k10_row["unique_patients"],
            "k_min": e1_k10_row["k_min"],
            "l_min": e1_k10_row["l_min"],
            "num_classes": e1_k10_row["num_classes"],
            "ncp_mean": e1_k10_row["ncp_mean"],
            "ncp_std": e1_k10_row["ncp_std"],
            "p_link_max": e1_k10_row["p_link_max"],
            "p_link_avg": e1_k10_row["p_link_avg"],
            "r_res": e1_k10_row["r_res"],
            "passes_gate": e1_k10_row["passes_gate"],
            "epsilon": eps_val,
            "delta": DELTA,
            "auc_mean": round(auc_mean, 6),
            "auc_std": round(auc_std, 6),
            "delta_auc_vs_inf": round(delta_auc, 6),
            "mia_adv_mean": round(mia_adv_mean, 6),
            "mia_adv_std": round(mia_adv_std, 6),
            "mia_local_adv_mean": round(mia_local_adv_mean, 6),
            "mia_local_adv_std": round(mia_local_adv_std, 6),
            "seeds": ",".join(str(s) for s in SEEDS),
            "sigma_noise": round(sig_m_mean, 6),
            "sigma_local": round(sig_l_mean, 6),
            "clip_norm": c_main if is_dp else "",
            "passes_condition2": bool(passes_c2),
            "auc_raw_inf_mean": round(auc_raw_inf_mean, 6),
            "delta_auc_vs_raw": round(delta_auc_raw, 6),
            "mia_yeom_mean_adv": round(float(np.mean(main_res[eps]["mia_mean"])), 6),
            "mia_local_yeom_mean_adv": round(float(np.mean(local_res[eps]["mia_mean"])), 6),
            "local_cohort_n": LOCAL_COHORT_N,
            "local_auc_mean": round(float(np.mean(local_res[eps]["auc"])), 6),
            "local_auc_std": round(float(np.std(local_res[eps]["auc"])), 6),
            "full_cohort_num_classes": e1_k10_row["full_cohort_num_classes"],
            "full_cohort_ncp": e1_k10_row["full_cohort_ncp"],
        })

    return e2_rows


# ==============================================================================
# F6: Export CSV & Publication Figure 2
# ==============================================================================

def export_benchmark_csv(rows: list[dict], csv_path: str) -> None:
    fieldnames = [
        "experiment", "setting", "dataset_records", "unique_patients",
        "k_min", "l_min", "num_classes", "ncp_mean", "ncp_std",
        "p_link_max", "p_link_avg", "r_res", "passes_gate",
        "epsilon", "delta", "auc_mean", "auc_std", "delta_auc_vs_inf",
        "mia_adv_mean", "mia_adv_std", "mia_local_adv_mean", "mia_local_adv_std",
        "seeds",
        "sigma_noise", "sigma_local", "clip_norm", "passes_condition2",
        "auc_raw_inf_mean", "delta_auc_vs_raw",
        "mia_yeom_mean_adv", "mia_local_yeom_mean_adv",
        "local_cohort_n", "local_auc_mean", "local_auc_std",
        "full_cohort_num_classes", "full_cohort_ncp",
    ]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported empirical benchmark CSV ({len(rows)} rows) -> {csv_path}")


def assert_clean_figure_texts(texts: list[str]) -> None:
    """Ensure zero Chinese characters and zero em/en/double dashes in all visible figure text."""
    forbidden = re.compile(r"[\u4e00-\u9fff\u2013\u2014\u2015]|--")
    for txt in texts:
        if forbidden.search(txt):
            raise ValueError(f"Forbidden character or dash in figure text: {txt!r}")


def generate_figure2_from_csv(csv_path: str) -> None:
    """Plot 300 DPI dual-panel Figure 2 directly from uci_diabetes_benchmark.csv."""
    df = pd.read_csv(csv_path)
    e1 = df[df["experiment"] == "E1"].copy().reset_index(drop=True)
    e2 = df[df["experiment"] == "E2"].copy().reset_index(drop=True)

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.35), dpi=300)

    # --------------------------------------------------------------------------
    # Panel (a): E1 Mondrian (k, l) Risk vs. Information Loss
    # --------------------------------------------------------------------------
    x1 = np.arange(len(e1))
    x1_labels = [
        "Raw\n(k=1, l=1)",
        "k=5, l=3\n(Fail k>=10)",
        "k=10, l=3\n(Safe Harbor)",
        "k=20, l=3\n(Strict)",
    ]
    r_res_pct = e1["r_res"].to_numpy(dtype=np.float64) * 100.0
    p_link_pct = e1["p_link_max"].to_numpy(dtype=np.float64) * 100.0
    ncp_m = e1["ncp_mean"].to_numpy(dtype=np.float64)
    ncp_s = e1["ncp_std"].to_numpy(dtype=np.float64)
    passes = e1["passes_gate"].astype(bool).tolist()

    bar_colors = ["#DC2626" if not p else "#0D9488" for p in passes]
    edge_colors = ["#991B1B" if not p else "#115E59" for p in passes]

    bars = ax1.bar(
        x1, r_res_pct, width=0.46, color=bar_colors, edgecolor=edge_colors,
        linewidth=0.9, zorder=3, label=r"Residual risk $R_{\mathrm{res}}$ (%)",
    )
    l_plink, = ax1.plot(
        x1, p_link_pct, color="#475569", marker="o", linestyle="--",
        linewidth=1.5, markersize=5.2, zorder=4,
        label=r"Max linkage $p_{\mathrm{link,max}} = 1/k_{\min}$ (%)",
    )
    l_thresh = ax1.axhline(
        4.0, color="#D97706", linestyle=":", linewidth=1.6, zorder=4,
        label=r"Threshold $\tau_{\mathrm{safe}} = 4.0\%$",
    )

    ax1.set_yscale("log")
    ax1.set_ylim(0.35, 360.0)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(x1_labels, fontsize=8.0, fontweight="bold", color="#1E293B")
    ax1.set_ylabel("Re-identification Risk (%, log scale)", fontsize=8.8, fontweight="bold", color="#1E293B")
    ax1.set_title("(a) E1: Mondrian (k, l) Risk vs. Information Loss", fontsize=9.6, fontweight="bold", color="#0F172A", pad=10)
    ax1.grid(axis="y", which="major", linestyle=":", alpha=0.55, zorder=0)

    # Annotate bar values and max linkage probabilities cleanly
    for idx, bar in enumerate(bars):
        h = bar.get_height()
        if idx == 1:
            # Place inside top of bar in white to avoid crossing the 4.0% dashed threshold line
            ax1.annotate(
                f"{h:.2f}%",
                xy=(bar.get_x() + bar.get_width() / 2.0, h),
                xytext=(0, -4.5),
                textcoords="offset points",
                ha="center", va="top", fontsize=7.2, fontweight="bold", color="white",
            )
        else:
            ax1.annotate(
                f"{h:.2f}%",
                xy=(bar.get_x() + bar.get_width() / 2.0, h),
                xytext=(0, 3.0),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=7.2, fontweight="bold",
                color="#991B1B" if not passes[idx] else "#115E59",
            )
        y_off = 6.0 if idx == 0 else 5.5
        ax1.annotate(
            f"{p_link_pct[idx]:.0f}%",
            xy=(x1[idx], p_link_pct[idx]),
            xytext=(0, y_off),
            textcoords="offset points",
            ha="center", va="bottom", fontsize=7.0, fontweight="bold", color="#334155",
        )

    ax1_r = ax1.twinx()
    l_ncp = ax1_r.errorbar(
        x1 + 0.08, ncp_m, yerr=ncp_s, color="#1E3A8A", marker="D",
        linewidth=1.8, markersize=5.2, capsize=3.0, zorder=5,
        label="Information loss (NCP)",
    )
    ax1_r.set_ylabel("Normalized Certainty Penalty (NCP)", fontsize=8.8, fontweight="bold", color="#1E3A8A")
    ax1_r.set_ylim(-0.002, 0.036)
    ax1_r.tick_params(axis="y", colors="#1E3A8A", labelsize=8.0)
    ax1.tick_params(axis="y", labelsize=8.0)

    # Combined legend placed cleanly in upper right above low bars (k=5, 10, 20)
    h1, lb1 = ax1.get_legend_handles_labels()
    h1_r, lb1_r = ax1_r.get_legend_handles_labels()
    ax1.legend(
        h1 + h1_r, lb1 + lb1_r, loc="upper right",
        fontsize=6.9, frameon=True, facecolor="white", framealpha=0.95,
        borderpad=0.35, labelspacing=0.25,
    )

    # --------------------------------------------------------------------------
    # Panel (b): E2 DP-SGD Utility and Yeom MIA Defense
    # --------------------------------------------------------------------------
    x2 = np.arange(len(e2))
    x2_labels = [
        "No Noise\n(inf)",
        r"$\varepsilon = 4.0$",
        r"$\varepsilon = 2.0$",
        r"$\varepsilon = 1.0$",
        r"$\varepsilon = 0.5$",
    ]
    auc_m = e2["auc_mean"].to_numpy(dtype=np.float64)
    auc_s = e2["auc_std"].to_numpy(dtype=np.float64)
    mia_m = e2["mia_adv_mean"].to_numpy(dtype=np.float64)
    mia_s = e2["mia_adv_std"].to_numpy(dtype=np.float64)
    mia_loc_m = e2["mia_local_adv_mean"].to_numpy(dtype=np.float64)
    mia_loc_s = e2["mia_local_adv_std"].to_numpy(dtype=np.float64)
    auc_cutoff = float(auc_m[0]) - 0.05

    ax2.errorbar(
        x2, auc_m, yerr=auc_s, color="#0D9488", marker="o", linewidth=2.0,
        markersize=5.5, capsize=3.0, zorder=4,
        label="Safe Harbor Test ROC-AUC",
    )
    ax2.axhline(
        auc_cutoff, color="#64748B", linestyle="-.", linewidth=1.4, zorder=3,
        label=f"Condition 2 Cutoff ({auc_cutoff:.3f})",
    )
    ax2.set_ylim(0.59, 0.745)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(x2_labels, fontsize=8.0, fontweight="bold", color="#1E293B")
    ax2.set_ylabel("Test ROC-AUC", fontsize=8.8, fontweight="bold", color="#0F766E")
    ax2.set_title("(b) E2: DP-SGD Utility and Yeom MIA Defense", fontsize=9.6, fontweight="bold", color="#0F172A", pad=10)
    ax2.grid(axis="y", linestyle=":", alpha=0.55, zorder=0)
    ax2.tick_params(axis="y", colors="#0F766E", labelsize=8.0)

    for idx in range(len(x2)):
        if idx == 0:
            ax2.annotate(
                f"{auc_m[idx]:.3f}",
                xy=(x2[idx], auc_m[idx]),
                xytext=(10.0, 2.5),
                textcoords="offset points",
                ha="left", va="bottom", fontsize=7.0, fontweight="bold", color="#115E59",
            )
        else:
            ax2.annotate(
                f"{auc_m[idx]:.3f}",
                xy=(x2[idx], auc_m[idx] + auc_s[idx]),
                xytext=(0, 4.0),
                textcoords="offset points",
                ha="center", va="bottom", fontsize=7.0, fontweight="bold", color="#115E59",
            )

    ax2_r = ax2.twinx()
    ax2_r.errorbar(
        x2, mia_loc_m, yerr=mia_loc_s, color="#DC2626", marker="s", linewidth=1.8,
        markersize=5.0, capsize=3.0, zorder=5,
        label="Local Overfit MIA Adv (N=2,000)",
    )
    ax2_r.errorbar(
        x2, mia_m, yerr=mia_s, color="#1E3A8A", marker="^", linewidth=1.8,
        markersize=5.2, capsize=3.0, zorder=5,
        label="Safe Harbor MIA Adv (Full Cohort)",
    )
    ax2_r.set_ylim(-0.015, 0.245)
    ax2_r.set_ylabel("Yeom MIA Advantage (max TPR - FPR)", fontsize=8.8, fontweight="bold", color="#991B1B")
    ax2_r.tick_params(axis="y", colors="#991B1B", labelsize=8.0)

    ax2_r.annotate(
        f"{mia_loc_m[0]:.3f}",
        xy=(x2[0], mia_loc_m[0] + mia_loc_s[0]),
        xytext=(5, 2.0),
        textcoords="offset points",
        ha="left", va="bottom", fontsize=7.0, fontweight="bold", color="#991B1B",
    )
    ax2_r.annotate(
        f"{mia_loc_m[4]:.3f}",
        xy=(x2[4], mia_loc_m[4] - mia_loc_s[4]),
        xytext=(-6, -4.0),
        textcoords="offset points",
        ha="right", va="top", fontsize=7.0, fontweight="bold", color="#991B1B",
    )

    # Combined legend placed cleanly in upper right (MIA curves drop from left to right)
    h2, lb2 = ax2.get_legend_handles_labels()
    h2_r, lb2_r = ax2_r.get_legend_handles_labels()
    ax2.legend(
        h2 + h2_r, lb2 + lb2_r, loc="upper right",
        fontsize=6.9, frameon=True, facecolor="white", framealpha=0.95,
        borderpad=0.35, labelspacing=0.25,
    )

    # Verify zero Chinese characters & zero em/en/double dashes in visible text
    all_texts = (
        [ax1.get_title(), ax1.get_ylabel(), ax1_r.get_ylabel()]
        + [ax2.get_title(), ax2.get_ylabel(), ax2_r.get_ylabel()]
        + x1_labels
        + ["No Noise (inf)", "eps = 4.0", "eps = 2.0", "eps = 1.0", "eps = 0.5"]
        + lb1 + lb1_r + lb2 + lb2_r
    )
    assert_clean_figure_texts(all_texts)

    plt.tight_layout(pad=1.0)
    fig_repo_path = os.path.join(FIG_DIR, "figure2_uci_benchmark.png")
    plt.savefig(fig_repo_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    os.makedirs(ROOT_FIG_DIR, exist_ok=True)
    fig_root_path = os.path.join(ROOT_FIG_DIR, "figure2_uci_benchmark.png")
    shutil.copy2(fig_repo_path, fig_root_path)
    print(f"Generated Figure 2 (300 DPI) -> {fig_repo_path}")
    print(f"Synchronized Figure 2 copy -> {fig_root_path}")


def main() -> None:
    t_start = time.perf_counter()
    print("=" * 80)
    print("UCI DIABETES 130-US (ID=296) EMPIRICAL BENCHMARK (E1 + E2)")
    print("=" * 80)

    raw_df = load_uci_diabetes_df()
    df, y, groups, sa, d_sizes = prepare_base_dataframe(raw_df)
    print(
        f"Dataset: {len(df):,} encounters | {df['patient_nbr'].nunique():,} unique patients | "
        f"Positive rate (readmitted != 'NO'): {y.mean()*100:.2f}%"
    )

    sim_cfg = SimulationConfig()
    print("\n--- Experiment E1: Multidimensional Mondrian (k, l)-Anonymity ---")
    e1_rows, k10_trees_by_seed = run_e1_experiments(df, sa, groups, d_sizes, sim_cfg)
    e1_k10_row = next(r for r in e1_rows if r["setting"] == "Mondrian_k10_l3")

    print("\n--- Experiment E2: DP-SGD Utility & Yeom MIA Defense ---")
    e2_rows = run_e2_experiments(df, y, groups, d_sizes, k10_trees_by_seed, e1_k10_row)

    csv_path = os.path.join(DATA_DIR, "uci_diabetes_benchmark.csv")
    export_benchmark_csv(e1_rows + e2_rows, csv_path)
    generate_figure2_from_csv(csv_path)

    print(f"\n[SUCCESS] Empirical benchmark completed in {time.perf_counter() - t_start:.1f}s.")


if __name__ == "__main__":
    main()
