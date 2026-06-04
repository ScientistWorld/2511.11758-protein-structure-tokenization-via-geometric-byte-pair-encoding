# Verification Report

## Initial Assessment

The workspace started at `core_claim`. That milestone remains justified: the submitted method path uses the official PT-BPE implementation, produces held-out CAMEO and CASP14 artifacts, and the evaluator scores reconstruction quality plus compactness from method outputs without importing from `method/`.

## Issues Found

- Minor: method-agnostic documentation leaked solution-specific vocabulary in `briefing/evaluation.md` and `scoring/TARGETS.md`.
- Minor: `scripts/evaluate.sh`, `scripts/evaluate_train.sh`, `scripts/evaluate_test.sh`, and their Python entry points defaulted to the older unrenamed artifact instead of the current scored sweep artifact.
- Minor: `method/run_official_geobpe.py` printed full coordinate artifacts to stdout, making job logs unnecessarily large.
- Minor: `README.md` is mounted as `/dev/null` (`devtmpfs[/null]`) in this environment and cannot be replaced from the workspace. It remains an external system-state caveat; the gym documentation lives in `briefing/`, `scoring/`, `PROGRESS.md`, and `MILESTONES.md`.

## Fixes Applied

- Rephrased method-agnostic docs to describe structural-tokenization operating points without naming internal method knobs.
- Updated evaluator defaults to `checkpoints/geobpe_table16_sweep/results.json`, matching the current scored artifact format.
- Added explicit notes in `scoring/reference.json` explaining that paper BPR values are full description-length BPR while the compact gym computes an encoded-token proxy.
- Changed the method wrapper to print a compact artifact summary instead of full coordinate arrays.
- Verified all `scripts/download.sh` RCSB URLs with `curl -I -L --max-time 15`; every URL returned HTTP 200.
- Confirmed there are no `shared/` references in committed method/eval/baseline/script/data files and no `eval/` imports from `method/`.

## Final Judgment

The workspace is ready to serve as a compact research gym. Improve-mode agents can build on the official-method reproduction, while from-scratch agents can use the data and method-agnostic evaluation contract without depending on the paper implementation.

- Milestone: core_claim
- Ready for gym use: yes
- Confidence: medium
- Key limitation: compact public PDB subset only; broader vocabulary sweeps and ablations remain future work.
