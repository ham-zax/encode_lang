"""Lambda H/2.2 shallow numeric rows over the existing semantic graph.

No semantic inference, execution, English reconstruction, or implicit context.
Numeric records are an internal assembly detail, never a second wire format.
"""
from __future__ import annotations

import json
import math
import re
from typing import Any

from .protocol import PREFIX, PROTOCOL, ProtocolError, validate_packet
from .wire import MAX_INDEX, RECORDS, _component_table, decode_graph, encode_graph

ROWS_PROTOCOL = PROTOCOL
ROWS_PREFIX = PREFIX
MAX_BYTES = 1024 * 1024
MAX_ROWS = 16384
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
INDEX = re.compile(r"0|[1-9][0-9]*")


class RowError(ProtocolError):
    """Structural failure carrying an existing numeric invalid code."""

    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code


class RowCapacityError(ProtocolError):
    """Input exceeds the declared endpoint limits; reject as invalid, do not truncate."""


def validate_rows_graph(packet: dict[str, Any]) -> None:
    errors = validate_packet(packet)
    if errors:
        code = 1 if any("unbound local reference" in error for error in errors) else 0
        if not code and any(error.startswith(("task.", "A.after:")) for error in errors):
            code = 3
        raise RowError("; ".join(errors), code)
    encode_graph(packet)


def _index(token: str, maximum: int = MAX_INDEX) -> int:
    if not INDEX.fullmatch(token) or len(token) > 16:
        raise RowError("expected canonical bounded index")
    value = int(token)
    if value > maximum:
        raise RowError("index out of range")
    return value


def _number(token: str) -> int | float:
    if not NUMBER.fullmatch(token):
        raise RowError("expected JSON number")
    try:
        value = json.loads(token)
    except ValueError as exc:
        raise RowError("invalid number") from exc
    if isinstance(value, float) and not math.isfinite(value):
        raise RowError("number must be finite")
    return value


def _payload(tokens: list[str], kind: str) -> Any:
    family = kind.partition(":")[0]
    if family in {"number", "namespace", "id", "enum", "bool"}:
        if len(tokens) != 1:
            raise RowError("expected one numeric value")
        return _number(tokens[0]) if family == "number" else _index(tokens[0])
    if family == "ref":
        if len(tokens) != 2:
            raise RowError("reference needs namespace and ID")
        return [_index(token) for token in tokens]
    if family in {"refs", "q", "bands"}:
        width = 3 if family == "bands" else 2
        if len(tokens) % width:
            raise RowError("incomplete pair or band")
        result = []
        for offset in range(0, len(tokens), width):
            axis = _index(tokens[offset])
            if family == "refs":
                result.append([axis, _index(tokens[offset + 1])])
            elif family == "q":
                result.append([axis, _number(tokens[offset + 1])])
            else:
                result.append([axis, [_number(token) for token in tokens[offset + 1:offset + 3]]])
        return result
    if family == "scalar":
        if not tokens:
            raise RowError("missing scalar type")
        tag = _index(tokens[0], 2)
        if len(tokens) != (1 if tag == 2 else 2):
            raise RowError("wrong scalar arity")
        if tag == 2:
            return [2]
        return [tag, _number(tokens[1]) if tag == 0 else _index(tokens[1], 1)]
    raise RowError("field requires its dedicated row form")


def _put(record: dict, key: Any, value: Any) -> None:
    if key in record:
        raise RowError("duplicate row property or item")
    record[key] = value


def _ordered(items: dict[int, Any]) -> list[Any]:
    if sorted(items) != list(range(len(items))):
        raise RowError("list positions must be contiguous from zero")
    return [items[position] for position in range(len(items))]


def _record(items: dict[int, Any]) -> list[list[Any]]:
    return [[tag, items[tag]] for tag in sorted(items)]


