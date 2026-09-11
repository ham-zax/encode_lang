# encode_lang — Lambda H/2.2

Lambda H/2.2 is a numeric semantic communication format for language-model endpoints. It combines shallow row framing, semantic fields, exact graph relationships, policy, epistemic state, and task progress.

The transport goal is direct semantic action while keeping the human control plane usable:

```text
human source -> Encoder -> numeric packet -> Receiver/Doer -> action -> numeric packet
                  |                                      |
                  +-> English audit                      +-> human Decoder -> English explanation
```

Agent-to-agent transport is exactly one `ΛH2.2|` numeric frame. Source wording, field labels, developer JSON, code fences, and human audits are excluded from that packet. Human-facing Encoder audits and Decoder explanations are outside the transport boundary. A remote task that itself requires textual output receives numeric abstention code 2.

## Roles

| Prompt | Responsibility |
|---|---|
| `prompt/ENCODER.md` | Source meaning -> numeric packet plus separate human audit; never execute it |
| `prompt/DOER.md` | Numeric packet -> authorized action -> numeric packet |
| `prompt/DECODER.md` | Numeric packet -> English explanation for the human; never execute it |
| `PROMPT.md` | Select one role from user intent |

Each role prompt contains the complete row grammar, graph invariants, semantic anchors, valid controls, worked packets, and a path that requires no Python.

## Numeric rows

A frame begins with `ΛH2.2|`, declares its data-row count with row kind 8, and closes with row kind 9 and the same count:

```text
ΛH2.2|
8 1
0 12 0
9 1
```

That packet is the ready control. Data rows use only finite JSON numbers separated by spaces. The format rejects brackets, strings, comments, blank lines, unknown fields, duplicate ownership, missing list positions, invalid references, inconsistent state, and inputs beyond the declared limits.

Row counts detect truncation, while graph validation checks semantic structure. Neither proves that a sender chose the intended meaning.

## Optional deterministic codec boundary

Python 3.10+ and the standard library can translate local symbolic IR and numeric transport:

```sh
python3 -m src.codec encode local.ir
python3 -m src.codec decode examples/field.lh
python3 -m src.codec format examples/field.lh
python3 -m src.codec format examples/field.lh --output /tmp/canonical-field.lh
```

`encode` accepts local `LH-IR 2.2` and emits canonical numeric transport. `decode` accepts numeric transport and emits local symbolic IR for a Doer or human-facing Decoder to interpret. `format` only canonicalizes an already numeric frame. With `--output`, the destination must be new and success leaves stdout empty.

Python is optional. It owns deterministic structural conversion when available; it does not choose semantic meaning, execute tasks, acquire context, or make model-only behavior reliable.

## Agent-native ambient context

Repo-aware hosts may ground deictic references without copying exact identities onto the wire. The ambient-capable conventions are `X02` active goal, `X03` active artifact, `X06` active plan, `X07` current blocker, `X08` current workspace/environment/repository, and `X09` output/result target.

A host binding is usable only when its numeric context namespace exactly matches the packet context. Packet-inline X values take precedence; matching host-local bindings are fallback; otherwise the reference is missing and normal `need` behavior applies. A receiver must never reinterpret `X08` as whatever different repository it currently has open. Host-local bindings may contain richer objects or text because `src.context` never serializes them into Lambda H transport.

## Meaning and exact structure

A point `q` marks a semantic location. A field `f` holds one or more components with center `q`, default width `s`, optional directional bands `b`, and optional relative weight `w`. Separate components stay separate. Width and uncertainty are independent.

Subject/object direction, action target/tool, prerequisites, negation, prohibitions, conditions, policy, epistemic state, and task state remain exact. Missing context produces a numeric need control. Material ambiguity, unrepresentable meaning, incompatible text output, missing contract, or insufficient capability produces numeric abstention.

The public anchors in `semantics/basis.json` make the numbers interpretable. Lambda H is opaque in the limited sense that ordinary wording is absent from packets. It is not encryption: an observer with the basis and context can infer meaning.

## Project map

| Path | Role |
|---|---|
| `SPEC.md` | Active 2.2 contract |
| `src/protocol.py` | Developer graph and invariants |
| `src/wire.py` | Numeric structural mapping used by row assembly |
| `src/rows.py` | Public shallow numeric row parser/formatter |
| `src/ir.py` | Local model-facing symbolic IR parser/formatter |
| `src/codec.py` | IR <-> numeric transport boundary and numeric canonicalizer |
| `src/context.py` | Host-local ambient context conventions and exact namespace resolution |
| `src/geometry.py` | Field activation and numeric candidate helpers |
| `semantics/basis.json` | Shared semantic directions |
| `schema/lambda_h_packet.schema.json` | Generated local graph schema |
| `examples/` | Numeric packets and numeric candidate data |
| `calibration/` | Version-bound behavioral evidence framework |
| `docs/PRIVACY.md` | Opacity and security boundary |

Older formats are outside the active runtime. There is no compatibility parser or conversion command.
