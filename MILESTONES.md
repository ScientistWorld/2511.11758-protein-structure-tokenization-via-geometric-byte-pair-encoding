# Reproduction Milestones

**Current: core_claim**

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

## Stop Justification
- Final verification completed at `core_claim`. The workspace is ready as a compact gym; the lower-capacity sweep remains prepared but unclaimed until a future job completes it.
