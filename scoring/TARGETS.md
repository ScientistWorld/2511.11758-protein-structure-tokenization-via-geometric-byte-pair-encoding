# Targets

Optimize `scaled_pdb_tokenization_cameo` and `scaled_pdb_tokenization_casp14`.

The current benchmark can score two reproduced operating points when both artifacts are available:

- `geobpe_table16_high`: higher-capacity structural vocabulary regime.
- `geobpe_table16_low`: lower-capacity structural vocabulary regime.

Primary target: increase `lddt` on held-out PDB chains for both splits. In this compact public-data gym, lDDT is the primary reconstruction-quality signal because it is stable on small held-out slices and measures whether local backbone geometry is preserved.

Secondary targets: reduce global-coordinate `rmsd`, reduce the encoded-token `bpr` proxy, and keep `vocab_size` compact. A valid improvement should not simply expand the vocabulary until every local fragment is memorized.
