# Lambda H/2.2 Model-Facing IR + Opaque Wire Architecture

**Status:** active design, clean migration.

**Contract:** [SPEC.md](../../../SPEC.md)
**Implementation plan:** [Human Decoder + codec-owned IR repair](../plans/2026-09-11-human-decoder-ir-codec-repair.md)

## Outcome

Lambda H carries semantic fields and exact operational structure between language-model endpoints without natural-language runtime payloads. The receiving model uses the representation to act directly. It does not need to reconstruct an English sentence first.

```text
source meaning
    -> Encoder
    -> local symbolic IR
    -> codec
    -> shallow numeric packet
    -> Receiver/Doer
    -> codec
    -> local symbolic IR
    -> semantic handoff
    -> normal authorized agent action/output

optional only when P.reply=packet:
    response IR -> codec -> shallow numeric packet
```

Python is optional. With repository tooling, models operate on the local symbolic IR and the deterministic codec owns IR <-> numeric transport conversion. Without tooling, the standalone prompts retain the complete numeric fallback grammar.

## Guarantees and limits

The design separates three claims:

| Claim | Meaning |
|---|---|
| Structural fidelity | A conforming parser recovers the same supported graph, scalar types, field presence, arrays, constraints, and task state. Deterministic round-trips can prove this. |
| Semantic fidelity | A model selected the intended meaning and acts at the required precision. Only behavioral evidence can support this. |
| Numeric instruction transport | Each Lambda H packet itself contains one numeric frame and no English text, labels, audit, or developer JSON. Successful Doer execution is host-native by default; only explicit `P.reply=packet` constrains the final response back to Lambda H. |

The system cannot guarantee arbitrary meaning recovery for every model or observe the language of hidden reasoning. “Direct semantic action” describes the input/output workflow; it does not claim access to or control of internal model embeddings.

When meaning, context, or capacity is insufficient, the endpoint returns a numeric need/abstain control. It must not hide uncertainty behind a valid-looking answer.

## One semantic contract, two representations

Lambda H/2.2 has one semantic graph with two representations at different boundaries:

1. local `LH-IR 2.2`, a shallow symbolic model-facing representation; and
2. `ΛH2.2|` shallow numeric rows, the sole agent-to-agent runtime wire.

The IR is not a second network/runtime protocol and is never automatically forwarded. The codec converts between the two without changing the developer graph. Every numeric data row names its structural owner and list position, and the frame declares the row count twice to expose common truncation errors.

```text
LH-IR 2.2
control ready

        codec encode
             |
             v
ΛH2.2|
8 1
0 12 0
9 1
```

The formal row grammar is in `SPEC.md`; the symbolic grammar is owned by `src/ir.py`. Standalone role prompts include enough of both contracts for their preferred codec-backed path and explicit no-codec fallback.

## Opacity model

Runtime packets contain only:

- fixed numeric structural tags;
- numeric semantic coordinates and field widths;
- numeric references and state;
- genuine numeric, boolean, and null scalar data;
- the fixed version marker and whitespace framing.

The format excludes source wording, English field labels, human audits, developer JSON, text sidecars, word-token dictionaries, base64, and character-number disguises. That restriction applies to Lambda H packets, not ordinary Doer output after semantic handoff. Code 2 is reserved for an explicitly requested packet reply whose required result cannot be represented faithfully.

Opacity is an interface property, not cryptographic confidentiality. An observer with the shared anchors and relevant context can infer meaning. Packet length, row shape, repeated identifiers, and traffic metadata also leak information. Confidential transfers require established authenticated encryption outside Lambda H.

The numeric lexer cannot determine whether a sender intentionally used quantities to smuggle text. The Encoder prompt prohibits that behavior; the project does not claim a perfect semantic exfiltration detector.

## Semantic model

The semantic graph retains E/R/A/T/C/K/P/task/V roles. Approximate meaning lives in q points or f fields. Operational structure stays exact.

- q is a sparse semantic point.
- f is an ordered set of semantic components.
- Each component has center q and width s, with optional directional bands b and relative peak weight w.
- Separate components remain separate; the receiver does not average alternatives into a fabricated midpoint.
- Node uncertainty u is independent of field breadth.
- R subject/object, A target/tool/prerequisites/gates/prohibition, P constraints, and task progress are never softened by semantic geometry.

Field arithmetic is a compatibility envelope over supplied coordinates. It is not probability, truth, lexical lookup, or a learned model embedding. A model may interpret fields qualitatively. If unavailable arithmetic is essential to choosing a safe action, it abstains.

## Tool-free operation

Each role prompt provides the complete standalone procedure.

Encoder:

1. Identify semantic concepts and exact operational structure.
2. Preserve alternatives and uncertainty.
3. Use only established numeric/nontext context bindings.
4. Express the graph as local symbolic IR.
5. With codec tooling, serialize through `src.codec encode` and transfer numeric output unchanged; otherwise use the explicit numeric-row fallback.
6. In a human session, show the packet plus a separate English audit; never put the audit in transport.

Receiver/Doer:

1. Check the version, frame, row ownership, and graph invariants.
2. Resolve required context under the context-0/nonzero grounding rules.
3. Interpret q/f against the shared anchors without requiring sentence reconstruction.
4. Apply policy, conditions, epistemic state, prerequisites, and task progress.
5. Hand the recovered intent to normal authorized agent execution and use the same workflow/output conventions as equivalent ordinary-language input.
6. Encode a numeric final response only when `P.reply=packet` is explicitly present; protocol controls remain available when a usable instruction cannot be recovered.

