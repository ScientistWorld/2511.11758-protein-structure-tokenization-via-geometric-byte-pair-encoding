#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python method/train.py --name geobpe_reference --run-id main_compression --bins 500 --interior 500 --terminal 100 --main-codebook --candidates 2048 --iterations 5
