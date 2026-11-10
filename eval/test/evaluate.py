"""Private, method-independent decoder, measurement and failure gates.

Every checkpoints/submissions/*/manifest.json on disk is encoded through the same
interface and decoded here. Each method's four metrics per experiment are written
to scoring/scores_test.json under experiments.<name>.results.<method>. That file is
the only scored output. A malformed, crashed, file-modifying or constraint-failing
attempt receives the fixed worst value of every scored metric in every experiment.

Submitted values are representation symbols, never scores, counts, flags or
targets. Targets, test size, limits and worst values are owned by this directory.
Method, data and public evaluation code are not imported. Evaluation never trains
a submitted method.
"""
from __future__ import annotations
import hashlib,json,math,os,subprocess,time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SLICE='test'
EXPERIMENTS={'short_backbones':('short',64),'long_backbones':('long',64)}
SCORES=ROOT/'scoring'/'scores_test.json'
REFERENCE=ROOT/'scoring'/'reference.json'
# Evaluator-owned copy of the published comparison (coefficients, weights and the
# reproduced reference values). It replaces any edited public copy before and
# after every attempt, so a method cannot move the other side of a comparison.
CANONICAL=HERE/'reference_canonical.json'

def read_json(path):
 return json.loads(Path(path).read_text(),parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
def write_json(path,obj):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_name(path.name+'.partial'); temp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n'); temp.replace(path)

CONTRACT=read_json(HERE/'contract.json')
METRICS={m:(d['higher_is_better'],abs(d['coefficient'])) for m,d in CONTRACT['experiments'][next(iter(EXPERIMENTS))]['metrics'].items()}
WEIGHTS={e:CONTRACT['experiments'][e]['weight'] for e in EXPERIMENTS}
# Fixed task feasibility constraints, chosen before the final runs.
LIMITS={k:float(v) for k,v in CONTRACT['limits'].items()}
# Every failed attempt is scored at these values: no better than any feasible run.
WORST={m:float(CONTRACT['worst'][m]) for m in METRICS}

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
 if not isinstance(obj,dict): raise ValueError('model must be an object')
 codec=obj.get('codec'); model_bits=128
 if codec=='motif':
  exact_keys(obj,['codec','motifs','glue'])
  if not isinstance(obj['motifs'],list) or not 1<=len(obj['motifs'])<=8192: raise ValueError('invalid dictionary size')
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
  exact_keys(obj,['codec','bins'])
  if not isinstance(obj['bins'],list): raise ValueError('invalid internal-coordinate alphabets')
  bins=[floats(v) for v in obj['bins']]
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
  if not isinstance(ids,list) or not isinstance(joins,list): raise ValueError('invalid stream lengths')
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
   if not isinstance(seq,list) or len(seq)!=expected: raise ValueError('incomplete internal stream')
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

def parse_backbone(text):
 x=[]
 for line in text.splitlines():
  if line.startswith('ATOM  '): x.append([float(line[j:j+8]) for j in (30,38,46)])
 a=np.asarray(x,float)
 if len(a)%3 or not np.isfinite(a).all(): raise ValueError('invalid evaluator target')
 return a
def target(path):
 return parse_backbone(Path(path).read_text())

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
 """Load and verify every private target once; measurement never rereads files."""
 rows=read_json(HERE/'sources.json'); out={}
 for exp,(split,size) in EXPERIMENTS.items():
  selected=[r for r in rows if r['split']==split]
  if len(selected)!=size: raise ValueError('fixed test size mismatch')
  entries=[]
  for r in selected:
   name=f"{r['pdb']}_{r['chain']}"; path=HERE/'downloads'/split/f"{name}.pdb"; data=path.read_bytes()
   if hashlib.sha256(data).hexdigest()!=r['sha256']: raise ValueError('private source integrity failure: '+name)
   native=parse_backbone(data.decode())
   if len(native)//3!=r['residues']: raise ValueError('private source length mismatch: '+name)
   entries.append((name,path,r,native))
  out[exp]=entries
 return out

def measure(raw,model_info,targets):
 model,model_bits,vocab=model_info
 if not isinstance(raw,list) or not all(isinstance(r,dict) for r in raw): raise ValueError('outputs must be a list of objects')
 wanted={name for entries in targets.values() for name,_,_,_ in entries}
 ids=[r.get('id') for r in raw]
 if len(raw)!=len(wanted) or len(set(map(str,ids)))!=len(ids) or set(ids)!=wanted: raise ValueError('missing, duplicate or unknown instances')
 by_id={r['id']:r for r in raw}; result={}; details={}
 total_residues=sum(len(native)//3 for entries in targets.values() for _,_,_,native in entries)
 for exp,entries in targets.items():
  rr=[]; ll=[]; lengths=[]; stream_bits=[]
  for name,_,_,native in entries:
   n=len(native)//3
   pred,bits=decode(by_id[name],model,n); rmsd,lddt=quality(native,pred)
   rr.append(rmsd); ll.append(lddt); lengths.append(n); stream_bits.append(bits)
  result[exp]={'rmsd':float(np.mean(rr)),'lddt':float(np.mean(ll)),'bpr':float(sum(stream_bits)/sum(lengths)+model_bits/total_residues),'vocab_size':float(vocab)}
  details[exp]={'ids':[name for name,_,_,_ in entries],'rmsd':rr,'lddt':ll,'residues':lengths,'bits':stream_bits,'model_bits':model_bits}
 return result,details

def feasibility(values):
 reasons=[]
 for exp,row in values.items():
  if any(not math.isfinite(v) for v in row.values()): reasons.append(exp+': nonfinite metric'); continue
  if row['rmsd']>LIMITS['rmsd'] or row['lddt']<LIMITS['lddt']: reasons.append(exp+': reconstruction constraint')
  if not 0<row['bpr']<=LIMITS['bpr'] or not 1<=row['vocab_size']<=LIMITS['vocab_size']: reasons.append(exp+': rate/dictionary constraint')
 return reasons

def scored(record):
 """The only values that are ranked: measured metrics, or worst values on failure."""
 if record.get('failed',True) or 'metrics' not in record: return {exp:dict(WORST) for exp in EXPERIMENTS}
 return {exp:{m:float(record['metrics'][exp][m]) for m in METRICS} for exp in EXPERIMENTS}

def write_outputs(records):
 scores={'_metadata':{'slice':SLICE,'source':'evaluator-decoded raw representations of every checkpoints/submissions/*/manifest.json','failed_attempts_scored_at':WORST,'failed':{n:r.get('reasons',[]) for n,r in records.items() if r.get('failed',True)}},
  'experiments':{exp:{'results':{n:scored(r)[exp] for n,r in records.items()}} for exp in EXPERIMENTS}}
 write_json(SCORES,scores)
 write_json(HERE/'measurements.json',records)

def restore_reference():
 if CANONICAL.exists():
  data=CANONICAL.read_bytes()
  if not REFERENCE.exists() or REFERENCE.read_bytes()!=data:
   REFERENCE.parent.mkdir(parents=True,exist_ok=True); REFERENCE.write_bytes(data); return True
 return False

def snapshot(targets):
 paths=[REFERENCE,CANONICAL,HERE/'contract.json',HERE/'sources.json',Path(__file__).resolve()]
 paths+=[p for entries in targets.values() for _,p,_,_ in entries]
 return {p:p.read_bytes() for p in paths if p.exists()}
def restore(snap):
 """Undo any change an attempt made to evaluator-owned or comparison files. Never raises."""
 changed=[]
 for p,data in snap.items():
  try: same=p.read_bytes()==data
  except OSError: same=False
  if not same:
   try: p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
   except OSError: pass
   try: changed.append(str(p.relative_to(ROOT)))
   except ValueError: changed.append(str(p))
 return changed

def evaluate_one(path,targets,snap,runs):
 name=path.parent.name; record={'failed':True,'reasons':[]}
 try:
  manifest=read_json(path)
  if not isinstance(manifest,dict) or not isinstance(manifest.get('model'),str): raise ValueError('invalid manifest')
  command=manifest.get('command')
  if not isinstance(command,list) or not command or not all(isinstance(s,str) for s in command): raise ValueError('invalid manifest command')
  model_json=read_json(ROOT/manifest['model']); model_info=load_model(model_json)
  run=runs/name; run.mkdir(parents=True,exist_ok=True)
  frozen=run/'model.json'; write_json(frozen,model_json)
  request=run/'request.json'; write_json(request,[{'id':n,'path':str(p)} for entries in targets.values() for n,p,_,_ in entries])
  output=run/'outputs.json'
  if os.environ.get('EVAL_RESCORE')!='1' or not output.exists():
   output.unlink(missing_ok=True)
   argv=[s.format(request=str(request),output=str(output),model=str(frozen)) for s in command]
   start=time.time()
   try:
    with (run/'encoder.log').open('w') as log:
     subprocess.run(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=7200)
   finally:
    changed=restore(snap); record['encoder_seconds']=round(time.time()-start,1)  # diagnostic only, never scored
   if changed: raise ValueError('attempt modified evaluation or comparison files: '+', '.join(changed[:5]))
  values,details=measure(read_json(output),model_info,targets)
  reasons=feasibility(values); record.update(metrics=values,details=details,failed=bool(reasons),reasons=reasons)
 except Exception as exc:
  restore(snap); record.update(failed=True,malformed=True,reasons=[f'{type(exc).__name__}: {exc}'[:500]])
 return name,record

def main():
 restore_reference()
 targets=dataset(); snap=snapshot(targets)
 runs=HERE/'runs'; runs.mkdir(exist_ok=True); records={}
 manifests=sorted((ROOT/'checkpoints'/'submissions').glob('*/manifest.json'))
 for path in manifests:
  name,record=evaluate_one(path,targets,snap,runs); records[name]=record
  write_outputs(records)
 write_outputs(records)
 restore_reference()
 print(json.dumps({name:{'failed':r['failed'],'reasons':r['reasons'],'scored':scored(r)} for name,r in records.items()},indent=2))
if __name__=='__main__': main()
