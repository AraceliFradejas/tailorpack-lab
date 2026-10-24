"""Baseline and deliberately small, seeded, one-parameter experiment."""
import math
import random
from .geometry import Square, validate


def grid(n):
    if type(n) is not int or not 1 <= n <= 1000:
        raise ValueError("n must be in 1..1000")
    width = math.isqrt(n-1)+1
    return [Square(i % width+.5, i // width+.5) for i in range(n)]


def five_pattern(angle, margin=1e-9):
    """Four axis-aligned corner squares plus a rotated central square.

    For theta in [0, pi/4], separation from each corner is guaranteed by
    its central-square diagonal axis when L >= 2 + 1/(cos(theta)+sin(theta)).
    This is a feasible family, not a claim of global optimality.
    """
    if not math.isfinite(angle) or not 0 <= angle <= math.pi/4:
        raise ValueError("angle must be in [0, pi/4]")
    if not math.isfinite(margin) or margin <= 0:
        raise ValueError("positive finite margin required")
    length = 2 + 1/(math.cos(angle)+math.sin(angle)) + margin
    lo, hi = .5, length-.5
    return [Square(x, y) for x, y in ((lo, lo), (hi, lo), (lo, hi), (hi, hi))] + [
        Square(length/2, length/2, angle)]


def experiment(n, seed=42, trials=64, margin=1e-9):
    if type(trials) is not int or trials < 1:
        raise ValueError("trials must be a positive integer")
    if not math.isfinite(margin) or margin <= 0:
        raise ValueError("positive finite margin required")
    best = grid(n)
    best_length = validate(n, best)
    if n != 5:
        return best
    rng = random.Random(seed)
    # Endpoints make the baseline/45-degree ablation explicit. trials is
    # the number of additional random angles, not a runtime budget.
    angles = [0.0, math.pi/4] + [rng.uniform(0, math.pi/4) for _ in range(trials)]
    for angle in angles:
        candidate = five_pattern(angle, margin)
        length = validate(n, candidate)
        if length < best_length:
            best, best_length = candidate, length
    return best
