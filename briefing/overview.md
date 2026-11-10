# Overview

This workspace studies compact lossy coding of complete protein backbones. Fit a representation on 128 public PDB chains, then encode unseen structures with a frozen dictionary. Public and private evaluation each contain another 128 chains, split equally between short and long backbones. Reconstruction error, local distance preservation, complete description length, and alphabet size are measured independently from raw representations.

The reference uses the released implementation from “Protein Structure Tokenization via Geometric Byte Pair Encoding,” with documented resource reductions. The package includes public-source acquisition commands, an independent coding baseline, separate public and private evaluators, preserved paper results, and an end-to-end reference driver in `scripts/run.sh`.

The test scores every method from its decoded raw representation, records failed attempts at the worst value of every metric, and distinguishes measured fidelity and rate improvements from weaker controls on paired unseen inputs. The reference sits at the operating point the paper reports for its main codebook; at this scale merge rounds add only unused vocabulary, so a hierarchical-merge rate benefit is not established. See `HARDENING.md` for paired comparisons, shortcut replays, headroom and remaining limitations.