def parse_rows(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise RowError("packet must be text")
    if len(text) > MAX_BYTES or len(text.encode("utf-8")) > MAX_BYTES:
        raise RowCapacityError("packet byte limit exceeded")
    lines = text.replace("\r\n", "\n").removesuffix("\n").split("\n")
    if len(lines) < 3 or lines[0] != ROWS_PREFIX:
        raise RowError("expected exact 2.2 row marker and frame")
    if len(lines) - 3 > MAX_ROWS:
        raise RowCapacityError("packet row limit exceeded")
    frame = []
    for line in (lines[1], lines[-1]):
        tokens = line.split(" ")
        tokens = [token for token in tokens if token]
        if len(tokens) != 2:
            raise RowError("invalid frame boundary")
        frame.append([_index(token) for token in tokens])
    count = frame[0][1]
    if count > MAX_ROWS:
        raise RowCapacityError("declared row limit exceeded")
    if frame != [[8, count], [9, count]] or count != len(lines) - 3:
        raise RowError("row counts or frame boundaries disagree")

    root: dict[int, Any] = {}
    nodes: dict[int, dict[int, dict[int, Any]]] = {}
    components: dict[tuple[int, int], dict[int, dict[int, Any]]] = {}
    choices: dict[tuple[int, int], dict[int, Any]] = {}
    records: dict[int, dict[int, Any]] = {}
    bindings: dict[int, Any] = {}
    for line_number, line in enumerate(lines[2:-1], 3):
        tokens = [token for token in line.split(" ") if token]
        try:
            if not tokens:
                raise RowError("blank data row")
            row = _index(tokens[0], 5)
            if row == 4:
                if len(tokens) < 3:
                    raise RowError("incomplete binding row")
                _put(bindings, _index(tokens[1], 255), _payload(tokens[2:], "scalar"))
                continue
            minimum = {0: 2, 1: 4, 2: 5, 3: 3, 5: 5}[row]
            if len(tokens) < minimum:
                raise RowError("incomplete property row")
            root_tag = _index(tokens[1], len(RECORDS["root"]) - 1)
            name, root_kind = RECORDS["root"][root_tag]
            if row == 0:
                _put(root, root_tag, _payload(tokens[2:], root_kind))
            elif row == 3:
                if not root_kind.startswith("record:"):
                    raise RowError("expected P or task root tag")
                field = _index(tokens[2], len(RECORDS[name]) - 1)
                _put(records.setdefault(root_tag, {}), field,
                     _payload(tokens[3:], RECORDS[name][field][1]))
            else:
                if not root_kind.startswith("nodes:"):
                    raise RowError("expected node-layer root tag")
                position = _index(tokens[2], MAX_ROWS - 1)
                if row == 1:
                    field = _index(tokens[3], len(RECORDS[name]) - 1)
                    node = nodes.setdefault(root_tag, {}).setdefault(position, {})
                    _put(node, field, _payload(tokens[4:], RECORDS[name][field][1]))
                elif row == 2:
                    if name not in {"E", "R", "A", "T"}:
                        raise RowError("field component needs a semantic node")
                    component = _index(tokens[3], MAX_ROWS - 1)
                    field = _index(tokens[4], 3)
                    fields = components.setdefault((root_tag, position), {}).setdefault(component, {})
                    _put(fields, field, _payload(tokens[5:], _component_table(name)[field][1]))
                else:
                    if name != "E" or _index(tokens[3]) != 5:
                        raise RowError("choices rows require E.choices")
                    item = _index(tokens[4], MAX_ROWS - 1)
                    _put(choices.setdefault((root_tag, position), {}), item,
                         _payload(tokens[5:], "scalar"))
        except RowError as exc:
            raise RowError(f"line {line_number}: {exc}", exc.code) from exc

    for (tag, position), items in components.items():
        node = nodes.setdefault(tag, {}).setdefault(position, {})
        _put(node, 2, [_record(component) for component in _ordered(items)])
    for (tag, position), items in choices.items():
        node = nodes.setdefault(tag, {}).setdefault(position, {})
        _put(node, 5, _ordered(items))
    for tag, items in nodes.items():
        _put(root, tag, [_record(node) for node in _ordered(items)])
    for tag, fields in records.items():
        _put(root, tag, _record(fields))
    if bindings:
        _put(root, 9, _record(bindings))

    try:
        packet = decode_graph(_record(root))
    except ProtocolError as exc:
        message = str(exc)
        code = 1 if "unbound local reference" in message else 0
        if not code and ("task." in message or "A.after:" in message):
            code = 3
        raise RowError(message, code) from exc
    validate_rows_graph(packet)
    return packet


def _flat(value: Any, kind: str) -> list[int | float]:
    family = kind.partition(":")[0]
    if family in {"number", "namespace", "id", "enum", "bool"}:
        return [value]
    if family in {"ref", "scalar"}:
        return value
    if family in {"q", "refs"}:
        return [number for pair in value for number in pair]
    if family == "bands":
        return [number for axis, widths in value for number in (axis, *widths)]
    raise RowError("field requires dedicated formatting")


def format_rows(packet: dict[str, Any]) -> str:
    validate_rows_graph(packet)
    body = encode_graph(packet)
    rows = []
    for tag, value in body:
        name, kind = RECORDS["root"][tag]
        if kind.startswith("nodes:"):
            for position, node in enumerate(value):
                for field, data in node:
                    field_kind = RECORDS[name][field][1]
                    if field_kind.startswith("field:"):
                        for component, fields in enumerate(data):
                            for component_tag, payload in fields:
                                rows.append([2, tag, position, component, component_tag,
                                             *_flat(payload, _component_table(name)[component_tag][1])])
                    elif field_kind == "scalars":
                        rows.extend([5, tag, position, field, item, *scalar]
                                    for item, scalar in enumerate(data))
                    else:
                        rows.append([1, tag, position, field, *_flat(data, field_kind)])
        elif kind.startswith("record:"):
            rows.extend([3, tag, field, *_flat(data, RECORDS[name][field][1])]
                        for field, data in value)
        elif kind == "bindings":
            rows.extend([4, index, *scalar] for index, scalar in value)
        else:
            rows.append([0, tag, *_flat(value, kind)])
    if len(rows) > MAX_ROWS:
        raise RowCapacityError("formatted row limit exceeded")
    lines = [ROWS_PREFIX, f"8 {len(rows)}"]
    try:
        lines.extend(" ".join(json.dumps(number, allow_nan=False) for number in row) for row in rows)
    except ValueError as exc:
        raise RowError("number cannot be serialized") from exc
    lines.append(f"9 {len(rows)}")
    text = "\n".join(lines) + "\n"
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise RowCapacityError("formatted byte limit exceeded")
    return text
