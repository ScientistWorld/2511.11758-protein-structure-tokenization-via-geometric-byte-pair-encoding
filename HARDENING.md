# Hardening audit

The final test rewards a demonstrated fidelity improvement at fixed rate: `refined_glue` ranks +1.25409 (paired 95% interval [1.195446, 1.319235]), while the weaker control ranks −2.95926. The reference passes every task constraint and has no scored metric at its best bound. Four forced fresh paired encodings matched exactly; this small replay diagnostic is not a general population noise bound. The remaining limitation is that learned merges provide no held-out geometric benefit at this corpus size.

The first combined job passed the independent decoder checks but stopped before fitting on a float32 +/-pi range-check incompatibility in the released PDB loader. This was repaired with a 1e-6 roundoff tolerance and clipping to the physical interval; no chains were removed and no algorithmic settings were changed. The resumed combined audit also checks complete public-corpus parsing before fitting.

The resumed job `56ca3ebd-e4c` completed all three 50-round training runs, but scheduler preemptions repeatedly restarted inference and overwrote its partial streams. It was cancelled to add atomic per-chain recovery, with checkpoint/dictionary/code/input fingerprints. Completed training and unchanged-chain raw outputs are retained; every score is recomputed. The forced four-input inference replay bypasses recovery. Repeated pandas FutureWarnings are suppressed without changing the released numerical operations.

Partial public measurements exposed a size mismatch: full dictionary storage was divided across 32 public versus 64 private chains. The larger vocabulary therefore failed the public rate gate while the private corpus amortized the same dictionary twice as far. Public evaluation was enlarged to 64 unseen chains in each range before the resumed combined audit. Fitting inputs, operating limits, coefficients, and private data were unchanged. New public sources exclude private sources and exact sequences; only the test-side acquisition helper reads the private exclusion list.

## Report and decisions

The original REDTEAM report found a strong genuine improvement (`better_bins300`, audit/control ranks +0.693188/+0.629933) and a clearly worse low-capacity variant (−1.238218/−3.488790). The old reference's seed-to-seed rank range was 0.128686/0.359406, while the translation-weight change was below that range. Its three merge rounds did not affect held-out geometry: the no-merge alternative tied reconstruction and slightly improved the flawed rate proxy. This is an honest headroom problem, not an exploit to prohibit.

The report also found that the test trusted supplied targets, sizes, and token/vocabulary counts, omitted boundary information and dictionary cost, accepted negative counts, truncated predictions to the smaller length, and took experiment selection from a mutable public score file. Five public test chains let a ten-entry dictionary memorize all answers. The supplied baseline transmitted exact native frames without charging them and dominated the reference.

All fixes were decided together before a single combined compute job. Final-code reference, stronger and weaker variants, no-merge control, independent baseline, and former supplied baseline are rerun; evaluator-only attacks reuse the final reference raw outputs. No training is performed by the hidden test. The test does not defend against leftover processes or Python environment changes.

## Changes

The test owns targets, size, thresholds, reference measurements, representation decoder, and rank contract. It decodes raw symbols and recomputes every scientific quantity; method-written metrics, targets, sizes, and flags are never consumed. Complete-chain checks reject truncation, unknown fields and invalid symbols fail, and feasibility gates place every failed attempt below every successful one. All finite dictionary floats, lengths, boundary indices, and stream symbols are charged. The continuous-coordinate diagnostic pays 288 bits per residue before headers and fails the 96-BPR limit.

The new data has 128 fitting chains, 128 public evaluation chains, and 128 unseen private evaluation chains, split equally between 64–192 and 256–512 residues. Every chain has a complete, continuous backbone. Source entries and exact sequences are disjoint between public and private data. Private source lists, downloads, raw predictions, repeatability checks, and the frozen reference with per-chain measurements live only under eval/test/. A public download command fetches every source from RCSB on a fresh clone. No committed code refers to shared/.

The reference restores the paper's histogram bins 500, free bond quantization, original-geometry reassignment, prior-regularized global glue optimization every ten rounds, and the paper's Pareto translation weight 1. The completed audit used the paper's Table 16 smaller codebook with 128 fitting chains, 512 clustering candidates and 50 merges. The final reference instead uses the main Table 14 medoid schedule, 2,048 candidates and five compression merges, as described below. The earlier higher-capacity control (1,000 bins and 100/20 initial medoids) is retained as a measured alternative; the weaker control uses 50 bins and 5/2 initial medoids. File/occurrence ordering and random seeds are fixed. An additional inference replay measures decoded numerical variation across CPU hosts, and paired bootstrap intervals measure between-input uncertainty. The initial 50-merge audit and final correction are recorded below.

