"""Kaggle-shaped candidate CSV. Export does not certify official acceptance."""
import csv
from .geometry import validate

HEADER = ("id", "n", "square_id", "x", "y", "angle")


def write_candidate(path, packings):
    if not packings:
        raise ValueError("No puzzles")
    # Validate all puzzles before opening/truncating the output.
    for n, squares in packings.items():
        validate(n, squares)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(HEADER)
        row_id = 0
        for n in sorted(packings):
            for square_id, sq in enumerate(packings[n]):
                writer.writerow((row_id, n, square_id, *(format(v, ".17g")
                                  for v in (sq.x, sq.y, sq.angle))))
                row_id += 1
