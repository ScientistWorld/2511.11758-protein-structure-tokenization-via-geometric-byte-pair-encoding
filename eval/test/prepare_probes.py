"""Register verifier-only attacks. No hidden coordinates leave eval/test/."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'baseline'))
from internal import coordinates,geometry

def main():
 source=json.loads((ROOT/'checkpoints/submissions/geobpe_reference/model.json').read_text())
 motifs=[]
 for public in sorted((ROOT/'data/pdb_smoke/cameo').glob('*.pdb'))+sorted((ROOT/'data/pdb_smoke/casp14').glob('*.pdb')):
  d,a,t=geometry(coordinates(public)); motifs.append({'bonds':d.tolist(),'angles':a.tolist(),'torsions':t.tolist()})
 dictionary={'codec':'motif','motifs':motifs,'glue':{'theta':[1.9],'omega':[3.14],'phi':[3.14]}}
 for attack in ('forged_target','forged_counts','negative_counts','truncated','constant_template','public_dictionary','prune_comparison'):
  dest=ROOT/'checkpoints/submissions'/('attack_'+attack); dest.mkdir(parents=True,exist_ok=True)
  model=source if attack not in ('truncated','constant_template','public_dictionary') else dictionary if attack=='public_dictionary' else {'codec':'cartesian'}
  (dest/'model.json').write_text(json.dumps(model)+'\n')
  (dest/'manifest.json').write_text(json.dumps({'model':str((dest/'model.json').relative_to(ROOT)),'command':['python','eval/test/probes.py','--attack',attack,'--request','{request}','--output','{output}','--model','{model}']},indent=2)+'\n')
if __name__=='__main__': main()
