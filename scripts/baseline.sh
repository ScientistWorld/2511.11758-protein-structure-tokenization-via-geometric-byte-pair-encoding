#!/usr/bin/env bash
# Fit the independent coding baseline, then evaluate all registered public submissions.
# Run inside a compute job after scripts/download.sh.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONHASHSEED=0
python baseline/internal.py --fit
bash scripts/evaluate_train.sh
