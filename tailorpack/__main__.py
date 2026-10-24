import argparse
import hashlib
import json
import platform
from pathlib import Path
from . import __version__
from .export import write_candidate
from .geometry import excess, validate
from .render import svg
from .solvers import experiment, grid


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a local experiment, NOT an official submission")
    parser.add_argument("--max-n", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trials", type=int, default=64)
    parser.add_argument("--margin", type=float, default=1e-9)
    parser.add_argument("--out", type=Path, default=Path("runs/demo"))
    args = parser.parse_args(argv)
    if not 1 <= args.max_n <= 1000:
        parser.error("--max-n must be in 1..1000")
    if args.trials < 1 or not 0 < args.margin < float("inf"):
        parser.error("--trials and finite --margin must be positive")
    packings, rows = {}, []
    for n in range(1, args.max_n+1):
        baseline = validate(n, grid(n))
        packing = experiment(n, args.seed, args.trials, args.margin)
        length = validate(n, packing)
        packings[n] = packing
        rows.append(dict(n=n, grid_side=baseline, experiment_side=length,
                         grid_excess=excess(n, baseline), experiment_excess=excess(n, length)))
    config = dict(max_n=args.max_n, seed=args.seed, trials=args.trials, margin=args.margin)
    source = hashlib.sha256()
    for p in sorted(Path(__file__).parent.glob("*.py")):
        source.update(p.name.encode()); source.update(p.read_bytes())
    result = dict(status="LOCAL_PROTOTYPE_NOT_OFFICIALLY_VALIDATED", version=__version__,
                  config=config, source_sha256=source.hexdigest(), rows=rows,
                  local_subset_sum=sum(r["experiment_excess"] for r in rows),
                  grid_subset_sum=sum(r["grid_excess"] for r in rows))
    args.out.mkdir(parents=True, exist_ok=True)
    write_candidate(args.out/"candidate_NOT_VALIDATED.csv", packings)
    (args.out/"results.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    environment = dict(python=platform.python_version(), platform=platform.platform())
    (args.out/"environment.json").write_text(json.dumps(environment, indent=2)+"\n")
    if 5 in packings:
        (args.out/"packing_5.svg").write_text(svg(packings[5]))
    print(json.dumps({"status": result["status"], "output": str(args.out),
                      "subset_improvement": result["grid_subset_sum"]-result["local_subset_sum"]}))


if __name__ == "__main__":
    main()
