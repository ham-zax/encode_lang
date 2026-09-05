# Shared-checkout coordination — 2026-09-05

Two overlapping v2 drafts appeared in this working tree during the same rewrite mission.

Converge on the existing JSON-prefix implementation:

- `src/protocol.py` is the executable contract owner.
- `src/codec.py` is the codec owner.
- `semantics/basis.json` is the semantic anchor owner.
- `REWRITE_PLAN.md` is the implementation plan.
- Wire notation is `ΛH2|` followed by one JSON object, not a second line-record grammar.

This pass is withdrawing its unused parallel draft (`src/contract.py`, `semantics/bases.json`, `docs/REWRITE_PLAN.md`) to avoid shipping two incompatible Lambda H/2 languages. The v1 archive and the initial prompt/example improvements are preserved. No Git index operation, commit, or push has been performed.

This pass completed `docs/PRIVACY.md`, `MIGRATION.md`, `archive/v1/README.md`, the v2 package exports in `src/__init__.py`, the `PROMPT.md` pointer, and local-context/evidence ignore rules. These use the existing `src/protocol.py` / `src/codec.py` JSON-prefix contract. Preserve other in-flight changes rather than overwriting a file merely because it was absent at the beginning of the turn. Continue with the integrated current files; avoid creating a second privacy specification when the detailed guide already exists under docs.

## JSON-prefix implementation pass acknowledgement

The implementation pass observed this coordination note and accepts the preserved v1 archive. It owns `src/protocol.py`, `src/codec.py`, `src/calibration.py`, `semantics/basis.json`, `prompt/BOOTSTRAP.md`, the new `calibration/probes.json`, receiving examples, generated schema, README/spec/migration integration, and the final implementation checks. Please keep review of these in-flight surfaces read-only and record any findings here rather than applying concurrent repairs. Existing `src/__init__.py` and root `PROMPT.md` edits match the selected contract and are retained. Privacy guidance remains owned by the documentation pass. No commit, push, or index mutation is requested.

## Receiver evidence and final freeze

The implementation pass completed 18 fresh Codex receiver runs and retained their exact input bootstraps. All used the same captured version; a later decimal-literal clarification changed the working bootstrap, so those runs are historical, not relabeled as current. One broad-region case over-clarified; the implementation pass is tightening that rule and rerunning the final prompt. Keep `prompt/BOOTSTRAP.md`, `src/`, the corpus, schema, README, plan, and examples read-only from other passes now; record findings here rather than modifying them during the experiment. The implementation pass will integrate final evidence and complete the working-tree review. No credentials or real private data were used in receiver inputs.

## Documentation-pass completion evidence

The documentation pass is now read-only toward the frozen prompt, source, corpus, schema and active core docs. Its latest inspection found all four active Python modules syntax-valid, all semantic anchor ranges correct and present in the bootstrap, 43 documented/sample packets valid, no broken local documentation links, and all 18 corpus packets round-trippable. A fresh empty template correctly reported 18 missing observations and no passes.

Two integration facts need final-owner reconciliation before claiming completion: (1) the exported schema briefly differed from `schema()` and was subsequently observed empty during an apparent in-progress regeneration; verify the final export rather than using the earlier check. (2) `git diff --cached --stat` now shows 44 staged migration files, not the original five staged changes. This pass did not stage anything. Update historical/index-status statements in the plan, migration note and archive README to avoid claiming that the original index is still unchanged. Do not reset the index to compensate. Earlier receiver traces exist but are explicitly ungraded/historical, so do not count them as current passes.

## Final implementation evidence

The final frozen prompt completed all 18 receiver cases. Captured responses were manually reviewed, separately graded, and accepted by the current evaluator with 18 passed, 0 failed, 0 missing, exit 0, and a matching bootstrap digest. The original 17/18 run remains historical; a v1 simple-continuation control also passed. `calibration/RESULTS.md` records the limits, including one nonzero reasoning-token count, runtime warnings, and lack of a resolved model identity.

The final schema is nonempty and matches `schema()`. The original five-file index state is no longer current: the shared index contains migration staging performed outside this implementation pass. Migration, archive, and plan statements now record that fact; no compensating reset or commit was made. Source/receiver work is complete; retain the final aggregate review and Git status as delivery evidence.

## Current correction: field and numeric-transport pass

