from contextlib import redirect_stdout
import io
import json
import math
import random
from pathlib import Path
import tempfile
import unittest

from tailorpack.geometry import Square, candidate_pairs, overlaps, validate
from tailorpack.export import write_candidate
from tailorpack.scale import run
from tailorpack.search import repair, search
from tailorpack.solvers import five_pattern, grid


class ScaleTests(unittest.TestCase):
    def test_spatial_validation_contains_all_collisions(self):
        rng = random.Random(4)
        for _ in range(20):
            squares = [Square(rng.uniform(-5,5), rng.uniform(-5,5), rng.uniform(-3,3)) for i in range(30)]
            candidates = set(candidate_pairs(squares))
            collisions = {(i,j) for i in range(30) for j in range(i+1,30) if overlaps(squares[i],squares[j])}
            self.assertTrue(collisions <= candidates)

    def test_repair_matches_exhaustive_random_layouts(self):
        rng = random.Random(9)
        for n in (2, 3, 10, 40):
            for _ in range(10):
                packing = [Square(rng.uniform(-10,10), rng.uniform(-10,10), rng.uniform(-3,3)) for i in range(n)]
                a = repair(packing, backend="spatial")
                b = repair(packing, backend="all-pairs")
                self.assertEqual(a, b)
                if a is not None:
                    validate(n, a, backend="all-pairs")

    def test_search_matches_exhaustive(self):
        for seed in range(3):
            self.assertEqual(search(10, seed=seed, evaluations=100, backend="spatial"),
                             search(10, seed=seed, evaluations=100, backend="all-pairs"))

    def test_exact_resume_and_completed_cache(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"checkpoint.json"
            uninterrupted = search(10, seed=4, evaluations=150)
            interrupted = search(10, seed=4, evaluations=150, stop_after=57,
                                 checkpoint=path, checkpoint_every=20)
            self.assertEqual(interrupted.evaluations, 57)
            resumed = search(10, seed=4, evaluations=150, checkpoint=path)
            self.assertEqual(uninterrupted, resumed)
            self.assertEqual(resumed, search(10, seed=4, evaluations=150, checkpoint=path))
            with self.assertRaises(ValueError):
                search(10, seed=4, evaluations=151, checkpoint=path)

    def test_checkpoint_rejects_source_change(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"checkpoint.json"
            search(5, evaluations=5, checkpoint=path)
            state = json.loads(path.read_text())
            state["config"]["engine_sha256"] = "different"
            path.write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                search(5, evaluations=5, checkpoint=path)

    def test_parallel_and_serial_outputs_and_cache(self):
        with tempfile.TemporaryDirectory() as d, redirect_stdout(io.StringIO()):
            a, b = Path(d)/"serial", Path(d)/"parallel"
            run([5,10], [0,1], 20, 1, a)
            run([5,10], [0,1], 20, 2, b)
            self.assertEqual((a/"candidate_NOT_VALIDATED.csv").read_bytes(),
                             (b/"candidate_NOT_VALIDATED.csv").read_bytes())
            cached = run([5,10], [0,1], 20, 2, b)
            self.assertEqual(cached["cached_jobs"], 4)

    def test_warm_start_cannot_degrade_best(self):
        with tempfile.TemporaryDirectory() as d, redirect_stdout(io.StringIO()):
            root = Path(d)
            warm = root/"warm.csv"
            packing = five_pattern(0)
            write_candidate(warm, {5:packing})
            report = run([5], [0], 20, 1, root/"weak", warm)
            self.assertLess(report["rows"][0]["initial_side"], validate(5, packing))
            stronger = five_pattern(math.pi/4, margin=1e-10)
            write_candidate(warm, {5:stronger})
            report = run([5], [0], 20, 1, root/"strong", warm)
            self.assertEqual(report["rows"][0]["initial_side"], validate(5, stronger))
            self.assertLessEqual(report["rows"][0]["best_side"], validate(5, stronger))
            with self.assertRaises(ValueError):
                run([5], [0], 30, 1, root/"strong")

    def test_grid_1000_spatial_validation(self):
        self.assertEqual(validate(1000, grid(1000)), 32)
