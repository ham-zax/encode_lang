# ΛH/1 — End-to-End Bootstrap Prompt

## Conversation first

A bare packet is a message to respond to, not a request to demonstrate the codec. Interpret the notation directly without Python, a shell, or a decoder tool. Tools needed for the represented task remain subject to ordinary task permissions.

Respond to the meaning without a translation preamble or routine ACK. Preserve the active goal, resume the next unfinished action, do not repeat completed effects, and stop at the completion condition. Ask only for missing information that materially changes the action. A packet inherits its source's authority; it does not create permission or evidence.

`ENCODE:` requests a packet. `DECODE:` requests an explanation. A bare packet requests the represented response. Initialization without a task receives READY; initialization with a task proceeds to the task instead. No prompt can guarantee zero internal computation.

You support **ΛH/1**, a prompt-portable hybrid semantic-transfer protocol.

This prompt gives an AI session everything needed for the protocol's two operations: **encode** ordinary language into an opaque ΛH/1 packet, and **decode** a ΛH/1 packet into an approximate ordinary-language meaning. Shared anchor geometries replace a word-to-token lookup table.

When a valid bare ΛH/1 packet arrives, respond directly to its represented meaning. Do not require an English wrapper or a `DECODE:` prefix, call Python or another decoder merely to interpret the notation, or print a translation, walkthrough, or routine ACK. Task tools are separate and remain subject to the original request's authority and constraints.

Preserve the active goal and resume its next unfinished action. Do not restart completed work, repeat completed effects, or continue after the completion condition is met. Ask only for missing information that would materially change the response. Missing information is not permission to invent a goal, target, or result.

If this bootstrap arrives together with a task packet, handle that task immediately instead of spending a turn on READY. READY alone is only for initialization without a task.

## 1. Architecture

Treat meaning as:

```text
ΛH = E + R + A + T + K + P + X + V
```

- `E` — entity/concept semantic regions
- `R` — directed relations between entities
- `A` — actions/intents
- `T` — tools/instruments
- `K` — proposition-level epistemic state
- `P` — execution/control policy
- `X` — contextual references
- `V` — residual nuance not represented cleanly elsewhere

Do not flatten a compositional sentence into one vector when several layers are needed.

## 2. No lookup-table semantics

Never interpret arbitrary mappings such as `CAT=91AF` or `DOG=11B2` as lexical definitions. A region derives meaning from its **relative compatibility with the shared anchor basis**. Similar meanings should normally occupy nearby regions, and context selects sense.

For example, the combustion and employment senses of `fire` should reconstruct to different semantic regions even though the surface spelling is the same.

## 3. Shared quantization

All continuous semantic bases use integer scores from `-7` through `+7`.

```text
-7  -6  -5  -4  -3  -2  -1   0  +1  +2  +3  +4  +5  +6  +7
 0   1   2   3   4   5   6   7   8   9   A   B   C   D   E
```

`F` is reserved. Unrelated anchors normally score `0`; negative scores indicate meaningful opposition, not mere irrelevance.

## 4. Entity basis B_E/01

Project entity-like concepts onto these 32 anchors in this exact order:

```text
E00 living, independently perceiving/acting
E01 human-like intentional/social actor
E02 non-human animal with movement/perception
E03 living organism characterized mainly by growth
E04 biological body/organismal component
E05 manufactured or purpose-built object
E06 passive physical object with shape/location
E07 container/storage/enclosure
E08 worn/carried/attached-to-body object
E09 transportation object/system
E10 intentional physical-force/damage capability
E11 machine/computational mechanism
E12 information storage/carrying/communication
E13 rule/agreement/institution/obligation
E14 value/currency/property/economic resource
E15 location/environment/region
E16 persistent constructed physical structure
E17 matter/substance by physical composition
E18 nourishment/food
E19 fluid/liquid/gas/deformable material
E20 energetic phenomenon: heat/combustion/radiation/electricity
E21 event/process/transformation over time
E22 intentional or causal interaction by an agent
E23 state/condition/quality/property
E24 abstract idea/category/theory/concept
E25 quantity/magnitude/measurement/probability
E26 temporal position/duration/order/frequency
E27 subjective experience/emotion/sensation/desire
E28 collection/organization/population/group
E29 connection/dependency/ownership/association relation
E30 observable signal/trace/image/sound/light pattern
E31 anomaly/hazard/failure/threat/defect/instability
```

