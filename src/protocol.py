"""Lambda H/2.1 contract, structural validation, and disclosure inspection.

This module does not infer meaning, execute actions, authenticate senders, or
persist task state. Its schema checker implements only the vocabulary emitted
by schema(); it is not a general-purpose JSON Schema implementation.
"""
from __future__ import annotations

import json
import math
import re
from copy import deepcopy
from typing import Any

PROTOCOL = "ΛH/2.1"
PREFIX = "ΛH2.1|"
LAYERS = {"E": 32, "R": 16, "A": 16, "T": 16, "V": 8}
NODE_LAYERS = ("E", "R", "A", "T", "C")
REF = r"^(?:[eratc][0-9]+|X(?:0[0-9]|[1-9A-F][0-9A-F]))$"
XREF = r"^X(?:0[0-9]|[1-9A-F][0-9A-F])$"
NAME = {"type": "string", "minLength": 1, "maxLength": 128}
LITERAL = {"type": ["string", "number", "boolean", "null"]}
REFERENCE = {"type": "string", "pattern": REF}
XREFERENCE = {"type": "string", "pattern": XREF}
ACTION = {"type": "string", "pattern": r"^a[0-9]+$"}
CONDITION = {"type": "string", "pattern": r"^c[0-9]+$"}
BINARY_OPS = {"eq", "ne", "lt", "le", "gt", "ge"}


class ProtocolError(ValueError):
    """Malformed or inconsistent protocol input, not a semantic verdict."""


def object_shape(properties: dict[str, Any], required: tuple[str, ...] = ()) -> dict[str, Any]:
    return {"type": "object", "properties": properties,
            "required": list(required), "additionalProperties": False}


def array_shape(items: dict[str, Any], *, empty: bool = False, unique: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "array", "items": items, "minItems": 0 if empty else 1}
    if unique:
        result["uniqueItems"] = True
    return result


def choices(*values: str) -> dict[str, Any]:
    return {"type": "string", "enum": list(values)}


def region(layer: str) -> dict[str, Any]:
    # Shared axis/value constraints keep point and component-center schemas equal.
    return {"type": "object", "minProperties": 1,
            "propertyNames": {"enum": [f"{layer}{i:02d}" for i in range(LAYERS[layer])]},
            "additionalProperties": {"type": "integer", "enum": [-7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7]}}


def field_shape(layer: str) -> dict[str, Any]:
    """Weighted components with default and per-direction coordinate widths."""
    width = {"type": "number", "exclusiveMinimum": 0, "maximum": 14}
    pair = {"type": "array", "items": width, "minItems": 2, "maxItems": 2}
    bands = {"type": "object", "minProperties": 1,
             "propertyNames": region(layer)["propertyNames"], "additionalProperties": pair}
    component = object_shape({
        "q": region(layer), "s": width, "b": bands,
        "w": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
    }, ("q", "s"))
    return array_shape(component)


def node(layer: str, fields: dict[str, Any], required: tuple[str, ...]) -> dict[str, Any]:
    common = {"id": {"type": "string", "pattern": rf"^{layer.lower()}[0-9]+$"}}
    if layer in LAYERS:
        common.update({"q": region(layer), "f": field_shape(layer),
                       "u": {"type": "integer", "minimum": 0, "maximum": 7}})
    result = object_shape(common | fields, ("id",) + required)
    if layer in LAYERS:
        result["not"] = {"required": ["q", "f"]}
    return result


