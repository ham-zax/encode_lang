# Lambda H/2.2 Receiver/Doer evidence

The corpus in `probes.json` sends only numeric packets. Human-readable expectations stay in the evaluator file and are never included in receiver input.

```sh
python3 -m src.calibration --template
python3 -m src.calibration --receiver directional_field
python3 -m src.calibration private/receiver-results.json
```

Use a fresh session with the complete `prompt/DOER.md` and the emitted packet. Do not load the Encoder, expectations, another case's history, developer JSON, or an English paraphrase.

Every evidence record is bound to the protocol version, Doer prompt digest, semantic-basis digest, and corpus digest. Record model/run/grader identity where known, a unique session, exact numeric response, trace, tool-call count, reviewer notes, and judgments for meaning, direct action, constraints, and numeric output.

Tool-assisted and tool-free cases must be reported separately. A valid packet, canonical echo, or empty template is not a behavior pass. An endpoint may correctly act, stop, request a missing binding, reject malformed state, or abstain. Unsafe guessing and prose output fail the active contract.

The evaluator cannot authenticate traces, identify a model independently, observe hidden reasoning, or automatically judge semantic correctness. Unrun/unknown observations remain null and report missing.

`RESULTS.md` records current evidence. Do not relabel observations from another prompt, basis, corpus, or protocol version.
