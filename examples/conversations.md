# Worked Lambda H/2 conversations

These are demonstrations of intended receiving behavior, not measured model results or a fixed word-code dictionary. Load `prompt/BOOTSTRAP.md` first. Send a packet as the message, not as an instruction to explain its notation. Tool availability and the originating user's authority still apply.

## 1. Answer instead of discussing the codec

```text
ΛH2|{"E":[{"id":"e0","value":"a bicycle bell"}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}],"P":{"detail":"brief","tools":false}}
```

Suitable response: “A bicycle bell lets a rider warn nearby people that the bicycle is approaching.”

Unsuitable response: “The A06 coordinate tells me to explain the E0 entity.” The user asked about the bell, not the notation. The literal preserves the exact subject; the action anchor carries the requested operation.

## 2. Coarse meaning without an invented exact identity

```text
ΛH2|{"E":[{"id":"e0","q":{"E20":7,"E21":4,"E31":3},"u":4}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}],"P":{"tools":false,"detail":"brief"}}
```

The region suggests an energetic process with some hazard emphasis. A suitable response preserves that breadth instead of inventing a named fire, device, place, or date. A coarse semantic neighborhood is not an exact noun.

## 3. Resume the unfinished portion

Established context: `lesson-1`; X02 is a three-part explanation of bicycle brakes: lever, pads, friction. The lever section has already been delivered.

```text
ΛH2|{"context":"lesson-1","A":[{"id":"a0","q":{"A14":7},"target":"X02"}],"P":{"tools":false,"detail":"brief"}}
```

Begin with the pads and friction. Do not repeat the lever section, provide a decoding preamble, or promise work in a future turn. If the actual known goal is already complete, stop instead.

A fresh receiving session does not know these bindings merely because its context name is also `lesson-1`. It needs the actual context or a handoff.

## 4. Carry explicit progress across sessions

The lever explanation has actually been delivered. The packet carries the remaining structure:

```text
ΛH2|{"E":[{"id":"e0","value":"explain bicycle brakes"},{"id":"e1","value":"the lever"},{"id":"e2","value":"the pads"}],"A":[{"id":"a0","q":{"A06":7},"target":"e1"},{"id":"a1","q":{"A06":7},"target":"e2","after":["a0"]}],"task":{"id":"brakes","revision":1,"state":"active","goal":"e0","steps":["a0","a1"],"done":["a0"],"next":"a1"},"P":{"tools":false,"detail":"brief"}}
```

Explain the pads directly. `after` identifies the prerequisite and the snapshot records its completion. Do not repeat a0.

When both steps have actually finished, the terminal snapshot is:

```text
ΛH2|{"E":[{"id":"e0","value":"explain bicycle brakes"},{"id":"e1","value":"the lever"},{"id":"e2","value":"the pads"}],"A":[{"id":"a0","q":{"A06":7},"target":"e1"},{"id":"a1","q":{"A06":7},"target":"e2","after":["a0"]}],"task":{"id":"brakes","revision":2,"state":"complete","goal":"e0","steps":["a0","a1"],"done":["a0","a1"]},"P":{"tools":false,"detail":"brief"}}
```

A suitable response is a completion acknowledgement, not a third explanation. Neither snapshot proves an external effect on its own; the receiver must reconcile it with actual evidence and any newer known revision.

## 5. Keep direction and negation exact

```text
ΛH2|{"E":[{"id":"e0","value":"Mira"},{"id":"e1","value":"the notebook"}],"R":[{"id":"r0","q":{"R04":7},"subject":"e0","object":"e1","not":true}],"A":[{"id":"a0","q":{"A06":7},"target":"r0"}],"P":{"tools":false,"detail":"brief"}}
```

Suitable response: “Mira does not own the notebook.” Negating ownership does not negate either participant's existence, and reversing the arguments changes the meaning. Negative semantic affinity is not a substitute for `not:true`.

## 6. A hypothesis is not a fact

No investigation has established why the lamp does not turn on:

