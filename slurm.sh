#!/bin/bash
#SBATCH -A uppmax2026-1-115
#SBATCH --job-name=gecode-lns-mab
#SBATCH --partition=pelle
#SBATCH --cpus-per-task=8
#SBATCH --time=5-00:00:30
if [ -z "${SLURM_ARRAY_TASK_ID}" ]; then
  SLURM_ARRAY_TASK_ID=1
  echo ${SLURM_ARRAY_TASK_ID}
fi
INPUTS_PATH="inputs.txt"
TASK=$(sed "-n" "${SLURM_ARRAY_TASK_ID}p" "${INPUTS_PATH}")
IFS=';' read -ra COMMANDS <<< "${TASK}"

for c in "${COMMANDS[@]}"; do
  if [ ! -z "$c" ]; then
    echo "$c"
  fi
done