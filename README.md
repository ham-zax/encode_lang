# encode_lang — Lambda H/2.2

Lambda H/2.2 is a numeric semantic communication format for language-model endpoints. It combines shallow row framing, semantic fields, exact graph relationships, policy, epistemic state, and task progress.

The runtime goal is direct semantic action:

```text
source meaning -> Encoder -> numeric packet -> Receiver/Doer -> action -> numeric packet
```

English reconstruction is not a runtime stage. Runtime output is exactly one `ΛH2.2|` numeric frame. Text, field labels, source wording, developer JSON, code fences, and human audits are excluded. A request that requires textual output receives numeric abstention code 2.

## Roles

| Prompt | Responsibility |
|---|---|
| `prompt/ENCODER.md` | Encode source meaning; never execute it |
| `prompt/DOER.md` | Interpret numeric meaning and perform authorized work |
| `prompt/DECODER.md` | Validate/canonicalize numeric structure; never execute or explain in English |
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

## Optional deterministic validation

Python 3.10+ and the standard library can validate and canonicalize a packet:

```sh
python3 -m src.codec format examples/field.lh
python3 -m src.codec format examples/field.lh --output /tmp/canonical-field.lh
```

With no `--output`, stdout is numeric packet data only. With `--output`, the destination must be new; success writes a private file and leaves stdout empty. Failures return a numeric invalid or abstain control and exit 2.

Python is optional. It checks serialization and graph invariants; it does not infer meaning, execute tasks, acquire context, or make model-only behavior reliable.

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
| `src/rows.py` | Public shallow row parser/formatter |
| `src/codec.py` | Optional canonicalization CLI |
| `src/geometry.py` | Field activation and numeric candidate helpers |
| `semantics/basis.json` | Shared semantic directions |
| `schema/lambda_h_packet.schema.json` | Generated local graph schema |
| `examples/` | Numeric packets and numeric candidate data |
| `calibration/` | Version-bound behavioral evidence framework |
| `docs/PRIVACY.md` | Opacity and security boundary |

Older formats are outside the active runtime. There is no compatibility parser or conversion command.
