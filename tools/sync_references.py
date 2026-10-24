"""Derive browser references from the exact offline-validated portfolio CSV."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def build_references(root):
    candidate = root / 'examples/m3-best/candidate_NOT_VALIDATED.csv'
    report = json.loads((root / 'examples/m3-best/official-v17/official_validation.json').read_text())
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if digest != report['candidate_sha256']:
        raise ValueError('Source CSV differs from the evaluated candidate')
    accepted = {p['n'] for p in report['puzzles'] if p['reason'] == 'ok' and p['L'] is not None}
    if not {5, 10} <= accepted:
        raise ValueError('Required references are not accepted in the source report')
    with candidate.open(newline='') as f:
        rows = list(csv.DictReader(f))
    return dict(source='tAilorPack M3 portfolio snapshot', metric_version=17,
                candidate_sha256=digest,
                status='Saved reference only: offline validated, not submitted to Kaggle',
                packings={str(n): [dict(x=float(r['x']), y=float(r['y']), angle=float(r['angle']))
                                   for r in rows if int(r['n']) == n] for n in (5, 10)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / 'app/public/references.json'
    expected = build_references(root)
    if args.check:
        if json.loads(path.read_text()) != expected:
            raise ValueError('Browser references have drifted; run tools/sync_references.py')
        print('Browser references match the exact evaluated CSV.')
    else:
        path.write_text(json.dumps(expected, indent=2) + '\n')
        print('Browser references updated from the evaluated CSV.')


if __name__ == '__main__':
    main()
