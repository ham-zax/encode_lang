# Context-0 X00 Subject Grounding Implementation Plan

**Goal:** Let Lambda H/2.2 resolve `X00` from one already-established conversational subject in `context 0`, while making the Encoder avoid unresolved required X references and preserving strict nonzero-context behavior.

**Architecture:** `src.context` remains the runtime owner for required-X discovery and exact context resolution. It gains context-0 `X00` support plus a deterministic preflight classification API; the host/model must supply a single established subject explicitly rather than asking the library to infer from arbitrary conversation text. Encoder/Doer/Decoder prompts define when that conversational subject is semantically valid and keep `X08` distinct as workspace identity. The numeric wire, symbolic IR grammar, schema, and codec serialization remain unchanged.

**Tech Stack:** Python standard library, existing Lambda H/2.2 context APIs, Markdown role prompts/specs.

## Global Constraints

- Keep `ΛH2.2|` and `LH-IR 2.2` unchanged.
- `X00` means current conversational/task subject; `X08` remains current workspace/environment/repository.
- Prefer the most semantically correct already-groundable X role, not merely the easiest available binding.
- Context-0 `X00` may use one already-established, unambiguous subject present before packet receipt; never search or manufacture a subject.
- Nonzero `X00` remains strict and requires a matching host binding.
- Explicit packet bindings and explicit matching host bindings outrank conversational fallback.
- Encoder preflight classifies every required X as packet-bound, host-ambient-resolvable, conversation-ambient-resolvable, or unresolved.
- `UNBOUND_REQUIRED_X` is an Encoder/local diagnostic, not a new wire control or codec error.
- Do not add or run tests unless separately authorized. Use focused non-test checks at candidate-final state.

### Task 1: Extend the local context API

**Files:**
- Modify: `src/context.py`
- Modify: `src/__init__.py`

**Interfaces:**
- Consumes: valid packet graph, optional `HostContext`, optional caller-supplied single current subject.
- Produces: normal `ContextResolution` plus a deterministic required-X preflight classification.

**Steps:**
- [ ] Add `subject -> X00` to the ambient-role table.
- [ ] Add a small immutable preflight result carrying each required X classification and unresolved refs.
- [ ] Add `preflight_context(...)` that preserves packet-inline precedence, recognizes exact same-namespace host bindings, recognizes caller-supplied current subject only for `context 0` + `X00`, and marks all remaining refs unresolved.
- [ ] Extend `resolve_context(...)` with the same optional current-subject fallback after inline and matching host binding resolution.
- [ ] Keep multiple-subject ambiguity outside the library: callers pass a subject only when exactly one is established.
- [ ] Export the new preflight API from `src`.

**Acceptance criteria:**
- Context-0 X00 resolves from an explicit single current-subject value when no stronger binding exists; nonzero X00 never does; X08 behavior is unchanged.

### Task 2: Make Encoder selection and lint explicit

**Files:**
- Modify: `prompt/ENCODER.md`
- Modify: `PROMPT.md`

**Interfaces:**
- Consumes: source meaning plus already-known host/conversation context.
- Produces: semantically appropriate X selection and no accidentally unresolved required X refs.

**Steps:**
- [ ] Add `X00` to context-0 ambient-capable roles as the established discourse/task subject.
- [ ] Require role-first selection: use X08 for repo/workspace identity, X02 for goal, X03 for artifact, X06 for plan, X07 for blocker, X09 for output, and X00 only for a genuinely separate/current discourse subject.
- [ ] Add `UNBOUND_REQUIRED_X` preflight semantics before codec serialization.
- [ ] Require the Encoder to rewrite to another X only when it represents the same intended identity role; otherwise surface the unresolved requirement instead of emitting an accidentally unbound task packet.
- [ ] State that one clear conversational subject is resolvable in context 0; multiple/no subjects are unresolved.

**Acceptance criteria:**
- Encoder guidance no longer casually emits X00 when X08 or another exact role is semantically correct, and it does not emit an unintentionally unresolved required X ref.

### Task 3: Add controlled Doer/Decoder subject grounding

**Files:**
- Modify: `prompt/DOER.md`
- Modify: `prompt/DECODER.md`

**Interfaces:**
- Consumes: decoded X refs plus receiver-current conversation state.
- Produces: context-0 X00 grounding only when one subject is already dominant and unambiguous.

**Steps:**
- [ ] Define X00 as a snapshot of one established active conversational/task subject at packet receipt.
- [ ] Preserve precedence: packet-inline -> exact matching host/session binding -> context-0 single established conversational subject -> missing.
- [ ] Prohibit deriving X00 from cwd/X08, filenames, repository scans, relation-field names, or post-packet investigation.
- [ ] Require `need X00` when multiple or no plausible established subjects remain.
- [ ] Keep nonzero X00 strict.

**Acceptance criteria:**
- A conversation centered on one project can resolve context-0 X00 without interruption, while ambiguous or nonzero contexts still fail closed.

### Task 4: Synchronize the active contract documentation

**Files:**
- Modify: `SPEC.md`
- Modify: `README.md`
- Modify: `MIGRATION.md`
- Modify: `docs/PRIVACY.md`
- Modify: `docs/superpowers/specs/2026-09-11-agent-native-ambient-context-design.md`
- Modify: `docs/superpowers/plans/2026-09-11-agent-native-ambient-context.md`

**Interfaces:**
- Consumes: Tasks 1-3 target contract.
- Produces: one documented interpretation of context-0 ambient subject/workspace behavior.

**Steps:**
- [ ] Add X00 to the context-0 ambient model while explicitly separating it from X08.
- [ ] Document the single-established-subject rule and strict nonzero behavior.
- [ ] Document Encoder preflight classification and `UNBOUND_REQUIRED_X` as local-only.
- [ ] Preserve the existing X08 frozen-workspace/no-search and native-output rules.

**Acceptance criteria:**
- Active code, prompts, and docs all describe the same X00/X08 resolution semantics without introducing a second compatibility path or wire change.

### Task 5: Candidate-final non-test verification

**Files:** none

**Interfaces:**
- Consumes: final working tree.
- Produces: observable evidence for the requested contract without running the test suite.

**Steps:**
- [ ] Compile `src` without executing tests.
- [ ] Run focused Python probes for context-0 X00 conversational fallback, explicit-binding precedence, ambiguous/no-subject missing behavior, nonzero strictness, and unchanged X08 resolution.
- [ ] Parse all numeric packet examples embedded in Encoder/Doer/Decoder prompts.
- [ ] Run `git diff --check` and a bounded stale-contract search.

**Acceptance criteria:**
- The focused probes and structural checks pass, with no tests executed and no wire/schema changes.