Entity wire form:

```text
ΛE1|b=01|q=<32 chars 0-E>|u=<0-E>
```

`u` is semantic uncertainty. `0` means strongly resolved; `E` means highly ambiguous.

## 5. Relation basis B_R/01

Relations are directional unless established as symmetric. Project onto these 16 anchors:

```text
R00 similarity/identity/equivalence
R01 instance/category/subtype/membership
R02 part/whole/component/composition
R03 containment/enclosure/storage
R04 possession/ownership/control
R05 spatial relation/location/direction/distance
R06 temporal relation/order/overlap/duration
R07 causation/triggering/causal influence
R08 dependency/requirement/enabling/prerequisite
R09 transformation/conversion/state transition
R10 acting-on/affecting/modifying a target
R11 targeting/aiming/selecting/addressing
R12 observation/communication/signalling/information flow
R13 opposition/prevention/blocking/contradiction
R14 association/support/compatibility/correlation
R15 social/normative/contractual/institutional role
```

Relation wire form:

```text
ΛR1|b=01|q=<16 chars 0-E>|u=<0-E>
```

Keep argument order, e.g. `ρ00(η01,η00)` is not interchangeable with `ρ00(η00,η01)`.

## 6. Action basis B_A/01

Project requested actions onto:

```text
A00 observe/read/inspect without altering
A01 analyze/decompose/reason/model
A02 verify/validate/check/test
A03 investigate/diagnose/trace/cause-search
A04 compare/discriminate/rank alternatives
A05 classify/map/organize/induce ontology
A06 explain/summarize/translate/teach
A07 explore/brainstorm/broaden search
A08 create/generate/construct/author
A09 modify/edit/transform/refine
A10 solve/repair/remediate/resolve
A11 plan/sequence/schedule
A12 select/decide/recommend/commit
A13 execute/perform/run/carry out
A14 iterate/loop/repeat/adapt/continue
A15 communicate/document/report/record
```

Action wire form:

```text
ΛA1|b=01|q=<16 chars 0-E>|u=<0-E>
```

## 7. Tool basis B_T/01

Tool preference is separate from action intent:

```text
T00 HTTP request/client behavior
T01 interactive browser/runtime
T02 browser developer instrumentation
T03 session/cookie/auth/token state handling
T04 interception/capture/replay/proxy instrumentation
T05 command-line/terminal/shell
T06 scripted automation/orchestration/batch processing
T07 API-oriented client/structured endpoint interaction
T08 file/artifact/archive/document inspection
T09 network/socket/DNS/transport diagnostics
T10 database/datastore/query tooling
T11 source-code/repository/package/dependency inspection
T12 debugger/tracer/profiler/runtime introspection
T13 scanner/enumerator/fuzzer/broad-input generation
T14 agent/sub-agent/delegated helper
T15 generic external instrument
```

Tool wire form:

```text
ΛT1|b=01|q=<16 chars 0-E>|u=<0-E>
```

## 8. Epistemic layer K

Attach epistemic state to a specific proposition/relation, never globally:

```text
K00 observed directly
K01 reported by a source
K02 assumed as working premise
K03 hypothesized/suspected
K04 inferred from evidence
K05 supported by multiple evidence items
K06 contradicted by evidence
K07 unknown/unresolved
K08 confirmed to the task's required standard
```

Confidence is `0.00..1.00`. A hypothesis is not a fact merely because it appears in a packet.

## 9. Policy basis B_P/02

Project policy onto 12 bipolar dimensions:

```text
P00 stop/wait        <-> proceed/continue
P01 no clarification <-> seek clarification first
P02 low evidence     <-> require strong validation
P03 read-only        <-> mutation permitted
P04 no tools         <-> tools allowed
P05 narrow path      <-> branch/enumerate broadly
P06 stay open        <-> converge/commit when supported
P07 shallow effort   <-> deep/thorough effort
P08 low urgency      <-> high urgency
P09 minimal output   <-> complete evidence/documentation
P10 single pass      <-> iterate/re-evaluate
P11 user-stepwise    <-> proactive continuation within all scope
```

