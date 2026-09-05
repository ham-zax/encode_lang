# ΛH/1 Protocol Specification

## 1. Purpose

ΛH/1 is a prompt-portable semantic representation format. It is designed to let separate AI sessions exchange approximate semantic/task state using shared anchor geometries rather than a word-to-token lookup table.

The representation is hybrid:

```text
ΛH = E + R + A + T + K + P + X + V
```

- `E`: entities and concepts
- `R`: relations between entities
- `A`: actions/intents
- `T`: tools/instruments
- `K`: epistemic status and proposition confidence
- `P`: execution/control policy
- `X`: contextual references
- `V`: residual nuance

The canonical modular bases and their ordering live in `semantics/*.yaml`; `semantics.json` is retained as the earlier aggregate compatibility snapshot. Changing an anchor meaning or order requires a new basis version.

## 2. Quantization

Continuous semantic judgments are coarsened to integer scores in `[-7,+7]`.

Wire encoding uses one hexadecimal-like digit per coordinate:

```text
-7  -6  -5  -4  -3  -2  -1   0  +1  +2  +3  +4  +5  +6  +7
 0   1   2   3   4   5   6   7   8   9   A   B   C   D   E
```

`F` is reserved.

Use `0` semantic score for unrelated anchors. Negative scores are for meaningful opposition/incompatibility, not merely lack of affinity.

## 3. Layer packets

### Entity

`B_E/01` contains 32 anchors:

```text
ΛE1|b=01|q=<32 digits>|u=<0-E>
```

`u` is uncertainty. Low values mean the intended sense is well resolved; high values indicate ambiguity/polysemy.

### Relation

`B_R/01` contains 16 directed relation anchors:

```text
ΛR1|b=01|q=<16 digits>|u=<0-E>
```

Relations are directional unless a shared relation region is explicitly known to be symmetric.

### Action

`B_A/01` contains 16 operation anchors:

```text
ΛA1|b=01|q=<16 digits>|u=<0-E>
```

### Tool

`B_T/01` contains 16 tool/instrument anchors:

```text
ΛT1|b=01|q=<16 digits>|u=<0-E>
```

### Policy

`B_P/01` contains 12 bipolar policy axes:

```text
ΛP1|b=01|q=<12 digits>|u=<0-E>
```

A policy code never grants actual access or authority. It only expresses desired execution posture.

### Residual

`B_V/01` contains 8 bipolar residual axes:

```text
ΛV1|b=01|q=<8 digits>|u=<0-E>
```

Use `V` only for nuance that is not cleanly represented by the other layers.

## 4. Epistemics

`K` is proposition-level metadata, not a global confidence score.

Normative compact forms target the relation handle and carry status/confidence separately:

```text
K=R02:K03:0.35
K=R04:K05:0.82
```

This means the first relation proposition is a hypothesis at 0.35 support, while the second is supported at 0.82. The underlying relation packet is separate from the epistemic status.

## 5. Context and handles

Fixed references are `X00` through `X09`; dynamic references use `X10` through `XFF`.

Session-local handles:

```text
ηNN  entity/concept
ρNN  relation
αNN  action
τNN  tool
```

A handle is not universal. If a receiver lacks a binding it must return:

```text
ΛH1|SYNC?
```

The sender should then resend the missing region binding, not invent a textual meaning for the handle.

## 6. Compact wire form

ΛH/1 defines a deterministic compact chat syntax in addition to canonical JSON. Fields are separated by `|`; unused fields are omitted. The canonical field order is `E,R,A,T,K,P,X,V`.

```text
ΛH1|E=00.<32q>.<u>,01.<32q>.<u>|R=00.<16q>.<u>(01,00)|A=00.<16q>.<u>|T=00.<16q>.<u>|K=R00:K03:0.42|P=<12q>.<u>|X=00,02|V=<8q>.<u>
```

Rules:

