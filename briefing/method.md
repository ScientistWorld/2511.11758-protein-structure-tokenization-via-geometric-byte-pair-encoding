# Method

The paper proposes GEOBPE, a protein structure tokenizer that adapts byte pair encoding to 3D backbone geometry.

The reproduction uses the official PT-BPE GEOBPE code release at a reduced data scale. The implemented path runs the paper's tokenizer rather than a surrogate:

- initialize residue-level tokens by clustering residue backbone frames with Kabsch RMSD;
- build pair keys from adjacent token ids and quantized boundary geometry;
- repeatedly select frequent geometric pair keys;
- cluster occurrences of the selected pair into prototype structural motifs using RMSD medoids;
- greedily merge non-overlapping occurrences and hard-quantize them to medoid prototypes;
- optimize inter-motif glue angles with the official global glue optimization path;
- encode held-out structures by replaying the learned merge order without creating new keys;
- reconstruct structures and score RMSD, lDDT, bits per residue, and vocabulary size.

The main deviations are scale-related: the workspace uses a small public PDB subset, fewer BPE iterations, and a lower-resolution vocabulary than the paper's full PDB-scale experiments.