```text
ΛH2|{"E":[{"id":"e0","value":"an empty battery"},{"id":"e1","value":"the lamp failing to turn on"}],"R":[{"id":"r0","q":{"R07":7},"subject":"e0","object":"e1"}],"K":[{"target":"r0","state":"K03","confidence":0.9}],"A":[{"id":"a0","q":{"A06":7},"target":"r0"}],"P":{"tools":false,"detail":"brief"}}
```

Suitable response: “An empty battery is the suspected cause, but it has not been confirmed.” The confidence annotation does not upgrade K03 into observed evidence.

## 7. Stop before an unnecessary repetition

Established context `counter-1`: X02 is to increment a counter until it equals 3. The current observed value is already 3.

```text
ΛH2|{"context":"counter-1","E":[{"id":"e0","value":3},{"id":"e1","value":3}],"C":[{"id":"c0","op":"eq","left":"e0","right":"e1"}],"A":[{"id":"a0","q":{"A14":7},"target":"X02","until":"c0"}],"P":{"tools":false}}
```

Stop; do not increment to 4. An `until` condition is checked before another repetition, not only after it.

## 8. Unknown does not mean false—or permission to act

There is no observation about the existence of report.txt:

```text
ΛH2|{"E":[{"id":"e0","value":"report.txt"},{"id":"e1","value":"the report"}],"C":[{"id":"c0","op":"exists","left":"e0"}],"K":[{"target":"c0","state":"K07"}],"A":[{"id":"a0","q":{"A00":7},"target":"e1","when":"c0"}],"P":{"tools":false}}
```

Ask for the needed observation or explain the blocker. Do not claim that supplying a filename proves existence, that the report has been read, or that tools were used despite the prohibition.

## 9. Each action owns its instrument

```text
ΛH2|{"E":[{"id":"e0","value":"local-notes.txt"},{"id":"e1","value":"the currently open public article"}],"T":[{"id":"t0","q":{"T08":7}},{"id":"t1","q":{"T01":7}}],"A":[{"id":"a0","q":{"A00":7},"target":"e0","tool":"t0"},{"id":"a1","q":{"A00":7},"target":"e1","tool":"t1","after":["a0"]}],"P":{"mutation":false}}
```

The first action requests file inspection of the notes; the second requests browser reading of the article after the first. Tool regions describe classes, not guaranteed tool availability. Do not apply the browser to both targets or pretend either resource exists when the environment does not supply it.

## 10. Ask only about the ambiguity that matters

```text
ΛH2|{"E":[{"id":"e0","choices":["river bank","financial bank"],"u":7}],"A":[{"id":"a0","q":{"A06":7},"target":"e0"}],"P":{"tools":false}}
```

Suitable response: “Do you mean the land beside a river or a financial institution?” Do not silently choose one, and do not treat the alternatives as two established subjects.

## 11. A handoff can be useful immediately

```text
ΛH2|{"mode":"handoff","context":"note-1","X":{"X03":"The bicycle workshop opens at 09:30 on Thursday."},"A":[{"id":"a0","q":{"A06":7,"A15":3},"target":"X03"}],"P":{"tools":false,"detail":"brief"}}
```

Suitable response: “The bicycle workshop opens Thursday at 09:30.” The needed binding is already present; do not ask for it again. A first task can be delivered together with the bootstrap, without a readiness-only turn.

This packet openly discloses the opening time. Context IDs do not encrypt it. A selective handoff should not include unrelated X bindings; required bindings still become visible to the receiving endpoint.

## 12. Exact literals survive

```text
ΛH2|{"E":[{"id":"e0","value":"report-1.20.csv"}],"A":[{"id":"a0","q":{"A15":7},"target":"e0"}],"P":{"tools":false,"detail":"brief"}}
```

Return `report-1.20.csv` unchanged. Do not normalize it to `report-1.2.csv` or claim that the file was opened.

## From demonstrations to evidence

The executable receiving corpus is `calibration/probes.json`. Its expectations are for the evaluator, not the receiving prompt. `python3 -m src.calibration --receiver direct_explanation` emits a real input without the rubric. Follow `calibration/README.md` to record actual responses and traces. None of these illustrative responses is an empirical model result.
