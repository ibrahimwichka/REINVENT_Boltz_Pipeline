# reinvent-boltz-pipeline

A closed-loop generative chemistry pipeline combining **REINVENT4** (molecule generation) and **Boltz-2** (structure prediction) for structure-based drug discovery. 

## Overview

The pipeline iteratively generates candidate molecules using REINVENT4's transfer learning framework, scores them via Boltz-2 structure prediction, and feeds the results back into the next generation cycle. The current campaign targets **p38 MAPK and CDK2**.

