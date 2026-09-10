# Lambda H/2.x Model-Facing IR + Opaque Wire Architecture

## Goal

Make Lambda H reliably usable by weaker and stronger language models while preserving the project's core requirement: ordinary agent-to-agent transport should remain opaque numeric Lambda H rather than readable natural-language payload.

The central change is to stop asking models to directly author, compact, rewrite, or repair the canonical numeric wire. Models operate on a simple line-oriented Lambda semantic IR. A deterministic codec owns the conversion between that IR and the opaque numeric transport.

## Core decision

Lambda H has two distinct representations with one semantic contract:

1. **Model-facing Lambda IR** — line-oriented, shallow, code-like, easy for models to read and produce.
2. **Canonical Lambda wire** — opaque numeric transport, deterministic, compact, and not manually edited by models.

The IR is not a second protocol. It is a readable structural representation of the same graph, analogous to an AST/debug form. The wire remains the agent-to-agent transport artifact.

Normal architecture:

```text
source language
    |
    v
Encoder model
    |
    v
Lambda IR
    |
    v
codec serialize
    |
    v
opaque Lambda wire
    |
    v
codec parse
    |
    v
Lambda IR
    |
    v
Doer model
    |
    v
Lambda IR response
    |
    v
codec serialize
    |
    v
opaque Lambda wire
```

A human-facing Decoder follows the same receive path but converts parsed IR to natural explanation instead of executing it.

## Why this change

The current numeric tagged-array wire is structurally precise for machines but fragile when models manipulate it directly. Recent observed behavior demonstrates the failure mode:

- the Encoder constructed and validated a correct nested packet;
- when presenting the packet, it removed nested pair brackets and produced a different invalid packet;
- the Doer then manually recopied and debugged that malformed packet;
- the Doer also emitted flattened control forms such as `ΛH2.1|[12,0]` instead of `ΛH2.1|[[12,0]]`.

The violated invariant is not semantic understanding. It is serialization ownership. Models treat some nested punctuation as presentation and may normalize it. Lambda H treats that punctuation as structure.

The repair is therefore architectural: put serialization behind a deterministic boundary instead of trying to make prompts repeatedly warn models not to rewrite punctuation.

## Model-facing Lambda IR

### Design principles

The IR should exploit syntax patterns models already handle well:

- one declaration per line;
- shallow structure;
- stable identifiers such as `E0`, `R0`, `A0`, `T0`, `C0`, `X08`;
- explicit direction with `->`;
- compact numeric semantic coordinates;
- no recursive punctuation where a flat declaration suffices;
- no arbitrary natural-language message content embedded in the IR.

The IR remains structural and semantic, not sentence reconstruction.

### Initial grammar baseline

The first implementation uses this line-oriented grammar shape for a packet representing "investigate the repository bound as environment X08":

```text
LH 2.1
CTX 0
MODE msg

E0 q 12:+6
R0 q 1:+6 X08 -> E0
A0 q 3:+7 -> X08
```

The initial grammar uses one declaration per line, whitespace-separated structural tokens, stable typed identifiers (`E0`, `R0`, `A0`, `T0`, `C0`, `X08`), signed coordinate pairs such as `12:+6`, and `->` only for directed references. Compound structures that cannot fit one flat declaration, such as multi-component `f`, policy, and task state, use additional indented continuation lines rather than nested JSON-style punctuation. The implementation plan must specify the complete canonical spelling for every existing developer-graph field before parser mutation begins.

The IR may expose stable symbolic structural names such as `CTX`, `MODE`, `E`, `R`, `A`, `T`, `C`, `K`, `P`, `TASK`, `q`, and `f` because the IR is an internal/model-facing representation rather than the opaque transport.

It must not become a lexical side channel for arbitrary source text.

## Semantic fidelity

The new IR must preserve the entire existing Lambda H semantic graph rather than simplify away meaning.

It must be able to represent, without loss:

- E/R/A/T/C/K nodes and their IDs;
- directed R subject/object structure;
- A target, tool, prerequisites, when, until, and prohibition;
- q sparse points;
- f multi-component semantic fields;
- component width `s`;
- asymmetric bands `b`;
- relative component weight `w`;
- node uncertainty `u`;
- P policy fields;
- task revision/state/steps/completion/next/stop/blocker;
- V coordinates;
- context namespace;
- X references and permitted inline numeric bindings;
- control / need / invalid packets;
- typed numeric/boolean/null scalar forms.

