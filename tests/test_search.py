import math
import unittest
from tailorpack.geometry import Square, validate
from tailorpack.search import repair, search
from tailorpack.solvers import five_pattern


class SearchTests(unittest.TestCase):
    def test_repair_rotated_overlaps(self):
        packing = [Square(0, 0, .2), Square(.2, .1, -.3), Square(-.1, .2, .7)]
        result = repair(packing)
        self.assertIsNotNone(result)
        self.assertGreater(validate(3, result), math.sqrt(3))
        self.assertEqual([s.angle for s in result], [s.angle for s in packing])

    def test_coincident_centres_declined(self):
        self.assertIsNone(repair([Square(0, 0), Square(0, 0, .5)]))

    def test_repair_translated_family(self):
        for i in range(9):
            original = five_pattern(i*math.pi/32)
            packing = [Square(s.x*.8+10, s.y*.8-5, s.angle) for s in original]
            self.assertLess(validate(5, repair(packing)), 3.000001)

    def test_reproducible_and_never_worse(self):
        for method in ("greedy", "annealing"):
            a = search(6, seed=7, evaluations=100, method=method)
            b = search(6, seed=7, evaluations=100, method=method)
            self.assertEqual(a, b)
            self.assertEqual(a.evaluations, 100)
            self.assertLessEqual(a.best_side, a.initial_side)
            self.assertEqual(validate(6, a.squares), a.best_side)

    def test_invalid_budget_method_initial(self):
        for kwargs in ({"evaluations":0}, {"method":"unknown"}, {"initial":[Square(0, 0)]}):
            with self.assertRaises(ValueError):
                search(5, **kwargs)

    def test_improves_loose_feasible_start(self):
        result = search(5, seed=2, evaluations=500, method="greedy", initial=five_pattern(0))
        self.assertLess(result.best_side, 2.9)
        validate(5, result.squares)
