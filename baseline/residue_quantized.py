"""Former supplied baseline, with its full continuous output now transmitted.

Sixteen residue prototypes in exact native residue frames. This intentionally
retains the old favorable geometry; the evaluator charges all transmitted floats.
"""
import argparse,json
from pathlib import Path
import numpy as np
from internal import coordinates

def frame(x):
 n,ca,c=x; u=c-ca; u/=np.linalg.norm(u); v=n-ca; v-=np.dot(v,u)*u; v/=np.linalg.norm(v); w=np.cross(u,v)
 return np.stack((u,v,w),axis=1),ca

def fit():
 residues=[]
 for p in sorted(Path('data/downloads/pdb/train').glob('*.pdb')):
  residues.extend(coordinates(p).reshape(-1,3,3))
 rng=np.random.default_rng(0); candidates=[residues[i] for i in rng.choice(len(residues),512,replace=False)]
 local=[]
 for x in candidates:
  r,t=frame(x); local.append((x-t)@r)
 local=np.asarray(local); delta=local[:,None]-local[None,:]; distances=np.sqrt((delta**2).sum((2,3))/3)
 medoids=rng.choice(512,16,replace=False)
 for _ in range(8):
  labels=np.argmin(distances[:,medoids],axis=1); new=[]
  for k,m in enumerate(medoids):
   members=np.where(labels==k)[0]; new.append(int(members[np.argmin(distances[np.ix_(members,members)].sum(1))]) if len(members) else int(m))
  if np.array_equal(new,medoids): break
  medoids=np.array(new)
 dest=Path('checkpoints/submissions/supplied_baseline'); dest.mkdir(parents=True,exist_ok=True)
 (dest/'prototypes.json').write_text(json.dumps(local[medoids].tolist())+'\n')
 (dest/'model.json').write_text(json.dumps({'codec':'cartesian'})+'\n')
 (dest/'manifest.json').write_text(json.dumps({'model':str(dest/'model.json'),'command':['python','baseline/residue_quantized.py','--prototypes',str(dest/'prototypes.json'),'--request','{request}','--output','{output}']},indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--fit',action='store_true'); p.add_argument('--prototypes'); p.add_argument('--request'); p.add_argument('--output'); a=p.parse_args()
 if a.fit: fit(); return
 protos=np.array(json.loads(Path(a.prototypes).read_text())); rows=[]
 for item in json.loads(Path(a.request).read_text()):
  pred=[]
  for residue in coordinates(item['path']).reshape(-1,3,3):
   r,t=frame(residue); local=(residue-t)@r; k=np.argmin(((protos-local)**2).sum((1,2)))
   pred.extend(protos[k]@r.T+t)
  rows.append({'id':item['id'],'coordinates':np.asarray(pred).tolist()})
 Path(a.output).write_text(json.dumps(rows)+'\n')
if __name__=='__main__': main()
