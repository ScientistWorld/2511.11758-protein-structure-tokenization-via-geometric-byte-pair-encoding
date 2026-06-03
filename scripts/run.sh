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

export TRAIN_LIMIT="${TRAIN_LIMIT:-8}"
export TEST_LIMIT="${TEST_LIMIT:-5}"
export ITERATIONS="${ITERATIONS:-3}"
export SEED="${SEED:-0}"

bash scripts/reproduce.sh
python validate.py --compare
