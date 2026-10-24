"""Check the saved v0.2 benchmark and independently validate its CSV in Python."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tailorpack.geometry import Square, validate


def check(folder):
    folder = Path(folder)
    report = json.loads((folder / 'benchmark.json').read_text())
    config = report['config']
    for name, digest in report['sources'].items():
        path = ROOT / 'app/public' / name
        if path.parent != ROOT / 'app/public' or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Benchmark source mismatch: {name}')
    keys = set()
    for row in report['rows']:
        key = (row['n'], row['start'], row['seed'], row['strategy'])
        if key in keys or row['step'] != config['budget']:
            raise ValueError('Duplicate trial or unequal proposal budget')
        keys.add(key)
    for n in config['ns']:
        starts = {start for size, start, _, _ in keys if size == n}
        for start in starts:
            for seed in config['seeds']:
                for strategy in ('v1', 'v2'):
                    if (n, start, seed, strategy) not in keys:
                        raise ValueError('Unpaired trial')
    candidate = folder / 'candidate_NOT_VALIDATED.csv'
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if digest != config['candidate_sha256']:
        raise ValueError('Candidate hash mismatch')
    packs = {}
    with candidate.open(newline='') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ['id', 'n', 'square_id', 'x', 'y', 'angle']:
            raise ValueError('CSV schema mismatch')
        for i, row in enumerate(reader):
            n = int(row['n'])
            pack = packs.setdefault(n, [])
            if int(row['id']) != i or int(row['square_id']) != len(pack):
                raise ValueError('CSV IDs mismatch')
            pack.append(Square(float(row['x']), float(row['y']), float(row['angle'])))
    if set(packs) != set(config['ns']):
        raise ValueError('Candidate coverage mismatch')
    official = folder / 'official-v17/official_validation.json'
    if official.exists():
        certification = json.loads(official.read_text())
        if certification['candidate_sha256'] != digest or {p['n'] for p in certification['puzzles']} != set(packs):
            raise ValueError('Official report does not match this CSV')
        if any(p['reason'] != 'ok' or p['L'] is None for p in certification['puzzles']):
            raise ValueError('Official report contains a rejected puzzle')
    return dict(status='INDEPENDENT_PYTHON_FLOAT_CHECK_NOT_OFFICIAL' , candidate_sha256=digest,
                puzzles=[dict(n=n, L=validate(n, pack)) for n, pack in packs.items()])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=ROOT / 'examples/web-v02')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = check(args.folder)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(f"Web benchmark checked: {len(result['puzzles'])} puzzles; independent Python float validation")
