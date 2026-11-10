# Experiments

## short_backbones

Measure compact lossy coding on complete, unseen protein backbones with 64–192 residues. Report aligned backbone error, local distance preservation, complete transmitted bits per residue, and alphabet size. This tests whether a representation generalizes while balancing fidelity against storage. Private and public evaluation each use 64 chains.

## long_backbones

Measure the same quantities on complete, unseen backbones with 256–512 residues. Small local errors can accumulate into large global errors over long chains, so success on short inputs alone is insufficient. This experiment supplies scientific headroom below perfect reconstruction, with half the total experiment weight. Private and public evaluation each use 64 chains under the same selection rules.

A fixed representation is encoded on all 128 chains. Its dictionary storage is charged once across the corpus and apportioned by native residue count; each experiment also pays its own complete stream cost. Every method sees identical inputs, complete predictions are required, and both distortion and rate constraints must pass. Aggregate reference-only results are in scores_test.json and scores_train.json. Hardening controls and attack results are in HARDENING.md.
