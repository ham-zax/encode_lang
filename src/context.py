"""Host-local context resolution for Lambda H/2.2.

Ambient bindings are endpoint-local state. They may contain arbitrary host
objects or text because this module never serializes them onto Lambda H wire.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType
from typing import Any, Mapping

from .protocol import XREF, references, require_valid

AMBIENT_ROLES = MappingProxyType({
    "goal": "X02",
    "artifact": "X03",
    "plan": "X06",
    "blocker": "X07",
    "environment": "X08",
    "output": "X09",
})
AMBIENT_REFS = frozenset(AMBIENT_ROLES.values())
_NAMESPACE = re.compile(r"(?:0|[1-9][0-9]*)")
_XREF = re.compile(XREF)


@dataclass(frozen=True)
class HostContext:
    """One host-local Lambda H context namespace and its exact X bindings."""

    namespace: str
    bindings: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.namespace, str) or not _NAMESPACE.fullmatch(self.namespace):
            raise ValueError("host context namespace must be a canonical decimal string")
        copied = dict(self.bindings)
        invalid = [ref for ref in copied if not isinstance(ref, str) or not _XREF.fullmatch(ref)]
        if invalid:
            raise ValueError("host context binding keys must be canonical X references")
        object.__setattr__(self, "bindings", MappingProxyType(copied))


@dataclass(frozen=True)
class ContextResolution:
    """Resolved exact X values plus any still-missing references."""

    resolved: Mapping[str, Any]
    missing: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "resolved", MappingProxyType(dict(self.resolved)))

    @property
    def complete(self) -> bool:
        return not self.missing


def ambient_ref(role: str) -> str:
    """Return the conventional X reference for one ambient-capable role."""
    try:
        return AMBIENT_ROLES[role]
    except KeyError as exc:
        raise ValueError(f"unknown ambient role {role!r}") from exc


def _required_x(packet: dict[str, Any]) -> list[str]:
    if packet.get("control") == "need":
        refs = list(packet["refs"])
    elif "control" in packet:
        return []
    else:
        refs = [ref for _, ref in references(packet) if ref.startswith("X")]
    # Preserve first semantic occurrence for deterministic missing/ref reporting.
    return list(dict.fromkeys(refs))


def resolve_context(packet: dict[str, Any], host_context: HostContext | None = None) -> ContextResolution:
    """Resolve exact X references without mutating or serializing host state.

    Packet-inline bindings have precedence. Host-local values are fallback only
    when the packet and host namespaces match exactly. A different namespace is
    treated as unavailable context, never as permission to retarget the packet.
    """
    require_valid(packet)
    required = _required_x(packet)
    if not required:
        return ContextResolution({}, ())

    inline = packet.get("X", {}) if "control" not in packet else {}
    same_namespace = (
        host_context is not None
        and packet.get("context") == host_context.namespace
    )
    resolved: dict[str, Any] = {}
    missing: list[str] = []
    for ref in required:
        if ref in inline:
            resolved[ref] = inline[ref]
        elif same_namespace and ref in host_context.bindings:
            resolved[ref] = host_context.bindings[ref]
        else:
            missing.append(ref)
    return ContextResolution(resolved, tuple(missing))
