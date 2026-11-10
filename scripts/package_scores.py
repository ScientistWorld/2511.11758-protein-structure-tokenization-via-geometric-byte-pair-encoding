"""Publish the reference runs' evaluator-written scores into scoring/reference.json.

The evaluators themselves write scoring/scores_train.json and scoring/scores_test.json.
This step copies the test-slice reference/baseline values into reference.json results,
keeps the paper's reported numbers verbatim under _paper_reported, mirrors train scores
to the legacy scoring/scores.json, refreshes the evaluator-owned canonical copy that
eval/test/ restores before scoring, and freezes per-input reference measurements on
each side for paired comparisons. It never computes a metric.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REF='geobpe_reference'; BASE='internal_baseline'
def read(p): return json.loads((ROOT/p).read_text())
def write(p,obj):
 path=ROOT/p; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

DESCRIPTIONS={
 'rmsd':'Mean complete-backbone RMSD in angstroms after proper Kabsch alignment.',
 'lddt':'Mean per-residue CA lDDT, 15 angstrom inclusion radius and tolerances 0.5, 1, 2, 4 angstroms.',
 'bpr':'Encoded streams plus the shared dictionary charged once across the full corpus, in bits per native residue.',
 'vocab_size':'Total dictionary and boundary alphabet size, also limited to 8192.'}
RANGES={'short_backbones':'64–192','long_backbones':'256–512'}

def main():
 contract=read('eval/test/contract.json')
 assert contract==read('eval/train/contract.json'),'public and private contracts differ'
 old=read('scoring/reference.json'); history=old['_paper_reported']
 test=read('scoring/scores_test.json'); train=read('scoring/scores_train.json')
 for side,scores in (('test',test),('train',train)):
  if REF in scores['_metadata']['failed']: raise ValueError(f'reference failed on {side}: {scores["_metadata"]["failed"][REF]}')
 measured=read('eval/test/measurements.json')
 experiments={}
 for exp,spec in contract['experiments'].items():
  results={REF:dict(type='proposed',**test['experiments'][exp]['results'][REF])}
  notes=('Scaled RCSB corpus, distinct from the paper evaluation splits. Results are the reproduced reference measured by scripts/evaluate_test.sh, not paper targets. '
         'Reference: released GEOBPE at the paper Table 14 main codebook {2:100,3:500,5:20,6:100} reported in Table 16 at |V|=600 (no merged keys), 128 fitting chains, 2,048 clustering occurrences. '
         'Full finite dictionary storage is charged. Failed attempts are scored at the fixed worst values '+json.dumps(contract['worst'])+'. Paper Table 16 values are retained verbatim under _paper_reported.')
  if BASE in test['experiments'][exp]['results']:
   results[BASE]=dict(type='baseline',**test['experiments'][exp]['results'][BASE])
   if BASE in test['_metadata']['failed'] and measured.get(BASE,{}).get('metrics'):
    raw=measured[BASE]['metrics'][exp]
    notes+=(f' The independent fixed-bin baseline fails ({"; ".join(test["_metadata"]["failed"][BASE])}) and is therefore scored at the worst values; '
            f'its measured values here are RMSD {raw["rmsd"]:.3f}, lDDT {raw["lddt"]:.3f}, BPR {raw["bpr"]:.3f}.')
  metrics={m:{'higher_is_better':d['higher_is_better'],'coefficient':d['coefficient'],'description':DESCRIPTIONS[m]} for m,d in spec['metrics'].items()}
  experiments[exp]={'description':f'Compact lossy coding of complete {RANGES[exp]} residue protein backbones on 64 unseen chains.','notes':notes,'weight':spec['weight'],'primary_metric':'lddt','metrics':metrics,'results':results}
 reference={'_paper_reported':history,'experiments':experiments}
 write('scoring/reference.json',reference)
 (ROOT/'eval/test/reference_canonical.json').write_bytes((ROOT/'scoring/reference.json').read_bytes())
 write('scoring/scores.json',train)
 for side in ('train','test'):
  rec=read(f'eval/{side}/measurements.json')[REF]
  write(f'eval/{side}/reference_frozen.json',{'metrics':rec['metrics'],'details':rec['details']})
 print('Packaged reference-run scores:',json.dumps({e:experiments[e]['results'] for e in experiments},indent=1))
if __name__=='__main__': main()
