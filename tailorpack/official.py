"""Offline adapter for the exact, downloaded Kaggle metric v17.

No metric code or competition data is distributed here. The snapshot hash is
checked before importing any downloaded Python. Requires optional dependencies.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import csv
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile

from .export import HEADER
from .solvers import grid

SOURCE_SHA256 = "312458227c78f56bd5e2eec3dc5fbb8787989422bbf72ce66c3c290048e89733"
SAMPLE_SHA256 = "a7f736d6cc72975459732a15d6ce6ae6588ad97d0c84f4d26905fd31ec09c74c"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extract_source(notebook):
    data = json.loads(Path(notebook).read_text(encoding="utf-8"))
    source = "\n\n".join("".join(cell["source"]) for cell in data["cells"]
                         if cell["cell_type"] == "code")
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA256:
        raise ValueError("Metric source differs from reviewed v17. Review it before updating the hash.")
    return source


@contextmanager
def metric_snapshot(notebook):
    source = extract_source(notebook)
    name = "tailorpack_kaggle_metric_v17"
    with tempfile.TemporaryDirectory() as directory:
        Path(directory, name+".py").write_text(source, encoding="utf-8")
        # Importable file also supports the official multiprocessing workers.
        sys.path.insert(0, directory)
        try:
            yield importlib.import_module(name)
        finally:
            sys.path.remove(directory)
            sys.modules.pop(name, None)


def inspect_sample(path):
    if sha256(path) != SAMPLE_SHA256:
        raise ValueError("Sample differs from reviewed download; inspect the new version first")
    counts = Counter()
    baseline_prefix = []
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != HEADER:
            raise ValueError("Unexpected sample header")
        for row_id, row in enumerate(reader):
            n = int(row["n"])
            if not 1 <= n <= 1000 or int(row["id"]) != row_id or int(row["square_id"]) != counts[n]:
                raise ValueError("Unexpected sample identifiers")
            counts[n] += 1
            if n <= 16:
                baseline_prefix.append(row)
    if set(counts) != set(range(1, 1001)) or any(counts[n] != n for n in counts):
        raise ValueError("Incomplete sample puzzles")
    for row in baseline_prefix:
        expected = grid(int(row["n"]))[int(row["square_id"])]
        if tuple(float(row[k]) for k in ("x", "y", "angle")) != (expected.x, expected.y, expected.angle):
            raise ValueError("Sample prefix differs from local grid")
    return dict(sha256=sha256(path), rows=sum(counts.values()), puzzles=len(counts),
                header=list(HEADER), grid_prefix_matches_through_n=16)


@contextmanager
def in_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def validate_candidate(notebook, sample, candidate, out):
    import mpmath
    import pandas as pd

    notebook, sample, candidate = (Path(p).resolve() for p in (notebook, sample, candidate))
    out = Path(out).resolve()
    sample_summary = inspect_sample(sample)
    # Preserve decimal strings; pandas float inference would lose literal digits.
    submission = pd.read_csv(candidate, dtype=str, keep_default_na=False)
    if tuple(submission.columns) != HEADER or list(submission["id"]) != [str(i) for i in range(len(submission))]:
        raise ValueError("Candidate must have exact header and consecutive unique row IDs")
    solution = pd.DataFrame({"id": list(range(1000)), "n": list(range(1, 1001))})
    out.mkdir(parents=True, exist_ok=True)
    with metric_snapshot(notebook) as metric:
        puzzles = metric._parse_submission_csv(submission.drop(columns=["id"]).to_csv(index=False))
        diagnostics = [metric.evaluate_single_puzzle(n, rows) for n, rows in sorted(puzzles.items())]
        if any(reason != "ok" or length is None for _, _, length, reason in diagnostics):
            raise ValueError(f"Official metric rejected a submitted puzzle: {diagnostics}")
        # Call the unchanged backend entry point, including its multiprocessing
        # and details output. The score universe is explicitly all 1000 puzzles.
        with in_directory(out):
            total = metric.score(solution, submission, "id")
        omitted_penalty = sum(metric.infeasible_score(n) for n in range(1, 1001) if n not in puzzles)
        subset = sum(score for _, score, _, _ in diagnostics)
        if not math.isclose(total, subset+omitted_penalty, abs_tol=1e-10):
            raise ValueError("Full score disagrees with subset plus missing-puzzle penalties")
    report = dict(status="VALIDATED_OFFLINE_WITH_KAGGLE_METRIC_V17_NOT_SUBMITTED",
                  metric_url="https://www.kaggle.com/code/metric/squares-in-squares",
                  metric_kernel_version=360167936, metric_source_sha256=SOURCE_SHA256,
                  notebook_sha256=sha256(notebook), candidate_sha256=sha256(candidate),
                  sample=sample_summary,
                  environment=dict(python=platform.python_version(), pandas=pd.__version__, mpmath=mpmath.__version__),
                  submitted_puzzles=len(puzzles), scoring_universe=1000, subset_score=subset,
                  omitted_penalty=omitted_penalty, full_score_offline=total,
                  puzzles=[dict(n=n, score=score, L=length, reason=reason)
                           for n, score, length, reason in diagnostics])
    (out/"official_validation.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline validation against the pinned official metric; never submits")
    p.add_argument("--notebook", required=True, type=Path)
    p.add_argument("--sample", required=True, type=Path)
    p.add_argument("--candidate", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    report = validate_candidate(args.notebook, args.sample, args.candidate, args.out)
    print(json.dumps({key: report[key] for key in ("status", "submitted_puzzles", "subset_score", "full_score_offline")}))


if __name__ == "__main__":
    main()
