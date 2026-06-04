#!/usr/bin/env bash
# Reproduce the paper's results end-to-end.
#
# This script runs inside the compute container and should call
# scripts/baseline.sh and scripts/method.sh to run baselines and
# the paper's method, each of which calls scripts/evaluate.sh.
#
# Assumes:
#   - Container is built (environment/container.sif)
#   - Data and models are downloaded (via scripts/download.sh)
#   - Working directory is the repository root
#
# This is the "gold standard" reproduction — 
# You do not need to run this, but keep this in good shape
# so other agents can easily run a full loop of reproduction and get the paper's numbers.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

HIGH_OUTPUT_DIR="${HIGH_OUTPUT_DIR:-checkpoints/geobpe_table16_high_multisplit}"
HIGH_INDUCE_DIR="${HIGH_INDUCE_DIR:-checkpoints/geobpe_table16_high_multisplit_induce}"
LOW_OUTPUT_DIR="${LOW_OUTPUT_DIR:-checkpoints/geobpe_table16_low_multisplit}"
LOW_INDUCE_DIR="${LOW_INDUCE_DIR:-checkpoints/geobpe_table16_low_multisplit_induce}"

GEOBPE_OUTPUT_DIR="$HIGH_OUTPUT_DIR" \
GEOBPE_INDUCE_DIR="$HIGH_INDUCE_DIR" \
GEOBPE_TEST_SPLIT="${GEOBPE_TEST_SPLIT:-all}" \
TRAIN_LIMIT="${TRAIN_LIMIT:-12}" \
TEST_LIMIT="${TEST_LIMIT:-5}" \
ITERATIONS="${ITERATIONS:-3}" \
bash scripts/method.sh

GEOBPE_OUTPUT_DIR="$LOW_OUTPUT_DIR" \
GEOBPE_INDUCE_DIR="$LOW_INDUCE_DIR" \
GEOBPE_TEST_SPLIT=all \
GEOBPE_NUM_P="2-2:3-5:5-1:6-2:8-1" \
TRAIN_LIMIT="${TRAIN_LIMIT:-12}" \
TEST_LIMIT="${TEST_LIMIT:-5}" \
ITERATIONS="${ITERATIONS:-3}" \
bash scripts/method.sh

python scripts/merge_artifacts.py \
  --input "$HIGH_OUTPUT_DIR/results.json:geobpe_scaled:geobpe_table16_high" \
  --input "$LOW_OUTPUT_DIR/results.json:geobpe_scaled:geobpe_table16_low" \
  --output checkpoints/geobpe_table16_sweep/results.json

bash scripts/evaluate.sh checkpoints/geobpe_table16_sweep/results.json
