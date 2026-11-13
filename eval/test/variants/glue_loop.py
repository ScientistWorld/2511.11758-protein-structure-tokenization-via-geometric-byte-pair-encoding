"""Verifier-only probes on the frozen reference tokenizer (not shipped).

Every mode keeps the released dictionary (the reference's 600 learned residue
medoids). The glue modes also keep the reference encoder's own motif stream (nearest
residue medoid, Algorithm 10 step 1, produced by invoking the released encoder as a
subprocess) and change only the boundary glue symbols:

  open     each boundary angle snaps to the bin holding its native value: the paper's
           "GeoBPE without glue optimization" ablation (Appendix A, Fig. 6).
  closed   boundary symbols are chosen sequentially so the placed CA, C and next N
           atoms land nearest the input given the already decoded prefix: an exact,
           discrete form of the paper's drift-correcting glue refinement, at the same
           dictionary, alphabets and rate as the reference.
  compact  closed, with the glue alphabets re-quantized per angle type to 8 (theta),
           4 (omega) and 64 (phi) quantiles of the public fitting chains.

The token modes re-tokenize in closed loop over the same frozen vocabulary: for each
residue the learned medoid and its boundary glue are chosen together so the placed
CA, C and next N atoms land nearest the input given the decoded prefix (only the first
residue keeps the released encoder's medoid). This replaces the paper's open-loop
nearest-medoid assignment plus batch glue refinement by sequential discrete IK.
  tokens          reference glue alphabets: same dictionary, alphabets and rate.
  tokens_compact  compact glue alphabets as above.

Uses only the encoder's supplied input geometry; imports no method or evaluator code.
"""
import argparse,json,math,subprocess,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
COMPACT={'theta':8,'omega':4,'phi':64}

def atomic(path,obj):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_name(path.name+'.partial'); temp.write_text(json.dumps(obj,allow_nan=False)+'\n'); temp.replace(path)

def coordinates(path):
 x=[[float(s[j:j+8]) for j in (30,38,46)] for s in Path(path).read_text().splitlines() if s.startswith('ATOM  ') and s[12:16].strip() in ('N','CA','C')]
 return np.asarray(x,float)

def frame(x,j):
 bc=x[j-1]-x[j-2]; bc=bc/np.linalg.norm(bc)
 n=np.cross(x[j-2]-x[j-3],bc); n=n/np.linalg.norm(n)
 return bc,n,np.cross(n,bc)

def place(x,j,D,A,T):
 bc,n,tg=frame(x,j)
 return x[j-1]+D*(-math.cos(A)*bc+math.sin(A)*(math.cos(T)*tg+math.sin(T)*n))

def native_glue(native):
 """Boundary angles of the input in the decoder's convention, per CA atom index j."""
 def angle(j):
  u=native[j-2]-native[j-1]; v=native[j]-native[j-1]
  return math.acos(max(-1.,min(1.,float(u@v/np.linalg.norm(u)/np.linalg.norm(v)))))
 def torsion(j):
  bc,n,tg=frame(native,j); r=native[j]-native[j-1]
  return math.atan2(float(r@n),float(r@tg))%(2*math.pi)
 return angle,torsion

def expand(ids,motifs):
 """Flattened internals with glue slots left open; returns slot -> CA atom index."""
 d=[]; a=[]; t=[]; cas=[]
 for i,mid in enumerate(ids):
  if i:
   cas.append(len(a)+2); a.append(None); t.extend((None,None))
  md,ma,mt=motifs[mid]; d+=md; a+=ma; t+=mt
 return d,a,t,cas

def seed(d,a):
 x=np.zeros((len(d)+1,3)); x[1,0]=d[0]; x[2]=[d[0]-d[1]*math.cos(a[0]),d[1]*math.sin(a[0]),0]
 return x

def superpose(native,x):
 """Input placed so its first three atoms best overlay the decoder's fixed seed triad."""
 P=native[:3]-native[:3].mean(0); Q=x[:3]-x[:3].mean(0)
 u,_,vh=np.linalg.svd(P.T@Q); C=np.eye(3); C[-1,-1]=np.sign(np.linalg.det(u@vh)) or 1.
 return (native-native[:3].mean(0))@(u@C@vh)+x[:3].mean(0)

def nearest_bin(v,centers):
 return int(np.argmin(np.abs(centers-v)))

def encode_open(native,ids,motifs,G):
 d,a,t,cas=expand(ids,motifs); angle,torsion=native_glue(native); glue=[]
 for j in cas:
  glue.append([nearest_bin(angle(j),G[0]),nearest_bin(torsion(j),G[1]),nearest_bin(torsion(j+1),G[2])])
 return glue

