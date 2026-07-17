#!/usr/bin/env python3
"""
dock_cdk2.py

Reads generated_molecules.csv from the generation/ folder, prepares
Boltz-2 YAML input files, and runs docking against CDK2.

Run via SLURM:
    sbatch iterations/CDK2/1/docking/dock.sh
"""

import os
import csv
import subprocess

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = f"/anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline"
ITER_DIR    = os.path.join(REPO_ROOT, "iterations/CDK2/1")
SMILES_FILE = os.path.join(ITER_DIR, "generation/generated_molecules.csv")
INPUT_DIR   = os.path.join(ITER_DIR, "docking/boltz_inputs")
OUTPUT_DIR  = os.path.join(ITER_DIR, "docking/boltz_outputs")

os.makedirs(INPUT_DIR,  exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── CDK2 protein sequence (UniProt P24941, human) ────────────────────────────
CDK2_SEQUENCE = (
    "MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNH"
    "PNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCH"
    "SHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKY"
    "YSTPVDIWSVGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPS"
    "FPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"
)

YAML_TEMPLATE = """\
version: 1

sequences:
  - protein:
      id: A
      sequence: {sequence}
      msa: empty

  - ligand:
      id: B
      smiles: "{smiles}"

properties:
  - affinity:
      binder: B
"""

def load_smiles(path):
    smiles_list = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            smi = row.get("SMILES", "").strip()
            if smi:
                smiles_list.append(smi)
    return smiles_list

if __name__ == "__main__":
    smiles_list = load_smiles(SMILES_FILE)
    print(f"Loaded {len(smiles_list)} molecules from {SMILES_FILE}")
    print(f"Writing Boltz-2 inputs to {INPUT_DIR}/\n")

    input_files = []
    for i, smi in enumerate(smiles_list):
        mol_id    = f"mol_{i+1:03d}"
        yaml_path = os.path.join(INPUT_DIR, f"{mol_id}.yaml")
        with open(yaml_path, "w") as f:
            f.write(YAML_TEMPLATE.format(sequence=CDK2_SEQUENCE, smiles=smi))
        input_files.append(yaml_path)
        print(f"  [{i+1:02d}] {mol_id}.yaml  |  {smi[:60]}")

    print(f"\nPrepared {len(input_files)} input files.")
    print("Running Boltz-2 docking...\n")

    for yaml_path in input_files:
        mol_id  = os.path.basename(yaml_path).replace(".yaml", "")
        out_dir = os.path.join(OUTPUT_DIR, mol_id)
        print(f"  [{mol_id}] Docking...")

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

    print(f"\nAll docking complete. Outputs: {OUTPUT_DIR}")
