# Train/Test Evaluation Design Notes

Checked the train/test split scripts, slice evaluators, scoring metadata, and leakage/static failure modes for the GEOBPE protein backbone tokenization benchmark.

Changes made:

- Fixed a row-omission shortcut. The previous slice evaluators scored whatever `structures` rows a method emitted, so a future method could omit hard chains and improve averages. `eval/train/evaluate.py` and `eval/test/evaluate.py` now require fixed per-experiment structure names and fail if any required row is missing.
- Reduced train-to-test leakage. The visible train evaluator no longer exposes the hash split seed/rule that generated the held-out rows. Train and test now carry only their own required structure lists.
- Added duplicate-row validation so repeated structure names fail explicitly instead of being silently collapsed or reweighted.
- Completed `scoring/reference.json` metric schema by adding required descriptions for `rmsd`, `lddt`, `bpr`, and `vocab_size` in both experiments.
- Removed generated `eval/__pycache__` artifacts from the source tree.

Static checks performed:

- `bash -n scripts/evaluate_train.sh`
- `bash -n scripts/evaluate_test.sh`
- `python -m json.tool scoring/reference.json`
- Confirmed `scoring/scores_train.json` and `scoring/scores_test.json` are absent.
- Grepped for train/test cross-imports, hardcoded `METHOD_NAME`, score path copy-paste errors, and paper-agreement metric names.

Runtime concerns for the next iteration:

- I did not run either evaluator, per the file-edit-only instruction. The next runner should confirm that the current method artifact contains all required names and still produces `scores_train.json`/`scores_test.json`.
- Each experiment has only five held-out structures total, split into two or three rows per slice. The multi-metric scoring helps, but the test signal remains small and may have high variance.
- The scripts still default to `checkpoints/geobpe_scaled_multisplit/results.json`; future methods can pass another artifact path, but the runner should confirm improve-mode documentation makes that contract clear.
