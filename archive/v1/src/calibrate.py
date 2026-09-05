#!/usr/bin/env python3
"""Evaluate ΛH/1 semantic geometry against qualitative probes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # package import
    from .lambda_h import CodecError, WIDTHS, compare_q, decode_q
except ImportError:  # direct-script compatibility
    from lambda_h import CodecError, WIDTHS, compare_q, decode_q

DEFAULT_PROBES = Path(__file__).resolve().parents[1] / "calibration" / "probes.json"


class CalibrationError(ValueError):
    """Raised when calibration input is malformed or incomplete."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CalibrationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CalibrationError(f"{path} must contain a JSON object")
    return value


def _probe_index(probes: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = probes.get("probes")
    if not isinstance(raw, list):
        raise CalibrationError("probes.json must contain a probes array")
    indexed: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise CalibrationError("each probe must be an object")
        probe_id = item.get("id")
        layer = item.get("layer")
        command = item.get("command")
        if not isinstance(probe_id, str) or not probe_id:
            raise CalibrationError("each probe requires a non-empty id")
        if probe_id in indexed:
            raise CalibrationError(f"duplicate probe id {probe_id!r}")
        if layer not in WIDTHS:
            raise CalibrationError(f"probe {probe_id!r} has unknown layer {layer!r}")
        if not isinstance(command, str) or not command:
            raise CalibrationError(f"probe {probe_id!r} requires a command")
        indexed[probe_id] = item
    return indexed


def make_template(probes: dict[str, Any]) -> dict[str, Any]:
    indexed = _probe_index(probes)
    basis = probes.get("basis", {})
    if not isinstance(basis, dict):
        raise CalibrationError("probes.json basis must be an object")
    return {
        "protocol": "ΛH/1",
        "model": "",
        "basis": basis,
        "regions": {probe_id: "" for probe_id in indexed},
    }


def _validated_regions(
    probes: dict[str, Any], results: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    if results.get("protocol") != "ΛH/1":
        raise CalibrationError('results.protocol must equal "ΛH/1"')

    indexed = _probe_index(probes)
    expected_basis = probes.get("basis", {})
    actual_basis = results.get("basis")
    if not isinstance(actual_basis, dict):
        raise CalibrationError("results.basis must be an object")
    if isinstance(expected_basis, dict):
        for layer, version in expected_basis.items():
            if actual_basis.get(layer) != version:
                raise CalibrationError(
                    f"results basis {layer!r} must be {version!r}, got {actual_basis.get(layer)!r}"
                )

    raw_regions = results.get("regions")
    if not isinstance(raw_regions, dict):
        raise CalibrationError("results.regions must be an object")

    regions: dict[str, str] = {}
    for probe_id, q in raw_regions.items():
        if probe_id not in indexed:
            raise CalibrationError(f"unknown result probe id {probe_id!r}")
        if q == "":
            continue
        if not isinstance(q, str):
            raise CalibrationError(f"result {probe_id!r} must be a wire-vector string")
        layer = indexed[probe_id]["layer"]
        try:
            decode_q(q, width=WIDTHS[layer])
        except CodecError as exc:
            raise CalibrationError(f"result {probe_id!r}: {exc}") from exc
        regions[probe_id] = q

    return indexed, regions


def evaluate(probes: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    indexed, regions = _validated_regions(probes, results)
    raw_checks = probes.get("qualitative_checks")
    if not isinstance(raw_checks, list):
        raise CalibrationError("probes.json must contain a qualitative_checks array")

    checks: list[dict[str, Any]] = []
    passed = failed = missing = 0

    for index, check in enumerate(raw_checks):
        if not isinstance(check, dict):
            raise CalibrationError(f"qualitative_checks[{index}] must be an object")
        kind = check.get("type")
        layer = check.get("layer")
        meaning = check.get("meaning", "")
        if layer not in WIDTHS:
            raise CalibrationError(f"qualitative_checks[{index}] has unknown layer {layer!r}")

        required = [check.get("a"), check.get("b")]
        if kind == "closer_than":
            required.append(check.get("c"))
        if not all(isinstance(item, str) and item in indexed for item in required):
            raise CalibrationError(f"qualitative_checks[{index}] references unknown probes")
        if any(indexed[item]["layer"] != layer for item in required):
            raise CalibrationError(f"qualitative_checks[{index}] mixes semantic layers")

        absent = [item for item in required if item not in regions]
        if absent:
            missing += 1
            checks.append(
                {
                    "type": kind,
                    "meaning": meaning,
                    "status": "missing",
                    "missing": absent,
                }
            )
            continue

        a, b = required[0], required[1]
        if kind == "closer_than":
            c = required[2]
            ab = compare_q(regions[a], regions[b], width=WIDTHS[layer])
            ac = compare_q(regions[a], regions[c], width=WIDTHS[layer])
            ok = ab["rmse"] < ac["rmse"]
            checks.append(
                {
                    "type": kind,
                    "meaning": meaning,
                    "status": "pass" if ok else "fail",
                    "distance_ab": ab["rmse"],
                    "distance_ac": ac["rmse"],
                }
            )
        elif kind == "sense_separation":
            metrics = compare_q(regions[a], regions[b], width=WIDTHS[layer])
            ok = metrics["rmse"] > 0
            checks.append(
                {
                    "type": kind,
                    "meaning": meaning,
                    "status": "pass" if ok else "fail",
                    "rmse": metrics["rmse"],
                    "mean_abs_delta": metrics["mean_abs_delta"],
                    "cosine": metrics["cosine"],
                }
            )
        else:
            raise CalibrationError(f"unsupported qualitative check type {kind!r}")

        if ok:
            passed += 1
        else:
            failed += 1

    return {
        "protocol": "ΛH/1",
        "model": results.get("model", ""),
        "summary": {"passed": passed, "failed": failed, "missing": missing},
        "checks": checks,
    }


def evaluate_pair(
    probes: dict[str, Any], results_a: dict[str, Any], results_b: dict[str, Any]
) -> dict[str, Any]:
    """Evaluate two sessions and derive empirical cross-model separation checks."""
    indexed, regions_a = _validated_regions(probes, results_a)
    _, regions_b = _validated_regions(probes, results_b)
    raw_checks = probes.get("qualitative_checks")
    if not isinstance(raw_checks, list):
        raise CalibrationError("probes.json must contain a qualitative_checks array")

    pair_checks: list[dict[str, Any]] = []
    passed = failed = missing = 0

    for index, check in enumerate(raw_checks):
        if not isinstance(check, dict):
            raise CalibrationError(f"qualitative_checks[{index}] must be an object")
        kind = check.get("type")
        layer = check.get("layer")
        meaning = check.get("meaning", "")
        required = [check.get("a"), check.get("b")]
        if kind == "closer_than":
            required.append(check.get("c"))
        if layer not in WIDTHS or not all(
            isinstance(item, str) and item in indexed for item in required
        ):
            raise CalibrationError(f"qualitative_checks[{index}] is malformed")

        absent = [
            item
            for item in required
            if item not in regions_a or item not in regions_b
        ]
        if absent:
            missing += 1
            pair_checks.append(
                {
                    "type": kind,
                    "meaning": meaning,
                    "status": "missing",
                    "missing": sorted(set(absent)),
                }
            )
            continue

        a, b = required[0], required[1]
        if kind == "closer_than":
            c = required[2]
            a_ab = compare_q(regions_a[a], regions_a[b], width=WIDTHS[layer])["rmse"]
            a_ac = compare_q(regions_a[a], regions_a[c], width=WIDTHS[layer])["rmse"]
            b_ab = compare_q(regions_b[a], regions_b[b], width=WIDTHS[layer])["rmse"]
            b_ac = compare_q(regions_b[a], regions_b[c], width=WIDTHS[layer])["rmse"]
            ok = a_ab < a_ac and b_ab < b_ac
            detail = {
                "type": kind,
                "meaning": meaning,
                "status": "pass" if ok else "fail",
                "session_a": {"distance_ab": a_ab, "distance_ac": a_ac},
                "session_b": {"distance_ab": b_ab, "distance_ac": b_ac},
            }
        elif kind == "sense_separation":
            within_a = compare_q(regions_a[a], regions_a[b], width=WIDTHS[layer])["rmse"]
            within_b = compare_q(regions_b[a], regions_b[b], width=WIDTHS[layer])["rmse"]
            drift_a = compare_q(regions_a[a], regions_b[a], width=WIDTHS[layer])["rmse"]
            drift_b = compare_q(regions_a[b], regions_b[b], width=WIDTHS[layer])["rmse"]
            empirical_floor = max(drift_a, drift_b)
            observed_separation = min(within_a, within_b)
            ok = observed_separation > empirical_floor
            detail = {
                "type": kind,
                "meaning": meaning,
                "status": "pass" if ok else "fail",
                "within_session_rmse": {"a": within_a, "b": within_b},
                "same_sense_cross_model_rmse": {"a": drift_a, "b": drift_b},
                "empirical_floor": empirical_floor,
                "observed_separation": observed_separation,
            }
        else:
            raise CalibrationError(f"unsupported qualitative check type {kind!r}")

        pair_checks.append(detail)
        if ok:
            passed += 1
        else:
            failed += 1

    probe_agreement: dict[str, dict[str, float | None]] = {}
    for probe_id, item in indexed.items():
        if probe_id in regions_a and probe_id in regions_b:
            probe_agreement[probe_id] = compare_q(
                regions_a[probe_id], regions_b[probe_id], width=WIDTHS[item["layer"]]
            )

    return {
        "protocol": "ΛH/1",
        "models": [results_a.get("model", ""), results_b.get("model", "")],
        "summary": {"passed": passed, "failed": failed, "missing": missing},
        "checks": pair_checks,
        "probe_agreement": probe_agreement,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate ΛH/1 semantic-geometry calibration results"
    )
    parser.add_argument(
        "results",
        nargs="*",
        help="one result JSON for local checks, or two result JSON files for cross-model checks",
    )
    parser.add_argument(
        "--probes",
        default=str(DEFAULT_PROBES),
        help="probe definition JSON (default: calibration/probes.json)",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="print a blank result template instead of evaluating",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        probes = _load_json(Path(args.probes))
        if args.template:
            print(json.dumps(make_template(probes), ensure_ascii=False, indent=2))
            return 0
        if not args.results:
            parser.error("one or two results files are required unless --template is used")
        if len(args.results) > 2:
            parser.error("at most two results files may be supplied")
        results_a = _load_json(Path(args.results[0]))
        if len(args.results) == 1:
            report = evaluate(probes, results_a)
        else:
            results_b = _load_json(Path(args.results[1]))
            report = evaluate_pair(probes, results_a, results_b)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        summary = report["summary"]
        if summary["failed"]:
            return 1
        if summary["missing"]:
            return 2
        return 0
    except CalibrationError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
