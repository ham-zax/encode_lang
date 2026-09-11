# Lambda H/2.2 Agent-Native Ambient Context Design

**Status:** implemented in the current working tree.

## Goal

Make deictic agent requests such as “this repo”, “the current artifact”, and “continue the plan” map to exact host-grounded context references instead of generic semantic stand-ins, while preserving the existing opaque Lambda H/2.2 wire.

## Core invariant

Ambient context is host-grounded, context-scoped, and never model-guessed.

The numeric wire remains unchanged. A packet carries only its existing numeric `context` namespace and X references. Exact local objects, paths, strings, handles, or other host state remain outside transport.

## Ambient-capable roles

These conventional references may be selected automatically for deictic source meaning when the host has explicitly established the corresponding binding:

| Reference | Ambient role |
|---|---|
| `X02` | active goal |
| `X03` | active artifact |
| `X06` | active plan |
| `X07` | current blocker |
| `X08` | current workspace/environment/repository |
| `X09` | output/result target |

`X00`, `X01`, `X04`, and `X05` keep their existing contextual meanings but are not automatically selected from deictic wording by this feature.

Ambient-capable does not mean globally or always bound. The host establishes only values it actually knows.

## Host-local context API

`src/context.py` owns host-local context resolution. It defines:

- `AMBIENT_ROLES`: the fixed role-to-X mapping above;
- `AMBIENT_REFS`: the corresponding set of X references;
- `HostContext(namespace, bindings)`: one local namespace plus arbitrary endpoint-local X bindings;
- `ContextResolution(resolved, missing)`: deterministic resolution output;
- `resolve_context(packet, host_context)`: resolve packet X references without changing the packet;
- `ambient_ref(role)`: return the conventional X reference for an ambient role.

Host-local binding values are deliberately outside the protocol schema and may be real endpoint objects or textual identities. They are never serialized by `src.rows`, `src.ir`, or `src.codec` merely because they exist in `HostContext`.

## Resolution semantics

For every X reference used by a valid packet:

1. If the packet carries an explicit inline X binding, use that protocol value.
2. Otherwise, if a `HostContext` exists, its namespace exactly equals the packet `context`, and it contains the reference, use that host-local value.
3. Otherwise the reference is missing.

A host context with a different namespace is ignored for resolution. The receiver must not reinterpret `X08` as whatever repository it happens to have open.

Packet inline bindings retain protocol precedence. Host-local ambient bindings are fallback context, not transport assertions.

The resolver does not authenticate a namespace, mutate host state, infer missing identities, or execute packet actions.

## Encoder behavior

When source wording is deictic and exact identity matters, the Encoder prefers the corresponding ambient reference if the current host context establishes it. Examples:

- “this repo”, “this workspace”, “the current environment” -> `X08`;
- “the current goal” -> `X02`;
- “this artifact” -> `X03`;
- “the plan” when it is the active host plan -> `X06`;
- “the blocker” when the host exposes one -> `X07`;
- “the output/result target” -> `X09`.

For `encode: investigate this repo`, a grounded encoding is conceptually:

```text
LH-IR 2.2
context <host namespace>
mode message
A a0 q 3:+7 target X08
```

The Encoder must not invent a generic `E` node merely to avoid a missing ambient identity when the phrase denotes a specific current object. If the needed ambient binding is unavailable, use the existing missing-context behavior rather than silently broadening exact identity into an abstract entity.

Semantic entities remain appropriate when the source genuinely denotes a category or non-identifying abstraction.

## Doer behavior

The Doer resolves required X references against the matching host context before acting. Missing ambient references use the existing `need` control. A different host namespace does not authorize substitution with local ambient state.

After resolution, policy, prerequisites, task state, and normal external authority still govern execution. Ambient resolution grants identity, not permission.

## Decoder behavior

The human Decoder explains an ambient reference as exact host-grounded context when the matching host binding is available. Otherwise it reports the conventional role and explicitly says the identity is unresolved. It never invents a path/name or executes the represented action.

## Wire and opacity

No Lambda H/2.2 numeric row, tag, control, schema field, or version changes.

Ambient bindings are endpoint-local state. They are not emitted by the codec, embedded in audits, converted to character codes, or treated as encryption. Numeric context namespaces remain identifiers, not authentication or confidentiality mechanisms.

## Error behavior

- Missing required host/inline binding -> existing `need` with the packet namespace and missing X refs.
- Malformed packet -> existing `invalid` behavior.
- Namespace mismatch -> ambient binding is unavailable; do not substitute another host context.
- Material semantic ambiguity unrelated to identity -> existing `abstain` behavior.

## Integration boundaries

- `src/context.py`: ambient conventions and host-local resolution.
- `src/protocol.py`: unchanged developer graph and wire-level context rules.
- `src/ir.py`, `src/rows.py`, `src/codec.py`: unchanged transport/IR serialization behavior.
- `prompt/ENCODER.md`: prefer grounded ambient X refs for deictic identities.
- `prompt/DOER.md`: resolve X refs from matching host context before action.
- `prompt/DECODER.md`: explain resolved/unresolved ambient identities to the human.
- `PROMPT.md`, `SPEC.md`, `README.md`, `MIGRATION.md`, `docs/PRIVACY.md`: describe the host-local ambient boundary consistently.

## Non-goals

- No global meaning that `X08` is “whatever repo the receiver currently has open”.
- No automatic context namespace invention or cross-host synchronization.
- No wire fingerprint, plaintext sidecar, or new transport field.
- No authentication, permission grant, encryption, or hidden-reasoning claim.
- No change to strict nontext inline X binding rules.

## Acceptance behavior

A repo-aware host with namespace `37` and `X08` bound to its current repository allows an Encoder to represent “investigate this repo” as an action targeting `X08` in context `37`. A Doer with the same namespace/binding resolves that exact repository. A Doer with no matching namespace/binding returns `need X08`; it never substitutes another repository. The numeric packet remains ordinary Lambda H/2.2 rows.
