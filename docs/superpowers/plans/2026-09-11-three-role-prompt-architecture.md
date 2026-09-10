# Lambda H/2.1 Three-Role Prompt Architecture Implementation Plan

**Goal:** Migrate Lambda H/2.1 from the ambiguous two-role prompt split to standalone Doer, Encoder, and Decoder prompts, with a repo-aware `PROMPT.md` router.

**Architecture:** `prompt/DOER.md` consumes Lambda H and performs represented work; `prompt/ENCODER.md` converts source language/state into a numeric packet plus a separate human semantic audit; `prompt/DECODER.md` converts Lambda H into human-readable explanation without execution. `PROMPT.md` routes repo-aware agents to one or more of those role prompts rather than duplicating the protocol tables.

**Tech Stack:** Markdown role prompts, existing Python Lambda H/2.1 codec/protocol implementation, calibration metadata.

## Global Constraints

- Do not change the Lambda H/2.1 wire format merely to support role separation.
- Do not require natural-language sentence reconstruction before Doer execution.
- Encoder audit must distinguish exact protocol semantics from expected receiver interpretation.
- Decoder must explain, not execute.
- Existing Doer-style calibration ultimately binds to `prompt/DOER.md`.
- Do not restore, reset, overwrite, or recreate concurrent human deletions/edits.
- Before editing a shared existing file, read its current content and apply only the smallest still-required migration.
- Files currently marked human/other-pass-owned by `docs/REWRITE_COORDINATION.md` remain read-only during this pass; record incomplete migration rather than racing that owner.
- No unit-test creation or execution is authorized. Candidate-final validation is limited to focused non-test contract checks.

### Task 1: Create the standalone Doer prompt

**Files:**
- Create: `prompt/DOER.md`

**Interfaces:**
- Consumes: current Lambda H/2.1 wire/field tables and semantic anchors as represented by the current receiver bootstrap and implementation authorities.
- Produces: a standalone Lambda H-native execution prompt.

**Steps:**
- [ ] Copy the current active protocol tables, field contract, context roles, and semantic anchors without changing their values.
- [ ] Make the operational path packet -> structural graph -> semantic interpretation -> hard constraints/task state -> action -> Lambda H response.
- [ ] Retain deterministic `src.codec parse` as the preferred bookkeeping path when tools are permitted, plus a complete manual path.
- [ ] Remove the human-facing `DECODE:` reconstruction exception and any general source-to-packet encoding workflow.

**Acceptance criteria:**
- `DOER.md` is standalone, acts on represented work, defaults protocol replies to Lambda H when prose is not required, and never requires sentence-level reconstruction.

### Task 2: Create the standalone Decoder prompt

**Files:**
- Create: `prompt/DECODER.md`

**Interfaces:**
- Consumes: the same Lambda H/2.1 wire/field tables and semantic anchors as the Doer.
- Produces: a standalone packet-to-human reconstruction prompt.

**Steps:**
- [ ] Reuse the exact structural tables, field contract, context roles, and semantic anchors.
- [ ] Define packet -> structural graph -> semantic interpretation -> human reconstruction as the only normal workflow.
- [ ] Explain exact graph roles, q/f breadth/components, policy/task state, X dependencies, and unresolved ambiguity.
- [ ] Explicitly prohibit executing represented actions merely because they appear in the packet.

**Acceptance criteria:**
- `DECODER.md` is standalone, explains Lambda H accurately to a human, and does not execute the represented task.

### Task 3: Upgrade the Encoder output contract

**Files:**
- Modify: `prompt/ENCODER.md`

**Interfaces:**
- Consumes: ordinary/source meaning and the existing encoder construction workflow.
- Produces: `PACKET` plus a separate `AUDIT` by default.

**Steps:**
- [ ] Preserve the existing source -> graph -> q/f -> numeric-wire construction flow.
- [ ] Change default output to a machine-separable `PACKET` section followed by a human `AUDIT` section.
- [ ] Make the audit cover principal concepts, exact directed structure, field geometry where material, conditions/policy/task state, X dependencies, deliberately preserved ambiguity, exact protocol semantics, and expected conforming-receiver interpretation.
- [ ] State that the audit is outside the wire and must not be forwarded automatically to a Doer.
- [ ] Preserve the safety/non-encryption/hidden-reasoning boundaries.

**Acceptance criteria:**
- The encoder does not execute its source task and emits an inspectable semantic portrayal after the numeric packet.

### Task 4: Make `PROMPT.md` the repo-aware universal router

**Files:**
- Modify: `PROMPT.md`

**Interfaces:**
- Consumes: user intent plus repository access.
- Produces: role selection or explicit role chaining.

**Steps:**
- [ ] Route source -> Lambda H to `prompt/ENCODER.md`.
- [ ] Route Lambda H -> human explanation to `prompt/DECODER.md`.
- [ ] Route Lambda H -> execution/continuation to `prompt/DOER.md`.
- [ ] Explain explicit chaining for mixed workflows and keep the router compact by relying on repo files as authoritative references.

**Acceptance criteria:**
- A repo-aware agent can perform or chain all three roles without treating `PROMPT.md` as a fourth protocol definition.

### Task 5: Migrate protected callers when their owner boundary is available

**Files:**
- Modify when no longer protected: `src/calibration.py`, `calibration/README.md`, `calibration/RESULTS.md`, `README.md`, `SPEC.md`, and any directly affected active role-selection documentation.
- Retire or historicalize: `prompt/BOOTSTRAP.md` only according to the current human-owned migration state.

**Interfaces:**
- Consumes: three-role prompt paths.
- Produces: one active role vocabulary with existing receiver calibration bound to `DOER.md`.

**Steps:**
- [ ] Re-read every shared file immediately before editing.
- [ ] Migrate calibration bootstrap binding from `BOOTSTRAP.md` to `DOER.md` without changing the corpus.
- [ ] Mark prior combined-bootstrap observations historical after the new Doer digest.
- [ ] Replace active two-role documentation references with Doer/Encoder/Decoder terminology.
- [ ] Do not recreate any section already removed or rewritten compatibly by the human/other pass.

**Acceptance criteria:**
- No active calibration or role-selection documentation treats `BOOTSTRAP.md` as the current execution/decoder role, unless a concurrent owner boundary prevents completion and that remaining work is reported explicitly.

### Task 6: Candidate-final non-test contract verification

**Files:**
- Read-only verification of the three role prompts and direct callers.

**Steps:**
- [ ] Confirm Doer, Encoder, and Decoder structural tag/enum tables are identical.
- [ ] Confirm E/R/A/T/K/V anchor blocks agree across all three prompts and with `semantics/basis.json`.
- [ ] Parse every bracketed Lambda H example embedded in the three role prompts with the current codec.
- [ ] Confirm role-specific prohibitions: Doer has no general source encoding/reconstruction workflow; Decoder does not execute; Encoder emits packet plus audit and does not execute.
- [ ] Run `git diff --check HEAD`.

**Acceptance criteria:**
- The three prompts are structurally compatible with one Lambda H/2.1 protocol contract and the implementation contains no accidental dual-role fallback introduced by this migration.
