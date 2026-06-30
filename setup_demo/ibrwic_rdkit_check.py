"""Practice script for the Anvil + GitHub setup tutorial.
Computes basic RDKit descriptors and writes a name-stamped results file."""
from rdkit import Chem
from rdkit.Chem import Descriptors
import getpass
import datetime
# Replace this with your own 3+3 code (e.g. "ibrwic")
ACCESS_CODE = "ibrwic"
test_smiles = [
"CCO", # ethanol
"c1ccccc1", # benzene
"CC(=O)Oc1ccccc1C(=O)O", # aspirin
"CN1C=NC2=C1C(=O)N(C(=O)N2C)C", # caffeine
]
lines = [
f"# RDKit environment check -- {ACCESS_CODE}",
f"# Run by: {getpass.getuser()}",
f"# Date: {datetime.date.today().isoformat()}",
"",
f"{'SMILES':<30}{'MolWt':>10}{'LogP':>10}{'NumRings':>10}",
]

for smi in test_smiles:
    mol = Chem.MolFromSmiles(smi)
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    rings = Descriptors.RingCount(mol)
    lines.append(f"{smi:<30}{mw:>10.2f}{logp:>10.2f}{rings:>10d}")

output_path = f"setup_demo/{ACCESS_CODE}_rdkit_results.txt"
with open(output_path, "w") as f:
    f.write("\n".join(lines) + "\n")
    print(f"Wrote results to {output_path}")


