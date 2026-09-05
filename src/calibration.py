"""Evidence-recording receiver calibration; never fabricates model outcomes.

Judgments are explicit human/reviewer assessments, not an automatic semantic
oracle. A parsed packet or an empty template cannot count as a behavior pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from .codec import format_packet, read_json
from .protocol import PROTOCOL, ProtocolError, require_valid

ROOT = Path(__file__).resolve().parents[1]
PROBES = ROOT / "calibration" / "probes.json"
BOOTSTRAP = ROOT / "prompt" / "BOOTSTRAP.md"
DIMENSIONS = ("meaning", "direct_response", "constraints", "disclosure")


def load_cases(path: Path = PROBES) -> dict[str, dict[str, Any]]:
    source = read_json(path.read_text(encoding="utf-8"))
    if not isinstance(source, dict) or source.get("protocol") != PROTOCOL:
        raise ProtocolError("calibration corpus must identify Lambda H/2")
    raw = source.get("cases")
    if not isinstance(raw, list) or not raw:
        raise ProtocolError("calibration corpus requires cases")
    cases = {}
    for case in raw:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"]:
            raise ProtocolError("each case requires an id")
        if case["id"] in cases:
            raise ProtocolError("duplicate calibration case id")
        if not isinstance(case.get("context"), str) or not isinstance(case.get("expect"), str):
            raise ProtocolError("each case requires context and evaluator expectation")
        require_valid(case.get("packet"))
        cases[case["id"]] = case
    return cases


def bootstrap_digest() -> str:
    return hashlib.sha256(BOOTSTRAP.read_bytes()).hexdigest()


def make_template(cases: dict[str, Any]) -> dict[str, Any]:
    return {
        "protocol": PROTOCOL, "bootstrap_sha256": bootstrap_digest(),
        "model": None, "run": None, "grader": None,
        "observations": {case_id: {
            "session": None, "response": None, "trace": None,
            "decoder_tool_calls": None,
            "judgments": {dimension: None for dimension in DIMENSIONS},
            "judge_notes": None,
        } for case_id in cases},
    }


def receiver_input(case: dict[str, Any]) -> str:
    # Deliberately exclude the source/expectation, case label, and scoring rubric.
    context = case["context"].strip()
    return (context + "\n\n" if context else "") + format_packet(case["packet"])


def evaluate(cases: dict[str, Any], results: Any, *, trace_root: Path) -> dict[str, Any]:
    if not isinstance(results, dict) or results.get("protocol") != PROTOCOL:
        raise ProtocolError("results must identify Lambda H/2")
    if results.get("bootstrap_sha256") != bootstrap_digest():
        raise ProtocolError("results belong to a different bootstrap; retain them as historical evidence, not a current pass")
    observations = results.get("observations")
    if not isinstance(observations, dict) or set(observations) - set(cases):
        raise ProtocolError("observations must be an object containing only known case ids")
    metadata_ready = all(isinstance(results.get(key), str) and results[key].strip() for key in ("model", "run", "grader"))
    summary = {"passed": 0, "failed": 0, "missing": 0}
    reports = []
    sessions: set[str] = set()
    for case_id in cases:
        item = observations.get(case_id, {})
        if not isinstance(item, dict):
            raise ProtocolError(f"{case_id}: observation must be an object")
        judgments = item.get("judgments", {})
        if not isinstance(judgments, dict) or set(judgments) - set(DIMENSIONS):
            raise ProtocolError(f"{case_id}: unknown judgment dimension")
        if any(value is not None and type(value) is not bool for value in judgments.values()):
            raise ProtocolError(f"{case_id}: judgments must be boolean or null")
        calls = item.get("decoder_tool_calls")
        if calls is not None and (type(calls) is not int or calls < 0):
            raise ProtocolError(f"{case_id}: decoder_tool_calls must be nonnegative integer or null")
        absent = []
        for key in ("session", "response", "trace", "judge_notes"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                absent.append(key)
        absent += [key for key in DIMENSIONS if judgments.get(key) is None]
        if calls is None:
            absent.append("decoder_tool_calls")
        if not metadata_ready:
            absent.append("run_metadata")
        if isinstance(item.get("trace"), str) and item["trace"].strip():
            trace = Path(item["trace"])
            if not trace.is_absolute():
                trace = trace_root / trace
            if not trace.is_file():
                absent.append("trace_file")
        session = item.get("session")
        if isinstance(session, str) and session:
            if session in sessions:
                raise ProtocolError("reuse of a receiving session contaminates fresh-session calibration")
            sessions.add(session)
        status = "missing" if absent else "pass" if calls == 0 and all(judgments.values()) else "fail"
        summary[{"pass": "passed", "fail": "failed", "missing": "missing"}[status]] += 1
        reports.append({"id": case_id, "status": status, "missing": absent,
                        "judgments": judgments, "decoder_tool_calls": calls})
    return {"protocol": PROTOCOL, "model": results.get("model"), "summary": summary,
            "cases": reports, "method": "explicit reviewer judgments backed by captured receiver traces; not an independent automatic semantic oracle"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", nargs="?", help="recorded receiver observations JSON")
    parser.add_argument("--probes", type=Path, default=PROBES)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--template", action="store_true")
    action.add_argument("--receiver", metavar="CASE_ID", help="emit receiver input without grading answers")
    args = parser.parse_args()
    try:
        cases = load_cases(args.probes)
        if args.template:
            result = make_template(cases)
        elif args.receiver:
            if args.receiver not in cases:
                raise ProtocolError("unknown case id")
            print(receiver_input(cases[args.receiver]))
            return 0
        elif args.results:
            path = Path(args.results)
            result = evaluate(cases, read_json(path.read_text(encoding="utf-8")), trace_root=path.parent)
        else:
            parser.error("supply --template, --receiver CASE_ID, or a results path")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if "summary" not in result:
            return 0
        if result["summary"]["failed"]:
            return 1
        return 2 if result["summary"]["missing"] else 0
    except (ProtocolError, OSError, UnicodeError, RecursionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
