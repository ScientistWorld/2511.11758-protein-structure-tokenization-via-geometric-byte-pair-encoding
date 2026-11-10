"""Verifier-only headroom probe: closed-loop internal-coordinate coding.

Not a shipped baseline. Nine small alphabets are fitted on the public fitting
chains only (bond lengths: one value each; bond angles: eight quantile values;
omega: four quantile values; psi and phi: 64 uniform values), i.e. 26 bits per
residue before headers. At inference each atom's (bond, angle, torsion) symbols
are chosen sequentially so the decoded atom lands nearest the supplied input atom
given the already-decoded prefix, which prevents drift from accumulating. The
decoded geometry uses exactly the evaluator's float32 alphabets and NeRF
convention. Uses only the supplied input geometry; imports no method/evaluator code.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
SIZES=[1,1,1,8,8,8,64,4,64]
UNIFORM={6,8}

def coordinates(path):
 x=[[float(s[i:i+8]) for i in (30,38,46)] for s in Path(path).read_text().splitlines() if s.startswith('ATOM  ') and s[12:16].strip() in ('N','CA','C')]
 return np.asarray(x,float)

def geometry(x):
 b=x[1:]-x[:-1]; d=np.linalg.norm(b,axis=1); u=b/d[:,None]
 a=np.arccos(np.clip(-(u[:-1]*u[1:]).sum(1),-1,1))
 n=np.cross(u[:-1],u[1:]); n/=np.linalg.norm(n,axis=1)[:,None]
 t=np.arctan2((np.cross(n[:-1],n[1:])*u[1:-1]).sum(1),(n[:-1]*n[1:]).sum(1))%(2*np.pi)
 return d,a,t

def fit(name):
 values=[[] for _ in range(9)]
 for p in sorted((ROOT/'data/downloads/pdb/train').glob('*.pdb')):
  for g,arr in enumerate(geometry(coordinates(p))):
   for j in range(3): values[g*3+j].extend(arr[j::3].tolist())
 bins=[]
 for j,arr in enumerate(values):
  n=SIZES[j]
  centers=(np.arange(n)+.5)*2*np.pi/n if j in UNIFORM else np.quantile(np.asarray(arr),(np.arange(n)+.5)/n)
  bins.append([float(v) for v in centers])
 dest=ROOT/'checkpoints/submissions'/name; dest.mkdir(parents=True,exist_ok=True)
 (dest/'model.json').write_text(json.dumps({'codec':'internal','bins':bins})+'\n')
 (dest/'manifest.json').write_text(json.dumps({'model':str((dest/'model.json').relative_to(ROOT)),'command':['python','eval/test/variants/closed_loop.py','--request','{request}','--output','{output}','--model','{model}']},indent=2)+'\n')

def encode(native,B):
 d,a,_=geometry(native); n_atoms=len(native)
 di=[int(np.argmin(np.abs(B[0]-d[0]))),int(np.argmin(np.abs(B[1]-d[1])))]; ai=[int(np.argmin(np.abs(B[3]-a[0])))]; ti=[]
 x=np.zeros((n_atoms,3)); D0=B[0][di[0]]; D1=B[1][di[1]]; A0=B[3][ai[0]]
 x[1]=[D0,0,0]; x[2]=[D0-D1*math.cos(A0),D1*math.sin(A0),0]
 # Superpose the input's first three atoms on the decoder's canonical frame.
 P=native[:3]-native[:3].mean(0); Q=x[:3]-x[:3].mean(0)
 u,_,vh=np.linalg.svd(P.T@Q); C=np.eye(3); C[-1,-1]=np.sign(np.linalg.det(u@vh)) or 1.
 goal=(native-native[:3].mean(0))@(u@C@vh)+x[:3].mean(0)
 for j in range(3,n_atoms):
  bD=B[(j-1)%3]; bA=B[3+(j-2)%3]; bT=B[6+(j-3)%3]
  bc=x[j-1]-x[j-2]; bc/=np.linalg.norm(bc)
  normal=np.cross(x[j-2]-x[j-3],bc); normal/=np.linalg.norm(normal); tangent=np.cross(normal,bc)
  r=goal[j]-x[j-1]; rb,rt,rn=r@bc,r@tangent,r@normal
  dd=bD[:,None,None]; aa=bA[None,:,None]; tt=bT[None,None,:]
  cb=np.broadcast_to(-dd*np.cos(aa),(len(bD),len(bA),len(bT)))
  ct=dd*np.sin(aa)*np.cos(tt); cn=dd*np.sin(aa)*np.sin(tt)
  k=np.unravel_index(int(np.argmin((cb-rb)**2+(ct-rt)**2+(cn-rn)**2)),cb.shape)
  di.append(int(k[0])); ai.append(int(k[1])); ti.append(int(k[2]))
  D,A,T=bD[k[0]],bA[k[1]],bT[k[2]]
  x[j]=x[j-1]+D*(-math.cos(A)*bc+math.sin(A)*(math.cos(T)*tangent+math.sin(T)*normal))
 return [di,ai,ti]

def main():
 p=argparse.ArgumentParser(); p.add_argument('--fit',action='store_true'); p.add_argument('--name',default='closed_loop_internal')
 p.add_argument('--request'); p.add_argument('--output'); p.add_argument('--model'); a=p.parse_args()
 if a.fit: fit(a.name); return
 model=json.loads(Path(a.model).read_text())
 # Mirror the decoder exactly: alphabets are rounded to float32 before use.
 B=[np.asarray(v,dtype=np.float32).astype(float) for v in model['bins']]
 rows=[{'id':r['id'],'indices':encode(coordinates(r['path']),B)} for r in json.loads(Path(a.request).read_text())]
 Path(a.output).write_text(json.dumps(rows)+'\n')
if __name__=='__main__': main()
