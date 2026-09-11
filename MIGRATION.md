# Clean migration to Lambda H/2.2

Lambda H/2.2 replaces the earlier active formats. The migration is a clean cut:

- `ΛH2.2|` shallow numeric rows are the only accepted runtime wire.
- `prompt/ENCODER.md`, `prompt/DOER.md`, and `prompt/DECODER.md` are the only role prompts.
- Runtime replies are numeric packets only.
- The old bootstrap, nested-array parser, compatibility conversion, natural reply mode, and readable context-sidecar workflow are removed.
- Older packets must be recreated from their actual source meaning and current context. Renaming a prefix is invalid because the structure and controls differ.

The 2.2 graph retains semantic fields and exact relations, actions, conditions, epistemics, policy, and task state. New abstention distinguishes valid-but-unusable meaning from malformed structure.

Use the active entrypoint:

```sh
python3 -m src.codec format packet.lh
```

The formatter accepts only 2.2 numeric rows. A successful result is canonical numeric output. Failure is a numeric control and exit 2.

Textual identities are not migrated into hidden numeric payloads. Replace them with semantic fields where exact identity is unnecessary, provision a local binding before use, or abstain. Text-producing tasks are outside the active runtime profile.

Historical repository material is not an active decoder or compatibility promise. Current evidence must use the final Doer prompt, semantic basis, corpus, and 2.2 packets.
