#!/usr/bin/env bash
# Visible train-slice evaluator. Mirrors scripts/evaluate.sh's artifact
# contract, but writes scoring/scores_train.json.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

mkdir -p scoring

python -m eval.train.evaluate \
  --artifact "${1:-checkpoints/geobpe_table16_sweep/results.json}" \
  --output scoring/scores_train.json
