"""Apply a frozen released GEOBPE vocabulary to evaluator-supplied PDB inputs."""
import argparse,json,os,pickle,sys
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1'); os.environ.setdefault('MKL_NUM_THREADS','1'); os.environ.setdefault('GEOBPE_DATASET_WORKERS','1'); os.environ.setdefault('SLURM_CPUS_PER_TASK','1')
sys.path.insert(0,str(Path(__file__).resolve().parent/'PT-BPE'))
import numpy as np
import torch
from foldingdiff.bpe import BPE
from foldingdiff.datasets import FullCathCanonicalCoordsDataset
from foldingdiff.tokenizer import Tokenizer

def main():
 p=argparse.ArgumentParser(); p.add_argument('--checkpoint',required=True); p.add_argument('--request',required=True); p.add_argument('--output',required=True); p.add_argument('--model',required=True); a=p.parse_args()
 torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)
 with open(a.checkpoint,'rb') as f: bpe=pickle.load(f)
 keys=list(bpe._tokens); keymap={k:i for i,k in enumerate(keys)}
 requests=json.loads(Path(a.request).read_text()); paths={str(Path(r['path']).resolve()):r['id'] for r in requests}; outputs=[]
 # All inputs are in two evaluator-owned length buckets. Dataset parsing is unchanged.
 for directory in sorted({str(Path(p).parent) for p in paths}):
  dataset=FullCathCanonicalCoordsDataset(directory,use_cache=False,zero_center=False,toy=0,pad=512)
  for structure in dataset.structures:
   path=str(Path(structure['fname']).resolve())
   if path not in paths: continue
   tok,_=bpe.tokenize(Tokenizer(structure)); ids=[]; glue=[]
   for start,key,length in tok.bond_to_token.values():
    ids.append(keymap[key]); b=start+length
    if b<3*tok.n-1:
     vals=[tok._bond_angle(b-1),tok._dihedral_angle(b-2),tok._dihedral_angle(b-1)]
     glue.append([int(BPE.get_ind((float(v)+2*np.pi)%(2*np.pi),bpe._thresholds[1][k])) for k,v in zip(('C:1N:1CA','omega','phi'),vals)])
   outputs.append({'id':paths[path],'motifs':ids,'glue':glue})
   # Incremental recovery if a long encoding job is interrupted.
   Path(a.output).write_text(json.dumps(outputs,allow_nan=False)+'\n')
   print('encoded',paths[path],len(ids),flush=True)
 if len(outputs)!=len(requests): raise ValueError(f'missing inputs: {len(outputs)}/{len(requests)}')
if __name__=='__main__': main()
