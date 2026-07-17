#!/usr/bin/env python3
"""
dock_worker.py

Runs Boltz-2 structure + affinity prediction for one chunk of molecules
from manifest.csv, selected by --start/--end row indices. Skips molecules
that already have an affinity result (safe to re-submit/resume).

Invoked per-task by the SLURM array job:
    sbatch threshold/P38_MAPK14/dock_array.sh
"""

import os
import csv
import argparse
import subprocess

REPO_ROOT  = "/anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline"
CALIB_DIR  = os.path.join(REPO_ROOT, "threshold/P38_MAPK14")
INPUT_DIR  = os.path.join(CALIB_DIR, "boltz_inputs")
OUTPUT_DIR = os.path.join(CALIB_DIR, "boltz_outputs")
MANIFEST   = os.path.join(CALIB_DIR, "manifest.csv")

def load_manifest(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def already_done(mol_id):
    path = os.path.join(
        OUTPUT_DIR, mol_id, f"boltz_results_{mol_id}",
        "predictions", mol_id, f"affinity_{mol_id}.json"
    )
    return os.path.exists(path)

def dock_one(mol_id):
    if already_done(mol_id):
        print(f"  [{mol_id}] Already done, skipping.")
        return

    yaml_path = os.path.join(INPUT_DIR, f"{mol_id}.yaml")
    out_dir   = os.path.join(OUTPUT_DIR, mol_id)

    cmd = [
        "boltz", "predict", yaml_path,
        "--out_dir",                   out_dir,
        "--accelerator",               "gpu",
        "--model",                     "boltz2",
        "--diffusion_samples",         "1",
        "--sampling_steps",            "200",
        "--diffusion_samples_affinity","5",
        "--sampling_steps_affinity",   "200",
        "--affinity_mw_correction",
        "--override"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  [{mol_id}] Done -> {out_dir}")
    else:
        print(f"  [{mol_id}] ERROR:")
        print(result.stderr[-300:])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end",   type=int, required=True)
    args = parser.parse_args()

    manifest = load_manifest(MANIFEST)
    chunk = manifest[args.start:args.end]
    print(f"Docking molecules {args.start}-{args.end} ({len(chunk)} of {len(manifest)} total)")

    for row in chunk:
        dock_one(row["mol_id"])

    print("Chunk complete.")
