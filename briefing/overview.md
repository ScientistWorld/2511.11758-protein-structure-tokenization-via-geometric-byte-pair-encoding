# Overview

This workspace studies compact lossy coding of complete protein backbones. Fit a representation on 128 public PDB chains, then encode unseen structures with a frozen dictionary. Public and private evaluation each contain another 128 chains, split equally between short and long backbones. Reconstruction error, local distance preservation, complete description length, and alphabet size are measured independently from raw representations.

The reference uses the released implementation from “Protein Structure Tokenization via Geometric Byte Pair Encoding,” with documented resource reductions. The package includes public-source acquisition commands, an independent coding baseline, separate public and private evaluators, preserved paper results, and an end-to-end reference driver in `scripts/run.sh`.

The hardened test distinguishes a measured fidelity improvement at unchanged rate from a weaker control. At this fitting scale, however, the no-merge ablation matches reference geometry and saves a little storage; the paper's comparative merge benefit is not established. The audited milestone is `method_runs`. See `HARDENING.md` for paired comparisons, shortcut replays, and remaining limitations.
