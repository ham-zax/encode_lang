# Historical Lambda H/2.2 Direct-Row Migration Plan

> Historical record of the `4dab29a` direct-row migration. It is superseded for the active architecture by `2026-09-11-human-decoder-ir-codec-repair.md` and the later agent-native semantic-handoff/context corrections. Numeric-only Doer output described below is historical, not the current contract.

**Goal:** Record the earlier direct-row migration that made shallow numeric Lambda H/2.2 the only model/runtime representation.

**Architecture:** Models and tools consume the same numeric rows. `src.protocol` owns semantics, `src.wire` owns structural mappings, and `src.rows` owns the public frame. Runtime output is numeric-only; Python is optional.

**Spec:** [Direct numeric semantics architecture](../specs/2026-09-11-model-facing-ir-opaque-wire-design.md)

## Constraints

- No legacy runtime parser, conversion command, combined bootstrap, natural reply, or readable sidecar.
- No source wording, developer JSON, audit, code fence, or English explanation in runtime output.
- No claim to control hidden reasoning or guarantee arbitrary semantic recovery.
- Exact graph structure remains authoritative over approximate geometry.
- Tool-free operation is complete; tool-assisted and tool-free evidence remain distinct.
- Preserve the Git index and concurrent work. No tests, model runs, commit, or deployment without independent authorization.

## Task 1: Active graph and numeric mapping

**Files:** `src/protocol.py`, `src/wire.py`, `semantics/basis.json`, generated schema.

- [x] Set the sole active protocol to Lambda H/2.2.
- [x] Add abstention and its bounded numeric codes.
- [x] Restrict developer literals to number/boolean/null.
- [x] Restrict context/task IDs to canonical decimal namespaces.
- [x] Restrict reply to packet and modes to message/bind.
- [x] Retain E/R/A/T/C/K/P/task/V and q/f/s/b/w semantics.
- [x] Regenerate the local graph schema from the active contract.

**Acceptance:** text and natural replies cannot validate; every active field has one fixed numeric mapping.

## Task 2: Shallow row parser and formatter

**Files:** `src/rows.py`.

- [x] Parse the exact marker and row-count frame.
- [x] Enforce numeric lexical rules, 1 MiB, and 16384 rows.
- [x] Assemble root, nodes, records, fields, components, bindings, and choices by explicit owner/position.
- [x] Reject duplicate ownership and noncontiguous positions.
- [x] Delegate graph meaning/invariants to the existing semantic validator.
- [x] Canonically format by root, node, field, component, and item order.
- [x] Preserve arrays, omissions, booleans/null, numeric values, and component order.

**Acceptance:** graph and canonical-text round-trips hold for supported graphs; malformed input is never repaired.

## Task 3: Optional deterministic codec

**Files:** `src/codec.py`, `src/__init__.py`.

- [x] Accept only the 2.2 row format.
- [x] Validate and canonicalize with a parse-format-parse comparison.
- [x] Emit only numeric output on stdout.
- [x] Create only new private artifacts and leave stdout empty on successful file output.
- [x] Map structural/capacity failures to numeric controls and exit 2.
- [x] Remove compatibility conversion and context-sidecar commands/APIs.

**Acceptance:** the codec cannot become a textual runtime path or overwrite a destination.

## Task 4: Standalone role prompts

**Files:** `prompt/ENCODER.md`, `prompt/DOER.md`, `prompt/DECODER.md`, `PROMPT.md`.

- [x] Give each role the complete grammar, tables, invariants, controls, anchors, and no-tool procedure.
- [x] Encoder emits one packet/control and never executes source work.
- [x] Doer acts directly from represented meaning and returns numeric state/result/control.
- [x] Decoder canonicalizes structure without action or English explanation.
- [x] Router selects one role from intent and defaults a bare frame to Doer.
- [x] Remove the combined bootstrap and PACKET/AUDIT workflow.

**Acceptance:** the prompts share one contract and can operate without Python.

## Task 5: Active docs, examples, and calibration

**Files:** README, SPEC, MIGRATION, privacy/field docs, examples, calibration source/corpus/docs/results.

- [x] Migrate checked-in packet examples to rows.
- [x] Remove readable context-sidecar examples and obsolete plans/designs.
- [x] Replace active docs with the sole 2.2 entrypoints and limits.
- [x] Bind calibration to the actual Doer prompt and semantic basis.
- [x] Replace English-output/context cases with numeric-only cases.
- [ ] Complete final documentation cross-reference and stale-contract scan.

**Acceptance:** no active doc/corpus directs a user to old syntax, bootstrap, natural output, sidecar, or conversion.

## Task 6: Focused non-test completion checks

- [ ] Parse/canonicalize all checked-in `.lh` packets.
- [ ] Validate every calibration graph and generated schema equality.
- [ ] Check all prompt packet examples and anchor blocks.
- [ ] Exercise all control packets and representative full-field/task packets.
- [ ] Exercise malformed frame, duplicate field, missing position, invalid reference, inconsistent state, text, unsupported version, and capacity paths.
- [ ] Confirm stdout contains one numeric frame and successful artifact output leaves stdout empty.
- [ ] Run Python syntax compilation without executing a test suite.
- [ ] Run `git diff --check` and inspect the attributable diff.
- [ ] Record mechanical evidence and mark model behavior unmeasured.

**Acceptance:** active structural behavior is falsifiably verified, while tool-free/model semantic reliability remains explicitly unmeasured.
