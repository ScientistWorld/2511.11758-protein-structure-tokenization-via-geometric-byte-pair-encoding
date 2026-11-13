# Final hardening audit (generated)

Ranks apply the external rule to `scoring/scores_test.json` as written by `scripts/evaluate_test.sh`; failed attempts enter at the fixed worst values. Cohort standard deviations are population values. Paired 95% intervals use 1,000 bootstrap resamples of the same private inputs.

## test slice

| Attempt | Failed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab | Rank (all) | Rank (science) | Rank (paper line) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| closed_glue | False | 0.6884 | 0.9351 | 44.207 | 0.8440 | 0.9223 | 44.178 | 2100 | 1.0159 | 1.0159 | 1.0088 |
| closed_loop_internal | False | 0.3780 | 0.9626 | 26.282 | 0.4350 | 0.9580 | 26.218 | 159 | 1.7223 | 1.7223 | — |
| closed_loop_motif | False | 0.6657 | 0.9114 | 22.796 | 0.8030 | 0.8970 | 22.675 | 336 | 1.4160 | 1.4160 | — |
| closed_tokens | False | 0.0389 | 1.0000 | 44.207 | 0.0376 | 1.0000 | 44.178 | 2100 | 1.5640 | 1.5640 | 1.5499 |
| closed_tokens_compact | False | 0.3928 | 0.9614 | 26.802 | 0.5291 | 0.9504 | 26.680 | 676 | 1.6705 | 1.6705 | 1.6728 |
| compact_glue | False | 2.8524 | 0.6344 | 26.802 | 3.6292 | 0.5258 | 26.680 | 676 | -1.0328 | -1.0328 | -1.0000 |
| geobpe_reference | False | 1.9803 | 0.7557 | 44.207 | 1.5183 | 0.8241 | 44.178 | 2100 | 0.0000 | 0.0000 | 0.0000 |
| geobpe_seed1 | False | 1.9865 | 0.7553 | 44.207 | 1.5304 | 0.8230 | 44.178 | 2100 | -0.0061 | -0.0061 | -0.0060 |
| geobpe_seed2 | False | 1.9946 | 0.7546 | 44.207 | 1.5314 | 0.8195 | 44.178 | 2100 | -0.0188 | -0.0188 | -0.0185 |
| higher_capacity | False | 1.8947 | 0.7639 | 53.967 | 1.8838 | 0.7627 | 53.955 | 3173 | -0.4181 | -0.4181 | -0.4212 |
| internal_baseline | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -6.2026 | -6.2026 | -6.1340 |
| lower_capacity | False | 3.6908 | 0.6179 | 29.771 | 7.6112 | 0.4894 | 29.865 | 407 | -1.6581 | -1.6581 | -1.6099 |
| merge5 | False | 1.9807 | 0.7557 | 44.373 | 1.5194 | 0.8240 | 44.344 | 2107 | -0.0047 | -0.0047 | -0.0048 |
| no_bpe | False | 1.9807 | 0.7557 | 44.207 | 1.5194 | 0.8240 | 44.178 | 2100 | -0.0006 | -0.0006 | -0.0006 |
| open_glue | False | 1.9737 | 0.7983 | 44.207 | 5.1659 | 0.6825 | 44.178 | 2100 | -0.5587 | -0.5587 | -0.5393 |
| refined_glue | False | 1.2239 | 0.8365 | 44.207 | 0.9243 | 0.8893 | 44.178 | 2100 | 0.5556 | 0.5556 | 0.5498 |

Measured (unscored) metrics of failed attempts and failure reasons:

- `internal_baseline` — long_backbones: reconstruction constraint — measured: short_backbones: RMSD 7.6904, lDDT 0.5448, BPR 45.344; long_backbones: RMSD 19.8132, lDDT 0.4281, BPR 45.332

Paired 95% rank intervals versus the reference:

