#!/usr/bin/env bash
# Held-out test-slice evaluator. Mirrors scripts/evaluate.sh's artifact
# contract, but writes scoring/scores_test.json and follows the method keys
# recorded by the train-slice score file when it exists.

set -euo pipefail

cd /home/user

mkdir -p scoring

python -m eval.test.evaluate \
  --artifact "${1:-checkpoints/geobpe_scaled_multisplit/results.json}" \
  --train-scores scoring/scores_train.json \
  --output scoring/scores_test.json
