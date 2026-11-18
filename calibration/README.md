# Lambda H/2.2 Receiver/Doer evidence

The corpus in `probes.json` contains 15 mixed native and packet-reply cases and sends only numeric packets. Human-readable expectations and `reply_mode` metadata (`"packet"` or `"native"`) stay in the evaluator file and are never included in receiver input.

```sh
python3 -m src.calibration --template
python3 -m src.calibration --receiver directional_field
python3 -m src.calibration private/receiver-results.json
```

Use a fresh session with the complete `prompt/DOER.md` and the emitted packet. Do not load the Encoder, expectations, another case's history, developer JSON, or an English paraphrase.

Every evidence record is bound to the protocol version, Doer prompt digest, semantic-basis digest, and corpus digest. Record model/run/grader identity where known, a unique session, exact response, trace, tool-call count, reviewer notes, and judgments for `meaning`, `direct_action`, `constraints`, and `output_contract`.

The corpus mixes `P.reply=packet` cases (`reply_mode: "packet"`, 11 cases), which require canonical numeric packet output, and omitted-`P.reply` cases (`reply_mode: "native"`, 4 cases: `missing_binding`, `native_workspace_inspect`, `selective_transform_framing`, `delegate_orchestration`), which expect normal host-native prose/artifact/tool output. Tool-assisted and tool-free cases must be reported separately. A valid packet, canonical echo, or empty template is not a behavior pass.

The evaluator cannot authenticate traces, identify a model independently, observe hidden reasoning, or automatically judge semantic correctness. Unrun/unknown observations remain null and report missing.

`RESULTS.md` records current evidence. Do not relabel observations from another prompt, basis, corpus, or protocol version.
