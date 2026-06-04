#!/usr/bin/env bash
# Verify the completed GEOBPE core-claim artifact.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

ARTIFACT="${1:-checkpoints/geobpe_scaled_multisplit/results.json}"

bash scripts/evaluate.sh "$ARTIFACT"
bash scripts/evaluate_train.sh "$ARTIFACT"
bash scripts/evaluate_test.sh "$ARTIFACT"
python validate.py --compare
