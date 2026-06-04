#!/usr/bin/env bash
# Example job script submitted via the end-of-turn YAML block.
#
# This runs inside the compute container with:
#   - Your workspace mounted at /home/user
#   - GPU(s) available
#   - No internet access
#
# Make sure all data, code, and dependencies are already in the
# workspace or baked into the container before submitting.

set -euo pipefail

cd /home/user

export TRAIN_LIMIT="${TRAIN_LIMIT:-12}"
export TEST_LIMIT="${TEST_LIMIT:-5}"
export ITERATIONS="${ITERATIONS:-3}"
export GEOBPE_BINS="${GEOBPE_BINS:-1-50}"
export GEOBPE_NUM_P="${GEOBPE_NUM_P:-2-10:3-50:5-1:6-5:8-1}"
export GEOBPE_MAX_NUM_STRUCS="${GEOBPE_MAX_NUM_STRUCS:-100}"
export SEED="${SEED:-0}"

bash scripts/reproduce.sh
python validate.py --compare
