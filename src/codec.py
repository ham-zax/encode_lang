"""Optional, dependency-free Lambda H/2 file/transport tooling.

Receivers read the bootstrap and packets directly. This CLI is for authors and
integrators; it is neither an AI semantic encoder nor an encryption program.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .protocol import (PREFIX, PROTOCOL, ProtocolError, inspect_packet,
                       make_handoff, require_valid, schema)


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
    if text.startswith("ΛH1|"):
        raise ProtocolError("Lambda H/1 is retired; re-encode from source/context using MIGRATION.md")
    if text.startswith(PREFIX):
        packet = read_json(text[len(PREFIX):])
        if not isinstance(packet, dict):
            raise ProtocolError("wire body must be a JSON object")
        if "protocol" in packet:
            raise ProtocolError("wire prefix owns the version; omit protocol inside the wire body")
        packet = {"protocol": PROTOCOL, **packet}
    else:
        packet = read_json(text)
        if isinstance(packet, dict) and packet.get("protocol") == "ΛH/1":
            raise ProtocolError("Lambda H/1 is retired; re-encode from source/context using MIGRATION.md")
    require_valid(packet)
    return packet


def format_packet(packet: dict[str, Any]) -> str:
    require_valid(packet)
    body = {key: value for key, value in packet.items() if key != "protocol"}
    return PREFIX + json.dumps(body, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("parse", "validate wire/JSON and print canonical JSON"),
        ("format", "validate wire/JSON and print a bare wire packet"),
        ("inspect", "report binding requirements and declared task state without exposing binding values"),
        ("handoff", "include only required bindings from an explicitly supplied context file"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("packet", nargs="?", default="-", help="UTF-8 packet path, or - for stdin")
        if name in {"inspect", "handoff"}:
            command.add_argument("--context", required=name == "handoff", help="local context JSON path; never a secret key")
    commands.add_parser("schema", help="print the generated JSON Schema")
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
        else:
            context = read_json(_read(args.context)) if args.context else None
            if args.command == "inspect":
                result = inspect_packet(packet, context)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 2 if result.get("missing") else 0
            print(format_packet(make_handoff(packet, context)))
        return 0
    except (ProtocolError, OSError, UnicodeError, RecursionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
