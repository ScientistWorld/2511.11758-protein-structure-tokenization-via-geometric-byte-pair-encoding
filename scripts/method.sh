#!/usr/bin/env bash
# Run the paper's proposed method.
#
# This script trains/runs the paper's method using code in method/.
#
# Usage:
#   bash scripts/method.sh

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

python method/run_official_geobpe.py \
  --data-root data/pdb_smoke \
  --output-dir "${GEOBPE_OUTPUT_DIR:-checkpoints/geobpe_scaled}" \
  --induce-dir "${GEOBPE_INDUCE_DIR:-checkpoints/geobpe_scaled_${GEOBPE_TEST_SPLIT:-cameo}}" \
  --test-split "${GEOBPE_TEST_SPLIT:-cameo}" \
  --train-limit "${TRAIN_LIMIT:-2}" \
  --test-limit "${TEST_LIMIT:-2}" \
  --max-iter "${ITERATIONS:-1}" \
  --bins "${GEOBPE_BINS:-1-50}" \
  --num-p "${GEOBPE_NUM_P:-2-10:3-50:5-1:6-5:8-1}" \
  --max-num-strucs "${GEOBPE_MAX_NUM_STRUCS:-100}" \
  --seed "${SEED:-0}"
