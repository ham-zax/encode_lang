# Lambda H/2.2 Direct Numeric Semantics Architecture

**Status:** active design, clean migration.

**Contract:** [SPEC.md](../../../SPEC.md)  
**Implementation plan:** [Lambda H/2.2 implementation](../plans/2026-09-11-three-role-prompt-architecture.md)

## Outcome

Lambda H carries semantic fields and exact operational structure between language-model endpoints without natural-language runtime payloads. The receiving model uses the representation to act directly. It does not need to reconstruct an English sentence first.

```text
source meaning
    -> Encoder
    -> shallow numeric packet
    -> Receiver/Doer
    -> authorized semantic action
    -> shallow numeric packet
```

Python is optional. A model without tools receives the complete numeric grammar, graph invariants, controls, and semantic anchors in its role prompt. A deterministic codec can validate and canonicalize the same representation when available.

## Guarantees and limits

The design separates three claims:

| Claim | Meaning |
|---|---|
| Structural fidelity | A conforming parser recovers the same supported graph, scalar types, field presence, arrays, constraints, and task state. Deterministic round-trips can prove this. |
| Semantic fidelity | A model selected the intended meaning and acts at the required precision. Only behavioral evidence can support this. |
| Numeric-only runtime | Observable protocol output contains one numeric frame and no English text, labels, audit, or developer JSON. This can be checked mechanically. |

The system cannot guarantee arbitrary meaning recovery for every model or observe the language of hidden reasoning. “Direct semantic action” describes the input/output workflow; it does not claim access to or control of internal model embeddings.

When meaning, context, or capacity is insufficient, the endpoint returns a numeric need/abstain control. It must not hide uncertainty behind a valid-looking answer.

## One active representation

Lambda H/2.2 uses the shallow numeric row representation as the runtime wire and the model-facing representation. There is no mandatory English-keyword IR and no active nested-array compatibility path.

Every data row names its structural owner and list position. This makes row order irrelevant and makes gaps, duplication, and wrong ownership detectable. The frame declares the row count twice to expose common truncation errors.

```text
ΛH2.2|
8 1
0 12 0
9 1
```

The formal row grammar and complete tags are in `SPEC.md` and are duplicated exactly in the three standalone role prompts.

## Opacity model

Runtime packets contain only:

- fixed numeric structural tags;
- numeric semantic coordinates and field widths;
- numeric references and state;
- genuine numeric, boolean, and null scalar data;
- the fixed version marker and whitespace framing.

The format excludes source wording, English field labels, human audits, developer JSON, text sidecars, word-token dictionaries, base64, and character-number disguises. Text-producing tasks receive abstention code 2.

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
4. Assign graph IDs and row positions.
5. Verify closure, constraints, framing, and numeric-only output.
6. Emit one packet or a numeric control.

Receiver/Doer:

1. Check the version, frame, row ownership, and graph invariants.
2. Resolve required context in the same namespace.
3. Interpret q/f against the shared anchors without sentence reconstruction.
4. Apply policy, conditions, epistemic state, prerequisites, and task progress.
5. Act only at supported precision and existing authority.
6. Emit numeric result/state or a numeric control.

Decoder:

1. Validate structure and recover the graph.
2. Preserve every field, omission, list position, and scalar type.
3. Return canonical numeric rows or a control.
4. Never execute or explain in English.

Manual validation does not become deterministic merely because the steps are written down. Tool-free reliability remains a separate behavioral question.

## Optional deterministic boundary

`python3 -m src.codec format` validates and canonicalizes a 2.2 frame. It accepts the original packet bytes, assembles the graph through fixed structural tables, invokes the authoritative validator, formats canonical rows, parses them again, and compares the recovered graph.

The codec:

- never infers missing meaning or context;
- never executes actions;
- never repairs or clamps malformed data;
- never emits developer JSON on the runtime channel;
- never overwrites an artifact destination;
- returns a numeric invalid or abstain control on failure.

A canonical echo proves structural validity, not semantic comprehension or task completion. The model must not substitute canonicalization for doing the requested work.

## Context discipline

X references are namespace-scoped handles. X00..X09 carry conventional roles, but a role does not establish a binding. Text is never sent as a binding. Bind frames can establish only genuine numeric, boolean, or null values.

A missing required binding produces need with exactly the missing X references. A conflicting namespace/binding produces invalid code 2. An exact textual identity that is unavailable cannot be reconstructed from coordinates; the encoder or receiver abstains where exact text is essential.

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
- 2: required textual output;
- 3: missing/incompatible shared contract or basis;
- 4: endpoint capacity, capability, or required permission unavailable.

Need is reserved for known missing X bindings. Ready is only bootstrap readiness. Controls contain no task payload or prose diagnostic.

## Role and ownership boundaries

| Surface | Owner |
|---|---|
| `src/protocol.py` | Graph schema and invariants |
| `src/wire.py` | Fixed numeric structural mappings |
| `src/rows.py` | Public row parsing and formatting |
| `src/codec.py` | Optional CLI and artifact boundary |
| `src/geometry.py` | Field calculations |
| `semantics/basis.json` | Shared semantic directions |
| `prompt/ENCODER.md` | Source meaning to numeric packet |
| `prompt/DOER.md` | Numeric packet to action and numeric response |
| `prompt/DECODER.md` | Numeric structural canonicalization only |
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

The active repository contains no legacy parser, conversion command, combined bootstrap, natural reply mode, or readable context-sidecar workflow. Older packets are not upgraded by changing their marker. They must be recreated from actual source meaning under the 2.2 contract.

Historical material may explain project lineage, but it is not an executable compatibility promise and is excluded from active entrypoints.
