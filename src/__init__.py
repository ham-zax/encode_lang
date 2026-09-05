"""Optional local tooling for the Lambda H/2 semantic notation.

The receiving agent needs the standalone bootstrap, not this Python package.
Imports are lazy so `python3 -m src.codec` has no eager module side effects.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "ProtocolError", "parse_packet", "format_packet", "validate_packet",
    "inspect_packet", "make_handoff", "schema",
]


def __getattr__(name: str) -> Any:
    if name in {"parse_packet", "format_packet"}:
        from . import codec
        return getattr(codec, name)
    if name in {"ProtocolError", "validate_packet", "inspect_packet", "make_handoff", "schema"}:
        from . import protocol
        return getattr(protocol, name)
    raise AttributeError(name)
