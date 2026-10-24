"""Checkpointed parallel puzzle search with a persistent best-packing catalogue."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import json
from pathlib import Path
import time

from .export import write_candidate
from .geometry import Square, validate
from .search import atomic_json, engine_hash, search
from .solvers import experiment


def read_packings(path):
    groups = {}
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != ["id", "n", "square_id", "x", "y", "angle"]:
            raise ValueError("Unexpected candidate header")
        for i, row in enumerate(reader):
            n, sid = int(row["n"]), int(row["square_id"])
            if int(row["id"]) != i or sid != len(groups.get(n, [])):
                raise ValueError("Invalid row or square identifiers")
            groups.setdefault(n, []).append(Square(*(float(row[k]) for k in ("x", "y", "angle"))))
    for n, squares in groups.items():
        validate(n, squares)
    return groups


def run_job(job):
    path = Path(job["checkpoint"])
    initial = [Square(*s) for s in job["initial"]]
    cached = False
    if path.exists():
        state = json.loads(path.read_text())
        # A resume uses its frozen initial packing, not a later catalogue winner.
        initial = [Square(*s) for s in state["initial"]]
        cached = state["step"] == job["evaluations"]
    start = time.perf_counter()
    result = search(job["n"], seed=job["seed"], evaluations=job["evaluations"],
                    method=job["method"], initial=initial, checkpoint=path,
                    checkpoint_every=job["checkpoint_every"])
    return dict(n=job["n"], seed=job["seed"], method=job["method"],
                initial_side=result.initial_side, best_side=result.best_side,
                squares=[[s.x, s.y, s.angle] for s in result.squares],
                evaluations=result.evaluations, cached=cached, seconds=time.perf_counter()-start)


def run(ns, seeds, evaluations, workers, out, warm_start=None, checkpoint_every=25, method="annealing"):
    if not ns or len(set(ns)) != len(ns) or any(type(n) is not int or not 1 <= n <= 1000 for n in ns):
        raise ValueError("Unique ns in 1..1000 required")
    if not seeds or len(set(seeds)) != len(seeds) or evaluations < 1 or not 1 <= workers <= 8:
        raise ValueError("Unique seeds, positive budget and 1..8 workers required")
    if method not in ("greedy", "annealing") or checkpoint_every < 1:
        raise ValueError("Invalid method/checkpoint interval")
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    config = dict(ns=ns, seeds=seeds, evaluations=evaluations, method=method,
                  engine_sha256=engine_hash())
    manifest = out/"manifest.json"
    if manifest.exists() and json.loads(manifest.read_text()) != config:
        raise ValueError("Run configuration/source changed; choose a new output directory")
    atomic_json(manifest, config)
    best = {n: experiment(n) for n in ns}
    catalogue = out/"best.json"
    sources = []
    if warm_start is not None:
        sources.append(read_packings(warm_start))
    if catalogue.exists():
        sources.append({int(n): [Square(*s) for s in value["squares"]]
                        for n, value in json.loads(catalogue.read_text()).items()})
    for source in sources:
        for n in set(ns) & source.keys():
            if validate(n, source[n]) < validate(n, best[n]):
                best[n] = source[n]
    jobs = [dict(n=n, seed=seed, method=method, evaluations=evaluations,
                 checkpoint_every=checkpoint_every, checkpoint=str(out/"checkpoints"/f"{n}-{seed}.json"),
                 initial=[[s.x, s.y, s.angle] for s in best[n]]) for n in ns for seed in seeds]
    rows = []

    def consume(iterator):
        for row in iterator:
            n = row["n"]
            candidate = [Square(*s) for s in row.pop("squares")]
            if validate(n, candidate) < validate(n, best[n]):
                best[n] = candidate
            rows.append(row)
            # Only the parent writes the catalogue, avoiding concurrent updates.
            atomic_json(catalogue, {str(k): dict(side=validate(k, v), squares=[[s.x,s.y,s.angle] for s in v])
                                   for k, v in sorted(best.items())})
            print(f'n={n} seed={row["seed"]} side={row["best_side"]:.10f} cached={row["cached"]}', flush=True)

    started = time.perf_counter()
    if workers == 1:
        consume(map(run_job, jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            consume(pool.map(run_job, jobs))
    report = dict(status="LOCAL_SCALE_RUN_NOT_OFFICIALLY_VALIDATED", config=config, workers=workers,
                  elapsed_seconds=time.perf_counter()-started, cached_jobs=sum(r["cached"] for r in rows), rows=rows)
    atomic_json(out/"scale_report.json", report)
    write_candidate(out/"candidate_NOT_VALIDATED.csv", best)
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ns", nargs="+", type=int, default=[10, 100, 250, 500, 1000])
    p.add_argument("--seeds", nargs="+", type=int, default=[0])
    p.add_argument("--evaluations", type=int, default=100)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--checkpoint-every", type=int, default=25)
    p.add_argument("--warm-start", type=Path)
    p.add_argument("--method", choices=["greedy", "annealing"], default="annealing")
    p.add_argument("--out", type=Path, default=Path("runs/scale"))
    a = p.parse_args(argv)
    run(a.ns, a.seeds, a.evaluations, a.workers, a.out, a.warm_start, a.checkpoint_every, a.method)


if __name__ == "__main__":
    main()
