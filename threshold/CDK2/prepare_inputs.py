#!/usr/bin/env python3
"""
prepare_inputs.py

Reads the CDK2 known-actives ground-truth dataset and writes one Boltz-2
YAML input (with an affinity block) per molecule, plus a manifest.csv
mapping mol_id -> ChEMBL ID, SMILES, and experimental IC50/pIC50.

Run directly on the login node (fast, no GPU/PyTorch needed):
    python threshold/CDK2/prepare_inputs.py
"""

import os
import csv

REPO_ROOT   = "/anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline"
CALIB_DIR   = os.path.join(REPO_ROOT, "threshold/CDK2")
ACTIVES_CSV = os.path.join(REPO_ROOT, "target_mols/CDK2/IC50/CDK2_Actives_CHEMBL_Bioactivities.csv")
INPUT_DIR   = os.path.join(CALIB_DIR, "boltz_inputs")
MANIFEST    = os.path.join(CALIB_DIR, "manifest.csv")

os.makedirs(INPUT_DIR, exist_ok=True)

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

if __name__ == "__main__":
    with open(ACTIVES_CSV) as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} known actives from {ACTIVES_CSV}")

    manifest_rows = []
    for i, row in enumerate(rows):
        smi = row["Smiles"].strip()
        if not smi:
            continue
        mol_id = f"mol_{i+1:04d}"

        yaml_path = os.path.join(INPUT_DIR, f"{mol_id}.yaml")
        with open(yaml_path, "w") as f:
            f.write(YAML_TEMPLATE.format(sequence=CDK2_SEQUENCE, smiles=smi))

        manifest_rows.append({
            "mol_id":    mol_id,
            "chembl_id": row["Molecule ChEMBL ID"],
            "smiles":    smi,
            "ic50_nM":   row["IC50_nM"],
            "pIC50":     row["pIC50"],
        })

    with open(MANIFEST, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["mol_id", "chembl_id", "smiles", "ic50_nM", "pIC50"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Wrote {len(manifest_rows)} YAML inputs to {INPUT_DIR}/")
    print(f"Wrote manifest to {MANIFEST}")
