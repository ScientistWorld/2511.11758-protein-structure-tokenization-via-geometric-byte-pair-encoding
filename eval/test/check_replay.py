"""Measure decoded CPU-host replay noise on paired inputs, without retraining."""
import json,subprocess
from pathlib import Path
import evaluate as evaluator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def main():
 m=json.loads((ROOT/'checkpoints/submissions/geobpe_reference/manifest.json').read_text())
 run=HERE/'runs/geobpe_reference'; all_inputs=json.loads((run/'request.json').read_text()); inputs=all_inputs[:2]+all_inputs[64:66]
 req=run/'repeat_request.json'; out=run/'repeat_output.json'; req.write_text(json.dumps(inputs)+'\n')
 out.unlink(missing_ok=True); out.with_suffix('.resume.json').unlink(missing_ok=True)
 command=[s.format(request=str(req),output=str(out),model=str(run/'model.json')) for s in m['command']]
 with (run/'repeat.log').open('w') as log: subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 reference={r['id']:r for r in json.loads((run/'outputs.json').read_text())}
 repeated=json.loads(out.read_text()); assert len(repeated)==len(inputs)
 model=evaluator.load_model(json.loads((run/'model.json').read_text()))[0]
 scales=json.loads((HERE/'ranking.json').read_text())['normalization']; by_id={r['id']:r for r in inputs}
 differences={}; bounds={e:{'rmsd':0.,'lddt':0.,'bpr':0.} for e in evaluator.EXPERIMENTS}
 for row in repeated:
  rid=row['id']; native=evaluator.target(by_id[rid]['path']); n=len(native)//3
  a,bits_a=evaluator.decode(reference[rid],model,n); b,bits_b=evaluator.decode(row,model,n)
  qa=evaluator.quality(native,a); qb=evaluator.quality(native,b)
  exp='short_backbones' if n<=192 else 'long_backbones'
  delta={'rmsd':abs(qa[0]-qb[0]),'lddt':abs(qa[1]-qb[1]),'bpr':abs(bits_a-bits_b)/n}
  differences[rid]=delta
  for metric,value in delta.items(): bounds[exp][metric]=max(bounds[exp][metric],value)
 noise=sum(evaluator.WEIGHTS[e]*abs(evaluator.METRICS[m][1])*v/scales[e][m] for e,values in bounds.items() for m,v in values.items() if scales[e][m]>1e-12)
 report={'exact_raw_replay':all(r==reference[r['id']] for r in repeated),'paired_inputs':len(inputs),'absolute_metric_differences':differences,'maximum_difference_by_experiment':bounds,'conservative_normalized_rank_noise':noise,'note':'Four-input numerical replay diagnostic across CPU hosts, not a population confidence bound.'}
 evaluator.write_json(HERE/'replay_noise.json',report)
 print('Decoded numerical replay rank-noise diagnostic:',noise,flush=True)
if __name__=='__main__': main()