def schema() -> dict[str, Any]:
    alternatives = array_shape(LITERAL, unique=True)
    alternatives["minItems"] = 2
    entity = node("E", {"value": LITERAL, "choices": alternatives}, ())
    entity["anyOf"] = [{"required": [key]} for key in ("q", "f", "value", "choices")]
    tool = node("T", {"value": LITERAL}, ())
    tool["anyOf"] = [{"required": [key]} for key in ("q", "f", "value")]
    relation = node("R", {"subject": REFERENCE, "object": REFERENCE, "not": {"type": "boolean"}}, ("subject", "object"))
    relation["anyOf"] = [{"required": ["q"]}, {"required": ["f"]}]
    action = node("A", {
        "target": REFERENCE, "tool": {"type": "string", "pattern": r"^t[0-9]+$"},
        "after": array_shape(ACTION, unique=True), "when": CONDITION,
        "until": CONDITION, "not": {"type": "boolean"},
    }, ("target",))
    action["anyOf"] = [{"required": ["q"]}, {"required": ["f"]}]
    condition = node("C", {
        "op": choices("eq", "ne", "lt", "le", "gt", "ge", "exists", "done"),
        "left": REFERENCE, "right": REFERENCE,
    }, ("op", "left"))
    epistemic = object_shape({
        "target": REFERENCE,
        "state": choices(*[f"K{i:02d}" for i in range(9)]),
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "truth": {"type": "boolean"},
    }, ("target", "state"))
    policy = object_shape({
        "mutation": {"type": "boolean"}, "tools": {"type": "boolean"},
        "scope": array_shape(REFERENCE, unique=True),
        "detail": choices("brief", "normal", "full"),
        "reply": choices("natural", "packet"),
        "effort": {"type": "integer", "minimum": -7, "maximum": 7},
        "initiative": {"type": "integer", "minimum": -7, "maximum": 7},
    })
    policy["minProperties"] = 1
    task = object_shape({
        "id": NAME, "revision": {"type": "integer", "minimum": 0},
        "state": choices("active", "complete", "blocked", "cancelled"),
        "goal": REFERENCE, "steps": array_shape(ACTION, unique=True),
        "done": array_shape(ACTION, empty=True, unique=True), "next": ACTION,
        "stop": CONDITION, "blocker": REFERENCE,
    }, ("id", "revision", "state", "goal", "steps", "done"))
    bindings = {"type": "object", "minProperties": 1,
                "propertyNames": {"pattern": XREF}, "additionalProperties": LITERAL}
    data = object_shape({
        "protocol": {"const": PROTOCOL}, "context": NAME,
        "mode": choices("message", "handoff", "bind"),
        "E": array_shape(entity), "R": array_shape(relation),
        "A": array_shape(action), "T": array_shape(tool),
        "C": array_shape(condition), "K": array_shape(epistemic),
        "P": policy, "X": bindings, "V": region("V"), "task": task,
    }, ("protocol",))
    data["anyOf"] = [{"required": [key]} for key in (*NODE_LAYERS, "K", "P", "X", "V", "task")]
    ready = object_shape({"protocol": {"const": PROTOCOL}, "control": {"const": "ready"}}, ("protocol", "control"))
    need = object_shape({"protocol": {"const": PROTOCOL}, "control": {"const": "need"},
                         "context": NAME, "refs": array_shape(XREFERENCE, unique=True)},
                        ("protocol", "control", "context", "refs"))
    invalid = object_shape({"protocol": {"const": PROTOCOL}, "control": {"const": "invalid"},
                            "code": {"type": "integer", "minimum": 0, "maximum": 3}},
                           ("protocol", "control", "code"))
    return {"$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Lambda H/2.1 developer graph (numeric wire decoded first; graph validation also required)",
            "oneOf": [data, ready, need, invalid]}


def _matches_type(value: Any, kind: str) -> bool:
    return {
        "object": isinstance(value, dict), "array": isinstance(value, list),
        "string": isinstance(value, str), "boolean": isinstance(value, bool),
        "null": value is None,
        "integer": type(value) is int or (type(value) is float and math.isfinite(value) and value.is_integer()),
        "number": type(value) in (int, float) and (not isinstance(value, float) or math.isfinite(value)),
    }[kind]


def _same_json(left: Any, right: Any) -> bool:
    """JSON distinguishes booleans from numbers, but 1 and 1.0 are equal."""
    if type(left) in (int, float) and type(right) in (int, float):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_same_json(left[key], right[key]) for key in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(_same_json(a, b) for a, b in zip(left, right))
    return left == right


