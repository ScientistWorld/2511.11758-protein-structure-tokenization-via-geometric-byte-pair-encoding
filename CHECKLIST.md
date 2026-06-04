# Checklist

## Briefing

- [x] `briefing/problem.md`
- [x] `briefing/evaluation.md`
- [x] `briefing/method.md`
- [x] `briefing/overview.md`

## Scoring

- [x] `scoring/reference.json`
- [x] `scoring/EXPERIMENTS.md`
- [x] `scoring/TARGETS.md`
- [x] `scoring/CONSTRAINTS.md`
- [x] `scoring/DIRECTION.md`
- [x] Workspace validated via `python validate.py`
- [x] `scoring/scores.json`

## Code

- [x] Evaluation code in `eval/`
- [x] Official method code in `method/PT-BPE/`
- [x] Reproduction wrapper in `method/run_official_geobpe.py`
- [x] Baseline implementation in `baseline/`

## Scripts And Environment

- [x] `scripts/evaluate.sh`
- [x] `scripts/reproduce.sh`
- [x] `scripts/download.sh`
- [x] `scripts/baseline.sh`
- [x] `environment/container.def`
- [x] `environment/setup.sh`

## Data

- [x] Public PDB smoke subset tracked in `data/pdb_smoke/`
- [x] Idempotent downloader for the PDB subset
- [x] No pretrained models required

## Milestones

- [x] `method_runs`
- [x] `core_claim`
- [x] `core_claim_plus`
- [ ] `secondary_claims`
- [ ] `majority`
- [ ] `near_complete`
- [ ] `full`
