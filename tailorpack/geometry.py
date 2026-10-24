"""Unit squares and float SAT. Touching is allowed; no overlap epsilon is used."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Square:
    x: float
    y: float
    angle: float = 0.0

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.x, self.y, self.angle)):
            raise ValueError("Coordinates and angles must be finite")

    def corners(self):
        c, s = math.cos(self.angle), math.sin(self.angle)
        return tuple((self.x + c*u - s*v, self.y + s*u + c*v)
                     for u, v in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)))


def overlaps(a: Square, b: Square) -> bool:
    """Positive interior intersection using separating axes (float approximation)."""
    pa, pb = a.corners(), b.corners()
    for square in (a, b):
        c, s = math.cos(square.angle), math.sin(square.angle)
        for ux, uy in ((c, s), (-s, c)):
            aa = [x*ux + y*uy for x, y in pa]
            bb = [x*ux + y*uy for x, y in pb]
            if max(aa) <= min(bb) or max(bb) <= min(aa):
                return False
    return True


def bounds(squares):
    if not squares:
        raise ValueError("Empty packing")
    points = [p for sq in squares for p in sq.corners()]
    xs, ys = zip(*points)
    return min(xs), min(ys), max(xs), max(ys)


def side(squares):
    x0, y0, x1, y1 = bounds(squares)
    return max(x1-x0, y1-y0)


def candidate_pairs(squares):
    """Spatial broad phase; each potentially intersecting AABB pair once."""
    buckets = {}
    for i, square in enumerate(squares):
        points = square.corners()
        xs, ys = zip(*points)
        cells = [(x, y) for x in range(math.floor(min(xs)), math.floor(max(xs))+1)
                 for y in range(math.floor(min(ys)), math.floor(max(ys))+1)]
        nearby = set()
        for cell in cells:
            nearby.update(buckets.get(cell, ()))
        for j in sorted(nearby):
            yield j, i
        for cell in cells:
            buckets.setdefault(cell, []).append(i)


def validate(n, squares, *, backend="spatial"):
    if type(n) is not int or not 1 <= n <= 1000 or len(squares) != n:
        raise ValueError("Require n in 1..1000 and exactly n squares")
    if backend not in ("spatial", "all-pairs"):
        raise ValueError("Unknown validation backend")
    pairs = candidate_pairs(squares) if backend == "spatial" else (
        (i, j) for i in range(n) for j in range(i+1, n))
    for i, j in pairs:
        if overlaps(squares[i], squares[j]):
            raise ValueError("Overlapping squares (local float check)")
    return side(squares)


def excess(n, length):
    if type(n) is not int or n < 1 or not math.isfinite(length) or length < math.sqrt(n):
        raise ValueError("Invalid n or side below area lower bound")
    return length/math.sqrt(n)-1
