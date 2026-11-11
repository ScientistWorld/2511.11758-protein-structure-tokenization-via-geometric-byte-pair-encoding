# Hardening audit (final)

**Better results now score higher, and worse ones lower, by far more than the noise.** On the hidden test, a fixed-cost encoder improvement of the reproduced GEOBPE ranks **+0.424** above the reference (paired 95% interval [0.404, 0.443]). A simple closed-loop internal-coordinate codec ranks **+1.282** [1.223, 1.337]. A lower-capacity GEOBPE ranks **−1.270** [−1.363, −1.182]. Refitting the reference with two other training seeds moves it by at most **0.015**. Every major shortcut from `REDTEAM.md` now fails: it is written to `scoring/scores_test.json` at the fixed worst value of every metric in both experiments, or else it ties the reference with no gain.

The reference is the released PT-BPE GEOBPE at the paper's main Table 14 codebook. It sits at the operating point the paper reports in Table 16 (|V| = 600), with the paper's glue and quantizer settings restored. No reference metric sits at a bound.

Two limitations remain and are stated plainly:
- **A simple codec dominates the reference.** A classical closed-loop internal-coordinate codec beats the paper's method on every metric. This is an honest shortfall of the method, not a loophole, and it cannot be removed without replacing the paper's algorithm.
- **Hierarchical merges show no benefit.** At this corpus size, merging adds nothing on held-out chains.

All ranks below apply the external rule to the evaluator-written score files. For each experiment and metric, the rule takes the weight times the coefficient magnitude, times the improvement in the metric's better direction, divided by that metric's population standard deviation across the cohort, and sums the terms. Unless noted, the cohort is every non-attack attempt of the final audit ("science" cohort), and the reference is 0. Raw tables, the "all attempts" cohort and the train slice are in `redteam/hardening_final.md`. The seed results are in `redteam/seed_spread.md`.

## Does a better result score higher? Variants before and after

Before: the original `REDTEAM.md` gym (5 public chains per split, proxy rate, method-supplied targets), with its audit / control-scale ranks. After: the final gym on the hidden test (64 unseen chains per experiment, full description length, evaluator-owned targets).

| Variant | Before | After (test, science cohort) [paired 95%] | After (train) |
|---|---:|---:|---:|
| Stronger quantizer (`better_bins300`, 50→300 bins) | +0.693 / +0.630 | Settings now in the reference (500 bins) | — |
| Translation weight 1 (`better_glue`) | +0.043 / +0.213, below seed spread | Now the reference setting (paper Pareto setting) | — |
| `refined_glue`: same frozen dictionary, motif stream and rate; boundary symbols re-chosen against complete-backbone geometry | — | **+0.4244** [0.4038, 0.4433] | +0.4138 |
| `closed_loop_internal`: 26-bit/residue internal-coordinate codec, symbols chosen sequentially against the decoded prefix | — | **+1.2815** [1.2227, 1.3374] | +1.2673 |
| `lower_capacity` (50 bins, 5/2 initial medoids) | −1.238 / −3.489 | **−1.2698** [−1.3626, −1.1818] | −1.2916 |
| `higher_capacity` (old small codebook with 1000 bins, 100/20 medoids, 50 merges) | — | −0.3020 [−0.3329, −0.2696] | −0.2854 |
| `merge5` (reference fit plus five merge rounds) | — | −0.0033 [−0.0058, −0.0003] | −0.0005 |
| `no_bpe` (pre-merge vocabulary, earlier host) | +0.000027 / +0.034 | −0.0005 [−0.0030, 0.0024] (tie) | +0.0021 |
| `weaker_no_glue` | Failed before evaluation | Not rerun | — |

Notes on the table:
- **`higher_capacity` is not a strictly larger model.** It has more bins but five times fewer medoids than the reference, and it pays about 10 BPR more. Its lower rank is a trade-off measurement, not evidence against the paper's codebook-growth trend.
- **Shared dictionary.** `refined_glue` and `merge5` use the reference's dictionary, so their comparisons carry no training-seed noise.
- **Train and test agree** for every variant, so an honest method scores alike on both slices.

### Noise

| Source of noise | Before | After |
|---|---:|---:|
| Training seed (max − min rank over seeds 0/1/2) | 0.129 / 0.359 | **0.0147** (seeds 1 and 2: −0.0046 [−0.0287, 0.0194], −0.0147 [−0.0333, 0.0043]) |
| Fresh re-encoding on one host (forced four-input replay) | — | 0 (bit-identical) |
| Cross-host re-encoding (`no_bpe` vs fresh reference, same algorithm) | — | 0.0005 rank; 89 of 128 private chains differ in at least one boundary bin |

The seeds were refit in this pass with identical settings (`method/train.py --seed`; the default seed 0 is unchanged). Their raw test metrics:

