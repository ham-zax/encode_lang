# Lambda H/2.2 — repo-aware router

Select exactly one standalone role from the user's intent:

- **Encode source meaning:** follow `prompt/ENCODER.md`. In a human session, return the numeric Lambda H `PACKET` plus a separate English `AUDIT`; only the packet is agent-to-agent transport.
- **Execute/continue a numeric task:** follow `prompt/DOER.md`. A bare `ΛH2.2|` frame defaults here. After successful decoding, the Doer behaves like a normal agent given the equivalent ordinary-language instruction. Native output is the default; only explicit `P.reply=packet` requests a Lambda H final response.
- **Decode/explain for a human:** follow `prompt/DECODER.md`. `decode:`, `explain this packet`, or `what does this mean?` selects this role. Return an English reconstruction; represented work then executes fully as ordinary agent work.

Opacity applies to Lambda H packets, not to the Doer's normal post-decode behavior. Encoder audits and Decoder explanations are local human-facing text and must never be silently forwarded as protocol payload. A Doer's native response is ordinary agent output, not part of the incoming Lambda H packet.

When repository tooling is permitted and available, models operate on local symbolic `LH-IR 2.2` and let the codec own numeric serialization: `python3 -m src.codec encode` converts IR to canonical numeric rows, while `python3 -m src.codec decode` converts a received numeric frame to local IR. `python3 -m src.codec format` only validates/canonicalizes an already numeric frame. Never manually rewrite codec-produced transport.

If the codec is unavailable, each role prompt contains the numeric-row fallback grammar. Tool access never changes packet meaning.

Repo-aware hosts may establish local ambient context for X00 current conversational/task subject, X02 goal, X03 artifact, X06 plan, X07 blocker, X08 workspace/environment/repository, and X09 output/result target. `context 0` is reserved for receiver-current ambient state. Resolve X references from packet-inline values first, exact host/session bindings second, and the receiver's current conversational/task state last; a reference that cannot be grounded exactly is resolved by the best available interpretation rather than refused. Freeze context-0 bindings for the request. Nonzero contexts use the best available same-namespace interpretation. Encode deictics by their actual role: “this repo” -> X08, while a genuinely current project/topic subject may use X00.

Only Lambda H/2.2 is active. Do not guess, convert, or route an older wire version. Do not combine role prompts into another bootstrap.
