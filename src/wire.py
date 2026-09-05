"""Numeric transport for the public 2.1 graph, not a cipher or word codebook.

Only fixed structural tags, references, coordinates, enum indices and typed
nontext scalars are represented. Text is deliberately rejected, not disguised
as byte codes/base64 or silently dropped. Readable developer JSON is separate.
"""
from __future__ import annotations

import math
import re
from typing import Any

from .protocol import LAYERS, PROTOCOL, ProtocolError, require_valid

MAX_INDEX = 9007199254740991
REF_PREFIXES = ("e", "r", "a", "t", "c", "X")
ENUMS = {
    "mode": ("message", "handoff", "bind"),
    "op": ("eq", "ne", "lt", "le", "gt", "ge", "exists", "done"),
    "epistemic": tuple(f"K{i:02d}" for i in range(9)),
    "detail": ("brief", "normal", "full"),
    "reply": ("natural", "packet"),
    "state": ("active", "complete", "blocked", "cancelled"),
    "control": ("ready", "need", "invalid"),
}
# The position in each table is a STRUCTURAL field tag, never a word identity.
RECORDS = {
    "root": (("context", "namespace"), ("mode", "enum:mode"),
             ("E", "nodes:E"), ("R", "nodes:R"), ("A", "nodes:A"), ("T", "nodes:T"),
             ("C", "nodes:C"), ("K", "nodes:K"), ("P", "record:P"),
             ("X", "bindings"), ("V", "q:V"), ("task", "record:task"),
             ("control", "enum:control"), ("refs", "refs"), ("code", "number")),
    "E": (("id", "id:e"), ("q", "q:E"), ("f", "field:E"), ("u", "number"),
          ("value", "scalar"), ("choices", "scalars")),
    "R": (("id", "id:r"), ("q", "q:R"), ("f", "field:R"), ("u", "number"),
          ("subject", "ref"), ("object", "ref"), ("not", "bool")),
    "A": (("id", "id:a"), ("q", "q:A"), ("f", "field:A"), ("u", "number"),
          ("target", "ref"), ("tool", "ref"), ("after", "refs"),
          ("when", "ref"), ("until", "ref"), ("not", "bool")),
    "T": (("id", "id:t"), ("q", "q:T"), ("f", "field:T"), ("u", "number"), ("value", "scalar")),
    "C": (("id", "id:c"), ("op", "enum:op"), ("left", "ref"), ("right", "ref")),
    "K": (("target", "ref"), ("state", "enum:epistemic"), ("confidence", "number"), ("truth", "bool")),
    "P": (("mutation", "bool"), ("tools", "bool"), ("scope", "refs"),
          ("detail", "enum:detail"), ("reply", "enum:reply"), ("effort", "number"), ("initiative", "number")),
    "task": (("id", "namespace"), ("revision", "number"), ("state", "enum:state"),
             ("goal", "ref"), ("steps", "refs"), ("done", "refs"),
             ("next", "ref"), ("stop", "ref"), ("blocker", "ref")),
}


def _index(value: Any, maximum: int = MAX_INDEX) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ProtocolError("wire index must be a nonnegative bounded integer")
    return value


def _number(value: Any) -> int | float:
    if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)):
        raise ProtocolError("wire number must be finite; booleans need their typed form")
    return value


def _array(value: Any, size: int | None = None) -> list[Any]:
    if not isinstance(value, list) or (size is not None and len(value) != size):
        raise ProtocolError("invalid wire array shape")
    return value


def _namespace(value: Any) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]*", value):
        raise ProtocolError("numeric wire requires a non-identifying decimal context/task ID; readable names stay local")
    return _index(int(value))


def _to_ref(value: str) -> list[int]:
    prefix = value[0]
    if prefix not in REF_PREFIXES:
        raise ProtocolError("invalid reference namespace")
    suffix = int(value[1:], 16) if prefix == "X" else _namespace(value[1:])
    return [REF_PREFIXES.index(prefix), suffix]


def _from_ref(value: Any) -> str:
    kind, identifier = _array(value, 2)
    prefix = REF_PREFIXES[_index(kind, len(REF_PREFIXES) - 1)]
    identifier = _index(identifier, 255 if prefix == "X" else MAX_INDEX)
    return f"X{identifier:02X}" if prefix == "X" else prefix + str(identifier)


def _to_scalar(value: Any) -> list[Any]:
    if type(value) is bool:
        return [1, int(value)]
    if value is None:
        return [2]
    if type(value) in (int, float):
        return [0, _number(value)]
    raise ProtocolError("text cannot enter the numeric wire; use a semantic field or an already shared X reference, not encoded text")