def encode_closed(native,ids,motifs,G,top=8):
 d,a,t,cas=expand(ids,motifs); x=seed(d,a); goal=superpose(native,x)
 TH,OM,PH=G; slots={j:k for k,j in enumerate(cas)}; glue=[None]*len(cas); n=len(x); j=3
 while j<n:
  if j not in slots:
   x[j]=place(x,j,d[j-1],a[j-2],t[j-3]); j+=1; continue
  # CA (theta, omega), then C (phi); look ahead to the motif-fixed next N.
  bc,nn,tg=frame(x,j); r=goal[j]-x[j-1]; D=d[j-1]
  cb=-D*np.cos(TH)[:,None]; sa=D*np.sin(TH)[:,None]
  err=(cb-r@bc)**2+(sa*np.cos(OM)[None,:]-r@tg)**2+(sa*np.sin(OM)[None,:]-r@nn)**2
  k=min(top,err.size); flat=np.argpartition(err.ravel(),k-1)[:k]; best=None
  for f in flat:
   ti,oi=np.unravel_index(int(f),err.shape); y=x[j-3:j].copy()
   ca=y[2]+D*(-math.cos(TH[ti])*bc+math.sin(TH[ti])*(math.cos(OM[oi])*tg+math.sin(OM[oi])*nn))
   cost=float(np.sum((ca-goal[j])**2)); z=np.vstack([y,ca])
   if j+1<n:
    b2,n2,t2=frame(z,4); r2=goal[j+1]-ca; D2=d[j]; A2=a[j-1]
    e2=(-D2*math.cos(A2)-r2@b2)**2+(D2*math.sin(A2)*np.cos(PH)-r2@t2)**2+(D2*math.sin(A2)*np.sin(PH)-r2@n2)**2
    pi=int(np.argmin(e2)); c=place(z,4,D2,A2,PH[pi]); cost+=float(np.sum((c-goal[j+1])**2)); z=np.vstack([z,c])
    if j+2<n:
     nx=place(z,5,d[j+1],a[j],t[j-1]); cost+=float(np.sum((nx-goal[j+2])**2))
   else: pi=0
   if best is None or cost<best[0]: best=(cost,ti,oi,pi)
  _,ti,oi,pi=best; k=slots[j]; glue[k]=[int(ti),int(oi),int(pi)]
  a[j-2]=TH[ti]; t[j-3]=OM[oi]; t[j-2]=PH[pi]
  x[j]=place(x,j,d[j-1],a[j-2],t[j-3])
  if j+1<n: x[j+1]=place(x,j+1,d[j],a[j-1],t[j-2])
  j+=2
 return glue

def encode_tokens(native,first,motifs,G,top=3):
 TH,OM,PH=G; order=np.argsort(PH); PHs=PH[order]; P=len(PH)
 def table(length):
  ids=np.asarray([i for i,m in enumerate(motifs) if len(m[0])==length])
  return ids,np.asarray([motifs[i][0] for i in ids]),np.asarray([motifs[i][1] for i in ids]),np.asarray([(motifs[i][2] or [0.])[0] for i in ids])
 tables={3:table(3),2:table(2)}
 N=len(native)//3; md,ma,mt=motifs[first]
 x=np.zeros((3*N,3)); x[1]=[md[0],0,0]; x[2]=[md[0]-md[1]*math.cos(ma[0]),md[1]*math.sin(ma[0]),0]
 goal=superpose(native,x); x[3]=place(x,3,md[2],ma[1],mt[0]); ids=[first]; glue=[]
 unit=lambda v:v/np.linalg.norm(v,axis=1)[:,None]
 for res in range(1,N):
  last=res==N-1; jN=3*res; jCA=jN+1; jC=jN+2
  mids,B,A,PSI=tables[2 if last else 3]
  bc,nn,tg=frame(x,jCA); r=goal[jCA]-x[jN]; Dn=float(np.median(B[:,0]))
  cb=-Dn*np.cos(TH)[:,None]; sa=Dn*np.sin(TH)[:,None]
  err=(cb-r@bc)**2+(sa*np.cos(OM)[None,:]-r@tg)**2+(sa*np.sin(OM)[None,:]-r@nn)**2
  k=min(top,err.size); best=None
  for f in np.argpartition(err.ravel(),k-1)[:k]:
   ti,oi=np.unravel_index(int(f),err.shape)
   u=-math.cos(TH[ti])*bc+math.sin(TH[ti])*(math.cos(OM[oi])*tg+math.sin(OM[oi])*nn)
   CA=x[jN]+B[:,0,None]*u; tot=((CA-goal[jCA])**2).sum(1)
   b2=unit(CA-x[jN]); n2=unit(np.cross(x[jN]-x[jN-1],b2)); t2=np.cross(n2,b2); r2=goal[jC]-CA
   want=np.arctan2((r2*n2).sum(1),(r2*t2).sum(1))%(2*math.pi)
   pos=np.searchsorted(PHs,want); c=np.stack([(pos-1)%P,pos%P],1)
   gap=np.abs(PHs[c]-want[:,None]); gap=np.minimum(gap,2*math.pi-gap)
   pi=order[c[np.arange(len(c)),np.argmin(gap,1)]]; ph=PH[pi]
   C=CA+B[:,1,None]*(-np.cos(A[:,0])[:,None]*b2+np.sin(A[:,0])[:,None]*(np.cos(ph)[:,None]*t2+np.sin(ph)[:,None]*n2))
   tot+=((C-goal[jC])**2).sum(1)
   if not last:
    b3=unit(C-CA); n3=unit(np.cross(CA-x[jN],b3)); t3=np.cross(n3,b3)
    Nx=C+B[:,2,None]*(-np.cos(A[:,1])[:,None]*b3+np.sin(A[:,1])[:,None]*(np.cos(PSI)[:,None]*t3+np.sin(PSI)[:,None]*n3))
    tot+=((Nx-goal[jC+1])**2).sum(1)
   m=int(np.argmin(tot))
   if best is None or tot[m]<best[0]: best=(float(tot[m]),int(ti),int(oi),m,int(pi[m]))
  _,ti,oi,m,p=best; mid=int(mids[m]); ids.append(mid); glue.append([ti,oi,p]); md,ma,mt=motifs[mid]
  x[jCA]=place(x,jCA,md[0],TH[ti],OM[oi]); x[jC]=place(x,jC,md[1],ma[0],PH[p])
  if not last: x[jC+1]=place(x,jC+1,md[2],ma[1],mt[0])
 return ids,glue

