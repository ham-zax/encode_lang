"""Lambda H/2.2 numeric transport, semantic fields, and exact task graphs.

The receiver may use Python or the standalone bootstrap. Imports are lazy so
`python3 -m src.codec` has no eager module side effects.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "AMBIENT_REFS",
    "AMBIENT_ROLES",
    "CURRENT_CONTEXT",
    "ContextPreflight",
    "ContextResolution",
    "HostContext",
    "ProtocolError",
    "activation",
    "ambient_ref",
    "explain_packet",
    "fix_packet",
    "focus_field",
    "format_ir",
    "format_packet",
    "lint_packet",
    "load_host_context",
    "make_field",
    "parse_ir",
    "parse_packet",
    "preflight_context",
    "preflight_packet",
    "rank_candidates",
    "recipe_packet",
    "resolve_context",
    "schema",
    "shift_field",
    "validate_packet",
]


def __getattr__(name: str) -> Any:
    if name in {"make_field", "activation", "focus_field", "shift_field", "rank_candidates"}:
        from . import geometry
        return getattr(geometry, name)
    if name in {"parse_packet", "format_packet", "explain_packet", "lint_packet", "fix_packet", "recipe_packet", "preflight_packet"}:
        from . import codec
        return getattr(codec, name)
    if name in {"parse_ir", "format_ir"}:
        from . import ir
        return getattr(ir, name)
    if name in {"HostContext", "ContextResolution", "ContextPreflight", "AMBIENT_ROLES", "AMBIENT_REFS", "CURRENT_CONTEXT", "resolve_context", "preflight_context", "ambient_ref", "load_host_context"}:
        from . import context
        return getattr(context, name)
    if name in {"ProtocolError", "validate_packet", "schema"}:
        from . import protocol
        return getattr(protocol, name)
    raise AttributeError(name)
