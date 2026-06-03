# Evaluation

How success is measured. Describe only the metrics, targets, and evaluation procedure — do NOT describe the paper's method or how they achieved these results. Think of this as a general evaluation protocal for other scientists trying to solve the same problem, where they should not see this paper's solution.

## Metrics

<!-- What metrics are used? How are they computed? What does higher/lower mean? -->

## Baselines and Targets

<!-- What performance levels exist as reference points? Include the paper's reported numbers as targets, and any standard baselines. A scientist agent should know what "good" looks like. -->

## Evaluation Protocol

<!-- How should evaluation be run? What data split, what conditions? Any important details about how to compare fairly (e.g., fixed seeds, specific test sets, averaging over runs). -->
# Evaluation

Evaluation reads a method artifact, not method code. `scripts/evaluate.sh` calls only `eval/` and writes `scoring/scores.json`.

The main experiment is `scaled_pdb_tokenization`. Metrics are:

- `rmsd`: lower is better; backbone reconstruction RMSD after Kabsch alignment.
- `lddt`: higher is better; a dependency-free CA lDDT approximation.
- `bpr`: lower is better; bits per residue computed as token count times `log2(vocab_size)` divided by residue count.
- `vocab_size`: lower is better as a compactness constraint.

The reference values in `scoring/reference.json` are the paper's low-resolution GEOBPE values from Table 16. The reproduction uses a much smaller public PDB subset, so exact numerical agreement is not expected; the important signal is whether learned geometric merges improve compression while maintaining reconstruction quality.
