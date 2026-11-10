#!/usr/bin/env bash
# Temporary: the one combined hardening audit job. Restored to scripts/reproduce.sh afterwards.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec bash scripts/hardening_audit.sh
