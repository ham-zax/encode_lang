"""Lambda H/2.1 numeric transport, semantic fields, and exact task graphs.

The receiver may use Python or the standalone bootstrap. Imports are lazy so
`python3 -m src.codec` has no eager module side effects.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "ProtocolError", "parse_packet", "format_packet", "validate_packet",
    "inspect_packet", "make_handoff", "schema",
    "make_field", "activation", "focus_field", "shift_field", "rank_candidates",
]


def __getattr__(name: str) -> Any:
    if name in {"make_field", "activation", "focus_field", "shift_field", "rank_candidates"}:
        from . import geometry
        return getattr(geometry, name)
    if name in {"parse_packet", "format_packet"}:
        from . import codec
        return getattr(codec, name)
    if name in {"ProtocolError", "validate_packet", "inspect_packet", "make_handoff", "schema"}:
        from . import protocol
        return getattr(protocol, name)
    raise AttributeError(name)
