#!/usr/bin/env bash
# Public RCSB PDB downloads, ~0.5 GB; idempotent from an empty clone.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python3 data/fetch.py --manifest data/sources.json --root data/downloads/pdb
python3 eval/test/fetch.py --manifest eval/test/sources.json --root eval/test/downloads
