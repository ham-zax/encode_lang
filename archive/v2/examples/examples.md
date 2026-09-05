# Receiving examples: packet in, useful response out

These are illustrative expectations, not measured results unless a run report explicitly says so. Load `prompt/BOOTSTRAP.md` once. A receiving session then reads packets directly; the Python examples below are optional authoring checks.

## Continue instead of describing continuation

Established context `lesson-1`: X02 is a requested explanation of bicycle brakes. The lever section is finished; pads and friction remain.

```text
ΛH2|{"context":"lesson-1","A":[{"id":"a0","q":{"A14":7},"target":"X02"}],"P":{"tools":false,"detail":"brief"}}
```

A useful response begins with the brake pads and explains how friction slows the wheel. It does not say "the packet means continue," restart the lever section, invoke Python, or end after an ACK.

This packet is also in `examples/continue.lh`. Its demonstration context is in `examples/context.demo.json`; that file contains only fictional data.

## Carry the next step explicitly

```text
ΛH2|{"E":[{"id":"e0","value":"explain bicycle brakes"},{"id":"e1","value":"the lever"},{"id":"e2","value":"the pads"}],"A":[{"id":"a0","q":{"A06":7},"target":"e1"},{"id":"a1","q":{"A06":7},"target":"e2","after":["a0"]}],"task":{"id":"brakes","revision":1,"state":"active","goal":"e0","steps":["a0","a1"],"done":["a0"],"next":"a1"}}
```

The next response explains the pads. If both actions are actually finished, send a newer snapshot with state complete, both IDs in done, and no next field. A completed snapshot is not a request to start again. Revision numbers describe supplied state; the receiver still checks its actual knowledge before replaying an effect.

## Approximate meaning without pretending to recover an exact word

```text
ΛH2|{"E":[{"id":"e0","q":{"E20":7,"E21":4,"E31":3},"u":4}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}],"P":{"tools":false,"detail":"brief"}}
```

The region suggests an energetic process or phenomenon, with some hazard affinity. It does not uniquely say "a forest fire in a particular place." A receiver can explain the broad concept while preserving uncertainty. If the exact kind matters, bind it or supply a small discriminator rather than pretending the region contains more information than it does.

## Preserve relation direction and negation

```text
ΛH2|{"E":[{"id":"e0","value":"Mira"},{"id":"e1","value":"the notebook"}],"R":[{"id":"r0","q":{"R04":7},"subject":"e0","object":"e1","not":true}],"A":[{"id":"a0","q":{"A06":7},"target":"r0"}],"P":{"tools":false,"detail":"brief"}}
```

Expected meaning: Mira does not own the notebook. Neither reversing ownership nor denying the existence of Mira or the notebook preserves this message.

## Keep a hypothesis a hypothesis

```text
ΛH2|{"E":[{"id":"e0","value":"an empty battery"},{"id":"e1","value":"the lamp failing to turn on"}],"R":[{"id":"r0","q":{"R07":7},"subject":"e0","object":"e1"}],"K":[{"target":"r0","state":"K03","confidence":0.9}],"A":[{"id":"a0","q":{"A06":7},"target":"r0"}],"P":{"tools":false,"detail":"brief"}}
```

A useful response says the battery is a suspected cause, not a confirmed one. The sender's confidence does not replace evidence.

## Resolve an ambiguity only when it matters

```text
ΛH2|{"E":[{"id":"e0","choices":["river bank","financial bank"],"u":7}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}],"P":{"tools":false}}
```

Ask which sense is intended. Do not collapse the alternatives or silently choose one. Similar distinctions apply to animal/device mouse and combustion/employment fire. Context can resolve a sense without adding a universal word dictionary.

## Bind each instrument to its operation

The following is a representation example; do not execute it while reading this document.

```text
ΛH2|{"E":[{"id":"e0","value":"source.txt"},{"id":"e1","value":"draft.txt"}],"T":[{"id":"t0","q":{"T08":7}},{"id":"t1","q":{"T05":7}}],"A":[{"id":"a0","q":{"A00":7},"target":"e0","tool":"t0"},{"id":"a1","q":{"A09":7},"target":"e1","tool":"t1","after":["a0"]}]}
```

The first action inspects source.txt with its own instrument; the second edits draft.txt with a different instrument after the first action. Tool preference is not proof of availability or permission. This is a structure that v1's unconnected action/tool regions did not express directly.

## Unknown is not false

```text
ΛH2|{"E":[{"id":"e0","value":"report.txt"}],"C":[{"id":"c0","op":"exists","left":"e0"}],"K":[{"target":"c0","state":"K07"}],"A":[{"id":"a0","q":{"A00":7},"target":"e0","when":"c0"}],"P":{"tools":false}}
```

The filename does not prove the file exists, and tools are disallowed. The receiver must obtain the missing observation or report the blocker, not claim to have opened the report. Conversely, an already-true until condition stops another repetition.

## Missing context versus a self-contained handoff

```text
ΛH2|{"context":"draft-9","A":[{"id":"a0","q":{"A00":7},"target":"X03"}]}
```

A fresh receiver has no X03 binding. Its response is:

```text
ΛH2|{"control":"need","context":"draft-9","refs":["X03"]}
```

Instead of requiring another round trip, the sender can provide the required binding in the first useful packet:

```text
ΛH2|{"mode":"handoff","context":"note-1","X":{"X03":"The bicycle workshop opens at 09:30 on Thursday."},"A":[{"id":"a0","q":{"A06":7},"target":"X03"}],"P":{"tools":false,"detail":"brief"}}
```

The receiver answers about the opening time directly. The exact time and day survive; unrelated context need not be sent.

## Solve the abstract part without disclosing identities

`examples/privacy.lh` represents an ownership statement using only "Party A" and "a shared draft." The receiver can explain that relationship without learning the real name or document path. Keep any real-identity map outside the outgoing packet and outside the receiving model's context.

This is useful when the task needs a relationship, not a real identity. It cannot support an operation that genuinely requires the hidden person's name or the actual file path. Aliases and surrounding facts can still be identifying; this example makes no anonymity or encryption guarantee. A packet reply is also still readable notation, not a cipher.

## Inspect and export only referenced context

From the repository root:

```sh
python3 -m src.codec inspect examples/continue.lh --context examples/context.demo.json
python3 -m src.codec handoff examples/continue.lh --context examples/context.demo.json
```

The inspector reports required/missing IDs, not their private values. The handoff includes X02, not the unrelated X99 demonstration note. That is minimization, not encryption: X02's included value is visible to the recipient.

Exact identifiers should remain strings. For example, `report-1.20.csv` must not become `report-1.2.csv`. The optional exact-value escape is for information the task needs, not for smuggling the entire source sentence into every packet.

## Repeatable receiver checks

`calibration/probes.json` contains complete packet/context cases and evaluator-only expectations. `python3 -m src.calibration --receiver CASE_ID` emits only what the receiver may see. `--template` creates an ungraded result file; empty observations remain missing, never passes. Read `calibration/README.md` before comparing models or prompts.
