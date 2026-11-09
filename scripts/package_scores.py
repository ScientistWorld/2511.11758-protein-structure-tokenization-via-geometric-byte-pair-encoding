"""Publish reference-only aggregate scores; retain historical paper numbers verbatim."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text())
def write(p,obj): (ROOT/p).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def main():
 old=read('scoring/reference.json')
 history=old.get('_paper_reported',old.get('experiments'))
 slices={s:read(f'eval/{s}/ranking.json') for s in ('train','test')}
 for side,record in slices.items():
  r=record['methods']['geobpe_reference']
  if r['failed']: raise ValueError('reference failed on '+side)
  scores={'_metadata':{'slice':side,'source':'evaluator-decoded raw streams; reference method only','reference':'GEOBPE Table 14 pipeline, Table 16 small codebook, 128 fitting chains, 50 merges, 512 clustering occurrences; no matching to paper numbers'},'experiments':{exp:{'results':{'geobpe_reference':row}} for exp,row in r['metrics'].items()}}
  write(f'scoring/scores_{side}.json',scores)
  if side=='train': write('scoring/scores.json',scores)
 test=slices['test']['methods']; experiments={}
 for exp,row in test['geobpe_reference']['metrics'].items():
  definitions={
   'rmsd':{'higher_is_better':False,'coefficient':-.6,'description':'Mean complete-backbone RMSD in angstroms after proper Kabsch alignment.'},
   'lddt':{'higher_is_better':True,'coefficient':1.,'description':'Mean per-residue CA lDDT, 15 angstrom inclusion radius and tolerances 0.5, 1, 2, 4 angstroms.'},
   'bpr':{'higher_is_better':False,'coefficient':-.4,'description':'Full dictionary plus encoded streams, in bits per native residue.'},
   'vocab_size':{'higher_is_better':False,'coefficient':-.02,'description':'Total dictionary and boundary alphabet size, also limited to 8192.'}}
  results={'geobpe_reference':dict(type='proposed',**row)}
  if 'metrics' in test.get('internal_baseline',{}): results['internal_baseline']=dict(type='baseline',**test['internal_baseline']['metrics'][exp])
  experiments[exp]={'description':'Compact lossy coding of complete '+('64–192' if exp.startswith('short') else '256–512')+' residue protein backbones on 64 unseen chains.','notes':'Scaled RCSB corpus, distinct from the paper evaluation splits. Results here are measured reference values, not paper targets. Full finite dictionary storage is charged. Paper Table 16 values are retained verbatim under _paper_reported.','weight':.5,'primary_metric':'lddt','metrics':definitions,'results':results}
 write('scoring/reference.json',{'_paper_reported':history,'experiments':experiments})
 # Report every measured variant/attack only in the audit, not reference score files.
 lines=['\n## Final combined job results\n','These ranks use the final cohort standard deviations; failed attempts receive −10¹⁰⁰ and cannot outrank a feasible run. Reference rank is zero by definition. Intervals are paired 1,000-replicate bootstrap intervals over the same private chains.\n','| Attempt | Failed | Rank | Paired 95% interval |','|---|---|---:|---|']
 for name,r in test.items():
  ci=r.get('paired_rank_95ci'); lines.append(f"| {name} | {r['failed']} | {r['rank']:.6g} | {'' if ci is None else str([round(v,6) for v in ci])} |")
 lines+=['\n| Attempt / experiment | RMSD ↓ | lDDT ↑ | Full BPR ↓ | Vocabulary ↓ |','|---|---:|---:|---:|---:|']
 for name,r in test.items():
  for exp,v in r.get('metrics',{}).items(): lines.append(f"| {name} / {exp} | {v['rmsd']:.6f} | {v['lddt']:.6f} | {v['bpr']:.6f} | {v['vocab_size']:.0f} |")
 lines+=['\nFailed attempts and reasons:\n']
 for name,r in test.items():
  if r['failed']: lines.append(f"- `{name}`: {'; '.join(r.get('reasons',[]))}")
 better=test.get('higher_capacity',{}); weaker=test.get('lower_capacity',{}); nobpe=test.get('no_bpe',{})
 # State evidence rather than automatically declaring all requested conditions met.
 bounds={'rmsd':0.,'lddt':1.,'bpr':0.,'vocab_size':1.}
 at_bound=[f'{exp}/{metric}' for exp,row in test['geobpe_reference']['metrics'].items() for metric,value in row.items() if abs(value-bounds[metric])<1e-12]
 lines+=['\nReference metrics at their best bound: '+(', '.join(at_bound) if at_bound else 'none.')+' Long backbones are the added scored experiment; their weight is 0.5.', '\nHeadroom evidence: the stronger variant '+('has a strictly positive paired lower confidence limit.' if not better.get('failed',True) and better.get('paired_rank_95ci',[0])[0]>0 else 'did NOT establish a strictly positive paired lower confidence limit. This requirement remains unmet.'),'The weaker variant '+('fails the task constraints.' if weaker.get('failed') else f"has rank {weaker.get('rank',0):.6f}."),'The no-merge ablation '+('fails constraints.' if nobpe.get('failed') else f"has rank {nobpe.get('rank',0):.6f}; indistinguishable geometry is a scientific headroom limitation, not a forged-output loophole.")]
 p=ROOT/'HARDENING.md'; text=p.read_text().split('\n## Final combined job results')[0]; p.write_text(text+'\n'+'\n'.join(lines)+'\n')
 write('scoring/hardening_summary.json',{'higher_capacity_beats_reference':not better.get('failed',True) and better.get('paired_rank_95ci',[0])[0]>0,'weaker_below_reference':weaker.get('failed',False) or weaker.get('rank',0)<0,'reference_at_metric_bound':at_bound})
if __name__=='__main__': main()
