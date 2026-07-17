#!/bin/bash
#SBATCH --job-name=p38_calib_dock
#SBATCH --output=threshold/P38_MAPK14/logs/dock_%A_%a.log
#SBATCH --error=threshold/P38_MAPK14/logs/dock_%A_%a.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --partition=gpu
#SBATCH --gpus-per-node=1
#SBATCH --account=bio220114-gpu
#SBATCH --array=0-77%10

# NOTE: submit this from the repo root (cd /anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline
# first) so the relative --output/--error paths above resolve correctly.
#
# Chunking: manifest.csv has 3860 P38 actives, CHUNK_SIZE=50 -> 78 tasks (array indices 0-77).
# %10 caps this at 10 concurrent GPU jobs so it doesn't monopolize the shared gpu partition.
# If manifest.csv row count changes (e.g. re-run of prepare_inputs.py with filtering), update
# both CHUNK_SIZE below and the --array range above to match.

echo "Task $SLURM_ARRAY_TASK_ID started: $(date)"
echo "Running on node: $HOSTNAME"

source ~/.bashrc
conda activate boltz2

cd /anvil/projects/x-bio220114/ibrwic/REINVENT_Boltz_Pipeline

mkdir -p threshold/P38_MAPK14/logs
mkdir -p threshold/P38_MAPK14/boltz_outputs

CHUNK_SIZE=50
START=$(( SLURM_ARRAY_TASK_ID * CHUNK_SIZE ))
END=$(( START + CHUNK_SIZE ))

echo "Docking P38_MAPK14 calibration set, manifest rows $START-$END..."
python threshold/P38_MAPK14/dock_worker.py --start $START --end $END

echo "Task $SLURM_ARRAY_TASK_ID complete: $(date)"
