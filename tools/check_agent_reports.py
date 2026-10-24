"""Verify saved agent controls; no model call and no official certification."""
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
    report = json.loads((folder / 'report.json').read_text())
    for name, digest in report['sources'].items():
        path = (ROOT / 'app' / name).resolve()
        if not path.is_relative_to(ROOT / 'app') or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Agent report source mismatch')
    config = report['config']
    if report['modelExecuted'] or report['inferenceAttempts'] or report['inferenceResponses']:
        raise ValueError('Saved controls must not claim model inference')
    if report['provider'] not in ('scripted_round_robin_control', 'scripted_v1_control'):
        raise ValueError('Expected a labelled scripted control')
    if sum(t['budget'] for t in report['trials']) != report['usedProposals'] or report['usedProposals'] > config['totalBudget']:
        raise ValueError('Proposal ledger mismatch')
    keys = set()
    for trial in report['trials']:
        key = (trial['strategy'], trial['seed'], trial['budget'])
        if key in keys or trial['seed'] not in config['seeds'] or not 1 <= trial['budget'] <= config['maxTrial']:
            raise ValueError('Invalid or duplicate trial')
        keys.add(key)
    candidate = folder / 'candidate_NOT_VALIDATED.csv'
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != report['candidate_sha256']:
        raise ValueError('Candidate hash mismatch')
    with candidate.open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    if any(int(r['id']) != i or int(r['square_id']) != i or int(r['n']) != config['n'] for i, r in enumerate(rows)):
        raise ValueError('CSV ID or coverage mismatch')
    length = validate(config['n'], [Square(float(r['x']), float(r['y']), float(r['angle'])) for r in rows])
    if abs(length - report['bestL']) > 1e-10 or length > report['initialL']:
        raise ValueError('Saved result does not match the CSV')
    print(f"Agent control checked: {report['provider']}; n={config['n']}; L={length}; no model inference")


if __name__ == '__main__':
    for name in ('agent-v03-control', 'agent-v03-fixed'):
        check(ROOT / 'examples' / name)
