"""Honest headroom control: discrete boundary-coordinate descent at fixed rate.

The released model and its assignments remain frozen. Unlike the reference's
SE(3) boundary-frame loss, this variant chooses existing boundary symbols using
full-chain aligned Cartesian error, accepting only results that also preserve
local-distance fidelity. It uses only the encoder's supplied input geometry.
"""
import argparse,copy,hashlib,json,math,subprocess,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def atomic(path,obj):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.partial'); temp.write_text(json.dumps(obj,allow_nan=False)+'\n'); temp.replace(path)

def coordinates(path):
 return np.asarray([[float(s[j:j+8]) for j in (30,38,46)] for s in Path(path).read_text().splitlines() if s.startswith('ATOM  ')],float)

def nerf(d,a,t):
 x=np.zeros((len(d)+1,3)); x[1,0]=d[0]; x[2]=[d[0]-d[1]*math.cos(a[0]),d[1]*math.sin(a[0]),0]
 for j in range(3,len(x)):
  bc=x[j-1]-x[j-2]; bc/=np.linalg.norm(bc)
  normal=np.cross(x[j-2]-x[j-3],bc); normal/=np.linalg.norm(normal); tangent=np.cross(normal,bc)
  x[j]=x[j-1]+d[j-1]*(-math.cos(a[j-2])*bc+math.sin(a[j-2])*(math.cos(t[j-3])*tangent+math.sin(t[j-3])*normal))
 return x

def expand(row,model):
 d=[]; a=[]; t=[]; boundaries=[]
 for i,mid in enumerate(row['motifs']):
  if i:
   boundaries.append(len(d)); theta,omega,phi=[model['glue'][k][v] for k,v in zip(('theta','omega','phi'),row['glue'][i-1])]
   a.append(theta); t.extend((omega,phi))
  motif=model['motifs'][mid]; d+=motif['bonds']; a+=motif['angles']; t+=motif['torsions']
 return d,a,t,boundaries

def align(native,x):
 q=native-native.mean(0); p=x-x.mean(0)
 u,_,vh=np.linalg.svd(q.T@p); correction=np.eye(3); correction[-1,-1]=np.linalg.det(u@vh)
 return q@u@correction@vh+x.mean(0)

def quality(native,x):
 rmsd=float(np.sqrt(np.mean(np.sum((align(native,x)-x)**2,axis=1))))
 ca=native[1::3]; cb=x[1::3]; dist=np.linalg.norm(ca[:,None]-ca[None,:],axis=-1)
 pred=np.linalg.norm(cb[:,None]-cb[None,:],axis=-1); mask=(dist<15)&(~np.eye(len(ca),dtype=bool)); count=mask.sum(1)
 local=sum((np.abs(dist-pred)<cut)*mask for cut in (.5,1.,2.,4.))/4; valid=count>0
 return rmsd,float((local.sum(1)[valid]/count[valid]).mean())

def rotation_geometry(x,b,channel):
 if channel==0:
  axis=np.cross(x[b]-x[b-1],x[b+1]-x[b]); pivot=x[b]; start=b+1; sign=-1
 elif channel==1:
  axis=x[b]-x[b-1]; pivot=x[b]; start=b+1; sign=1
 else:
  axis=x[b+1]-x[b]; pivot=x[b+1]; start=b+2; sign=1
 return start,pivot,axis/np.linalg.norm(axis),sign

def rotated_tail(x,b,channel,delta):
 start,pivot,axis,sign=rotation_geometry(x,b,channel)
 v=x[start:]-pivot; parallel=np.outer(v@axis,axis); perpendicular=v-parallel
 return start,pivot+parallel+perpendicular*math.cos(sign*delta)+np.cross(axis,perpendicular)*math.sin(sign*delta)

