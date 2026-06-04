# Constraints

Use the provided PDB splits unless explicitly documenting a new experiment. Do not train on the held-out split being evaluated.

Report token efficiency with the same encoded-token `bpr` proxy used by `eval/`: total tokens times `log2(vocab_size)` divided by total residues. The paper's full BPR additionally includes tokenizer description length; in this compact benchmark, `vocab_size` is reported alongside `bpr` to preserve a compactness constraint.

Do not improve scores by using private data, fetching extra files during evaluation, hardcoding held-out structures, or changing `scripts/evaluate.sh` to depend on a particular method implementation.

## Compliance Requirements

- Use the provided `data/pdb_smoke` train, CAMEO, and CASP14 splits for the benchmark experiments.
- Do not train, tune, or select vocabulary elements using the held-out split being evaluated.
- Do not fetch data, models, or remote resources during `scripts/evaluate.sh`.
- Keep `scripts/evaluate.sh` method-agnostic; evaluation code must not import from `method/`.
- Report `rmsd`, `lddt`, encoded-token `bpr`, and `vocab_size` for every submitted benchmark experiment.
- Do not improve reconstruction by memorizing held-out coordinates or using an unbounded vocabulary.
