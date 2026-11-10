#!/usr/bin/env bash
# Reference: released GEOBPE at the paper's Table 14 main codebook, at the operating
# point Table 16 reports for it (|V| = 600, i.e. before merge rounds add keys).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python method/train.py --name geobpe_reference --run-id table16_v600 --bins 500 --interior 500 --terminal 100 --main-codebook --candidates 2048 --iterations 0
