import os
from pathlib import Path
import tempfile
import unittest

from tailorpack.official import extract_source, metric_snapshot


class SnapshotTests(unittest.TestCase):
    def test_unreviewed_notebook_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"metric.ipynb"
            path.write_text('{"cells":[{"cell_type":"code","source":["raise RuntimeError()"]}]}')
            with self.assertRaises(ValueError):
                extract_source(path)


@unittest.skipUnless(os.environ.get("TAILORPACK_METRIC_NOTEBOOK"),
                     "Optional: set TAILORPACK_METRIC_NOTEBOOK and install requirements-official.txt")
class OfficialRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = metric_snapshot(os.environ["TAILORPACK_METRIC_NOTEBOOK"])
        cls.metric = cls.snapshot.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.snapshot.__exit__(None, None, None)

    def pair(self, x="1.5"):
        return [dict(square_id="0", x="0.5", y="0.5", angle="0"),
                dict(square_id="1", x=x, y="0.5", angle="0")]

    def test_contact_accepted_overlap_rejected(self):
        self.assertEqual(self.metric.evaluate_single_puzzle(2, self.pair())[3], "ok")
        result = self.metric.evaluate_single_puzzle(2, self.pair("1.499999999999"))
        self.assertIsNone(result[2])
        self.assertIn("infeasible", result[3])

    def test_duplicate_or_missing_square(self):
        rows = self.pair()
        rows[1]["square_id"] = "0"
        self.assertIsNone(self.metric.evaluate_single_puzzle(2, rows)[2])
        self.assertIsNone(self.metric.evaluate_single_puzzle(2, rows[:1])[2])

    def test_invalid_decimal(self):
        for x in ("NaN", "inf", "1+sqrt(2)", "1e400"):
            self.assertIsNone(self.metric.evaluate_single_puzzle(2, self.pair(x))[2])

    def test_invalid_n_is_global_error(self):
        with self.assertRaises(self.metric.ParticipantVisibleError):
            self.metric._parse_submission_csv("n,square_id,x,y,angle\n1001,0,0,0,0\n")

    def test_missing_puzzle_penalty(self):
        total, rows = self.metric._evaluate_puzzles_parallel({}, {1, 2, 5})
        self.assertAlmostEqual(total, sum(self.metric.infeasible_score(n) for n in (1, 2, 5)))
        self.assertTrue(all(r[2] is None for r in rows))
