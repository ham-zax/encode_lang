# Agent-Native Ambient Context Implementation Plan

**Goal:** Make deictic agent references resolve to exact host-grounded X bindings without changing the Lambda H/2.2 wire.

**Architecture:** Add a host-local context resolution module that is outside transport and expose it through the package API. Keep the existing numeric packet and symbolic IR unchanged. Update the three role prompts and active docs so Encoder selects ambient-capable X references only when grounded, Doer resolves them against an exact namespace match, and Decoder reports whether those identities are resolved.

**Tech Stack:** Python standard library, existing Lambda H/2.2 developer graph, symbolic IR, numeric row codec, Markdown prompts/docs.

## Global Constraints

- Keep `ΛH2.2|` numeric rows byte-compatible and version unchanged.
- Ambient context is host-grounded, context-scoped, and never model-guessed.
- Lambda H constrains instruction transport, not normal Doer behavior after semantic handoff; native output is default and `P.reply=packet` is explicit opt-in.
- Ambient-capable roles are `X02`, `X03`, `X06`, `X07`, `X08`, and `X09` only.
- Host-local bindings may contain arbitrary endpoint-local objects/text but are never serialized by the protocol merely because they exist.
- `context 0` intentionally resolves from receiver-current grounded ambient state already active at packet receipt; X08 is a frozen starting workspace, never a filesystem/repository search. Nonzero namespace mismatch never falls back to the receiver's current environment.
- Existing inline X bindings retain protocol precedence.
- Missing exact ambient identity uses existing `need` behavior; do not replace it with a generic semantic entity when identity matters.
- Do not add or run tests unless separately authorized. Use focused non-test checks only at candidate-final state.
- Preserve current staged/user work; do not stage, reset, commit, or push.

### Task 1: Add host-local ambient resolution

**Files:**
- Create: `src/context.py`
- Modify: `src/__init__.py`

**Interfaces:**
- Consumes: valid Lambda H developer graph and optional host-local namespace/bindings.
- Produces: `HostContext`, `ContextResolution`, `resolve_context`, `ambient_ref`, `AMBIENT_ROLES`, and `AMBIENT_REFS`.

**Steps:**
- [x] Define canonical ambient role mappings.
- [x] Validate host namespace and X binding keys without constraining local binding value types.
- [x] Resolve required X references using packet-inline value first, then context-appropriate host grounding: receiver-current ambient state for context 0 or exact-namespace host binding for nonzero contexts, otherwise mark missing.
- [x] Keep resolution side-effect free and independent of codec serialization.
- [x] Export the context API lazily from `src`.

**Acceptance criteria:**
- Context 0 can represent receiver-current ambient values through `HostContext.current`; matching nonzero host namespaces resolve scoped X references; different nonzero namespaces leave them missing; no local object is serialized.

### Task 2: Make role prompts agent-native

**Files:**
- Modify: `prompt/ENCODER.md`
- Modify: `prompt/DOER.md`
- Modify: `prompt/DECODER.md`
- Modify: `PROMPT.md`

**Interfaces:**
- Encoder: deictic source meaning + host context -> grounded X reference.
- Doer: packet + matching host context -> resolved exact target or `need`.
- Decoder: packet + optional matching host context -> English resolved/unresolved explanation.

**Steps:**
- [x] Define ambient-capable role table in each standalone role prompt.
- [x] In Encoder, map “this repo/workspace/environment” to grounded `X08` and analogous deictic roles to their ambient refs.
- [x] Prohibit replacing a missing exact deictic identity with a generic semantic `E` solely to avoid `need`.
- [x] In Doer, ground context-0 ambient references from authoritative receiver-current host/session facts, bind X08 only from the already-active host/IDE workspace or cwd/enclosing Git root without global/lateral repository search, freeze it for the request, require exact namespace matches for nonzero host-local resolution, preserve normal authority/policy after identity resolution, and hand successful decoding into normal native agent execution/output unless `P.reply=packet` is explicit.
- [x] In Decoder, report host-grounded identity only when actually available; otherwise explain the conventional X role and missing context.
- [x] Make root router state that repo-aware host context is local setup, not protocol payload.

**Acceptance criteria:**
- A grounded “investigate this repo” uses `X08`, stays inside the already-active workspace, and then behaves like the equivalent ordinary-language agent instruction; the same packet on a different/unbound host does not silently target another repository.

### Task 3: Synchronize active architecture documentation

**Files:**
- Modify: `SPEC.md`
- Modify: `README.md`
- Modify: `MIGRATION.md`
- Modify: `docs/PRIVACY.md`
- Modify: `docs/superpowers/specs/2026-09-11-model-facing-ir-opaque-wire-design.md`
- Modify: `docs/superpowers/plans/2026-09-11-human-decoder-ir-codec-repair.md` only where its prior strict-X note is superseded.

**Interfaces:**
- Consumes: host-local ambient resolution contract.
- Produces: one consistent active description of context identity, transport opacity, and failure behavior.

**Steps:**
- [x] Document ambient-capable refs and exact namespace resolution precedence.
- [x] State that host-local objects/text are outside wire/schema and do not weaken numeric transport opacity.
- [x] Preserve `need` for missing host context and clarify namespace mismatch behavior.
- [x] Remove stale statements that all X roles require explicit non-ambient provisioning or that ambient X08 is categorically out of scope.

**Acceptance criteria:**
- Active docs and plans agree that ambient context is host-grounded and scoped, with no new wire representation or implicit receiver-local substitution.

### Task 4: Candidate-final non-test verification

**Files:**
- Read-only verification of the changed implementation and contract surfaces.

**Steps:**
- [x] Exercise `resolve_context` for matching namespace, mismatched namespace, packet-inline precedence, arbitrary local object values, and missing refs.
- [x] Confirm equivalent packets format to the same Lambda H/2.2 numeric rows before and after this feature.
- [x] Confirm the grounded “investigate this repo” IR encodes through `src.codec` without a generic E target.
- [x] Run Python syntax compilation and `git diff --check` on attributable changes.
- [x] Sweep active files for stale claims that X08 is never ambient-capable or that deictic exact identities should become generic semantic nodes.

**Acceptance criteria:**
- Host-grounded ambient resolution works end to end at the library/prompt boundary while transport bytes and protocol version remain unchanged.
