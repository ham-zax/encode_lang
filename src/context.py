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
    "subject": "X00",
    "goal": "X02",
    "artifact": "X03",
    "plan": "X06",
    "blocker": "X07",
    "environment": "X08",
    "output": "X09",
})
AMBIENT_REFS = frozenset(AMBIENT_ROLES.values())
CURRENT_CONTEXT = "0"
_NAMESPACE = re.compile(r"(?:0|[1-9][0-9]*)")
_XREF = re.compile(XREF)
_UNSET = object()


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

    @classmethod
    def current(cls, bindings: Mapping[str, Any]) -> "HostContext":
        """Build context 0 from values already grounded by the active host session.

        Callers supply the current bindings; this API never searches the filesystem
        or enumerates candidate repositories to discover X08.
        """
        return cls(CURRENT_CONTEXT, bindings)


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


@dataclass(frozen=True)
class ContextPreflight:
    """Encoder/local classification of every required X reference."""

    classifications: Mapping[str, str]
    unresolved: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "classifications", MappingProxyType(dict(self.classifications)))

    @property
    def complete(self) -> bool:
        return not self.unresolved


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


def preflight_context(
    packet: dict[str, Any],
    host_context: HostContext | None = None,
    *,
    current_subject: Any = _UNSET,
) -> ContextPreflight:
    """Classify required X references before transport or execution.

    `current_subject` is accepted only for context 0 and only as the already-
    established single conversational/task subject. Callers must omit it when
    the subject is absent or ambiguous; this module never infers from transcript
    text, cwd, filenames, or repository discovery.
    """
    require_valid(packet)
    required = _required_x(packet)
    inline = packet.get("X", {}) if "control" not in packet else {}
    same_namespace = (
        host_context is not None
        and packet.get("context") == host_context.namespace
    )
    classifications: dict[str, str] = {}
    unresolved: list[str] = []
    for ref in required:
        if ref in inline:
            classifications[ref] = "packet-bound"
        elif same_namespace and ref in host_context.bindings:
            classifications[ref] = "host-ambient-resolvable"
        elif (
            packet.get("context") == CURRENT_CONTEXT
            and ref == "X00"
            and current_subject is not _UNSET
        ):
            classifications[ref] = "conversation-ambient-resolvable"
        else:
            classifications[ref] = "unresolved"
            unresolved.append(ref)
    return ContextPreflight(classifications, tuple(unresolved))


def resolve_context(
    packet: dict[str, Any],
    host_context: HostContext | None = None,
    *,
    current_subject: Any = _UNSET,
) -> ContextResolution:
    """Resolve exact X references without mutating or serializing host state.

    Packet-inline bindings have precedence, followed by exact matching host
    bindings. Context 0 may additionally resolve X00 from a caller-supplied
    single conversational/task subject that was already established before the
    packet arrived. A different nonzero namespace is unavailable context, never
    permission to retarget the packet.
    """
    preflight = preflight_context(
        packet,
        host_context,
        current_subject=current_subject,
    )
    if not preflight.classifications:
        return ContextResolution({}, ())

    inline = packet.get("X", {}) if "control" not in packet else {}
    same_namespace = (
        host_context is not None
        and packet.get("context") == host_context.namespace
    )
    resolved: dict[str, Any] = {}
    for ref, classification in preflight.classifications.items():
        if classification == "packet-bound":
            resolved[ref] = inline[ref]
        elif classification == "host-ambient-resolvable":
            resolved[ref] = host_context.bindings[ref]
        elif classification == "conversation-ambient-resolvable":
            resolved[ref] = current_subject
    return ContextResolution(resolved, preflight.unresolved)
