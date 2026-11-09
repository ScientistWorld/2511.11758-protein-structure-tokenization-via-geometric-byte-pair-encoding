# Gym scoring audit

**The score responds to substantial genuine improvements, but does not reliably reward the paper's scientific contribution.** Increasing quantization resolution improves geometry and raises rank beyond the three-seed spread; reducing capacity lowers rank beyond that spread. However, removing the central BPE merge procedure leaves both reconstruction metrics exactly unchanged and improves the two compression metrics. **The reproduced method also loses to the supplied residue baseline on every scored metric.** That baseline transmits continuous boundary frames whose information cost is absent from the score. These are failures of the benchmark's scientific comparison, even before deliberate artifact shortcuts.

All numbers below come from actual runs through the unchanged hidden test. RMSD and BPR are lower-is-better, lDDT higher-is-better, and vocabulary size `V` lower-is-better. `C / P` means CAMEO / CASP14. The reference is the reproduced `geobpe_table16_high` in the original `scoring/scores_test.json`, rather than the paper numbers in `reference.json`.

**Scientific sensitivity.** Each row has a runnable `redteam/<case>/run.sh` and saved test scores, except the explicitly failed ablation.

| Variant | RMSD C / P | lDDT C / P | BPR C / P | V | Rank over reference, audit / control scales |
|---|---:|---:|---:|---:|---:|
| Reference artifact and fresh seed 0 | 7.516185 / 4.207396 | .577381 / .574539 | 7.774787 / 7.774787 | 219 | 0 / 0 |
| `better_bins300`: 300 rather than 50 bins, otherwise same training procedure | 3.364105 / 2.888040 | .694959 / .645111 | 9.912889 / 9.912889 | 964 | +.693188 / +.629933 |
| `better_glue`: translation loss weight 1 rather than .1, following the paper's ablation | 7.825877 / 3.918290 | .571080 / .600697 | 7.768184 / 7.768184 | 218 | +.042926 / +.213450 |
| `lower_capacity`: fewer residue/pair medoids | 12.528728 / 7.154893 | .342748 / .424688 | 7.316248 / 7.348728 | 163 | -1.238218 / -3.488790 |
| `no_bpe_shortcut`: official initialized vocabulary, zero BPE rounds | 7.516185 / 4.207396 | .577381 / .574539 | 7.714246 / 7.714246 | 210 | +.000027 / +.034073 |
| `weaker_no_glue`: glue disabled | Training completed; induction failed | No test score | — | — | Failed before evaluation |

The stronger quantization model pays a real rate/vocabulary cost and improves both geometry metrics on both experiments. Its rank gain exceeds the seed spread under both reported normalizations. The lower-capacity model makes the converse tradeoff and ranks lower. The glue-weight change has a mixed effect and its aggregate gain is smaller than seed spread: it is **not demonstrated improvement**. The no-glue ablation fails in the upstream quantizer with `value 0.0002127341431332752 is below the first bin range`; it supplies no evidence about score ordering. The successful lower-capacity run and the successful removal of BPE cover the weaker-method checks.

The `no_bpe_shortcut` is an honest alternative that the test cannot distinguish in reconstruction quality. Both experiments have one motif token per residue with and without merges; only unused vocabulary entries change. Its tiny aggregate gain is below aggregate seed spread and is not a research improvement. Nevertheless it strictly beats the matched seed-0 reference through lower BPR and smaller vocabulary, with identical geometry. The test does not establish a benefit from its central hierarchical merge idea.

**Rank calculation and its limits.** The hidden evaluator produces metric JSON, not an aggregate rank. [The analysis program](redteam/analyze.py) applies the specified ranking rule to those JSON files:

`rank = sum_experiments weight * sum_metrics abs(coefficient) * direction * (attempt - reproduced_reference) / cohort_sd`.

Both experiment weights are .5. Coefficient magnitudes are .6 for RMSD, 1 for lDDT, .4 for BPR, and .1 for vocabulary. Direction alone determines improvement; the negative coefficient signs are not applied a second time. Standardization is per experiment and metric, so changing a metric's units does not change its influence. We use population standard deviations; using sample standard deviations on a fixed cohort rescales every total equally.

