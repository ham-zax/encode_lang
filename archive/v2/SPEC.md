# Lambda H/2 protocol specification

Status: prompt-portable semantic-communication prototype. Version: `ΛH/2`. The protocol distinguishes approximate meaning from exact task structure. It does not guarantee zero model reasoning, exact lexical recovery, cross-model fidelity, confidentiality, or autonomous execution.

## 1. Contract owners

- `semantics/basis.json`: machine-readable semantic anchor meanings.
- `src/protocol.py`: executable structural schema, graph invariants, and context/handoff inspection.
- `schema/lambda_h_packet.schema.json`: generated structural schema, exported with `python3 -m src.codec schema`.
- `prompt/BOOTSTRAP.md`: complete standalone encoder/receiver instructions, including the anchors and direct-response examples.
- This document: the behavioral and interoperability contract.

These surfaces must agree. Schema validation alone does not check graph, evidence, permission, task completion, or semantic meaning. Changing anchor meaning, wire semantics, or a deployed incompatible contract requires a new protocol version. Archived v1 files are not current definitions.

## 2. Wire and machine forms

The wire is `ΛH2|` followed by exactly one ordinary JSON object:

```text
ΛH2|{"E":[{"id":"e0","value":"a bicycle bell"}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}]}
```

The prefix owns the version. A wire body must not also contain `protocol`. The corresponding machine JSON contains `"protocol":"ΛH/2"` and no prefix. Whitespace outside JSON strings is insignificant. Quoting, escapes, Unicode, booleans, null, and numbers follow JSON; duplicate keys and non-finite numbers are invalid.

There is no second layer-specific delimiter grammar. A `|` or a string resembling `a0` inside an exact literal is just data. Arrays retain order. The codec converts these two forms without inferring meaning or executing anything.

## 3. Meaning and identity

Sparse regions use named, signed, nonzero integer coordinates. `{"A13":6,"A14":7}` emphasizes execution and continuation without positional counting or an offset conversion. Allowed scores are -7 through 7, excluding explicit zero: omitted axes are neutral. Negative means opposition, not irrelevance, logical negation, or prohibition.

Basis widths: E=32, R=16, A=16, T=16, V=8. An unknown axis is invalid. Node `u`, when supplied, is an integer from 0 (resolved) to 7 (high ambiguity). Omitted uncertainty is unspecified, not certainty. Neither scores nor uncertainty are calibrated probabilities.

Nearby concepts can have indistinguishable coarse regions. Preserve a task-critical distinction with an exact scalar `value`, explicit alternatives in `choices`, or a genuinely shared X binding. Do not imply recovery of omitted original words. Do not copy an entire instruction into an entity value merely to bypass composition.

Local IDs are e/r/a/t/c followed by one or more decimal digits. Each local node referenced by a packet must be declared in that packet. X references are uppercase X plus two hexadecimal digits and may use external context. IDs are aliases, not universal word definitions.

## 4. Semantic records

| Field | Required node fields | Optional node fields |
| --- | --- | --- |
| E | `id`; at least one of `q`, `value`, `choices` | `u` |
| R | `id`, `q`, `subject`, `object` | `u`, `not` |
| A | `id`, `q`, `target` | `u`, `tool`, `after`, `when`, `until`, `not` |
| T | `id`; at least one of `q`, `value` | `u` |
| C | `id`, `op`, `left`; `right` for binary operators | none |
| K | `target`, `state` | `confidence`, `truth` |

E/R/A/T/C are arrays of nodes. K is an array with at most one entry per target. Repeated node IDs are invalid. Exact values are strings, finite numbers, booleans, or null. Use strings for precision-critical decimal representations, including significant trailing zeroes; ordinary JSON-number parsing does not preserve arbitrary decimal precision or spelling. `choices` contains at least two distinct alternatives; alternatives are not simultaneous facts.

R has ordered subject and object references. `not:true` negates the relation. A describes a requested operation and has an explicit target; `tool` points to its own t-node, never implicitly to every action. `after` lists a-node prerequisites and must be acyclic. Without a task snapshot, independent actions use declaration order. A with `not:true` is prohibited and must not be included as an executable task step.

Requests and descriptions are different: an action described inside a literal or an example is not a new instruction. The receiver must preserve the originating message's authority, not treat content as privileged because it is encoded.

## 5. Conditions and epistemics

