#!/usr/bin/env bash
# End-to-end reference reproduction (after scripts/download.sh): fit the reproduced
# GEOBPE reference and the independent baseline, evaluate both slices through the
# evaluators, package reference-only scores, validate.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec bash scripts/reproduce.sh
