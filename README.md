# Protein Structure Tokenization via Geometric Byte Pair Encoding

| This paper | Scientist World, the framework this environment belongs to |
|:---:|:---:|
| <a href="https://arxiv.org/abs/2511.11758"><img alt="This paper on arXiv" src="https://img.shields.io/badge/arXiv-2511.11758-b31b1b?logo=arxiv&logoColor=white"></a> | <a href="https://arxiv.org/abs/2611.08478"><img alt="Scientist World on arXiv" src="https://img.shields.io/badge/arXiv-2611.08478-b31b1b?logo=arxiv&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world"><img alt="Scientist World code" src="https://img.shields.io/badge/Code-Scientist_World-181717?logo=github&logoColor=white"></a> <a href="https://github.com/zlab-princeton/scientist_world_cli"><img alt="Command line code" src="https://img.shields.io/badge/Code-Command_line-181717?logo=github&logoColor=white"></a> |

| | |
|---|---|
| **Paper ID** | [2511.11758](https://arxiv.org/abs/2511.11758) |

## Summary

This workspace reproduces the core idea of “Protein Structure Tokenization via Geometric Byte Pair Encoding” at a small public-PDB scale. GEOBPE learns recurring protein backbone motifs by applying BPE-style merges to geometry-aware adjacent motif pairs, then evaluates whether the resulting discrete token sequences reconstruct structures accurately with fewer bits per residue.

## Run it

```bash
pip install sciworld
sw research 2511.11758 --mode innovate --agent claude-code
sw evaluate 2511.11758
```

## More

The full problem statement, method notes, evaluation protocol and reproduction log are in [DETAILS.md](DETAILS.md).

