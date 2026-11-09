"""Independent fixed-bin internal-coordinate coding baseline."""
import argparse,json,math
from pathlib import Path
import numpy as np

def coordinates(path):
 return np.array([[float(s[i:i+8]) for i in (30,38,46)] for s in Path(path).read_text().splitlines() if s.startswith('ATOM  ') and s[12:16].strip() in ('N','CA','C')])
def geometry(x):
 b=x[1:]-x[:-1]; d=np.linalg.norm(b,axis=1); u=b/d[:,None]
 a=np.arccos(np.clip(-(u[:-1]*u[1:]).sum(1),-1,1))
 n=np.cross(u[:-1],u[1:]); n/=np.linalg.norm(n,axis=1)[:,None]
 t=np.arctan2((np.cross(n[:-1],n[1:])*u[1:-1]).sum(1),(n[:-1]*n[1:]).sum(1))%(2*np.pi)
 return d,a,t

def fit():
 values=[[] for _ in range(9)]
 for p in sorted(Path('data/downloads/pdb/train').glob('*.pdb')):
  for g,arr in enumerate(geometry(coordinates(p))):
   for j in range(3): values[g*3+j].extend(arr[j::3].tolist())
 bins=[]
 for j,arr in enumerate(values):
  lo,hi=(min(arr),max(arr)) if j<3 else (0.,2*np.pi)
  bins.append((np.linspace(lo,hi,33)[:-1]+(hi-lo)/64).tolist())
 dest=Path('checkpoints/submissions/internal_baseline'); dest.mkdir(parents=True,exist_ok=True)
 (dest/'model.json').write_text(json.dumps({'codec':'internal','bins':bins})+'\n')
 (dest/'manifest.json').write_text(json.dumps({'model':str(dest/'model.json'),'command':['python','baseline/internal.py','--request','{request}','--output','{output}','--model','{model}']},indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--fit',action='store_true'); p.add_argument('--request'); p.add_argument('--output'); p.add_argument('--model'); a=p.parse_args()
 if a.fit: fit(); return
 model=json.loads(Path(a.model).read_text()); bins=[np.array(v) for v in model['bins']]; rows=[]
 for r in json.loads(Path(a.request).read_text()):
  groups=[]
  for g,arr in enumerate(geometry(coordinates(r['path']))):
   seq=[]
   for j,v in enumerate(arr):
    centers=bins[g*3+j%3]; delta=np.abs(centers-v)
    if g: delta=np.minimum(delta,2*np.pi-delta)
    seq.append(int(np.argmin(delta)))
   groups.append(seq)
  rows.append({'id':r['id'],'indices':groups})
 Path(a.output).write_text(json.dumps(rows)+'\n')
if __name__=='__main__': main()
