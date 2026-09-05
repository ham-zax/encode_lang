#!/usr/bin/env python3
"""Validate canonical ΛH/1 JSON packets using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HEX_RE = re.compile(r"^[0-E]+$")
HANDLE_RES = {
    "E": re.compile(r"^η[0-9A-F]{2}$"),
    "R": re.compile(r"^ρ[0-9A-F]{2}$"),
    "A": re.compile(r"^α[0-9A-F]{2}$"),
    "T": re.compile(r"^τ[0-9A-F]{2}$"),
}
EXPECTED_WIDTH = {"E": 32, "R": 16, "A": 16, "T": 16, "P": 12, "V": 8}
ALLOWED_TOP = {"protocol", "basis", "E", "R", "A", "T", "K", "P", "X", "V"}
K_CODES = {f"K{i:02d}" for i in range(9)}


def _error(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def _check_q(errors: list[str], path: str, q: Any, width: int) -> None:
    if not isinstance(q, str):
        _error(errors, path, "must be a string")
        return
    if len(q) != width:
        _error(errors, path, f"must be exactly {width} characters")
    if not HEX_RE.fullmatch(q):
        _error(errors, path, "must contain only 0-E; F is reserved")


def _check_u(errors: list[str], path: str, u: Any) -> None:
    if not isinstance(u, int) or isinstance(u, bool) or not 0 <= u <= 14:
        _error(errors, path, "must be an integer from 0 through 14")


def _check_region_list(errors: list[str], packet: dict[str, Any], layer: str) -> set[str]:
    handles: set[str] = set()
    values = packet.get(layer, [])
    if not isinstance(values, list):
        _error(errors, layer, "must be an array")
        return handles
    for i, item in enumerate(values):
        path = f"{layer}[{i}]"
        if not isinstance(item, dict):
            _error(errors, path, "must be an object")
            continue
        required = {"handle", "q", "u"}
        if layer == "R":
            required |= {"subject", "object"}
        missing = sorted(required - item.keys())
        if missing:
            _error(errors, path, f"missing fields: {', '.join(missing)}")
        unknown = sorted(set(item) - required)
        if unknown:
            _error(errors, path, f"unknown fields: {', '.join(unknown)}")
        handle = item.get("handle")
        if not isinstance(handle, str) or not HANDLE_RES[layer].fullmatch(handle):
            _error(errors, f"{path}.handle", f"invalid {layer} handle")
        elif handle in handles:
            _error(errors, f"{path}.handle", "duplicate handle")
        else:
            handles.add(handle)
        _check_q(errors, f"{path}.q", item.get("q"), EXPECTED_WIDTH[layer])
        _check_u(errors, f"{path}.u", item.get("u"))
    return handles


def validate_packet(packet: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(packet, dict):
        return ["packet: must be a JSON object"]
    unknown_top = sorted(set(packet) - ALLOWED_TOP)
    if unknown_top:
        _error(errors, "packet", f"unknown top-level fields: {', '.join(unknown_top)}")
    if packet.get("protocol") != "ΛH/1":
        _error(errors, "protocol", 'must equal "ΛH/1"')

    basis = packet.get("basis")
    if basis is not None:
        if not isinstance(basis, dict):
            _error(errors, "basis", "must be an object")
        else:
            for key, value in basis.items():
                if key not in {"E", "R", "A", "T", "P", "V"}:
                    _error(errors, f"basis.{key}", "unknown basis layer")
                elif value != "01":
                    _error(errors, f"basis.{key}", 'must equal "01"')

    entity_handles = _check_region_list(errors, packet, "E") if "E" in packet else set()
    for layer in ("R", "A", "T"):
        if layer in packet:
            _check_region_list(errors, packet, layer)

    if isinstance(packet.get("R"), list):
        for i, relation in enumerate(packet["R"]):
            if not isinstance(relation, dict):
                continue
            for role in ("subject", "object"):
                ref = relation.get(role)
                if not isinstance(ref, str) or not HANDLE_RES["E"].fullmatch(ref):
                    _error(errors, f"R[{i}].{role}", "must be a valid entity handle")
                elif entity_handles and ref not in entity_handles:
                    _error(errors, f"R[{i}].{role}", f"unbound entity handle {ref}")

    if "K" in packet:
        values = packet["K"]
        if not isinstance(values, list):
            _error(errors, "K", "must be an array")
        else:
            for i, item in enumerate(values):
                path = f"K[{i}]"
                if not isinstance(item, dict):
                    _error(errors, path, "must be an object")
                    continue
                if set(item) != {"target", "status", "confidence"}:
                    _error(errors, path, "must contain exactly target, status, confidence")
                if not isinstance(item.get("target"), str) or not item.get("target"):
                    _error(errors, f"{path}.target", "must be a non-empty string")
                if item.get("status") not in K_CODES:
                    _error(errors, f"{path}.status", "must be K00 through K08")
                confidence = item.get("confidence")
                if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
                    _error(errors, f"{path}.confidence", "must be a number from 0.0 through 1.0")

    if "P" in packet:
        value = packet["P"]
        if not isinstance(value, dict) or set(value) != {"q", "u"}:
            _error(errors, "P", "must contain exactly q and u")
        else:
            _check_q(errors, "P.q", value.get("q"), EXPECTED_WIDTH["P"])
            _check_u(errors, "P.u", value.get("u"))

    if "V" in packet:
        value = packet["V"]
        if not isinstance(value, dict) or set(value) != {"q", "u"}:
            _error(errors, "V", "must contain exactly q and u")
        else:
            _check_q(errors, "V.q", value.get("q"), EXPECTED_WIDTH["V"])
            _check_u(errors, "V.u", value.get("u"))

    if "X" in packet:
        refs = packet["X"]
        if not isinstance(refs, list):
            _error(errors, "X", "must be an array")
        else:
            seen: set[str] = set()
            for i, ref in enumerate(refs):
                if not isinstance(ref, str) or not re.fullmatch(r"X[0-9A-F]{2}", ref):
                    _error(errors, f"X[{i}]", "must match X00 through XFF")
                elif ref in seen:
                    _error(errors, f"X[{i}]", "duplicate reference")
                else:
                    seen.add(ref)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a canonical ΛH/1 JSON packet")
    parser.add_argument("packet", nargs="?", help="JSON file; omit to read stdin")
    args = parser.parse_args()
    try:
        text = Path(args.packet).read_text(encoding="utf-8") if args.packet else sys.stdin.read()
        packet = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2

    errors = validate_packet(packet)
    if errors:
        for err in errors:
            print(f"ERROR {err}", file=sys.stderr)
        return 1
    print("VALID ΛH/1 packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
