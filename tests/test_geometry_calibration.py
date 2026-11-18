"""Tests for src.geometry, src.calibration, and lazy exports in src.__init__."""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import src
from src import calibration
from src.geometry import (
    activation,
    focus_field,
    make_field,
    rank_candidates,
    shift_field,
)
from src.protocol import PROTOCOL, ProtocolError, require_valid

ROOT = Path(__file__).resolve().parents[1]


class TestGeometry(unittest.TestCase):
    def test_make_field_and_asymmetric_band_activation(self) -> None:
        field = make_field({"E00": 2}, layer="E", width=2.0, bands={"E00": [1.0, 4.0]}, weight=1.0)
        # Peak at center
        self.assertAlmostEqual(activation(field, {"E00": 2}, layer="E"), 1.0)
        # Negative delta (-1) uses lower band width (1.0) -> exp(-0.5 * (-1 / 1.0)^2)
        self.assertAlmostEqual(
            activation(field, {"E00": 1}, layer="E"),
            math.exp(-0.5 * 1.0),
        )
        # Positive delta (+2) uses upper band width (4.0) -> exp(-0.5 * (2 / 4.0)^2)
        self.assertAlmostEqual(
            activation(field, {"E00": 4}, layer="E"),
            math.exp(-0.5 * 0.25),
        )
        # Omitted point axes default to neutral zero (delta = -2 -> lower band 1.0)
        self.assertAlmostEqual(
            activation(field, {}, layer="E"),
            math.exp(-0.5 * 4.0),
        )

    def test_multi_component_max_envelope_without_midpoint_averaging(self) -> None:
        left = make_field({"E00": -4}, layer="E", width=1.0, weight=1.0)[0]
        right = make_field({"E00": 4}, layer="E", width=1.0, weight=0.5)[0]
        field = [left, right]

        # At neutral midpoint (0), max-envelope takes max, never sums both components.
        expected_mid = math.exp(-0.5 * 16.0)
        self.assertAlmostEqual(activation(field, {}, layer="E"), expected_mid)
        self.assertLess(activation(field, {}, layer="E"), 2 * expected_mid)

        # At right peak (4), score reflects normalized weight 0.5 / 1.0 without adding left tail.
        expected_right = 0.5 * 1.0
        self.assertAlmostEqual(activation(field, {"E00": 4}, layer="E"), expected_right)

    def test_focus_field_global_axis_selective_and_out_of_range(self) -> None:
        field = make_field({"E00": 2, "E01": 3}, layer="E", width=2.0, bands={"E01": [1.0, 3.0]})

        global_focus = focus_field(field, layer="E", scale=0.5)
        self.assertAlmostEqual(global_focus[0]["s"], 1.0)
        self.assertEqual(global_focus[0]["b"]["E01"], [0.5, 1.5])
        # Original field not mutated
        self.assertEqual(field[0]["s"], 2.0)

        axis_focus = focus_field(field, layer="E", scale=2.0, axes=["E00"])
        self.assertEqual(axis_focus[0]["s"], 2.0)
        self.assertEqual(axis_focus[0]["b"]["E00"], [4.0, 4.0])
        self.assertEqual(axis_focus[0]["b"]["E01"], [1.0, 3.0])

        # Out-of-range widths (>14) and invalid scale/axes rejected.
        with self.assertRaises(ProtocolError):
            focus_field(field, layer="E", scale=8.0)
        with self.assertRaises(ProtocolError):
            focus_field(field, layer="E", scale=5.0, axes=["E01"])
        with self.assertRaises(ProtocolError):
            focus_field(field, layer="E", scale=0)
        with self.assertRaises(ProtocolError):
            focus_field(field, layer="E", scale=float("nan"))
        with self.assertRaises(ProtocolError):
            focus_field(field, layer="E", scale=1.0, axes=["E00", "E00"])
        with self.assertRaises(ProtocolError):
            focus_field(field, layer="E", scale=1.0, axes=["E99"])

    def test_shift_field_pruning_and_out_of_range(self) -> None:
        field = make_field({"E00": 2, "E01": 3}, layer="E", width=2.0)
        shifted = shift_field(field, {"E00": -2, "E01": 2}, layer="E")
        # E00 becomes 0 and must be pruned from q.
        self.assertEqual(shifted[0]["q"], {"E01": 5})

        # Pruning every axis leaves q empty and must fail.
        single = make_field({"E00": 2}, layer="E", width=2.0)
        with self.assertRaises(ProtocolError):
            shift_field(single, {"E00": -2}, layer="E")

        # Out-of-range coordinate (>7 or <-7) fails.
        with self.assertRaises(ProtocolError):
            shift_field(field, {"E01": 5}, layer="E")

    def test_rank_candidates_selected_ambiguous_unresolved(self) -> None:
        field = make_field({"E00": 5}, layer="E", width=1.0)

        # Selected when best >= minimum and gap >= margin (>0).
        sel = rank_candidates(
            field,
            {"c1": {"E00": 5}, "c2": {"E00": 2}},
            layer="E",
            minimum=0.5,
            margin=0.2,
        )
        self.assertEqual(sel["status"], "selected")
        self.assertEqual(sel["selected"], "c1")
        self.assertGreaterEqual(sel["gap"], 0.2)

        # Ambiguous on exact tie even when margin == 0.
        tie = rank_candidates(
            field,
            {"a": {"E00": 5}, "b": {"E00": 5}},
            layer="E",
            minimum=0.5,
            margin=0.0,
        )
        self.assertEqual(tie["status"], "ambiguous")
        self.assertIsNone(tie["selected"])
        self.assertEqual(tie["gap"], 0.0)

        # Ambiguous when gap < margin.
        narrow_gap = rank_candidates(
            field,
            {"c1": {"E00": 5}, "c2": {"E00": 4}},
            layer="E",
            minimum=0.5,
            margin=0.5,
        )
        self.assertEqual(narrow_gap["status"], "ambiguous")
        self.assertIsNone(narrow_gap["selected"])

        # Unresolved when best < minimum.
        low = rank_candidates(
            field,
            {"c1": {"E00": -5}},
            layer="E",
            minimum=0.5,
            margin=0.0,
        )
        self.assertEqual(low["status"], "unresolved")
        self.assertIsNone(low["selected"])

        # Single candidate above minimum is selected with gap=None.
        solo = rank_candidates(field, {"only": {"E00": 5}}, layer="E", minimum=0.5, margin=0.2)
        self.assertEqual(solo["status"], "selected")
        self.assertEqual(solo["selected"], "only")
        self.assertIsNone(solo["gap"])


