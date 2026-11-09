#!/usr/bin/env bash
# Resume the combined hardening check after fixing float32 angle endpoints.
# Existing official checkpoints/caches are reused; no experiments are split up.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export GEOBPE_DATASET_WORKERS=1 SLURM_CPUS_PER_TASK=1 PYTHONHASHSEED=0 MPLBACKEND=Agg
mkdir -p logs/hardening
python scripts/check_codec.py
python method/train.py --name geobpe_reference --bins 500 --iterations 50 > logs/hardening/reference.log 2>&1
python method/train.py --name higher_capacity --bins 1000 --interior 100 --terminal 20 --iterations 50 > logs/hardening/higher.log 2>&1
python method/train.py --name lower_capacity --bins 50 --interior 5 --terminal 2 --iterations 50 > logs/hardening/lower.log 2>&1
python method/train.py --name no_bpe --export-only checkpoints/hardening/geobpe_reference/post_init.pkl
python baseline/internal.py --fit
python baseline/residue_quantized.py --fit
# Fresh final-code encoding on both sides, followed by one evaluator-only replay of attacks.
EVAL_FREEZE_REFERENCE=1 EVAL_REFERENCE_NAME=geobpe_reference bash scripts/evaluate_train.sh > logs/hardening/train.log 2>&1
EVAL_FREEZE_REFERENCE=1 EVAL_REFERENCE_NAME=geobpe_reference bash scripts/evaluate_test.sh > logs/hardening/test.log 2>&1
python eval/test/check_replay.py
python eval/test/prepare_probes.py
# Replay a pruned public selector too; hidden enumeration and experiments must stay complete.
python -c 'from pathlib import Path; Path("scoring/scores_train.json").write_text("{\"experiments\":{}}\n")'
EVAL_RESCORE=1 bash scripts/evaluate_test.sh > logs/hardening/probes.log 2>&1
python scripts/package_scores.py
python validate.py
