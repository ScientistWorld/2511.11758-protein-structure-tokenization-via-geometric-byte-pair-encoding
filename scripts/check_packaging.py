"""Check fresh reference-only packaging without variants or private replay files."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    (ROOT / 'tmp').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as temporary:
        fresh = Path(temporary)
        (fresh / 'scripts').mkdir()
        (fresh / 'scoring').mkdir()
        shutil.copy2(ROOT / 'scripts/package_scores.py', fresh / 'scripts')
        history = json.loads((ROOT / 'scoring/reference.json').read_text())['_paper_reported']
        (fresh / 'scoring/reference.json').write_text(json.dumps({'_paper_reported': history}))
        (fresh / 'HARDENING.md').write_text('Keep the completed audit unchanged.\n')
        expected = {}
        for number, side in enumerate(('train', 'test')):
            # Synthetic aggregates only: no private per-input data leaves eval/test/.
            metrics = {experiment: {'rmsd': 2. + number, 'lddt': .7,
                                    'bpr': 44., 'vocab_size': 2107.}
                       for experiment in ('short_backbones', 'long_backbones')}
            record = {'methods': {'geobpe_reference': {'failed': False, 'metrics': metrics},
                                  'internal_baseline': {'failed': True, 'metrics': metrics}}}
            folder = fresh / 'eval' / side
            folder.mkdir(parents=True)
            (folder / 'ranking.json').write_text(json.dumps(record))
            expected[side] = record['methods']['geobpe_reference']['metrics']
        subprocess.run([sys.executable, str(fresh / 'scripts/package_scores.py')], check=True)
        assert json.loads((fresh / 'scoring/reference.json').read_text())['_paper_reported'] == history
        for side in ('train', 'test'):
            scores = json.loads((fresh / f'scoring/scores_{side}.json').read_text())
            for experiment, values in expected[side].items():
                assert scores['experiments'][experiment]['results'] == {'geobpe_reference': values}
        assert (fresh / 'HARDENING.md').read_text() == 'Keep the completed audit unchanged.\n'
    print('Fresh reference-only packaging passes without audit variants or replay artifacts.')


if __name__ == '__main__':
    main()
