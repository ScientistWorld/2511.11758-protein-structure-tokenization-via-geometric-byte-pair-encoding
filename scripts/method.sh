#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python method/train.py --name geobpe_reference --bins 500 --iterations 50
