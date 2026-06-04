#!/usr/bin/env bash
# Run the paper's glue-optimization ablation with the official PT-BPE code.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ ! -f checkpoints/geobpe_scaled_multisplit/results.json ]; then
  TRAIN_LIMIT="${TRAIN_LIMIT:-12}" \
  TEST_LIMIT="${TEST_LIMIT:-5}" \
  ITERATIONS="${ITERATIONS:-3}" \
  GEOBPE_TEST_SPLIT=all \
  GEOBPE_OUTPUT_DIR=checkpoints/geobpe_scaled_multisplit \
  GEOBPE_INDUCE_DIR=checkpoints/geobpe_scaled_multisplit_induce \
  GEOBPE_GLUE_OPT=true \
  GEOBPE_METHOD_NAME=geobpe_scaled \
  bash scripts/method.sh
fi

TRAIN_LIMIT="${TRAIN_LIMIT:-12}" \
TEST_LIMIT="${TEST_LIMIT:-5}" \
ITERATIONS="${ITERATIONS:-3}" \
GEOBPE_TEST_SPLIT="${GEOBPE_TEST_SPLIT:-cameo}" \
GEOBPE_OUTPUT_DIR="${GEOBPE_OUTPUT_DIR:-checkpoints/geobpe_no_glue}" \
GEOBPE_INDUCE_DIR="${GEOBPE_INDUCE_DIR:-checkpoints/geobpe_no_glue_cameo}" \
GEOBPE_GLUE_OPT=false \
GEOBPE_METHOD_NAME=geobpe_no_glue \
bash scripts/method.sh

python method/combine_ablation_artifacts.py \
  --with-glue checkpoints/geobpe_scaled_multisplit/results.json \
  --without-glue "${GEOBPE_OUTPUT_DIR:-checkpoints/geobpe_no_glue}/results.json" \
  --output checkpoints/geobpe_glue_ablation/results.json \
  --source-experiment scaled_pdb_tokenization_cameo \
  --experiment glue_optimization_ablation

bash scripts/evaluate.sh checkpoints/geobpe_glue_ablation/results.json
