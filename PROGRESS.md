# Progress

## What Works

- Paper analysis identified the central claim: GEOBPE tokenizes protein backbone structure with geometric BPE merges while preserving reconstruction quality and improving token efficiency.
- The official PT-BPE code release is vendored under `method/PT-BPE/` at commit `68ff87eaf13068c1ef93dd72139efe4b91532219`, with bundled benchmark payloads removed.
- `method/run_official_geobpe.py` runs the official `bin/encode.py` and `bin/induce.py` path on the tracked public PDB smoke subset, then writes a method artifact for evaluation.
- Evaluation is separated in `eval/` and reads only `checkpoints/geobpe_scaled/results.json`.

## Results Achieved

No completed compute job has been scored yet. The next CPU test job is prepared to execute official GEOBPE and write `scoring/scores.json`.

## Deviations From Paper

- The paper trains on large PDB-scale/CATH-style collections; this reproduction starts with a small public PDB subset to keep the benchmark lightweight.
- Vocabulary size, BPE iterations, and number of medoid candidates are scaled down for the initial smoke job.
- The algorithm itself is not substituted: the job calls the official GEOBPE implementation, including residue initialization, RMSD medoid partitioning, geometric pair merging, and glue optimization.

## What Remains

- Run the prepared compute job and inspect `scoring/scores.json`.
- If the smoke run succeeds, scale up train/test limits or add an ablation while staying within the GPU-hour budget.

## Issues

- The initial local scratch implementation was not faithful enough to claim `method_runs`; the runnable path has been switched to the official implementation.
- Job `52b4b62d-f5c` failed during import before GEOBPE execution because `esm.utils.structure.protein_chain` requires `brotli`. Added `brotli` to `environment/setup.sh`.
- Job `b20a522a-14b` reached the same ESM `ProteinChain` import path and failed on `msgpack_numpy`. Inspected the ESM 3.2.0 wheel metadata and added the small missing runtime dependencies.
- Job `a777ea58-e69` reached official PT-BPE PDB featurization but failed because modern Biotite no longer exposes `biotite.structure.filter_backbone`.
- Added a compatibility shim in the official geometry parser that computes the same standard-residue N/CA/C backbone mask, imported the missing `OrderedDict`, and capped dataset featurization workers through `GEOBPE_DATASET_WORKERS`.
- Job `535e943b-b62` successfully featurized the smoke structures and reached official GEOBPE BPE initialization, including histogram generation and bond standardization.
- The job then failed because the upstream BPE worker helper returned zero workers from `SLURM_CPUS_PER_TASK=0`. Patched the BPE and induction helpers to clamp worker counts to at least one and changed the wrapper to run with one worker from a clean output directory.
