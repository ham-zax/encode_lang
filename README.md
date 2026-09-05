# encode_lang — Lambda H/2.1

**Semantic fields, directed task structure, and a numeric communication wire.**

A concept need not resolve to one word. Represent its center of emphasis, the falloff around it, and separate regions for distinct live meanings. Keep who acts on what, prerequisites, negation, permissions and progress exact.

This is a forward development of the V2 graph—not a rollback to V1. Python may unpack and score the representation. There is no compulsory English reconstruction between receiving a packet and using its meaning.

## Start here

Give the receiving agent the complete [`prompt/BOOTSTRAP.md`](prompt/BOOTSTRAP.md). Then send a bare packet. For example, with namespace 1 and X02 already bound to an unfinished goal:

```text
ΛH2.1|[[0,1],[4,[[[0,0],[1,[[14,7]]],[4,[5,2]]]]],[8,[[3,0],[4,0]]]]
```

The receiver should continue the unfinished work, not explain this notation. The last policy record explicitly requests a brief natural-language response. Protocol replies otherwise stay in numeric form unless the user or requested output asks for prose. A completed goal must not be restarted.

`ENCODE:` asks for a packet. `DECODE:` explicitly asks for a reconstruction. Loading the bootstrap with a task should address the task immediately, not spend a turn on READY.

## What changed

The default wire has **no readable object keys, ordinary words, literal text, or descriptive task names**. After `ΛH2.1|`, it contains arrays and finite numbers only. Fixed structural tags identify fields; they are not a word-to-code dictionary. The formatter rejects text instead of silently omitting it or hiding it as byte codes. Readable developer JSON is available deliberately for inspection, not as the normal wire.

Semantic fields add actual geometric behavior, beyond renaming metadata. A field can have multiple weighted centers and different lower/upper widths on each axis. Focus can be moved, narrowed or broadened without collapsing separate meanings. A single component peaks at its center and fades with distance. Thresholds determine acceptance; they do not create lexical identity or evidence.

The V2 direction, action/tool binding, conditions, exact policy limits and task snapshots remain. A broader action field never softens a read-only constraint. An unknown stop condition is not permission to continue. Progress and revisions are still supplied state, not a durable execution ledger.

## Python is allowed

From the repository root, using Python 3.10 or later and only the standard library:

```sh
# Readable developer inspection, explicitly requested.
python3 -m src.codec parse examples/field.lh

# Normal wire output; rejects plaintext payloads and descriptive namespaces.
python3 -m src.codec format examples/field.lh

# Score explicit numeric candidates; thresholds are caller policy.
python3 -m src.codec score examples/field.lh --node e0 \
  --candidates examples/field-candidates.json --minimum 0.2 --margin 0.05

# Narrow one direction; output remains a numeric packet.
python3 -m src.codec focus examples/field.lh --node e0 --scale 0.5 --axis E20

# Move the center without changing the widths.
python3 -m src.codec focus examples/field.lh --node e0 --shift E20=-1

python3 -m src.codec inspect examples/continue.lh --context examples/context.demo.json
```

Point `q` remains available when no width is asserted. Field `f` carries one or more components with `q` center, `s` default width, optional `b` lower/upper bands, and optional `w` relative peak weight. Scoring requires explicit `f`; it does not invent a width for a point.

Public helpers include `make_field`, `activation`, `focus_field`, `shift_field`, and `rank_candidates`, alongside the existing graph/codec helpers. Candidate ranking reports every supplied score and abstains on weak or tied matches. There is no built-in lexicon, network lookup, automatic task execution, or model API call.

## Exact context without plaintext in the wire

An exact filename, quotation or name belongs in a genuinely shared X binding, not a guessed geometric neighborhood. Numeric context IDs identify an agreed namespace; they are not passwords or authenticated identities. An unknown binding produces a need control rather than a fabricated identity.

For a fresh receiver, explicitly export a selected context sidecar alongside the numeric packet:

```sh
# Creates a NEW directory; parent must already exist. Never overwrites it.
python3 -m src.codec handoff examples/continue.lh \
  --context examples/context.demo.json --output /tmp/encode-lang-handoff-demo
```

The result contains `packet.lh` and `context.private.json`. Only referenced bindings enter the sidecar. **The sidecar is readable disclosure**; inspect it and transfer it only to the intended endpoint. The numeric packet alone is not self-contained when it needs that context. The Python `make_handoff` API still returns an explicit developer bundle with selected bindings; do not mistake that bundle for an opaque packet.

Numeric notation is casual opacity, not confidentiality; anyone with the public bootstrap can interpret it. Use established encryption for transit/storage and a trusted endpoint for sensitive processing. See [`docs/PRIVACY.md`](docs/PRIVACY.md).

## Evidence, not claims about hidden thought

[`calibration/probes.json`](calibration/probes.json) contains current receiver cases; the evaluator binds results to both the bootstrap and the corpus. Optional Python calls are recorded, not automatically marked as failure. Explicit no-tool constraints still apply.

```sh
python3 -m src.calibration --template
python3 -m src.calibration --receiver directional_field
python3 -m src.calibration private/receiver-results.json
```

The current geometry and transport checks are documented in [`calibration/RESULTS.md`](calibration/RESULTS.md). Prior V2 receiving results are historical and do not establish 2.1 performance. No hidden-reasoning-language, token-saving, latency or cross-model superiority claim follows from a successful codec check.

## Project map

| Path | Role |
| --- | --- |
| `prompt/BOOTSTRAP.md` | Standalone field/graph reader and complete numeric grammar |
| `src/protocol.py` | Developer graph schema and exact reference/task invariants |
| `src/wire.py` | Numeric structural tags, strict encode/decode, plaintext rejection |
| `src/geometry.py` | Directional field activation, focus, shift and explicit-candidate ranking |
| `src/codec.py` | CLI and separate context-sidecar export |
| `semantics/basis.json` | Shared semantic directions, not a word dictionary |
| `schema/lambda_h_packet.schema.json` | Generated developer-graph schema; decode the wire first |
| `examples/` | Numeric packets and synthetic local context/candidate data |
| `calibration/` | Version-bound receiving corpus and evidence records |
| `docs/FIELD_MODEL.md` | Field interpretation and mathematical limits |
| `MIGRATION.md` | Forward migration and the text-disclosure boundary |
| `archive/v1/`, `archive/v2/` | Historical definitions and evidence, not active fallback decoders |

The geometry is a specified communication model, not access to an LLM's internal embeddings. A correct next action and preserved meaning are the objective; avoiding a provider refusal is not an evaluation criterion.