- Compact handles are two uppercase hexadecimal digits. The field supplies the namespace: `E=00...` maps to `η00`, `R=00...` maps to `ρ00`, `A=00...` maps to `α00`, and `T=00...` maps to `τ00`.
- Relation arguments are entity handle IDs in `(subject,object)` order.
- Every region entry includes `q` and a one-digit uncertainty `u` in `0-E`.
- `K` entries use `<target>:<K00-K08>:<confidence>`. Compact targets are `ENN`, `RNN`, `ANN`, `TNN`, or `XNN`.
- `P` is exactly 12 wire digits plus uncertainty; `V` is exactly 8 wire digits plus uncertainty.
- `X` contains two-digit reference IDs; `X=02` means `X02`.
- Basis version `01` is implicit in compact ΛH1 packets. A different basis requires a new compatible protocol/basis declaration rather than silent reinterpretation.
- JSON remains the canonical machine contract. `python3 -m src.lambda_h parse` and `compact` provide deterministic conversion between the two forms.

Control frames are normative too:

```text
ΛH1|SYNC?
ΛH1|SYNC|E=00.<32q>.<u>
ΛH1|ACK|E=00,01|R=00(01,00)|A=00|T=00
ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=01|BV=01
ΛH1|CALFAIL
```

`SYNC` must carry at least one ordinary semantic field. `ACK` must contain at least one of E/R/A/T and uses relation summaries `HH(HH,HH)`. New ACK frames do not use square brackets.

Do not merge several entities by averaging their vectors. Keep them as distinct `E` entries and express relationships in `R`.

## 7. Encoding algorithm

For ordinary language:

1. Resolve context and polysemy.
2. Identify distinct entities/concepts.
3. Project each entity onto `B_E/01`.
4. Identify directed relationships and project each onto `B_R/01`.
5. Identify requested operation(s) and project onto `B_A/01`.
6. Identify requested/preferred tool classes and project onto `B_T/01`.
7. Attach proposition-level epistemic state using `K`.
8. Encode control posture in `B_P/01`.
9. Resolve contextual references in `X`.
10. Put only leftover nuance into `V`.
11. Emit the hybrid packet.

For single-word encoding, select the primary semantic layer first. A concrete/abstract noun usually starts in `E`; a verb-like requested operation usually starts in `A`; a relation word such as `inside` starts in `R`; an execution posture such as `continue` may start in `P`; and a tool name starts in `T`.

Explicit commands are `ACTION:`, `RELATION:`, `TOOL:`, and `POLICY:`. `SEMANTIC:` is the generic selector: first emit `LAYER=<E|R|A|T|K|P|V>`, then the native layer representation. K is proposition-level; if no target proposition exists, return `TARGET_REQUIRED` rather than fabricating one.

## 8. Decoding algorithm

1. Validate basis versions and packet lengths.
2. Decode wire digits into `[-7,+7]` coordinates.
3. Reconstruct each region relative to the corresponding shared basis.
4. Resolve handles and `X` references.
5. Compose entities, relations, actions, tools, epistemics, policy, and residual state.
6. Act on the reconstructed meaning unless the caller explicitly requested an English projection.

Decoding is approximate. The receiver should reconstruct the semantic neighborhood and compositional structure, not claim recovery of exact original wording.

## 9. Interoperability criterion

Prompt-only models may not produce identical coordinates. A successful implementation preserves:

- relative semantic neighborhoods;
- polysemy/context separation;
- relation argument order;
- distinction between entity/action/tool/policy layers;
- proposition-level uncertainty;
- session-handle synchronization.

For example, ordinary senses should usually satisfy:

```text
sim(cat,dog) > sim(cat,hat)
sim(cat,rat) > sim(cat,fire)
```

The two senses of `fire` in combustion and employment termination should separate strongly when context is supplied.

## 10. Entity-resolution limit and planned contrastive residual

`B_E/01` is a coarse universal geometry. It can place nearby concepts such as cat, dog, and rat in the correct neighborhood without necessarily carrying enough information to recover which nearby concept was intended.

A future version may extend entity representation as:

```text
E = E0 + EΔ
```

where `E0` is the current 32-anchor universal region and `EΔ` is a task/session-induced contrastive subregion used only when a coarse neighborhood contains multiple live candidates. `EΔ` is not part of ΛH/1 v1.0 and must not be invented ad hoc in current packets; adding it requires a versioned contract.
