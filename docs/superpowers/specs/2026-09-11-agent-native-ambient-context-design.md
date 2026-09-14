# Lambda H/2.2 Agent-Native Ambient Context Design

**Status:** implemented in the current working tree.

## Goal

Make deictic agent requests such as “this repo”, “the current artifact”, and “continue the plan” map to exact host-grounded context references instead of generic semantic stand-ins, while preserving the existing opaque Lambda H/2.2 wire.

## Core invariant

Ambient context is host-grounded, context-scoped, and never model-guessed.

The numeric wire remains unchanged. `context 0` is reserved for receiver-current ambient host/session state; nonzero contexts are explicit scoped namespaces. A packet carries only its numeric `context` and X references. Exact local objects, paths, strings, handles, or other host state remain outside transport.

## Ambient-capable roles

These conventional references may be selected automatically for receiver-relative meaning when the corresponding identity is already established:

| Reference | Ambient role |
|---|---|
| `X00` | current conversational/task subject |
| `X02` | active goal |
| `X03` | active artifact |
| `X06` | active plan |
| `X07` | current blocker |
| `X08` | current workspace/environment/repository |
| `X09` | output/result target |

`X01`, `X04`, and `X05` keep their existing contextual meanings but are not automatically selected by this feature. `X00` and `X08` are intentionally distinct: a project/topic may be the conversational subject without being the current workspace, and an open repository does not by itself establish X00.

Ambient-capable does not mean globally or always bound. In context 0, directly observable unambiguous current host/session facts count as established ambient values; X00 additionally requires exactly one already-established conversational/task subject before packet receipt. In nonzero contexts, the host establishes only values present in that exact scoped namespace.

## Host-local context API

`src/context.py` owns host-local context resolution. It defines:

- `AMBIENT_ROLES`: the fixed role-to-X mapping above;
- `AMBIENT_REFS`: the corresponding set of X references;
- `CURRENT_CONTEXT`: the reserved receiver-current namespace, `"0"`;
- `HostContext(namespace, bindings)`: one local namespace plus arbitrary endpoint-local X bindings;
- `HostContext.current(bindings)`: construct host bindings for receiver-current context 0;
- `ContextResolution(resolved, missing)`: deterministic resolution output;
- `ContextPreflight(classifications, unresolved)`: local Encoder/host classification of required X refs;
- `preflight_context(packet, host_context, current_subject=...)`: classify required X refs without changing the packet;
- `resolve_context(packet, host_context, current_subject=...)`: resolve packet X references without changing the packet;
- `ambient_ref(role)`: return the conventional X reference for an ambient role.

Host-local binding values are deliberately outside the protocol schema and may be real endpoint objects or textual identities. They are never serialized by `src.rows`, `src.ir`, or `src.codec` merely because they exist in `HostContext`.

## Resolution semantics

For every X reference used by a valid packet:

1. If the packet carries an explicit inline X binding, use that protocol value.
2. Otherwise, if an exact same-namespace host/session binding exists, use it.
3. Otherwise, if packet `context` is `0` and the reference is `X00`, use a caller-supplied conversational/task subject only when exactly one such subject was already established and unambiguous before packet receipt. Do not derive X00 from cwd, X08, filenames, repository discovery, or the fact that a relation field is named `subject`.
4. Otherwise the reference is missing.

Context-0 host/session bindings for X02/X03/X06/X07/X08/X09 remain valid through step 2. For X08, prefer the host/IDE-provided workspace root; otherwise use the process/tool current working directory, optionally normalized only to its enclosing Git worktree root. Do not enumerate sibling repositories, caches, `/home`, `/`, or unrelated worktrees to discover X08. Snapshot resolved context-0 identities for the request so later topic changes or `cd` operations do not rebind them.

Receiver-current ambient state must never satisfy a different nonzero namespace. Packet inline bindings retain protocol precedence. Host-local ambient bindings are context, not transport assertions. `preflight_context` mirrors these known bindings and classifies each required X as `packet-bound`, `host-ambient-resolvable`, `conversation-ambient-resolvable`, or `unresolved`. `UNBOUND_REQUIRED_X` is the Encoder's local diagnostic for the unresolved set; it is not a Lambda H wire control.

