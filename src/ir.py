"""Model-facing symbolic IR for Lambda H/2.2.

The IR is a local structural representation of the developer graph. It is not
an agent-to-agent wire format and cannot carry arbitrary source text.
"""
from __future__ import annotations

import json
import math
import re
from typing import Any

from .protocol import LAYERS, PROTOCOL, ProtocolError, _same_json, require_valid

IR_HEADER = "LH-IR 2.2"
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
NODE_IDS = {"E": re.compile(r"e[0-9]+"), "R": re.compile(r"r[0-9]+"),
            "A": re.compile(r"a[0-9]+"), "T": re.compile(r"t[0-9]+"),
            "C": re.compile(r"c[0-9]+")}
REF = re.compile(r"(?:[eratc][0-9]+|X(?:0[0-9]|[1-9A-F][0-9A-F]))")
XREF = re.compile(r"X(?:0[0-9]|[1-9A-F][0-9A-F])")


class IRError(ProtocolError):
    """Malformed symbolic IR."""


def _number(token: str) -> int | float:
    if not NUMBER.fullmatch(token):
        raise IRError(f"expected number, got {token!r}")
    value = json.loads(token)
    if isinstance(value, float) and not math.isfinite(value):
        raise IRError("number must be finite")
    return value


def _integer(token: str) -> int:
    value = _number(token)
    if type(value) is not int:
        raise IRError(f"expected integer, got {token!r}")
    return value


def _bool(token: str) -> bool:
    if token not in {"0", "1"}:
        raise IRError("boolean must be 0 or 1")
    return token == "1"


def _ref(token: str) -> str:
    if not REF.fullmatch(token):
        raise IRError(f"invalid reference {token!r}")
    return token


def _scalar(token: str) -> Any:
    if token == "null":
        return None
    if token.startswith("b:"):
        return _bool(token[2:])
    if token.startswith("n:"):
        return _number(token[2:])
    raise IRError("scalar must be n:<number>, b:0, b:1, or null")


def _scalar_token(value: Any) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "b:1" if value else "b:0"
    if type(value) in (int, float) and (type(value) is int or math.isfinite(value)):
        return "n:" + json.dumps(value, allow_nan=False, separators=(",", ":"))
    raise IRError("IR scalar cannot contain text")


def _coord(token: str, layer: str) -> tuple[str, int]:
    parts = token.split(":")
    if len(parts) != 2 or not parts[0].isdigit():
        raise IRError(f"invalid {layer} coordinate {token!r}")
    axis = int(parts[0])
    raw = parts[1]
    if raw.startswith("+"):
        raw = raw[1:]
    value = _integer(raw)
    if not 0 <= axis < LAYERS[layer] or value == 0 or not -7 <= value <= 7:
        raise IRError(f"{layer} coordinate out of range")
    return f"{layer}{axis:02d}", value


def _coords(tokens: list[str], layer: str) -> dict[str, int]:
    if not tokens:
        raise IRError("q requires at least one coordinate")
    result: dict[str, int] = {}
    for token in tokens:
        axis, value = _coord(token, layer)
        if axis in result:
            raise IRError(f"duplicate coordinate {axis}")
        result[axis] = value
    return result


def _coord_tokens(value: dict[str, Any], layer: str) -> list[str]:
    result = []
    for axis, coordinate in sorted(value.items(), key=lambda item: int(item[0][1:])):
        if not re.fullmatch(rf"{layer}[0-9]{{2}}", axis):
            raise IRError(f"invalid {layer} axis {axis!r}")
        sign = "+" if coordinate > 0 else ""
        result.append(f"{int(axis[1:])}:{sign}{coordinate}")
    return result


def _band(token: str, layer: str) -> tuple[str, list[int | float]]:
    parts = token.split(":")
    if len(parts) != 3 or not parts[0].isdigit():
        raise IRError(f"invalid {layer} band {token!r}")
    axis = int(parts[0])
    if not 0 <= axis < LAYERS[layer]:
        raise IRError(f"{layer} band axis out of range")
    widths = [_number(parts[1]), _number(parts[2])]
    if any(width <= 0 or width > 14 for width in widths):
        raise IRError("band widths must be >0 and <=14")
    return f"{layer}{axis:02d}", widths


def _bands(tokens: list[str], layer: str) -> dict[str, list[int | float]]:
    if not tokens:
        raise IRError("b requires at least one band")
    result: dict[str, list[int | float]] = {}
    for token in tokens:
        axis, widths = _band(token, layer)
        if axis in result:
            raise IRError(f"duplicate band {axis}")
        result[axis] = widths
    return result


