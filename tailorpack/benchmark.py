"""Equal-budget multi-seed benchmark. No network or automatic submission."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import statistics
import time

from .export import write_candidate
from .geometry import validate
from .search import search
from .solvers import five_pattern


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ns", type=int, nargs="+", default=[5, 6, 7, 8, 10])
    p.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    p.add_argument("--evaluations", type=int, default=2000)
    p.add_argument("--initialization", choices=("m0", "axis-five"), default="m0")
    p.add_argument("--out", type=Path, default=Path("runs/search"))
    args = p.parse_args(argv)
    if not args.seeds or len(set(args.ns)) != len(args.ns) or any(not 1 <= n <= 1000 for n in args.ns):
        p.error("Require unique ns in 1..1000 and nonempty seeds")
    if len(set(args.seeds)) != len(args.seeds) or args.evaluations < 1:
        p.error("Require unique seeds and positive evaluations")
    args.out.mkdir(parents=True, exist_ok=True)
    rows, timings, best = [], [], {}
    for n in args.ns:
        for method in ("greedy", "annealing"):
            for seed in args.seeds:
                start = time.perf_counter()
                initial = five_pattern(0) if args.initialization == "axis-five" and n == 5 else None
                result = search(n, seed=seed, evaluations=args.evaluations, method=method, initial=initial)
                timings.append(dict(n=n, method=method, seed=seed, seconds=time.perf_counter()-start))
                row = asdict(result)
                del row["squares"]
                rows.append(dict(n=n, **row))
                if n not in best or result.best_side < validate(n, best[n]):
                    best[n] = list(result.squares)
            print(f"n={n} method={method} seeds={len(args.seeds)} complete", flush=True)
    summary = []
    for n in args.ns:
        for method in ("greedy", "annealing"):
            group = [r for r in rows if r["n"] == n and r["method"] == method]
            lengths = [r["best_side"] for r in group]
            summary.append(dict(n=n, method=method, best=min(lengths), median=statistics.median(lengths),
                                mean=statistics.mean(lengths), stdev=statistics.pstdev(lengths),
                                improved_runs=sum(r["best_side"] < r["initial_side"]-1e-7 for r in group)))
    h = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        h.update(path.name.encode()); h.update(path.read_bytes())
    report = dict(status="LOCAL_SEARCH_NOT_OFFICIALLY_VALIDATED", source_sha256=h.hexdigest(),
                  config=dict(ns=args.ns, seeds=args.seeds, evaluations=args.evaluations,
                              initialization=args.initialization),
                  initialization=("M0 experiment: grid except constructive five-square packing"
                                  if args.initialization == "m0" else "Axis-aligned corner/centre family for n=5; M0 otherwise"),
                  rows=rows, summary=summary)
    (args.out/"benchmark.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    (args.out/"timings.json").write_text(json.dumps(dict(python=platform.python_version(),
                                    platform=platform.platform(), rows=timings), indent=2)+"\n")
    write_candidate(args.out/"candidate_NOT_VALIDATED.csv", best)


if __name__ == "__main__":
    main()
