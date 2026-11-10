# Constraints

Fit only on `data/downloads/pdb/train`; use public visible splits for model selection. Freeze all dictionary contents and operating points before receiving private requests. Do not train, tune, extend the dictionary, or select parameters on private inputs. Inference encodes each requested backbone using the frozen representation. Choosing transmitted symbols using the supplied input geometry is encoding; the decoder contents and global hyperparameters must stay fixed.

Each experiment must satisfy RMSD ≤15 Å, lDDT ≥0.35, 0<BPR≤96, and vocabulary between 1 and 8192. A failure in either experiment fails the attempt, below all feasible methods. These broad operating limits prevent lossless continuous geometry from replacing compact coding and prevent sacrificing reconstruction to get a tiny stream.

Transmit every value required for reconstruction in a supported decoder format. The evaluator charges dictionaries, boundary symbols, coordinate floats, and headers; it derives sizes and native residue counts itself. Supply every requested structure in full, with no extra or repeated ids. NaNs, infinities, negative indices, claimed metrics, supplied targets, invented counts, and unknown fields fail validation.

No network access during evaluation. Do not read private evaluation sources or answer artifacts during fitting, or modify evaluation files, reference comparisons, thresholds, or source lists. `eval/` and `data/` do not import the submitted method. Private targets and all artifacts that regenerate them remain under `eval/test/`.
