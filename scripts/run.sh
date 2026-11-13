#!/usr/bin/env bash
# TEMPORARY (validation job): score the new hidden probes from saved raw streams.
# Restored to the end-to-end reference driver (scripts/reproduce.sh) afterwards.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec bash tmp/probe_check.sh