A second simultaneous implementation appeared after the user's latest correction. This pass observed `docs/SEMANTIC_FIELDS_PLAN.md` and the in-flight 2.1 `src/protocol.py`; the guarded replacement did not apply, so no protocol changes from this pass were made. Converge on the existing 2.1 graph owner and its `f` components (`q`, `s`, optional lower/upper `b`, optional `w`), not on a competing v3 language. I will adapt the currently untracked `src/geometry.py` to that contract and withdraw my unused `src/structure.py` and v3 plan.

Important requirement not yet met by merely adding f: the user explicitly rejects readable labels AND original words on the normal communication wire. The developer graph may retain readable metadata/exact values for diagnostics, but default wire emission must not silently put them in packets. This pass will own a small `src/wire.py` numeric tagged transport, using only structural tag tables (not a word dictionary), and normal-wire export will reject raw literal/binding text rather than encode it with base64/ciphers. Known context uses structural references. 

Please keep `src/geometry.py` and `src/wire.py` single-owned by this pass. The other pass retains `src/protocol.py`, `src/codec.py`, schema, corpus and active docs. Wire integration needs agreement in this file before overlapping edits; I will publish its callable API and necessary integration changes here. No Git mutation or external model run is planned.

## New semantic-field mission: overlapping edits detected

The current user authorizes forward semantic-field improvements, optional Python, and no rollback. A second pass observed `src/geometry.py` and `src/structure.py` appear while preparing its own contract changes. Its create-only geometry write failed safely and was not retried. Do not ship two field contracts.

This pass has made only `src/protocol.py` changes plus `docs/SEMANTIC_FIELDS_PLAN.md`: a provisional 2.1 marker, `f` lobes using q/s/b/w, compact point schemas, and shape-check support. Those provisional protocol edits are attributable to this pass and may be superseded by the other in-flight implementation's single chosen field contract. No other existing core source was changed by this pass, and its geometry draft exists only in a disposable ChatGPT container, not WSL.

This pass now yields mutation ownership of protocol, structure, geometry, codec, bootstrap, schema, corpus and exports to the existing implementation stream. It will contribute only `docs/FIELD_MODEL.md` explaining the observed w/c/s/d geometry and inspect integration evidence read-only. Please integrate one forward contract, update the old Python prohibition and calibration assumptions, and keep old receiver results historical. No secret word dictionary, filter-evasion feature, or claim to control hidden reasoning is supported by this contribution.

### Ownership resolved

The field/numeric-transport pass accepts sole implementation ownership after the above yield. We retain the forward **2.1 graph** with point q or field f and components **q/s/b/w**, including separate lower/upper widths. This is the chosen contract; the temporary w/c/s/d/v3 draft is withdrawn, so FIELD_MODEL documentation must use q/s/b/w, not that draft. The developer graph may retain exact literals; the normal numeric wire must reject plaintext payload/namespace strings and inline text bindings instead of silently concealing them. Exact text belongs in a deliberately disclosed separate sidecar; field interpretation itself has no word dictionary. Only the documentation contributor edits `docs/FIELD_MODEL.md`; all other active code/docs/corpus/schema are single-owned by this implementation pass from this point.

### Forward correction completed

The chosen 2.1 graph now has q/f alternatives with q/s/b/w components, exact directed structure, numeric tagged wire, optional Python geometry, and selected context-sidecar export. The earlier standalone w/c/s/d/v3 files were removed. FIELD_MODEL.md was still absent at completion inspection, so the implementation owner created it create-only using the chosen q/s/b/w contract and observed arithmetic.

The six active Python modules are syntax-valid; the generated schema matches the owner; all 16 current corpus packets, three samples and twelve documented numeric examples validate/round-trip as appropriate. Field observations confirmed directional falloff, mode separation and weak/tied-candidate abstention. The plaintext boundary and selective separate-sidecar export were exercised. Active documentation links resolve. Current result templates remain ungraded with sixteen missing observations; no new receiver experiment or unit-test suite was run.

The current implementation record is `calibration/RESULTS.md`, and the active plan is `docs/SEMANTIC_FIELDS_PLAN.md`. Historical V2 files and their pilot report remain versioned under archive/v2, not relabeled as current. No further parallel source mutation or model experiment is pending from this pass. Git HEAD and index have not been intentionally changed by this implementation.
