"""One-time public corpus extension; private exclusion data stays test-side.

This only downloads/extracts PDB text; no model fitting or scientific inference.
Final selected public sources are frozen in data/sources.json. Ordinary fresh
clones use scripts/download.sh, not this selection utility.
"""
import concurrent.futures,hashlib,importlib.util,json,random,string,urllib.request
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fetch_public',ROOT/'data/fetch.py')
fetch=importlib.util.module_from_spec(spec); spec.loader.exec_module(fetch)
def sequence(text):
 return tuple(s[17:20] for s in text.splitlines() if s.startswith('ATOM  ') and s[12:16].strip()=='CA')
def main():
 public=ROOT/'data/sources.json'; rows=json.loads(public.read_text())
 hidden=json.loads((Path(__file__).parent/'sources.json').read_text())
 used={r['pdb'] for r in rows+hidden}; seqs=set()
 for path in list((ROOT/'data/downloads/pdb').glob('*/*.pdb'))+list((Path(__file__).parent/'downloads').glob('*/*.pdb'))+list((ROOT/'data/pdb_smoke').glob('*/*.pdb')):
  if path.parent.name!='raw': seqs.add(sequence(path.read_text()))
 counts=Counter(r['split'] for r in rows)
 rng=random.Random(20261110); alphabet=string.digits+string.ascii_lowercase
 candidates=[]
 while len(candidates)<1800:
  pdb=rng.choice('123456789')+''.join(rng.choices(alphabet,k=3))
  if pdb not in used: used.add(pdb); candidates.append(pdb)
 rawdir=ROOT/'data/downloads/pdb/raw'; rawdir.mkdir(exist_ok=True)
 def download(pdb):
  path=rawdir/f'{pdb.upper()}.pdb'
  try:
   if not path.exists():
    with urllib.request.urlopen(f'https://files.rcsb.org/download/{pdb.upper()}.pdb',timeout=30) as response: path.write_bytes(response.read())
   return pdb,path.read_text()
  except Exception: return pdb,None
 # Batches keep acquisition bounded and preserve deterministic selection order.
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
  for offset in range(0,len(candidates),24):
   for pdb,text in pool.map(download,candidates[offset:offset+24]):
    if text is None: continue
    for chain in sorted({s[21:22] for s in text.splitlines() if s.startswith('ATOM  ')}):
     extracted,n=fetch.extract(text,chain)
     split='visible_short' if 64<=n<=192 else 'visible_long' if 256<=n<=512 else None
     seq=sequence(extracted)
     if split is None or counts[split]>=64 or seq in seqs: continue
     row={'pdb':pdb,'chain':chain,'residues':n,'sha256':hashlib.sha256(extracted.encode()).hexdigest(),'split':split}
     fetch.fetch(row,ROOT/'data/downloads/pdb'); rows.append(row); counts[split]+=1; seqs.add(seq)
     public.write_text(json.dumps(rows,indent=2)+'\n'); print('added',pdb,chain,split,n,dict(counts),flush=True)
     break
   if counts['visible_short']==counts['visible_long']==64: break
 if counts['visible_short']!=64 or counts['visible_long']!=64: raise RuntimeError('extension incomplete')
 print('public corpus frozen:',dict(counts),flush=True)
if __name__=='__main__': main()
