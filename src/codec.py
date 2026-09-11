"""Lambda H/2.2 codec boundary between local symbolic IR and numeric transport.

`encode` maps local `LH-IR 2.2` to canonical numeric rows, `decode` maps numeric
rows to local IR, and `format` canonicalizes an already numeric frame. The codec
does not execute actions, infer semantic intent, or bind missing context.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .ir import IRError, format_ir, parse_ir
from .protocol import PROTOCOL, ProtocolError, _same_json
from .rows import MAX_BYTES, RowCapacityError, RowError, format_rows, parse_rows


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ProtocolError(f"non-finite JSON number: {value}")


def read_json(text: str) -> Any:
    """Read local developer/context data; this is not a runtime wire parser."""
    try:
        return json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except (ValueError, RecursionError) as exc:
        raise ProtocolError(f"invalid JSON: {exc}") from exc


def parse_packet(text: str) -> dict[str, Any]:
    return parse_rows(text)


def format_packet(packet: dict[str, Any]) -> str:
    content = format_rows(packet)
    recovered = parse_rows(content)
    if not _same_json(packet, recovered) or format_rows(recovered) != content:
        raise RowError("row serialization did not preserve the graph")
    return content


def _read_bounded(path: str) -> str:
    if path == "-":
        text = sys.stdin.read(MAX_BYTES + 1)
    else:
        with Path(path).open(encoding="utf-8", newline="") as stream:
            text = stream.read(MAX_BYTES + 1)
    if len(text) > MAX_BYTES or len(text.encode("utf-8")) > MAX_BYTES:
        raise RowCapacityError("packet byte limit exceeded")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("format", "encode", "decode"),
                        help="format numeric rows, encode symbolic IR, or decode rows to local IR")
    parser.add_argument("input", nargs="?", default="-", help="input path; - is stdin")
    parser.add_argument("--output", help="NEW private output file; stdout is empty on success")
    args = parser.parse_args()
    try:
        source = _read_bounded(args.input)
        if args.command == "format":
            content = format_packet(parse_packet(source))
        elif args.command == "encode":
            content = format_packet(parse_ir(source))
        else:
            content = format_ir(parse_packet(source))
        if args.output is None:
            sys.stdout.write(content)
        else:
            descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        return 0
    except (ProtocolError, OSError, UnicodeError, RecursionError) as exc:
        if args.command == "decode":
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        capacity = isinstance(exc, (RowCapacityError, RecursionError, OSError))
        control = "abstain" if capacity else "invalid"
        code = 4 if capacity else exc.code if isinstance(exc, RowError) else 0
        if isinstance(exc, IRError):
            code = 0
        sys.stdout.write(format_rows({"protocol": PROTOCOL, "control": control, "code": code}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
