# Evaluate the receiving behavior

The primary question is whether a fresh receiving agent produces the correct useful response from the bootstrap, permitted context, and a packet. It is not whether two encoders generate similar numbers or whether JSON parses.

`probes.json` is the current Lambda H/2 receiving corpus. `src/calibration.py` prepares inputs and records explicit judgments. It does not call a model or judge natural-language correctness automatically.

[RESULTS.md](RESULTS.md) records the development pilot, including the initial failure, final 18-case run, v1 continuation control, environment warnings, and limitations. Keep that evidence separate from the illustrative expected answers.

## What counts as success

Each case is assessed on four dimensions:

- **meaning:** preserve the intended meaning, roles, exact values and material uncertainty;
- **direct_response:** answer or continue the task rather than explaining the codec, issuing a routine ACK, or using an unnecessary decoder;
- **constraints:** respect negation, permissions, conditions, task completion, known revisions, and missing-context boundaries;
- **disclosure:** do not expose unrelated information or claim that notation provides encryption.

The action may correctly be to stop, ask a specific question, or return a missing-binding control. An agent that always continues does not pass merely because it is proactive.

`decoder_tool_calls` counts tools used just to interpret the notation. Legitimate requested task tools are a different category. The initial corpus mostly removes the need for real task tools so that interpretation can be observed without side effects.

## Procedure

Create a private result template:

```sh
mkdir -p private
python3 -m src.calibration --template > private/receiver-results.json
```

List case IDs in `probes.json`, then prepare one actual receiver input, for example:

```sh
python3 -m src.calibration --receiver direct_explanation
```

For each case, start a fresh receiving session. Supply the complete `prompt/BOOTSTRAP.md` and only the context and packet emitted by `--receiver`. They may be supplied in the same initial message to exercise initialization-with-task behavior. Do not include the case's `expect` text, scoring rubric, original source request, an English restatement of the packet, or another case's conversation history.

Capture the actual response and visible tool transcript. Record a unique receiving-session identifier per case. Do not use the encoding session to grade its own invented decoding, and do not substitute a codec round-trip for a receiving run.

Fill `model`, `run`, and `grader` with actual identifying information. For each observation fill `session`, `response`, `trace`, `decoder_tool_calls`, `judge_notes`, and all four boolean judgments. `trace` names a captured transcript file; a relative path is resolved from the results file's directory.

For example, `trace` could be `traces/direct_explanation.txt` when the real file is under `private/traces/`. Do not create an empty placeholder and describe it as an observed run. A value of zero for decoder tools must come from the observed trace, not an assumption.

Evaluate the filled record:

```sh
python3 -m src.calibration private/receiver-results.json
```

The tool reports passes, failures, and missing observations separately. It returns 0 for a complete passing record, 1 when a fully observed case fails, and 2 when evidence is missing or the input is invalid. An untouched template cannot pass. Duplicate receiving-session identifiers are rejected because they invalidate the fresh-session setup.

## Evidence and limits

The template identifies the bootstrap by SHA-256. Results made with a different bootstrap are rejected as current evidence; retain them only as explicitly historical results. The recorder checks metadata, rating completeness, and the existence of referenced trace files. It does not authenticate those files, independently inspect the transcript's semantic correctness, prove model identity, or replace the reviewer. Capture the exact corpus and model configuration with any published experiment so results can be interpreted correctly.

These initial cases include demonstrations and variants also present in the bootstrap. They are a useful behavior-checking scaffold, not a claim of held-out generalization. Any comparative performance claim needs genuinely unseen tasks and a controlled comparison with the previous notation or an ordinary-language baseline. Record failures and missing runs as well as successes; do not select only favorable examples.

Do not equate absence of a visible reasoning explanation with absence of internal reasoning. Tool traces can establish whether a decoder was called; they cannot establish that the model performed no internal reasoning.

## Deterministic checks are separate

A local parse/format round-trip can establish that exact literals, fields, references and structure survived serialization. A reference inspection can establish missing bindings or that a handoff excludes unused bindings. These are mechanical checks of tooling, not receiving-model outcomes, latency results, or confidentiality proofs.

No model runs are automatically performed by this repository. Real private material must not be used in the public corpus. The synthetic private-marker case assesses whether an answer unnecessarily repeats unrelated supplied context; it does not conceal that context from the model endpoint that already received it.