The future ranking population is unknown. “Audit” uses all 16 successful, finite, complete attempts collected here. “Control scales” uses the seven successful reference/scientific-control attempts, and evaluates every candidate at those fixed scales as a sensitivity diagnostic. The latter is not a second actual ranking population containing every shortcut. Complete raw scores, scales, contributions, and invalid-output records are in [summary.json](redteam/summary.json); each successful complete case also has `rank.json`.

The negative-count outlier inflates the audit cohort's BPR standard deviations to 803.89 / 1553.15 and vocabulary standard deviation to 242111.82. Its enormous raw numbers therefore do **not** guarantee a win: it loses in the audit cohort. Claims below based on componentwise dominance or exact ties hold for any positive standardization scales, independent of these cohort choices.

**Three-seed spread.** The fresh seed-0 run reproduces the stored reference to floating-point precision. All three seeds retrain and induce both public held-out splits.

| Seed | RMSD C / P | lDDT C / P | BPR both | V | Rank, audit / control scales |
|---|---:|---:|---:|---:|---:|
| 0 | 7.516185 / 4.207396 | .577381 / .574539 | 7.774787 | 219 | 0 / 0 |
| 1 | 7.734951 / 4.767184 | .535656 / .577102 | 7.774787 | 219 | -.128686 / -.359406 |
| 2 | 6.762202 / 4.510420 | .534544 / .571709 | 7.768184 | 218 | -.064649 / -.222791 |
| Max minus min | .972749 / .559788 | .042838 / .005393 | .006603 | 1 | .128686 / .359406 |

These ranges, not a single seed's score, are the noise threshold used above. Reference training plus induction took about 6.2–10.0 minutes per seed on one CPU; the better-bin run took 5.2 minutes. These timings are observations, not scored metrics.

**Reproduction and baseline check.** The runnable reference uses the official PT-BPE implementation: residue initialization, geometric pair selection, medoid clustering, quantization, and glue optimization. It is recognizable as the paper's algorithm. That establishes execution, not the main comparative claim. The paper describes a compression–distortion Pareto advantage over tokenizers such as ProToken and VQ-VAE. Those comparisons are absent here.

The shipped `baseline/residue_quantized.py` delegates to `method.geobpe_repro.geobpe.residue_baseline`. Its existing exporter emits scalar quality fields without coordinate arrays, which the current evaluator rejects. `supplied_baseline_shortcut` runs the same fitted 16-medoid, zero-merge predictor and exports its existing predictions as coordinates, without changing predictions. It scores:

| Method | RMSD C / P | lDDT C / P | BPR both | V | Audit rank |
|---|---:|---:|---:|---:|---:|
| Reproduced reference | 7.516185 / 4.207396 | .577381 / .574539 | 7.774787 | 219 | 0 |
| `supplied_baseline_shortcut` | .007814 / .010967 | 1 / 1 | 4 | 16 | +2.352529 |

The baseline stores exact floating-point relative rotations and translations between residue frames in `glue_from_prev`. Reconstruction composes those transforms, retaining almost all backbone geometry. The scorer counts the 16-way motif IDs but none of that continuous side information. It is therefore a **shortcut**, not evidence of a superior discrete compressor. A simple baseline is already essentially perfect in geometry and componentwise better than the reference; the benchmark fails the requested baseline sanity check. The baseline also depends on `method/`, so its supplied packaging is unavailable when that directory starts empty.

The reproduced method's material departures from the paper are:

| Aspect | Gym reference | Paper setting or procedure |
|---|---|---|
| Data and test scale | 12 training chains; 5 public chains per held-out split; hidden scoring selects 3 CAMEO and 2 CASP14 chains | 33,992 training and 3,810 validation structures, with larger held-out benchmarks (Appendix B) |
| Merge duration and sampling | 3 rounds; occurrence cap 100 | Much larger checkpoint sweeps; default occurrence cap 5,000 |
| Resolution and medoids | 50 bins; `2:10,3:50,5:1,6:5,8:1` | The medoid schedule is a real Table 16 regime, but default reconstruction settings use 500 bins and a larger schedule; 50 bins is also used for transfer/coarsening |
| Bond lengths | `free_bonds=False` | Default reconstruction setting `True`; fixed lengths are a separate ablation/transfer setting |
| Adaptive requantization | `rmsd-super-res=False` | Default `True` uses original backbone occurrences for the update; this changes procedure, not merely resource scale |
| Glue | Prior 0, optimize every round, translation weight .1 | Table 14 prior 1, every 10 rounds; final Pareto experiments use translation weight 1 |
| Distortion | Simple CA-only lDDT approximation; targets supplied by method artifact | Standard reconstruction RMSD/lDDT against the actual structure |
| Bit accounting | Motif-token count times `log2(V)`; no glue stream or codebook description length | Explicit encoded representation and tokenizer description length; motif and glue-bin tokens are part of the representation |
| Comparisons and scope | High operating point only; no scored ProToken/VQ-VAE comparison | Multiple operating points, comparative Pareto curves, OOD and downstream results |

