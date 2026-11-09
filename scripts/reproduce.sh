#!/usr/bin/env bash
# Reference-only end-to-end reproduction, with all comparison settings fixed in eval/.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export GEOBPE_DATASET_WORKERS=1 SLURM_CPUS_PER_TASK=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
bash scripts/method.sh
python baseline/internal.py --fit
bash scripts/evaluate_train.sh
bash scripts/evaluate_test.sh
python scripts/package_scores.py
python validate.py
