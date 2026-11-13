#!/usr/bin/env bash
# Final hardening audit for this iteration. Stage markers make preemption restarts resume.
#  smoke    new closed-loop tokenizer probe on two public chains (diagnostic only)
#  fit      fresh end-to-end refit of the reference from final code (compared with the
#           previous fit byte for byte) and of the fixed-bin baseline
#  eval_ref fresh encoding and scoring of the reference and baseline on both slices
#  probes   hidden probes and archived variants scored on both slices; reference reused
#  report   ranks and paired intervals from the evaluator-written score files
#  package  reference-only score files, scoring/reference.json, validation
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export GEOBPE_DATASET_WORKERS=1 SLURM_CPUS_PER_TASK=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
export PYTHONWARNINGS=ignore::FutureWarning
unset EVAL_RESCORE
L=logs/hardening3; S=checkpoints/submissions; A=checkpoints/audit_archive; H=checkpoints/hardening
CK=$H/table16_v600/latest.pkl
GLUE="open_glue:open closed_glue:closed compact_glue:compact closed_tokens:tokens closed_tokens_compact:tokens_compact"
NEW="open_glue closed_glue compact_glue closed_tokens closed_tokens_compact closed_loop_motif closed_loop_internal"
OLD="refined_glue lower_capacity higher_capacity merge5 no_bpe geobpe_seed1 geobpe_seed2"
mkdir -p "$L" "$A"
stage(){ [[ -f "$L/$1.done" ]]; }
mark(){ touch "$L/$1.done"; echo "== stage $1 done $(date -u +%FT%TZ)"; }
ref_ok(){ python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); sys.exit(0 if "geobpe_reference" in s["experiments"]["short_backbones"]["results"] and "geobpe_reference" not in s["_metadata"]["failed"] else 1)' "$1"; }
evaluate(){ # slice, log prefix: retry while the resumable reference encode is unfinished
 for attempt in 1 2 3 4; do
  bash "scripts/evaluate_$1.sh" > "$L/$2_$attempt.log" 2>&1
  if ref_ok "scoring/scores_$1.json"; then return 0; fi
  echo "reference not complete on $1 after pass $attempt"
 done
 echo "reference failed on $1"; return 1
}
archive(){ # move submission $1 and its runs into the audit archive
 [[ -d "$S/$1" ]] || return 0
 rm -rf "$A/$1"; mv "$S/$1" "$A/$1"
 for side in train test; do
  if [[ -d "eval/$side/runs/$1" ]]; then mkdir -p "$A/runs_$side"; rm -rf "$A/runs_$side/$1"; mv "eval/$side/runs/$1" "$A/runs_$side/$1"; fi
 done
}
echo "== start $(date -u +%FT%TZ)"
if ! stage smoke; then
 python - > "$L/smoke.log" 2>&1 <<'EOF' || echo "smoke test failed (see $L/smoke.log)"
import json,sys
sys.path.insert(0,'eval/test/variants'); sys.path.insert(0,'eval/train')
import glue_loop as g, evaluate as ev
import numpy as np
model=json.load(open('checkpoints/submissions/geobpe_reference/model.json'))
f32=lambda v:np.asarray(v,dtype=np.float32).astype(float).tolist()
motifs=[(f32(m['bonds']),f32(m['angles']),f32(m['torsions'])) for m in model['motifs']]
G=[np.asarray(f32(model['glue'][k])) for k in ('theta','omega','phi')]
dec,_,_=ev.load_model(model)
rows={r['id']:r for r in json.load(open('eval/train/runs/geobpe_reference/outputs.json'))}
for req in json.load(open('eval/train/runs/geobpe_reference/request.json'))[:2]:
 nat=g.coordinates(req['path']); ids=rows[req['id']]['motifs']; n=len(nat)//3
 for mode in ('reference','closed','tokens'):
  if mode=='reference': row=rows[req['id']]
  elif mode=='closed': row={'id':req['id'],'motifs':ids,'glue':g.encode_closed(nat,ids,motifs,G)}
  else: i2,gl=g.encode_tokens(nat,ids[0],motifs,G); row={'id':req['id'],'motifs':i2,'glue':gl}
  x,bits=ev.decode(row,dec,n); print(req['id'],mode,'RMSD/lDDT',ev.quality(ev.parse_backbone(open(req['path']).read()),x),'bits/res',bits/n,flush=True)
