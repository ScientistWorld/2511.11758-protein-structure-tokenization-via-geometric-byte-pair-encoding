"""Fetch fixed public PDB sources and extract complete, continuous N/CA/C chains."""
import argparse,concurrent.futures,hashlib,json,math,time,urllib.request
from pathlib import Path
AMINO=set('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split())
def extract(text,chain):
 residues={}
 for line in text.splitlines():
  if line.startswith('ENDMDL'): break
  if not line.startswith('ATOM  ') or line[21:22]!=chain or line[16:17] not in (' ','A') or line[17:20] not in AMINO: continue
  atom=line[12:16].strip()
  if atom not in ('N','CA','C'): continue
  key=(line[22:26],line[26:27]); residues.setdefault(key,{})[atom]=line
 segments=[]; seg=[]
 for atoms in residues.values():
  if len(atoms)!=3:
   if seg: segments.append(seg); seg=[]
   continue
  if seg:
   a=[float(seg[-1]['C'][i:i+8]) for i in (30,38,46)]; b=[float(atoms['N'][i:i+8]) for i in (30,38,46)]
   d=math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
   if not .9<d<1.8: segments.append(seg); seg=[]
  seg.append(atoms)
 if seg: segments.append(seg)
 seg=max(segments,key=len,default=[])
 lines=[]
 for r,atoms in enumerate(seg,1):
  for atom in ('N','CA','C'):
   s=atoms[atom]; lines.append(f'ATOM  {len(lines)+1:5d} {s[12:16]} {s[17:20]} A{r:4d}    {s[30:54]}  1.00 20.00          {atom[0]:>2s}')
 return '\n'.join(lines+['TER','END','']),len(seg)
def fetch(row,root):
 root=Path(root); raw=root/'raw'/f"{row['pdb'].upper()}.pdb"; raw.parent.mkdir(parents=True,exist_ok=True)
 if not raw.exists():
  for retry in range(3):
   try:
    with urllib.request.urlopen(f"https://files.rcsb.org/download/{row['pdb'].upper()}.pdb",timeout=45) as response: content=response.read()
    raw.write_bytes(content); break
   except Exception:
    if retry==2: raise
    time.sleep(1)
 text,n=extract(raw.read_text(),row['chain']); digest=hashlib.sha256(text.encode()).hexdigest()
 if 'sha256' in row and row['sha256']!=digest: raise ValueError(f"Changed upstream structure: {row['pdb']}")
 folder=root/row.get('split','pool'); folder.mkdir(parents=True,exist_ok=True)
 path=folder/f"{row['pdb']}_{row['chain']}.pdb"; path.write_text(text)
 return dict(row,residues=n,sha256=digest)
def main():
 p=argparse.ArgumentParser(); p.add_argument('--manifest',default='eval/test/sources.json'); p.add_argument('--root',default='eval/test/downloads'); a=p.parse_args()
 rows=json.loads(Path(a.manifest).read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
  list(pool.map(lambda row:fetch(row,a.root),rows))
if __name__=='__main__': main()
