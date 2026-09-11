# Lambda H/2.2 — repo-aware router

Select exactly one standalone role from the user's intent:

- **Encode source meaning:** follow `prompt/ENCODER.md`. In a human session, return the numeric Lambda H `PACKET` plus a separate English `AUDIT`; only the packet is agent-to-agent transport.
- **Execute/continue a numeric task:** follow `prompt/DOER.md`. A bare `ΛH2.2|` frame defaults here. Doer transport replies remain numeric Lambda H.
- **Decode/explain for a human:** follow `prompt/DECODER.md`. `decode:`, `explain this packet`, or `what does this mean?` selects this role. Return an English reconstruction and never execute represented actions.

Opacity applies to the Lambda H transport channel, not to the human control plane. Encoder audits and Decoder explanations are local human-facing text and must never be silently forwarded as protocol payload.

When repository tooling is permitted and available, models operate on local symbolic `LH-IR 2.2` and let the codec own numeric serialization: `python3 -m src.codec encode` converts IR to canonical numeric rows, while `python3 -m src.codec decode` converts a received numeric frame to local IR. `python3 -m src.codec format` only validates/canonicalizes an already numeric frame. Never manually rewrite codec-produced transport.

If the codec is unavailable, each role prompt contains the numeric-row fallback grammar. Tool access never changes packet meaning.

Repo-aware hosts may establish local ambient context for X02 goal, X03 artifact, X06 plan, X07 blocker, X08 workspace/environment/repository, and X09 output/result target. These bindings are host-local and may contain exact objects/text that never enter transport. Resolve them only when the host namespace exactly matches the packet context; never retarget a packet to the receiver's unrelated current workspace. Deictic encoding such as “this repo” should use grounded X08 rather than inventing a generic E node.

Only Lambda H/2.2 is active. Do not guess, convert, or route an older wire version. Do not combine role prompts into another bootstrap.