def _band_tokens(value: dict[str, Any], layer: str) -> list[str]:
    result = []
    for axis, widths in sorted(value.items(), key=lambda item: int(item[0][1:])):
        if not re.fullmatch(rf"{layer}[0-9]{{2}}", axis) or len(widths) != 2:
            raise IRError("invalid band")
        result.append(f"{int(axis[1:])}:{json.dumps(widths[0], allow_nan=False)}:{json.dumps(widths[1], allow_nan=False)}")
    return result


def _take(tokens: list[str], index: int, fields: set[str], *, empty_marker: bool = False) -> tuple[list[str], int]:
    start = index
    while index < len(tokens) and tokens[index] not in fields:
        index += 1
    values = tokens[start:index]
    if empty_marker and values == ["-"]:
        return [], index
    if not values:
        raise IRError("field requires a value")
    return values, index


def _node(packet: dict[str, Any], layer: str, node_id: str) -> dict[str, Any]:
    for item in packet.get(layer, []):
        if item["id"] == node_id:
            return item
    raise IRError(f"unknown {layer} node {node_id}")


def _parse_node(tokens: list[str], packet: dict[str, Any], layer: str) -> None:
    if len(tokens) < 2 or not NODE_IDS[layer].fullmatch(tokens[1]):
        raise IRError(f"{layer} requires a canonical node id")
    node_id = tokens[1]
    if any(item["id"] == node_id for item in packet.get(layer, [])):
        raise IRError(f"duplicate node {node_id}")
    node: dict[str, Any] = {"id": node_id}
    packet.setdefault(layer, []).append(node)
    fields_by_layer = {
        "E": {"q", "u", "value", "choices"},
        "R": {"q", "u", "subject", "object", "not"},
        "A": {"q", "u", "target", "tool", "after", "when", "until", "not"},
        "T": {"q", "u", "value"},
        "C": {"op", "left", "right"},
    }
    fields = fields_by_layer[layer]
    seen: set[str] = set()
    index = 2
    while index < len(tokens):
        field = tokens[index]
        if field not in fields or field in seen:
            raise IRError(f"invalid or duplicate {layer} field {field!r}")
        seen.add(field)
        index += 1
        if field == "q":
            values, index = _take(tokens, index, fields)
            node["q"] = _coords(values, layer)
        elif field in {"subject", "object", "target", "tool", "when", "until", "left", "right"}:
            if index >= len(tokens):
                raise IRError(f"{field} requires a reference")
            node[field] = _ref(tokens[index])
            index += 1
        elif field == "after":
            values, index = _take(tokens, index, fields)
            node[field] = [_ref(value) for value in values]
        elif field == "not":
            if index >= len(tokens):
                raise IRError("not requires 0 or 1")
            node[field] = _bool(tokens[index])
            index += 1
        elif field == "u":
            if index >= len(tokens):
                raise IRError("u requires an integer")
            node[field] = _integer(tokens[index])
            index += 1
        elif field == "value":
            if index >= len(tokens):
                raise IRError("value requires a typed scalar")
            node[field] = _scalar(tokens[index])
            index += 1
        elif field == "choices":
            values, index = _take(tokens, index, fields)
            node[field] = [_scalar(value) for value in values]
        elif field == "op":
            if index >= len(tokens):
                raise IRError("op requires a value")
            node[field] = tokens[index]
            index += 1
        else:
            raise IRError(f"unsupported {layer} field {field}")


def _parse_component(tokens: list[str], packet: dict[str, Any], components: dict[tuple[str, str], dict[int, dict[str, Any]]]) -> None:
    if len(tokens) < 7 or tokens[1] not in {"E", "R", "A", "T"}:
        raise IRError("F requires layer, node id, component index, q, and s")
    layer, node_id = tokens[1], tokens[2]
    _node(packet, layer, node_id)
    component_index = _integer(tokens[3])
    if component_index < 0:
        raise IRError("component index must be nonnegative")
    fields = {"q", "s", "b", "w"}
    component: dict[str, Any] = {}
    index = 4
    while index < len(tokens):
        field = tokens[index]
        if field not in fields or field in component:
            raise IRError(f"invalid or duplicate component field {field!r}")
        index += 1
        if field == "q":
            values, index = _take(tokens, index, fields)
            component["q"] = _coords(values, layer)
        elif field == "b":
            values, index = _take(tokens, index, fields)
            component["b"] = _bands(values, layer)
        else:
            if index >= len(tokens):
                raise IRError(f"{field} requires a number")
            component[field] = _number(tokens[index])
            index += 1
    if "q" not in component or "s" not in component:
        raise IRError("field component requires q and s")
    bucket = components.setdefault((layer, node_id), {})
    if component_index in bucket:
        raise IRError("duplicate component index")
    bucket[component_index] = component


