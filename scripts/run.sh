#!/usr/bin/env bash
# Run the official GEOBPE glue-optimization ablation and score it.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

bash scripts/glue_ablation.sh
python validate.py --compare
