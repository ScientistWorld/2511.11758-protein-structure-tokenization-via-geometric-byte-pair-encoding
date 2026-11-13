"""Hardening audit summary from evaluator-written score files.

Ranks follow the external rule exactly: for each experiment and metric,
weight * |coefficient| * direction * (value - reference) / cohort standard
deviation (population), summed. Values are read from scoring/scores_*.json, so a
failed attempt enters at the evaluator's fixed worst values. Paired bootstrap
intervals resample the same private inputs for every method. Only aggregates
leave eval/test/; per-input details stay there.
"""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
REF='geobpe_reference'
CONTRACT=json.loads((ROOT/'eval/test/contract.json').read_text())
EXPS=list(CONTRACT['experiments'])
W={e:CONTRACT['experiments'][e]['weight'] for e in EXPS}
M={m:(d['higher_is_better'],abs(d['coefficient'])) for m,d in CONTRACT['experiments'][EXPS[0]]['metrics'].items()}
BOUNDS={'rmsd':0.,'lddt':1.,'bpr':0.,'vocab_size':1.}
# Hand-designed closed-loop codecs (no learned vocabulary); every other attempt is the
# reference, a baseline, or a variant of the paper's tokenizer.
SHORT_CODECS={'closed_loop_internal','closed_loop_motif'}

def read(p): return json.loads((ROOT/p).read_text())

def table(scores):
 return {e:scores['experiments'][e]['results'] for e in EXPS}

def scales(values,cohort):
 return {e:{m:float(np.std([values[e][n][m] for n in cohort])) for m in M} for e in EXPS}

def ranks(values,cohort):
 sd=scales(values,cohort)
 return {n:float(sum(W[e]*c*(1 if up else -1)*(values[e][n][m]-values[e][REF][m])/sd[e][m] for e in EXPS for m,(up,c) in M.items() if sd[e][m]>1e-12)) for n in cohort},sd

def paired(details,name,values,sd,draws=1000):
 rng=np.random.default_rng(20261110)
 ix={e:rng.integers(0,len(details[REF][e]['rmsd']),(draws,len(details[REF][e]['rmsd']))) for e in EXPS}
 for e in EXPS: assert details[name][e]['ids']==details[REF][e]['ids'],'inputs differ'
 total=sum(np.asarray(details[REF][e]['residues'])[ix[e]].sum(1) for e in EXPS)
 out=np.zeros(draws)
 for e in EXPS:
  def stats(d,vocab):
   return {'rmsd':np.asarray(d['rmsd'])[ix[e]].mean(1),'lddt':np.asarray(d['lddt'])[ix[e]].mean(1),
           'bpr':np.asarray(d['bits'])[ix[e]].sum(1)/np.asarray(d['residues'])[ix[e]].sum(1)+d['model_bits']/total,'vocab_size':vocab}
  c=stats(details[name][e],values[e][name]['vocab_size']); r=stats(details[REF][e],values[e][REF]['vocab_size'])
  for m,(up,coef) in M.items():
   if sd[e][m]>1e-12: out+=W[e]*coef*(1 if up else -1)*(c[m]-r[m])/sd[e][m]
 return [float(v) for v in np.quantile(out,[.025,.975])]

def same_streams(side,a,b):
 try:
  x=read(f'eval/{side}/runs/{a}/outputs.json'); y=read(f'eval/{side}/runs/{b}/outputs.json')
 except (OSError,ValueError): return None
 bx={r['id']:r for r in x}; by={r['id']:r for r in y}
 return sum(bx[k]!=by.get(k) for k in bx)