def _parse_k(tokens: list[str], packet: dict[str, Any]) -> None:
    fields = {"target", "state", "confidence", "truth"}
    item: dict[str, Any] = {}
    index = 1
    while index < len(tokens):
        field = tokens[index]
        if field not in fields or field in item:
            raise IRError(f"invalid or duplicate K field {field!r}")
        index += 1
        if index >= len(tokens):
            raise IRError(f"{field} requires a value")
        if field == "target":
            item[field] = _ref(tokens[index])
        elif field == "state":
            item[field] = tokens[index]
        elif field == "confidence":
            item[field] = _number(tokens[index])
        else:
            item[field] = _bool(tokens[index])
        index += 1
    if not item:
        raise IRError("K cannot be empty")
    packet.setdefault("K", []).append(item)


def _parse_policy(tokens: list[str], packet: dict[str, Any]) -> None:
    if "P" in packet:
        raise IRError("duplicate P record")
    fields = {"mutation", "tools", "scope", "detail", "reply", "effort", "initiative"}
    item: dict[str, Any] = {}
    index = 1
    while index < len(tokens):
        field = tokens[index]
        if field not in fields or field in item:
            raise IRError(f"invalid or duplicate P field {field!r}")
        index += 1
        if field == "scope":
            values, index = _take(tokens, index, fields)
            item[field] = [_ref(value) for value in values]
            continue
        if index >= len(tokens):
            raise IRError(f"{field} requires a value")
        if field in {"mutation", "tools"}:
            item[field] = _bool(tokens[index])
        elif field in {"effort", "initiative"}:
            item[field] = _integer(tokens[index])
        else:
            item[field] = tokens[index]
        index += 1
    if not item:
        raise IRError("P cannot be empty")
    packet["P"] = item


def _parse_task(tokens: list[str], packet: dict[str, Any]) -> None:
    if "task" in packet:
        raise IRError("duplicate TASK record")
    fields = {"id", "revision", "state", "goal", "steps", "done", "next", "stop", "blocker"}
    item: dict[str, Any] = {}
    index = 1
    while index < len(tokens):
        field = tokens[index]
        if field not in fields or field in item:
            raise IRError(f"invalid or duplicate TASK field {field!r}")
        index += 1
        if field in {"steps", "done"}:
            values, index = _take(tokens, index, fields, empty_marker=field == "done")
            item[field] = [_ref(value) for value in values]
            continue
        if index >= len(tokens):
            raise IRError(f"{field} requires a value")
        if field in {"goal", "next", "stop", "blocker"}:
            item[field] = _ref(tokens[index])
        elif field == "revision":
            item[field] = _integer(tokens[index])
        else:
            item[field] = tokens[index]
        index += 1
    packet["task"] = item


