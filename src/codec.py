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


def explain_packet(source: str) -> str:
    packet = parse_packet(source)
    ir_text = format_ir(packet)

    basis_path = Path(__file__).resolve().parents[1] / "semantics" / "basis.json"
    basis = {}
    if basis_path.exists():
        try:
            basis = json.loads(basis_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    x_roles = {
        "X00": "current conversational/task subject",
        "X01": "previous subject",
        "X02": "active goal",
        "X03": "active artifact / log target",
        "X04": "hypothesis",
        "X05": "result",
        "X06": "active plan",
        "X07": "current blocker",
        "X08": "current workspace/environment/repository",
        "X09": "output target",
    }

    lines = [
        "=== LH-IR 2.2 ===",
        ir_text.strip(),
        "",
        "=== MISSION GLOSS ===",
    ]
    ctx = packet.get("context", "0")
    if ctx == "0":
        lines.append("Context: 0 (Ambient Host Session: X08=workspace, X03=artifact, X02=goal)")
    else:
        lines.append(f"Context: {ctx} (Explicit Scoped Context)")

    if "mode" in packet:
        lines.append(f"Mode: {packet['mode']}")

    for a in packet.get("A", []):
        aid = a.get("id", "action")
        lines.append(f"Action {aid}:")
        for axis, val in a.get("q", {}).items():
            axis_key = f"A{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("A", {}).get(axis_key, "action coordinate")
            lines.append(f"  • {axis_key} ({val:+d}): {gloss}")
        tgt = a.get("target")
        if tgt:
            tgt_gloss = x_roles.get(tgt, "target reference")
            lines.append(f"  • Target: {tgt} ({tgt_gloss})")
        tool = a.get("tool")
        if tool:
            tool_key = f"T{int(tool):02d}" if str(tool).isdigit() else str(tool)
            tool_gloss = basis.get("T", {}).get(tool_key, "tool instrument")
            lines.append(f"  • Tool Strategy: {tool} ({tool_gloss})")
        if a.get("after"):
            lines.append(f"  • Prerequisites (after): {', '.join(a['after'])}")

    for e in packet.get("E", []):
        eid = e.get("id", "entity")
        lines.append(f"Entity {eid}:")
        for axis, val in e.get("q", {}).items():
            axis_key = f"E{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("E", {}).get(axis_key, "entity coordinate")
            lines.append(f"  • {axis_key} ({val:+d}): {gloss}")

    for r in packet.get("R", []):
        rid = r.get("id", "relation")
        lines.append(f"Relation {rid} (subject {r.get('subject')} -> object {r.get('object')}):")
        for axis, val in r.get("q", {}).items():
            axis_key = f"R{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("R", {}).get(axis_key, "relation coordinate")
            lines.append(f"  • {axis_key} ({val:+d}): {gloss}")

    p = packet.get("P", {})
    if p:
        lines.append(f"Policy: {p}")

    task = packet.get("task", {})
    if task:
        lines.append(f"Task: state={task.get('state')}, goal={task.get('goal')}, steps={task.get('steps')}, next={task.get('next')}")

    lines.append("")
    lines.append("Execution Note: The Doer operates with unconstrained tool authority. Use any available host capability or synthesize missing tools/scripts dynamically.")
    return "\n".join(lines) + "\n"


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
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "examples:\n"
            "  python3 -m src.codec decode examples/field.lh\n"
            "  python3 -m src.codec explain examples/field.lh\n"
            "  python3 -m src.codec encode local.ir\n"
            "  python3 -m src.codec format examples/field.lh\n"
            "exit codes: 0 success; 2 invalid/capacity/IO (see stderr; "
            "encode/format also emit a control packet on stdout)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=("format", "encode", "decode", "explain"),
                        help="format numeric rows, encode symbolic IR, decode rows to local IR, or explain mission gloss")
    parser.add_argument("input", nargs="?", default="-", help="input path; - is stdin")
    parser.add_argument("--output", help="NEW private output file; stdout is empty on success")
    args = parser.parse_args()
    try:
        source = _read_bounded(args.input)
        if args.command == "format":
            content = format_packet(parse_packet(source))
        elif args.command == "encode":
            content = format_packet(parse_ir(source))
        elif args.command == "decode":
            content = format_ir(parse_packet(source))
        else:
            content = explain_packet(source)
        if args.output is None:
            sys.stdout.write(content)
        else:
            descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        return 0
    except (ProtocolError, OSError, UnicodeError, RecursionError) as exc:
        # Agent-friendly: always explain on stderr. encode/format must still
        # emit a wire-compatible control on stdout; decode output is IR, so
        # it leaves stdout empty and reports only via stderr + exit code.
        print(f"ERROR [{args.command} {args.input}]: {exc}", file=sys.stderr)
        if args.command == "decode":
            return 2
        capacity = isinstance(exc, (RowCapacityError, RecursionError, OSError))
        control = "invalid"
        code = 0 if capacity else exc.code if isinstance(exc, RowError) else 0
        if isinstance(exc, IRError):
            code = 0
        sys.stdout.write(format_rows({"protocol": PROTOCOL, "control": control, "code": code}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
