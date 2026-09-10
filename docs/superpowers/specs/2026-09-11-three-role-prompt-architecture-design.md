# Lambda H/2.1 Three-Role Prompt Architecture

## Goal

Replace the current two-role prompt split with three explicit standalone roles: a Doer that operates in Lambda H, an Encoder that turns ordinary/source language into Lambda H plus a human audit, and a Decoder that reconstructs Lambda H into human-readable meaning without executing it. Make root `PROMPT.md` the repo-aware universal router for agents that have repository access and may need any of the three capabilities.

## Why three roles

The current receiver bootstrap combines two different jobs: understanding a packet well enough to act on it, and reconstructing the packet into natural language for a human. Those are not the same interface.

A Lambda H-native worker should not be encouraged to translate every packet into English before acting. A human-facing decoder should not perform the represented task. The encoder also needs a distinct audit surface so a human can inspect what semantic structure was actually encoded and what a conforming receiver is likely to derive.

The three-role split therefore separates:

- protocol-native execution;
- source-to-protocol representation;
- protocol-to-human explanation.

## Role 1: Doer

### File

`prompt/DOER.md`

### Contract

The Doer receives Lambda H/2.1 packets and performs the represented work. Its normal data flow is:

`Lambda H packet -> structural unpacking -> semantic interpretation -> policy/task-state evaluation -> action -> Lambda H response`

The Doer is not a translator. It may use a temporary structural developer graph for deterministic unpacking, but it must not require reconstruction of a sentence-level natural-language source before acting.

### Required behavior

1. Validate the `ΛH2.1|` frame and numeric tagged-array structure.
2. Honor `P.tools` before using decoder tooling.
3. When tools are permitted and `src.codec` exists, prefer the deterministic parse path for nested-array bookkeeping.
4. Otherwise unpack root, node, component and enum tags mechanically from the standalone tables.
5. Preserve exact graph directionality, conditions, prohibitions, policy, epistemic state and task continuation before interpreting fuzzy semantic fields.
6. Resolve only actually required X bindings for the active context namespace.
7. Preserve q/f semantic breadth and distinct field components without manufacturing a midpoint or unique lexical label.
8. Execute, continue, stop, or report a blocker according to represented state and actual external evidence.
9. Reply in Lambda H by default unless the represented output contract or user explicitly requires natural language.
10. Never claim that Lambda H controls or reveals hidden model reasoning, provides encryption, or bypasses model-provider safety or permissions.

### What the Doer must not teach

The Doer prompt should not contain a general source-language-to-packet encoding workflow and should not contain a human-facing decode/reconstruction workflow. Shared tables and anchors remain because the prompt must be standalone.

## Role 2: Encoder

### File

`prompt/ENCODER.md`

### Contract

The Encoder receives an ordinary-language message, task, state description or instruction and produces two logically separate outputs:

1. the Lambda H numeric packet intended for another agent;
2. a human-readable semantic audit describing what was encoded.

Its normal data flow is:

`source meaning -> semantic graph -> q/f representation -> exact constraints/context -> numeric wire + audit`

The encoder does not execute the task it is encoding.

### Packet output

The first output is the actual transport artifact. It must obey the existing Lambda H/2.1 wire contract: numeric tagged arrays only after the prefix, no arbitrary lexical codebook, no string hiding, no character-number escape, no base64 disguise, and no unreferenced inline X bindings in normal message/handoff packets.

### Human semantic audit

After the packet, the encoder should output a clearly separate audit intended for the human operator. The audit is not part of the wire and must not be silently forwarded to the Doer.

The audit should explain, at minimum:

- the principal entities/concepts represented;
- exact relation direction and action target/tool structure;
- q centers or f components, breadth, asymmetric widths and relative emphasis where material;
- conditions, prohibitions, permissions and task progress encoded exactly;
- required X bindings and what exact information remains outside the numeric wire;
- unresolved ambiguity deliberately preserved in the representation;
- a concise description of the intended semantic portrayal a conforming receiver should derive.

The audit must distinguish two claims:

- **Protocol semantics:** what the packet structurally and geometrically represents under the Lambda H/2.1 specification.
- **Expected receiver interpretation:** the reasonable semantic meaning a conforming receiver is expected to derive from those structures.

It must not describe the latter as observation of another model's hidden internal representation.

### Output shape

Default encoder output should be easy for a human to inspect and easy for automation to split. The recommended shape is:

```text
PACKET
<Lambda H packet>

AUDIT
<concise human-readable semantic portrayal>
```

When an exact-context sidecar is necessary, it remains a separate deliberate artifact and is described in the audit rather than embedded into the numeric packet.

## Role 3: Decoder

### File

`prompt/DECODER.md`

### Contract

The Decoder receives a Lambda H/2.1 packet and explains it to a human. Its normal data flow is:

`Lambda H packet -> structural unpacking -> semantic interpretation -> human-readable reconstruction`

The Decoder must not execute the represented task merely because the packet describes an action.

### Required behavior

1. Validate and unpack the same numeric wire contract used by the Doer.
2. Prefer deterministic `src.codec parse` when repository tooling is present and use is allowed; retain a full manual decoding path because the prompt is standalone.
3. Explain exact graph roles before collapsing them into prose: subjects/objects, action targets/tools, prerequisites, conditions, negation/prohibition, policy, epistemic state and task snapshot.
4. Explain q/f semantics at the represented level of abstraction rather than forcing one exact word where the field is broad or multi-component.
5. Identify missing X references instead of inventing exact identities.
6. State unresolved ambiguity explicitly when multiple interpretations remain materially live.
7. Produce human-readable reconstruction and interpretation only; do not perform the represented task.
8. Preserve the same safety, hidden-reasoning and non-encryption boundaries as the other prompts.