| Seed | RMSD short / long | lDDT short / long | BPR short / long |
|---|---|---|---|
| 0 | 1.980 / 1.518 | 0.7557 / 0.8241 | 44.207 / 44.178 |
| 1 | 1.987 / 1.530 | 0.7553 / 0.8230 | 44.207 / 44.178 |
| 2 | 1.995 / 1.531 | 0.7546 / 0.8195 | 44.207 / 44.178 |

The smallest genuine improvement is about 29 times the seed spread. The paper's own effect is much larger than either source of noise: GEOBPE against the matched-rate fixed-bin baseline is RMSD 1.98 / 1.52 versus 7.69 / 19.81 Å, at 44.2 versus 45.3 BPR.

## Major shortcuts: fix, and score before and after

"Before" is the `REDTEAM.md` audit-cohort rank. "After" is the final hidden-test outcome. Every failed attempt is written at RMSD 15, lDDT 0.35, BPR 96 and vocabulary 8192 in both experiments. That is rank −3.979 in the all-attempts cohort and −4.419 in the science cohort, below every feasible attempt.

| Shortcut | Before | Fix | After |
|---|---:|---|---|
| Supplied baseline with free continuous frames | +2.3525 | The decoder interface has no free side information. Continuous output is charged 32 bits per float; the 96-BPR rate limit applies. | Fails (BPR 288); worst values |
| Forged target coordinates | +2.3523 | Targets are evaluator PDBs, verified by sha256 and held in memory; target fields fail the schema | Fails; worst values |
| Forged token counts / vocabulary size | +0.0030 | Counts, sizes and alphabet are derived from the decoded representation; claimed fields fail | Fails; worst values |
| Public whole-chain dictionary | +2.3553 | Private unseen chains (64 + 64, source- and sequence-disjoint from public); dictionary storage charged | Fails (no complete coverage); worst values |
| Constant two-residue template | +2.3554 | Native residue count and complete reconstruction fixed by `eval/` | Fails; worst values |
| Truncated output | +2.3523 | No min-length matching; any incomplete chain fails | Fails; worst values |
| Negative counts | −1.667 (+2835 at fixed scales) | No claimed counts; negative or non-integer indices fail | Fails; worst values |
| Scalar quality fields beside valid predictions | 0 (tie) | Unknown fields fail the schema | Fails; worst values |
| Pruning the comparison via a mutable public score file | Incomplete output | Experiments, test size, thresholds, weights and the published comparison are owned by `eval/`. The private evaluator restores its own copy of `scoring/reference.json` before and after every attempt. | 0 (tie: valid reference streams, no selection benefit) |
| Crashed encoder (new probe) | — | Failed attempts are written at the worst values, not omitted | Fails; worst values |
| Tampering with the reference comparison or a private target (new probes) | — | Evaluator, comparison and input files are snapshotted, restored after each encoder, and the attempt fails | Fails; worst values |

The scalar-only, null-array and empty-array attacks already failed before; the strict schema still rejects them, and they were not replayed.

## Shortcuts and open alternatives deliberately left

- **Encoder-side search against the supplied input.** An encoder must see the structure it encodes, and the decoder is public. Any method can therefore compute its own distortion and search over symbols. This is left open on purpose:
  - every transmitted bit, including the dictionary, is charged, so search can only find a better representation inside a frozen codebook at a measured rate;
  - the paper's own encoder does exactly this, optimizing boundary glue against the original structure, so limiting it would cripple the reproduced method.
  This search is measured: `refined_glue` (+0.42) and `closed_loop_internal` (+1.28) are such encoders. Per-instance compute is bounded only by the 7,200 s per-attempt encoder timeout, about 56 s per chain. The reference encoder takes about 21–23 s per chain (44–50 minutes per 128-chain attempt on the job hosts).
- **No merges (`no_bpe`).** An honest alternative that the test cannot tell apart from the reference: same algorithm, zero merge rounds. The reference itself is the pre-merge checkpoint the paper reports. This is a headroom limitation, not a loophole.
- **Memorizing public evaluation chains.** This only raises train-slice scores. The hidden test uses unseen chains, so such a method loses there.
- **Method-owned files in the run directory.** The evaluator deletes `outputs.json` before each encoder run but leaves the method's own cache files (the reference uses them for per-chain resume). An encoder could keep private inputs there between hidden-test runs. This is not defended, consistent with not defending against leftover state; the grader's shortcut check covers it.
- **Entropy coding.** Symbols are charged at fixed width, `ceil(log2(alphabet))`, so entropy coding is not rewarded. JSON whitespace is not charged.

## Reference score before and after