def _shape_errors(value: Any, shape: dict[str, Any], path: str = "packet") -> list[str]:
    errors: list[str] = []
    kind = shape.get("type")
    if kind is not None:
        kinds = kind if isinstance(kind, list) else [kind]
        if not any(_matches_type(value, item) for item in kinds):
            return [f"{path}: expected {kind}"]
    if "not" in shape and not _shape_errors(value, shape["not"], path):
        errors.append(f"{path}: incompatible fields or value")
    if "const" in shape and value != shape["const"]:
        errors.append(f"{path}: expected {shape['const']!r}")
    if "enum" in shape and value not in shape["enum"]:
        errors.append(f"{path}: not an allowed value")
    for keyword, exclusive in (("anyOf", False), ("oneOf", True)):
        if keyword in shape:
            alternatives = [_shape_errors(value, option, path) for option in shape[keyword]]
            matches = sum(not item for item in alternatives)
            if matches == 0:
                errors += min(alternatives, key=len) or [f"{path}: no matching shape"]
            elif exclusive and matches != 1:
                errors.append(f"{path}: ambiguous shape")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            return errors + [f"{path}: keys must be strings"]
        for key in shape.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        if len(value) < shape.get("minProperties", 0):
            errors.append(f"{path}: must not be empty")
        properties = shape.get("properties", {})
        extra = shape.get("additionalProperties", True)
        for key, item in value.items():
            if "propertyNames" in shape:
                errors += _shape_errors(key, shape["propertyNames"], f"{path} key")
            if key in properties:
                errors += _shape_errors(item, properties[key], f"{path}.{key}")
            elif extra is False:
                errors.append(f"{path}.{key}: unknown field")
            elif isinstance(extra, dict):
                errors += _shape_errors(item, extra, f"{path}.{key}")
    elif isinstance(value, list):
        if len(value) > shape.get("maxItems", math.inf):
            errors.append(f"{path}: too many items")
        if len(value) < shape.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if shape.get("uniqueItems") and any(any(_same_json(item, prior) for prior in value[:i]) for i, item in enumerate(value)):
            errors.append(f"{path}: duplicate items")
        if "items" in shape:
            for i, item in enumerate(value):
                errors += _shape_errors(item, shape["items"], f"{path}[{i}]")
    elif isinstance(value, str):
        if "pattern" in shape and re.fullmatch(shape["pattern"], value) is None:
            errors.append(f"{path}: invalid identifier")
        if len(value) < shape.get("minLength", 0) or len(value) > shape.get("maxLength", math.inf):
            errors.append(f"{path}: invalid length")
    elif type(value) in (int, float):
        if "exclusiveMinimum" in shape and value <= shape["exclusiveMinimum"]:
            errors.append(f"{path}: must exceed {shape['exclusiveMinimum']}")
        if value < shape.get("minimum", -math.inf) or value > shape.get("maximum", math.inf):
            errors.append(f"{path}: out of range")
    return errors


def references(packet: dict[str, Any]) -> list[tuple[str, str]]:
    """Only reference-bearing fields, never literal text that resembles an ID."""
    refs: list[tuple[str, str]] = []
    for layer, fields in (("R", ("subject", "object")), ("A", ("target", "tool", "when", "until")),
                          ("C", ("left", "right")), ("K", ("target",))):
        for index, item in enumerate(packet.get(layer, [])):
            for key in fields:
                if key in item:
                    refs.append((f"{layer}[{index}].{key}", item[key]))
            if layer == "A":
                refs += [(f"A[{index}].after", ref) for ref in item.get("after", [])]
    for key in ("goal", "next", "stop", "blocker"):
        if key in packet.get("task", {}):
            refs.append((f"task.{key}", packet["task"][key]))
    for key in ("steps", "done"):
        refs += [(f"task.{key}", ref) for ref in packet.get("task", {}).get(key, [])]
    refs += [("P.scope", ref) for ref in packet.get("P", {}).get("scope", [])]
    return refs


