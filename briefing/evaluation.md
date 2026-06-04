# Evaluation

Evaluation reads a method artifact, not method code. `scripts/evaluate.sh` calls only `eval/` and writes `scoring/scores.json`. If an artifact contains `original_coords` and `reconstructed_coords`, the evaluator computes reconstruction metrics itself. Older smoke artifacts with only per-structure `rmsd` and `lddt` remain readable as diagnostics.

The main experiments are `scaled_pdb_tokenization_cameo` and `scaled_pdb_tokenization_casp14`. Metrics are:

- `rmsd`: lower is better; backbone reconstruction RMSD after Kabsch alignment.
- `lddt`: higher is better; a dependency-free CA lDDT approximation.
- `bpr`: lower is better; in this scaled gym, an encoded-token BPR proxy computed as token count times `log2(vocab_size)` divided by residue count.
- `vocab_size`: lower is better as a compactness constraint.

The reference values in `scoring/reference.json` are the paper's lowest-resolution reported values from Table 16 for the proposed structural tokenizer. The paper's full BPR includes tokenizer description length, while this compact benchmark uses the encoded-token term as a reproducible proxy and separately reports `vocab_size` as a compactness constraint. The reproduction uses a much smaller public PDB subset, so exact numerical agreement is not expected; the important signal is whether structural tokenization improves compression while maintaining reconstruction quality.
