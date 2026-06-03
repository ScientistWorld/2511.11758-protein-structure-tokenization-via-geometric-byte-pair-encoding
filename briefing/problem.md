# Problem Definition

What problem does this paper address? Write this so that someone with no knowledge of the paper can understand what needs to be solved and how success is measured.

Do NOT describe the paper's method or solution here — only the problem itself. Think about if a future scientist agent try to solve this problem from scratch without knowing what approach the paper took. If you leak the solution, you compromise the benchmark.

## Research Question

<!-- What problem or challenge does this paper tackle? What gap in existing work does it address? -->

## Why It Matters

<!-- Why is this problem important? What would a good solution enable? Make it short -->

## Success Criteria

<!-- What would a successful solution look like? What properties should it have? This is about the goal, not the paper's specific approach. Make it short -->
# Problem Definition

The task is to tokenize protein backbone structures into a compact vocabulary of reusable structural units. A candidate method receives training protein backbones and must learn a discrete structural vocabulary. On held-out structures it should encode the backbone into a token sequence and reconstruct the backbone from those tokens.

The benchmark measures whether the tokenization preserves geometry while using few bits per residue. Inputs are backbone atom coordinates from public PDB chains, represented by N, CA, and C atoms per residue. Outputs are JSON artifacts containing per-structure token counts, reconstructed coordinates, and reconstruction metrics.

The problem definition is method agnostic: future systems may use any tokenizer that writes the expected artifact format, as long as it is trained only on the provided training split and evaluated on the held-out split.
