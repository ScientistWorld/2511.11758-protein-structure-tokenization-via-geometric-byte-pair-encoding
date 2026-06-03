# Overview

- **Paper ID:** <!-- e.g. 1706.03762 -->
- **Title:** <!-- e.g. Attention Is All You Need -->
- **Domain:** <!-- e.g. Computer Vision / Object Detection -->
- **TL;DR:** <!-- One sentence: what this paper does and why it matters -->

## Short Summary

<!-- 3-5 sentences covering the problem, approach, and main findings -->

## Key Results

<!-- 2-3 bullet points: main findings or numbers in bullet points -->
# Overview

This workspace reproduces the core idea of “Protein Structure Tokenization via Geometric Byte Pair Encoding” at a small public-PDB scale. GEOBPE learns recurring protein backbone motifs by applying BPE-style merges to geometry-aware adjacent motif pairs, then evaluates whether the resulting discrete token sequences reconstruct structures accurately with fewer bits per residue.

The packaged benchmark contains a compact GEOBPE implementation, a public PDB smoke dataset, reusable evaluation code, reference paper numbers, and scripts for end-to-end reproduction.
