# Final hardening audit (generated)

Ranks apply the external rule to `scoring/scores_test.json` as written by `scripts/evaluate_test.sh`; failed attempts enter at the fixed worst values. Cohort standard deviations are population values. Paired 95% intervals use 1,000 bootstrap resamples of the same private inputs.

## test slice

| Attempt | Failed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab | Rank (all) | Rank (science) | Rank (science w/o closed loop) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| attack_constant_template | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_crash | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_forged_counts | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_forged_target | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_negative_counts | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_prune_comparison | False | 1.9803 | 0.7557 | 44.207 | 1.5183 | 0.8241 | 44.178 | 2100 | 0.0000 | — | — |
| attack_public_dictionary | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_quality_fields | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_tamper_reference | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_tamper_target | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| attack_truncated | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | — | — |
| closed_loop_internal | False | 0.3780 | 0.9626 | 26.282 | 0.4350 | 0.9580 | 26.218 | 159 | 1.1639 | 1.2815 | — |
| geobpe_reference | False | 1.9803 | 0.7557 | 44.207 | 1.5183 | 0.8241 | 44.178 | 2100 | 0.0000 | 0.0000 | 0.0000 |
| higher_capacity | False | 1.8947 | 0.7639 | 53.967 | 1.8838 | 0.7627 | 53.955 | 3173 | -0.2750 | -0.3020 | -0.3094 |
| internal_baseline | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | -4.4191 | -4.5506 |
| lower_capacity | False | 3.6908 | 0.6179 | 29.771 | 7.6112 | 0.4894 | 29.865 | 407 | -1.1731 | -1.2698 | -1.3161 |
| merge5 | False | 1.9807 | 0.7557 | 44.373 | 1.5194 | 0.8240 | 44.344 | 2107 | -0.0029 | -0.0033 | -0.0033 |
| no_bpe | False | 1.9807 | 0.7557 | 44.207 | 1.5194 | 0.8240 | 44.178 | 2100 | -0.0004 | -0.0005 | -0.0005 |
| refined_glue | False | 1.2239 | 0.8365 | 44.207 | 0.9243 | 0.8893 | 44.178 | 2100 | 0.3885 | 0.4244 | 0.4469 |
| supplied_baseline | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9790 | -4.4191 | -4.5506 |

Measured (unscored) metrics of failed attempts and failure reasons:

- `attack_constant_template` — ValueError: invalid full coordinate output — measured: not measurable
- `attack_crash` — CalledProcessError: Command '['python', 'eval/test/probes.py', '--attack', 'crash', '--request', '/home/user/eval/test/runs/attack_crash/request.json', '--output', '/home/user/eval/test/runs/attack_crash/outputs.json', '--model', '/home/user/eval/test/runs/attack_crash/model.json']' returned non-zero exit status 1. — measured: not measurable
- `attack_forged_counts` — ValueError: representation fields do not match codec — measured: not measurable
- `attack_forged_target` — ValueError: representation fields do not match codec — measured: not measurable
- `attack_negative_counts` — ValueError: invalid stream lengths — measured: not measurable
- `attack_public_dictionary` — ValueError: reconstruction does not cover the complete chain — measured: not measurable
- `attack_quality_fields` — ValueError: representation fields do not match codec — measured: not measurable
- `attack_tamper_reference` — ValueError: attempt modified evaluation or comparison files: scoring/reference.json — measured: not measurable
- `attack_tamper_target` — ValueError: attempt modified evaluation or comparison files: eval/test/downloads/short/2zsn_A.pdb — measured: not measurable
- `attack_truncated` — ValueError: invalid full coordinate output — measured: not measurable
- `internal_baseline` — long_backbones: reconstruction constraint — measured: short_backbones: RMSD 7.6904, lDDT 0.5448, BPR 45.344; long_backbones: RMSD 19.8132, lDDT 0.4281, BPR 45.332
- `supplied_baseline` — short_backbones: rate/dictionary constraint; long_backbones: rate/dictionary constraint — measured: short_backbones: RMSD 0.0108, lDDT 1.0000, BPR 288.282; long_backbones: RMSD 0.0101, lDDT 1.0000, BPR 288.097

Paired 95% rank intervals versus the reference:

| Attempt | science cohort | science w/o closed loop |
|---|---|---|
| closed_loop_internal | [1.2227, 1.3374] | — |
| higher_capacity | [-0.3329, -0.2696] | [-0.3418, -0.2759] |
| lower_capacity | [-1.3626, -1.1818] | [-1.4113, -1.2258] |
| merge5 | [-0.0058, -0.0003] | [-0.0061, -0.0003] |
| no_bpe | [-0.003, 0.0024] | [-0.0032, 0.0026] |
| refined_glue | [0.4038, 0.4433] | [0.425, 0.467] |

