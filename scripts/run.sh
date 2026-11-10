#!/usr/bin/env bash
# Temporary for the final-iteration job: reference training-seed spread on the private
# test, then the end-to-end reference driver. Restored to scripts/reproduce.sh afterwards.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec bash scripts/seed_audit.sh
