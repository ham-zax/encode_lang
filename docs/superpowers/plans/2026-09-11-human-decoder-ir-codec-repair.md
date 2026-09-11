# Lambda H/2.2 Human Decoder + Codec-Owned IR Repair Implementation Plan

**Goal:** Restore the human-facing Encoder/Decoder contract while keeping the shallow opaque Lambda H/2.2 numeric row wire and moving model-side serialization behind a deterministic symbolic IR codec boundary.

**Architecture:** `src/ir.py` owns a shallow symbolic line IR that can represent the full existing developer graph without arbitrary source text. `src.codec` translates symbolic IR to canonical numeric Lambda H/2.2 rows and numeric rows back to symbolic IR. Encoder and Doer reason/construct against symbolic IR when tooling is available; only the codec emits transport rows. Decoder consumes numeric rows through the codec and returns an English explanation to the human. Agent-to-agent transport remains numeric-only.

**Tech Stack:** Python standard library, existing `src.protocol` developer graph, `src.wire` structural mappings, `src.rows` numeric row framing, Markdown role prompts/docs.

## Global Constraints

- Keep Lambda H/2.2 shallow numeric rows as the sole agent-to-agent wire.
- Do not reintroduce Lambda H/2.1 compatibility or the retired combined bootstrap.
- Human-facing Encoder may emit `PACKET` plus a separate English `AUDIT`; only `PACKET` is transport.
- Human-facing Decoder returns English explanation and never executes represented actions.
- Historical note: this repair originally kept Doer replies numeric by default. The later native semantic-handoff correction supersedes that rule: omission of `P.reply` means normal host-native output, while `P.reply=packet` is explicit opt-in.
- When codec tooling is available, models must not manually serialize or rewrite numeric rows.
- The symbolic IR is model-facing/local only and must not carry arbitrary source wording or become a second transport protocol.
- Preserve all current E/R/A/T/C/K/P/task/V/q/f semantics and 2.2 numeric row bytes for equivalent graphs.
- Historical note: this repair preserved the then-current strict X/context semantics. The later agent-native ambient-context design supersedes that point with host-grounded, exact-namespace ambient-capable X02/X03/X06/X07/X08/X09 resolution without changing the wire.
- Do not add or run tests unless separately authorized. Use focused non-test parser/round-trip/CLI checks at candidate-final state.

### Task 1: Add the complete symbolic line IR

**Files:**
- Create: `src/ir.py`

**Interfaces:**
- Consumes: current Lambda H/2.2 developer graph dictionaries validated by `src.protocol`.
- Produces: `parse_ir(text) -> dict` and `format_ir(packet) -> str`.

**Steps:**
- [ ] Define one canonical line grammar with named structural records and typed references, coordinates, scalars, policy/task fields, q points, f components, bands, weights, choices, and controls.
- [ ] Keep each declaration shallow; use stable identifiers (`E0`, `R0`, `A0`, `T0`, `C0`, `X08`) and structural keywords only.
- [ ] Reject arbitrary unrecognized text/tokens instead of preserving them.
- [ ] Reuse `src.protocol.require_valid` as the semantic/invariant authority after parsing.
- [ ] Make `format_ir(parse_ir(format_ir(G)))` preserve the same developer graph under `_same_json`.

**Acceptance criteria:**
- Every currently supported developer-graph field has one deterministic symbolic IR spelling and round-trips without changing the numeric 2.2 wire representation.

### Task 2: Move serialization ownership into `src.codec`

**Files:**
- Modify: `src/codec.py`
- Modify: `src/__init__.py`

**Interfaces:**
- Consumes: symbolic IR or numeric Lambda H/2.2 rows.
- Produces: canonical numeric rows or canonical symbolic IR.

**Steps:**
- [ ] Keep existing `format` command as numeric canonicalization.
- [ ] Add `encode` command: symbolic IR input -> parse/validate -> canonical numeric rows.
- [ ] Add `decode` command: numeric rows -> parse/validate -> canonical symbolic IR.
- [ ] Preserve numeric-only failure controls for commands whose requested output is numeric (`format`, `encode`).
- [ ] For local `decode`, report local CLI errors on stderr rather than pretending a failed human/debug conversion is transport output.
- [ ] Export the IR parse/format APIs lazily from `src` alongside packet APIs.