Long backbones are the added scored experiment, weighted 0.5: the paper reports accumulation of local errors into global drift, which the former five-chain test barely measured. No reconstruction or rate metric is deliberately saturated. The reference cannot reach the zero-error/perfect-lDDT limits with a finite lossy representation; measured bound checks and stronger-variant evidence appear below.

Coefficient magnitudes remain RMSD 0.6, lDDT 1, BPR 0.4. Vocabulary size decreases from 0.1 to 0.02 because dictionary storage is now already fully charged in BPR; it retains a small preference for a compact alphabet without the former double penalty. Rank uses better-direction improvements over the frozen reproduced reference, divided by each metric's standard deviation among feasible attempts, and sums with 0.5 experiment weights. Failed attempts never enter this scientific ranking. The paper's numerical results are preserved verbatim under `_paper_reported`, separate from scaled measured reference results.

## Major shortcuts: before and fix

Ranks below are the old report's control-cohort ranks. Their magnitudes are not comparable with the new cohort's standardized ranks. The final table gives all rerun outcomes on the new hidden corpus.

| Shortcut | Before | Fix / final replay |
|---|---:|---|
| Supplied baseline's free exact frames | +2.352529 | Preserve its 16-prototype geometry, transmit and charge its entire continuous coordinate output; rate gate applies. |
| Forged target coordinates | +2.352333 | Only evaluator PDBs are targets; supplied target fields fail the interface. |
| Forged counts / vocabulary | +0.003025 | Derive counts, size and alphabet from decoded representation; forged fields fail. |
| Public whole-chain dictionary | +2.355349 | New private unseen sources; whole-chain dictionary storage charged. Replay a visible structure as a dictionary entry against unseen inputs. |
| Invented two-residue template | +2.355358 | Expected native size and complete reconstruction are fixed; short output fails. |
| Truncated native output | +2.352333 | No min-length matching; any incomplete chain fails. |
| Negative counts | −1.667061 in audit (arbitrarily favorable under fixed scaling) | No claimed counts; negative indices fail before measurement. |
| Scalar quality fields with valid reference predictions | 0 (tie) | Unknown metric fields now fail the raw-symbol interface; replay included. |
| Pruned comparisons | Incomplete CASP-only result | Both experiments and method enumeration are evaluator-owned. Its valid full reference predictions now tie the reference, with no pruning benefit. |

The pruning replay is a valid unchanged reference representation; structural checks verify that the evaluator never reads scoring/scores_train.json. The other major attacks run through the same hidden entry point after registration. Already rejected scalar-only, null, and empty-output attacks are not replayed. The formerly tying scalar-field attack is replayed explicitly. Strict decoder validation also rejects them.

## Limitations and deliberately open alternatives

The no-merge model is an honest alternative and still ranks +0.009567 after restoring the main paper settings. It matches reference geometry exactly and saves about 0.166 BPR and seven unused alphabet entries. Thus this corpus does not demonstrate the paper’s central hierarchical merge benefit. The larger reconstruction improvement from discrete boundary refinement supplies measured headroom; the no-merge control is not used as that evidence. Training on 128 rather than 33,992 chains remains a material scale reduction, and the comparative paper claim is not established. The audited milestone remains `method_runs`.

The corpus is larger but far below the paper's 33,992-chain fitting corpus and thousands of merge rounds. This iteration does not establish full PDB-scale compression gains, downstream transfer, or performance against the paper's external learned tokenizers. Exact sequence and source disjointness do not establish remote-homology separation. General-purpose dictionary learning and more efficient coding remain scientific research opportunities; attempts must still freeze their representation before private requests.

There is no exhaustive candidate-enumeration task here: encoding the input geometry is allowed, but storing each entire unseen chain costs its full geometry and cannot satisfy compact coding. The former public-answer lookup is closed by unseen inputs and dictionary accounting. The finite decoder interface supports motif dictionaries, independent internal-coordinate alphabets, and full coordinates; new decoder families would require an explicit benchmark extension. Serialized JSON whitespace is not charged; the fixed binary description-length convention is documented.

The old reference had CAMEO/CASP RMSD 7.516185/4.207396, lDDT 0.577381/0.574539, BPR proxy 7.774787/7.774787, and vocabulary 219. Its rank was zero by definition. The final reference also has rank zero, with full rate and evaluator-native targets on a different corpus; its new scientific measurements appear below. The higher-resolution and weaker controls have changed data and restored paper settings, so the before/after evidence establishes ranking behavior rather than a numerical longitudinal comparison.

