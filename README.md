# encode_lang — Lambda H/2

**A prompt-native notation for communicating meaning, constraints, and unfinished work.**

Give an AI session the standalone bootstrap, then send a packet. The intended response is the useful answer or next permitted action—not a translation of the packet or a Python decoding exercise.

Lambda H/2 uses sparse semantic anchors for approximate meaning and exact fields for identities, action targets, tools, conditions, permissions, and task state. It is a communication prototype, not a claim that arbitrary codes become a model's internal language.

**Encoding is not encryption.** Keep sensitive inference local when a model provider must not receive it. Use established encryption for transport/storage and disclose only necessary context. The [privacy guide](docs/PRIVACY.md) explains the trust boundaries and a separate local age workflow.

## Start with a conversation

Paste the whole of [`prompt/BOOTSTRAP.md`](prompt/BOOTSTRAP.md) into the receiving session. It contains the complete notation, anchor definitions, and worked receiving examples; the receiver needs neither Python nor repository access.

Then send this packet as-is:

```text
ΛH2|{"E":[{"id":"e0","value":"a bicycle bell"}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}],"P":{"detail":"brief","tools":false}}
```

The requested behavior is a brief explanation of a bicycle bell, directly. No `DECODE:` wrapper is necessary.

`ENCODE: <message>` asks the bootstrapped agent to produce a packet. `DECODE: <packet>` explicitly asks for a reconstruction rather than execution. Ordinary language remains ordinary conversation. A bootstrap supplied together with a task should address the task immediately; a readiness-only response is for initialization without a task.

## What v2 changes

Dense offset-hex coordinates are retired. An action now names the important axes—such as `{"A13":6,"A14":7}`—instead of making the reader count positions. The wire is a single JSON object prefixed by `ΛH2|`; machine JSON uses `"protocol":"ΛH/2"` instead.

Actions bind their own targets and instruments. Dependencies, conditions, and negation are explicit. Exact values preserve names, quantities, paths, and versions when a coarse semantic neighborhood is insufficient. `choices` preserves unresolved alternatives rather than silently guessing.

Task snapshots identify the goal, ordered steps, completed work, next unfinished action, stop condition, state, and revision. Scoped X references distinguish an established session from a fresh receiver that needs bindings. Exact policy limits are not hidden in approximate vectors.

None of this grants permission, authenticates a sender, proves a result, or creates an autonomous background worker. The receiving agent must preserve the actual task's authority and evidence boundaries.

## Continue without restarting

When `X02` is already bound to an unfinished goal in `lesson-1`, this can request continuation:

```text
ΛH2|{"context":"lesson-1","A":[{"id":"a0","q":{"A14":7},"target":"X02"}]}
```

The receiver should use the actual known state. It should resume unfinished work, stop if the goal is complete, or request the missing binding in a fresh context. A stronger continuation signal is not a substitute for a goal or a completion record.

For cross-session work, use an explicit task snapshot and a selective handoff. The [bootstrap](prompt/BOOTSTRAP.md), [specification](SPEC.md), and [worked examples](examples/examples.md) cover completion, blocked conditions, ambiguity, relation direction, exact literals, and multiple actions.

## Optional local tooling

The Python tools are for authors and integrations, not a dependency of the receiving prompt. Run from the repository root with Python 3.10 or later; no third-party package is required.

```sh
python3 -m src.codec parse examples/continue.lh
python3 -m src.codec parse examples/continue.lh | python3 -m src.codec format
python3 -m src.codec inspect examples/continue.lh --context examples/context.demo.json
python3 -m src.codec handoff examples/continue.lh --context examples/context.demo.json
python3 -m src.codec schema
```

The shipped demo files contain fictional data; replace their paths with your own reviewed inputs for real use. Input defaults to stdin. These commands convert representations, check structure, inspect references and declared task state, or prepare a handoff. They do not infer natural-language meaning, run actions, contact a model, encrypt data, or save a durable execution ledger.

The handoff includes only referenced X bindings. This excludes unrelated context, but **every included binding is still plaintext disclosure**. Review the output before sending it.

Package exports:

```python
from src import (
    ProtocolError, parse_packet, format_packet, validate_packet,
    inspect_packet, make_handoff, schema,
)
```

## Evaluate receiving behavior—not just valid JSON

The [calibration corpus](calibration/probes.json) contains receiving tasks with evaluator-only expectations. The recorder distinguishes missing evidence from a pass and tracks meaning, direct response, constraints, disclosure, and decoder-tool calls.

```sh
python3 -m src.calibration --template
python3 -m src.calibration --receiver CASE_ID
python3 -m src.calibration private/receiver-results.json
```

Use a real case ID from the corpus. Run cases in fresh receiving sessions with the bootstrap and permitted context only; do not leak the expected answer to the receiver. Capture the actual response and tool trace, then record explicit reviewer judgments. See the [calibration procedure](calibration/README.md).

A [recorded development pilot](calibration/RESULTS.md) met 18 of 18 shipped case expectations with no decoder-tool calls after one prompt correction; the initial 17-of-18 run is also retained. The original v1 prompt passed a matched simple-continuation control, so this is not evidence of universal v2 superiority. The pilot uses one CLI runtime and implementation-session grading, not an independent or held-out cross-model benchmark.

Mechanical codec checks are not cross-model evidence. There is no claimed speedup, token saving, cryptographic confidentiality, or absence of internal reasoning merely because the new format parses. One final pilot case reported nonzero reasoning-token usage.

## Project map

| Path | Responsibility |
| --- | --- |
| `prompt/BOOTSTRAP.md` | Standalone agent-facing instruction and demonstrations |
| `SPEC.md` | Current protocol and behavioral contract |
| `semantics/basis.json` | Shared semantic anchor meanings |
| `src/protocol.py` | Schema, graph validation, reference and handoff inspection |
| `src/codec.py` | Strict JSON/wire conversion and optional CLI |
| `schema/lambda_h_packet.schema.json` | Generated structural schema |
| `src/calibration.py` | Evidence-recording behavioral evaluator |
| `calibration/`, `examples/` | Receiving corpus, procedure, and demonstrations |
| `docs/PRIVACY.md` | Minimization, trusted endpoints, and external encryption |
| `MIGRATION.md` | Breaking changes and contextual v1 re-encoding |
| `archive/v1/` | Preserved historical prototype, not an active fallback |

## Migration and limits

V1 packets are rejected by the current codec with a migration diagnostic. Re-encode using source context and the actual task state; missing targets, permissions, or completion evidence cannot be reconstructed reliably from old vectors alone. Historical files and tests are preserved in the archive rather than presented as v2 functionality.

Prompt portability and direct response are design targets that require empirical evaluation with the intended receiving models. Precise data requires explicit representation. Genuine privacy requires control over disclosure, transport, storage, and the processing endpoint—not a secret-looking alphabet.
