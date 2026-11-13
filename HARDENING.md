# Hardening audit (final)

**The best honest improvement of the paper's own tokenizer now ties the short closed-loop codec.** Previously the short codec led by about 3× (+1.28 vs +0.42). Now:
- **Best honest improvement** (`closed_tokens_compact`): **+1.67** [1.59, 1.74]. It keeps the reference's frozen dictionary of 600 learned residue medoids; only the tokenization changes (closed loop), and the boundary alphabets are coarser (8 / 4 / 64 values).
- **The ~60-line short codec REVIEW.md flagged**: **+1.72** [1.65, 1.79].
- **Lossless at the reference's own rate.** With the reference's alphabets unchanged, closed-loop tokenization over the same vocabulary is nearly lossless: RMSD 0.04 Å, lDDT 1.000, rank **+1.56**.

So the reference's distortion comes from its encoder, not from its vocabulary or its corpus size. That is where the test now shows the paper's method falls short.

**The paper's own effect is measured.** Removing rigid-body glue refinement (the paper's Appendix A ablation) raises long-chain RMSD from 1.52 to 5.17 Å. Its rank is **−0.56** [−0.67, −0.46], against a training-seed spread of 0.019. The paper reports 1.66 → 4.39 Å for the same ablation.

**What stays open.** A short codec still outranks the reference, and merges still add nothing at this scale. Both are stated plainly below, with the evidence for why no faithful change of corpus, format or rate regime removes them.

**Reference rerun.** The reference was rerun end to end from final code, as REVIEW.md asked:
- Refit `model.json` is byte-identical to the previous fit.
- The fresh encodes of both slices reproduce `scoring/scores_{train,test}.json` and `scoring/reference.json` byte for byte.
- `validate.py` passes.

**How ranks are computed.** All ranks apply the external rule to the evaluator-written score files: weight × |coefficient| × improvement in the better direction ÷ the metric's population standard deviation over the cohort, summed. The reference is 0.
- The cohort is every attempt of this audit (the "science" cohort). No attacks were replayed this pass.
- Intervals are paired 95% bootstraps over the same 128 private chains.
- Raw tables, the train slice and the "paper-line" cohort, which excludes the two hand-designed codecs, are in `redteam/hardening_final.md`.

## What REVIEW.md listed, and what changed

| REVIEW item | This pass |
|---|---|
| A ~60-line closed-loop codec beats GeoBPE by about 3× the best honest improvement | Measured the paper's own drift-correction idea done exactly, over the frozen reference vocabulary. The best honest improvement rose from +0.42 to **+1.67**; the short codec is at +1.72, with overlapping intervals. The short codec still outranks the reference (left; see below). |
| Merges add nothing at this corpus size; scale the corpus until merges matter and a short codec stops outranking | Not scaled. The paper's Table 5 and the vocabulary-vs-encoder measurement show that a larger corpus cannot remove the gap; see "What could not be fixed". The paper's effect is now shown through its rigid-body refinement ablation instead. |
| Rerun the reference and baselines end to end; that `scores_test.json` is the new baseline | Done in job `2b23905d-701`: fresh fit, fresh encode on both slices, package, validate. Outputs are byte-identical to the previous packaging. |

No evaluator, data, reference or baseline code changed in this pass. The changes are hidden probes, the audit driver and documentation.

## Does a better result score higher? Variants before and after

"Before" is the previous `HARDENING.md`, which used a smaller cohort. "After" is this audit on the hidden test (science cohort), with the train slice alongside. Ranks move between the two because the cohort scales changed; the raw metrics of unchanged attempts are identical.

