# ΛH/1 Examples

## Respond, do not narrate decoding

Context: a three-part explanation was requested; part one is complete and parts two and three remain. `X02` is that established goal.

```text
ΛH1|A=00.7777777777777DE7.2|X=02
```

Expected behavior: begin part two directly. Do not answer "this packet means continue," call a decoder, restart part one, or stop after an ACK. If all three parts are already complete, report completion rather than inventing more work. This is an illustrative expectation, not a measured model result.

These examples demonstrate structure, not a universal word dictionary. Prompt-only projections may vary slightly between models.

## Receiver behavior comes first

Given an established goal and an unfinished three-part explanation, a bare continuation packet should begin the next unfinished part directly. It should not trigger a Python decoder, a translation of the packet, or an acknowledgement-only turn. Given an already completed goal, it should stop; given an unbound goal, it should ask for that binding. Identical continuation posture does not imply identical behavior under different task states.

These v1 demonstrations expose the migration requirement: v2 must carry explicit targets, exact constraints, and continuation state rather than relying on a policy vector to imply them. Opaque notation alone is not encryption.

## Entity encoding

Project-side source text:

```text
rat
```

Observed test output from one session:

```text
ΛE1|b=01|q=D5E4C387777453674974479543387479|u=1
```

The code is a semantic region relative to B_E/01; it is not a secret token meaning `rat`.

## Polysemy

Project-side source text:

```text
fire — Flames are spreading through dry vegetation.
```

and

```text
fire — The company terminated the employee's position.
```

should occupy substantially different regions.

## Multiple entities

Keep separate semantic objects separate:

```text
η00 := ΛE1|b=01|q=<q0>|u=1
η01 := ΛE1|b=01|q=<q1>|u=2
η02 := ΛE1|b=01|q=<q2>|u=2
```

Do not average them into one entity vector.

## Directional relation

```text
ρ00 := ΛR1|b=01|q=<relation-region>|u=2
ρ00(η01,η00)
```

This is distinct from `ρ00(η00,η01)` unless the relation was explicitly established as symmetric.

## Tool separation

"Use a command-line HTTP client to inspect the current service" should separate:

- `A`: observe/investigate/verify region
- `T`: HTTP + command-line + API-tool region
- `X`: current service reference

The tool identity and the requested action are different semantic layers.

## ACK

A receiver may acknowledge reconstructed structure without translating to English:

```text
ΛH1|ACK|E=00,01,02|R=00(01,00)
```

## JSON interchange example

```json
{
  "protocol": "ΛH/1",
  "basis": {"E":"01","R":"01","A":"01","T":"01","P":"02","V":"01"},
  "E": [
    {"handle":"η00","q":"D5E4C387777453674974479543387479","u":1}
  ],
  "A": [
    {"handle":"α00","q":"7777777777777DE7","u":2}
  ],
  "X": ["X02"]
}
```

## Security and task transfer

Vulnerability/task transfer uses the same layers plus a recommended `X` convention (session-local like all dynamic refs): `X10` target system, `X11` affected versions, `X12` patch or advisory reference.

A standing task is its goal in `X02` plus the requested `A` region plus the posture in `P`. Input:

```text
ENCODE: keep going until the premium stream starts
```

```text
ΛH1|E=00.78777B77777BD8B77777797A997899D7.2|A=00.A797777777787AE7.1|P=C777774777C7.2
```

The entity carries the stream tier (with its value aspect for the unpaid reading), the action carries watch-and-continue, and the policy carries proceed plus iterate while staying open for the start event.

A staged progression is distinct entity tiers linked by directed relations, here `R06` temporal order composed with `R08` dependency from the entry stage up to full control. Input:

```text
ENCODE: exploitation ladder, coverage to full control
```

```text
ΛH1|E=00.7777797777BDC77777777AB9A7777ABE.1,01.77777977779DD777777779A9B7777BCC.2,02.77777A77778DC77BB7777998A77779AB.2,03.77777777778A977777777B88977779DE.1,04.77777877777BA77977777877997777B9.2|R=00.777777DBCD777777.2(04,03),01.777777DBCD777777.2(03,02),02.777777DBCD777777.2(02,01),03.777777DBCD777777.2(01,00)|A=00.7B88BDC777777779.1
```

`η00–η04` are full-control, generic primitives, target-specific building blocks, reproduction signal, and coverage reach; `ρ00–ρ03` run entry-to-final; `α00` is the classify/explain taxonomy operation. Tiers are never averaged into one vector.