def main():
 report={}
 lines=['# Final hardening audit (generated)','',
  'Ranks apply the external rule to `scoring/scores_test.json` as written by `scripts/evaluate_test.sh`; failed attempts enter at the fixed worst values. Cohort standard deviations are population values. Paired 95% intervals use 1,000 bootstrap resamples of the same private inputs.','']
 for side in ('test','train'):
  scores=read(f'scoring/scores_{side}.json'); values=table(scores); meas=read(f'eval/{side}/measurements.json')
  names=sorted(values[EXPS[0]]); attacks=[n for n in names if n.startswith('attack_')]
  science=[n for n in names if n not in attacks]; core=[n for n in science if n not in SHORT_CODECS]
  cohorts={'all':names,'science':science,'paper_line':core}
  side_report={'failed':scores['_metadata']['failed'],'scored':values,'measured':{n:meas[n].get('metrics') for n in names},'cohorts':{}}
  details={n:meas[n]['details'] for n in names if not meas[n].get('failed',True) and 'details' in meas[n]}
  for label,cohort in cohorts.items():
   r,sd=ranks(values,cohort); entry={'ranks':r,'scales':sd,'paired_95ci':{}}
   if side=='test':
    for n in cohort:
     if n in details and n!=REF: entry['paired_95ci'][n]=paired(details,n,values,sd)
   side_report['cohorts'][label]=entry
  side_report['reference_at_bound']=[f'{e}/{m}' for e in EXPS for m,v in values[e][REF].items() if abs(v-BOUNDS[m])<1e-12]
  side_report['replay_no_bpe_vs_reference_changed_streams']=same_streams(side,REF,'no_bpe')
  report[side]=side_report
  lines+=[f'## {side} slice','','| Attempt | Failed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab | Rank (all) | Rank (science) | Rank (paper line) |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
  for n in names:
   v=values; rk=side_report['cohorts']
   cell=lambda lab: f"{rk[lab]['ranks'][n]:.4f}" if n in rk[lab]['ranks'] else '—'
   lines.append(f"| {n} | {n in scores['_metadata']['failed']} | {v['short_backbones'][n]['rmsd']:.4f} | {v['short_backbones'][n]['lddt']:.4f} | {v['short_backbones'][n]['bpr']:.3f} | {v['long_backbones'][n]['rmsd']:.4f} | {v['long_backbones'][n]['lddt']:.4f} | {v['long_backbones'][n]['bpr']:.3f} | {v['long_backbones'][n]['vocab_size']:.0f} | {cell('all')} | {cell('science')} | {cell('paper_line')} |")
  lines+=['','Measured (unscored) metrics of failed attempts and failure reasons:','']
  for n,reasons in scores['_metadata']['failed'].items():
   mm=meas[n].get('metrics')
   meas_txt='; '.join(f"{e}: RMSD {mm[e]['rmsd']:.4f}, lDDT {mm[e]['lddt']:.4f}, BPR {mm[e]['bpr']:.3f}" for e in EXPS) if mm else 'not measurable'
   lines.append(f"- `{n}` — {'; '.join(reasons)} — measured: {meas_txt}")
  if side=='test':
   lines+=['','Paired 95% rank intervals versus the reference:','','| Attempt | science cohort | paper-line cohort |','|---|---|---|']
   for n in science:
    a=side_report['cohorts']['science']['paired_95ci'].get(n); b=side_report['cohorts']['paper_line']['paired_95ci'].get(n)
    if a or b: lines.append(f"| {n} | {[round(x,4) for x in a] if a else '—'} | {[round(x,4) for x in b] if b else '—'} |")
  lines+=['',f"Reference metrics at a best bound: {side_report['reference_at_bound'] or 'none'}.",f"Chains whose raw streams differ between the fresh reference and the earlier-host no-merge replay: {side_report['replay_no_bpe_vs_reference_changed_streams']}.",'']
 try:
  replay=read('eval/test/replay_noise.json')
  report['forced_replay']={k:v for k,v in replay.items() if k!='absolute_metric_differences'}
  lines+=['Forced four-input fresh replay: '+json.dumps(report['forced_replay'],sort_keys=True),'']
 except (OSError,ValueError): pass
 out=ROOT/'redteam'; out.mkdir(exist_ok=True)
 (out/'hardening_final.json').write_text(json.dumps(report,indent=1,allow_nan=False)+'\n')
 (out/'hardening_final.md').write_text('\n'.join(lines)+'\n')
 print('\n'.join(lines))
if __name__=='__main__': main()
