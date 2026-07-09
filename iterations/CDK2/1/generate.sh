#!/bin/bash
#SBATCH --job-name=cdk2_generate_iter1
#SBATCH --output=iterations/CDK2/1/generation/generate_%j.log
#SBATCH --error=iterations/CDK2/1/generation/generate_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=3:00:00
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --account=bio220114-gpu

echo "Job started: $(date)"
echo "Running on node: $HOSTNAME"

source ~/.bashrc
conda activate reinvent4

cd /anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline

mkdir -p iterations/CDK2/1/generation

echo "Generating molecules from REINVENT4 prior..."
reinvent -l iterations/CDK2/1/generation/reinvent.log \
         iterations/CDK2/1/generation/sampling.toml

echo "Generation complete: $(date)"
echo "Output: iterations/CDK2/1/generation/generated_molecules.csv"
