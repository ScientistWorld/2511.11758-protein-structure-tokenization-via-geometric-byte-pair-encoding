#!/usr/bin/env bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -euo pipefail

cd /home/user

python method/run_official_geobpe.py \
  --data-root data/pdb_smoke \
  --output-dir checkpoints/geobpe_scaled \
  --induce-dir checkpoints/geobpe_scaled_cameo \
  --train-limit "${TRAIN_LIMIT:-2}" \
  --test-limit "${TEST_LIMIT:-2}" \
  --max-iter "${ITERATIONS:-1}" \
  --seed "${SEED:-0}"