**Acceptance criteria:**
- A model can give symbolic IR to the codec and receive canonical numeric transport without calculating row kinds, row counts, field tags, list positions, or reference namespaces manually.

### Task 3: Restore role boundaries

**Files:**
- Modify: `prompt/ENCODER.md`
- Modify: `prompt/DOER.md`
- Modify: `prompt/DECODER.md`
- Modify: `PROMPT.md`

**Interfaces:**
- Encoder: English/source meaning -> symbolic IR -> codec -> numeric `PACKET` + English `AUDIT`.
- Historical Doer path at the time: numeric packet -> codec -> symbolic IR -> execute -> symbolic response IR -> codec -> numeric packet. This output requirement is superseded by the later native semantic-handoff rule.
- Decoder: numeric packet -> codec -> symbolic IR -> English explanation only.

**Steps:**
- [ ] Remove normal-path instructions that tell Encoder/Doer/Decoder to manually calculate numeric row structure when codec tooling is available.
- [ ] Keep manual row construction/parsing only as the explicit no-codec fallback.
- [ ] Restore Encoder `PACKET` + `AUDIT` output and explicitly mark audit as non-transport.
- [ ] Restore Decoder English reconstruction of represented semantics, structure, ambiguity, controls, and missing X context without executing actions.
- [ ] Historical requirement: keep Doer numeric-only response contract and no-English-intermediate execution behavior. Superseded: only the no-required-English-intermediate part remains; successful post-handoff output is native unless `P.reply=packet` is explicit.
- [ ] Make root router select Decoder for `decode:`/`explain` and allow human-facing English there without weakening transport opacity.

**Acceptance criteria:**
- Historical acceptance at the time: `encode:` gives the human a numeric packet and readable audit; `decode:` gives the human a readable explanation; bare numeric packet routes to Doer. The later semantic-handoff correction supersedes the numeric-output requirement for Doer.

### Task 4: Synchronize active contract documentation

**Files:**
- Modify: `README.md`
- Modify: `SPEC.md`
- Modify: `MIGRATION.md`
- Modify: `docs/superpowers/specs/2026-09-11-model-facing-ir-opaque-wire-design.md`
- Modify: `docs/superpowers/plans/2026-09-11-three-role-prompt-architecture.md`
- Modify: `calibration/README.md` only if it encodes the stale Decoder/Encoder-output assumption.

**Interfaces:**
- Consumes: repaired role/codec contract.
- Produces: one active architecture description with numeric transport opacity and human control-plane decoding kept separate.

**Steps:**
- [ ] State explicitly that numeric-only applies to runtime agent-to-agent wire, not the human Decoder/Audit surface.
- [ ] Document the symbolic IR as local/model-facing and `src.codec encode|decode` as its deterministic boundary.
- [ ] Keep 2.2 row grammar authoritative for transport and preserve existing opacity/security limits.
- [ ] Remove stale claims that Decoder is only a canonicalizer or that every assistant response must be numeric.

**Acceptance criteria:**
- Active docs describe one consistent transport/control-plane split and no longer contradict the approved architecture.

### Task 5: Candidate-final non-test verification

**Files:**
- Read-only verification of the changed contract surfaces.

**Steps:**
- [ ] Round-trip representative full graphs through developer graph -> symbolic IR -> developer graph -> numeric rows -> developer graph.
- [ ] Confirm all existing `.lh` examples still canonicalize byte-for-byte under the 2.2 row codec.
- [ ] Confirm `src.codec encode` accepts symbolic IR and emits only one numeric frame; confirm `src.codec decode` emits symbolic IR locally.
- [ ] Confirm the review example control decodes through the symbolic IR to `control abstain` / code `0`, giving the Decoder enough structure to explain material ambiguity in English.
- [ ] Confirm root router and three prompts encode the intended role split with no stale numeric-only human-interface language.
- [ ] Run Python syntax compilation and `git diff --check` on the attributable change.

**Acceptance criteria:**
- The demonstrated regressions are removed while the 2.2 numeric wire remains stable and the codec, not the model, owns normal-path serialization.
