# encode_lang — ΛH/1 Hybrid Semantic Transfer

`encode_lang` is a self-contained prototype for transferring semantic structure between AI sessions using a **prompt-only shared basis** rather than a word-to-secret-token dictionary.

The core representation is:

```text
ΛH = E + R + A + T + K + P + X + V
```

- `E` entity/concept regions
- `R` directed relations
- `A` actions/intents
- `T` tools/instruments
- `K` epistemic state
- `P` execution/control policy
- `X` contextual references
- `V` residual semantic nuance

## Key files

- `prompt/LAMBDA_H_BOOTSTRAP.md` — complete end-to-end prompt for a fresh AI session
- `semantics/entity_basis.yaml` — `E00-E31`
- `semantics/relation_basis.yaml` — `R00-R15`
- `semantics/action_basis.yaml` — `A00-A15`
- `semantics/tool_basis.yaml` — `T00-T15`
- `semantics/epistemic.yaml` — proposition-level `K`
- `semantics/policy.yaml` — `P00-P11`
- `semantics/context_refs.yaml` — `X00-XFF`
- `semantics/residual_basis.yaml` — `V00-V07`
- `semantics/quantization.yaml` — shared `-7..+7 -> 0..E` encoding
- `examples/examples.md` — worked examples and interoperability checks
- `schema/lambda_h_packet.schema.json` — canonical JSON packet schema
- `src/validate_packet.py` — dependency-free packet validator
- `src/lambda_h.py` — dependency-free score/codec CLI for compact ↔ JSON packets
- `tests/test_validate_packet.py` — focused validator tests
- `PROJECT_NOTES.md` — rationale, contracts, and limitations
- `semantics.json` — earlier aggregate semantics snapshot retained for compatibility

## Quick start with any AI

1. Paste the entire contents of `prompt/LAMBDA_H_BOOTSTRAP.md` into a fresh session.
2. A compatible session should answer only:

```text
ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=01|BV=01
```

3. Try an entity:

```text
WORD: rat
```

4. Try a context-dependent word:

```text
WORD: fire
CONTEXT: Flames are spreading through dry vegetation.
```

5. Try compositional encoding:

```text
ENCODE: the dog sees the cat
```

The result should keep multiple entities and their directional relation separate rather than flattening the sentence into one vector.

## Canonical JSON packets

For machine interchange, use JSON conforming to `schema/lambda_h_packet.schema.json`.

Example:

```json
{
  "protocol": "ΛH/1",
  "basis": {"E":"01","A":"01"},
  "E": [{"handle":"η00","q":"77777777777777777777777777777777","u":1}],
  "A": [{"handle":"α00","q":"7777777777777777","u":1}],
  "X": ["X02"]
}
```

Validate it with:

```bash
python3 encode_lang/src/validate_packet.py packet.json
```

or via stdin:

```bash
cat packet.json | python3 encode_lang/src/validate_packet.py
```

The validator checks packet structure, vector widths/alphabet, handle syntax, and relation cross-references. It does **not** judge whether a semantic projection is correct.

## Local codec CLI

`src/lambda_h.py` turns numeric semantic coordinates into wire digits, decodes wire digits back to coordinates, and converts between canonical JSON and the compact chat form.

```bash
# Quantize a 16-axis action vector
python3 encode_lang/src/lambda_h.py score A 0 0 0 0 0 0 0 0 0 0 0 0 0 6 7 0

# Decode it back to signed scores
python3 encode_lang/src/lambda_h.py decode A 7777777777777DE7

# Compact wire -> canonical JSON
python3 encode_lang/src/lambda_h.py parse 'ΛH1|A=00.7777777777777DE7.2|X=02'

# Canonical JSON -> compact wire
python3 encode_lang/src/lambda_h.py compact packet.json
```

The CLI does not invent semantic scores from English. The AI performs the semantic projection against the prompt-defined basis; the CLI makes quantization, parsing, and transport deterministic.

## Design invariants

### Semantic geometry, not substitution

Never define `CAT = 91AF`. A concept is represented by compatibility with a shared semantic basis. Nearby concepts should generally produce nearby regions.

### Context defines sense

The same spelling can map to different regions under different contexts. Polysemy is expected and should preserve uncertainty when unresolved.

### Composition survives encoding

`R(subject, object)` and `R(object, subject)` are distinct unless the relation is explicitly symmetric.

### Opacity is not security

Opaque region codes are not encryption and do not grant authorization. Equivalent ordinary-language safety, privacy, access, and tool-use constraints remain fully applicable.

## Status

This is **ΛH/1 v1.0**, a prompt-only interoperability prototype. Basis versions are `01`; changing an anchor's order or meaning requires a new basis version.
