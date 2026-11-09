"""Apply a frozen released GEOBPE vocabulary to evaluator-supplied PDB inputs.

Atomic per-chain recovery is for interrupted reproduction jobs. The evaluator
still independently decodes and measures every saved representation.
"""
import argparse,hashlib,json,os,pickle,sys,warnings
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1'); os.environ.setdefault('MKL_NUM_THREADS','1'); os.environ.setdefault('GEOBPE_DATASET_WORKERS','1'); os.environ.setdefault('SLURM_CPUS_PER_TASK','1')
# The released pandas assignments work with the pinned pandas<3 dependency.
warnings.filterwarnings('ignore',category=FutureWarning)
UPSTREAM=Path(__file__).resolve().parent/'PT-BPE'
sys.path.insert(0,str(UPSTREAM))
import numpy as np
import torch
from foldingdiff.bpe import BPE
from foldingdiff.datasets import FullCathCanonicalCoordsDataset
from foldingdiff.tokenizer import Tokenizer

def atomic_json(path,value):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.partial')
 temp.write_text(json.dumps(value,allow_nan=False)+'\n'); temp.replace(path)

def fingerprint(checkpoint,model):
 h=hashlib.sha256(Path(checkpoint).read_bytes())
 h.update(Path(__file__).read_bytes())
 h.update(json.dumps(json.loads(Path(model).read_text()),sort_keys=True,separators=(',',':')).encode())
 for name in ('bpe.py','tokenizer.py','datasets.py','angles_and_coords.py'):
  h.update((UPSTREAM/'foldingdiff'/name).read_bytes())
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser(); p.add_argument('--checkpoint',required=True); p.add_argument('--request',required=True); p.add_argument('--output',required=True); p.add_argument('--model',required=True); a=p.parse_args()
 torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)
 requests=json.loads(Path(a.request).read_text())
 paths={str(Path(r['path']).resolve()):r['id'] for r in requests}
 if len(paths)!=len(requests) or len(set(paths.values()))!=len(requests): raise ValueError('duplicate input')
 hashes={r['id']:hashlib.sha256(Path(r['path']).read_bytes()).hexdigest() for r in requests}
 output=Path(a.output); meta=output.with_suffix('.resume.json'); identity=fingerprint(a.checkpoint,a.model)
 cached={}
 if output.exists() or meta.exists():
  try:
   state=json.loads(meta.read_text()) if meta.exists() else None
   # Explicit one-time adoption of outputs from the interrupted pre-recovery
   # audit. Scientific code, checkpoints and existing inputs are unchanged.
   if state is None and os.environ.get('GEOBPE_ADOPT_INTERRUPTED_OUTPUTS')=='1':
    state={'fingerprint':identity,'inputs':hashes,'outputs':json.loads(output.read_text())}
   if state and state['fingerprint']==identity:
    for row in state['outputs']:
     rid=row['id']
     if set(row)=={'id','motifs','glue'} and rid in hashes and state['inputs'].get(rid)==hashes[rid]: cached[rid]=row
  except (ValueError,KeyError,TypeError):
   cached={}
 def save():
  rows=[cached[r['id']] for r in requests if r['id'] in cached]
  # One atomic recovery artifact contains both provenance and its streams.
  # Re-render the evaluator's raw interface after committing that artifact.
  atomic_json(meta,{'fingerprint':identity,'inputs':hashes,'outputs':rows})
  atomic_json(output,rows)
 save()
 print('recovered',len(cached),'of',len(requests),'complete streams',flush=True)
 if len(cached)==len(requests): return
 with open(a.checkpoint,'rb') as f: bpe=pickle.load(f)
 keys=list(bpe._tokens); keymap={k:i for i,k in enumerate(keys)}
 # Dataset parsing and tokenization are unchanged; skip only completed chains.
 for directory in sorted({str(Path(p).parent) for p,rid in paths.items() if rid not in cached}):
  dataset=FullCathCanonicalCoordsDataset(directory,use_cache=False,zero_center=False,toy=0,pad=512)
  for structure in dataset.structures:
   path=str(Path(structure['fname']).resolve())
   if path not in paths or paths[path] in cached: continue
   tok,_=bpe.tokenize(Tokenizer(structure)); ids=[]; glue=[]
   for start,key,length in tok.bond_to_token.values():
    ids.append(keymap[key]); b=start+length
    if b<3*tok.n-1:
     vals=[tok._bond_angle(b-1),tok._dihedral_angle(b-2),tok._dihedral_angle(b-1)]
     glue.append([int(BPE.get_ind((float(v)+2*np.pi)%(2*np.pi),bpe._thresholds[1][k])) for k,v in zip(('C:1N:1CA','omega','phi'),vals)])
   cached[paths[path]]={'id':paths[path],'motifs':ids,'glue':glue}; save()
   print('encoded',paths[path],len(ids),flush=True)
 if len(cached)!=len(requests): raise ValueError(f'missing inputs: {len(cached)}/{len(requests)}')
if __name__=='__main__': main()
