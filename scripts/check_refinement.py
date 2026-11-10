"""Check the rotation calculus against complete reconstruction before the audit."""
import importlib.util
from pathlib import Path
import numpy as np
_spec=importlib.util.spec_from_file_location('refine_glue',Path(__file__).resolve().parents[1]/'eval/test/variants/refine_glue.py')
_mod=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
nerf,rotated_tail,refine,expand,quality=_mod.nerf,_mod.rotated_tail,_mod.refine,_mod.expand,_mod.quality

def main():
 d=[1.4]*11; a=[1.9]*10; t=[2.8,-1.1,.7]*3
 x=nerf(d,a,t)
 for channel in range(3):
  for delta in (-.02,.03):
   aa=a.copy(); tt=t.copy(); b=3
   if channel==0: aa[b-1]+=delta
   else: tt[b-3+channel]+=delta
   expected=nerf(d,aa,tt); start,tail=rotated_tail(x,b,channel,delta)
   actual=x.copy(); actual[start:]=tail
   assert np.max(np.abs(expected-actual))<1e-10,(channel,delta)
 model={'motifs':[{'bonds':[1.4]*3,'angles':[1.9]*2,'torsions':[2.8]}, {'bonds':[1.4]*2,'angles':[1.9],'torsions':[]}], 'glue':{'theta':[1.89,1.9,1.91],'omega':[2.79,2.8,2.81],'phi':[2.79,2.8,2.81]}}
 row={'id':'synthetic','motifs':[0,0,0,1],'glue':[[0,0,0] for _ in range(3)]}
 truth={'id':'synthetic','motifs':[0,0,0,1],'glue':[[1,1,1] for _ in range(3)]}
 native=nerf(*expand(truth,model)[:3]); result,before,after=refine(native,row,model)
 assert after[0]<before[0] and after[1]>=before[1]
 print('Boundary rotations match complete NeRF; discrete refinement improves synthetic fidelity at unchanged storage.')
if __name__=='__main__': main()
