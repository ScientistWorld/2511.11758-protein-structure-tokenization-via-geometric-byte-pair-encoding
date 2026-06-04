# Verification Report

## Initial Assessment

The workspace started at `core_claim`. That milestone is justified: the runnable artifact in `checkpoints/geobpe_scaled_multisplit/results.json` comes from the official PT-BPE GEOBPE implementation path, and the evaluator scores held-out CAMEO and CASP14 splits on reconstruction quality plus compactness constraints.

## Issues Found

- Critical: an unrun glue-optimization ablation had been added to the scoring contract and target docs, but no corresponding results existed in `scoring/scores.json`. A future scientist would have seen a phantom target that the gym could not score.
- Minor: several scoring guidance files still contained large template comment blocks, and `briefing/evaluation.md` named the paper method in a method-agnostic context.
- Minor: `scripts/reproduce.sh` still defaulted to an older smoke-scale artifact path rather than the multisplit artifact used for the current core-claim scores.

## Fixes Applied

- Removed the unrun ablation from `scoring/reference.json`, `scoring/TARGETS.md`, `scoring/EXPERIMENTS.md`, and `scoring/CONSTRAINTS.md`, and deleted the unused ablation runner/combiner files.
- Cleaned method-agnostic documentation in `briefing/evaluation.md` and the scoring guidance files.
- Updated `scripts/reproduce.sh` so its default end-to-end run targets the multisplit core-claim setting.
- Verified all URLs in `scripts/download.sh` return HTTP 200, confirmed there are no committed `shared/` path references, reran `scripts/evaluate.sh`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and confirmed `python validate.py --compare` passes.

## Final Judgment

The workspace is ready to serve as a compact research gym. Improve-mode agents can work from the reproduced method artifact and code, while from-scratch agents can use the method-agnostic problem, data, and evaluation interface without importing from `method/`.

- Milestone: core_claim
- Ready for gym use: yes
- Confidence: medium
- Key limitation: compact public PDB subset only; broader table sweeps and ablations remain future work.