## Completed 50-merge audit before the final repair

The complete audit stopped at a bitwise replay assertion after all model measurements. Motif identities matched; 1–5 boundary symbols per replayed chain differed by one bin across preempted CPU hosts. This is numerical variation to measure in decoded scientific units, not evidence of seed instability. The main failure was scientific: an oversized rarely used merge dictionary penalized the higher-capacity model, and the no-merge control beat the reference.

| Side / attempt | RMSD short / long | lDDT short / long | BPR short / long | Rank |
|---|---|---|---|---:|
| train / geobpe_reference | 1.813706 / 2.765136 | 0.766910 / 0.688813 | 53.080489 / 41.546349 | 0 |
| train / higher_capacity | 1.806610 / 1.897274 | 0.772017 / 0.762760 | 95.596086 / 58.863524 | -0.234047 |
| train / internal_baseline | 8.832851 / 19.412237 | 0.523633 / 0.429113 | 46.193884 / 45.432471 | -1e+100 |
| train / lower_capacity | 3.606429 / 7.675948 | 0.617163 / 0.485264 | 43.263242 / 31.352623 | -3.15737 |
| train / no_bpe | 1.813706 / 2.786364 | 0.766910 / 0.686203 | 40.934434 / 35.874158 | 0.205125 |
| train / supplied_baseline | 0.011148 / 0.010051 | 1.000000 / 1.000000 | 288.266177 / 288.096420 | -1e+100 |
| test / geobpe_reference | 1.906143 / 2.762641 | 0.760346 / 0.689849 | 55.020046 / 41.672752 | 0 |
| test / higher_capacity | 1.894694 / 1.883805 | 0.763872 / 0.762673 | 101.774617 / 59.276457 | -1e+100 |
| test / internal_baseline | 7.690368 / 19.813211 | 0.544783 / 0.428074 | 46.321956 / 45.441030 | -1e+100 |
| test / lower_capacity | 3.690832 / 7.611221 | 0.617876 / 0.489437 | 45.091968 / 31.570538 | -2.50685 |
| test / no_bpe | 1.907194 / 2.754692 | 0.760269 / 0.690576 | 41.785589 / 35.931044 | 0.755145 |
| test / supplied_baseline | 0.010811 / 0.010146 | 1.000000 / 1.000000 | 288.294731 / 288.098328 | -1e+100 |

The final repair restores the main Table 14 500/100 initial-medoid schedule (20/100 merged medoids), uses five merge rounds following Appendix K.2’s advice for small-corpus compression, and increases the clustering sample cap from 512 to 2,048. This remains below the paper’s 5,000-occurrence cap and 33,992 training chains. A single frozen dictionary serves both experiments; it is now charged once across the complete 128-chain corpus, with its cost apportioned by native residue count. This removes double charging and keeps every dictionary bit accounted for. No quality or rate threshold is relaxed. A separate variant optimizes the same discrete boundary symbols against complete-backbone geometry; it changes neither the reference algorithm nor storage cost. Its paired improvement must exceed measured numerical replay variation.


## Final packaging check

The main audit finished successfully in job `35dca7a9-39a`. Reference-only train/test scores were regenerated from decoded final reference runs; all variants and attacks are reported only here. Public/private reference RMSD is 1.917877/1.980736 for short chains and 1.526253/1.519381 for long chains, showing comparable difficulty. The independent baseline has long-chain RMSD 19.813211 and fails the fixed quality constraint; the reference is clearly better and remains far from perfect geometry.

The final rescore-only job `36b6eb18-d00` passed. The lookup probe used ten valid complete public chains, passed dictionary validation, and failed complete-chain coverage on unseen inputs. The formerly tying scalar-field attack failed the strict output schema. No model was retrained and no threshold changed. Fresh reference-only packaging passed without audit variants or replay files, and `scripts/run.sh` was restored to end-to-end reference reproduction. The standalone baseline launcher now uses the same independently implemented baseline and public evaluation commands already verified by the reproduction job. `validate.py` passes; its two heuristic warnings mistake the paired bootstrap RNG for experiment regeneration. That RNG only resamples already decoded per-input measurements.


## Final combined job results

These ranks use the final cohort standard deviations; failed attempts receive −10¹⁰⁰ and cannot outrank a feasible run. Reference rank is zero by definition. Intervals are paired 1,000-replicate bootstrap intervals over the same private chains.

