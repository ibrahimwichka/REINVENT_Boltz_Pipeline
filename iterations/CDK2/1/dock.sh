#!/bin/bash
#SBATCH --job-name=cdk2_dock_iter1
#SBATCH --output=iterations/CDK2/1/docking/dock_%j.log
#SBATCH --error=iterations/CDK2/1/docking/dock_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --account=bio220114-gpu

echo "Job started: $(date)"
echo "Running on node: $HOSTNAME"

source ~/.bashrc
conda activate boltz2

cd /anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline

mkdir -p iterations/CDK2/1/docking

echo "Running Boltz-2 docking for CDK2, Iteration 1..."
python iterations/CDK2/1/docking/dock_cdk2.py

echo "Docking complete: $(date)"