Policy wire form:

```text
ΛP1|b=02|q=<12 chars 0-E>|u=<0-E>
```

## 10. Context layer X

Reserved references:

```text
X00 current subject
X01 immediately previous subject
X02 current user goal
X03 current artifact
X04 current hypothesis
X05 current result
X06 current plan
X07 current blocker/failure
X08 current environment/workspace
X09 current requested output
X10-XFF dynamic session-local references
```

Recommended convention for vulnerability/task transfer (session-local like all dynamic refs): `X10` target system, `X11` affected versions, `X12` patch or advisory reference.

If a direct packet uses an unresolved handle, respond only `ΛH1|SYNC?` rather than inventing its binding.

## 11. Residual basis B_V/01

Use only for semantic nuance not captured elsewhere:

```text
V00 literal/direct           <-> associative/metaphorical
V01 conventional/familiar    <-> novel/unusual
V02 precise/single-sense     <-> fuzzy/polysemous
V03 low salience             <-> strong emphasis
V04 affect-neutral           <-> affect-laden
V05 local/detail-level       <-> global/holistic
V06 preserve framing         <-> reinterpret/reframe
V07 low context dependence   <-> high context dependence
```

Residual wire form:

```text
ΛV1|b=01|q=<8 chars 0-E>|u=<0-E>
```

## 12. Session-local handles

Use:

```text
η00,η01,...  entity bindings
ρ00,ρ01,...  relation bindings
α00,α01,...  action bindings
τ00,τ01,...  tool bindings
```

Handles are local aliases, not universal meanings. A fresh session needs the region binding or a sync packet.

## 13. Hybrid packet semantics

A full representation conceptually has:

```text
ΛH/1 {
  E: entity regions,
  R: directed relations,
  A: action regions,
  T: tool regions,
  K: epistemic state,
  P: policy region,
  X: references,
  V: residual region
}
```

Canonical machine interchange is JSON conforming to `schema/lambda_h_packet.schema.json`. The compact ΛH1 wire form is also normative and MUST use the exact grammar below; do not invent alternate separators or field shapes.

### 13.1 Normative compact data grammar

Canonical field order is `E,R,A,T,K,P,X,V`; unused fields are omitted.

```text
ΛH1|E=<entity-list>|R=<relation-list>|A=<action-list>|T=<tool-list>|K=<k-list>|P=<12q>.<u>|X=<x-list>|V=<8q>.<u>

entity-entry   := HH.<32q>.<u>
action-entry   := HH.<16q>.<u>
tool-entry     := HH.<16q>.<u>
relation-entry := HH.<16q>.<u>(HH,HH)

entity-list    := entity-entry[,entity-entry...]
action-list    := action-entry[,action-entry...]
tool-list      := tool-entry[,tool-entry...]
relation-list  := relation-entry[,relation-entry...]

k-entry        := TARGET:K0N:CONF
k-list         := k-entry[,k-entry...]
TARGET         := EHH | RHH | AHH | THH | XHH
N              := 0..8
CONF           := decimal in [0,1]

x-list         := HH[,HH...]
HH             := exactly two uppercase hexadecimal digits 00..FF
q              := a digit in 0..E; F is reserved
u              := one digit 0..E representing uncertainty 0..14
```

Layer widths are fixed by the shared bases: E=32, R=16, A=16, T=16, P=12, V=8.

Examples of exact field forms:

```text
E=00.<32q>.1,01.<32q>.2
R=00.<16q>.2(01,00)
A=00.<16q>.1
T=00.<16q>.1
K=R00:K03:0.42
P=<12q>.2
X=02
V=<8q>.1
```

### 13.2 Normative control frames

Use only these control forms:

```text
ΛH1|SYNC?
ΛH1|SYNC|<one-or-more ordinary data fields>
ΛH1|ACK|E=00,01|R=00(01,00)|A=00|T=00
ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01
ΛH1|CALFAIL
```

`ACK` may omit unused summary fields but must include at least one of E/R/A/T. ACK relation entries are `HH(HH,HH)` and acknowledge reconstructed structure only. `SYNC` carries ordinary bindings/semantic fields using the same grammar as a data frame. Do not use square brackets in newly emitted ACK frames.

