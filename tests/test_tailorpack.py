import csv
import json
import math
from pathlib import Path
import tempfile
import unittest
from tailorpack.__main__ import main
from tailorpack.export import HEADER, write_candidate
from tailorpack.geometry import Square, excess, overlaps, side, validate
from tailorpack.solvers import experiment, five_pattern, grid


class GeometryTests(unittest.TestCase):
    def test_contact_and_gap(self):
        a = Square(0, 0)
        self.assertFalse(overlaps(a, Square(1, 0)))
        self.assertFalse(overlaps(a, Square(1, 1)))
        self.assertFalse(overlaps(a, Square(1.001, 0)))
        self.assertTrue(overlaps(a, Square(1-1e-12, 0)))

    def test_rotated_overlap_and_separation(self):
        self.assertTrue(overlaps(Square(0, 0, .3), Square(.4, .1, -.4)))
        self.assertFalse(overlaps(Square(0, 0, .3), Square(3, 0, -.4)))

    def test_rotation_bounds(self):
        self.assertAlmostEqual(side([Square(0, 0, math.pi/4)]), math.sqrt(2))

    def test_translation_and_permutation(self):
        original = five_pattern(math.pi/4)
        shifted = [Square(s.x+7, s.y-3, s.angle) for s in reversed(original)]
        self.assertAlmostEqual(validate(5, original), validate(5, shifted))

    def test_nonfinite(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            for args in ((value, 0, 0), (0, value, 0), (0, 0, value)):
                with self.assertRaises(ValueError):
                    Square(*args)

    def test_invalid_packing(self):
        for n, packing in ((0, []), (2, [Square(0, 0)]), (2, [Square(0, 0)]*2)):
            with self.assertRaises(ValueError):
                validate(n, packing)

    def test_area_bound(self):
        self.assertEqual(excess(4, 2), 0)
        with self.assertRaises(ValueError):
            excess(5, 2)


class SolverTests(unittest.TestCase):
    def test_grid_small_suite(self):
        for n in range(1, 65):
            self.assertEqual(validate(n, grid(n)), math.ceil(math.sqrt(n)))

    def test_grid_domain(self):
        for n in (0, -1, 1001, 1.5, True):
            with self.assertRaises(ValueError):
                grid(n)

    def test_constructive_family(self):
        for i in range(101):
            theta = i*math.pi/400
            self.assertAlmostEqual(validate(5, five_pattern(theta)),
                                   2+1/(math.cos(theta)+math.sin(theta))+1e-9)

    def test_five_improvement_and_ablation(self):
        result = experiment(5)
        self.assertLess(validate(5, result), 3)
        self.assertAlmostEqual(side(result), 2+1/math.sqrt(2)+1e-9)
        self.assertGreater(side(five_pattern(0)), side(result))

    def test_seed_reproducibility(self):
        self.assertEqual(experiment(5, seed=87), experiment(5, seed=87))

    def test_fallback(self):
        for n in (1, 2, 4, 6, 16):
            self.assertEqual(experiment(n), grid(n))

    def test_invalid_parameters(self):
        for margin in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                experiment(5, margin=margin)
        with self.assertRaises(ValueError):
            experiment(5, trials=0)


class ArtifactTests(unittest.TestCase):
    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"candidate.csv"
            write_candidate(path, {5: experiment(5), 1: grid(1)})
            with path.open(newline="") as f:
                reader = csv.DictReader(f)
                self.assertEqual(tuple(reader.fieldnames), HEADER)
                rows = list(reader)
            self.assertEqual([int(r["id"]) for r in rows], list(range(6)))
            self.assertEqual([int(r["square_id"]) for r in rows[1:]], list(range(5)))
            restored = [Square(*(float(r[k]) for k in ("x", "y", "angle"))) for r in rows[1:]]
            self.assertAlmostEqual(validate(5, restored), side(experiment(5)))

    def test_export_rejects_before_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"candidate.csv"
            path.write_text("preserve me")
            with self.assertRaises(ValueError):
                write_candidate(path, {2: [Square(0, 0)]*2})
            self.assertEqual(path.read_text(), "preserve me")

    def test_end_to_end_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/"a", Path(d)/"b"
            for out in (a, b):
                main(["--max-n", "16", "--out", str(out)])
            for filename in ("results.json", "candidate_NOT_VALIDATED.csv", "packing_5.svg"):
                self.assertEqual((a/filename).read_bytes(), (b/filename).read_bytes())
            report = json.loads((a/"results.json").read_text())
            self.assertGreater(report["grid_subset_sum"], report["local_subset_sum"])
            self.assertIn("NOT_OFFICIALLY_VALIDATED", report["status"])


if __name__ == "__main__":
    unittest.main()