The paper's Table 16 high row copied into `reference.json` is RMSD 1.77, lDDT .70, BPR 34, V 237. Those paper numbers are reused for both experiments there; they are not the gym's reproduced test scores. The low paper operating point is listed there but is not produced by the default artifact. The gym's much lower BPR cannot be read as a compression improvement over the paper because the accounting differs. The existing `core_claim` milestone is not supported by these comparative checks; this audit leaves the original milestone document unchanged as requested.

**Bounds and task-failure check.** No scored reference metric is already at its physical bound, in either experiment: RMSD is above 0, lDDT below 1, BPR above 0, and vocabulary above the minimal positive size 1. Thus a better reference can be beaten; `better_bins300` does so. The implementation itself does not enforce nonnegative token counts or positive vocabulary sizes, so implemented compression scores have no valid lower bound.

The additive score has no task-validity gate. `constant_template_shortcut` returns the same invented two-residue object for every chain and reports zero tokens. It does not reconstruct the supplied proteins, yet receives RMSD 0, lDDT 1, BPR 0, V 1 and strictly dominates the reference on every metric. `truncated_output_shortcut` retains the full original target and returns only its first two residues, and still gets perfect geometry. Therefore a method failing the task can outrank the reference. Separate quality and compactness terms do not enforce a meaningful compression constraint when the evaluator trusts the target, lengths, and rate fields supplied by the method. Negative counts additionally demonstrate acceptance of impossible values, but are not counted as a winning shortcut under the audit cohort.

**Shortcut runs.** Every row has one `redteam/<name>/run.sh`. Successful outputs are saved as `scores_test.json` in that folder; rejected runs retain return codes and errors in `status.json`. Raw test values are experiment means for compactness; complete per-experiment results remain in the JSON. `Δrank` uses audit-cohort scales and the reference is 0.