No semantic-axis or graph-contract reduction is authorized merely to make the syntax shorter.

## Canonical wire

The current numeric Lambda H transport remains the canonical wire during this migration unless later evidence independently justifies changing it.

For example:

```text
ΛH2.1|[[0,0],[1,0],[2,[[[0,0],[1,[[12,6]]]]]],[3,[[[0,0],[1,[[1,6]]],[4,[5,8]],[5,[0,0]]]]],[4,[[[0,0],[1,[[3,7]]],[4,[5,8]]]]]]
```

The wire remains:

- numeric arrays after the `ΛH2.1|` prefix;
- free of arbitrary natural-language payload;
- free of arbitrary word-code dictionaries;
- free of base64 or character-number disguises;
- governed by `src/wire.py` and the existing protocol invariants.

The wire's opacity is preserved. The architectural simplification happens on the model side, not by making transport human-readable.

## Serialization ownership

This is the key invariant.

### When codec tooling is available

Models MUST NOT manually serialize Lambda IR into numeric wire and MUST NOT manually reconstruct IR from numeric wire.

The codec owns both boundaries:

```text
IR -> canonical wire
canonical wire -> IR
```

Codec output is immutable transport output. Once produced, the model must emit/pass it verbatim rather than compacting, normalizing, pretty-printing, flattening, or rewriting it.

Likewise an incoming packet must be passed as received to the codec. The model must not retype the packet into a Python literal or manually remove/rearrange brackets before parsing.

### No-codec fallback

Standalone role prompts still need a fallback for environments where repository tooling is unavailable or `P.tools` prohibits use.

In that fallback only:

- the model may manually unpack the canonical wire using the stable tables;
- structural pair boundaries are semantically significant and may not be flattened;
- manual response construction should use canonical worked templates for controls and small packets;
- the fallback is a compatibility path, not the preferred normal path.

The project should measure fallback reliability separately from codec-backed operation.

## Encoder contract

The Encoder becomes:

```text
source meaning -> Lambda IR -> codec -> PACKET
                             -> human AUDIT
```

Required behavior:

1. infer the semantic graph from source meaning;
2. express that graph in Lambda IR;
3. validate/serialize the IR through the codec when permitted and available;
4. copy the codec's canonical packet verbatim into `PACKET`;
5. independently produce the human `AUDIT` from the semantic graph/IR, not by rewriting the packet;
6. never execute the encoded task.

The audit continues distinguishing:

- **Protocol semantics** — what graph/geometry is represented;
- **Expected receiver interpretation** — what a conforming receiver is expected to derive.

The audit is outside the wire.

## Doer contract

The Doer becomes:

```text
canonical packet -> codec -> Lambda IR -> task execution
                                      -> Lambda IR response -> codec -> canonical packet
```

The Doer should normally reason over Lambda IR rather than raw numeric arrays.

It must not require natural-language reconstruction as an intermediate step.

When it needs to respond in Lambda H and codec tooling is available, it should construct response IR and let the codec serialize it. This includes ready/need/invalid controls; the Doer should not hand-author flattened control wire.

## Decoder contract

The human-facing Decoder becomes:

```text
canonical packet -> codec -> Lambda IR -> human explanation
```

It describes the represented task/message and does not execute it.

The Decoder may show IR in a debugging/technical explanation because the IR is specifically designed to make graph structure legible.

## Repo-aware `PROMPT.md`

Root `PROMPT.md` remains the universal router for agents with repository access.

It should additionally establish the representation boundary:

- role models operate on Lambda IR;
- `src.codec` converts IR and canonical wire;
- canonical wire is passed unchanged between agents;
- a model must not manually rewrite codec-produced wire.

This keeps the operational rule in one obvious entrypoint while the three standalone prompts remain usable without root routing.

## Context/X08 behavior

The serialization repair and context semantics are separate concerns.

The observed `investigate the repo` example also exposed that `X08` names an environment role but is not automatically an exact binding under the current contract.

This design does NOT silently change that semantic rule.

This migration retains the current strict X08 semantics: `X08` is an environment role, not an automatic exact binding. A fresh endpoint must receive or already possess the binding through the existing context mechanism. Repo-aware ambient binding is explicitly out of scope for this migration and requires a separate protocol decision if desired later.

This keeps the demonstrated serialization failure and the independent context-binding question causally separate.

## Why not runes as canonical syntax

Runes/glyphs may be visually compact, but they do not solve the demonstrated structural reliability problem and introduce new variability:

