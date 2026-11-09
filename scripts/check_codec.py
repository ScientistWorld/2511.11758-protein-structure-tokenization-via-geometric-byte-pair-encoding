"""Light job-side compatibility check against the released forward geometry."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'method/PT-BPE'))
import numpy as np
from foldingdiff.datasets import FullCathCanonicalCoordsDataset
from foldingdiff.tokenizer import Tokenizer
spec=importlib.util.spec_from_file_location('public_decoder',ROOT/'eval/train/evaluate.py'); ev=importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
d=([1.46,1.53,1.33]*4)[:-1]; a=([1.93,2.04,2.12]*4)[:10]; t=([.7,3.14,5.1]*4)[:9]
geo={}
for keys,arr in ((Tokenizer.BOND_TYPES,d),(Tokenizer.BOND_ANGLES,a),(Tokenizer.DIHEDRAL_ANGLES,t)):
 for j,k in enumerate(keys): geo[k]=arr[j::3]
official=Tokenizer.geo_nerf(geo).cartesian_coords
model={'codec':'motif','motifs':[{'bonds':d[:3],'angles':a[:2],'torsions':t[:1]},{'bonds':d[3:],'angles':a[3:],'torsions':t[3:]}],'glue':{'theta':[a[2]],'omega':[t[1]],'phi':[t[2]]}}
m,cost,vocab=ev.load_model(model); predicted,bits=ev.decode({'id':'synthetic','motifs':[0,1],'glue':[[0,0,0]]},m,4)
rmsd,lddt=ev.quality(official,predicted)
assert rmsd<1e-5,(rmsd,official,predicted)
assert lddt==1 and cost>32*sum(map(len,(d,a,t))) and bits>0 and vocab==5
for malformed in ({'id':'synthetic','motifs':[-1],'glue':[]},{'id':'synthetic','motifs':[0],'glue':[]},{'id':'synthetic','motifs':[0,1],'glue':[[0,0,0]],'tokens':0}):
 try: ev.decode(malformed,m,4)
 except ValueError: pass
 else: raise AssertionError('malformed stream accepted')
print('Independent decoder matches released geometry; invalid stream checks pass.')
# Exercise the released PDB parser before any costly fitting. This includes
# 1x5n_A, whose planar omega exposed float32 +/-pi boundary rejection.
for split,count in (('train',128),('visible_short',32),('visible_long',32)):
 dataset=FullCathCanonicalCoordsDataset(str(ROOT/'data/downloads/pdb'/split),use_cache=False,zero_center=False,toy=0,pad=512)
 assert len(dataset.structures)==count,(split,len(dataset.structures),count)
 for structure in dataset.structures:
  angles=structure['angles']
  assert angles['psi'].notna().sum()==len(angles)-1,structure['fname']
 print('Released parser accepts all',count,split,'chains.',flush=True)
