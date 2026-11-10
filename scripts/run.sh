#!/usr/bin/env bash
# One combined final repair audit. All changed models run from final code;
# unchanged models reuse saved raw streams, never their claimed measurements.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export GEOBPE_DATASET_WORKERS=1 SLURM_CPUS_PER_TASK=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
export PYTHONWARNINGS=ignore::FutureWarning
mkdir -p logs/hardening
python scripts/check_refinement.py
python scripts/check_codec.py
bash scripts/method.sh > logs/hardening/main_reference.log 2>&1
python method/train.py --name no_bpe --export-only checkpoints/hardening/main_compression/post_init.pkl
python baseline/internal.py --fit
python baseline/residue_quantized.py --fit
# Defer the refinement application until both final reference starting points exist.
if [[ -f checkpoints/submissions/refined_glue/manifest.json ]]; then
 mv checkpoints/submissions/refined_glue/manifest.json checkpoints/submissions/refined_glue/manifest.audit.json
fi
EVAL_FREEZE_REFERENCE=1 EVAL_REFERENCE_NAME=geobpe_reference bash scripts/evaluate_train.sh > logs/hardening/train.log 2>&1
EVAL_FREEZE_REFERENCE=1 EVAL_REFERENCE_NAME=geobpe_reference bash scripts/evaluate_test.sh > logs/hardening/test.log 2>&1
python method/refine.py --register refined_glue --checkpoint checkpoints/hardening/main_compression/latest.pkl --model checkpoints/submissions/geobpe_reference/model.json
python eval/test/seed_refinement.py
# Normal application resumes partial refinement per chain if the job was preempted.
# The released encoders immediately recover their unchanged complete raw streams.
EVAL_FREEZE_REFERENCE=1 EVAL_REFERENCE_NAME=geobpe_reference bash scripts/evaluate_train.sh > logs/hardening/train_refined.log 2>&1
EVAL_FREEZE_REFERENCE=1 EVAL_REFERENCE_NAME=geobpe_reference bash scripts/evaluate_test.sh > logs/hardening/test_refined.log 2>&1
python eval/test/prepare_probes.py
python -c 'from pathlib import Path; Path("scoring/scores_train.json").write_text("{\"experiments\":{}}\n")'
EVAL_RESCORE=1 bash scripts/evaluate_test.sh > logs/hardening/probes.log 2>&1
python eval/test/check_replay.py
python scripts/package_scores.py
python validate.py
