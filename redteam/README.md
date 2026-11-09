Run `bash redteam/run_all.sh` as a scheduled CPU job. Each case also has a
standalone `run.sh` that creates its method artifact, puts it at the evaluator's
default path, runs visible feedback, and invokes `bash scripts/evaluate_test.sh`
with **no arguments** in a new process. The evaluator and Python installation
are never changed. No process started by a candidate survives into its evaluator.

`scores_test.json`, `scores_train.json`, `status.json`, and `rank.json` are kept
in each case directory. Failures keep an error in `status.json` or `failure.json`.
Large reproducible intermediate artifacts and logs are ignored. Small result
JSON files are committed. The default artifact and score files are restored in
a `finally` block after every case.

The reference fixture in `cache/reference_artifact.json` is the original trained
output, reused only where explicitly permitted by the audit. If absent, the
runner rebuilds it with the visible official seed-0 method. The no-BPE shortcut
also rebuilds its initial vocabulary if needed. Honest runs use the visible official method.
Shortcut builders use only visible data, method output, and train feedback;
they do not read the hidden evaluator, hidden structure list, hidden scores, or
paper. The dictionary shortcut enumerates all visible held-out PDBs instead of
using any hidden selection information.

The rank formula uses experiment weights, coefficient **magnitudes**, and the
declared better directions. `analyze.py` calculates population standard
deviations over completed, finite, full-contract attempts. The later agent
population is unknown, so both this audit cohort and honest-control scales are
reported explicitly. Componentwise dominance conclusions hold for every
positive scale; an incomplete test output is not claimed to earn a rank.