| Shortcut folder | What it does | Test result `(RMSD, lDDT, BPR, V)`; Δrank | Works or fails |
|---|---|---|---|
| `no_bpe_shortcut` | Uses the official pre-merge initialized vocabulary and normal induction | `(5.86179, .575960, 7.71425, 210)`; +.000027 | **Works.** Honest alternative with identical geometry and improved compactness; gain is below aggregate seed noise |
| `supplied_baseline_shortcut` | Runs the supplied residue model with uncharged continuous frame glue | `(.009390, 1, 4, 16)`; +2.352529 | **Works.** Dominates every reference metric without a valid discrete bit accounting |
| `forged_target_shortcut` | Replaces artifact `original_coords` with the existing reconstruction | `(~0, 1, 7.77479, 219)`; +2.352333 | **Works.** The method moves the supposedly fixed comparison target; predictions are unchanged |
| `forged_counts_shortcut` | Leaves both coordinate arrays unchanged; writes `tokens=0`, `vocab_size=1` | `(5.86179, .575960, 0, 1)`; +.003025 | **Works.** Trusts invented compression fields; strictly dominates the reference independent of scales, although this cohort's gain is below seed spread |
| `public_dictionary_shortcut` | Enumerates all 10 visible held-out chains as whole-chain codewords, then exact-matches each input | `(~0, 1, .016153, 10)`; +2.355349 | **Works.** Visible test answers and uncharged dictionary storage solve the tiny test |
| `constant_template_shortcut` | Writes the same invented two-residue target and prediction for every required filename, with zero tokens | `(0, 1, 0, 1)`; +2.355358 | **Works.** Degenerate output achieves every physical metric bound |
| `truncated_output_shortcut` | Keeps the complete original target; predicts only its first two residues copied from input, with original full-chain rate fields | `(~0, 1, 7.77479, 219)`; +2.352333 | **Works.** Geometry silently truncates to the shorter array, rewarding almost empty reconstruction |
| `negative_counts_shortcut` | Uses full-sized all-zero predictions with real original coordinates; reports -1,000,000 tokens per chain and vocabulary -1,000,000 | `(17.7431, .010424, -4862.59, -1000000)`; -1.667061 | **Fails to pay in audit cohort**, despite acceptance. At fixed control scales its diagnostic total is +2835.65; no cohort-independent win is claimed |
| `quality_fields_shortcut` | Overwrites scalar row quality fields with RMSD 0 and lDDT 1; keeps coordinates | Reference metrics exactly; 0 | **Shortcut tie.** Scalar spoofing is ineffective because geometry is recomputed, but unchanged reference predictions still tie |
| `scalar_quality_shortcut` | Keeps the perfect scalar fields and removes coordinates | Test exit 1; no score | **Fails.** Missing advertised reconstruction arrays are rejected |
| `null_coords_shortcut` | Writes null coordinate arrays | Test exit 1; no score | **Fails.** Unsized-array error |
| `empty_coords_shortcut` | Writes empty coordinate arrays | Test exit 1; no score | **Fails.** Empty-array shape error, rather than a useful score |
| `prune_comparison_shortcut` | Uses visible train lDDT to keep only the preferred experiment in mutable `scores_train.json` | Test exits 0, emits CASP14 only with reference metrics; full rank unavailable | **Not demonstrated to pay.** Hidden evaluation trusts the mutable experiment selector, but the output violates the full scoring contract; downstream handling is unknown |

These shortcut families cover visible-answer recovery, self-written score inputs, moving ground truth/comparison selection, replacing a supposedly fixed target artifact, and degenerate/impossible outputs. No attack modifies evaluator code, interpreter state, packages, imports, or evaluator processes. None needs a process to survive the candidate run.

**Brute force and test size.** The `public_dictionary_shortcut` is an actual exhaustive dictionary: read all five CAMEO and five CASP14 files available to an agent, build ten whole-chain entries, enumerate entries for an exact match, and emit one token per chain. It does not read the hidden selection list or score files. It completes artifact creation plus visible and hidden evaluation in about 1.9 seconds and reconstructs every scored chain essentially exactly. The test is too small and too exposed to rule this out. This is memorization of visible held-out inputs, not evidence that exhaustive search solves the general geometric tokenizer problem. Counting the full dictionary and glue representation, and evaluating genuinely unseen chains, are necessary to make the intended compression problem nontrivial.

**Execution and scope.** The bundled CPU job `56a72c66-1ab` performed the main runs and resumed after scheduler preemption; `0318b64c-c51` independently confirmed the final truncation shortcut against complete targets. Each candidate's training/build step ends before the evaluator runs. Each scored trial installs its ordinary on-disk artifact, runs visible feedback, then invokes exactly `bash scripts/evaluate_test.sh` with no arguments in a new process. Evaluation sources were unchanged throughout every scored trial, recorded in each `status.json`; evaluator restoration therefore does not change these filesystem-only results. There is no network access during jobs.

The suite reads paper/hidden files only for this audit's interpretation and ranking analysis. Shortcut builders use agent-visible data, visible train feedback, and the allowed reuse of reference-trained outputs. Data-only dictionary and constant-template shortcuts also work without `method/`. Reference fixtures and large intermediate outputs are ignored and rebuildable; source, small scores, configurations, and status records are committed. [redteam/README.md](redteam/README.md) describes rerunning individual cases and the cohort analysis.

The temporary `scripts/run.sh` and original train score file were restored from the starting git revision. The ignored runtime artifact was restored from its original byte-for-byte snapshot after scheduler preemption interrupted a transaction. Method, baseline, data, evaluator, briefing, environment, scoring contract, and original test scores are unchanged, checked in [verification.json](redteam/verification.json). System-added job/trajectory entries were removed from the git index while their ignored runtime logs were retained. Pre-existing system-managed README/manifest, job-log, and trajectory working-tree differences were left intact. `action.yaml` is the required job-controller signal.
