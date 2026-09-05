# ΛH/1 Examples

These examples demonstrate structure, not a universal word dictionary. Prompt-only projections may vary slightly between models.

## Entity encoding

Input:

```text
WORD: rat
```

Observed test output from one session:

```text
ΛE1|b=01|q=D5E4C387777453674974479543387479|u=1
```

The code is a semantic region relative to B_E/01; it is not a secret token meaning `rat`.

## Polysemy

```text
WORD: fire
CONTEXT: Flames are spreading through dry vegetation.
```

and

```text
WORD: fire
CONTEXT: The company terminated the employee's position.
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
  "basis": {"E":"01","R":"01","A":"01","T":"01","P":"01","V":"01"},
  "E": [
    {"handle":"η00","q":"D5E4C387777453674974479543387479","u":1}
  ],
  "A": [
    {"handle":"α00","q":"7777777777777DE7","u":2}
  ],
  "X": ["X02"]
}
```
