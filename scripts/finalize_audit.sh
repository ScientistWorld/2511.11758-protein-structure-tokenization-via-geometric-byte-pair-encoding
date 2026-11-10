#!/usr/bin/env bash
# Final packaging and valid-lookup replay; reuse all unchanged raw predictions.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONHASHSEED=0 PYTHONWARNINGS=ignore::FutureWarning
mkdir -p logs/hardening
python scripts/check_packaging.py
python eval/test/prepare_probes.py
EVAL_RESCORE=1 bash scripts/evaluate_test.sh > logs/hardening/final_probes.log 2>&1
python scripts/package_scores.py --audit
cp scripts/reproduce.sh scripts/run.sh
python validate.py