Decoder:

1. Validate structure and recover the graph, preferably through `src.codec decode` into local IR.
2. Preserve every field, omission, list position, scalar type, semantic breadth, and unresolved X dependency.
3. Explain the represented meaning and structure in English to the human.
4. Never execute the represented action.

Manual validation does not become deterministic merely because the steps are written down. Tool-free reliability remains a separate behavioral question.

## Optional deterministic boundary

The codec owns three structural operations:

- `python3 -m src.codec encode`: local symbolic IR -> canonical numeric 2.2 rows;
- `python3 -m src.codec decode`: canonical numeric 2.2 rows -> local symbolic IR;
- `python3 -m src.codec format`: numeric 2.2 rows -> canonical numeric 2.2 rows.

The codec never infers missing meaning or context, executes actions, repairs malformed semantic state, or overwrites an existing destination. Codec parsing/serialization is protocol infrastructure rather than a task instrument, so represented `P.tools=false` does not force models back into manual wire manipulation. Numeric-output commands return numeric invalid/abstain controls on failure; local decode reports local conversion errors without pretending they are transport.

A successful encode/decode/format proves structural conversion only, not semantic comprehension or task completion. Models must not manually rewrite codec-produced numeric transport.

## Context discipline

X references are namespace-scoped handles. `X02`, `X03`, `X06`, `X07`, `X08`, and `X09` are ambient-capable conventions for active goal, artifact, plan, blocker, workspace/environment/repository, and output/result target. `context 0` is the receiver-current ambient namespace, so directly observable unambiguous current host/session facts may establish these roles there; nonzero contexts require explicit same-namespace host grounding. See [Agent-native ambient context](2026-09-11-agent-native-ambient-context-design.md).

Resolution uses packet-inline values first; context 0 then uses receiver-current grounded ambient state already active at packet receipt, while nonzero contexts use only matching host-local bindings; otherwise the reference is missing. For X08, use the host/IDE workspace root or current cwd/enclosing Git worktree root and never scan elsewhere to discover a candidate repository. Freeze the context-0 binding for the request. Host-local values may be richer endpoint objects/text because they never become Lambda H transport. Receiver-current state must never satisfy a different nonzero namespace. Bind frames still carry only genuine numeric, boolean, or null values.

A missing required binding produces need with exactly the missing X references. Context conflict code 2 remains for contradictory established state, not simple namespace absence. An exact identity that is unavailable cannot be reconstructed from coordinates or replaced by a generic E node solely to avoid missing context.

Persistent context storage, sender authentication, request correlation, replay protection, and exactly-once effects belong to the host environment.

## Failure semantics

Malformed packets use invalid:

- 0: shape, token, arity, tag, or range failure;
- 1: unresolved local reference;
- 2: context conflict;
- 3: dependency or task-state inconsistency.

Valid requests that cannot be satisfied faithfully use abstain:

- 0: material semantic ambiguity;
- 1: meaning not representable by the shared contract;
- 2: explicit packet-reply output incompatibility;
- 3: missing/incompatible shared contract or basis;
- 4: endpoint capacity, capability, or required permission unavailable.

Need is reserved for known missing X bindings. Ready is only bootstrap readiness. Controls contain no task payload or prose diagnostic.

## Role and ownership boundaries

| Surface | Owner |
|---|---|
| `src/protocol.py` | Graph schema and invariants |
| `src/wire.py` | Fixed numeric structural mappings |
| `src/rows.py` | Public numeric row parsing and formatting |
| `src/ir.py` | Local symbolic model-facing IR |
| `src/codec.py` | Deterministic IR <-> wire and numeric canonicalization boundary |
| `src/geometry.py` | Field calculations |
| `semantics/basis.json` | Shared semantic directions |
| `prompt/ENCODER.md` | Source meaning to numeric packet plus separate human audit |
| `prompt/DOER.md` | Numeric packet to semantic handoff and normal authorized agent execution/output; optional explicit packet reply |
| `prompt/DECODER.md` | Numeric packet to human English explanation without execution |
| `PROMPT.md` | Role selection |

No surface may silently introduce another runtime representation.

## Evidence requirements

Deterministic checks must exercise every field type, controls, q/f alternatives, multiple components, bands, weights, V, typed scalars, nonsequential IDs, ordering, omission, and explicit false/null/empty values. Negative checks must cover malformed/truncated frames, duplicates, position gaps, invalid references, cycles, inconsistent tasks, text, unsupported versions, and resource limits.

Behavioral evaluation must keep separate:

- Encoder semantic choice versus syntax validity;
- Doer action versus packet canonicalization;
- tool-assisted versus tool-free operation;
- correct abstention versus unsafe guessing;
- exact structure contrasts such as reversed direction, negation, prerequisite order, false versus omitted permission, and missing context.

Results record the exact Doer prompt digest, semantic-basis digest, corpus digest, model identity where known, tool availability, packet, response, and evaluator judgments. An unrun case remains missing. Structural round-trips never count as model behavior passes.

## Clean migration

The active repository contains no legacy parser, old-version conversion command, combined bootstrap, natural reply mode inside the numeric protocol, or readable context-sidecar workflow. The local symbolic IR and human Decoder/Audit are deliberate control-plane surfaces, not compatibility paths. Older packets are not upgraded by changing their marker; they must be recreated from actual source meaning under the 2.2 contract.

Historical material may explain project lineage, but it is not an executable compatibility promise and is excluded from active entrypoints.
