"""Directional semantic activation fields, not a word dictionary or encryption.

A field is a weighted sum of Gaussian-shaped bumps, normalized by total peak
weight. Lower/upper half-widths can differ along each anchor axis. Scores are
compatibility with supplied coordinates, NOT a calibrated probability or an
embedding learned from a model. Hard graph constraints remain exact.
"""
from __future__ import annotations

import math
from copy import deepcopy
from typing import Any

from .protocol import (LAYERS, ProtocolError, _shape_errors,
                       field_shape as field_schema, region as coordinates_schema)


def require_shape(value: Any, shape: dict[str, Any], path: str) -> None:
    errors = _shape_errors(value, shape, path)
    if errors:
        raise ProtocolError("; ".join(errors))


def _layer(layer: str) -> None:
    if layer not in LAYERS:
        raise ProtocolError("unknown semantic layer")


def make_field(center: dict[str, float], *, layer: str, width: float = 2.0,
               bands: dict[str, list[float]] | None = None, weight: float = 1.0) -> list[dict[str, Any]]:
    """Build one lobe; width is an explicit judgment, not evidence confidence."""
    _layer(layer)
    component: dict[str, Any] = {"q": dict(center), "s": width, "w": weight}
    if bands:
        component["b"] = deepcopy(bands)
    result = [component]
    require_shape(result, field_schema(layer), "field")
    return result


def _activation(field: list[dict[str, Any]], point: dict[str, float], layer: str) -> float:
    # Scale weights first so a valid very small relative peak does not underflow
    # merely because all components use the same tiny weight.
    largest = max(lobe.get("w", 1) for lobe in field)
    weights = [lobe.get("w", 1) / largest for lobe in field]
    terms = []
    for lobe, weight in zip(field, weights):
        distance = 0.0
        for i in range(LAYERS[layer]):
            axis = f"{layer}{i:02d}"
            delta = point.get(axis, 0) - lobe["q"].get(axis, 0)
            widths = lobe.get("b", {}).get(axis, (lobe["s"], lobe["s"]))
            ratio = delta / widths[0 if delta < 0 else 1]
            distance += ratio * ratio
            if distance > 1500:  # already below floating-point exp resolution
                break
        terms.append(weight * math.exp(-0.5 * distance))
    return math.fsum(terms) / math.fsum(weights)


def activation(field: list[dict[str, Any]], point: dict[str, float], *, layer: str) -> float:
    """Score a supplied point in [0,1]; omitted point axes are neutral zeroes."""
    _layer(layer)
    require_shape(field, field_schema(layer), "field")
    require_shape(point, {**coordinates_schema(layer), "minProperties": 0}, "point")
    return _activation(field, point, layer)


def focus_field(field: list[dict[str, Any]], *, layer: str, scale: float,
                axes: list[str] | None = None) -> list[dict[str, Any]]:
    """Scale widths without moving centers or pretending new evidence exists.

    A factor below one sharpens; above one broadens. Selected axes modify only
    their explicit widths. Out-of-range widths fail rather than being clamped.
    """
    _layer(layer)
    require_shape(field, field_schema(layer), "field")
    if type(scale) not in (int, float) or scale <= 0:
        raise ProtocolError("width scale must be positive and finite")
    try:
        scale = float(scale)
    except OverflowError as exc:
        raise ProtocolError("width scale is not representable") from exc
    if not math.isfinite(scale):
        raise ProtocolError("width scale must be positive and finite")
    if axes is not None:
        allowed = set(coordinates_schema(layer)["propertyNames"]["enum"])
        if not isinstance(axes, list) or not axes or any(not isinstance(axis, str) or axis not in allowed for axis in axes):
            raise ProtocolError("focus axes must be nonempty valid layer coordinates")
        if len(set(axes)) != len(axes):
            raise ProtocolError("duplicate focus axis")
    result = deepcopy(field)
    for lobe in result:
        if axes is None:
            lobe["s"] *= scale
            if "b" in lobe:
                lobe["b"] = {axis: [width * scale for width in pair] for axis, pair in lobe["b"].items()}
        else:
            bands = lobe.setdefault("b", {})
            for axis in axes:
                bands[axis] = [width * scale for width in bands.get(axis, (lobe["s"], lobe["s"]))]
    require_shape(result, field_schema(layer), "focused field")
    return result


def shift_field(field: list[dict[str, Any]], delta: dict[str, float], *, layer: str) -> list[dict[str, Any]]:
    """Translate every lobe, preserving widths and separation between senses."""
    _layer(layer)
    require_shape(field, field_schema(layer), "field")
    require_shape(delta, coordinates_schema(layer), "displacement")
    result = deepcopy(field)
    for lobe in result:
        for axis, shift in delta.items():
            value = lobe["q"].get(axis, 0) + shift
            if value == 0:
                lobe["q"].pop(axis, None)
            else:
                lobe["q"][axis] = value
    require_shape(result, field_schema(layer), "shifted field")
    return result


def rank_candidates(field: list[dict[str, Any]], candidates: dict[str, dict[str, float]], *,
                    layer: str, minimum: float, margin: float) -> dict[str, Any]:
    """Rank explicitly supplied context candidates and abstain on ambiguity.

    There is no hidden lexicon, model lookup, or nearest-word fallback. Cutoffs
    are caller-supplied acceptance policy, not universal semantic constants.
    Ties remain ambiguous even when the requested margin is zero.
    """
    _layer(layer)
    require_shape(field, field_schema(layer), "field")
    for name, cutoff in (("minimum", minimum), ("margin", margin)):
        if type(cutoff) not in (int, float) or not 0 <= cutoff <= 1 or not math.isfinite(cutoff):
            raise ProtocolError(f"{name} must be finite and between zero and one")
    if not isinstance(candidates, dict) or not candidates or any(not isinstance(key, str) or not key for key in candidates):
        raise ProtocolError("candidates must be a nonempty mapping of local IDs to coordinates")
    ranked = []
    for handle, point in candidates.items():
        require_shape(point, {**coordinates_schema(layer), "minProperties": 0}, "candidate coordinates")
        ranked.append({"id": handle, "score": _activation(field, point, layer)})
    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    best = ranked[0]["score"]
    gap = best - ranked[1]["score"] if len(ranked) > 1 else None
    status = "unresolved" if best < minimum else "ambiguous" if gap is not None and (gap <= 0 or gap < margin) else "selected"
    return {"status": status, "selected": ranked[0]["id"] if status == "selected" else None,
            "gap": gap, "candidates": ranked,
            "note": "Compatibility under supplied geometry and candidates only; not lexical identity or factual confidence."}
