# Numeric-only role flows

These flows describe intended behavior. They do not reconstruct packet meaning into English at runtime and do not claim measured model reliability.

## Encode

1. Load `prompt/ENCODER.md`.
2. Supply source meaning.
3. Receive exactly one numeric Lambda H/2.2 frame.
4. Meaning is encoded as far as the graph allows; any unrepresentable remainder is handled per the Encoder prompt (noted in the audit, never invented).

## Do

1. Load `prompt/DOER.md`.
2. Send one numeric frame, for example `field.lh`.
3. The Doer applies graph constraints and acts at the represented precision.
4. Receive numeric result/state or the invalid control for malformed structure.

## Canonicalize without execution

1. Load `prompt/DECODER.md` or use the optional codec.
2. Send one numeric frame.
3. Receive the canonical numeric frame or a numeric control.

```sh
python3 -m src.codec format examples/bounty-continue.lh
```

Canonicalization is not proof of semantic comprehension or task completion.

## Missing context

`continue.lh` references X02 in a numeric namespace but does not establish that binding. A fresh Doer resolves it from its best available grounding; a role name is never an ambient binding.

Text context is not sent by this runtime. Exact text-dependent actions and outputs may not be fully representable in the packet. Bind frames carry only numeric, boolean, or null values.