Reference metrics at a best bound: none.
Chains whose raw streams differ between the fresh reference and the earlier-host no-merge replay: 89.

## train slice

| Attempt | Failed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab | Rank (all) | Rank (science) | Rank (science w/o closed loop) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| attack_constant_template | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_crash | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_forged_counts | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_forged_target | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_negative_counts | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_prune_comparison | False | 1.9242 | 0.7610 | 43.916 | 1.5263 | 0.8235 | 43.891 | 2100 | 0.0000 | — | — |
| attack_public_dictionary | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_quality_fields | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_tamper_reference | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_tamper_target | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| attack_truncated | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | — | — |
| closed_loop_internal | False | 0.3512 | 0.9641 | 26.265 | 0.4296 | 0.9605 | 26.210 | 159 | 1.1510 | 1.2673 | — |
| geobpe_reference | False | 1.9242 | 0.7610 | 43.916 | 1.5263 | 0.8235 | 43.891 | 2100 | 0.0000 | 0.0000 | 0.0000 |
| higher_capacity | False | 1.8066 | 0.7720 | 53.327 | 1.8973 | 0.7628 | 53.317 | 3173 | -0.2602 | -0.2854 | -0.2920 |
| internal_baseline | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | -4.4220 | -4.5485 |
| lower_capacity | False | 3.6064 | 0.6172 | 29.718 | 7.6759 | 0.4853 | 29.575 | 407 | -1.1949 | -1.2916 | -1.3392 |
| merge5 | False | 1.9179 | 0.7616 | 44.076 | 1.5263 | 0.8237 | 44.051 | 2107 | -0.0004 | -0.0005 | -0.0005 |
| no_bpe | False | 1.9179 | 0.7616 | 43.916 | 1.5263 | 0.8237 | 43.891 | 2100 | 0.0019 | 0.0021 | 0.0023 |
| refined_glue | False | 1.2138 | 0.8393 | 43.916 | 0.9400 | 0.8891 | 43.891 | 2100 | 0.3792 | 0.4138 | 0.4350 |
| supplied_baseline | True | 15.0000 | 0.3500 | 96.000 | 15.0000 | 0.3500 | 96.000 | 8192 | -3.9816 | -4.4220 | -4.5485 |

Measured (unscored) metrics of failed attempts and failure reasons:

- `attack_constant_template` — ValueError: invalid full coordinate output — measured: not measurable
- `attack_crash` — CalledProcessError: Command '['python', 'eval/test/probes.py', '--attack', 'crash', '--request', '/home/user/eval/train/runs/attack_crash/request.json', '--output', '/home/user/eval/train/runs/attack_crash/outputs.json', '--model', '/home/user/eval/train/runs/attack_crash/model.json']' returned non-zero exit status 1. — measured: not measurable
- `attack_forged_counts` — ValueError: representation fields do not match codec — measured: not measurable
- `attack_forged_target` — ValueError: representation fields do not match codec — measured: not measurable
- `attack_negative_counts` — ValueError: invalid stream lengths — measured: not measurable
- `attack_public_dictionary` — ValueError: reconstruction does not cover the complete chain — measured: not measurable
- `attack_quality_fields` — ValueError: representation fields do not match codec — measured: not measurable
- `attack_tamper_reference` — ValueError: attempt modified evaluation or comparison files: scoring/reference.json — measured: not measurable
- `attack_tamper_target` — ValueError: attempt modified evaluation or comparison files: data/downloads/pdb/visible_short/3ivq_A.pdb — measured: not measurable
- `attack_truncated` — ValueError: invalid full coordinate output — measured: not measurable
- `internal_baseline` — long_backbones: reconstruction constraint — measured: short_backbones: RMSD 8.8329, lDDT 0.5236, BPR 45.329; long_backbones: RMSD 19.4122, lDDT 0.4291, BPR 45.319
- `supplied_baseline` — short_backbones: rate/dictionary constraint; long_backbones: rate/dictionary constraint — measured: short_backbones: RMSD 0.0111, lDDT 1.0000, BPR 288.255; long_backbones: RMSD 0.0101, lDDT 1.0000, BPR 288.095

Reference metrics at a best bound: none.
Chains whose raw streams differ between the fresh reference and the earlier-host no-merge replay: 93.

Forced four-input fresh replay: {"exact_raw_replay": true, "maximum_difference_by_experiment": {"long_backbones": {"bpr": 0.0, "lddt": 0.0, "rmsd": 0.0}, "short_backbones": {"bpr": 0.0, "lddt": 0.0, "rmsd": 0.0}}, "note": "Four-input forced fresh encoding on the job host versus the saved run; not a population confidence bound.", "paired_inputs": 4}