| Attempt | Failed | Rank | Paired 95% interval |
|---|---|---:|---|
| attack_constant_template | True | -1e+100 |  |
| attack_forged_counts | True | -1e+100 |  |
| attack_forged_target | True | -1e+100 |  |
| attack_negative_counts | True | -1e+100 |  |
| attack_prune_comparison | False | 0 | [0.0, 0.0] |
| attack_public_dictionary | True | -1e+100 |  |
| attack_quality_fields | True | -1e+100 |  |
| attack_truncated | True | -1e+100 |  |
| geobpe_reference | False | 0 | [0.0, 0.0] |
| higher_capacity | False | -0.755637 | [-0.835256, -0.675312] |
| internal_baseline | True | -1e+100 |  |
| lower_capacity | False | -2.95926 | [-3.269801, -2.679492] |
| no_bpe | False | 0.0095675 | [0.009193, 0.009943] |
| refined_glue | False | 1.25409 | [1.195446, 1.319235] |
| supplied_baseline | True | -1e+100 |  |

| Attempt / experiment | RMSD ↓ | lDDT ↑ | Full BPR ↓ | Vocabulary ↓ |
|---|---:|---:|---:|---:|
| attack_prune_comparison / short_backbones | 1.980736 | 0.755715 | 44.372994 | 2107 |
| attack_prune_comparison / long_backbones | 1.519381 | 0.823977 | 44.344111 | 2107 |
| geobpe_reference / short_backbones | 1.980736 | 0.755715 | 44.372994 | 2107 |
| geobpe_reference / long_backbones | 1.519381 | 0.823977 | 44.344111 | 2107 |
| higher_capacity / short_backbones | 1.894694 | 0.763872 | 53.966919 | 3173 |
| higher_capacity / long_backbones | 1.883805 | 0.762673 | 53.955366 | 3173 |
| internal_baseline / short_backbones | 7.690368 | 0.544783 | 45.343702 | 288 |
| internal_baseline / long_backbones | 19.813211 | 0.428074 | 45.332149 | 288 |
| lower_capacity / short_backbones | 3.690832 | 0.617876 | 29.771404 | 407 |
| lower_capacity / long_backbones | 7.611221 | 0.489437 | 29.865329 | 407 |
| no_bpe / short_backbones | 1.980736 | 0.755715 | 44.207101 | 2100 |
| no_bpe / long_backbones | 1.519381 | 0.823977 | 44.178218 | 2100 |
| refined_glue / short_backbones | 1.224961 | 0.836642 | 44.372994 | 2107 |
| refined_glue / long_backbones | 0.924750 | 0.889168 | 44.344111 | 2107 |
| supplied_baseline / short_backbones | 0.010811 | 1.000000 | 288.281731 | 1 |
| supplied_baseline / long_backbones | 0.010146 | 1.000000 | 288.096881 | 1 |

Failed attempts and reasons:

- `attack_constant_template`: invalid full coordinate output
- `attack_forged_counts`: representation fields do not match codec
- `attack_forged_target`: representation fields do not match codec
- `attack_negative_counts`: invalid stream lengths
- `attack_public_dictionary`: reconstruction does not cover the complete chain
- `attack_quality_fields`: representation fields do not match codec
- `attack_truncated`: invalid full coordinate output
- `internal_baseline`: long_backbones: reconstruction constraint
- `supplied_baseline`: short_backbones: rate/dictionary constraint; long_backbones: rate/dictionary constraint

Reference metrics at their best bound: none. Long backbones are the added scored experiment; their weight is 0.5.

Headroom evidence: the stronger variant has a paired lower confidence limit above zero and the measured normalized replay difference (0).
The weaker variant has rank -2.959262.
The no-merge ablation has rank 0.009567; indistinguishable geometry is a scientific headroom limitation, not a forged-output loophole.

The boundary-refinement variant changes only the encoder’s choice of existing finite boundary symbols. It uses its input structure, keeps the reference dictionary and motif sequence, and pays identical rate/vocabulary cost. Its output is accepted only when its independently evaluated RMSD and lDDT are both no worse. Measured RMSD remains above zero and lDDT below one in both experiments; this simple variant does not attain a scored quality bound.

Decoded replay diagnostic: {"conservative_normalized_rank_noise": 0.0, "exact_raw_replay": true, "maximum_difference_by_experiment": {"long_backbones": {"bpr": 0.0, "lddt": 0.0, "rmsd": 0.0}, "short_backbones": {"bpr": 0.0, "lddt": 0.0, "rmsd": 0.0}}, "note": "Four-input numerical replay diagnostic across CPU hosts, not a population confidence bound.", "paired_inputs": 4}
