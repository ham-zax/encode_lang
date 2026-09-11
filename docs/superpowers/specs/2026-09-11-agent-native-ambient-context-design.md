# Lambda H/2.2 Agent-Native Ambient Context Design

**Status:** implemented in the current working tree.

## Goal

Make deictic agent requests such as “this repo”, “the current artifact”, and “continue the plan” map to exact host-grounded context references instead of generic semantic stand-ins, while preserving the existing opaque Lambda H/2.2 wire.

## Core invariant

Ambient context is host-grounded, context-scoped, and never model-guessed.

The numeric wire remains unchanged. `context 0` is reserved for receiver-current ambient host/session state; nonzero contexts are explicit scoped namespaces. A packet carries only its numeric `context` and X references. Exact local objects, paths, strings, handles, or other host state remain outside transport.

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

Ambient-capable does not mean globally or always bound. In context 0, directly observable unambiguous current host/session facts count as established ambient values. In nonzero contexts, the host establishes only values present in that exact scoped namespace.

## Host-local context API

`src/context.py` owns host-local context resolution. It defines:

- `AMBIENT_ROLES`: the fixed role-to-X mapping above;
- `AMBIENT_REFS`: the corresponding set of X references;
- `CURRENT_CONTEXT`: the reserved receiver-current namespace, `"0"`;
- `HostContext(namespace, bindings)`: one local namespace plus arbitrary endpoint-local X bindings;
- `HostContext.current(bindings)`: construct host bindings for receiver-current context 0;
- `ContextResolution(resolved, missing)`: deterministic resolution output;
- `resolve_context(packet, host_context)`: resolve packet X references without changing the packet;
- `ambient_ref(role)`: return the conventional X reference for an ambient role.

Host-local binding values are deliberately outside the protocol schema and may be real endpoint objects or textual identities. They are never serialized by `src.rows`, `src.ir`, or `src.codec` merely because they exist in `HostContext`.

## Resolution semantics

For every X reference used by a valid packet:

1. If the packet carries an explicit inline X binding, use that protocol value.
2. Otherwise, if packet `context` is `0`, use a directly observable, unambiguous receiver-current ambient value that was already active when the packet arrived. For `X08`, prefer the host/IDE-provided workspace root; otherwise use the process/tool current working directory, optionally normalized only to its enclosing Git worktree root. Do not enumerate sibling repositories, caches, `/home`, `/`, or unrelated worktrees to discover X08.
3. Snapshot the resolved context-0 identity for the request. Later `cd` operations or task exploration do not rebind it. X08-scoped repository discovery stays inside that workspace unless another authorized scope is explicitly represented.
4. Otherwise, for a nonzero packet context, if a `HostContext` exists with exactly the same namespace and contains the reference, use that host-local value.
5. Otherwise the reference is missing.

Receiver-current ambient state must never satisfy a different nonzero namespace. Packet inline bindings retain protocol precedence. Host-local ambient bindings are context, not transport assertions.

The resolver does not authenticate a namespace, mutate host state, infer missing identities, or execute packet actions.

## Encoder behavior

When source wording is receiver-relative and deictic, the Encoder uses context 0 with the corresponding ambient reference so the receiving agent can ground it from authoritative current host/session state. For explicit nonzero contexts, the Encoder uses an ambient reference only when that scoped host binding is established. Examples:

- “this repo”, “this workspace”, “the current environment” -> `X08`;
- “the current goal” -> `X02`;
- “this artifact” -> `X03`;
- “the plan” when it is the active host plan -> `X06`;
- “the blocker” when the host exposes one -> `X07`;
- “the output/result target” -> `X09`.

For `encode: investigate this repo` intended for an agent already operating in the target repository, the normal receiver-relative encoding is:

```text
LH-IR 2.2
context 0
mode message
A a0 q 3:+7 target X08
```

The Encoder must not invent a generic `E` node merely to avoid a missing ambient identity when the phrase denotes a specific current object. If the needed ambient binding is unavailable, use the existing missing-context behavior rather than silently broadening exact identity into an abstract entity.

Semantic entities remain appropriate when the source genuinely denotes a category or non-identifying abstraction.

## Doer behavior

The Doer resolves required X references before acting. In context 0, X08 is the workspace already active at packet receipt, not a search query. It uses a host/IDE workspace root if present; otherwise it inspects only its current process/tool working directory and may normalize upward to that directory's Git worktree root. It must not scan the filesystem for candidate repositories. The binding is then frozen for the request, and X08-scoped work remains inside it. In nonzero contexts the Doer requires an exact same-namespace host binding. Missing ambient references use the existing `need` control. Receiver-current state never authorizes substitution into a different nonzero namespace.

After resolution, policy, prerequisites, task state, and normal external authority still govern execution. Ambient resolution grants identity, not permission. Once a usable semantic instruction is recovered, the Doer resumes normal host-native agent behavior and output; Lambda H does not remain a mandatory response language unless `P.reply=packet` is explicitly present.

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

- No use of the receiver's current repo to satisfy `X08` in a nonzero context. Context 0 intentionally denotes receiver-current ambient state.
- No automatic nonzero context namespace invention or cross-host synchronization.
- No wire fingerprint, plaintext sidecar, or new transport field.
- No authentication, permission grant, encryption, or hidden-reasoning claim.
- No change to strict nontext inline X binding rules.

## Acceptance behavior

For the ordinary repo-local workflow, an Encoder represents “investigate this repo” as an action targeting `X08` in context `0`. A Doer already operating inside one authoritative repository/workspace resolves that exact starting workspace and proceeds without a separate X08 injection. It may use the host workspace root or current cwd/Git root to normalize that existing location, but it never searches other repositories to choose X08. For a packet using nonzero context `37`, only a host binding in namespace `37` may resolve X08; otherwise the Doer returns `need X08` and never substitutes its current repository. The numeric packet remains ordinary Lambda H/2.2 rows.
