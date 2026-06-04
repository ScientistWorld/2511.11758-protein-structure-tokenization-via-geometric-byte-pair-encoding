#!/usr/bin/env bash
# Visible train-slice evaluator. Mirrors scripts/evaluate.sh's artifact
# contract, but writes scoring/scores_train.json.

set -euo pipefail

cd /home/user

mkdir -p scoring

python -m eval.train.evaluate \
  --artifact "${1:-checkpoints/geobpe_scaled_multisplit/results.json}" \
  --output scoring/scores_train.json
