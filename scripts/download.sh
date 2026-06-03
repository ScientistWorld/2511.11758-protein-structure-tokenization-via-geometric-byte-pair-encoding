#!/usr/bin/env bash
# Download all data and models needed for this environment.
#
# Run on a node with internet access BEFORE building the container
# or submitting compute jobs.
#
# This script should be idempotent — safe to run multiple times.
# It should skip files that already exist.
#
# Update the storage estimate below as you add downloads.
#
# Estimated total download size: ~35 MB
# Estimated disk usage after extraction: ~35 MB
#
# This script is intentionally workspace-local so a future user with just
# this repository can repopulate the needed public PDB files.

set -euo pipefail

cd /home/user

mkdir -p data/downloads/rcsb_pdb data/pdb_smoke/train data/pdb_smoke/validation data/pdb_smoke/cameo data/pdb_smoke/casp14

fetch_pdb() {
  local pdb_id="$1"
  local chain_id="$2"
  local split="$3"
  local upper raw out
  upper="$(printf '%s' "$pdb_id" | tr '[:lower:]' '[:upper:]')"
  raw="data/downloads/rcsb_pdb/${upper}.pdb"
  out="data/pdb_smoke/${split}/${pdb_id}_${chain_id}.pdb"
  if [ ! -s "$raw" ]; then
    curl -fsSL "https://files.rcsb.org/download/${upper}.pdb" -o "$raw"
  fi
  if [ ! -s "$out" ]; then
    awk -v c="$chain_id" 'substr($0,1,6)=="ATOM  " && substr($0,22,1)==c {print} /^END/ {print}' "$raw" > "$out"
  fi
}

fetch_pdb 1a0o F train
fetch_pdb 1a1k A train
fetch_pdb 1a28 A train
fetch_pdb 1a2a G train
fetch_pdb 1a40 A train
fetch_pdb 1a4m A train
fetch_pdb 1a55 A train
fetch_pdb 1a6p A train
fetch_pdb 1a7d A train
fetch_pdb 1a7u A train
fetch_pdb 1ab1 A train
fetch_pdb 1ae8 H train

fetch_pdb 1a8r I validation
fetch_pdb 1a92 A validation
fetch_pdb 1ai6 A validation
fetch_pdb 1aok A validation
fetch_pdb 1aph B validation
fetch_pdb 1aut C validation

fetch_pdb 7b8b A cameo
fetch_pdb 7ctx B cameo
fetch_pdb 7dri A cameo
fetch_pdb 7egt B cameo
fetch_pdb 7ejg C cameo

fetch_pdb 6n64 A casp14
fetch_pdb 6poo A casp14
fetch_pdb 6px4 R casp14
fetch_pdb 6px4 T casp14
fetch_pdb 6s44 A casp14