def glue_angles(paths):
 values={'theta':[],'omega':[],'phi':[]}
 for p in paths:
  x=coordinates(p); angle,torsion=native_glue(x)
  for j in range(4,len(x),3):
   values['theta'].append(angle(j)); values['omega'].append(torsion(j))
   if j+1<len(x): values['phi'].append(torsion(j+1))
 return values

def register(a):
 dest=ROOT/'checkpoints/submissions'/a.register; dest.mkdir(parents=True,exist_ok=True)
 base=json.loads(Path(a.base_model).read_text())
 (dest/'base_model.json').write_text(json.dumps(base,allow_nan=False)+'\n')
 model=dict(base)
 if a.mode in ('compact','tokens_compact'):
  values=glue_angles(sorted((ROOT/'data/downloads/pdb/train').glob('*.pdb')))
  model['glue']={k:[float(v) for v in np.quantile(np.asarray(values[k]),(np.arange(COMPACT[k])+.5)/COMPACT[k])] for k in ('theta','omega','phi')}
 (dest/'model.json').write_text(json.dumps(model,allow_nan=False)+'\n')
 rel=lambda p:str(Path(p).resolve().relative_to(ROOT))
 atomic(dest/'manifest.json',{'model':rel(dest/'model.json'),'command':['python','eval/test/variants/glue_loop.py','--mode',a.mode,'--checkpoint',a.checkpoint,'--base-model',rel(dest/'base_model.json'),'--request','{request}','--output','{output}','--model','{model}']})

def main():
 p=argparse.ArgumentParser(); p.add_argument('--mode',choices=('open','closed','compact','tokens','tokens_compact'),required=True)
 p.add_argument('--checkpoint',required=True); p.add_argument('--base-model',required=True)
 p.add_argument('--request'); p.add_argument('--output'); p.add_argument('--model'); p.add_argument('--register'); a=p.parse_args()
 if a.register: register(a); return
 output=Path(a.output); base=output.with_name(output.stem+'.base.json')
 subprocess.run([sys.executable,str(ROOT/'method/encode.py'),'--checkpoint',a.checkpoint,'--request',a.request,'--output',str(base),'--model',a.base_model],cwd=ROOT,check=True)
 # Mirror the decoder exactly: dictionary numbers are rounded to float32 before use.
 model=json.loads(Path(a.model).read_text())
 f32=lambda v:np.asarray(v,dtype=np.float32).astype(float).tolist()
 motifs=[(f32(m['bonds']),f32(m['angles']),f32(m['torsions'])) for m in model['motifs']]
 G=[np.asarray(f32(model['glue'][k])) for k in ('theta','omega','phi')]
 streams={r['id']:r for r in json.loads(base.read_text())}; rows=[]
 for request in json.loads(Path(a.request).read_text()):
  native=coordinates(request['path']); ids=streams[request['id']]['motifs']
  if a.mode.startswith('tokens'): ids,glue=encode_tokens(native,ids[0],motifs,G)
  else: glue=encode_open(native,ids,motifs,G) if a.mode=='open' else encode_closed(native,ids,motifs,G)
  rows.append({'id':request['id'],'motifs':ids,'glue':glue})
 atomic(output,rows)
if __name__=='__main__': main()
