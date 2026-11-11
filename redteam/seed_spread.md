# Reference training-seed spread (private test)

Same settings and fitting data; only the sampling/k-medoid seed changes. Ranks use the fixed cohort scales of `redteam/hardening_final.json`.

| Seed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1.9803 | 0.7557 | 44.207 | 1.5183 | 0.8241 | 44.178 | 2100 |
| 1 | 1.9865 | 0.7553 | 44.207 | 1.5304 | 0.8230 | 44.178 | 2100 |
| 2 | 1.9946 | 0.7546 | 44.207 | 1.5314 | 0.8195 | 44.178 | 2100 |

| Cohort scales | Seed 1 rank [paired 95%] | Seed 2 rank [paired 95%] | Seed spread (max−min) | refined_glue | closed_loop_internal |
|---|---|---|---:|---:|---:|
| science | -0.0046 [-0.0287, 0.0194] | -0.0147 [-0.0333, 0.0043] | 0.0147 | +0.4244 | +1.2815 |
| science_without_closed_loop | -0.0048 [-0.0299, 0.0203] | -0.0153 [-0.0347, 0.0046] | 0.0153 | +0.4469 | — |
| all | -0.0043 [-0.0262, 0.0177] | -0.0136 [-0.0308, 0.0039] | 0.0136 | +0.3885 | +1.1639 |
