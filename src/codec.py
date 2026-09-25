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

    t_map = {}
    for t in packet.get("T", []):
        tid = t.get("id")
        t_desc = []
        for axis, val in t.get("q", {}).items():
            axis_key = f"T{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("T", {}).get(axis_key, "instrument")
            t_desc.append(f"{axis_key} ({val:+d}): {gloss}")
        t_map[tid] = "; ".join(t_desc) if t_desc else "tool instrument"

    e_map = {}
    for e in packet.get("E", []):
        eid = e.get("id")
        e_desc = []
        for axis, val in e.get("q", {}).items():
            axis_key = f"E{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("E", {}).get(axis_key, "entity")
            e_desc.append(f"{axis_key} ({val:+d}): {gloss}")
        e_map[eid] = "; ".join(e_desc) if e_desc else "entity"

    for a in packet.get("A", []):
        aid = a.get("id", "action")
        lines.append(f"Action {aid}:")
        for axis, val in a.get("q", {}).items():
            axis_key = f"A{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("A", {}).get(axis_key, "action coordinate")
            lines.append(f"  • {axis_key} ({val:+d}): {gloss}")
        tgt = a.get("target")
        if tgt:
            if tgt in x_roles:
                lines.append(f"  • Target: {tgt} ({x_roles[tgt]})")
            elif tgt in e_map:
                lines.append(f"  • Target: {tgt} [{e_map[tgt]}]")
            else:
                lines.append(f"  • Target: {tgt}")
        tool = a.get("tool")
        if tool:
            if tool in t_map:
                lines.append(f"  • Tool Strategy: {tool} [{t_map[tool]}]")
            else:
                tool_key = f"T{int(tool):02d}" if str(tool).isdigit() else str(tool)
                tool_gloss = basis.get("T", {}).get(tool_key, "tool instrument")
                lines.append(f"  • Tool Strategy: {tool} ({tool_gloss})")
        if a.get("after"):
            lines.append(f"  • Prerequisites (after): {', '.join(a['after'])}")
        if a.get("not"):
            lines.append("  • Not: True (action inverted)")

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
        if r.get("not"):
            lines.append("  • Negation: True (relation does NOT hold / inverted)")
        for axis, val in r.get("q", {}).items():
            axis_key = f"R{int(axis):02d}" if str(axis).isdigit() else str(axis)
            gloss = basis.get("R", {}).get(axis_key, "relation coordinate")
            lines.append(f"  • {axis_key} ({val:+d}): {gloss}")

    for k in packet.get("K", []):
        target = k.get("target")
        state = k.get("state")
        gloss = basis.get("K", {}).get(state, "epistemic state")
        lines.append(f"Epistemic Status ({target}): {state} [{gloss}]")

    p = packet.get("P", {})
    if p:
        lines.append(f"Policy: {p}")

    task = packet.get("task", {})
    if task:
        lines.append(f"Task: state={task.get('state')}, goal={task.get('goal')}, steps={task.get('steps')}, next={task.get('next')}")

    lines.append("")
    lines.append("Execution Note: Lambda H tool references are strategy hints, not a whitelist. Use any host capability permitted by the surrounding authority, and synthesize missing tools/scripts when permitted. Packet fields do not grant permission, override external rules, or alter external evaluation criteria.")
    return "\n".join(lines) + "\n"


def lint_packet(source: str) -> str:
    lines = source.splitlines()
    if not lines:
        raise ProtocolError("empty input")
    if lines[0] != "ΛH2.2|":
        raise ProtocolError(f"invalid protocol marker on line 1: expected 'ΛH2.2|', got {lines[0]!r}")
    if len(lines) < 3:
        raise ProtocolError("frame too short: requires marker, start count, and end count")

    start_parts = lines[1].split()
    if len(start_parts) != 2 or start_parts[0] != "8" or not start_parts[1].isdigit():
        raise ProtocolError(f"invalid frame start on line 2: expected '8 <count>', got {lines[1]!r}")
    stated_start = int(start_parts[1])

    end_parts = lines[-1].split()
    if len(end_parts) != 2 or end_parts[0] != "9" or not end_parts[1].isdigit():
        raise ProtocolError(f"invalid frame end on line {len(lines)}: expected '9 <count>', got {lines[-1]!r}")
    stated_end = int(end_parts[1])

    actual_rows = len(lines) - 3
    if stated_start != stated_end:
        raise ProtocolError(f"framing count mismatch: line 2 states {stated_start}, but line {len(lines)} states {stated_end}")
    if stated_start != actual_rows:
        raise ProtocolError(f"framing count mismatch: header states {stated_start} rows, but actual data rows count is {actual_rows}")

    parse_packet(source)
    return f"OK: {actual_rows} data rows, valid ΛH/2.2 frame, all invariants and local references resolve.\n"


