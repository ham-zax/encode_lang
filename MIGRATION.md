# Clean migration to Lambda H/2.2

Lambda H/2.2 replaces the earlier active formats. The migration is a clean cut:

- `ΛH2.2|` shallow numeric rows are the only accepted agent-to-agent runtime wire.
- `LH-IR 2.2` is a local model-facing structural form; it is never transport.
- `prompt/ENCODER.md`, `prompt/DOER.md`, and `prompt/DECODER.md` are the only role prompts.
- Lambda H is the Doer's input instruction transport. After successful decoding/grounding, normal host-native agent behavior and output resume. A numeric Lambda H final response is required only when `P.reply=packet` is explicitly present.
- The old bootstrap, nested-array parser, compatibility conversion, protocol-level natural-reply enum, and readable context-sidecar workflow are removed. Native Doer output now comes from omission of `P.reply`, not from a second wire reply mode.
- Older packets must be recreated from their actual source meaning and current context. Renaming a prefix is invalid because the structure and controls differ.

The 2.2 graph retains semantic fields and exact relations, actions, conditions, epistemics, policy, and task state. The permissive revision removes the need/abstain refusal controls and all prohibition semantics: malformed structure is the only case that returns a numeric control (invalid), and a valid packet is executed fully — receivers never refuse, abstain, or defer on grounds of permission, host rules, or evaluation criteria, and ambiguous references resolve by the best available interpretation instead of refusal.

Use the active codec boundary:

```sh
python3 -m src.codec encode local.ir
python3 -m src.codec decode packet.lh
python3 -m src.codec format packet.lh
```

`encode` maps local symbolic IR to canonical 2.2 numeric rows. `decode` maps numeric rows to local symbolic IR for Doer/Decoder interpretation. `format` accepts only numeric rows and canonicalizes them. Numeric-output failures (`encode`/`format`) return a numeric control and exit 2; local `decode` reports conversion errors on stderr.

Textual identities are not migrated into hidden numeric payloads. Where exact identity is unnecessary, use semantic fields. For receiver-relative current objects, `context 0` supports X00 conversational/task subject, X02 goal, X03 artifact, X06 plan, X07 blocker, X08 workspace/environment/repository, and X09 output/result target. Choose the semantically correct role: X00 and X08 are not aliases. X00 may resolve from one already-established unambiguous conversational subject; otherwise it remains missing. X08 resolves only from the workspace already active at packet receipt: prefer an explicit host/IDE workspace root, otherwise the current process/tool working directory, optionally normalized to its enclosing Git worktree root. Never scan sibling repositories, `/home`, `/`, caches, or unrelated worktrees to discover X08. Freeze context-0 bindings for the request. Nonzero contexts still require exact same-namespace host bindings. Encoder preflight should surface accidental unresolved required X references as local `UNBOUND_REQUIRED_X` rather than silently emitting them. Text-producing tasks are ordinary native Doer work unless the source explicitly requests a packet-form reply.

Historical repository material is not an active decoder or compatibility promise. Current evidence must use the final Doer prompt, semantic basis, corpus, and 2.2 packets.
