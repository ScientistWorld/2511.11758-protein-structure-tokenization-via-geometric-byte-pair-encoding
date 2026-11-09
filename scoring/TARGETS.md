# Targets

Both scored experiments are `short_backbones` and `long_backbones`, weighted equally. Each has the same four scored quantities: increase `lddt`; decrease `rmsd`, full `bpr`, and `vocab_size`. All four appear in every reference score entry and are described in EXPERIMENTS.md.

Improve the rate–distortion tradeoff on previously unseen complete backbones. Do not optimize agreement with published numbers. Finite dictionaries and all per-input side information incur storage cost. Longer backbones specifically test reconstruction drift where local accuracy alone is insufficient.
