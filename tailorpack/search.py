"""General feasible search: translations, rotations and uniform centre repair.

Repair is analytical along the four SAT axes of each pair. Float feasibility
still needs independent checking and the official metric before certification.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random

from .geometry import Square, bounds, side, validate
from .solvers import experiment


def repair(squares, margin=1e-8, *, backend="spatial"):
    """Scale centres uniformly until every pair has a separating axis.

    For each pair, scale >= min_axis(sum(projected half widths)/distance).
    The maximum of these pair thresholds suffices for all pairs. Square sizes
    and angles stay fixed. Return None for coincident centres/unsafe expansion.
    """
    if not squares or not math.isfinite(margin) or margin <= 0:
        raise ValueError("Nonempty packing and positive finite margin required")
    if backend not in ("spatial", "all-pairs"):
        raise ValueError("Unknown repair backend")
    axes = [(math.cos(s.angle), math.sin(s.angle)) for s in squares]

    def pair_threshold(i, j):
        a, b = squares[i], squares[j]
        ca, sa = axes[i]
        cb, sb = axes[j]
        dx, dy = a.x-b.x, a.y-b.y
        threshold = math.inf
        for ux, uy in ((ca, sa), (-sa, ca), (cb, sb), (-sb, cb)):
            distance = abs(dx*ux+dy*uy)
            if distance > 1e-14:
                support = .5*(abs(ca*ux+sa*uy)+abs(-sa*ux+ca*uy)
                               +abs(cb*ux+sb*uy)+abs(-sb*ux+cb*uy))
                threshold = min(threshold, (support+margin)/distance)
        return threshold

    scale = pair_threshold(1, 0) if len(squares) > 1 else 0.0
    if not math.isfinite(scale):
        return None
    if backend == "all-pairs" or len(squares) < 3 or scale <= 0:
        pairs = ((i, j) for i in range(len(squares)) for j in range(i))
    else:
        # One of a square's orthogonal axes projects distance >= r/sqrt(2).
        # Both squares' combined half widths <= sqrt(2), hence every pair
        # threshold <= (2+sqrt(2)*margin)/r. Far pairs cannot exceed scale.
        radius = (2+math.sqrt(2)*margin)/scale*(1+1e-12)
        buckets = {}
        nearby_pairs = []
        for i, sq in enumerate(squares):
            cell = math.floor(sq.x/radius), math.floor(sq.y/radius)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nearby_pairs.extend((i, j) for j in buckets.get((cell[0]+dx, cell[1]+dy), ()))
            buckets.setdefault(cell, []).append(i)
        pairs = nearby_pairs
    for i, j in pairs:
        scale = max(scale, pair_threshold(i, j))
    if not math.isfinite(scale) or scale > 1e6:
        return None
    if len(squares) == 1:
        scale = 1.0
    # Recentring avoids magnifying large irrelevant absolute offsets.
    cx = sum(s.x for s in squares)/len(squares)
    cy = sum(s.y for s in squares)/len(squares)
    result = [Square((s.x-cx)*scale, (s.y-cy)*scale, s.angle) for s in squares]
    x0, y0, _, _ = bounds(result)
    return [Square(s.x-x0, s.y-y0, s.angle) for s in result]


@dataclass(frozen=True)
class SearchResult:
    squares: tuple[Square, ...]
    initial_side: float
    best_side: float
    evaluations: int
    accepted_moves: int
    seed: int
    method: str


def engine_hash():
    digest = hashlib.sha256()
    for name in ("geometry.py", "solvers.py", "search.py"):
        digest.update(Path(__file__).with_name(name).read_bytes())
    return digest.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name+".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True, allow_nan=False)+"\n")
    os.replace(temporary, path)


def _tuples(value):
    return tuple(_tuples(x) for x in value) if isinstance(value, list) else value


def _pack(squares):
    return [[s.x, s.y, s.angle] for s in squares]


def search(n, *, seed=42, evaluations=2000, method="annealing", initial=None, backend="spatial",
           checkpoint=None, checkpoint_every=100, stop_after=None):
    if type(evaluations) is not int or evaluations < 1:
        raise ValueError("evaluations must be a positive integer")
    if method not in ("greedy", "annealing"):
        raise ValueError("method must be greedy or annealing")
    if backend not in ("spatial", "all-pairs") or checkpoint_every < 1:
        raise ValueError("Invalid backend/checkpoint interval")
    if stop_after is not None and (type(stop_after) is not int or stop_after < 1):
        raise ValueError("stop_after must be a positive integer")
    current = list(experiment(n) if initial is None else initial)
    initial_side = validate(n, current)
    best, best_side = list(current), initial_side
    current_side = initial_side
    rng = random.Random(seed)
    accepted = 0
    config = dict(n=n, seed=seed, evaluations=evaluations, method=method, backend=backend,
                  engine_sha256=engine_hash())
    initial_pack = _pack(current)
    start_step = 0
    if checkpoint is not None and Path(checkpoint).exists():
        state = json.loads(Path(checkpoint).read_text())
        if state["config"] != config:
            raise ValueError("Checkpoint configuration/source mismatch; use a new output directory")
        if initial is not None and state["initial"] != initial_pack:
            raise ValueError("Checkpoint initial packing mismatch")
        current = [Square(*s) for s in state["current"]]
        best = [Square(*s) for s in state["best"]]
        current_side, best_side = validate(n, current), validate(n, best)
        initial_pack, initial_side = state["initial"], state["initial_side"]
        start_step, accepted = state["step"], state["accepted"]
        if not 0 <= start_step <= evaluations:
            raise ValueError("Invalid checkpoint progress")
        rng.setstate(_tuples(state["rng"]))

    def save(step):
        if checkpoint is not None:
            atomic_json(checkpoint, dict(config=config, step=step, accepted=accepted,
                        initial=initial_pack, initial_side=initial_side,
                        current=_pack(current), best=_pack(best), rng=rng.getstate()))

    end_step = evaluations if stop_after is None else min(evaluations, start_step+stop_after)
    for step in range(start_step, end_step):
        fraction = step/max(1, evaluations-1)
        # Repeated cooling cycles let the search revisit larger moves.
        cycle = (fraction*4) % 1 if fraction < 1 else 1
        temperature = .20*(1-cycle)**2 + .00005
        move_size = .12*(1-cycle)+.005
        proposal = list(current)
        i = rng.randrange(n)
        sq = proposal[i]
        proposal[i] = Square(sq.x+rng.gauss(0, move_size),
                             sq.y+rng.gauss(0, move_size),
                             (sq.angle+rng.gauss(0, move_size*2)) % (math.pi/2))
        candidate = repair(proposal, backend=backend)
        if candidate is None:
            if (step+1) % checkpoint_every == 0:
                save(step+1)
            continue
        length = side(candidate)
        delta = length-current_side
        # Consume the acceptance draw in both methods for comparable RNG budgets.
        draw = rng.random()
        if delta <= 0 or (method == "annealing" and draw < math.exp(-delta/temperature)):
            current, current_side = candidate, length
            accepted += 1
        if length < best_side:
            # Only retain independently locally validated feasible incumbents.
            validate(n, candidate)
            best, best_side = candidate, length
        if (step+1) % checkpoint_every == 0:
            save(step+1)
    validate(n, best)
    save(end_step)
    return SearchResult(tuple(best), initial_side, best_side, end_step, accepted, seed, method)
