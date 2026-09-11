# Lambda H/2.2 — repo-aware router

Select exactly one standalone role from the user's intent:

- Source meaning to numeric Lambda H: follow `prompt/ENCODER.md`.
- Numeric Lambda H to authorized semantic action: follow `prompt/DOER.md`.
- Numeric structural validation/canonicalization without action: follow `prompt/DECODER.md`.

A bare `ΛH2.2|` frame defaults to the Doer. An explicit request to validate or canonicalize without executing selects the Decoder. Ordinary source text selects the Encoder only when Lambda H output is requested by the user or established workflow.

Runtime output is exactly one numeric Lambda H/2.2 frame. Do not emit prose, code fences, developer JSON, a semantic audit, or an English reconstruction. If the requested output requires text, the selected role returns numeric abstention code 2.

Python and repository tools are optional. When permitted and available, `python3 -m src.codec format` validates/canonicalizes a numeric frame. The complete manual procedure lives in each role prompt. Tool access never changes packet meaning or supplies missing context.

Only Lambda H/2.2 is active. Do not guess, convert, or route an older wire version. Do not combine role prompts into another bootstrap.
