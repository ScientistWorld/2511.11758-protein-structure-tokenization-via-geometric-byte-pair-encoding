# Overview

This workspace reproduces the core idea of “Protein Structure Tokenization via Geometric Byte Pair Encoding” at a small public-PDB scale. GEOBPE learns recurring protein backbone motifs by applying BPE-style merges to geometry-aware adjacent motif pairs, then evaluates whether the resulting discrete token sequences reconstruct structures accurately with fewer bits per residue.

The packaged benchmark vendors the official PT-BPE implementation, a public PDB smoke dataset, reusable evaluation code, reference paper numbers, and scripts for end-to-end reproduction.