| Variant (what changes; dictionary frozen unless stated) | Before (test) | After, test [paired 95%] | After, train |
|---|---:|---:|---:|
| `closed_tokens_compact`: closed-loop choice of learned medoid + glue; glue alphabets 8 θ / 4 ω / 64 φ quantiles | — | **+1.6705** [1.594, 1.736] | +1.5140 |
| `closed_tokens`: closed-loop choice of learned medoid + glue; reference alphabets, same rate | — | **+1.5640** [1.511, 1.613] | +1.4503 |
| `closed_glue`: reference motif stream; glue chosen in closed loop | — | +1.0159 [0.942, 1.087] | +0.9013 |
| `refined_glue`: reference motif stream; glue re-chosen against full-chain error (±0.2–0.3 rad) | +0.4244 | +0.5556 [0.529, 0.580] | +0.5111 |
| `merge5`: reference fit plus five merge rounds | −0.0033 | −0.0047 [−0.008, −0.001] | −0.0010 |
| `no_bpe`: pre-merge vocabulary of the merge5 fit | −0.0005 | −0.0006 (tie) | +0.0027 |
| `higher_capacity`: 1000 bins, 100/20 medoids, 50 merges | −0.3020 | −0.4181 [−0.458, −0.376] | −0.3711 |
| `open_glue`: paper ablation without glue refinement (native glue snapped to bins) | — | **−0.5587** [−0.669, −0.463] | −0.6668 |
| `compact_glue`: compact alphabets, reference motif stream, glue-only closed loop | — | −1.0328 [−1.144, −0.896] | −1.0511 |
| `lower_capacity`: 50 bins, 5/2 medoids, 50 merges | −1.2698 | −1.6581 [−1.786, −1.539] | −1.5905 |

Raw test metrics (short / long):

| Attempt | RMSD (Å) | lDDT | BPR | Vocabulary |
|---|---|---|---|---:|
| reference | 1.980 / 1.518 | 0.756 / 0.824 | 44.21 / 44.18 | 2100 |
| `closed_tokens` | 0.039 / 0.038 | 1.000 / 1.000 | 44.21 / 44.18 | 2100 |
| `closed_tokens_compact` | 0.393 / 0.529 | 0.961 / 0.950 | 26.80 / 26.68 | 676 |
| `closed_glue` | 0.688 / 0.844 | 0.935 / 0.922 | 44.21 / 44.18 | 2100 |
| `open_glue` | 1.974 / 5.166 | 0.798 / 0.683 | 44.21 / 44.18 | 2100 |
| `compact_glue` | 2.852 / 3.629 | 0.634 / 0.526 | 26.80 / 26.68 | 676 |

What these show:
- **Better methods score higher by far more than the noise.** The smallest genuine improvement, `refined_glue`, is about 30× the seed spread.
- **Weaker variants score lower.**
- **Train and test order every variant identically.**
- **Each step of the paper's own idea moves the score in its direction.** Drift correction goes from none (`open_glue`) to batch inverse kinematics (the reference), then bounded discrete refinement, closed-loop glue, and closed-loop tokens.
- **`compact_glue` vs `closed_tokens_compact`.** Coarse boundary alphabets fail when medoids are chosen open-loop (−1.03). They work once the medoid choice is also closed-loop (+1.67). Rate allocation and encoder design interact, and the test resolves both.

### Noise

| Source | Value |
|---|---:|
| Training seed (max − min rank over seeds 0/1/2, same cohort) | **0.019**. Seed 1: −0.0061 [−0.037, 0.025]; seed 2: −0.0188 [−0.043, 0.006] |
| Fresh end-to-end refit and re-encode, same code (this pass) | 0 (`model.json` and all score files byte-identical) |
| Cross-host re-encoding (earlier pass) | 0.0005 rank |

Seeds 1 and 2 were fitted in the previous pass and rescored here from their saved streams.

## Major shortcuts

The evaluator is unchanged, so every shortcut outcome from the previous audit (job `2175ebd6-1ed`) stands. They were not replayed. Each failed attempt is written at RMSD 15, lDDT 0.35, BPR 96, vocabulary 8192 in both experiments. In this pass's science-cohort scales that is about −6.2, below every feasible attempt.

| Shortcut | Score before the earlier fix | Fix (earlier pass) | After |
|---|---:|---|---|
| Supplied baseline with free continuous frames | +2.3525 | No free side information; continuous output costs 32 bits per float; 96-BPR limit | Fails (BPR 288); worst values |
| Forged target coordinates | +2.3523 | Targets are evaluator PDBs, verified by sha256 and held in memory | Fails; worst values |
| Forged token counts / vocabulary size | +0.0030 | Counts and sizes are derived from the decoded representation | Fails; worst values |
| Public whole-chain dictionary | +2.3553 | Unseen private chains; dictionary storage charged | Fails; worst values |
| Constant template / truncated output | +2.3554 / +2.3523 | Evaluator owns native residue counts; incomplete chains fail | Fails; worst values |
| Negative counts, scalar quality fields | −1.667 / 0 | No claimed counts; unknown fields fail the schema | Fails; worst values |
| Mutating `scoring/reference.json`, tampering with targets, crashing | — | Evaluator files snapshotted and restored; such attempts fail | Fails; worst values |

