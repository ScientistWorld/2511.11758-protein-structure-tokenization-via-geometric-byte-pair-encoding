# Targets

Optimize `scaled_pdb_tokenization_cameo` and `scaled_pdb_tokenization_casp14`.

The current benchmark scores two paper-reported GEOBPE resolution settings when both artifacts are available:

- `geobpe_table16_high`: Table 16 setting `{2:10,3:50,5:1,6:5,8:1}`, compared with the `|V|=237` checkpoint row.
- `geobpe_table16_low`: Table 16 setting `{2:2,3:5,5:1,6:2,8:1}`, compared with the `|V|=109` checkpoint row.

Primary target: reduce `rmsd` on held-out PDB chains for both splits.

Secondary targets: increase `lddt`, reduce the encoded-token `bpr` proxy, and keep `vocab_size` compact. A valid improvement should not simply expand the vocabulary until every local fragment is memorized.
