> **Compatibility note:** the canonical maintained file is [`examples/examples.md`](./examples/examples.md). This root-level file is retained for earlier links.

# ΛH/1 Examples

These examples demonstrate structure and interoperability expectations. Numeric regions shown here are illustrative unless explicitly noted as captured from a model run.

## 1. Single entity region

A prior model run encoded `rat` as:

```text
ΛE1|b=01|q=D5E4C387777453674974479543387479|u=1
```

Decoding the 32 coordinates places the strongest positive affinity around living/non-human-animal/biological anchors. The string does not contain a direct word token for `rat`.

## 2. Semantic proximity test

Using the project-side semantic encoder, encode these source concepts separately:

```text
cat
dog
rat
hat
```

Expected qualitative geometry:

```text
sim(cat,dog)  high
sim(cat,rat)  high-ish
sim(cat,hat)  substantially lower
```

Do not require exact matching hex across sessions.

## 3. Polysemy test

Encode separately with the project-side encoder:

```text
fire — Flames are spreading through dry vegetation.
```

and:

```text
fire — The company terminated the employee's position.
```

The first should emphasize energetic-phenomenon/process/environment/hazard regions. The second should shift toward social actor, institution/normative structure, intentional action, relation, and state-transition regions.

## 4. Three distinct entity regions

Three captured/illustrative entity regions can remain distinct in one packet:

```text
ΛE1|b=01|q=77777839777BA87877777B7DA7B77C97|u=1
ΛE1|b=01|q=7777797777BB987777777CDAD8777C9E|u=2
ΛE1|b=01|q=77777B777777777777777777A777777D|u=2
```

Bind them separately:

```text
η00 := ΛE1|b=01|q=77777839777BA87877777B7DA7B77C97|u=1
η01 := ΛE1|b=01|q=7777797777BB987777777CDAD8777C9E|u=2
η02 := ΛE1|b=01|q=77777B777777777777777777A777777D|u=2
```

Do not average the three regions.

## 5. Add relations

With relation regions established as:

```text
ρ00 := ΛR1|b=01|q=7777777987DE7777|u=2
ρ01 := ΛR1|b=01|q=AD77777777777797|u=3
```

compose:

```text
ΛH1|E=00.77777839777BA87877777B7DA7B77C97.1,01.7777797777BB987777777CDAD8777C9E.2,02.77777B777777777777777777A777777D.2|R=00.7777777987DE7777.2(01,00),01.AD77777777777797.3(01,02)
```

A receiver can ACK the reconstructed structure:

```text
ΛH1|ACK|E=00,01,02|R=00(01,00),01(01,02)
```

The ACK confirms entity/relation structure, not exact original wording.

## 6. Tool-class tests

For project-side tool-region calibration, encode these source concepts separately:

```text
curl
browser DevTools
session tools
```

Expected qualitative tool geometry:

- a command-line HTTP client should emphasize `T00`, `T05`, and `T07`;
- browser developer tooling should emphasize `T01`, `T02`, and `T12`, with context-dependent `T03/T04`;
- session-oriented tooling should emphasize `T03`, with context-dependent `T00/T01/T04/T07`.

The regions need not recover exact software product names unless shared context has bound those names.

## 7. Action/tool composition

For a request conceptually equivalent to “inspect the current artifact using browser developer instrumentation,” keep operation and instrument separate:

```text
A=[α00:<inspection/action-region>]
T=[τ00:<browser-devtool-region>]
X=03
```

Do not fold the tool identity into the action vector.

## 8. Epistemic distinction

Represent a suspected relation:

```text
K=R02:K03:0.35
```

Represent a strongly supported relation:

```text
K=R02:K05:0.86
```

The relation can remain the same while its epistemic status changes.

## 9. Synchronization

If a receiver gets a packet containing unknown handles, it should return:

```text
ΛH1|SYNC?
```

The sender then provides only the missing bindings. After synchronization, the receiver can continue with compact handles.

## 10. Fresh-session interoperability test

1. Start AI session A with `prompt/LAMBDA_H_BOOTSTRAP.md`.
2. Start AI session B with the same canonical bootstrap.
3. Ask both to encode the same 10 words and 5 contextual polysemy pairs.
4. Compare relative nearest-neighbor order, not exact hex.
5. Ask A to encode a compositional sentence and B to decode it.
6. Ask B to return `ACK` structure.
7. Check that entity identity, relation direction, requested action, tool class, and epistemic status survive the transfer.

The protocol is succeeding if semantic topology and compositional structure survive despite modest coordinate drift.
