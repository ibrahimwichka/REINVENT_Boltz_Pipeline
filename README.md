# reinvent-boltz-pipeline

A closed-loop generative chemistry pipeline combining **REINVENT4** (molecule generation) and **Boltz-2** (structure prediction) for structure-based drug discovery. Developed in the Lai Lab, Summer 2026.

## Overview

The pipeline iteratively generates candidate molecules using REINVENT4's reinforcement learning framework, scores them via Boltz-2 structure prediction, and feeds the results back into the next generation cycle. The current campaign targets **p38 MAPK and CDK2**.

## Dependencies

- [REINVENT4](https://github.com/MolecularAI/REINVENT4) — molecule generation and reinforcement learning
- [Boltz-2](https://github.com/jwohlwend/boltz) — structure-based scoring via protein-ligand prediction

See `setup_demo/` for sample commit in environment installation instructions on Anvil (Purdue HPC).

## Compute

Jobs are run on **Anvil** (Purdue/ACCESS) under allocation `bio220114`. Generation steps use the `shared` (CPU) partition; Boltz-2 scoring and REINVENT4 fine-tuning use the `gpu` partition.
