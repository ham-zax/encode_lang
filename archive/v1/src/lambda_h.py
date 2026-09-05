#!/usr/bin/env python3
"""Deterministic codec utilities for the ΛH/1 semantic-transfer protocol.

This module does not infer semantic scores from natural language. It handles the
mechanical part of the protocol: score quantization, compact-wire parsing, and
canonical JSON formatting/validation.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

try:  # package import
    from .validate_packet import validate_packet
except ImportError:  # direct-script compatibility
    from validate_packet import validate_packet

ALPHABET = "0123456789ABCDE"
DIGIT_TO_SCORE = {digit: index - 7 for index, digit in enumerate(ALPHABET)}
SCORE_TO_DIGIT = {score: digit for digit, score in DIGIT_TO_SCORE.items()}
WIDTHS = {"E": 32, "R": 16, "A": 16, "T": 16, "P": 12, "V": 8}
HANDLE_PREFIX = {"E": "η", "R": "ρ", "A": "α", "T": "τ"}
PREFIX_LAYER = {prefix: layer for layer, prefix in HANDLE_PREFIX.items()}
REGION_LAYERS = ("E", "R", "A", "T")
BASIS_LAYERS = ("E", "R", "A", "T", "P", "V")
ID_RE = r"[0-9A-F]{2}"
WIRE_Q_RE = re.compile(r"^[0-E]+$")
CONTEXT_RE = re.compile(r"^X[0-9A-F]{2}$")
K_STATUS_RE = re.compile(r"^K0[0-8]$")


class CodecError(ValueError):
    """Raised when a ΛH/1 codec input violates the wire contract."""


def encode_scores(scores: list[int], *, width: int | None = None) -> str:
    """Quantize signed semantic scores in [-7,+7] into the 0-E wire alphabet."""
    if width is not None and len(scores) != width:
        raise CodecError(f"expected {width} scores, got {len(scores)}")
    encoded: list[str] = []
    for index, score in enumerate(scores):
        if isinstance(score, bool) or not isinstance(score, int):
            raise CodecError(f"score {index} must be an integer")
        try:
            encoded.append(SCORE_TO_DIGIT[score])
        except KeyError as exc:
            raise CodecError(f"score {index}={score} is outside -7..+7") from exc
    return "".join(encoded)


def decode_q(q: str, *, width: int | None = None) -> list[int]:
    """Decode a 0-E vector into signed semantic scores."""
    if not isinstance(q, str):
        raise CodecError("q must be a string")
    if width is not None and len(q) != width:
        raise CodecError(f"expected {width} wire digits, got {len(q)}")
    if not q or not WIRE_Q_RE.fullmatch(q):
        raise CodecError("q must contain only 0-E; F is reserved")
    return [DIGIT_TO_SCORE[digit] for digit in q]


def compare_q(q1: str, q2: str, *, width: int) -> dict[str, float | None]:
    """Compare two regions without assuming bit-identical prompt projections."""
    a = decode_q(q1, width=width)
    b = decode_q(q2, width=width)
    deltas = [x - y for x, y in zip(a, b)]
    mean_abs_delta = sum(abs(delta) for delta in deltas) / width
    rmse = math.sqrt(sum(delta * delta for delta in deltas) / width)
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    cosine = dot / (norm_a * norm_b) if norm_a and norm_b else None
    if cosine is not None:
        if abs(cosine - 1.0) < 1e-12:
            cosine = 1.0
        elif abs(cosine + 1.0) < 1e-12:
            cosine = -1.0
    return {
        "mean_abs_delta": mean_abs_delta,
        "rmse": rmse,
        "cosine": cosine,
    }


def _decode_u(digit: str) -> int:
    if len(digit) != 1 or digit not in DIGIT_TO_SCORE:
        raise CodecError("uncertainty must be one wire digit 0-E")
    return ALPHABET.index(digit)


def _encode_u(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 14:
        raise CodecError("uncertainty must be an integer from 0 through 14")
    return ALPHABET[value]


def _handle(layer: str, compact_id: str) -> str:
    if layer not in HANDLE_PREFIX or not re.fullmatch(ID_RE, compact_id):
        raise CodecError(f"invalid {layer} compact handle {compact_id!r}")
    return HANDLE_PREFIX[layer] + compact_id


def _compact_id(layer: str, handle: Any) -> str:
    prefix = HANDLE_PREFIX[layer]
    if not isinstance(handle, str) or not re.fullmatch(re.escape(prefix) + ID_RE, handle):
        raise CodecError(f"invalid {layer} handle {handle!r}")
    return handle[1:]


def _parse_region_entries(value: str, layer: str) -> list[dict[str, Any]]:
    if not value:
        raise CodecError(f"{layer} field cannot be empty")
    width = WIDTHS[layer]
    if layer == "R":
        pattern = re.compile(
            rf"^({ID_RE})\.([0-E]{{{width}}})\.([0-E])\(({ID_RE}),({ID_RE})\)$"
        )
    else:
        pattern = re.compile(rf"^({ID_RE})\.([0-E]{{{width}}})\.([0-E])$")

    entries: list[dict[str, Any]] = []
    raw_entries = re.split(r"(?<=\)),", value) if layer == "R" else value.split(",")
    for raw in raw_entries:
        match = pattern.fullmatch(raw)
        if not match:
            raise CodecError(f"invalid {layer} entry {raw!r}")
        compact_id, q, u_digit = match.group(1), match.group(2), match.group(3)
        entry: dict[str, Any] = {
            "handle": _handle(layer, compact_id),
            "q": q,
            "u": _decode_u(u_digit),
        }
        if layer == "R":
            entry["subject"] = _handle("E", match.group(4))
            entry["object"] = _handle("E", match.group(5))
        entries.append(entry)
    return entries


def _parse_k_entries(value: str) -> list[dict[str, Any]]:
    if not value:
        raise CodecError("K field cannot be empty")
    pattern = re.compile(rf"^([ERATX]{ID_RE}):(K0[0-8]):([01](?:\.\d+)?)$")
    entries: list[dict[str, Any]] = []
    for raw in value.split(","):
        match = pattern.fullmatch(raw)
        if not match:
            raise CodecError(f"invalid K entry {raw!r}")
        target, status, confidence_text = match.groups()
        confidence = float(confidence_text)
        if not 0.0 <= confidence <= 1.0:
            raise CodecError(f"K confidence {confidence_text} is outside 0..1")
        if target[0] in HANDLE_PREFIX:
            target = _handle(target[0], target[1:])
        entries.append({"target": target, "status": status, "confidence": confidence})
    return entries


def _parse_ack_fields(tail: str) -> dict[str, Any]:
    allowed = {"E", "R", "A", "T"}
    fields: dict[str, str] = {}
    for part in tail.split("|"):
        if "=" not in part:
            raise CodecError(f"invalid ACK field {part!r}; expected NAME=value")
        name, value = part.split("=", 1)
        if name not in allowed:
            raise CodecError(f"unknown ACK field {name!r}")
        if name in fields:
            raise CodecError(f"duplicate ACK field {name!r}")
        fields[name] = value
    if not fields:
        raise CodecError("ACK frame requires at least one summary field")

    ack: dict[str, Any] = {}
    for layer in ("E", "A", "T"):
        if layer not in fields:
            continue
        value = fields[layer]
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        if not value:
            raise CodecError(f"ACK {layer} field cannot be empty")
        ids = value.split(",")
        if any(not re.fullmatch(ID_RE, item) for item in ids):
            raise CodecError(f"ACK {layer} entries must be two-digit uppercase hex ids")
        ack[layer] = ids

    if "R" in fields:
        value = fields["R"]
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        pattern = re.compile(rf"^({ID_RE})\(({ID_RE}),({ID_RE})\)$")
        raw_entries = re.split(r"(?<=\)),", value)
        relations: list[dict[str, str]] = []
        for raw in raw_entries:
            match = pattern.fullmatch(raw)
            if not match:
                raise CodecError(f"invalid ACK relation entry {raw!r}")
            handle, subject, obj = match.groups()
            relations.append({"handle": handle, "subject": subject, "object": obj})
        ack["R"] = relations

    packet = {"protocol": "ΛH/1", "control": "ACK", "ack": ack}
    errors = validate_packet(packet)
    if errors:
        raise CodecError("invalid ACK frame: " + "; ".join(errors))
    return packet


def parse_compact(text: str) -> dict[str, Any]:
    """Parse normative compact ΛH1 data/control syntax into canonical JSON shape."""
    text = text.strip()
    if not text.startswith("ΛH1|"):
        raise CodecError("compact packet must start with 'ΛH1|'")

    tail = text[len("ΛH1|") :]
    if not tail:
        raise CodecError("compact packet has no fields")

    if tail in {"SYNC?", "CALFAIL"}:
        packet = {"protocol": "ΛH/1", "control": tail}
        errors = validate_packet(packet)
        if errors:
            raise CodecError("invalid control frame: " + "; ".join(errors))
        return packet

    if tail.startswith("READY|"):
        ready_fields: dict[str, str] = {}
        for part in tail[len("READY|") :].split("|"):
            if "=" not in part:
                raise CodecError(f"invalid READY field {part!r}")
            name, value = part.split("=", 1)
            if name in ready_fields:
                raise CodecError(f"duplicate READY field {name!r}")
            ready_fields[name] = value
        expected_names = {"BE", "BR", "BA", "BT", "BP", "BV"}
        if (
            set(ready_fields) != expected_names
            or ready_fields["BP"] != "02"
            or any(value != "01" for name, value in ready_fields.items() if name != "BP")
        ):
            raise CodecError("READY must contain exactly BE/BR/BA/BT/BV=01 and BP=02")
        packet = {
            "protocol": "ΛH/1",
            "control": "READY",
            "basis": {"E": "01", "R": "01", "A": "01", "T": "01", "P": "02", "V": "01"},
        }
        errors = validate_packet(packet)
        if errors:
            raise CodecError("invalid READY frame: " + "; ".join(errors))
        return packet

    if tail.startswith("ACK|"):
        return _parse_ack_fields(tail[len("ACK|") :])

    control: str | None = None
    if tail.startswith("SYNC|"):
        control = "SYNC"
        tail = tail[len("SYNC|") :]
        if not tail:
            raise CodecError("SYNC frame requires at least one binding or semantic field")

    allowed = {"E", "R", "A", "T", "K", "P", "X", "V"}
    fields: dict[str, str] = {}
    for part in tail.split("|"):
        if "=" not in part:
            raise CodecError(f"invalid field {part!r}; expected NAME=value")
        name, value = part.split("=", 1)
        if name not in allowed:
            raise CodecError(f"unknown compact field {name!r}")
        if name in fields:
            raise CodecError(f"duplicate compact field {name!r}")
        fields[name] = value

    packet: dict[str, Any] = {"protocol": "ΛH/1"}
    if control is not None:
        packet["control"] = control
    basis: dict[str, str] = {}

    for layer in REGION_LAYERS:
        if layer in fields:
            packet[layer] = _parse_region_entries(fields[layer], layer)
            basis[layer] = "01"

    if "K" in fields:
        packet["K"] = _parse_k_entries(fields["K"])

    if "P" in fields:
        match = re.fullmatch(r"([0-E]{12})\.([0-E])", fields["P"])
        if not match:
            raise CodecError("P must be <12 wire digits>.<uncertainty>")
        packet["P"] = {"q": match.group(1), "u": _decode_u(match.group(2))}
        basis["P"] = "02"

    if "V" in fields:
        match = re.fullmatch(r"([0-E]{8})\.([0-E])", fields["V"])
        if not match:
            raise CodecError("V must be <8 wire digits>.<uncertainty>")
        packet["V"] = {"q": match.group(1), "u": _decode_u(match.group(2))}
        basis["V"] = "01"

    if "X" in fields:
        if not fields["X"]:
            raise CodecError("X field cannot be empty")
        refs: list[str] = []
        for raw in fields["X"].split(","):
            ref = "X" + raw if re.fullmatch(ID_RE, raw) else raw
            if not CONTEXT_RE.fullmatch(ref):
                raise CodecError(f"invalid context reference {raw!r}")
            refs.append(ref)
        packet["X"] = refs

    if basis:
        packet["basis"] = basis

    errors = validate_packet(packet)
    if errors:
        raise CodecError("invalid compact packet: " + "; ".join(errors))
    return packet


def _format_k_target(target: Any) -> str:
    if not isinstance(target, str):
        raise CodecError("K target must be a string")
    if CONTEXT_RE.fullmatch(target):
        return target
    for layer, prefix in HANDLE_PREFIX.items():
        if re.fullmatch(re.escape(prefix) + ID_RE, target):
            return layer + target[1:]
    if re.fullmatch(rf"[ERATX]{ID_RE}", target):
        return target
    raise CodecError(
        "compact K targets must be E/R/A/T handles or X references; use JSON for free-form targets"
    )


def format_compact(packet: dict[str, Any]) -> str:
    """Format a canonical JSON packet as normative compact ΛH1 data/control syntax."""
    errors = validate_packet(packet)
    if errors:
        raise CodecError("invalid JSON packet: " + "; ".join(errors))

    control = packet.get("control")
    if control in {"SYNC?", "CALFAIL"}:
        return f"ΛH1|{control}"
    if control == "READY":
        return "ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01"
    if control == "ACK":
        ack = packet["ack"]
        ack_parts: list[str] = []
        for layer in ("E", "R", "A", "T"):
            values = ack.get(layer)
            if values is None:
                continue
            if layer == "R":
                rendered = ",".join(
                    f"{item['handle']}({item['subject']},{item['object']})" for item in values
                )
            else:
                rendered = ",".join(values)
            ack_parts.append(f"{layer}={rendered}")
        return "ΛH1|ACK|" + "|".join(ack_parts)

    parts: list[str] = []
    for layer in REGION_LAYERS:
        values = packet.get(layer)
        if not values:
            continue
        entries: list[str] = []
        for item in values:
            compact_id = _compact_id(layer, item["handle"])
            q = item["q"]
            decode_q(q, width=WIDTHS[layer])
            base = f"{compact_id}.{q}.{_encode_u(item['u'])}"
            if layer == "R":
                subject = _compact_id("E", item["subject"])
                obj = _compact_id("E", item["object"])
                base += f"({subject},{obj})"
            entries.append(base)
        parts.append(f"{layer}=" + ",".join(entries))

    if packet.get("K"):
        entries = []
        for item in packet["K"]:
            confidence = format(float(item["confidence"]), ".12g")
            entries.append(f"{_format_k_target(item['target'])}:{item['status']}:{confidence}")
        parts.append("K=" + ",".join(entries))

    if "P" in packet:
        q = packet["P"]["q"]
        decode_q(q, width=WIDTHS["P"])
        parts.append(f"P={q}.{_encode_u(packet['P']['u'])}")

    if packet.get("X"):
        refs = []
        for ref in packet["X"]:
            if not CONTEXT_RE.fullmatch(ref):
                raise CodecError(f"invalid context reference {ref!r}")
            refs.append(ref[1:])
        parts.append("X=" + ",".join(refs))

    if "V" in packet:
        q = packet["V"]["q"]
        decode_q(q, width=WIDTHS["V"])
        parts.append(f"V={q}.{_encode_u(packet['V']['u'])}")

    if not parts:
        raise CodecError("packet has no compact-encodable fields")
    prefix = "ΛH1|SYNC|" if control == "SYNC" else "ΛH1|"
    return prefix + "|".join(parts)


def _read_text(path: str | None) -> str:
    return Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()


def _layer_width(layer: str) -> int:
    try:
        return WIDTHS[layer.upper()]
    except KeyError as exc:
        raise CodecError("layer must be one of E, R, A, T, P, V") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ΛH/1 deterministic score and compact-wire codec"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser("score", help="quantize signed semantic scores to 0-E")
    score.add_argument("layer", choices=WIDTHS, help="semantic layer")
    score.add_argument("scores", nargs="+", type=int, help="scores in -7..+7")

    decode = sub.add_parser("decode", help="decode a wire vector to signed scores")
    decode.add_argument("layer", choices=WIDTHS, help="semantic layer")
    decode.add_argument("q", help="0-E wire vector")

    compare = sub.add_parser("compare", help="compare two regions from the same layer")
    compare.add_argument("layer", choices=WIDTHS, help="semantic layer")
    compare.add_argument("q1", help="first 0-E wire vector")
    compare.add_argument("q2", help="second 0-E wire vector")

    parse = sub.add_parser("parse", help="compact wire -> canonical JSON")
    parse.add_argument("wire", nargs="?", help="wire packet; omit to read stdin")

    compact = sub.add_parser("compact", help="canonical JSON -> compact wire")
    compact.add_argument("packet", nargs="?", help="JSON file; omit to read stdin")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        if args.command == "score":
            print(encode_scores(args.scores, width=_layer_width(args.layer)))
            return 0

        if args.command == "decode":
            print(" ".join(f"{score:+d}" for score in decode_q(args.q, width=_layer_width(args.layer))))
            return 0

        if args.command == "compare":
            metrics = compare_q(args.q1, args.q2, width=_layer_width(args.layer))
            print(json.dumps(metrics, indent=2))
            return 0

        if args.command == "parse":
            text = args.wire if args.wire is not None else sys.stdin.read()
            print(json.dumps(parse_compact(text), ensure_ascii=False, indent=2))
            return 0

        if args.command == "compact":
            packet = json.loads(_read_text(args.packet))
            if not isinstance(packet, dict):
                raise CodecError("canonical packet must be a JSON object")
            print(format_compact(packet))
            return 0

        parser.error("unknown command")
        return 2
    except (CodecError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
