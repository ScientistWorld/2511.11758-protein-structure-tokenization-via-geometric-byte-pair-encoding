# Experiments

## scaled_pdb_tokenization_cameo

This experiment tests whether structural vocabularies at multiple operating points can encode held-out CAMEO protein backbones compactly while preserving geometric reconstruction quality. The evaluator compares reconstructed coordinates with the original backbone and reports RMSD, lDDT, an encoded-token bits-per-residue proxy, and vocabulary size.

The experiment is intentionally small so future agents can iterate quickly. It should still preserve the central tradeoff: better tokenizers must improve reconstruction or token efficiency without using an unbounded vocabulary.

## scaled_pdb_tokenization_casp14

This experiment tests whether structural tokenization remains useful on a second held-out split from CASP14 across the same operating points. It measures the same reconstruction, locality-preservation, token-efficiency, and compactness quantities as the CAMEO split.

The experiment is intentionally small so future agents can iterate quickly. It should still preserve the central tradeoff: better tokenizers must improve reconstruction or token efficiency without using an unbounded vocabulary.