- tokenizer treatment differs across models;
- Unicode normalization/copying can alter representation;
- rare glyphs have weaker learned structural priors than common code syntax;
- visually similar characters increase debugging cost.

Therefore runes are not part of the canonical model IR or wire in this design.

A future display-only glyph layer could map IR tokens to symbols, but it must remain cosmetic and must never become a required parser path without empirical evidence.

## Opacity model

Opacity remains a transport/interface property:

- ordinary source wording is absent from canonical wire;
- canonical wire uses structural numbers and numeric semantic coordinates;
- exact textual identity is disclosed only through deliberate X/context sidecars where needed;
- model-facing IR exists inside the endpoint/model workflow and is not automatically transmitted to another endpoint.

The IR therefore does not weaken transport opacity merely by being easier for the local model to manipulate.

Lambda H does not claim cryptographic confidentiality. A party that receives the semantic basis, decoder, context, or local IR may infer represented meaning. The objective is minimal ordinary-language disclosure and model-native semantic transport, not encryption.

## Implementation authorities

The architecture should converge around these owners:

- `src/protocol.py` — semantic graph and invariants;
- `src/wire.py` — canonical numeric wire mapping;
- `src/geometry.py` — semantic-field behavior;
- `semantics/basis.json` — semantic axes;
- `src.codec` — deterministic IR/wire parsing and serialization boundary;
- `prompt/ENCODER.md` — source -> IR -> codec + audit behavior;
- `prompt/DOER.md` — codec -> IR -> action -> response IR -> codec behavior;
- `prompt/DECODER.md` — codec -> IR -> human explanation behavior;
- `PROMPT.md` — repo-aware routing and boundary selection.

If the current codec only supports developer JSON rather than the new line IR, implementation should extend the codec at that boundary rather than teaching models another ad hoc serializer.

## Migration strategy

This should be a coordinated internal migration, not a permanent dual model-facing syntax.

1. define the minimal Lambda IR grammar from the existing developer graph;
2. implement deterministic IR parse/format at `src.codec`/an appropriate focused module;
3. verify IR round-trips to the existing developer graph and canonical wire without semantic loss;
4. update Encoder to generate IR and consume codec output verbatim;
5. update Doer to parse incoming wire to IR and serialize response IR through codec;
6. update Decoder to decode through IR;
7. update repo-aware `PROMPT.md`;
8. migrate active examples/docs/calibration only when their concurrent human ownership boundary is available;
9. keep manual numeric parsing only as an explicit standalone fallback;
10. remove model instructions that encourage direct manual serialization in the normal codec-backed path.

The canonical numeric wire itself does not need a version bump merely because endpoint implementation now uses an IR internally. If wire semantics or bytes change later, that is a separate protocol-version decision.

## Concurrency boundary

The repository is being edited concurrently by a human/other pass.

Implementation must:

- treat concurrent deletions as intentional;
- not restore text another human removes;
- not reset/check out/discard shared work;
- re-read shared files immediately before editing;
- accept compatible human rewrites rather than recreating prior wording;
- avoid protected/shared files until their ownership boundary is available;
- prefer new focused files or narrowly guarded edits where possible.

## Acceptance criteria

- A model can express the full existing Lambda H graph using a shallow line-oriented IR.
- The codec deterministically parses and formats that IR.
- IR -> developer graph -> canonical wire and canonical wire -> developer graph -> IR preserve the same semantics.
- Models do not manually rewrite codec-produced canonical wire in the normal path.
- Encoder emits codec-produced `PACKET` verbatim plus a separate human `AUDIT`.
- Doer normally acts from parsed IR and emits response wire only through deterministic serialization when available.
- Decoder normally explains from parsed IR and never executes the represented task.
- Canonical transport remains opaque numeric Lambda H during this migration.
- No arbitrary source wording is introduced into the canonical wire.
- Manual raw-wire reasoning is retained only as the no-codec fallback.
- Runes/glyphs are not required for interoperability.
- The migration does not reverse concurrent human edits.

## Explicit non-goals

- redesigning the semantic basis;
- weakening or deleting E/R/A/T/C/K/P/task/q/f semantics;
- introducing cryptographic encryption claims;
- hiding deliberately supplied context from an endpoint that receives it;
- changing canonical wire bytes solely to make the model-facing syntax prettier;
- building a rune-based protocol before empirical evidence supports it;
- adding decoder-specific or model-performance benchmark frameworks as part of the initial architecture change.
