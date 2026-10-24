"""Measure exhaustive versus spatial geometry without changing algorithms."""
import argparse
import json
from pathlib import Path
import platform
import statistics
import time

from .geometry import candidate_pairs, validate
from .search import engine_hash, repair
from .solvers import grid


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ns", nargs="+", type=int, default=[10,100,250,500,1000])
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--out", type=Path, default=Path("runs/profile-scale.json"))
    a = p.parse_args(argv)
    if a.repeats < 1:
        p.error("positive repeats required")
    rows = []
    for n in a.ns:
        packing = grid(n)
        repaired = {}
        record = dict(n=n, total_pairs=n*(n-1)//2, validation_spatial_pairs=sum(1 for _ in candidate_pairs(packing)))
        for operation in ("validate", "repair"):
            for backend in ("all-pairs", "spatial"):
                samples = []
                for _ in range(a.repeats):
                    start = time.perf_counter()
                    result = validate(n, packing, backend=backend) if operation == "validate" else repair(packing, backend=backend)
                    samples.append(time.perf_counter()-start)
                record[f"{operation}_{backend}_median_seconds"] = statistics.median(samples)
                if operation == "repair":
                    repaired[backend] = result
            record[f"{operation}_speedup"] = record[f"{operation}_all-pairs_median_seconds"]/record[f"{operation}_spatial_median_seconds"]
        if repaired["all-pairs"] != repaired["spatial"]:
            raise ValueError("Optimized repair differs from reference")
        record["repair_equal"] = True
        rows.append(record)
        print(json.dumps(record), flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(dict(engine_sha256=engine_hash(), platform=platform.platform(),
                                     python=platform.python_version(), repeats=a.repeats,
                                     workload="axis-aligned grid per n; not arbitrary dense inputs", rows=rows), indent=2)+"\n")


if __name__ == "__main__":
    main()