The resolver does not authenticate a namespace, mutate host state, infer a subject from arbitrary transcript text, or execute packet actions.

## Encoder behavior

When source wording is receiver-relative and deictic, the Encoder chooses the X reference by semantic identity role first, then verifies that the chosen role is groundable. For explicit nonzero contexts, the Encoder uses an ambient reference only when that scoped host binding is established. Examples:

- “this repo”, “this workspace”, “the current environment” -> `X08`;
- “the current goal” -> `X02`;
- “this artifact” -> `X03`;
- “the plan” when it is the active host plan -> `X06`;
- “the blocker” when the host exposes one -> `X07`;
- “the output/result target” -> `X09`;
- “it”, “this project”, or the current topic when they denote one established discourse/task subject -> `X00`.

Do not replace a project/topic X00 with X08 merely because its repository is open. Before serialization, classify every required X. An accidental unresolved required X is `UNBOUND_REQUIRED_X` locally and blocks task-packet emission; selecting a different X is allowed only when that reference denotes the same intended identity role. If the protocol interaction intentionally requires the receiver to request a missing binding, use the existing `need` control.

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

The Doer resolves required X references before acting. Packet-inline and exact same-namespace host/session bindings win first. In context 0 only, X00 may then resolve from exactly one conversational/task subject that was already established and unambiguous immediately before packet receipt. If several subjects are plausible or none is established, X00 remains missing. The Doer must not infer X00 from cwd/X08, relation-slot terminology, filenames, or post-packet investigation.

X08 remains the workspace already active at packet receipt, not a search query. The Doer uses a host/IDE workspace root if present; otherwise it inspects only its current process/tool working directory and may normalize upward to that directory's Git worktree root. It must not scan the filesystem for candidate repositories. Resolved context-0 bindings are frozen for the request, and X08-scoped work remains inside that workspace. In nonzero contexts the Doer requires an exact same-namespace host binding and never uses conversational fallback. Missing ambient references use the existing `need` control.

After resolution, policy, prerequisites, task state, and normal external authority still govern execution. Ambient resolution grants identity, not permission. Once a usable semantic instruction is recovered, the Doer resumes normal host-native agent behavior and output; Lambda H does not remain a mandatory response language unless `P.reply=packet` is explicitly present.

## Decoder behavior

The human Decoder explains an ambient reference from the same resolution contract as the Doer: packet-inline or exact host/session bindings first, then the single-established-subject fallback for context-0 X00 only. Otherwise it reports the conventional role and explicitly says the identity is unresolved. It never invents a path/name, derives X00 from X08, or executes the represented action.

## Wire and opacity

No Lambda H/2.2 numeric row, tag, control, schema field, or version changes.

Ambient bindings are endpoint-local state. They are not emitted by the codec, embedded in audits, converted to character codes, or treated as encryption. Numeric context namespaces remain identifiers, not authentication or confidentiality mechanisms.

## Error behavior

- Missing required binding after packet/host/context-0-X00 resolution -> existing `need` with the packet namespace and missing X refs.
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

For the ordinary repo-local workflow, an Encoder represents “investigate this repo” as an action targeting `X08` in context `0`. A Doer already operating inside one authoritative repository/workspace resolves that exact starting workspace and proceeds without a separate X08 injection. It may use the host workspace root or current cwd/Git root to normalize that existing location, but it never searches other repositories to choose X08.

For a conversation that has one clearly established active project/topic, an Encoder may represent that discourse identity as `X00` in context `0`; a Doer may resolve it from that same single established subject without interruption. If two plausible subjects are active, the Doer returns `need X00`. A current workspace does not silently substitute for X00. For a packet using nonzero context `37`, only a host binding in namespace `37` may resolve X00/X08; receiver-current conversation or repository state is never substituted. The numeric packet remains ordinary Lambda H/2.2 rows.
