#!/usr/bin/env bash
# TEMPORARY (final audit job): fresh end-to-end reference rerun plus hidden probes.
# Restored to the end-to-end reference driver (scripts/reproduce.sh) afterwards.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec bash scripts/hardening_audit.sh
