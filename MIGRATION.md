# Migrating from Lambda H/1 to Lambda H/2

This is a deliberate protocol break, not a new interpretation of old bytes. The active codec accepts Lambda H/2 only. The v1 prototype is preserved under `archive/v1/` as historical material, not imported as a fallback or advertised as a second supported runtime.

## Why a version break is necessary

V1 mixed approximate meaning with operational details that were not always explicit: which action targets which object, which tool belongs to it, what condition gates it, what has already finished, and what stops a continuing mission. Reconstructing missing information from a stronger continuation policy would still be guessing.

V2 retains the useful separation of entities, relations, actions, instruments, epistemics, references, and nuance. It changes the representation and supplies exact task structure instead of pretending that stronger semantic coordinates can recover lost facts.

## What changes

| V1 | V2 |
| --- | --- |
| Dense positional offset-hex strings | Sparse named signed coordinates, such as `{"A13":6,"A14":7}` |
| Custom separator grammar for every layer | `ΛH2|` followed by an ordinary JSON object |
| Implicit action/object/tool association | Explicit `target`, `tool`, `after`, `when`, and `until` fields |
| Behavioral permission inferred from a graded policy region | Exact `P.mutation` and `P.tools` booleans, constrained by the originating authority |
| Unscoped session-local reference assumptions | Explicit `context` namespace and stable X bindings |
| Continuation mainly expressed as posture | Versioned task snapshot with `goal`, ordered `steps`, `done`, state, and `next` |
| Coarse regions expected to distinguish nearby words | Optional exact scalar `value` or explicit `choices` when a distinction matters |
| Silent loss of conditional or negative scope | Explicit condition records and `not:true` |
| Geometry-only calibration emphasis | Receiving behavior, constraints, disclosure, decoder-tool use, and captured evidence |

`u` is now an integer from 0 to 7; omitted uncertainty is unspecified, not certainty. Neutral sparse coordinates are omitted. Negative affinity is not logical negation or permission denial. Anchor names such as A14 are public semantic axes, not encrypted word tokens.

## Re-encode, do not invent a conversion

Use the original user request, the actual current task state, and the bindings available to the intended receiver. Encode a new v2 packet with the current bootstrap. Do not manufacture completed steps, missing filenames, permissions, stop conditions, or evidence from a v1 vector.

For illustration, a v1 action region emphasizing execution and continuation can preserve those affinities as `{"A13":6,"A14":7}`. That conversion alone does not determine its target or mission state. A usable v2 message with an already established goal is:

```text
ΛH2|{"context":"lesson-1","A":[{"id":"a0","q":{"A13":6,"A14":7},"target":"X02"}]}
```

This is valid only as a reference to a goal that the receiver actually knows in `lesson-1`. It does not magically recreate that goal in a fresh session.

When only a v1 packet remains, an approximate reconstruction using the archived v1 bootstrap may recover broad meaning. Treat it as uncertain evidence. Obtain task-critical missing facts before producing an actionable v2 replacement. There is intentionally no automatic migration command that fabricates these facts.

## Public tooling

The active module is `src.codec`:

```sh
python3 -m src.codec parse message.lh
python3 -m src.codec format packet.json
python3 -m src.codec inspect message.lh --context private/context.json
python3 -m src.codec handoff message.lh --context private/context.json
python3 -m src.codec schema
```

The active package exports `ProtocolError`, `parse_packet`, `format_packet`, `validate_packet`, `inspect_packet`, `make_handoff`, and `schema`. Old quantization, dense-vector comparison, compact-v1, and validator entry points are retired. Read the active schema and bootstrap rather than adapting calls by renaming fields alone.

The optional tooling checks representation and supplied state. It does not infer semantic scores, authenticate the sender, execute actions, provide a durable task database, or prove that a receiving model will respond correctly.

## Context and task state

Local e/r/a/t/c nodes must be declared in each packet. Only X references can depend on named external context. Supply a matching namespace to the inspector; do not merge a context map from an unrelated session.

The `handoff` operation includes only referenced X bindings. It is not a privacy scrubber: every included binding becomes visible to the recipient. Read [the privacy model](docs/PRIVACY.md) before exporting confidential state.

Task revisions describe a snapshot; they are not an authenticated event log. Reconcile the newest actual state before resuming. Preserve completion and cancellation, and recheck uncertain external effects rather than replaying them automatically.

## Historical work and Git

The original checkout was `main` at `667204d`, one commit ahead of its recorded upstream, with five staged v1 documentation/calibration/example changes. The retired files and the earlier edits were preserved in the archive. During final integration, the shared checkout's index was observed to contain the staged migration rather than only those original five files. This implementation pass did not stage, reset, commit, or push; it preserved the index as found. Additional report/document changes may remain unstaged, so inspect the complete working tree before making a commit.

The historical tests were preserved without changing their contents. They do not establish v2 correctness and are not a current default test suite. No cross-model success rate, latency improvement, token saving, or absence of internal reasoning is implied by the new format or by a codec check.
