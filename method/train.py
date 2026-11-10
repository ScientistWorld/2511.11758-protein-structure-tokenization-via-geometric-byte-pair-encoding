"""Train the released GEOBPE algorithm, without the upstream plotting driver.

Table 14 pipeline with explicit codebook, occurrence and iteration settings:
empirical quantizers, RMSD k-medoid residue initialization, global glue
optimization, the geo-pair map, then `--iterations` merge steps. The reference
uses the main codebook at the operating point Table 16 reports for it
(|V| = 600, no merged keys; Appendix K.2 stops merging early at high
resolution). `--iterations 5` on the same fit gives the merge ablation.
No held-out data is loaded during fitting.
"""
import argparse,json,os,pickle,sys,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'method'/'PT-BPE'
sys.path.insert(0,str(UPSTREAM))
os.environ.setdefault('OMP_NUM_THREADS','1'); os.environ.setdefault('MKL_NUM_THREADS','1')
os.environ.setdefault('GEOBPE_DATASET_WORKERS','1'); os.environ.setdefault('SLURM_CPUS_PER_TASK','1')
import numpy as np
import torch
from foldingdiff.bpe import BPE
from foldingdiff.datasets import FullCathCanonicalCoordsDataset
from foldingdiff.tokenizer import Tokenizer

def export_model(bpe,path):
 motifs=[]
 for key,geo in bpe._tokens.items():
  n=Tokenizer.num_bonds(geo)
  lists=[]
  for keys,count in ((Tokenizer.BOND_TYPES,n),(Tokenizer.BOND_ANGLES,n-1),(Tokenizer.DIHEDRAL_ANGLES,n-2)):
   lists.append([float(geo[keys[j%3]][j//3]) for j in range(count)])
  motifs.append(dict(zip(('bonds','angles','torsions'),lists)))
 glue={k:[float(sum(pair)/2) for pair in bpe._thresholds[1][source]] for k,source in (('theta','C:1N:1CA'),('omega','omega'),('phi','phi'))}
 Path(path).write_text(json.dumps({'codec':'motif','motifs':motifs,'glue':glue},allow_nan=False)+'\n')
def manifest(name,checkpoint):
 dest=ROOT/'checkpoints'/'submissions'/name; dest.mkdir(parents=True,exist_ok=True)
 with Path(checkpoint).open('rb') as f: bpe=pickle.load(f)
 export_model(bpe,dest/'model.json')
 (dest/'manifest.json').write_text(json.dumps({'model':str((dest/'model.json').relative_to(ROOT)),'command':['python','method/encode.py','--checkpoint',str(Path(checkpoint).relative_to(ROOT)),'--request','{request}','--output','{output}','--model','{model}']},indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--name',required=True); p.add_argument('--bins',type=int,default=500); p.add_argument('--iterations',type=int,default=50); p.add_argument('--interior',type=int,default=50); p.add_argument('--terminal',type=int,default=10); p.add_argument('--export-only'); p.add_argument('--run-id'); p.add_argument('--main-codebook',action='store_true'); p.add_argument('--candidates',type=int,default=512); p.add_argument('--seed',type=int,default=0); a=p.parse_args()
 if a.export_only: manifest(a.name,ROOT/a.export_only); return
 np.random.seed(a.seed); random.seed(a.seed); torch.manual_seed(a.seed); torch.set_num_threads(1)
 dest=ROOT/'checkpoints'/'hardening'/(a.run_id or a.name); dest.mkdir(parents=True,exist_ok=True)
 # The default seed 0 is the reference; its stored configuration predates this option.
 config=dict(vars(a)); configfile=dest/'config.json'
 if a.seed==0: config.pop('seed')
 if configfile.exists() and json.loads(configfile.read_text())!=config: raise ValueError('refusing to resume incompatible configuration')
 configfile.write_text(json.dumps(config,indent=2)+'\n')
 ckpt=dest/'latest.pkl'
 if ckpt.exists():
  with ckpt.open('rb') as f: bpe=pickle.load(f)
 else:
  dataset=FullCathCanonicalCoordsDataset(str(ROOT/'data'/'downloads'/'pdb'/'train'),use_cache=False,zero_center=False,toy=0,pad=512)
  if len(dataset.structures)!=128:
   expected={str(p) for p in (ROOT/'data/downloads/pdb/train').glob('*.pdb')}
   missing=sorted(expected-{s['fname'] for s in dataset.structures})
   raise ValueError(f'expected 128 training chains, got {len(dataset.structures)}; missing: {missing}')
  for s in dataset.structures:
   if s['angles']['psi'].notna().sum()<len(s['angles'])-1: raise ValueError('incomplete training chain')
  bpe=BPE(dataset.structures,bins={1:a.bins},bin_strategy='histogram',save_dir=str(dest),res_init=True,std_bonds=False,rmsd_partition_min_size=2,rmsd_super_res=True,rmsd_only=False,num_partitions=({2:a.terminal,3:a.interior,5:20,6:100} if a.main_codebook else {2:a.terminal,3:a.interior,5:1,6:5,8:1}),max_num_strucs=a.candidates,glue_opt=True,glue_opt_prior=1.,glue_opt_every=10,glue_opt_method='all',seed=a.seed)
  bpe.initialize()
  bpe.glue_opt_all()
  with (dest/'post_init.pkl').open('wb') as f: pickle.dump(bpe,f)
  bpe.bin()
  with ckpt.open('wb') as f: pickle.dump(bpe,f)
 while bpe._step<a.iterations:
  bpe.step()
  temp=dest/'latest.partial'
  with temp.open('wb') as f: pickle.dump(bpe,f)
  temp.replace(ckpt)
  print(a.name,'step',bpe._step,'motifs',len(bpe._tokens),flush=True)
 manifest(a.name,ckpt)
if __name__=='__main__': main()
