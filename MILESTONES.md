# Reproduction Milestones

**Current: none**

<!-- Milestone levels (update "Current" above as you progress):
  none             — just started, no meaningful progress yet
  method_runs      — the paper's method executes end-to-end without errors
  core_claim       — minimum experiment supports the paper's central claim
  core_claim_plus  — core claim reproduced on additional settings
  secondary_claims — secondary results or contributions reproduced
  majority         — more than half of reported results reproduced
  near_complete    — most results reproduced, only minor gaps remain
  full             — all reported results reproduced
-->

## Progress Log

### [2026-06-03 00:00] - none
- Read the paper and identified GEOBPE as a geometry-grounded BPE tokenizer over protein backbone motifs.
- Replaced the initial scratch implementation as the primary path with the official PT-BPE GEOBPE code release, because the scratch path did not yet implement enough of the paper's algorithm.
- Prepared a CPU job to run official GEOBPE and evaluation on a small public PDB subset.

### [2026-06-03 05:55] - none
- First compute job reached the official PT-BPE import path but failed before GEOBPE execution due to a missing `brotli` dependency required by ESM's `ProteinChain`.
- Added the missing dependency and kept the milestone at `none`.

## Stop Justification
- Not stopped.
