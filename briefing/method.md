# Paper's Method

How the paper approaches the problem, i.e. the paper's core contributions.

## Key Contribution

<!-- What is the paper's main contribution? -->

## Approach

<!-- How does the paper solve the problem? Key ideas, architecture, algorithm. -->

## Main Claims

<!-- What are the paper's central claims? Which are primary vs. secondary? -->
# Method

The paper proposes GEOBPE, a protein structure tokenizer that adapts byte pair encoding to 3D backbone geometry.

The reproduction implements the core computational loop at reduced scale:

- initialize residue-level tokens by clustering residue backbone frames with Kabsch RMSD;
- build pair keys from adjacent token ids and quantized boundary geometry;
- repeatedly select frequent geometric pair keys;
- cluster occurrences of the selected pair into prototype structural motifs using RMSD medoids;
- greedily merge non-overlapping occurrences and hard-quantize them to medoid prototypes;
- encode held-out structures by replaying the learned merge order without creating new keys;
- reconstruct structures and score RMSD, lDDT, bits per residue, and vocabulary size.

The main scale deviation is glue optimization. The paper optimizes inter-motif glue with global inverse kinematics and snaps glue bins. This implementation uses rigid placement against each held-out span as a lightweight analogue for the reconstruction refinement, while also reporting a no-refinement variant to expose drift.
