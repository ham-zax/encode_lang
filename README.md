# encode_lang — Lambda H/2.2

Lambda H/2.2 is a numeric semantic communication format for language-model endpoints. It combines shallow row framing, semantic fields, exact graph relationships, policy, epistemic state, and task progress.

The transport goal is direct semantic action while keeping the human control plane usable:

```text
human source -> Encoder -> numeric packet -> Receiver/Doer -> normal agent execution/output
                  |
                  +-> English audit

numeric packet -> human Decoder -> English explanation
```

A Lambda H instruction is exactly one `ΛH2.2|` numeric frame. Source wording, field labels, developer JSON, code fences, and human audits are excluded from that packet. Once a Doer recovers a usable semantic instruction, it resumes the same native tools, workflow, artifacts, progress reporting, and response style it would use for equivalent ordinary-language input. Only explicit `P.reply=packet` requests a Lambda H final response.

## Roles

| Prompt | Responsibility |
|---|---|
| `prompt/ENCODER.md` | Source meaning -> numeric packet plus separate human audit; never execute it |
| `prompt/DOER.md` | Numeric packet -> semantic handoff -> normal authorized agent execution/output; packet reply only when explicitly requested |
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

`context 0` is the receiver-current ambient namespace. Packet-inline X values take precedence; then directly observable, unambiguous host/session facts already active at packet receipt may ground ambient-capable references. For `X08`, use the host/IDE workspace root if exposed, otherwise the current process/tool working directory, optionally normalized only to its enclosing Git worktree root. Do not search the machine or enumerate other repositories to identify X08. Freeze the resulting workspace for the request, and keep X08-scoped exploration inside it. For nonzero contexts, only an exact same-namespace host-local binding may resolve the reference. A receiver must never use its current workspace to satisfy a different nonzero context. Host-local bindings may contain richer objects or text because `src.context` never serializes them into Lambda H transport.

## Meaning and exact structure

A point `q` marks a semantic location. A field `f` holds one or more components with center `q`, default width `s`, optional directional bands `b`, and optional relative weight `w`. Separate components stay separate. Width and uncertainty are independent.

Subject/object direction, action target/tool, prerequisites, negation, prohibitions, conditions, policy, epistemic state, and task state remain exact. Failures that prevent a usable semantic handoff may produce protocol controls. Ordinary post-handoff text or artifact output is allowed; abstain code 2 is only for incompatibility when `P.reply=packet` was explicitly requested.

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
| `src/context.py` | Receiver-current context-0 conventions and strict nonzero host-context resolution |
| `src/geometry.py` | Field activation and numeric candidate helpers |
| `semantics/basis.json` | Shared semantic directions |
| `schema/lambda_h_packet.schema.json` | Generated local graph schema |
| `examples/` | Numeric packets and numeric candidate data |
| `calibration/` | Version-bound behavioral evidence framework |
| `docs/PRIVACY.md` | Opacity and security boundary |

Older formats are outside the active runtime. There is no compatibility parser or conversion command.
