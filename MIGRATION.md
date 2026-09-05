# Forward migration to Lambda H/2.1

This change preserves V2's exact graph and adds semantic fields plus a numeric communication boundary. It does not restore V1 or rewrite Git history. The V2 baseline is commit `38b12de`; its bootstrap, corpus, pilot report and selected documentation are preserved under `archive/v2/`. V1 remains under `archive/v1/`.

## The three representations are distinct

**Developer graph:** ordinary JSON with `protocol: ΛH/2.1`, readable field names and optional exact data. It is a deliberate diagnostic/integration view. `src.protocol.schema()` describes this representation.

**Normal wire:** `ΛH2.1|` followed by numeric tagged arrays. It has no ordinary words, descriptive field labels, raw strings or textual bindings. `format_packet` and `src.codec format` produce it. A graph that validates structurally may still be non-exportable because it contains text or descriptive namespace names.

**Context sidecar:** explicitly supplied exact data, outside the numeric wire. Its text is disclosed to the receiving endpoint. A reference is useful only when the intended receiver genuinely has its binding.

Do not print developer JSON as if it were the new opaque communication format. Do not relabel an old V2 JSON wire object as 2.1; the numeric transport has a different grammar.

## Preserve graph meaning

Point q remains supported. Add f only when the concept needs breadth, directional falloff or several live regions. A node cannot carry both q and f. A component has a q center and a positive s width; optional b gives per-axis lower/upper widths, and optional w sets relative peak emphasis. Widths are a deliberate modeling choice, not something recovered from old confidence values.

Preserve each action's target/tool, ordered relation arguments, conditions, negation, permissions, and actual task state. Do not average separate meanings. No action or completion evidence is inferred merely by converting the transport.

Textual node values cannot be exported on the normal wire. When exact text is necessary, use a genuinely shared X reference and provide its selected sidecar deliberately. When only broad meaning matters, retain the numerical semantic representation rather than copying its English name. Do not delete a necessary literal merely to make formatting succeed.

Context and task IDs must be canonical nonnegative decimal strings for numeric export, and local node IDs must have canonical decimal suffixes. Renaming an established namespace requires coordinated bindings/state, not an automatic string substitution. Examples use small numeric namespaces only for fictional demonstrations; they do not establish global identities.

## Current entry points

```sh
python3 -m src.codec parse examples/field.lh
python3 -m src.codec format examples/field.lh
python3 -m src.codec score examples/field.lh --node e0 \
  --candidates examples/field-candidates.json --minimum 0.2 --margin 0.05
python3 -m src.codec focus examples/field.lh --node e0 --scale 0.5 --axis E20
python3 -m src.codec inspect examples/continue.lh --context examples/context.demo.json
python3 -m src.codec handoff examples/continue.lh \
  --context examples/context.demo.json --output /tmp/encode-lang-handoff-demo
```

The handoff CLI now requires a new output directory and writes separate packet and context files; it no longer prints an inline plaintext-bearing handoff as a communication packet. The Python `make_handoff` helper remains a readable developer-level operation for integrations. Its output may contain text and must not be mistaken for numeric wire.

Invalid controls now use numeric `code` rather than a free-form `reason`: 0 shape, 1 local reference, 2 context conflict, 3 inconsistent state. The CLI can still report readable errors to its explicit caller; those diagnostics are not protocol payloads.

Old wire versions are rejected with a migration diagnostic. Retain the matching historical decoder when historical interpretation is necessary, or re-encode using actual source context. The runtime does not silently guess a cross-version conversion.

## Python and evidence

Decoder and geometry tools are permitted. A tool call alone is no longer a failed receiving case; exact no-tool restrictions still take precedence. Direct task response matters, not whether the receiver used arithmetic internally.

Current evidence records identify both bootstrap and corpus. The earlier V2 pilot remains historical; a new protocol marker does not upgrade those observations into 2.1 results. No hidden-reasoning-language, confidentiality, latency or model-reliability guarantee is implied.
