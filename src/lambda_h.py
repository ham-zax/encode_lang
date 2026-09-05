#!/usr/bin/env python3
"""Deterministic codec utilities for the ΛH/1 semantic-transfer protocol.

This module does not infer semantic scores from natural language. It handles the
mechanical part of the protocol: score quantization, compact-wire parsing, and
canonical JSON formatting/validation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

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
    for raw in value.split(","):
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


def parse_compact(text: str) -> dict[str, Any]:
    """Parse normative compact ΛH1 wire syntax into canonical JSON shape."""
    text = text.strip()
    if not text.startswith("ΛH1|"):
        raise CodecError("compact packet must start with 'ΛH1|'")

    tail = text[len("ΛH1|") :]
    if not tail:
        raise CodecError("compact packet has no fields")

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
        basis["P"] = "01"

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
    """Format a canonical JSON packet as normative compact ΛH1 wire syntax."""
    errors = validate_packet(packet)
    if errors:
        raise CodecError("invalid JSON packet: " + "; ".join(errors))

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
    return "ΛH1|" + "|".join(parts)


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
