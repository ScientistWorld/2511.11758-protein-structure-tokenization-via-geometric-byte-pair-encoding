#!/usr/bin/env bash
# One combined final hardening audit. The changed reference reruns from final code
# (fresh fitting and encoding); unchanged models are rescored from their saved raw
# streams through encoder recovery. Stage markers make preemption restarts resume.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export GEOBPE_DATASET_WORKERS=1 SLURM_CPUS_PER_TASK=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
export PYTHONWARNINGS=ignore::FutureWarning
unset EVAL_RESCORE
L=logs/hardening2; S=checkpoints/submissions; A=checkpoints/audit_archive
mkdir -p "$L" "$A"
stage(){ [[ -f "$L/$1.done" ]]; }
ref_ok(){ python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); sys.exit(0 if "geobpe_reference" in s["experiments"]["short_backbones"]["results"] and "geobpe_reference" not in s["_metadata"]["failed"] else 1)' "$1"; }
evaluate(){ # slice, log prefix: retry while the resumable fresh reference encode is unfinished
 for attempt in 1 2 3 4; do
  bash "scripts/evaluate_$1.sh" > "$L/$2_$attempt.log" 2>&1
  if ref_ok "scoring/scores_$1.json"; then return 0; fi
  echo "reference not complete on $1 after pass $attempt"
 done
 echo "reference failed on $1"; return 1
}
mark(){ touch "$L/$1.done"; echo "== stage $1 done $(date -u +%FT%TZ)"; }
archive(){ # archive submission $1 (and its runs) as $2
 [[ -d "$S/$1" ]] || return 0
 rm -rf "$A/$2"; mv "$S/$1" "$A/$2"
 for side in train test; do
  if [[ -d "eval/$side/runs/$1" ]]; then mkdir -p "$A/runs_$side"; rm -rf "$A/runs_$side/$2"; mv "eval/$side/runs/$1" "$A/runs_$side/$2"; fi
 done
}
echo "== start $(date -u +%FT%TZ)"
if ! stage setup; then
 python scripts/check_codec.py
 python scripts/check_refinement.py
 # Former 5-merge reference becomes the merge ablation; its raw streams are recovered unchanged.
 if [[ -f "$S/geobpe_reference/manifest.json" ]] && grep -q main_compression "$S/geobpe_reference/manifest.json"; then
  for side in train test; do
   if [[ -d "eval/$side/runs/geobpe_reference" ]]; then rm -rf "eval/$side/runs/merge5"; mv "eval/$side/runs/geobpe_reference" "eval/$side/runs/merge5"; fi
  done
  rm -rf "$S/geobpe_reference"
 fi
 [[ -f "$S/merge5/manifest.json" ]] || python method/train.py --name merge5 --export-only checkpoints/hardening/main_compression/latest.pkl
 # The variant and attacks built on the former reference are archived and rebuilt below.
 archive refined_glue refined_glue_on_merge5
 for d in "$S"/attack_*; do if [[ -d "$d" ]]; then archive "$(basename "$d")" "old_$(basename "$d")"; fi; done
 python baseline/internal.py --fit
 python baseline/residue_quantized.py --fit
 python eval/test/variants/closed_loop.py --fit
 # Early end-to-end evaluator check on both slices before costly fitting.
 bash scripts/evaluate_train.sh > "$L/train_early.log" 2>&1
 bash scripts/evaluate_test.sh > "$L/test_early.log" 2>&1
 mark setup
fi
if ! stage reference; then
 bash scripts/method.sh > "$L/reference_fit.log" 2>&1
 mark reference
fi
if ! stage eval1; then
 evaluate train train1
 evaluate test test1
 mark eval1
fi
if ! stage eval2; then
 python eval/test/variants/refine_glue.py --register refined_glue --checkpoint checkpoints/hardening/table16_v600/latest.pkl --model "$S/geobpe_reference/model.json"
 python eval/test/seed_refinement.py
 python eval/test/prepare_probes.py
 evaluate train train2
 evaluate test test2
 (cd eval/test && python check_replay.py) > "$L/replay.log" 2>&1
 mark eval2
fi
if ! stage report; then
 python scripts/hardening_report.py > "$L/report.log" 2>&1
 cp scoring/scores_test.json redteam/audit_scores_test.json
 cp scoring/scores_train.json redteam/audit_scores_train.json
 mark report
fi
if ! stage package; then
 # Reference runs alone: the reproduced reference and the independent baseline.
 for d in "$S"/*; do n=$(basename "$d"); [[ "$n" == geobpe_reference || "$n" == internal_baseline ]] || archive "$n" "$n"; done
 export EVAL_RESCORE=1
 evaluate train train_final
 evaluate test test_final
 unset EVAL_RESCORE
 python scripts/package_scores.py > "$L/package.log" 2>&1
 mark package
fi
python validate.py
echo "== end $(date -u +%FT%TZ)"