## Shortcuts and alternatives deliberately left

### A short hand-designed closed-loop codec outranks the reference

`closed_loop_internal` ranks +1.72, and its port to the paper's own motif format, `closed_loop_motif`, ranks +1.42 at 22.7 BPR. This is left. It is not a loophole: it pays every bit, decodes through the same interface, and wins on all four metrics on unseen chains. Three findings explain it:
1. **The short codec adds nothing beyond two honest changes to the paper's tokenizer.** Closed-loop tokenization plus per-angle boundary resolution, applied to the frozen GeoBPE vocabulary, ties it (+1.67 vs +1.72, overlapping intervals).
2. **Restricting the decoder format would not help.** The motif-format port still ranks +1.42.
3. **No faithful regime removes it.** Every GeoBPE operating point the paper reports has BPR of at least 27 and RMSD of at least 1.05 Å (Tables 5 and 16–18, paper's own accounting). The short codec reaches 0.4 Å at 26 BPR. Rate caps, metric changes or a single shared glue alphabet would either leave the paper's operating regime or penalize encoder-side optimization against the input, which the reference's own glue refinement also performs.

Hiding this would mean rigging the score. The test instead rewards fixing it from inside the paper's method, and that path is now measured to reach the same score.

### Encoder-side search against the supplied input

This is open by design: every bit is charged, and the paper's own encoder optimizes glue against the input. It is now fully measured:
- the honest closed-loop encoders above;
- per-chain cost about a second, against the 7,200 s per-attempt timeout (all seven probes on both slices took 34 minutes, including rescoring).

### Other items left

- **`no_bpe` and merges.** An honest alternative the test cannot tell apart from the reference (same algorithm, zero merge rounds). This is a headroom limitation, not a loophole.
- **Memorizing public evaluation chains.** This only helps the train slice. The hidden test uses unseen chains.
- **Method-owned cache files in run directories.** Not defended, consistent with not defending against leftover state.
- **Entropy coding.** Symbols are charged at fixed width, `ceil(log2(alphabet))`, so entropy coding is not rewarded.

## Reference score before and after

| | RMSD | lDDT | BPR | Vocabulary |
|---|---|---|---|---:|
| Before (previous packaging), test short / long | 1.9803 / 1.5183 | 0.7557 / 0.8241 | 44.207 / 44.178 | 2100 |
| After (fresh refit + encode, job `2b23905d-701`), test | 1.9803 / 1.5183 | 0.7557 / 0.8241 | 44.207 / 44.178 | 2100 |
| After, train (public unseen) | 1.9242 / 1.5263 | 0.7610 / 0.8235 | 43.916 / 43.891 | 2100 |
| Paper Table 16, same codebook at \|V\| = 600 (kept under `_paper_reported`) | 1.66 | 0.73 | 36.02 | 600 |

The reference is the released PT-BPE GEOBPE at the paper's main Table 14 codebook, at the Table 16 operating point (|V| = 600, no merged keys), with the paper's glue and quantizer settings. Its BPR is higher than the paper's for two reasons:
- symbols are charged at whole-bit width;
- the complete dictionary (about 7.2 bits per residue) is amortized over 128 chains rather than a PDB-scale corpus.

The independent fixed-bin baseline fails the long-chain reconstruction constraint (RMSD 19.8 Å), so it is packaged at the worst values.

## Headroom check

- **Reference at a bound: none.** RMSD > 0, lDDT < 1, BPR 44 against a feasible floor of a few bits, vocabulary 2100 > 1.
- **Measured headroom.** Six attempts beat the reference well beyond noise; the best reach +1.7.
- **Saturation.** `closed_tokens` reaches the lDDT bound (1.000) at the reference's rate, but not RMSD (0.04 Å) or rate (44 BPR). No attempt sits at every bound. Further gains must come from lower rate at near-lossless distortion; `closed_tokens_compact` and both short codecs sit at 23–27 BPR with 0.4–0.85 Å.
- **Added experiment.** `long_backbones` (256–512 residues, weight 0.5), added in an earlier pass, measures drift accumulation, where the paper's method falls short. The no-refinement ablation shows the drift directly (5.17 vs 1.52 Å).
- **Brute force fails.** Lossless coordinates (288 BPR) and whole-chain lookup both fail.
- **Baseline.** The independent fixed-bin baseline is far below the reference.

## Weights and coefficients

Unchanged. Coefficients are RMSD 0.6, lDDT 1.0, BPR 0.4, vocabulary 0.02; the experiment weights are 0.5 each. The measurements in this pass gave no reason to reweigh:
- every variant that improved distortion or rate moved in the expected direction;
- changing coefficients cannot reverse a codec that is better on all four metrics.

## Changes in this pass

- **`eval/test/variants/glue_loop.py`** (hidden; imports no method or evaluator code): probes on the frozen reference tokenizer, in five modes:
  - `open`: the paper's no-refinement ablation;
  - `closed`: closed-loop glue;
  - `compact`: closed-loop glue with compact alphabets;
  - `tokens`: closed-loop medoid and glue;
  - `tokens_compact`: closed-loop medoid and glue with compact alphabets.

  Base motif streams come from the released encoder, recovered from the reference run's own resume cache.
- **`eval/test/variants/closed_loop_motif.py`** (hidden): the short codec expressed in the motif format.
- **`scripts/hardening_audit.sh`**: stage-marked audit, robust to preemption. It runs a fresh refit (compared byte for byte with the previous fit), fresh encodes of both slices, probes and archived variants from raw streams, the report, reference-only packaging and validation.
- **`scripts/rank_summary.py`**: a pure-Python rank calculator.
- **`scripts/hardening_report.py`**: cohorts changed to "science" and "paper line".
- **`redteam/`**: `hardening_final.{md,json}` and `audit_scores_{train,test}.json` regenerated from this audit.
- **`scripts/run.sh`**: restored to the end-to-end reference driver (`scripts/reproduce.sh`).
- **Unchanged**: evaluators, contracts, data, reference, baseline, briefing and scoring documents. The packaged score files are byte-identical after the fresh rerun.

## What could not be fixed

- **A short hand-designed codec still outranks the paper's method.** The method's rate–distortion position is set by its tokenization procedure: open-loop nearest-medoid assignment, then batch inverse kinematics with an empirical prior and snapping. Its learned vocabulary is not the limit: closed-loop tokenization over the same 600 medoids is nearly lossless at the reference's rate.
  - **Why a bigger corpus cannot help.** It can only improve the vocabulary. The paper's Table 5 also shows that 1% of the data (about 340 chains) gives the same distortion as the full 34K-chain corpus at |V| = 600.
  - **Why restricting encoders is ruled out.** It would remove the very direction in which the method improves.
  - **Net effect.** The gym rewards encoder and rate-allocation ideas from classical coding. The paper's own line reaches the same score through them.
- **Hierarchical merges show no held-out benefit, and the corpus was not scaled.**
  - **Paper's own evidence.** Table 16 observation 1 and Appendix K.2 say merges stop paying at high resolution even at 34K chains.
  - **This gym's evidence.** Five merge rounds add seven motifs that no held-out chain uses (`merge5`). At coarse resolution, 50 merge rounds (`lower_capacity`) cost more dictionary bits than they save.
  - **Compute.** The paper's merge regime needs hundreds of rounds, each tenth of which re-optimizes glue over every chain. The official implementation needs about 8–14 s per chain per pass on the one CPU a job receives; the fresh 128-chain fit alone took 31 minutes.
  - **What the test does show instead.** The paper's rigid-body refinement effect, at about 30× the seed noise.
- **Not covered:** downstream transfer, language-model generation and data-efficiency claims, and the comparison against learned VQ-VAE tokenizers that the paper's Pareto claim is about.
- **Encoder timeout.** The 7,200 s per-attempt timeout is a wall-clock feasibility bound. It is generous, since the reference encoder uses about 30–50 minutes per 128-chain slice, but a host more than about 2.4× slower could time it out.