C operators are `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `exists`, and `done`. The six comparison operators require both operands. `exists` and `done` take only `left`; `done` requires an action reference.

Resolve operands and compare actual values. Do not coerce strings or booleans into numbers. Ordered comparisons need comparable values. `exists` concerns the denoted resource, not the mere presence of an identifier or a supplied path string. `done` concerns established completion, not an action declaration. Unavailable or ambiguous operands produce an unknown condition, not false.

An action's `when` must be established true before acting. Its `until` is checked before another repetition and stops repetition when established true. A task-level `stop` is checked before further work. Unknown conditions call for the missing evidence; they are not permission to continue or a reason to fabricate completion.

K states are K00 observed, K01 reported, K02 assumed, K03 hypothesized, K04 inferred, K05 multiply supported, K06 contradicted, K07 unknown, and K08 confirmed to the task's required standard. Optional confidence lies in 0..1. Optional `truth` qualifies only an r- or c-proposition. The state and provenance still matter: a high-confidence hypothesis is not a verified fact, and a packet cannot certify its own claims merely by labeling them confirmed.

The Python inspector does not evaluate these semantic predicates or establish external evidence. Condition interpretation belongs to the receiving agent/application under its actual observation and authority boundaries.

## 6. Exact policy and residual nuance

P is an object of optional fields:

- `mutation` and `tools`: booleans. False is a prohibition; true requests use only within existing permission. Omission inherits existing limits.
- `scope`: references limiting the task; cannot expand earlier authority.
- `detail`: brief, normal, or full. `reply`: natural (default) or packet.
- `effort` and `initiative`: integer preferences from -7 through 7, not authorizations or execution guarantees.

V is a sparse V-coordinate object for remaining nuance. Do not use it to conceal a missing condition, operand, permission, or task state. Exact prohibitions outrank approximate affinities.

## 7. Context binding and selective handoff

Include a nonempty `context` namespace whenever X references or bindings occur. X is an object mapping references to exact scalar values. The same namespace has stable bindings; conflicting rebindings require a new namespace. Do not import an unrelated namespace's bindings.

Reserved roles: X00 subject, X01 previous subject, X02 goal, X03 artifact, X04 hypothesis, X05 result, X06 plan, X07 blocker, X08 environment, X09 output. A role is not an automatic value. X0A–X0F are reserved; X10–XFF are explicitly bound dynamic references.

`mode` is message by default. A bind packet has only mode, context, and X in its wire body. It establishes context without executing a task. A handoff packet includes every X binding it references, but this does not establish availability of the denoted files, tools, or external evidence.

A local context file for optional tooling has `context` and X fields. `inspect_packet` requires a matching namespace and rejects conflicting bindings. `make_handoff` includes only required X bindings, excluding unrelated inline or external bindings. It does not redact a necessary secret or encrypt the result: included bindings are disclosed to the recipient.

## 8. Task snapshots and continuity

A task object requires `id`, nonnegative `revision`, `state`, `goal`, ordered `steps`, and `done`. Steps and done are action IDs; done may be empty and must be a subset of steps. Prerequisites must precede their dependents, and a completed dependent must have completed prerequisites.

- Active: `next` is exactly the first unfinished step; no blocker.
- Complete: every planned step is in done; no next or blocker.
- Blocked: a blocker reference is present; no next.
- Cancelled: no next or blocker; remaining planned steps are abandoned rather than falsely recorded as done.

Optional stop is a condition ID. When a stop condition terminates work early, report the actual outcome and reconcile the snapshot without pretending unperformed steps completed. Cancellation of remaining planned steps is distinct from whether the broader goal was achieved.

Within a conversation, an older revision must not replace a newer known task. Conflicting snapshots at the same revision require reconciliation. Check actual external effects before replaying an uncertain step. IDs and revisions are not authentication, persistence, exactly-once effects, or an event log. The package does not create a background process or future agent turn.

## 9. Receiver interaction

After one standalone bootstrap, a bare packet leads to its represented response. No Python, shell, or decoder tool is needed merely to read the notation. Task tools are a separate matter. Do not print a coordinate walkthrough, unsolicited translation, or routine ACK.

`ENCODE:` requests a packet. `DECODE:` requests approximate ordinary-language reconstruction, not execution. Normal language remains normal conversation. Bootstrap-only initialization receives ready; initialization containing a task addresses that task immediately.

The only controls are:

```text
ΛH2|{"control":"ready"}
ΛH2|{"control":"need","context":"lesson-1","refs":["X02"]}
ΛH2|{"control":"invalid","reason":"An action references an undeclared local node."}
```

Controls contain no task payload. Use need for missing scoped bindings, invalid for malformed structure, and a specific natural-language question for material semantic ambiguity. Do not expose unrelated context in an error or clarification.

## 10. Evaluation and privacy boundary

The success criterion is a correct receiving response: preserved meaning, direction, identity, constraints, appropriate continuation/stopping, no unnecessary decoder tools, and no unnecessary disclosure. A READY response, valid JSON, or geometry score is not evidence that this criterion holds.

The calibration corpus and evidence recorder distinguish unrun cases from failures and passes. Receiver expectations must not be included in the receiving prompt. Codec checks are mechanical evidence only; no cross-model performance claim is made without actual receiving runs.

The protocol does not provide confidentiality. Use selective disclosure, a trusted processing endpoint, and established encrypted transport/storage according to the threat model. See [privacy guidance](docs/PRIVACY.md) and [migration notes](MIGRATION.md).