def _from_scalar(value: Any) -> Any:
    items = _array(value)
    if not items:
        raise ProtocolError("empty scalar")
    kind = _index(items[0], 2)
    if kind == 2:
        _array(items, 1)
        return None
    _array(items, 2)
    return _number(items[1]) if kind == 0 else bool(_index(items[1], 1))


def _pairs(value: Any, width: int | None = None) -> list[tuple[int, Any]]:
    pairs = []
    seen = set()
    for item in _array(value):
        key, content = _array(item, 2)
        key = _index(key, width - 1 if width is not None else MAX_INDEX)
        if key in seen:
            raise ProtocolError("duplicate wire tag or coordinate")
        seen.add(key)
        pairs.append((key, content))
    return pairs


def _to_record(value: dict[str, Any], name: str) -> list[Any]:
    table = RECORDS[name]
    permitted = {key for key, _ in table} | ({"protocol"} if name == "root" else set())
    if set(value) - permitted:
        raise ProtocolError("unmapped developer field cannot be silently omitted from wire")
    return [[tag, _to_value(value[key], kind)] for tag, (key, kind) in enumerate(table) if key in value]


def _from_record(value: Any, name: str) -> dict[str, Any]:
    table = RECORDS[name]
    return {table[tag][0]: _from_value(content, table[tag][1]) for tag, content in _pairs(value, len(table))}


def _component_table(layer: str) -> tuple[tuple[str, str], ...]:
    return (("q", "q:" + layer), ("s", "number"), ("b", "bands:" + layer), ("w", "number"))


def _to_value(value: Any, kind: str) -> Any:
    family, _, argument = kind.partition(":")
    if family == "number":
        return _number(value)
    if family == "namespace":
        return _namespace(value)
    if family == "id":
        if not value.startswith(argument):
            raise ProtocolError("wrong node namespace")
        return _namespace(value[1:])
    if family == "enum":
        return ENUMS[argument].index(value)
    if family == "bool":
        return int(value)
    if family == "ref":
        return _to_ref(value)
    if family == "refs":
        return [_to_ref(item) for item in value]
    if family == "scalar":
        return _to_scalar(value)
    if family == "scalars":
        return [_to_scalar(item) for item in value]
    if family == "q":
        return [[int(axis[1:]), coordinate] for axis, coordinate in sorted(value.items())]
    if family == "bands":
        return [[int(axis[1:]), pair] for axis, pair in sorted(value.items())]
    if family == "field":
        table = _component_table(argument)
        return [[[tag, _to_value(component[key], item_kind)] for tag, (key, item_kind) in enumerate(table) if key in component]
                for component in value]
    if family == "record":
        return _to_record(value, argument)
    if family == "nodes":
        return [_to_record(item, argument) for item in value]
    if family == "bindings":
        return [[int(ref[1:], 16), _to_scalar(item)] for ref, item in sorted(value.items())]
    raise ProtocolError("unknown transport field type")


def _from_value(value: Any, kind: str) -> Any:
    family, _, argument = kind.partition(":")
    if family == "number":
        return _number(value)
    if family == "namespace":
        return str(_index(value))
    if family == "id":
        return argument + str(_index(value))
    if family == "enum":
        return ENUMS[argument][_index(value, len(ENUMS[argument]) - 1)]
    if family == "bool":
        return bool(_index(value, 1))
    if family == "ref":
        return _from_ref(value)
    if family == "refs":
        return [_from_ref(item) for item in _array(value)]
    if family == "scalar":
        return _from_scalar(value)
    if family == "scalars":
        return [_from_scalar(item) for item in _array(value)]
    if family == "q":
        return {f"{argument}{axis:02d}": _number(item) for axis, item in _pairs(value, LAYERS[argument])}
    if family == "bands":
        return {f"{argument}{axis:02d}": [_number(width) for width in _array(item, 2)]
                for axis, item in _pairs(value, LAYERS[argument])}
    if family == "field":
        table = _component_table(argument)
        return [{table[tag][0]: _from_value(item, table[tag][1]) for tag, item in _pairs(component, len(table))}
                for component in _array(value)]
    if family == "record":
        return _from_record(value, argument)
    if family == "nodes":
        return [_from_record(item, argument) for item in _array(value)]
    if family == "bindings":
        return {f"X{ref:02X}": _from_scalar(item) for ref, item in _pairs(value, 256)}
    raise ProtocolError("unknown transport field type")


def _numeric_tree(value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            _numeric_tree(item)
    else:
        _number(value)


def encode_graph(packet: dict[str, Any]) -> list[Any]:
    require_valid(packet)
    result = _to_record(packet, "root")
    _numeric_tree(result)
    return result


def decode_graph(body: Any) -> dict[str, Any]:
    _numeric_tree(body)
    packet = {"protocol": PROTOCOL, **_from_record(body, "root")}
    require_valid(packet)
    return packet
