#!/usr/bin/env python3
"""
analyze_calibration.py

Collects Boltz-2 affinity predictions for the P38_MAPK14 known-actives
calibration set, joins them with experimental ground truth, and plots:
  1. Predicted vs. experimental pIC50 (scatter, with correlation)
  2. Distribution of predicted binder probability (p_bind) across actives,
     to help select the gating threshold tau (research plan Section 1.3).

Run directly on the login node after dock_array.sh completes (fast, no GPU):
    python threshold/P38_MAPK14/analyze_calibration.py
"""

import os
import csv
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT   = "/anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline"
CALIB_DIR   = os.path.join(REPO_ROOT, "threshold/P38_MAPK14")
MANIFEST    = os.path.join(CALIB_DIR, "manifest.csv")
OUTPUT_DIR  = os.path.join(CALIB_DIR, "boltz_outputs")
RESULTS_CSV = os.path.join(CALIB_DIR, "calibration_results.csv")

def load_manifest(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def load_affinity(mol_id):
    path = os.path.join(
        OUTPUT_DIR, mol_id, f"boltz_results_{mol_id}",
        "predictions", mol_id, f"affinity_{mol_id}.json"
    )
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

if __name__ == "__main__":
    manifest = load_manifest(MANIFEST)
    print(f"Manifest has {len(manifest)} molecules.")

    results = []
    missing = 0
    for row in manifest:
        aff = load_affinity(row["mol_id"])
        if aff is None:
            missing += 1
            continue

        pred_value = aff["affinity_pred_value"]
        p_bind     = aff["affinity_probability_binary"]

        # Boltz-2's affinity_pred_value is predicted log10(IC50) in uM.
        # Convert to pIC50 (-log10(IC50 in M)) to compare directly against
        # the ground-truth pIC50 column: pIC50 = -log10(IC50_uM * 1e-6) = 6 - pred_value
        pred_pIC50   = 6.0 - pred_value
        pred_IC50_uM = 10.0 ** pred_value

        results.append({
            "mol_id":       row["mol_id"],
            "chembl_id":    row["chembl_id"],
            "exp_ic50_nM":  float(row["ic50_nM"]),
            "exp_pIC50":    float(row["pIC50"]),
            "pred_IC50_uM": pred_IC50_uM,
            "pred_pIC50":   pred_pIC50,
            "p_bind":       p_bind,
        })

    print(f"Loaded affinity predictions for {len(results)} of {len(manifest)} molecules "
          f"({missing} missing/not yet docked).")

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "mol_id", "chembl_id", "exp_ic50_nM", "exp_pIC50",
            "pred_IC50_uM", "pred_pIC50", "p_bind",
        ])
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {RESULTS_CSV}")

    if not results:
        print("No results to plot yet -- run dock_array.sh first.")
        raise SystemExit(0)

    exp_pIC50  = np.array([r["exp_pIC50"] for r in results])
    pred_pIC50 = np.array([r["pred_pIC50"] for r in results])
    p_bind     = np.array([r["p_bind"] for r in results])

    # --- Plot 1: predicted vs experimental pIC50 ---
    r = np.corrcoef(exp_pIC50, pred_pIC50)[0, 1]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(exp_pIC50, pred_pIC50, alpha=0.3, s=10)
    lims = [min(exp_pIC50.min(), pred_pIC50.min()), max(exp_pIC50.max(), pred_pIC50.max())]
    ax.plot(lims, lims, "k--", linewidth=1, label="y = x")
    ax.set_xlabel("Experimental pIC50")
    ax.set_ylabel("Boltz-2 predicted pIC50")
    ax.set_title(f"P38_MAPK14 known actives: predicted vs. experimental pIC50 (r = {r:.2f}, n = {len(results)})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(CALIB_DIR, "pIC50_correlation.png"), dpi=150)
    print(f"Pearson r = {r:.3f}")

    # --- Plot 2: p_bind distribution across known actives ---
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(p_bind, bins=30, color="steelblue", edgecolor="white")
    for tau in (0.3, 0.4, 0.5):
        ax.axvline(tau, color="red", linestyle="--", linewidth=1)
        ax.text(tau, ax.get_ylim()[1] * 0.95, f"tau={tau}", rotation=90, va="top", ha="right", fontsize=8)
    ax.set_xlabel("Predicted binder probability (p_bind)")
    ax.set_ylabel("Count")
    ax.set_title(f"P38_MAPK14 known actives: p_bind distribution (n = {len(results)})")
    fig.tight_layout()
    fig.savefig(os.path.join(CALIB_DIR, "p_bind_distribution.png"), dpi=150)

    print("\np_bind percentiles among known actives:")
    for pct in (10, 25, 50, 75, 90):
        print(f"  {pct}th percentile: {np.percentile(p_bind, pct):.3f}")
    print(f"\nSaved plots to {CALIB_DIR}/")