## Root repo-aware prompt

### File

`PROMPT.md`

### Contract

Root `PROMPT.md` becomes the universal entrypoint for an agent that has repository access. It should be compact and route the agent to authoritative role prompts rather than duplicate the full protocol tables.

The repo-aware agent chooses the role from the user's intent:

- ordinary/source language -> Lambda H: load `prompt/ENCODER.md`;
- Lambda H -> human explanation: load `prompt/DECODER.md`;
- Lambda H -> actual task execution / continuation: load `prompt/DOER.md`.

For a mixed workflow, the agent may chain roles explicitly. For example, it may encode source language, show the encoder audit to the human, then provide only the packet/context to a Doer. Or it may decode a Doer response for human inspection.

Because it has repository access, the universal prompt may use `src.codec`, `src.protocol`, `src.wire`, `src.geometry`, `semantics/basis.json`, and the role prompt files as authoritative implementation/reference surfaces. It should not copy hundreds of lines of tables into `PROMPT.md`.

## Fate of `prompt/BOOTSTRAP.md`

The ambiguous receiver/decoder name should be retired from the active three-role contract rather than remain as a fourth quasi-role.

Target state:

- active Doer prompt: `prompt/DOER.md`;
- active Encoder prompt: `prompt/ENCODER.md`;
- active Decoder prompt: `prompt/DECODER.md`;
- repo-aware router: `PROMPT.md`;
- no active documentation or calibration should describe `prompt/BOOTSTRAP.md` as a role prompt.

Whether the old file is deleted or retained only as clearly historical material should follow the repository's current human-owned migration state. The implementation must not recreate content that another human is actively deleting.

## Shared contract and drift prevention

All three standalone role prompts need enough of the Lambda H/2.1 contract to operate without depending on another prompt. Therefore the stable wire tables, enum tables, field contract, semantic anchors, context roles and policy/task semantics may be duplicated across role prompts.

The implementation authorities remain:

- `src/protocol.py` for developer graph and invariants;
- `src/wire.py` for numeric transport tables and enums;
- `src/geometry.py` for field behavior;
- `semantics/basis.json` for semantic anchors.

Role prompts are synchronized protocol documentation, not competing protocol implementations. A packet encoded under `ENCODER.md` must be understandable by both `DOER.md` and `DECODER.md` without translation through an ordinary-language source sentence.

## Calibration

Existing receiver calibration measures whether an agent correctly understands a packet and behaves according to it. Under the three-role architecture, that is Doer behavior, not Decoder behavior.

Therefore the existing receiver calibration bootstrap binding should migrate from `prompt/BOOTSTRAP.md` to `prompt/DOER.md`.

Changing that prompt path/digest makes any observations under the prior combined receiver prompt historical. No existing results may be relabeled as evidence for the new Doer prompt.

Decoder reconstruction fidelity is a separate empirical question. A decoder-specific calibration corpus may be added later, but it is outside this migration unless independently requested.

Encoder audit quality is likewise a separate evaluation surface. The initial migration only defines the audit contract and examples; it does not create a scoring framework unless independently requested.

## Documentation migration

Role-selection documentation should converge on the three-role vocabulary:

- **Doer:** understands Lambda H and performs represented work;
- **Encoder:** converts source language/state to Lambda H and emits a human audit;
- **Decoder:** converts Lambda H to human-readable explanation without executing;
- **`PROMPT.md`:** repo-aware router capable of selecting or chaining the three roles.

Documentation should stop using "receiver" where that word conflates execution with reconstruction. It may still use "receiving agent" descriptively when the receiving endpoint is specifically a Doer.

## Concurrency boundary

The repository is being edited by a human concurrently. Implementation must treat human deletions and concurrent edits as intentional user-owned state.

Rules for this migration:

- do not restore unrelated text that disappears during implementation;
- do not reset, checkout, or discard concurrent work;
- before editing a shared existing file, read its current contents and apply only the smallest three-role migration change still required;
- if the human has already removed or rewritten a target section in a way compatible with this design, accept that state instead of recreating the previous wording;
- new role prompt files may be created where absent;
- protocol source files should not change unless current evidence proves the three-role split actually requires a protocol behavior change.

## Acceptance criteria

- `prompt/DOER.md` is the standalone Lambda H-native execution prompt and does not require natural-language reconstruction before acting.
- `prompt/ENCODER.md` encodes source meaning and, by default, emits both a numeric packet and a clearly separate human semantic audit.
- `prompt/DECODER.md` reconstructs/explains Lambda H for a human and explicitly does not execute the represented task.
- `PROMPT.md` is a compact repo-aware universal router that can select or chain all three roles.
- All three role prompts agree on the active Lambda H/2.1 structural tables, enums, field contract, semantic anchors, X/context semantics, policy and task-state semantics.
- Existing Doer-style calibration binds to `prompt/DOER.md`, not to the Decoder prompt.
- Any pre-migration receiver evidence is marked historical after the Doer prompt/digest changes.
- The split does not change the Lambda H/2.1 wire format merely to support role separation.
- The Encoder audit distinguishes exact protocol semantics from expected receiver interpretation and never claims access to hidden model reasoning.
- No role prompt treats Lambda H opacity as encryption or as a mechanism to bypass safety systems, permissions or policy.
- Concurrent human deletions and edits are not reversed by this migration.