"""Deterministic inference replay on a fixed subset; no answers leave eval/test/."""
import json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def main():
 m=json.loads((ROOT/'checkpoints/submissions/geobpe_reference/manifest.json').read_text())
 run=HERE/'runs/geobpe_reference'; inputs=json.loads((run/'request.json').read_text())[:4]
 req=run/'repeat_request.json'; out=run/'repeat_output.json'; req.write_text(json.dumps(inputs)+'\n')
 command=[s.format(request=str(req),output=str(out),model=str(run/'model.json')) for s in m['command']]
 with (run/'repeat.log').open('w') as log: subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 reference={r['id']:r for r in json.loads((run/'outputs.json').read_text())}
 repeated=json.loads(out.read_text()); assert len(repeated)==len(inputs)
 assert all(r==reference[r['id']] for r in repeated)
 print('Deterministic replay: four complete raw streams are identical.')
if __name__=='__main__': main()
