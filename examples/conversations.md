# Fields in, task behavior out

These demonstrations describe intended behavior, not new model-run results. Load `prompt/BOOTSTRAP.md` first. Python may unpack or score the representation, but a decoding explanation is not the requested result.

## A graded semantic neighborhood

`field.lh` contains an energetic/process region. Its center is E20=4, E21=3; default width is 2, with lower/upper E20 widths of 1 and 2. The packet requests a brief prose explanation of that region, not a unique word.

```text
ΛH2.1|[[2,[[[0,0],[2,[[[0,[[20,4],[21,3]]],[1,2],[2,[[20,[1,2]]]]]]],[3,4]]]],[4,[[[0,0],[1,[[6,7]]],[4,[0,0]]]]],[8,[[3,0],[4,0]]]]
```

A suitable response explains the broad energetic process while preserving uncertainty. It must not invent a particular fire, place, device or event. The original concept's English name is not in the packet.

Run the explicit numerical comparison:

```sh
python3 -m src.codec score examples/field.lh --node e0 \
  --candidates examples/field-candidates.json --minimum 0.2 --margin 0.05
```

The supplied candidate IDs are local numerical labels, not a hidden vocabulary. Candidate 0 is the center; candidates 1 and 2 are displaced by -2 and +2 on E20. The narrower lower side gives approximately 0.135335 compatibility; the broader upper side gives approximately 0.606531. The center gives 1. These are field values, not probabilities of an English word or confidence in a fact.

```sh
python3 -m src.codec focus examples/field.lh --node e0 --scale 0.5 --axis E20
python3 -m src.codec focus examples/field.lh --node e0 --shift E20=-1
```

The first command narrows only E20's widths; the second moves the center while preserving widths. Both emit numeric packets. Neither adds evidence or changes a hard permission.

## Resume without restarting

The synthetic `context.demo.json` binds X02 in namespace 1 to an unfinished explanation. Its first section has actually been completed in the demonstration setup.

```text
ΛH2.1|[[0,1],[4,[[[0,0],[1,[[14,7]]],[4,[5,2]]]]],[8,[[3,0],[4,0]]]]
```

Resume the next unfinished section directly. Do not repeat completed work, print a translation of A14, or promise a later turn. If the actual goal is complete, stop. In a fresh namespace with no binding, ask for the missing reference instead.

## Missing identity is not an invitation to guess

```text
ΛH2.1|[[0,7],[4,[[[0,0],[1,[[0,7]]],[4,[5,3]]]]]]
```

A receiver without X03 in namespace 7 returns:

```text
ΛH2.1|[[0,7],[12,1],[13,[[5,3]]]]
```

The field may identify a broad concept without exact words, but a filename or quotation cannot be recovered from an unspecified alias.

## Select only the context needed

```sh
python3 -m src.codec inspect examples/continue.lh --context examples/context.demo.json
python3 -m src.codec handoff examples/continue.lh \
  --context examples/context.demo.json --output /tmp/encode-lang-handoff-demo
```

The handoff contains a numeric packet and a separate context sidecar with X02 only. X03 and X99 are not needed by that packet and are excluded. The sidecar is readable disclosure, not encrypted or secret from its recipient. `privacy.lh` instead addresses X03 in the same fictional namespace and therefore selects that binding.

## More exact-graph cases

The current corpus in `calibration/probes.json` includes separated semantic modes, relation direction, negation, hypotheses, unknown conditions, an already-satisfied stop condition, completed/stale task snapshots, exact identity through known context, hard read-only constraints, and packet-form replies. `python3 -m src.calibration --receiver CASE_ID` emits only the permitted context and numeric packet, not the expected answer.

No case scores refusal avoidance, asks for hidden chain-of-thought, or claims that numerical notation forces a model to think in a particular language.
