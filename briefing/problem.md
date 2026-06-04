# Problem Definition

The task is to tokenize protein backbone structures into a compact vocabulary of reusable structural units. A candidate method receives training protein backbones and must learn a discrete structural vocabulary. On held-out structures it should encode the backbone into a token sequence and reconstruct the backbone from those tokens.

The benchmark measures whether the tokenization preserves geometry while using few bits per residue. Inputs are backbone atom coordinates from public PDB chains, represented by N, CA, and C atoms per residue. Outputs are JSON artifacts containing per-structure token counts and, for full evaluation, original and reconstructed backbone coordinates.

The problem definition is method agnostic: future systems may use any tokenizer that writes the expected artifact format, as long as it is trained only on the provided training split and evaluated on the held-out split.
