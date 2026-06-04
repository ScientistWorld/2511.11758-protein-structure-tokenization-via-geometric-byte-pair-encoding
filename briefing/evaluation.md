# Evaluation

Evaluation reads a method artifact, not method code. `scripts/evaluate.sh` calls only `eval/` and writes `scoring/scores.json`. Artifacts that report reconstruction quality must include `original_coords` and `reconstructed_coords`; the evaluator recomputes RMSD and lDDT from those coordinates instead of trusting precomputed metric fields.

The main experiments are `scaled_pdb_tokenization_cameo` and `scaled_pdb_tokenization_casp14`. Metrics are:

- `lddt`: higher is better; the primary reconstruction-quality metric, computed as a dependency-free CA lDDT approximation.
- `rmsd`: lower is better; a secondary global backbone reconstruction metric after Kabsch alignment.
- `bpr`: lower is better; in this scaled gym, an encoded-token BPR proxy computed as token count times `log2(vocab_size)` divided by residue count.
- `vocab_size`: lower is better as a compactness constraint.

The reference values in `scoring/reference.json` are paper-reported structural-tokenizer results for two vocabulary-size regimes. The paper's full BPR includes tokenizer description length, while this compact benchmark uses the encoded-token term as a reproducible proxy and separately reports `vocab_size` as a compactness constraint. The reproduction uses a much smaller public PDB subset, so exact numerical agreement is not expected; the important signal is whether structural tokenization improves compression while maintaining reconstruction quality across operating points.
