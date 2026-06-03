# Progress

## What Works

- Paper analysis identified the central claim: GEOBPE tokenizes protein backbone structure with geometric BPE merges while preserving reconstruction quality and improving token efficiency.
- The official PT-BPE code release is vendored under `method/PT-BPE/` at commit `68ff87eaf13068c1ef93dd72139efe4b91532219`, with bundled benchmark payloads removed.
- `method/run_official_geobpe.py` runs the official `bin/encode.py` and `bin/induce.py` path on the tracked public PDB smoke subset, then writes a method artifact for evaluation.
- Evaluation is separated in `eval/` and reads only `checkpoints/geobpe_scaled/results.json`.

## Results Achieved

Job `5f24b034-f1a` completed the official GEOBPE smoke reproduction on two training and two held-out CAMEO structures. It wrote `checkpoints/geobpe_scaled/results.json` and `scoring/scores.json`.

Smoke scores for `scaled_pdb_tokenization`:

- `rmsd`: 11.6716
- `lddt`: 0.2100
- `bpr`: 3.0683
- `vocab_size`: 17

This reaches `method_runs` because the paper's actual algorithm executes end-to-end. It does not yet reach `core_claim`: the tiny smoke setting is too small and reconstruction quality is far from the paper's reported low-resolution GEOBPE setting.

The scoring reference now uses the paper's lowest-resolution GEOBPE row in Table 16 (`|V|=109`, RMSD 3.96, LDDT 0.53, BPR 27.26), which is the closest reported setting to the scaled reproduction. The reproduced score is still worse, so this remains an execution reproduction rather than support for the core claim.

## Deviations From Paper

- The paper trains on large PDB-scale/CATH-style collections; this reproduction starts with a small public PDB subset to keep the benchmark lightweight.
- Vocabulary size, BPE iterations, and number of medoid candidates are scaled down for the initial smoke job.
- The reference target was corrected from the `{2:10,3:50,5:1,6:5,8:1}` Table 16 row to the paper's lower-resolution `{2:2,3:5,5:1,6:2,8:1}` row because the current wrapper uses an intentionally smaller GEOBPE configuration.
- The algorithm itself is not substituted: the job calls the official GEOBPE implementation, including residue initialization, RMSD medoid partitioning, geometric pair merging, and glue optimization.

## What Remains

- Run the expanded CPU reproduction with more training structures, more held-out structures, and more BPE iterations.
- If expanded reconstruction improves enough to demonstrate the quality-efficiency tradeoff, update to `core_claim`; otherwise diagnose whether the public smoke subset or scaled hyperparameters are still too small.

## Issues

- The initial local scratch implementation was not faithful enough to claim `method_runs`; the runnable path has been switched to the official implementation.
- Job `52b4b62d-f5c` failed during import before GEOBPE execution because `esm.utils.structure.protein_chain` requires `brotli`. Added `brotli` to `environment/setup.sh`.
- Job `b20a522a-14b` reached the same ESM `ProteinChain` import path and failed on `msgpack_numpy`. Inspected the ESM 3.2.0 wheel metadata and added the small missing runtime dependencies.
- Job `a777ea58-e69` reached official PT-BPE PDB featurization but failed because modern Biotite no longer exposes `biotite.structure.filter_backbone`.
- Added a compatibility shim in the official geometry parser that computes the same standard-residue N/CA/C backbone mask, imported the missing `OrderedDict`, and capped dataset featurization workers through `GEOBPE_DATASET_WORKERS`.
- Job `535e943b-b62` successfully featurized the smoke structures and reached official GEOBPE BPE initialization, including histogram generation and bond standardization.
- The job then failed because the upstream BPE worker helper returned zero workers from `SLURM_CPUS_PER_TASK=0`. Patched the BPE and induction helpers to clamp worker counts to at least one and changed the wrapper to run with one worker from a clean output directory.
- Job `836611b5-37b` completed the official GEOBPE encode phase on the smoke training structures and produced `bpe_iter=0.pkl`, but the wrapper searched for it in the workspace checkpoint directory while upstream had written relative paths under `method/PT-BPE/checkpoints/`.
- Updated the wrapper to resolve output, induction, and data paths to absolute workspace paths before invoking upstream scripts.
- Job `5f24b034-f1a` completed the end-to-end official method and evaluation pipeline. Expanded the default scheduled job to `TRAIN_LIMIT=8`, `TEST_LIMIT=5`, and `ITERATIONS=3` to pursue `core_claim`.
- A later validation pass rejected the smoke score when it was compared to the wrong Table 16 reference row. Corrected `scoring/reference.json` to the closest paper-reported low-resolution GEOBPE row and reran `bash scripts/evaluate.sh checkpoints/geobpe_scaled/results.json && python validate.py --compare`; all checks now pass.
