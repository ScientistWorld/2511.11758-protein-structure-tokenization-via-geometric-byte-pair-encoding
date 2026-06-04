# Reproduction Milestones

**Current: core_claim**

## Progress Log

### [2026-06-04 12:18] - core_claim
- Official PT-BPE GEOBPE code ran end-to-end on the tracked public PDB subset.
- The expanded CAMEO held-out run produced `scoring/scores.json` with reconstruction quality (`rmsd`, `lddt`) and compactness/efficiency metrics (`bpr`, `vocab_size`), supporting the scaled core tokenization claim.
- Prepared a second held-out CASP14 run to test whether the scaled result extends beyond the first held-out split.
