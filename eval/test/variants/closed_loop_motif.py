"""Verifier-only probe: the closed-loop short codec expressed in the motif format.

Tests whether removing the internal-coordinate format would close the short-codec
gap. The dictionary is hand-designed, not learned: one residue motif per (bond angle
N-CA-C quantile, psi grid value) with median bond lengths and median C-N-CA angle
(4 x 64 interior + 4 terminal motifs); boundary alphabets hold 8 C-N-CA quantiles,
4 omega quantiles and a 64-value phi grid, all fitted on the public fitting chains.
At inference every symbol is chosen sequentially so each decoded atom lands nearest
the input atom given the already decoded prefix. Uses only the supplied input
geometry; imports no method or evaluator code.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
NA,NP,NT,NO,NF=4,64,8,4,64

def coordinates(path):
 x=[[float(s[j:j+8]) for j in (30,38,46)] for s in Path(path).read_text().splitlines() if s.startswith('ATOM  ') and s[12:16].strip() in ('N','CA','C')]
 return np.asarray(x,float)

def frame(x,j):
 bc=x[j-1]-x[j-2]; bc=bc/np.linalg.norm(bc)
 n=np.cross(x[j-2]-x[j-3],bc); n=n/np.linalg.norm(n)
 return bc,n,np.cross(n,bc)

def internals(x):
 """Bond lengths, bond angles and torsions in the decoder's NeRF convention."""
 d=np.linalg.norm(x[1:]-x[:-1],axis=1)
 u=x[:-2]-x[1:-1]; v=x[2:]-x[1:-1]
 a=np.arccos(np.clip((u*v).sum(1)/np.linalg.norm(u,axis=1)/np.linalg.norm(v,axis=1),-1,1))
 t=[]
 for j in range(3,len(x)):
  bc,n,tg=frame(x,j); r=x[j]-x[j-1]; t.append(math.atan2(float(r@n),float(r@tg))%(2*math.pi))
 return d,a,np.asarray(t)

def fit(name):
 d,a,t=[],[],[]
 for p in sorted((ROOT/'data/downloads/pdb/train').glob('*.pdb')):
  dd,aa,tt=internals(coordinates(p)); d.append(dd); a.append(aa); t.append(tt)
 bond=[float(np.median(np.concatenate([v[k::3] for v in d]))) for k in range(3)]       # N-CA, CA-C, C-N
 ang=[np.concatenate([v[k::3] for v in a]) for k in range(3)]                            # N-CA-C, CA-C-N, C-N-CA
 tor=[np.concatenate([v[k::3] for v in t]) for k in range(3)]                            # psi, omega, phi
 q=lambda v,n:[float(c) for c in np.quantile(v,(np.arange(n)+.5)/n)]
 grid=lambda n:[float(c) for c in (np.arange(n)+.5)*2*math.pi/n]
 ncac=q(ang[0],NA); cacn=float(np.median(ang[1])); psi=grid(NP)
 motifs=[{'bonds':bond,'angles':[ncac[k],cacn],'torsions':[psi[p]]} for k in range(NA) for p in range(NP)]
 motifs+=[{'bonds':bond[:2],'angles':[ncac[k]],'torsions':[]} for k in range(NA)]
 model={'codec':'motif','motifs':motifs,'glue':{'theta':q(ang[2],NT),'omega':q(tor[1],NO),'phi':grid(NF)}}
 dest=ROOT/'checkpoints/submissions'/name; dest.mkdir(parents=True,exist_ok=True)
 (dest/'model.json').write_text(json.dumps(model)+'\n')
 (dest/'manifest.json').write_text(json.dumps({'model':str((dest/'model.json').relative_to(ROOT)),'command':['python','eval/test/variants/closed_loop_motif.py','--request','{request}','--output','{output}','--model','{model}']},indent=2)+'\n')

def best(x,j,goal,D,A,T):
 """Index pair over (angle, torsion) alphabets placing atom j nearest its goal."""
 bc,n,tg=frame(x,j); r=goal[j]-x[j-1]
 A=np.asarray(A)[:,None]; T=np.asarray(T)[None,:]
 err=(-D*np.cos(A)-r@bc)**2+(D*np.sin(A)*np.cos(T)-r@tg)**2+(D*np.sin(A)*np.sin(T)-r@n)**2
 k,p=np.unravel_index(int(np.argmin(err)),err.shape)
 a,t=float(A[k,0]),float(T[0,p])
 return int(k),int(p),x[j-1]+D*(-math.cos(a)*bc+math.sin(a)*(math.cos(t)*tg+math.sin(t)*n))

def encode(native,model):
 f32=lambda v:np.asarray(v,dtype=np.float32).astype(float)
 M=model['motifs']; DNCA,DCAC,DCN=f32(M[0]['bonds']); CACN=float(f32(M[0]['angles'])[1])
 NCAC=f32([M[k*NP]['angles'][0] for k in range(NA)]); PSI=f32([M[p]['torsions'][0] for p in range(NP)])
 TH,OM,PH=(f32(model['glue'][k]) for k in ('theta','omega','phi'))
 N=len(native)//3; x=np.zeros((3*N,3)); x[1]=[DNCA,0,0]
 u=native[0]-native[1]; v=native[2]-native[1]
 k0=int(np.argmin(np.abs(NCAC-math.acos(float(u@v/np.linalg.norm(u)/np.linalg.norm(v))))))
 x[2]=[DNCA-DCAC*math.cos(NCAC[k0]),DCAC*math.sin(NCAC[k0]),0]
 P=native[:3]-native[:3].mean(0); Q=x[:3]-x[:3].mean(0)
 U,_,V=np.linalg.svd(P.T@Q); C=np.eye(3); C[-1,-1]=np.sign(np.linalg.det(U@V)) or 1.
 goal=(native-native[:3].mean(0))@(U@C@V)+x[:3].mean(0)
 ncac=[k0]; psi=[]; glue=[]
 for i in range(N-1):
  j=3*i+3; _,p,x[j]=best(x,j,goal,DCN,[CACN],PSI); psi.append(p)                  # N(i+1): motif psi
  j+=1; ti,oi,x[j]=best(x,j,goal,DNCA,TH,OM)                                       # CA(i+1): theta, omega
  j+=1; k,fi,x[j]=best(x,j,goal,DCAC,NCAC,PH); ncac.append(k); glue.append([ti,oi,fi])  # C(i+1): N-CA-C, phi
 ids=[ncac[i]*NP+psi[i] for i in range(N-1)]+[NA*NP+ncac[-1]]
 return {'motifs':ids,'glue':glue}

def main():
 p=argparse.ArgumentParser(); p.add_argument('--fit',action='store_true'); p.add_argument('--name',default='closed_loop_motif')
 p.add_argument('--request'); p.add_argument('--output'); p.add_argument('--model'); a=p.parse_args()
 if a.fit: fit(a.name); return
 model=json.loads(Path(a.model).read_text())
 rows=[{'id':r['id'],**encode(coordinates(r['path']),model)} for r in json.loads(Path(a.request).read_text())]
 Path(a.output).write_text(json.dumps(rows)+'\n')
if __name__=='__main__': main()
