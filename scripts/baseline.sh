#!/usr/bin/env bash
# Run a baseline method from the paper.
#
# Baselines are simple reference methods the paper compares against. 
# Implement this only if applicable, i.e. the paper has baselines.
# You do not need to implement all baselines to begin — 
# just enough to validate that the evaluation pipeline works 
# and provide a reference point. You can decide to expand more baselines later.
# Each baseline must be actually run and scored through evaluate.sh
# so the numbers are verified, not self-reported.
# You can decide what this baseline script should do yourself.
#
# Usage:
#   bash scripts/baseline.sh <name>

set -euo pipefail

cd /home/user

TRAIN_LIMIT="${TRAIN_LIMIT:-12}"
TEST_SPLIT="${TEST_SPLIT:-cameo}"
RESIDUE_K="${RESIDUE_K:-16}"
BINS="${BINS:-24}"
SEED="${SEED:-0}"

python -m method.geobpe_repro.geobpe \
  --data-root data/pdb_smoke \
  --output-dir checkpoints/residue_baseline \
  --train-limit "$TRAIN_LIMIT" \
  --test-split "$TEST_SPLIT" \
  --residue-k "$RESIDUE_K" \
  --pair-k 1 \
  --bins "$BINS" \
  --iterations 0 \
  --seed "$SEED"

bash scripts/evaluate.sh checkpoints/residue_baseline/results.json
