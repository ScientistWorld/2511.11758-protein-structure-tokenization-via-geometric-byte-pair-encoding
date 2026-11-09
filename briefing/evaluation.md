# Evaluation

Run `bash scripts/evaluate_train.sh` for public evaluation and `bash scripts/evaluate_test.sh` for private evaluation. Neither takes arguments. Each evaluates every `checkpoints/submissions/*/manifest.json` on disk through the same interface. No training runs during evaluation. The manifest supplies `model` (a JSON path) and `command` (an argument array). Command placeholders are `{model}`, `{request}`, and `{output}`. The request is a JSON list of `{id, path}` inputs; return a JSON list with exactly one full representation per id. Freeze the decoder dictionary before receiving the request.

The evaluator snapshots the model before invoking the encoder, decodes its symbols independently, and measures against evaluator-owned PDB coordinates. Results appear in `eval/train/ranking.json` or `eval/test/ranking.json`; full raw predictions remain in the corresponding `runs/` directory. Scalar quality claims, supplied targets, flags, counts, unknown fields, duplicate instances, nonfinite values, and partial reconstructions are rejected. `EVAL_RESCORE=1` reuses saved raw outputs when only evaluator code changed.

Supported finite output formats:

- Model `{"codec":"motif","motifs":[{"bonds":[...],"angles":[...],"torsions":[...]}],"glue":{"theta":[...],"omega":[...],"phi":[...]}}`. A row contains `id`, integer `motifs`, and one three-index `glue` entry per boundary, in theta/omega/phi order. Geometry uses radians and angstroms, with conventional internal-coordinate reconstruction. Every nonterminal entry spans a multiple of three bonds; the terminal entry spans two modulo three. All arrays together must decode exactly the input residue count.
- Model `{"codec":"internal","bins":[...]}` supplies nine finite alphabets: three bond-length, three bond-angle, and three torsion alphabets, cycling over the flattened N/CA/C chain. A row contains `id` and `indices`, a list of three integer arrays of lengths 3N−1, 3N−2, 3N−3. Each array cycles through its three alphabets.
- Model `{"codec":"cartesian"}` transmits a row with `id` and `coordinates`, a (3N,3) float32 array. All coordinate bits are charged; this diagnostic format generally exceeds the task rate limit.

All decoder floats are rounded to float32 and cost 32 bits. Description length includes 128 model header bits, 32 bits per dictionary array length, all dictionary floats, and 32 bits per chain header. Each discrete symbol costs max(1, ceil(log2(alphabet size))) bits. Dictionary cost is charged once per experiment, including unused entries, then divided by the actual native residue count. No continuous side information is free.

Both experiments report four quantities:

- `rmsd` ↓: mean complete-backbone error in angstroms after proper Kabsch alignment.
- `lddt` ↑: mean per-residue CA lDDT, with a 15 Å neighborhood and 0.5/1/2/4 Å tolerances.
- `bpr` ↓: full description length in bits per native residue.
- `vocab_size` ↓: total discrete dictionary and boundary alphabet size.

Every experiment must satisfy mean RMSD ≤15 Å, lDDT ≥0.35, 0<BPR≤96, and 1≤vocabulary≤8192. Malformed outputs or a failed constraint fail the whole attempt, which receives rank −10¹⁰⁰. Feasible attempts outrank all failures.

For feasible attempts, rank is the sum over metrics and experiments of experiment weight × absolute metric coefficient × signed improvement over the frozen reproduced reference / cohort standard deviation. The sign comes only from `higher_is_better`; a metric with zero cohort variation contributes zero. Standard deviations use feasible attempts on disk. Experiment weights are 0.5 each; coefficient magnitudes are RMSD 0.6, lDDT 1.0, BPR 0.4, vocabulary 0.02. Paired bootstrap intervals use the same inputs for all methods, with 1,000 fixed-seed resamples. The reference has rank zero. Rank magnitude changes with the cohort; scientific measurements do not.

The paper's reported numbers are retained separately in `scoring/reference.json` under `_paper_reported`; they are not targets on this scaled RCSB corpus. Evaluation comparison values, constraints, and dataset sizes are fixed inside eval/. Final `scoring/scores*.json` contain only the reproduced reference; audit variants and failed shortcuts are reported in HARDENING.md.