| | RMSD | lDDT | BPR | Vocabulary |
|---|---|---|---|---|
| Before (CAMEO / CASP, 5 chains each, proxy rate, method-supplied targets) | 7.516 / 4.207 | 0.5774 / 0.5745 | 7.775 (tokens only) | 219 |
| After, test (short / long, 64 unseen chains each) | 1.9803 / 1.5183 | 0.7557 / 0.8241 | 44.207 / 44.178 (full description length) | 2100 |
| After, train (public unseen, short / long) | 1.9242 / 1.5263 | 0.7610 / 0.8235 | 43.916 / 43.891 | 2100 |
| Paper, Table 16, same codebook at \|V\| = 600 (kept under `_paper_reported`) | 1.66 | 0.73 | 36.02 | 600 |

The final reference's distortion is on the paper's scale. Its BPR is higher than the paper's for two reasons:
- symbols are charged at whole-bit width;
- the complete dictionary (about 7.2 bits per residue: 211,424 bits over 29,513 private residues) is amortized over 128 chains rather than a PDB-scale corpus.

The packaged `scoring/scores_test.json`, `scores_train.json` and `reference.json` hold the reference runs alone: the reference, plus the fixed-bin baseline at worst values because it fails the long-chain reconstruction constraint. The final job regenerated them through `scripts/reproduce.sh`, byte-identical to the previous packaging.

## Headroom check

- **No reference metric at a bound.** RMSD is above 0 and lDDT below 1 in both experiments; BPR is 44 against a feasible range that goes down to a few bits; vocabulary is 2100, above the minimum of 1.
- **Added experiment.** `long_backbones` (256–512 residues, weight 0.5) is where the paper's method falls short: local quantization error accumulates into global drift.
- **Measured headroom.** Two variants beat the reference well beyond noise. Neither reaches a bound: `closed_loop_internal` has RMSD 0.378 / 0.435 and lDDT 0.963 / 0.958.
- **Brute force fails.** Lossless coordinates (288 BPR) and whole-chain lookup both fail.
- **Baseline below the reference.** The independent fixed-bin baseline (`baseline/internal.py`) is far below the reference: at equal rate it drifts to 19.8 Å on long chains and fails the constraint.

## Weights and coefficients

- **Coefficients:** RMSD 0.6, lDDT 1.0, BPR 0.4, vocabulary 0.02. The vocabulary coefficient was lowered from 0.1 earlier in this iteration because dictionary storage is now charged inside BPR; keeping it at 0.1 would penalize alphabet size twice.
- **Experiment weights:** 0.5 each. Global drift on long chains is the failure the paper's glue optimization exists to correct.
- **No changes in this final pass.**

## Changes in this iteration

- **Evaluators:** they decode raw symbols with an independent NeRF decoder and recompute every metric. They write every on-disk submission to `scoring/scores_{train,test}.json`, at worst values for any malformed, crashed, file-modifying or constraint-failing attempt. Targets are loaded and verified before any encoder runs; evaluator, comparison and input files are restored after each encoder.
- **Reference:** paper settings restored (500 bins, free bonds, original-geometry reassignment, glue prior 1 every 10 rounds, translation weight 1). It uses the main Table 14 codebook at the Table 16 |V| = 600 operating point, which follows Appendix K.2: stop merging early at high resolution.
- **Data:** 128 fitting, 128 public and 128 private chains, split into short and long. Private sources and downloads live only in `eval/test/`.
- **Hidden headroom probes:** they live in `eval/test/variants/` and are not shipped with the method.
- **This pass:**
  - measured the training-seed spread;
  - made `scripts/download.sh` skip the private fetch where `eval/test/` is absent;
  - restored `scripts/run.sh` to the end-to-end reference driver (`scripts/reproduce.sh`).
  No evaluator, data or reference code changed in this pass, so the final audit job `2175ebd6-1ed` remains the current shortcut and variant evidence.

## What could not be fixed

- **The paper's method is not on this benchmark's Pareto front.** A roughly 60-line closed-loop internal-coordinate codec reaches RMSD 0.38–0.44 at 26 BPR, against GEOBPE's 1.5–2.0 at 44 BPR. Its open-loop form is the shipped baseline, so a future agent can find it easily. Under the paper's own metrics this is a genuine improvement, not a shortcut, and the score orders it correctly. But it means future rankings will likely be led by encoder-design ideas from classical coding rather than by better hierarchical vocabularies. The paper's Pareto claims compare only against learned tokenizers (VQ-VAEs, ProToken), and those comparisons are not reproduced here.
- **Hierarchical merges show no held-out benefit.** At 128 fitting chains and 2,048 clustering occurrences (paper: 33,992 chains, a 5,000-occurrence cap), five merge rounds add seven motifs that no held-out chain uses.
- **Not covered:** downstream transfer, language-model generation and the claimed data-efficiency advantage.
- **Encoder timeout:** it is a wall-clock bound on feasibility. It is generous (the reference uses about 40% of it), but a host more than about twice as slow could time out the reference encoder, which would then be scored at the worst values.
