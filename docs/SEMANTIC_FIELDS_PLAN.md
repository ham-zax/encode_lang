# Semantic fields implementation plan

**Goal:** Represent a concept as a graded neighborhood, with a focus and directional falloff, rather than requiring an exact word or forcing an English reconstruction.

**Architecture:** Extend the current task graph forward to Lambda H/2.1. E/R/A/T nodes may use a point `q` or a field `f`: a weighted collection of numerical centers with explicit widths and optional lower/upper directional widths. The existing exact target, relation, condition, permission and progress structure remains authoritative. Optional Python computes geometric compatibility.

**Tech stack:** Existing Python standard-library codec and schema owner, JSON, Markdown. No new dependency or external model call.

## Constraints

- Do not roll back V2 or change existing Git history/index. Starting checkout is clean main at 38b12de.
- Python support is permitted, not compulsory. Remove the blanket prohibition on using a decoder, but do not require a decoding preamble or an English intermediate response.
- Preserve geometric alternatives instead of averaging distinct senses. A numerical field is not an encrypted word dictionary or a calibrated probability distribution.
- Keep source authority, explicit prohibitions, task completion, and unknown-condition behavior unchanged. No filter-evasion feature, secret alias rotation, or hidden-reasoning-language claim.
- Preserve necessary exact data in the developer graph or a deliberately selected context sidecar. The default communication wire is numeric tagged arrays and rejects plaintext payloads/descriptive namespace names instead of hiding or dropping them. Prefer numerical regions for broad concepts; do not claim omitted identities are recoverable.
- No new test suite, test edits, or external receiving-model experiments. Direct arithmetic/codec examples, syntax inspection and schema consistency are the completion evidence; earlier V2 model results remain historical.

## Task 1: Versioned field contract

**Files:** src/protocol.py; semantics/basis.json; schema/lambda_h_packet.schema.json.

Add `f` as an alternative to node `q`. Each component has q (center), s (positive default width), optional b (per-axis [lower-side width, upper-side width]), and optional w (positive relative peak weight, default 1). Multiple components preserve live regions; q and f must not coexist on one node. Preserve numeric widths, finite values, axis identity and exact role/permission constraints in the structural and executable contracts. Bump the active packet version to 2.1; reject old versions explicitly rather than silently interpreting an unsupported field.

**Acceptance:** Valid fields serialize without losing components or widths. Invalid widths, mixed bases and conflicting point/field declarations are rejected. Existing task structure is unchanged.

## Task 2: Optional geometric computation

**Files:** Create src/geometry.py, src/wire.py and examples/field-candidates.json; modify src/codec.py and src/__init__.py; create examples/field.lh.

Add a numeric tagged-array transport over the retained developer graph. Tables encode structural fields/enums only, not words. Default formatting rejects literal text; explicit developer parsing remains available. Handoff exports selected context into a separate readable sidecar and the numeric packet into a separate file. No ASCII/base64 word substitution or automatic secret dictionary is introduced.

Implement a weighted squared-exponential compatibility field normalized by total component weights. Scores are relative geometric compatibility, not truth/confidence/word identity. Widths may differ on either side of each axis. Candidate ranking returns all scores with caller-supplied minimum and margin thresholds, never a fabricated best-word decode. Add a codec score command using a declared node and a numerical candidate file. Demonstrate center, directional tails, distant candidates and preserved alternatives with synthetic data.

**Acceptance:** A single-component center scores 1; narrower sides decay faster; components and relation direction remain distinct; no candidate dictionary or network request is involved.

## Task 3: Receiver and contract closure

**Files:** prompt/BOOTSTRAP.md; SPEC.md; README.md; PROMPT.md; MIGRATION.md; examples/; calibration/probes.json; calibration/README.md; calibration/RESULTS.md; src/calibration.py; docs/PRIVACY.md.

Teach field-first broad interpretation and optional Python arithmetic, without prescribing hidden thought language. Show a numeric field before exact-word examples. Migrate active sample packet version markers; retain old experiment identities and mark them historical. The behavior recorder must distinguish optional geometric computation from task tools and must not treat a permitted decoder call as failure by itself. Synchronize documentation, exports and generated schema with the final contract.

**Acceptance:** Active samples parse; docs and schema describe the actual fields; Python is allowed consistently; empty evidence remains missing; no old model results become claims about the changed prompt.

## Implementation observations — 2026-09-05

- Forward 2.1 field contract and numeric wire are implemented; V2 exact graph relationships, conditions and task snapshots remain. The competing draft was removed rather than shipped as a second contract.
- Python decoding and field arithmetic are allowed. The current bootstrap defaults protocol replies to numeric packets unless prose is requested; no hidden-reasoning-language claim is made.
- Six active Python modules passed syntax inspection. The exported graph schema equals its owner, all anchor sets agree with the bootstrap, 16 corpus packets and 3 wire samples round-trip, and 12 numeric documentation examples parse. Current local documentation links resolve.
- Direct field observations establish center peak, different lower/upper falloff, preserved widths during shifts, preserved centers during narrowing, separated modes, and abstention for weak/tied candidates.
- Normal wire rejected synthetic plaintext. The handoff wrote a numeric packet plus a separate sidecar with only the required X02 binding and refused an existing output directory. The sidecar is readable disclosure, not encryption.
- A fresh evidence template records 0 passes, 0 failures and 16 missing observations. Both prompt and corpus identity are checked. No current receiving-model experiment or unit-test suite was run; prior V2 evidence remains historical.
- Details are recorded in `calibration/RESULTS.md`. No commit, push, reset, staging or dependency installation was performed by this implementation pass.
