"""Replay the major reported attacks on the final hidden interface, in the job.

Answers and attack outputs stay inside this directory. Never import method code.
"""
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--attack',required=True); p.add_argument('--request',required=True); p.add_argument('--output',required=True); p.add_argument('--model',required=True); a=p.parse_args()
 requests=json.loads(Path(a.request).read_text()); out=[]
 # Available only to the verifier's replay, never future submitted methods.
 reference=json.loads((Path(a.output).parents[1]/'geobpe_reference'/'outputs.json').read_text())
 by_id={r['id']:r for r in reference}
 for request in requests:
  row=dict(by_id[request['id']]); attack=a.attack
  if attack=='forged_target': row['original_coords']=[[0,0,0]]*6
  elif attack=='forged_counts': row.update(tokens=0,vocab_size=1,residues=1000000000)
  elif attack=='quality_fields': row.update(rmsd=0.,lddt=1.)
  elif attack=='negative_counts': row['motifs']=[-1000000]
  elif attack in ('truncated','constant_template'):
   coords=[[float(s[i:i+8]) for i in (30,38,46)] for s in Path(request['path']).read_text().splitlines() if s.startswith('ATOM  ')]
   row={'id':request['id'],'coordinates':coords[:6] if attack=='truncated' else [[0.,0.,0.]]*6}
  elif attack=='public_dictionary': row={'id':request['id'],'motifs':[0],'glue':[]}
  elif attack=='prune_comparison': pass
  else: raise ValueError(attack)
  out.append(row)
 Path(a.output).write_text(json.dumps(out)+'\n')
if __name__=='__main__': main()
