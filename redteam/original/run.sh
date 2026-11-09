#!/usr/bin/env bash
# Add the lower-resolution Table 16 GEOBPE setting and score the merged sweep.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

GEOBPE_OUTPUT_DIR=checkpoints/geobpe_table16_low_multisplit \
GEOBPE_INDUCE_DIR=checkpoints/geobpe_table16_low_multisplit_induce \
GEOBPE_TEST_SPLIT=all \
GEOBPE_NUM_P="2-2:3-5:5-1:6-2:8-1" \
TRAIN_LIMIT=12 \
TEST_LIMIT=5 \
ITERATIONS=3 \
bash scripts/method.sh

python scripts/merge_artifacts.py \
  --input checkpoints/geobpe_scaled_multisplit/results.json:geobpe_scaled:geobpe_table16_high \
  --input checkpoints/geobpe_table16_low_multisplit/results.json:geobpe_scaled:geobpe_table16_low \
  --output checkpoints/geobpe_table16_sweep/results.json

bash scripts/evaluate.sh checkpoints/geobpe_table16_sweep/results.json
bash scripts/evaluate_train.sh checkpoints/geobpe_table16_sweep/results.json
bash scripts/evaluate_test.sh checkpoints/geobpe_table16_sweep/results.json
python validate.py --compare
