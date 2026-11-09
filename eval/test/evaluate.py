"""Private, method-independent decoder, measurement, failure gates and cohort ranking.

All submitted values are representation symbols, never scores or targets.
Method, data and public evaluation implementations are not imported. Evaluation never trains a submitted method.
"""
from __future__ import annotations
import hashlib,json,math,os,subprocess,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EXPERIMENTS={'short_backbones':('short',64),'long_backbones':('long',64)}
METRICS={'rmsd':(False,.6),'lddt':(True,1.),'bpr':(False,.4),'vocab_size':(False,.02)}
WEIGHTS={'short_backbones':.5,'long_backbones':.5}
# Fixed task feasibility constraints, chosen before the final runs.
LIMITS={'rmsd':15.,'lddt':.35,'bpr':96.,'vocab_size':8192}

def read_json(path):
 return json.loads(Path(path).read_text(),parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
def write_json(path,obj):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def exact_keys(obj,keys):
 if not isinstance(obj,dict) or set(obj)!=set(keys): raise ValueError('representation fields do not match codec')
def floats(values):
 a=np.asarray(values,dtype=np.float32)
 if a.ndim!=1 or not np.isfinite(a).all(): raise ValueError('invalid dictionary numbers')
 return a.astype(float).tolist()
def width(n):
 if not 1<=n<=1000000: raise ValueError('invalid alphabet size')
 return max(1,math.ceil(math.log2(n)))
def index(v,n):
 if type(v)!=int or not 0<=v<n: raise ValueError('invalid symbol')
 return v

def load_model(obj):
 """Frozen decoder model. Charge float32 values, array sizes and dictionary headers."""
 codec=obj.get('codec'); model_bits=128
 if codec=='motif':
  exact_keys(obj,['codec','motifs','glue'])
  if not 1<=len(obj['motifs'])<=8192: raise ValueError('invalid dictionary size')
  motifs=[]
  for row in obj['motifs']:
   exact_keys(row,['bonds','angles','torsions']); d,a,t=[floats(row[k]) for k in ('bonds','angles','torsions')]
   if len(d)<2 or len(a)!=len(d)-1 or len(t)!=len(d)-2 or len(d)>1535: raise ValueError('invalid motif dimensions')
   if not all(0.5<x<3 for x in d): raise ValueError('invalid bond length')
   motifs.append((d,a,t)); model_bits+=96+32*(len(d)+len(a)+len(t))
  exact_keys(obj['glue'],['theta','omega','phi'])
  glue={k:floats(v) for k,v in obj['glue'].items()}
  if any(not 1<=len(v)<=4096 for v in glue.values()): raise ValueError('invalid boundary alphabet')
  model_bits+=sum(32+32*len(v) for v in glue.values())
  return {'codec':codec,'motifs':motifs,'glue':glue},model_bits,len(motifs)+sum(map(len,glue.values()))
 if codec=='internal':
  exact_keys(obj,['codec','bins']); bins=[floats(v) for v in obj['bins']]
  if len(bins)!=9 or any(not 1<=len(v)<=4096 for v in bins): raise ValueError('invalid internal-coordinate alphabets')
  return {'codec':codec,'bins':bins},model_bits+sum(32+32*len(v) for v in bins),sum(map(len,bins))
 if codec=='cartesian':
  exact_keys(obj,['codec']); return obj,model_bits,1
 raise ValueError('unsupported codec')

def nerf(d,a,t):
 if len(d)<2 or len(a)!=len(d)-1 or len(t)!=len(d)-2: raise ValueError('invalid chain dimensions')
 x=np.zeros((len(d)+1,3),float); x[1,0]=d[0]; x[2]=[d[0]-d[1]*math.cos(a[0]),d[1]*math.sin(a[0]),0]
 for j in range(3,len(x)):
  bc=x[j-1]-x[j-2]; bc/=np.linalg.norm(bc)
  normal=np.cross(x[j-2]-x[j-3],bc); length=np.linalg.norm(normal)
  if length<1e-10: raise ValueError('degenerate backbone')
  normal/=length; tangent=np.cross(normal,bc)
  x[j]=x[j-1]+d[j-1]*(-math.cos(a[j-2])*bc+math.sin(a[j-2])*(math.cos(t[j-3])*tangent+math.sin(t[j-3])*normal))
 if not np.isfinite(x).all(): raise ValueError('nonfinite reconstruction')
 return x

def decode(row,model,n):
 codec=model['codec']; bits=32
 if codec=='motif':
  exact_keys(row,['id','motifs','glue']); ids=row['motifs']; joins=row['glue']
  if not 1<=len(ids)<=n or len(joins)!=len(ids)-1: raise ValueError('invalid stream lengths')
  d=[]; a=[]; t=[]
  for i,mid in enumerate(ids):
   md,ma,mt=model['motifs'][index(mid,len(model['motifs']))]
   if len(md)%3 != (2 if i==len(ids)-1 else 0): raise ValueError('invalid terminal motif')
   if i:
    g=joins[i-1]
    if not isinstance(g,list) or len(g)!=3: raise ValueError('missing boundary information')
    theta,omega,phi=[model['glue'][k][index(v,len(model['glue'][k]))] for k,v in zip(('theta','omega','phi'),g)]
    a.append(theta); t.extend((omega,phi))
   d.extend(md); a.extend(ma); t.extend(mt)
  if len(d)!=3*n-1: raise ValueError('reconstruction does not cover the complete chain')
  bits+=len(ids)*width(len(model['motifs']))+len(joins)*sum(width(len(v)) for v in model['glue'].values())
  x=nerf(d,a,t)
 elif codec=='internal':
  exact_keys(row,['id','indices']); lists=row['indices']
  if not isinstance(lists,list) or len(lists)!=3: raise ValueError('invalid internal stream')
  values=[]
  for group,expected in enumerate((3*n-1,3*n-2,3*n-3)):
   seq=lists[group]
   if len(seq)!=expected: raise ValueError('incomplete internal stream')
   arr=[]
   for j,v in enumerate(seq):
    bins=model['bins'][group*3+j%3]; arr.append(bins[index(v,len(bins))]); bits+=width(len(bins))
   values.append(arr)
  x=nerf(*values)
 else:
  exact_keys(row,['id','coordinates']); x=np.asarray(row['coordinates'],dtype=np.float32).astype(float)
  if x.shape!=(3*n,3) or not np.isfinite(x).all(): raise ValueError('invalid full coordinate output')
  bits+=x.size*32
 if x.shape!=(3*n,3): raise ValueError('wrong reconstructed size')
 return x,bits

def target(path):
 x=[]
 for line in Path(path).read_text().splitlines():
  if line.startswith('ATOM  '): x.append([float(line[j:j+8]) for j in (30,38,46)])
 a=np.asarray(x,float)
 if len(a)%3 or not np.isfinite(a).all(): raise ValueError('invalid evaluator target')
 return a

def quality(native,reconstruction):
 """Backbone Kabsch RMSD and per-residue CA lDDT (15 A, four tolerances)."""
 if native.shape!=reconstruction.shape: raise ValueError('shape mismatch')
 p=reconstruction-reconstruction.mean(0); q=native-native.mean(0)
 u,_,vh=np.linalg.svd(p.T@q); correction=np.eye(3); correction[-1,-1]=np.linalg.det(u@vh)
 rmsd=float(np.sqrt(np.mean(np.sum((p@u@correction@vh-q)**2,axis=1))))
 ca=native[1::3]; cb=reconstruction[1::3]
 dist=np.linalg.norm(ca[:,None]-ca[None,:],axis=-1); pred=np.linalg.norm(cb[:,None]-cb[None,:],axis=-1)
 mask=(dist<15)&(~np.eye(len(ca),dtype=bool)); count=mask.sum(1)
 delta=np.abs(dist-pred); local=sum((delta<cut)*mask for cut in (.5,1.,2.,4.))/4
 valid=count>0
 lddt=float((local.sum(1)[valid]/count[valid]).mean())
 if not (math.isfinite(rmsd) and rmsd>=0 and math.isfinite(lddt) and 0<=lddt<=1): raise ValueError('impossible quality value')
 return rmsd,lddt

def dataset():
 rows=read_json(HERE/'sources.json'); out={}
 for exp,(split,size) in EXPERIMENTS.items():
  selected=[r for r in rows if r['split']==split]
  if len(selected)!=size: raise ValueError('fixed test size mismatch')
  out[exp]=[(f"{r['pdb']}_{r['chain']}",HERE/'downloads'/split/f"{r['pdb']}_{r['chain']}.pdb",r) for r in selected]
 return out

def measure(raw,model_info,targets):
 model,model_bits,vocab=model_info
 if not isinstance(raw,list): raise ValueError('outputs must be a list')
 wanted={name for entries in targets.values() for name,_,_ in entries}
 if len(raw)!=len(wanted) or {r.get('id') for r in raw}!=wanted: raise ValueError('missing, duplicate or unknown instances')
 by_id={r['id']:r for r in raw}; result={}; details={}
 for exp,entries in targets.items():
  rr=[]; ll=[]; lengths=[]; stream_bits=[]
  for name,path,source in entries:
   native=target(path); n=len(native)//3
   if n!=source['residues'] or hashlib.sha256(path.read_bytes()).hexdigest()!=source['sha256']: raise ValueError('private source integrity failure')
   pred,bits=decode(by_id[name],model,n); rmsd,lddt=quality(native,pred)
   rr.append(rmsd); ll.append(lddt); lengths.append(n); stream_bits.append(bits)
  result[exp]={'rmsd':float(np.mean(rr)),'lddt':float(np.mean(ll)),'bpr':float((model_bits+sum(stream_bits))/sum(lengths)),'vocab_size':float(vocab)}
  details[exp]={'rmsd':rr,'lddt':ll,'residues':lengths,'bits':stream_bits,'model_bits':model_bits}
 return result,details

def feasibility(values):
 reasons=[]
 for exp,row in values.items():
  if any(not math.isfinite(v) for v in row.values()): reasons.append(exp+': nonfinite metric')
  if row['rmsd']>LIMITS['rmsd'] or row['lddt']<LIMITS['lddt']: reasons.append(exp+': reconstruction constraint')
  if not 0<row['bpr']<=LIMITS['bpr'] or not 1<=row['vocab_size']<=LIMITS['vocab_size']: reasons.append(exp+': rate/dictionary constraint')
 return reasons

def rank(records,reference):
 """Normalize by this cohort's measured variation; failed runs never outrank passes."""
 comparable=[r for r in records.values() if 'metrics' in r and not r['failed']]
 if not comparable: raise RuntimeError('no valid attempts')
 scales={exp:{m:float(np.std([r['metrics'][exp][m] for r in comparable],ddof=0)) for m in METRICS} for exp in EXPERIMENTS}
 for r in records.values():
  if r['failed']:
   r['rank']=-1e100; continue
  r['rank']=float(sum(WEIGHTS[exp]*abs(c)*(1 if up else -1)*(r['metrics'][exp][m]-reference[exp][m])/scales[exp][m] for exp in EXPERIMENTS for m,(up,c) in METRICS.items() if scales[exp][m]>1e-12))
 return scales

def paired_intervals(records,reference_details,scales,reference):
 """Paired bootstrap of fixed inputs. Dictionary size/cost remain fixed per method."""
 rng=np.random.default_rng(20261109)
 indices={exp:rng.integers(0,size,(1000,size)) for exp,(_,size) in EXPERIMENTS.items()}
 for r in records.values():
  if r['failed']: continue
  draws=np.zeros(1000)
  for exp in EXPERIMENTS:
   ix=indices[exp]; d=r['details'][exp]; ref=reference_details[exp]
   candidate={'rmsd':np.asarray(d['rmsd'])[ix].mean(1),'lddt':np.asarray(d['lddt'])[ix].mean(1),'bpr':(d['model_bits']+np.asarray(d['bits'])[ix].sum(1))/np.asarray(d['residues'])[ix].sum(1),'vocab_size':r['metrics'][exp]['vocab_size']}
   base={'rmsd':np.asarray(ref['rmsd'])[ix].mean(1),'lddt':np.asarray(ref['lddt'])[ix].mean(1),'bpr':(ref['model_bits']+np.asarray(ref['bits'])[ix].sum(1))/np.asarray(ref['residues'])[ix].sum(1),'vocab_size':reference[exp]['vocab_size']}
   for m,(up,c) in METRICS.items():
    if scales[exp][m]>1e-12: draws+=WEIGHTS[exp]*abs(c)*(1 if up else -1)*(candidate[m]-base[m])/scales[exp][m]
  r['paired_rank_95ci']=[float(v) for v in np.quantile(draws,[.025,.975])]

def main():
 targets=dataset(); records={}; runs=HERE/'runs'; runs.mkdir(exist_ok=True)
 manifests=sorted((ROOT/'checkpoints'/'submissions').glob('*/manifest.json'))
 if not manifests: raise RuntimeError('no method manifests on disk')
 for path in manifests:
  name=path.parent.name; record={'failed':True}; records[name]=record
  try:
   manifest=read_json(path); model_json=read_json(ROOT/manifest['model']); model_info=load_model(model_json)
   run=runs/name; run.mkdir(exist_ok=True)
   frozen=run/'model.json'; write_json(frozen,model_json)
   request=run/'request.json'; write_json(request,[{'id':name,'path':str(p)} for entries in targets.values() for name,p,_ in entries])
   output=run/'outputs.json'
   if os.environ.get('EVAL_RESCORE')!='1' or not output.exists():
    command=[str(s).format(request=str(request),output=str(output),model=str(frozen)) for s in manifest['command']]
    with (run/'encoder.log').open('w') as log:
     subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=7200)
   values,details=measure(read_json(output),model_info,targets)
   reasons=feasibility(values); record.update(metrics=values,details=details,failed=bool(reasons),reasons=reasons)
  except Exception as exc: record.update(malformed=True,reasons=[str(exc)])
  write_json(HERE/'measurements.json',records)
 baseline_path=HERE/'reference_frozen.json'
 if os.environ.get('EVAL_FREEZE_REFERENCE')=='1':
  name=os.environ['EVAL_REFERENCE_NAME']; ref=records[name]
  if ref['failed']: raise RuntimeError('reference failed: '+str(ref.get('reasons')))
  write_json(baseline_path,{'metrics':ref['metrics'],'details':ref['details']})
 reference=read_json(baseline_path)
 scales=rank(records,reference['metrics']); paired_intervals(records,reference['details'],scales,reference['metrics'])
 write_json(HERE/'ranking.json',{'normalization':scales,'methods':records})
 write_json(HERE/'scores_all.json',{'experiments':{exp:{name:r['metrics'][exp] for name,r in records.items() if 'metrics' in r} for exp in EXPERIMENTS}})
 print(json.dumps({name:{k:r[k] for k in ('failed','rank','reasons','paired_rank_95ci') if k in r} for name,r in records.items()},indent=2))
if __name__=='__main__': main()