| Attempt | science cohort | paper-line cohort |
|---|---|---|
| closed_glue | [0.942, 1.0869] | [0.9349, 1.0787] |
| closed_loop_internal | [1.646, 1.7948] | — |
| closed_loop_motif | [1.3341, 1.4998] | — |
| closed_tokens | [1.511, 1.6128] | [1.497, 1.5985] |
| closed_tokens_compact | [1.5944, 1.7362] | [1.597, 1.738] |
| compact_glue | [-1.1442, -0.8956] | [-1.1111, -0.863] |
| geobpe_seed1 | [-0.0372, 0.0252] | [-0.0366, 0.0248] |
| geobpe_seed2 | [-0.0432, 0.0057] | [-0.0426, 0.0057] |
| higher_capacity | [-0.4583, -0.3764] | [-0.4605, -0.38] |
| lower_capacity | [-1.7863, -1.5385] | [-1.7353, -1.4928] |
| merge5 | [-0.0081, -0.001] | [-0.0082, -0.0011] |
| no_bpe | [-0.0039, 0.0032] | [-0.0039, 0.0032] |
| open_glue | [-0.6692, -0.4625] | [-0.6497, -0.4444] |
| refined_glue | [0.5288, 0.5797] | [0.5232, 0.5739] |

Reference metrics at a best bound: none.
Chains whose raw streams differ between the fresh reference and the earlier-host no-merge replay: None.

## train slice

| Attempt | Failed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab | Rank (all) | Rank (science) | Rank (paper line) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| closed_glue | False | 0.7703 | 0.9258 | 43.916 | 0.8302 | 0.9217 | 43.891 | 2100 | 0.9013 | 0.9013 | 0.8875 |
| closed_loop_internal | False | 0.3512 | 0.9641 | 26.265 | 0.4296 | 0.9605 | 26.210 | 159 | 1.6059 | 1.6059 | — |
| closed_loop_motif | False | 0.6892 | 0.9075 | 22.674 | 0.8524 | 0.8864 | 22.569 | 336 | 1.2611 | 1.2611 | — |
| closed_tokens | False | 0.0436 | 0.9999 | 43.916 | 0.0398 | 1.0000 | 43.891 | 2100 | 1.4503 | 1.4503 | 1.4257 |
| closed_tokens_compact | False | 0.4909 | 0.9453 | 26.559 | 0.4806 | 0.9572 | 26.454 | 676 | 1.5140 | 1.5140 | 1.5016 |
| compact_glue | False | 2.9920 | 0.6151 | 26.559 | 3.6040 | 0.5285 | 26.454 | 676 | -1.0511 | -1.0511 | -1.0151 |
| geobpe_reference | False | 1.9242 | 0.7610 | 43.916 | 1.5263 | 0.8235 | 43.891 | 2100 | 0.0000 | 0.0000 | 0.0000 |
| higher_capacity | False | 1.8066 | 0.7720 | 53.327 | 1.8973 | 0.7628 | 53.317 | 3173 | -0.3711 | -0.3711 | -0.3700 |
| internal_baseline | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -5.8469 | -5.8469 | -5.7340 |
| lower_capacity | False | 3.6064 | 0.6172 | 29.718 | 7.6759 | 0.4853 | 29.575 | 407 | -1.5905 | -1.5905 | -1.5363 |
| merge5 | False | 1.9179 | 0.7616 | 44.076 | 1.5263 | 0.8237 | 44.051 | 2107 | -0.0010 | -0.0010 | -0.0011 |
| no_bpe | False | 1.9179 | 0.7616 | 43.916 | 1.5263 | 0.8237 | 43.891 | 2100 | 0.0027 | 0.0027 | 0.0026 |
| open_glue | False | 2.4451 | 0.7698 | 43.916 | 5.3173 | 0.6871 | 43.891 | 2100 | -0.6668 | -0.6668 | -0.6433 |
| refined_glue | False | 1.2138 | 0.8393 | 43.916 | 0.9400 | 0.8891 | 43.891 | 2100 | 0.5111 | 0.5111 | 0.5019 |

Measured (unscored) metrics of failed attempts and failure reasons:

- `internal_baseline` — long_backbones: reconstruction constraint — measured: short_backbones: RMSD 8.8329, lDDT 0.5236, BPR 45.329; long_backbones: RMSD 19.4122, lDDT 0.4291, BPR 45.319

Reference metrics at a best bound: none.
Chains whose raw streams differ between the fresh reference and the earlier-host no-merge replay: None.

Forced four-input fresh replay: {"exact_raw_replay": true, "maximum_difference_by_experiment": {"long_backbones": {"bpr": 0.0, "lddt": 0.0, "rmsd": 0.0}, "short_backbones": {"bpr": 0.0, "lddt": 0.0, "rmsd": 0.0}}, "note": "Four-input forced fresh encoding on the job host versus the saved run; not a population confidence bound.", "paired_inputs": 4}