EOF
 cat "$L/smoke.log"; mark smoke
fi
if ! stage fit; then
 # Fresh refit from final code; the previous fit is kept for a byte comparison.
 [[ -f "$L/model_prev.json" ]] || cp "$S/geobpe_reference/model.json" "$L/model_prev.json"
 if [[ -d "$H/table16_v600" && ! -d "$H/table16_v600_prev" ]]; then mv "$H/table16_v600" "$H/table16_v600_prev"; fi
 bash scripts/method.sh > "$L/fit.log" 2>&1
 python baseline/internal.py --fit
 if cmp -s "$S/geobpe_reference/model.json" "$L/model_prev.json"; then echo "refit model.json identical to previous fit"; else echo "refit model.json DIFFERS from previous fit"; fi
 if cmp -s "$CK" "$H/table16_v600_prev/latest.pkl"; then echo "refit checkpoint identical"; else echo "refit checkpoint bytes differ (pickle)"; fi
 mark fit
fi
if ! stage eval_ref; then
 if [[ ! -f "$L/eval_ref.started" ]]; then
  for side in train test; do rm -f eval/$side/runs/geobpe_reference/outputs*.json eval/$side/runs/internal_baseline/outputs*.json; done
  touch "$L/eval_ref.started"
 fi
 evaluate train train_ref
 evaluate test test_ref
 cp scoring/scores_train.json "$L/scores_train_ref.json"; cp scoring/scores_test.json "$L/scores_test_ref.json"
 mark eval_ref
fi
if ! stage probes; then
 if [[ ! -f "$L/probes.started" ]]; then
  for n in $NEW; do rm -rf "$S/$n" "$A/$n"; for side in train test; do rm -rf "eval/$side/runs/$n"; done; done
  for spec in $GLUE; do
   python eval/test/variants/glue_loop.py --register "${spec%%:*}" --mode "${spec##*:}" --checkpoint "$CK" --base-model "$S/geobpe_reference/model.json"
  done
  python eval/test/variants/closed_loop_motif.py --fit
  python eval/test/variants/closed_loop.py --fit
  # The probes reuse the fresh reference's own motif streams through encoder recovery.
  for side in train test; do
   for spec in $GLUE; do n="${spec%%:*}"; mkdir -p "eval/$side/runs/$n"; cp "eval/$side/runs/geobpe_reference/outputs.resume.json" "eval/$side/runs/$n/outputs.base.resume.json"; done
  done
  touch "$L/probes.started"
 fi
 export EVAL_RESCORE=1
 for side in train test; do
  for n in $OLD; do
   rm -rf "$S/$n"
   if [[ -f "$A/runs_$side/$n/outputs.json" ]]; then rm -rf "eval/$side/runs/$n"; cp -r "$A/$n" "$S/$n"; cp -r "$A/runs_$side/$n" "eval/$side/runs/$n"; fi
  done
  evaluate "$side" "${side}_probes"
  cp "scoring/scores_$side.json" "redteam/audit_scores_$side.json"
  python scripts/rank_summary.py "scoring/scores_$side.json" | tee "$L/ranks_$side.md"
  for n in $OLD; do rm -rf "$S/$n" "eval/$side/runs/$n"; done
 done
 unset EVAL_RESCORE
 for n in $NEW; do for side in train test; do grep -h "Traceback\|Error" "eval/$side/runs/$n/encoder.log" 2>/dev/null | head -3 || true; done; done
 mark probes
fi
if ! stage report; then
 # Score files and measurements of both slices still hold the full audit cohort.
 for side in train test; do cp "redteam/audit_scores_$side.json" "scoring/scores_$side.json"; done
 python scripts/hardening_report.py > "$L/report.log" 2>&1 || { echo "report failed"; tail -20 "$L/report.log"; }
 mark report
fi
if ! stage package; then
 # Reference runs alone: the reproduced reference and the independent baseline.
 for d in "$S"/*; do n=$(basename "$d"); [[ "$n" == geobpe_reference || "$n" == internal_baseline ]] || archive "$n"; done
 export EVAL_RESCORE=1
 evaluate train train_final
 evaluate test test_final
 unset EVAL_RESCORE
 python scripts/package_scores.py > "$L/package.log" 2>&1
 mark package
fi
python validate.py
echo "== end $(date -u +%FT%TZ)"
