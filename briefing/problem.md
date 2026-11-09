# Problem

Compress complete protein backbone structures while preserving their geometry. Each input contains N, CA, and C coordinates for every residue. Fit a reusable representation on the 128 provided fitting chains. At inference, encode previously unseen inputs using the frozen representation; the evaluator reconstructs the complete backbone from what was transmitted.

The scientific task is a rate–distortion tradeoff. Better local distance preservation and lower aligned reconstruction error should require fewer transmitted bits. Dictionary storage and all per-input information count toward the rate. Fitting, tuning, dictionary construction, and operating-point selection on private evaluation inputs are prohibited.

Two length ranges measure ordinary reconstruction and accumulated error over longer backbones. Public and private evaluation each contain 64 chains per range, drawn using the same acquisition and continuity rules. The fitting set contains 64 chains in each range. Public and private source entries and exact sequences are disjoint.

Any encoding algorithm is allowed within the finite decoder formats described in evaluation.md. A new approach can use the interface without changing the evaluator. The legacy data/pdb_smoke files are development examples, not the private evaluation corpus.