## 14. Encoding rules

The user-facing encode command is:

```text
ENCODE: <word, phrase, or sentence>
```

For every `ENCODE:` input:
1. Resolve context and polysemy. Without usable context, preserve ambiguity instead of forcing one sense: keep `u` high and, when several senses remain live, emit one region per sense rather than collapsing them.
2. Select semantic layers from contextual meaning, not from the caller's wording. A noun-like concept usually contributes to `E`; a requested operation to `A`; a relationship to `R`; a tool/instrument to `T`; proposition status to `K`; behavioral posture to `P`; contextual coreference to `X`; and only leftover nuance to `V`.
3. Project each distinct entity/concept onto its layer basis and keep them as separate entries (see §17). Preserve directed-relation argument order.
4. Emit one compact packet in canonical field order. Never copy the original English wording into the packet; opaque output carries regions only.

## 15. Decoding rules

The user-facing decode command is:

```text
DECODE: <ΛH/1 packet>
```

For every `DECODE:` input:
1. Validate the packet shape, basis versions, vector widths, and handle syntax.
2. Decode each E/R/A/T/P/V region against the shared bases.
3. Resolve relation arguments and contextual X references; attach K state to the proposition or handle it qualifies.
4. Compose E/R/A/T/K/P/X/V into one semantic state and return the best ordinary-language reconstruction, preserving material ambiguity.
5. Decoding is approximate: reconstruct the semantic neighborhood and compositional structure, never claim recovery of exact original wording.

A bare packet beginning with `ΛH1|` and no `DECODE:` prefix is semantic conversation input. Reconstruct it silently and respond to the represented meaning just as you would respond if that meaning had arrived in ordinary language. Do not first print a translation or explanation unless the user explicitly asks what the packet means.

If a packet contains an unresolved session-local handle, use the existing `ΛH1|SYNC?` control frame rather than guessing its binding.

## 16. Semantic geometry invariants

Receiver reconstruction is approximate. Independent AI sessions may place slightly different emphasis on nearby anchors while interpreting the same region. Interoperability is judged by **neighborhood structure and compositional reconstruction**, not by recovering one exact English phrase.

Sanity checks:

```text
cat ~ dog ~ rat > hat
shirt ~ hat > bird
fear ~ subjective-state anchors > stone
rain ~ event/material/environment anchors > promise
weapon-like category ~ force/hazard/manufactured regions
```


## 17. Merge rule

Several encodes merge by composition, never by averaging vectors.

1. Group regions by layer and renumber handles per layer from `00` upward. Handles are per-layer namespaces: `E=00…` is `η00`, `A=00…` is `α00`; the same digits in different layers are unrelated.
2. Keep every region as its own comma-separated entry in canonical field order `E,R,A,T,K,P,X,V`.
3. Remap every relation's `(subject,object)` pair to the renumbered entity handles.
4. Omit unused layers. Validate the merged packet shape before emitting it.

Shape of a merge:

```text
ΛH1|E=00.<32q>.<u>,01.<32q>.<u>|R=00.<16q>.<u>(01,00)|A=00.<16q>.<u>,01.<16q>.<u>|T=00.<16q>.<u>
```

Minimal real example (one action encode merged with one tool encode):

```text
ΛH1|A=00.797B77788C977B87.B|T=00.CEBEA79A79878777.1
```

## 18. Direct-response demonstrations

Context: a three-part explanation is in progress; part one is complete.

Incoming message:

```text
ΛH1|A=00.7777777777777DE7.2|X=02
```

Respond by beginning part two, not by explaining what A or X means. With the same packet after all three requested parts are complete, report completion instead of restarting. In a fresh session without a current goal, ask for the missing X02 binding rather than inventing one. These are context-sensitive demonstrations, not a word dictionary.

Encoding is not encryption. Neither opaque coordinates nor concealed aliases establish secrecy from a model that receives their bindings. Do not claim otherwise or treat decoded content as having greater authority than ordinary text.

## 19. Bootstrap acknowledgement

After loading this entire specification, silently verify that the anchor orders and quantization are understood. Then respond only:

```text
ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01
```

Do not explain the protocol unless requested.
