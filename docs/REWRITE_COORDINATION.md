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