def parse_ir(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise IRError("IR input must be text")
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n") if line.strip()]
    if not lines or lines[0] != IR_HEADER:
        raise IRError(f"expected {IR_HEADER!r}")
    packet: dict[str, Any] = {"protocol": PROTOCOL}
    components: dict[tuple[str, str], dict[int, dict[str, Any]]] = {}
    singleton = {"context", "mode", "V", "control", "refs", "code"}
    seen_root: set[str] = set()
    for line_number, line in enumerate(lines[1:], 2):
        tokens = line.split()
        head = tokens[0]
        try:
            if head in singleton:
                if head in seen_root:
                    raise IRError(f"duplicate {head}")
                seen_root.add(head)
                if head == "context":
                    if len(tokens) != 2:
                        raise IRError("context requires one namespace")
                    packet["context"] = tokens[1]
                elif head == "mode":
                    if len(tokens) != 2:
                        raise IRError("mode requires one value")
                    packet["mode"] = tokens[1]
                elif head == "V":
                    packet["V"] = _coords(tokens[1:], "V")
                elif head == "control":
                    if len(tokens) != 2:
                        raise IRError("control requires one value")
                    packet["control"] = tokens[1]
                elif head == "refs":
                    if len(tokens) < 2:
                        raise IRError("refs requires at least one X reference")
                    refs = []
                    for token in tokens[1:]:
                        if not XREF.fullmatch(token):
                            raise IRError("refs accepts only X references")
                        refs.append(token)
                    packet["refs"] = refs
                else:
                    if len(tokens) != 2:
                        raise IRError("code requires one integer")
                    packet["code"] = _integer(tokens[1])
            elif head in NODE_IDS:
                _parse_node(tokens, packet, head)
            elif head == "F":
                _parse_component(tokens, packet, components)
            elif head == "K":
                _parse_k(tokens, packet)
            elif head == "P":
                _parse_policy(tokens, packet)
            elif head == "TASK":
                _parse_task(tokens, packet)
            elif head == "X":
                if len(tokens) != 3 or not XREF.fullmatch(tokens[1]):
                    raise IRError("X requires X-ref and typed scalar")
                if tokens[1] in packet.setdefault("X", {}):
                    raise IRError("duplicate X binding")
                packet["X"][tokens[1]] = _scalar(tokens[2])
            else:
                raise IRError(f"unknown IR directive {head!r}")
        except (IRError, ProtocolError, ValueError) as exc:
            if isinstance(exc, IRError):
                raise IRError(f"line {line_number}: {exc}") from exc
            raise IRError(f"line {line_number}: {exc}") from exc
    for (layer, node_id), indexed in components.items():
        if sorted(indexed) != list(range(len(indexed))):
            raise IRError(f"{layer} {node_id}: component indexes must be contiguous from zero")
        node = _node(packet, layer, node_id)
        if "q" in node or "f" in node:
            raise IRError(f"{layer} {node_id}: q and f cannot coexist")
        node["f"] = [indexed[index] for index in range(len(indexed))]
    try:
        require_valid(packet)
    except ProtocolError as exc:
        raise IRError(str(exc)) from exc
    return packet


def _node_line(layer: str, item: dict[str, Any]) -> str:
    tokens = [layer, item["id"]]
    order = {
        "E": ("q", "u", "value", "choices"),
        "R": ("q", "u", "subject", "object", "not"),
        "A": ("q", "u", "target", "tool", "after", "when", "until", "not"),
        "T": ("q", "u", "value"),
        "C": ("op", "left", "right"),
    }[layer]
    for field in order:
        if field not in item:
            continue
        value = item[field]
        tokens.append(field)
        if field == "q":
            tokens.extend(_coord_tokens(value, layer))
        elif field in {"subject", "object", "target", "tool", "when", "until", "left", "right"}:
            tokens.append(value)
        elif field == "after":
            tokens.extend(value)
        elif field == "not":
            tokens.append("1" if value else "0")
        elif field == "u":
            tokens.append(str(value))
        elif field == "value":
            tokens.append(_scalar_token(value))
        elif field == "choices":
            tokens.extend(_scalar_token(choice) for choice in value)
        else:
            tokens.append(str(value))
    return " ".join(tokens)


def format_ir(packet: dict[str, Any]) -> str:
    require_valid(packet)
    lines = [IR_HEADER]
    if "context" in packet:
        lines.append(f"context {packet['context']}")
    if "mode" in packet:
        lines.append(f"mode {packet['mode']}")
    for layer in ("E", "R", "A", "T", "C"):
        for item in packet.get(layer, []):
            lines.append(_node_line(layer, item))
            for index, component in enumerate(item.get("f", [])):
                tokens = ["F", layer, item["id"], str(index), "q", *_coord_tokens(component["q"], layer),
                          "s", json.dumps(component["s"], allow_nan=False)]
                if "b" in component:
                    tokens.extend(["b", *_band_tokens(component["b"], layer)])
                if "w" in component:
                    tokens.extend(["w", json.dumps(component["w"], allow_nan=False)])
                lines.append(" ".join(tokens))
    for item in packet.get("K", []):
        tokens = ["K", "target", item["target"], "state", item["state"]]
        if "confidence" in item:
            tokens.extend(["confidence", json.dumps(item["confidence"], allow_nan=False)])
        if "truth" in item:
            tokens.extend(["truth", "1" if item["truth"] else "0"])
        lines.append(" ".join(tokens))
    if "P" in packet:
        item = packet["P"]
        tokens = ["P"]
        for field in ("mutation", "tools", "scope", "detail", "reply", "effort", "initiative"):
            if field not in item:
                continue
            tokens.append(field)
            if field in {"mutation", "tools"}:
                tokens.append("1" if item[field] else "0")
            elif field == "scope":
                tokens.extend(item[field])
            else:
                tokens.append(str(item[field]))
        lines.append(" ".join(tokens))
    for ref in sorted(packet.get("X", {}), key=lambda value: int(value[1:], 16)):
        lines.append(f"X {ref} {_scalar_token(packet['X'][ref])}")
    if "V" in packet:
        lines.append("V " + " ".join(_coord_tokens(packet["V"], "V")))
    if "task" in packet:
        item = packet["task"]
        tokens = ["TASK"]
        for field in ("id", "revision", "state", "goal", "steps", "done", "next", "stop", "blocker"):
            if field not in item:
                continue
            tokens.append(field)
            if field == "done" and not item[field]:
                tokens.append("-")
            elif field in {"steps", "done"}:
                tokens.extend(item[field])
            else:
                tokens.append(str(item[field]))
        lines.append(" ".join(tokens))
    if "control" in packet:
        lines.append(f"control {packet['control']}")
    if "refs" in packet:
        lines.append("refs " + " ".join(packet["refs"]))
    if "code" in packet:
        lines.append(f"code {packet['code']}")
    text = "\n".join(lines) + "\n"
    recovered = parse_ir(text)
    if not _same_json(packet, recovered):
        raise IRError("IR serialization did not preserve the graph")
    return text
