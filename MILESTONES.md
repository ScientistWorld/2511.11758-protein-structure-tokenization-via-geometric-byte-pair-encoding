# Reproduction Milestones

**Current: method_runs**

## Progress Log

### [2026-06-03 02:18] - method_runs
- Ran the official PT-BPE GEOBPE encode/induce path end-to-end on the tracked public PDB smoke subset.
- Confirmed the paper's actual algorithm executes: residue initialization, Geo-Pair merging, RMSD medoid partitioning, quantization, and glue optimization.

### [2026-06-04 08:10] - core_claim
- Expanded the scaled benchmark to all 12 tracked training chains and five held-out CAMEO chains.
- Official GEOBPE produced compact tokenization with meaningful held-out reconstruction quality, supporting the paper's core compression-distortion claim at small public-data scale.

### [2026-06-04 08:36] - core_claim
- Reused the learned GEOBPE vocabulary on both CAMEO and CASP14 held-out splits.
- `scoring/scores.json` now covers reconstruction quality (`rmsd`, `lddt`) and compactness constraints (`bpr`, `vocab_size`) for both experiments.
- `python validate.py --compare` passes.

### [2026-06-04 12:48] - core_claim
- Continuation audit confirmed the runnable path uses the official PT-BPE GEOBPE algorithm rather than a surrogate.
- Fixed standalone evaluator packaging by defaulting `scripts/evaluate.sh` to the multisplit artifact and adding a dependency-free metric fallback when NumPy is unavailable.
- Added the missing `scoring/CONSTRAINTS.md` compliance checklist.
- Did not restore `core_claim_plus`: the multisplit run strengthens the core claim, but the current benchmark does not yet include a broader Table 16 sweep, baseline comparison, downstream transfer result, or glue ablation.

### [2026-06-04 13:13] - core_claim
- Final verification confirmed the workspace remains at `core_claim`.
- Removed an unrun ablation from the scoring contract so the documented targets match completed scores.

### [2026-06-04 13:25] - core_claim
- Prepared a two-setting Table 16 sweep without claiming the next milestone before the new run completes.
- Renamed the completed multisplit artifact in scoring as `geobpe_table16_high` and added the pending `geobpe_table16_low` reference target.
- Tightened evaluator integrity so reconstruction quality metrics require emitted coordinate arrays.

### [2026-06-04 13:36] - core_claim
- Fixed the final validation failure by making lDDT the compact gym's primary reconstruction-quality metric while keeping RMSD as a scored secondary distortion metric.
- Re-ran `python validate.py` and `python validate.py --compare`; both pass.

## Historical Stop Justification (superseded by hardening)
- The earlier iteration stopped at `core_claim`; that assessment was withdrawn on 2026-11-09.

### 2026-11-09 — method_runs

Hardening audit supersedes the earlier `core_claim` assessment. That assessment relied on proximity to a published lDDT value on a tiny corpus and omitted full representation cost. The actual released algorithm runs, but a compression advantage over honest alternatives must be demonstrated, not inferred from matching numbers. The final enlarged, restored-setting comparison is pending; no broader claim is made before its results.

### 2026-11-09 — method_runs

All three final 50-round GEOBPE training runs completed. The combined audit was interrupted repeatedly by scheduler preemptions during inference. Atomic per-chain recovery now preserves that work. Public evaluation has been enlarged to the same 64 chains per length range as private evaluation, correcting dictionary-cost amortization. Final paired headroom and attack outcomes remain pending; completed fitting alone does not advance the scientific milestone.

### [2026-11-10] - method_runs
- The complete paired audit exposed insufficient main-codebook scale and expensive rarely used merges. No new comparative milestone is claimed.
- Restored the main paper codebook with a short compression schedule, corrected shared-dictionary amortization, and prepared a cost-preserving boundary-refinement headroom check.
- Numerical replay now measures decoded variation across preempted CPU hosts; reference and ablation raw streams are regenerated where the frozen model changed.

### [2026-11-10] - method_runs
- Final main-codebook training and all paired evaluations completed in job `35dca7a9-39a`; independent codec and parser checks passed.
- Fixed-cost refinement improves rank by +1.25409, paired 95% interval [1.195446, 1.319235]; lower capacity scores −2.95926. Reference is feasible and below all quality bounds.
- Major shortcuts fail or lose their selection benefit; full description length rejects the former free-frame baseline. Reference-only score files and preserved paper numbers pass validation.
- Remain at `method_runs`: no-merge encoding still matches geometry and slightly improves rate, so this scale does not establish the paper’s hierarchical merge advantage. Final packaging/valid-public-lookup replay reuses saved raw outputs.

### [2026-11-10] - method_runs
- Final rescore-only job `36b6eb18-d00` passed: a valid public whole-chain dictionary fails unseen complete-chain coverage, and forged quality fields fail the output schema.
- Fresh reference-only packaging and validation pass. The default driver again reproduces the reference end to end; the standalone baseline launcher uses the independent baseline already measured in the completed jobs.
- Final audit is packaged in `HARDENING.md`. The comparative merge benefit remains unestablished at this scale, so no higher milestone is claimed.
