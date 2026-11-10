# Hardening audit

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
| Pruned comparisons | Incomplete CASP-only result | Both experiments and method enumeration are evaluator-owned. Its valid full reference predictions now tie the reference, with no pruning benefit. |

The pruning replay is a valid unchanged reference representation; structural checks verify that the evaluator never reads scoring/scores_train.json. The other major attacks run through the same hidden entry point after registration. Already ineffective scalar/null/empty-output and scalar-quality attacks are not replayed. Strict decoder validation also rejects them.

## Limitations and deliberately open alternatives

A no-merge model is an honest alternative. If it still ties or improves the final reference, report that scientific limitation; do not manufacture a prohibition or bonus for using merges. The stronger-variant paired confidence interval, not merely a metric below its mathematical bound, determines whether headroom is demonstrated. If the final interval is not positive, the requested scientific headroom remains unresolved.

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