class TestCalibration(unittest.TestCase):
    def _write_temp_probes(self, tmp_dir: Path) -> Path:
        probes = {
            "protocol": PROTOCOL,
            "cases": [
                {
                    "id": "probe_alpha",
                    "expect": "UNIQUE_EXPECTATION_ALPHA_DO_NOT_LEAK",
                    "packet": {
                        "protocol": PROTOCOL,
                        "context": "0",
                        "E": [{"id": "e0", "q": {"E00": 1}}],
                        "A": [{"id": "a0", "q": {"A00": 1}, "target": "e0"}],
                    },
                },
                {
                    "id": "probe_beta",
                    "expect": "UNIQUE_EXPECTATION_BETA_DO_NOT_LEAK",
                    "packet": {
                        "protocol": PROTOCOL,
                        "context": "0",
                        "A": [{"id": "a0", "q": {"A03": 7}, "target": "X08"}],
                    },
                },
            ],
        }
        path = tmp_dir / "probes.json"
        path.write_text(json.dumps(probes), encoding="utf-8")
        return path

    def test_live_load_cases_non_empty_and_valid(self) -> None:
        cases = calibration.load_cases()
        self.assertIsInstance(cases, dict)
        self.assertGreater(len(cases), 0)
        for case_id, case in cases.items():
            self.assertEqual(case["id"], case_id)
            require_valid(case["packet"])
            wire_in = calibration.receiver_input(case)
            self.assertTrue(wire_in.startswith("ΛH2.2|\n"))
            self.assertNotIn(case["expect"], wire_in)

    def test_template_receiver_input_and_evaluate_lifecycle(self) -> None:
        dims = tuple(calibration.DIMENSIONS)
        self.assertGreaterEqual(len(dims), 1)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            probes_path = self._write_temp_probes(tmp_dir)
            cases = calibration.load_cases(probes_path)

            for case in cases.values():
                text = calibration.receiver_input(case)
                self.assertTrue(text.startswith("ΛH2.2|\n"))
                self.assertNotIn(case["expect"], text)
                self.assertNotIn(case["id"], text)

            # Fresh template evaluates as all missing.
            template = calibration.make_template(cases)
            self.assertEqual(
                set(template["observations"]["probe_alpha"]["judgments"].keys()),
                set(dims),
            )
            missing_report = calibration.evaluate(cases, template, trace_root=tmp_dir)
            self.assertEqual(missing_report["summary"], {"passed": 0, "failed": 0, "missing": 2})

            # Create trace files and fill passing observations.
            trace_a = tmp_dir / "trace_a.json"
            trace_b = tmp_dir / "trace_b.json"
            trace_a.write_text("{}", encoding="utf-8")
            trace_b.write_text("{}", encoding="utf-8")

            passing = calibration.make_template(cases)
            passing.update({"model": "test-model", "run": "run-1", "grader": "reviewer"})
            passing["observations"]["probe_alpha"] = {
                "session": "sess-1",
                "response": "inspected",
                "trace": "trace_a.json",
                "tool_calls": 1,
                "judgments": {dim: True for dim in dims},
                "judge_notes": "ok",
            }
            passing["observations"]["probe_beta"] = {
                "session": "sess-2",
                "response": "checked",
                "trace": str(trace_b),
                "tool_calls": 0,
                "judgments": {dim: True for dim in dims},
                "judge_notes": "ok",
            }
            pass_report = calibration.evaluate(cases, passing, trace_root=tmp_dir)
            self.assertEqual(pass_report["summary"], {"passed": 2, "failed": 0, "missing": 0})

            # Missing trace file -> missing status with "trace_file".
            missing_trace = json.loads(json.dumps(passing))
            missing_trace["observations"]["probe_beta"]["trace"] = "does_not_exist.json"
            mt_report = calibration.evaluate(cases, missing_trace, trace_root=tmp_dir)
            self.assertEqual(mt_report["summary"], {"passed": 1, "failed": 0, "missing": 1})
            beta_entry = next(item for item in mt_report["cases"] if item["id"] == "probe_beta")
            self.assertIn("trace_file", beta_entry["missing"])

            # False judgment on any dimension -> fail.
            failing = json.loads(json.dumps(passing))
            failing["observations"]["probe_beta"]["judgments"][dims[-1]] = False
            fail_report = calibration.evaluate(cases, failing, trace_root=tmp_dir)
            self.assertEqual(fail_report["summary"], {"passed": 1, "failed": 1, "missing": 0})

            # Duplicate session rejected.
            dup_sess = json.loads(json.dumps(passing))
            dup_sess["observations"]["probe_beta"]["session"] = "sess-1"
            with self.assertRaises(ProtocolError):
                calibration.evaluate(cases, dup_sess, trace_root=tmp_dir)

            # Digest mismatches rejected.
            for digest_key in ("prompt_sha256", "basis_sha256", "corpus_sha256"):
                bad_digest = json.loads(json.dumps(passing))
                bad_digest[digest_key] = "0" * 64
                with self.subTest(digest_key=digest_key), self.assertRaises(ProtocolError):
                    calibration.evaluate(cases, bad_digest, trace_root=tmp_dir)


class TestLazyPackageExports(unittest.TestCase):
    def test_all_exports_resolve_lazily(self) -> None:
        resolved = [getattr(src, name) for name in src.__all__]
        self.assertEqual(len(resolved), len(src.__all__))
        for item in resolved:
            self.assertIsNotNone(item)
        with self.assertRaises(AttributeError):
            _ = src.nonexistent_symbol_name

    def test_importing_src_has_no_eager_submodule_side_effects(self) -> None:
        code = (
            "import sys, src; "
            "eager = [m for m in ('src.codec', 'src.geometry', 'src.ir', 'src.context', 'src.protocol') if m in sys.modules]; "
            "assert not eager, f'unexpected eager imports: {eager}'; "
            "vals = [getattr(src, name) for name in src.__all__]; "
            "assert len(vals) == len(src.__all__)"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)


class TestSyncDocs(unittest.TestCase):
    def test_sync_docs_check_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "src.sync_docs", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
