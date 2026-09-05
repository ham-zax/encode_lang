"""Lambda H/2.1 numeric wire, graph inspection and optional field arithmetic.

Python is permitted for decoding/scoring. Normal wire contains no textual
payload; readable developer JSON and deliberately exported context are not
opaque communication. This tool neither executes actions nor encrypts data.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from .protocol import (PREFIX, PROTOCOL, ProtocolError, inspect_packet,
                       make_handoff, require_valid, schema)
from .wire import decode_graph, encode_graph
from .geometry import focus_field, rank_candidates, shift_field


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ProtocolError(f"non-finite JSON number: {value}")


def read_json(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ProtocolError(f"invalid JSON: {exc}") from exc


def parse_packet(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise ProtocolError("packet input must be text")
    text = text.strip()
    if text.startswith(("ΛH1|", "ΛH2|")):
        raise ProtocolError("older wire version; retain its decoder or re-encode with actual context using MIGRATION.md")
    if text.startswith(PREFIX):
        return decode_graph(read_json(text[len(PREFIX):]))
    packet = read_json(text)
    if isinstance(packet, dict) and packet.get("protocol") in {"ΛH/1", "ΛH/2"}:
        raise ProtocolError("older developer graph; migration requires actual source/context, not a version rename")
    require_valid(packet)
    return packet


def format_packet(packet: dict[str, Any]) -> str:
    return PREFIX + json.dumps(encode_graph(packet), separators=(",", ":"), allow_nan=False)


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def _field_node(packet: dict[str, Any], handle: str) -> tuple[str, dict[str, Any]]:
    for layer in ("E", "R", "A", "T"):
        for node in packet.get(layer, []):
            if node["id"] == handle:
                if "f" not in node:
                    raise ProtocolError("field arithmetic requires explicit f widths; a point q has no implied width")
                return layer, node
    raise ProtocolError("field node not found")


def _export_handoff(packet: dict[str, Any], context: dict[str, Any], output: str) -> dict[str, str]:
    combined = make_handoff(packet, context)
    selected = {"context": combined["context"], "X": combined.pop("X", {})}
    # Bindings are transferred alongside, not inside, the numeric wire. The
    # wire alone is not a self-contained handoff and must not claim to be one.
    combined.pop("mode", None)
    wire = format_packet(combined)
    sidecar = json.dumps(selected, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    destination = Path(output)
    destination.mkdir(mode=0o700)  # new directory only; never overwrite
    for name, content in (("packet.lh", wire + "\n"), ("context.private.json", sidecar)):
        path = destination / name
        with path.open("x", encoding="utf-8") as stream:
            path.chmod(0o600)
            stream.write(content)
    return {"packet": str(destination / "packet.lh"), "context": str(destination / "context.private.json")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("parse", "format", "inspect", "handoff", "score", "focus"):
        command = commands.add_parser(name)
        command.add_argument("packet", nargs="?", default="-", help="wire or developer-JSON path; - is stdin")
        if name in {"inspect", "handoff"}:
            command.add_argument("--context", required=name == "handoff", help="explicit local context sidecar")
        if name == "handoff":
            command.add_argument("--output", required=True, help="NEW private directory; parent must exist; exports disclosed context separately")
        if name in {"score", "focus"}:
            command.add_argument("--node", required=True, help="declared field node, such as e0")
        if name == "score":
            command.add_argument("--candidates", required=True, help="local ID -> numeric coordinates JSON; no built-in lexicon")
            command.add_argument("--minimum", required=True, type=float)
            command.add_argument("--margin", required=True, type=float)
        if name == "focus":
            command.add_argument("--scale", type=float, default=1.0)
            command.add_argument("--axis", action="append", help="restrict width change to selected axes")
            command.add_argument("--shift", action="append", default=[], help="signed coordinate displacement, e.g. E20=-1")
    commands.add_parser("schema", help="print developer-graph schema; decode numeric wire first")
    args = parser.parse_args()
    try:
        if args.command == "schema":
            print(json.dumps(schema(), ensure_ascii=False, indent=2))
            return 0
        packet = parse_packet(_read(args.packet))
        if args.command == "parse":
            print(json.dumps(packet, ensure_ascii=False, indent=2, allow_nan=False))
        elif args.command == "format":
            print(format_packet(packet))
        elif args.command in {"score", "focus"}:
            packet = deepcopy(packet)
            layer, node = _field_node(packet, args.node)
            if args.command == "score":
                result = rank_candidates(node["f"], read_json(_read(args.candidates)), layer=layer,
                                         minimum=args.minimum, margin=args.margin)
                print(json.dumps(result, indent=2, allow_nan=False))
            else:
                delta = {}
                for item in args.shift:
                    axis, separator, value = item.partition("=")
                    if not separator or axis in delta:
                        raise ProtocolError("each displacement must be a unique AXIS=number")
                    try:
                        delta[axis] = float(value)
                    except ValueError as exc:
                        raise ProtocolError("displacement must be numeric") from exc
                node["f"] = focus_field(node["f"], layer=layer, scale=args.scale, axes=args.axis)
                if delta:
                    node["f"] = shift_field(node["f"], delta, layer=layer)
                print(format_packet(packet))
        else:
            context = read_json(_read(args.context)) if args.context else None
            if args.command == "inspect":
                result = inspect_packet(packet, context)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 2 if result.get("missing") else 0
            print(json.dumps(_export_handoff(packet, context, args.output), indent=2))
        return 0
    except (ProtocolError, OSError, UnicodeError, RecursionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
