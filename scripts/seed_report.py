"""Training-seed spread of the reproduced reference on the private test.

Seeds 1 and 2 refit the reference with identical settings. Their evaluator-written
scores are ranked against the reference with the external rule, using the fixed
cohort scales of the final hardening audit (redteam/hardening_final.json), so the
spread is in the same rank units as the variants reported there. Paired intervals
resample the same private inputs. Only aggregates leave eval/test/.
"""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import hardening_report as hr
SEEDS={0:'geobpe_reference',1:'geobpe_seed1',2:'geobpe_seed2'}

def main():
 scores=json.loads((ROOT/'scoring/scores_test.json').read_text()); values=hr.table(scores)
 meas=json.loads((ROOT/'eval/test/measurements.json').read_text())
 audit=json.loads((ROOT/'redteam/hardening_final.json').read_text())['test']
 present={s:n for s,n in SEEDS.items() if n in values[hr.EXPS[0]]}
 failed={n:scores['_metadata']['failed'][n] for n in present.values() if n in scores['_metadata']['failed']}
 details={n:meas[n]['details'] for n in present.values() if not meas[n].get('failed',True)}
 out={'failed':failed,'scores':{n:{e:values[e][n] for e in hr.EXPS} for n in present.values()},'cohorts':{}}
 lines=['# Reference training-seed spread (private test)','',
  'Same settings and fitting data; only the sampling/k-medoid seed changes. Ranks use the fixed cohort scales of `redteam/hardening_final.json`.','',
  '| Seed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab |','|---|---:|---:|---:|---:|---:|---:|---:|']
 for s,n in present.items():
  v=values
  lines.append(f"| {s} | {v['short_backbones'][n]['rmsd']:.4f} | {v['short_backbones'][n]['lddt']:.4f} | {v['short_backbones'][n]['bpr']:.3f} | {v['long_backbones'][n]['rmsd']:.4f} | {v['long_backbones'][n]['lddt']:.4f} | {v['long_backbones'][n]['bpr']:.3f} | {v['long_backbones'][n]['vocab_size']:.0f} |")
 lines+=['','| Cohort scales | Seed 1 rank [paired 95%] | Seed 2 rank [paired 95%] | Seed spread (max−min) | refined_glue | closed_loop_internal |','|---|---|---|---:|---:|---:|']
 for label in ('science','science_without_closed_loop','all'):
  sd=audit['cohorts'][label]['scales']
  ranks={}; ci={}
  for s,n in present.items():
   ranks[n]=float(sum(hr.W[e]*c*(1 if up else -1)*(values[e][n][m]-values[e][hr.REF][m])/sd[e][m] for e in hr.EXPS for m,(up,c) in hr.M.items() if sd[e][m]>1e-12))
   if n!=hr.REF and n in details and hr.REF in details: ci[n]=hr.paired(details,n,values,sd)
  spread=max(ranks.values())-min(ranks.values()) if ranks else None
  other=audit['cohorts'][label]['ranks']
  out['cohorts'][label]={'ranks':ranks,'paired_95ci':ci,'spread':spread}
  cell=lambda n: (f"{ranks[n]:+.4f} {[round(x,4) for x in ci[n]] if n in ci else ''}" if n in ranks else '—')
  fmt=lambda k: f"{other[k]:+.4f}" if k in other else '—'
  lines.append(f"| {label} | {cell(SEEDS[1])} | {cell(SEEDS[2])} | {spread:.4f} | {fmt('refined_glue')} | {fmt('closed_loop_internal')} |")
 if failed: lines+=['',f'Failed seeds: {failed}']
 (ROOT/'redteam/seed_spread.json').write_text(json.dumps(out,indent=1,allow_nan=False)+'\n')
 (ROOT/'redteam/seed_spread.md').write_text('\n'.join(lines)+'\n')
 print('\n'.join(lines))
if __name__=='__main__': main()
