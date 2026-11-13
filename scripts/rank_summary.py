"""Rank attempts from an evaluator-written score file (pure Python, no numpy).

Applies the external rule: for each experiment and metric, weight * |coefficient|
* direction * (attempt - reference) / population standard deviation over the
cohort, summed. Failed attempts enter at the evaluator's fixed worst values.
Usage: python scripts/rank_summary.py SCORES.json [--exclude NAME ...] [--json OUT]
"""
import argparse,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REF='geobpe_reference'

def ranks(scores,cohort,contract):
 exps=list(contract['experiments']); out={n:0. for n in cohort}; scales={}
 for e in exps:
  spec=contract['experiments'][e]; res=scores['experiments'][e]['results']; scales[e]={}
  for m,d in spec['metrics'].items():
   vals=[res[n][m] for n in cohort]; mu=sum(vals)/len(vals)
   sd=math.sqrt(sum((v-mu)**2 for v in vals)/len(vals)); scales[e][m]=sd
   if sd<=1e-12: continue
   sign=1 if d['higher_is_better'] else -1
   for n in cohort: out[n]+=spec['weight']*abs(d['coefficient'])*sign*(res[n][m]-res[REF][m])/sd
 return out,scales

def main():
 p=argparse.ArgumentParser(); p.add_argument('scores'); p.add_argument('--exclude',nargs='*',default=[]); p.add_argument('--json'); a=p.parse_args()
 contract=json.loads((ROOT/'eval/test/contract.json').read_text()); scores=json.loads(Path(a.scores).read_text())
 names=sorted(scores['experiments'][next(iter(contract['experiments']))]['results'])
 cohort=[n for n in names if n not in a.exclude and not n.startswith('attack_')]
 r,sd=ranks(scores,cohort,contract); failed=scores['_metadata']['failed']
 print('| Attempt | Failed | Short RMSD | Short lDDT | Short BPR | Long RMSD | Long lDDT | Long BPR | Vocab | Rank |')
 print('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|')
 for n in sorted(cohort,key=lambda n:-r[n]):
  s=scores['experiments']['short_backbones']['results'][n]; l=scores['experiments']['long_backbones']['results'][n]
  print(f"| {n} | {n in failed} | {s['rmsd']:.4f} | {s['lddt']:.4f} | {s['bpr']:.3f} | {l['rmsd']:.4f} | {l['lddt']:.4f} | {l['bpr']:.3f} | {l['vocab_size']:.0f} | {r[n]:+.4f} |")
 print('cohort scales:',json.dumps({e:{m:round(v,5) for m,v in d.items()} for e,d in sd.items()}))
 if a.json: Path(a.json).write_text(json.dumps({'cohort':cohort,'ranks':r,'scales':sd,'failed':failed},indent=1)+'\n')
if __name__=='__main__': main()