def refine(native,row,model,sweeps=12):
 original=copy.deepcopy(row); row=copy.deepcopy(row)
 d,a,t,boundaries=expand(row,model); x=nerf(d,a,t)
 initial=quality(native,x); best=initial; best_row=copy.deepcopy(row)
 alphabets=[np.asarray(model['glue'][k]) for k in ('theta','omega','phi')]
 for sweep in range(sweeps):
  aligned=align(native,x); changes=0
  order=range(len(boundaries)) if sweep%2==0 else reversed(range(len(boundaries)))
  for i in order:
   b=boundaries[i]
   for channel,centers in enumerate(alphabets):
    current=row['glue'][i][channel]; old=centers[current]
    start,pivot,axis,sign=rotation_geometry(x,b,channel)
    v=x[start:]-pivot; parallel=np.outer(v@axis,axis); perpendicular=v-parallel; cross=np.cross(axis,perpendicular)
    y=aligned[start:]-pivot-parallel
    aa=float(np.sum(perpendicular*y)); bb=float(np.sum(cross*y))
    delta=centers-old; phases=sign*delta
    objective=aa*np.cos(phases)+bb*np.sin(phases)
    # Local physical refinement; preserve the frozen finite alphabet and cost.
    wrapped=(delta+np.pi)%(2*np.pi)-np.pi
    objective[np.abs(wrapped)>(.2 if channel==0 else .3)]=-np.inf
    chosen=int(np.argmax(objective))
    if chosen!=current and objective[chosen]>objective[current]+1e-10:
     angle=float(phases[chosen]); x[start:]=pivot+parallel+perpendicular*math.cos(angle)+cross*math.sin(angle)
     row['glue'][i][channel]=chosen; changes+=1
  # Reconstruct from the actual emitted symbols, not accumulated rotations.
  d,a,t,_=expand(row,model); x=nerf(d,a,t); candidate=quality(native,x)
  if candidate[0]<best[0]-1e-9 and candidate[1]>=initial[1]-1e-12:
   best=candidate; best_row=copy.deepcopy(row)
  if not changes: break
 # Every accepted result has equal storage and non-worse values in both metrics.
 assert best[0]<=initial[0]+1e-9 and best[1]>=initial[1]-1e-12
 return best_row,initial,best

def main():
 p=argparse.ArgumentParser(); p.add_argument('--checkpoint',required=True); p.add_argument('--model',required=True)
 p.add_argument('--request'); p.add_argument('--output'); p.add_argument('--register'); a=p.parse_args()
 if a.register:
  dest=ROOT/'checkpoints/submissions'/a.register; dest.mkdir(parents=True,exist_ok=True)
  (dest/'model.json').write_bytes(Path(a.model).read_bytes())
  atomic(dest/'manifest.json',{'model':str((dest/'model.json').relative_to(ROOT)),'command':['python','method/refine.py','--checkpoint',a.checkpoint,'--request','{request}','--output','{output}','--model','{model}']}); return
 output=Path(a.output); base=output.with_suffix('.base.json')
 subprocess.run([sys.executable,str(ROOT/'method/encode.py'),'--checkpoint',a.checkpoint,'--request',a.request,'--output',str(base),'--model',a.model],cwd=ROOT,check=True)
 model=json.loads(Path(a.model).read_text(),parse_float=lambda x:float(np.float32(x)))
 inputs=json.loads(Path(a.request).read_text()); originals={r['id']:r for r in json.loads(base.read_text())}
 identity=hashlib.sha256(Path(__file__).read_bytes()+Path(a.model).read_bytes()+base.read_bytes()).hexdigest()
 hashes={r['id']:hashlib.sha256(Path(r['path']).read_bytes()).hexdigest() for r in inputs}
 meta=output.with_suffix('.refinement.json'); cached={}
 if meta.exists():
  state=json.loads(meta.read_text())
  if state['fingerprint']==identity:
   cached={r['id']:r for r in state['outputs'] if state['inputs'].get(r['id'])==hashes.get(r['id'])}
 for request in inputs:
  rid=request['id']
  if rid in cached: continue
  result,before,after=refine(coordinates(request['path']),originals[rid],model)
  cached[rid]=result; rows=[cached[r['id']] for r in inputs if r['id'] in cached]
  atomic(meta,{'fingerprint':identity,'inputs':hashes,'outputs':rows}); atomic(output,rows)
  print('refined',rid,'RMSD/lDDT',before,'->',after,flush=True)
 atomic(output,[cached[r['id']] for r in inputs])
if __name__=='__main__': main()
