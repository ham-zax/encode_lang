# Clean migration to Lambda H/2.2

Lambda H/2.2 replaces the earlier active formats. The migration is a clean cut:

- `ΛH2.2|` shallow numeric rows are the only accepted agent-to-agent runtime wire.
- `LH-IR 2.2` is a local model-facing structural form; it is never transport.
- `prompt/ENCODER.md`, `prompt/DOER.md`, and `prompt/DECODER.md` are the only role prompts.
- Doer transport replies are numeric packets only. Encoder audits and Decoder explanations are human-facing text outside the wire.
- The old bootstrap, nested-array parser, compatibility conversion, natural reply mode, and readable context-sidecar workflow are removed.
- Older packets must be recreated from their actual source meaning and current context. Renaming a prefix is invalid because the structure and controls differ.

The 2.2 graph retains semantic fields and exact relations, actions, conditions, epistemics, policy, and task state. New abstention distinguishes valid-but-unusable meaning from malformed structure.

Use the active codec boundary:

```sh
python3 -m src.codec encode local.ir
python3 -m src.codec decode packet.lh
python3 -m src.codec format packet.lh
```

`encode` maps local symbolic IR to canonical 2.2 numeric rows. `decode` maps numeric rows to local symbolic IR for Doer/Decoder interpretation. `format` accepts only numeric rows and canonicalizes them. Numeric-output failures (`encode`/`format`) return a numeric control and exit 2; local `decode` reports conversion errors on stderr.

Textual identities are not migrated into hidden numeric payloads. Where exact identity is unnecessary, use semantic fields. For deictic current objects, repo-aware hosts may provision ambient-capable local bindings: X02 goal, X03 artifact, X06 plan, X07 blocker, X08 workspace/environment/repository, and X09 output/result target. These values remain outside transport and resolve only under an exact context-namespace match; otherwise the packet uses normal `need` behavior. Do not turn “this repo” into a generic E node merely to avoid missing context. Text-producing remote tasks remain outside the active runtime profile.

Historical repository material is not an active decoder or compatibility promise. Current evidence must use the final Doer prompt, semantic basis, corpus, and 2.2 packets.
