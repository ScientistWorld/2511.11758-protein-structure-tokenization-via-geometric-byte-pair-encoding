# Experiments

## short_backbones

Measure compact lossy coding on complete, unseen protein backbones with 64–192 residues. Report aligned backbone error, local distance preservation, complete transmitted bits per residue, and alphabet size. This tests whether a representation generalizes while balancing fidelity against storage. Private evaluation uses 64 chains; the comparable public evaluation uses 32.

## long_backbones

Measure the same quantities on complete, unseen backbones with 256–512 residues. Small local errors can accumulate into large global errors over long chains, so success on short inputs alone is insufficient. This experiment supplies scientific headroom below perfect reconstruction, with half the total experiment weight. Private evaluation uses 64 chains; public evaluation uses 32 under the same selection rules.

A fixed representation is encoded separately on each experiment. Its dictionary storage is charged once in each experiment. Every method sees identical inputs, complete predictions are required, and both distortion and rate constraints must pass. Aggregate reference-only results are in scores_test.json and scores_train.json. Hardening controls and attack results are in HARDENING.md.
