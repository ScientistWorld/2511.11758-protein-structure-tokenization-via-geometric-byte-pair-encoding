"""Deterministic inference replay on a fixed subset; no answers leave eval/test/."""
import json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def main():
 m=json.loads((ROOT/'checkpoints/submissions/geobpe_reference/manifest.json').read_text())
 run=HERE/'runs/geobpe_reference'; all_inputs=json.loads((run/'request.json').read_text()); inputs=all_inputs[:2]+all_inputs[64:66]
 req=run/'repeat_request.json'; out=run/'repeat_output.json'; req.write_text(json.dumps(inputs)+'\n')
 # Force a fresh application rather than exercising per-chain recovery.
 out.unlink(missing_ok=True); out.with_suffix('.resume.json').unlink(missing_ok=True)
 command=[s.format(request=str(req),output=str(out),model=str(run/'model.json')) for s in m['command']]
 with (run/'repeat.log').open('w') as log: subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 reference={r['id']:r for r in json.loads((run/'outputs.json').read_text())}
 repeated=json.loads(out.read_text()); assert len(repeated)==len(inputs)
 assert all(r==reference[r['id']] for r in repeated)
 print('Deterministic replay: four complete raw streams are identical.')
if __name__=='__main__': main()
