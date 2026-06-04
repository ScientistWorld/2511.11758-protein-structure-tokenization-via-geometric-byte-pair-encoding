#!/usr/bin/env bash
# Score the frozen final GEOBPE artifact on the visible train slice and the
# held-out test slice. This job performs post-hoc evaluation only.

set -euo pipefail

cd /home/user

ARTIFACT="${1:-checkpoints/geobpe_scaled_multisplit/results.json}"

bash scripts/evaluate_train.sh "$ARTIFACT"
bash scripts/evaluate_test.sh "$ARTIFACT"
