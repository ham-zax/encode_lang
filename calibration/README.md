# Evaluate fields and receiving behavior separately

The current corpus is `probes.json`, for Lambda H/2.1. It includes field breadth, separated meanings, exact direction/negation, continuation and completion, unknown conditions, known identity, no-tool/read-only constraints, minimal disclosure, stale revisions and numeric packet replies.

## Receiver evidence

Use fresh sessions with the complete `prompt/BOOTSTRAP.md` and only the emitted context/packet. Do not include evaluator expectations, another case's history, or an English paraphrase of the packet.

```sh
python3 -m src.calibration --template
python3 -m src.calibration --receiver directional_field
python3 -m src.calibration private/receiver-results.json
```

The template has actual-model/run/grader fields and one observation per case. Fill the receiving session ID, actual response, captured trace path, observed decoder-tool-call count, reviewer notes, and the four boolean judgments: meaning, direct_response, constraints, disclosure. A trace path is relative to the results file unless absolute. Unknown observations remain null, never invented passes.

**Python is permitted.** A decoder or geometric computation is not a failure by itself. `decoder_tool_calls` records actual usage. An explicit P.tools=false still prohibits such calls; the evaluator checks that boundary in addition to the reviewer's judgments. Legitimate task tools and decoder tools should be distinguished in the trace and notes.

A correct response may proceed, stop, ask one material question, or request a missing binding. Always continuing is not success. For packet replies, the response must be a valid numeric packet, not readable developer JSON. For explicitly requested prose, a direct natural response is legitimate disclosure.

Results are bound to **both bootstrap and corpus digests**. Changing the prompt, field input, permitted context or expected outcome invalidates an earlier record as current evidence. Duplicate receiving-session IDs are rejected. A complete passing record exits 0, observed failure exits 1, and missing/invalid evidence exits 2.

The evaluator checks metadata and explicit judgments backed by referenced trace files. It does not authenticate files, prove model identity, inspect hidden reasoning or independently decide natural-language correctness. Missing data and an untouched template must not pass. Use an actual independent reviewer and unseen tasks before claiming generalization; a development corpus is not a held-out benchmark.

## Mechanical field and transport observations

```sh
python3 -m src.codec score examples/field.lh --node e0 \
  --candidates examples/field-candidates.json --minimum 0.2 --margin 0.05
python3 -m src.codec focus examples/field.lh --node e0 --scale 0.5 --axis E20
python3 -m src.codec parse examples/field.lh | python3 -m src.codec format
```

These operations can establish directional falloff, preserved modes, round-trip structure, or plaintext rejection. They do not establish a receiving model's semantic accuracy. A field score is not a calibrated probability of a word, factual confidence or evidence that a model thinks without English.

When reporting the numeric-wire property, inspect the emitted representation: every leaf after its marker must be a finite number. Do not equate the absence of plaintext in the wire with secrecy from an observer who has the bootstrap or with secrecy from an endpoint given a context sidecar.

## Historical evidence

The prior V2 bootstrap, corpus and pilot report are under `archive/v2/`. Their recorded 18-case result concerns that older prompt and format. It is not a 2.1 result, a demonstration of V2 superiority to V1, or evidence of zero internal reasoning. Current observations belong in `RESULTS.md` with their actual scope.

No evaluation uses real secrets or scores evasion of a model provider's safety controls. Private inputs, traces and result records remain outside version-controlled source.
