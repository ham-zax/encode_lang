from __future__ import annotations

import unittest

from src.calibrate import evaluate_pair
from src.lambda_h import encode_scores


def q(*scores: int) -> str:
    values = list(scores) + [0] * (32 - len(scores))
    return encode_scores(values, width=32)


class CalibrationTests(unittest.TestCase):
    def test_pair_uses_geometry_and_empirical_sense_floor(self):
        probes = {
            "protocol": "ΛH/1",
            "basis": {"E": "01"},
            "probes": [
                {"id": "cat", "layer": "E", "command": "WORD: cat"},
                {"id": "dog", "layer": "E", "command": "WORD: dog"},
                {"id": "hat", "layer": "E", "command": "WORD: hat"},
                {"id": "fire_a", "layer": "E", "command": "WORD: fire"},
                {"id": "fire_b", "layer": "E", "command": "WORD: fire"},
            ],
            "qualitative_checks": [
                {
                    "type": "closer_than",
                    "layer": "E",
                    "a": "cat",
                    "b": "dog",
                    "c": "hat",
                    "meaning": "cat closer to dog than hat",
                },
                {
                    "type": "sense_separation",
                    "layer": "E",
                    "a": "fire_a",
                    "b": "fire_b",
                    "meaning": "fire senses separate beyond model drift",
                },
            ],
        }
        results_a = {
            "protocol": "ΛH/1",
            "model": "A",
            "basis": {"E": "01"},
            "regions": {
                "cat": q(5, 0, 0, 0),
                "dog": q(4, 0, 0, 0),
                "hat": q(0, 5, 0, 0),
                "fire_a": q(0, 0, 5, 0),
                "fire_b": q(0, 0, 0, 5),
            },
        }
        results_b = {
            "protocol": "ΛH/1",
            "model": "B",
            "basis": {"E": "01"},
            "regions": {
                "cat": q(5, 0, 0, 1),
                "dog": q(4, 0, 0, 1),
                "hat": q(0, 5, 0, 1),
                "fire_a": q(0, 0, 5, 1),
                "fire_b": q(0, 0, 0, 5, 1),
            },
        }

        report = evaluate_pair(probes, results_a, results_b)
        self.assertEqual(report["summary"], {"passed": 2, "failed": 0, "missing": 0})
        sense = report["checks"][1]
        self.assertGreater(sense["observed_separation"], sense["empirical_floor"])


if __name__ == "__main__":
    unittest.main()