def validate_packet(packet: Any) -> list[str]:
    errors = _shape_errors(packet, schema())
    if errors:
        return errors
    if "control" in packet:
        return []
    nodes: dict[str, dict[str, Any]] = {}
    for layer in NODE_LAYERS:
        for item in packet.get(layer, []):
            if item["id"] in nodes:
                errors.append(f"{layer}: duplicate id {item['id']}")
            nodes[item["id"]] = item
    refs = references(packet)
    for path, ref in refs:
        if not ref.startswith("X") and ref not in nodes:
            errors.append(f"{path}: unbound local reference {ref}")
    external = {ref for _, ref in refs if ref.startswith("X")}
    if (external or "X" in packet) and "context" not in packet:
        errors.append("context: required whenever scoped X references or bindings are present")
    if packet.get("mode") == "handoff":
        for ref in sorted(external - packet.get("X", {}).keys()):
            errors.append(f"X: handoff is missing {ref}")
    if packet.get("mode") == "bind":
        if "X" not in packet or set(packet) - {"protocol", "mode", "context", "X"}:
            errors.append("mode: bind carries only protocol, mode, context, and nonempty X")
    for item in packet.get("C", []):
        binary = item["op"] in BINARY_OPS
        if binary != ("right" in item):
            errors.append(f"{item['id']}: right is required only for binary conditions")
        if item["op"] == "done" and not re.fullmatch(r"a[0-9]+", item["left"]):
            errors.append(f"{item['id']}: done requires an action reference")
    seen_k: set[str] = set()
    for item in packet.get("K", []):
        if item["target"] in seen_k:
            errors.append(f"K: duplicate epistemic target {item['target']}")
        seen_k.add(item["target"])
        if "truth" in item and not item["target"].startswith(("r", "c")):
            errors.append("K.truth: only a relation or condition can have proposition truth")
    actions = {item["id"]: item for item in packet.get("A", [])}
    # DFS checks the actual prerequisite graph, not array declaration order.
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(action_id: str) -> None:
        if action_id in visiting:
            errors.append(f"A.after: cycle at {action_id}")
            return
        if action_id in visited or action_id not in actions:
            return
        visiting.add(action_id)
        for dependency in actions[action_id].get("after", []):
            visit(dependency)
        visiting.remove(action_id)
        visited.add(action_id)
    for action_id in actions:
        visit(action_id)
    task = packet.get("task")
    if task:
        steps, done = task["steps"], set(task["done"])
        if not done <= set(steps):
            errors.append("task.done: contains an action outside task.steps")
        if any(actions.get(step, {}).get("not", False) for step in steps):
            errors.append("task.steps: prohibited actions cannot be executable steps")
        positions = {step: index for index, step in enumerate(steps)}
        for step in steps:
            for dependency in actions.get(step, {}).get("after", []):
                if dependency not in positions or positions[dependency] >= positions[step]:
                    errors.append(f"task.steps: prerequisite {dependency} must precede {step}")
                if step in done and dependency not in done:
                    errors.append(f"task.done: {step} lacks completed prerequisite {dependency}")
        if task["state"] == "active":
            remaining = [step for step in steps if step not in done]
            if not remaining or task.get("next") != remaining[0]:
                errors.append("task.next: active tasks require the first unfinished step")
            if "blocker" in task:
                errors.append("task.blocker: only blocked tasks carry a blocker")
        else:
            if "next" in task:
                errors.append("task.next: non-active tasks must not propose execution")
            if task["state"] == "complete" and done != set(steps):
                errors.append("task.done: complete requires every planned step accounted for")
            if (task["state"] == "blocked") != ("blocker" in task):
                errors.append("task.blocker: required exactly when state is blocked")
    return errors


def require_valid(packet: Any) -> None:
    errors = validate_packet(packet)
    if errors:
        raise ProtocolError("; ".join(errors))


def inspect_packet(packet: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Check disclosure/reference closure; report declared next, never execute it."""
    require_valid(packet)
    if "control" in packet:
        return {"control": packet["control"]}
    known: dict[str, Any] = {}
    if context is not None:
        context_shape = object_shape({"context": NAME, "X": {"type": "object", "propertyNames": {"pattern": XREF}, "additionalProperties": LITERAL}}, ("context", "X"))
        errors = _shape_errors(context, context_shape, "context file")
        if errors:
            raise ProtocolError("; ".join(errors))
        if context["context"] != packet.get("context"):
            raise ProtocolError("context namespace mismatch; never reuse bindings across namespaces")
        known.update(context["X"])
    for key, value in packet.get("X", {}).items():
        if key in known and not _same_json(known[key], value):
            raise ProtocolError(f"conflicting binding for {key}; use a new context namespace")
        known[key] = value
    required = sorted({ref for _, ref in references(packet) if ref.startswith("X")})
    missing = [ref for ref in required if ref not in known]
    task = packet.get("task", {})
    return {
        "context": packet.get("context"), "required": required, "missing": missing,
        "unused_inline_bindings": sorted(set(packet.get("X", {})) - set(required)),
        "declared_task_state": task.get("state"),
        "declared_next": task.get("next") if not missing else None,
        "note": "Structure and supplied state only; not meaning, evidence, permission, or execution verification.",
    }


def make_handoff(packet: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Include exactly referenced bindings, never dump the rest of a context."""
    require_valid(packet)
    if "control" in packet or packet.get("mode") == "bind":
        raise ProtocolError("handoff requires an ordinary message, not a control/binding frame")
    report = inspect_packet(packet, context)
    if report["missing"]:
        raise ProtocolError("missing bindings: " + ", ".join(report["missing"]))
    result = deepcopy(packet)
    result["mode"] = "handoff"
    values = context["X"] | packet.get("X", {})
    selected = {ref: values[ref] for ref in report["required"]}
    if selected:
        result["X"] = selected
    else:
        result.pop("X", None)
    require_valid(result)
    return result


if __name__ == "__main__":
    print(json.dumps(schema(), ensure_ascii=False, indent=2))
