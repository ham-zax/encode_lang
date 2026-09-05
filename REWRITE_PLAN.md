# Lambda H/2 Implementation Plan

> Historical plan for the V2 baseline. The active forward correction is [semantic fields and numeric wire](docs/SEMANTIC_FIELDS_PLAN.md). V2 pilot results below do not describe the current 2.1 prompt.

**Goal:** Replace positional semantic packets with a prompt-portable, directly actionable representation and an honest privacy model.

**Architecture:** One versioned JSON data model, transported as `ΛH2|` plus a JSON object. Sparse named coordinates carry approximate meaning; explicit references, roles, conditions, constraints, and task snapshots carry operational structure. Python is optional authoring/inspection tooling, never a receiver requirement. Encryption is a separate endpoint responsibility, not a property of semantic notation.

**Tech Stack:** Python standard library, JSON Schema, Markdown; existing semantic anchors retained where their meaning is unchanged.

## Global constraints

- User approved a complete project rewrite: improve prompts/examples, migrate the protocol and implementation, then finish the new bootstrap.
- Preserve semantic geometry rather than inventing a universal word-to-secret-code dictionary.
- Preserve task-critical distinctions and uncertainty. Never promise exact recovery of information that was omitted.
- A bare packet should elicit the represented response, not a decoding explanation or routine acknowledgement.
- No hidden reasoning or cross-model performance guarantees. Behavioral results require actual receiving-session evidence.
- No custom cryptography, secret keys in prompts, invented confidentiality, or changes to external accounts/services.
- Do not commit, push, install dependencies, change Git's existing index, or disturb unrelated state.
- Initial state: main at 667204d; five staged v1 documentation/calibration edits. Incorporate their general intent (composition, continuation, context synchronization, contextual sense separation) into v2. This pass does not manipulate the index. A later shared-checkout inspection found the migration staged outside this pass; preserve that state rather than resetting it.

## Ownership frontier

`SPEC.md` + `semantics/` + `schema/lambda_h_packet.schema.json` + `src/` + the receiver bootstrap + examples/calibration must describe the same v2 contract. Root redirects must not retain competing definitions.

## Tasks

### 1. Interaction-first bootstrap and demonstrations

Initial files: the v1 bootstrap and examples, now preserved under `archive/v1/`. Final receiver: `prompt/BOOTSTRAP.md`; final worked conversations: `examples/conversations.md`.

Make ordinary bare packets lead to direct responses; distinguish task tools from decoding tools; clarify bootstrap-with-payload behavior, material ambiguity, completion, and permission inheritance. Then migrate these demonstrations to v2 after the data model lands.

### 2. One v2 contract and optional codec

Files: `SPEC.md`, `schema/lambda_h_packet.schema.json`, `src/protocol.py`, `src/codec.py`, `src/__init__.py`, `semantics/basis.json`.

Use ordinary JSON grammar rather than a second custom lexer. Replace offset hex vectors with sparse coordinate objects such as `{"A13":6,"A14":7}`. Add explicit action targets/instruments/order, negation, exact conditions, scoped context bindings, and task completion state. Separate exact constraints from approximate semantic scores. Reject v1 packets with a migration diagnostic, rather than guessing a conversion of missing roles/state.

### 3. Behavioral calibration and complete receiving examples

Files: `calibration/probes.json`, `calibration/README.md`, `src/calibration.py`, `examples/conversations.md`.

Replace geometry-only success claims with a receiver task corpus and an evidence-recording evaluator. Include direct continuation, completed tasks, ambiguity, relation direction, exact literals, constraints, condition gates, fresh-context handoffs, and privacy-limited disclosure. Preserve unknown/unrun results rather than filling them with synthetic passes. Model execution is not available merely because local codec checks work.

### 4. Privacy and final product surface

Files: `docs/PRIVACY.md`, `MIGRATION.md`, `README.md`, `PROMPT.md`, `.gitignore`, `archive/v1/README.md`, final bootstrap.

Explain data minimization through scoped references, endpoint trust, encrypted transport/storage with established external tooling, metadata limits, and why a hosted receiver necessarily sees the meaning it processes. Supply local-only encryption usage without adding a bespoke encryption implementation. Retire competing legacy definitions and identify any remaining v1-only artifacts honestly.

## Completion evidence

Exercise the optional v2 CLI against the shipped packets, inspect schema/implementation/prompt agreement, inspect the attributable migration diff, and perform a bounded non-test syntax/contract check. Do not claim model-behavior improvement without actual fresh-session results. No test-suite expansion or execution is independently requested; do not manufacture test work.

## Progress

- Interaction-first changes were made before archiving v1; the pre-existing work is preserved in historical files. The shared index now contains migration staging, not merely its initial five-file state.
- The active implementation uses one JSON-prefix v2 contract, sparse anchors, explicit conditions/policy/task state, scoped references, and selective handoff. Retired v1 APIs are not runtime fallbacks.
- The standalone prompt, specification, generated schema, current exports, README, migration notes, worked conversations, and privacy guide are in place.
- The 18 receiving cases parse and round-trip. An empty evidence template reports 0 passes, 0 failures, and 18 missing observations. A direct codec check preserved quoted separators and line breaks; handoff excluded an unrelated context binding.
- Fresh Codex receiver observations are now recorded: initial v2 17/18, final frozen v2 18/18, zero decoder-tool calls. The initial broad-region over-clarification was repaired and the failed observation preserved. One final case reported 11 reasoning-output tokens; no zero-reasoning guarantee is made.
- A matched simple-continuation control using the original v1 bootstrap also succeeded. This small development pilot does not establish cross-model generalization, speedup, token savings, or universal v2 superiority. See `calibration/RESULTS.md`; raw evidence remains ignored under `.local/evaluations/`.
- Active Python compilation, 42 documented wire examples, the 18 corpus round-trips, generated-schema equality, and anchor-set consistency passed. The selected handoff carries X02 but excludes the unrelated X99 demo binding; unbound context remains explicitly missing.
- Direct boundary checks reject duplicate JSON keys, retired v1 packets, undeclared targets, cyclic action prerequisites, false complete-state snapshots, and mismatched context namespaces. Both shipped `.lh` demo files parse and round-trip.
- Implementation and the receiver pilot are complete. No encryption installation, key generation, unit-test suite execution, commit, push, or Git-index update was performed by this pass. Final aggregate working-tree evidence accompanies delivery; preserve any staging performed elsewhere in the shared checkout.
