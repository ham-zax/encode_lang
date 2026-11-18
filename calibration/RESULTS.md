# Lambda H/2.2 implementation observations

Date: 2026-11-18.

The active source implements shallow numeric transport rows, local symbolic IR, exact graph validation, numeric-only protocol controls, three standalone role prompts (`ENCODER` / `DOER` / `DECODER`), single-source-of-truth doc/schema/anchor sync (`src/sync_docs.py`), and an optional IR/wire codec boundary (`encode`, `decode`, `format`, `explain`, `lint`, `fix`, `recipe`, `preflight`). The permissive 2.2 revision (no need/abstain controls, no prohibition semantics) supersedes any earlier behavioral observations; the calibration corpus in `probes.json` contains 15 mixed cases (11 `reply_mode: "packet"`, 4 `reply_mode: "native"`), evaluated across `meaning`, `direct_action`, `constraints`, and `output_contract`. No fresh receiving-model experiment has been run against the current 2.2 prompt/basis/corpus; evidence must be re-measured against the current prompts.

## Mechanical evidence

Observed in the current worktree after edits:
- `python3 -m src.sync_docs && python3 -m src.sync_docs --check` exited 0 (`schema/lambda_h_packet.schema.json` matches `src.protocol.schema()`, `## Shared semantic anchors` in all three role prompts matches `semantics/basis.json` in canonical order `E, R, A, T, K, V, X`, and structural invariants across `SPEC.md` and `prompt/*.md` pass).
- `python3 -m src.calibration --template` validated all 15 cases in `calibration/probes.json` against `require_valid`, `format_packet`, and `reply_mode` consistency with `output_contract` as the fourth dimension.
- All 37 numeric packets and 11 `LH-IR 2.2` snippets in `SPEC.md`, `README.md`, and `prompt/{ENCODER,DOER,DECODER}.md` parsed and round-tripped canonically through `parse_packet`/`format_packet` and `parse_ir`/`format_ir`.

These mechanical checks establish syntax, schema, IR/wire round-trip fidelity, prompt-table agreement, and structural packet behavior. They do not establish semantic accuracy, Doer action quality, native post-handoff output quality, Encoder semantic choice, or human Decoder reconstruction quality.

## Model evidence

| Mode | Status |
|---|---|
| Tool-free Receiver/Doer | Unmeasured |
| Tool-assisted Receiver/Doer | Unmeasured |
| Encoder semantic fidelity | Unmeasured |
| Agent-native ambient deictic selection/resolution | Unmeasured |
| Native post-handoff Doer execution/output | Unmeasured |
| Human-facing Decoder reconstruction | Unmeasured |

No pass rate, latency, token saving, cross-model advantage, confidentiality, or hidden-reasoning claim is established.
