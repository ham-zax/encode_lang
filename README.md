# encode_lang — ΛH/1 Hybrid Semantic Transfer

`encode_lang` is a semantic-language project built around ΛH/1. The project owns conversion between ordinary text and ΛH/1 packets. `prompt/LAMBDA_H_BOOTSTRAP.md` has a narrower role: paste it into any AI session so that session can understand bare ΛH/1 packets as semantic conversation input.

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

- `prompt/LAMBDA_H_BOOTSTRAP.md` — receiver bootstrap that teaches an AI session the normative semantic bases and compact/control grammar
- `PROMPT.md` — compatibility redirect only; contains no protocol definition
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
- `src/__init__.py` — reusable package exports
- `src/validate_packet.py` — dependency-free packet/control-frame validator
- `src/lambda_h.py` — dependency-free score/codec CLI for compact ↔ JSON packets and region comparison
- `src/calibrate.py` — one-session and two-session qualitative calibration evaluator
- `calibration/probes.json` — cross-model semantic calibration prompts and qualitative checks
- `calibration/README.md` — repeatable project-side semantic-geometry calibration procedure
- `tests/test_validate_packet.py` — focused validator tests
- `tests/test_lambda_h.py` — compact/K/control/round-trip regression tests
- `tests/test_calibrate.py` — cross-model calibration regression test
- `PROJECT_NOTES.md` — rationale, contracts, and limitations
- `semantics.json` — earlier aggregate semantics snapshot retained for compatibility

## Quick start with any AI

1. Paste the entire contents of `prompt/LAMBDA_H_BOOTSTRAP.md` into a fresh AI session.
2. A compatible receiver should answer only:

```text
ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01
```

3. Use the project-side semantic encoder to produce a ΛH/1 packet from the word, phrase, or sentence you want to send.
4. Send the resulting packet to the AI **as-is**. Do not prefix it with `DECODE:` and do not restate the English source text.
5. The AI should reconstruct the packet's semantic state internally and respond to the represented meaning.

The receiver bootstrap is intentionally not an encoder UI. It does not expose `WORD:`, `ENCODE:`, `DECODE:`, `ACTION:`, `TOOL:`, or similar natural-language commands.

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
python3 -m src.validate_packet packet.json
```

or via stdin:

```bash
cat packet.json | python3 -m src.validate_packet
```

The validator checks packet structure, vector widths/alphabet, handle syntax, and relation cross-references. It does **not** judge whether a semantic projection is correct.

## Local codec CLI

`src/lambda_h.py` turns numeric semantic coordinates into wire digits, decodes wire digits back to coordinates, and converts between canonical JSON and the compact chat form.

```bash
# Quantize a 16-axis action vector
python3 -m src.lambda_h score A 0 0 0 0 0 0 0 0 0 0 0 0 0 6 7 0

# Decode it back to signed scores
python3 -m src.lambda_h decode A 7777777777777DE7

# Compare two same-layer regions across sessions/models
python3 -m src.lambda_h compare E "$Q1" "$Q2"

# Compact wire -> canonical JSON
python3 -m src.lambda_h parse 'ΛH1|A=00.7777777777777DE7.2|X=02'

# Canonical JSON -> compact wire
python3 -m src.lambda_h compact packet.json
```

The current CLI provides deterministic quantization, parsing, transport, JSON/compact conversion, and region-distance measurement. Natural-language semantic projection belongs on the project side; it is not delegated to the receiver bootstrap.

## Cross-model calibration

Use `calibration/probes.json` against the project-side semantic projector and follow `calibration/README.md`. Geometry is evaluated by relative semantic neighborhoods, not exact hexadecimal equality. The calibration set checks neighborhood ordering and context-sensitive sense separation without introducing a word-to-token dictionary.

Generate a fill-in result file and evaluate it with:

```bash
python3 -m src.calibrate --template > calibration-results-a.json
# Fill the returned q regions from one project-side projector run, then run local checks:
python3 -m src.calibrate calibration-results-a.json

# For empirical cross-model checks, fill a second result file and compare both:
python3 -m src.calibrate calibration-results-a.json calibration-results-b.json
```

## Normative compact control frames

The canonical bootstrap and codec share these exact control forms:

```text
ΛH1|SYNC?
ΛH1|SYNC|E=00.<32q>.<u>
ΛH1|ACK|E=00,01|R=00(01,00)|A=00|T=00
ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01
ΛH1|CALFAIL
```

The compact data grammar is defined in `prompt/LAMBDA_H_BOOTSTRAP.md` and `SPEC.md`; the Python codec parses and emits the same grammar.

The Python implementation is also importable as a package:

```python
from src import parse_compact, format_compact, compare_q, validate_packet
```

## Design invariants

### Semantic geometry, not substitution

Never define `CAT = 91AF`. A concept is represented by compatibility with a shared semantic basis. Nearby concepts should generally produce nearby regions.

### Context defines sense

The same spelling can map to different regions under different contexts. Polysemy is expected and should preserve uncertainty when unresolved.

### Composition survives encoding

`R(subject, object)` and `R(object, subject)` are distinct unless the relation is explicitly symmetric.

## Status

This is **ΛH/1 v1.0**, a semantic-interchange prototype with a receiver bootstrap for AI understanding. Basis versions are `01` for E/R/A/T/V and `02` for policy; changing an anchor's order or meaning requires a new basis version.