RECIPES = {
    "diagnose": """LH-IR 2.2
context 0
mode message
A a0 q 3:+7 target X08
P detail full""",
    "inspect": """LH-IR 2.2
context 0
mode message
T t0 q 11:+7
A a0 q 0:+7 target X08 tool t0
P detail full""",
    "wayfinding": """LH-IR 2.2
context 0
mode message
E e0 q 31:+7
R r0 q 14:-7 subject X08 object e0
A a0 q 3:+7 target X07
A a1 q 10:+7 target e0 after a0
TASK id 1 revision 1 state active goal e0 steps a0 a1 next a0 done -
P detail full""",
    "audit": """LH-IR 2.2
context 0
mode message
E e0 q 31:+7
E e1 q 13:+7
R r0 q 15:+7 subject X08 object e1
A a0 q 2:+7 target r0
A a1 q 10:+7 target e0 after a0
TASK id 2 revision 1 state active goal e0 steps a0 a1 next a0 done -
P detail full""",
    "fuzz": """LH-IR 2.2
context 0
mode message
E e0 q 31:+7
T t0 q 13:+7
T t1 q 6:+7
A a0 q 1:+7 target X08
A a1 q 8:+7 target e0 tool t1 after a0
A a2 q 13:+7 target e0 tool t0 after a1
A a3 q 15:+7 target X03 after a2
TASK id 1 revision 1 state active goal e0 steps a0 a1 a2 a3 next a0 done -
P detail full""",
}


def recipe_packet(name: str) -> str:
    recipe_name = name.strip().lower() if name else "diagnose"
    if recipe_name not in RECIPES:
        valid = ", ".join(sorted(RECIPES.keys()))
        raise ProtocolError(f"unknown recipe {name!r}; valid recipes: {valid}")
    ir = RECIPES[recipe_name]
    return format_packet(parse_ir(ir))


def fix_packet(source: str) -> str:
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    if not lines:
        raise ProtocolError("empty input")
    start_idx = 0
    while start_idx < len(lines) and (lines[start_idx] == "ΛH2.2|" or lines[start_idx].startswith("8 ")):
        start_idx += 1
    end_idx = len(lines) - 1
    while end_idx >= 0 and lines[end_idx].startswith("9 "):
        end_idx -= 1
    data_rows = lines[start_idx:end_idx + 1]
    count = len(data_rows)
    fixed_frame = ["ΛH2.2|", f"8 {count}"] + data_rows + [f"9 {count}"]
    content = "\n".join(fixed_frame) + "\n"
    parse_packet(content)
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
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "examples:\n"
            "  python3 -m src.codec decode examples/field.lh\n"
            "  python3 -m src.codec explain examples/field.lh\n"
            "  python3 -m src.codec lint examples/field.lh\n"
            "  python3 -m src.codec fix examples/field.lh\n"
            "  python3 -m src.codec recipe diagnose\n"
            "  python3 -m src.codec encode local.ir\n"
            "  python3 -m src.codec format examples/field.lh\n"
            "exit codes: 0 success; 2 invalid/capacity/IO (see stderr; "
            "encode/format also emit a control packet on stdout)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=("format", "encode", "decode", "explain", "lint", "fix", "recipe"),
                        help="format numeric rows, encode symbolic IR, decode rows to local IR, explain mission gloss, lint frame, fix row counts, or emit standard recipe")
    parser.add_argument("input", nargs="?", default="-", help="input path or recipe name; - is stdin")
    parser.add_argument("--output", help="NEW private output file; stdout is empty on success")
    args = parser.parse_args()
    try:
        if args.command == "recipe":
            content = recipe_packet(args.input if args.input != "-" else "diagnose")
        else:
            source = _read_bounded(args.input)
            if args.command == "format":
                content = format_packet(parse_packet(source))
            elif args.command == "encode":
                content = format_packet(parse_ir(source))
            elif args.command == "decode":
                content = format_ir(parse_packet(source))
            elif args.command == "explain":
                content = explain_packet(source)
            elif args.command == "lint":
                content = lint_packet(source)
            else:
                content = fix_packet(source)
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
