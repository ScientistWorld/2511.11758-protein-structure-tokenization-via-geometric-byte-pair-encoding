#!/usr/bin/env bash
# Final-iteration check: training-seed spread of the reproduced reference on the
# private test, then reference-only packaging through the end-to-end driver.
# Seeds 1 and 2 refit the reference with identical settings; only the sampling /
# k-medoid seed changes. Stage markers make preemption restarts resume.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export GEOBPE_DATASET_WORKERS=1 SLURM_CPUS_PER_TASK=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
export PYTHONWARNINGS=ignore::FutureWarning
unset EVAL_RESCORE
L=logs/seed_audit; S=checkpoints/submissions; A=checkpoints/audit_archive
mkdir -p "$L" "$A"
stage(){ [[ -f "$L/$1.done" ]]; }
mark(){ touch "$L/$1.done"; echo "== stage $1 done $(date -u +%FT%TZ)"; }
complete(){ python3 - "$@" <<'PY'
import json,sys
s=json.load(open('scoring/scores_test.json')); r=s['experiments']['short_backbones']['results']
m=json.load(open('eval/test/measurements.json'))
ok=all(n in r and n in m and (not m[n].get('malformed')) for n in sys.argv[1:])
sys.exit(0 if ok else 1)
PY
}
echo "== start $(date -u +%FT%TZ)"
for seed in 1 2; do
 if ! stage "fit_seed$seed"; then
  python method/train.py --name "geobpe_seed$seed" --run-id "table16_v600_seed$seed" --bins 500 --interior 500 --terminal 100 --main-codebook --candidates 2048 --iterations 0 --seed "$seed" > "$L/fit_seed$seed.log" 2>&1
  mark "fit_seed$seed"
 fi
done
if ! stage eval_test; then
 for attempt in 1 2 3 4; do
  bash scripts/evaluate_test.sh > "$L/test_$attempt.log" 2>&1 || true
  if complete geobpe_reference geobpe_seed1 geobpe_seed2; then break; fi
  echo "seed encodings incomplete after pass $attempt"
 done
 mark eval_test
fi
if ! stage report; then
 python scripts/seed_report.py > "$L/report.log" 2>&1
 cat "$L/report.log"
 cp scoring/scores_test.json redteam/seed_scores_test.json
 mark report
fi
if ! stage package; then
 for n in geobpe_seed1 geobpe_seed2; do
  if [[ -d "$S/$n" ]]; then rm -rf "$A/$n"; mv "$S/$n" "$A/$n"; fi
  if [[ -d "eval/test/runs/$n" ]]; then mkdir -p "$A/runs_test"; rm -rf "$A/runs_test/$n"; mv "eval/test/runs/$n" "$A/runs_test/$n"; fi
 done
 # The end-to-end reference driver: resumes the stored fit, re-encodes (per-chain
 # recovery), rescores both slices, packages reference-only scores and validates.
 bash scripts/reproduce.sh > "$L/reproduce.log" 2>&1
 tail -25 "$L/reproduce.log"
 mark package
fi
echo "== end $(date -u +%FT%TZ)"
