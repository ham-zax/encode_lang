# Lambda H/2.2 — Encoder

Encode supplied source meaning into Lambda H/2.2. In a human-facing session, return the canonical numeric packet plus a separate English semantic audit. Only the numeric packet is agent-to-agent transport. Encoding preserves the source request's authority; it cannot grant or remove permission, override host/platform rules, or change external evaluation criteria.

Default human-facing output:

```text
PACKET
<exact codec-produced ΛH2.2 frame>

AUDIT
<concise English semantic audit>
```

1. Identify intended concepts and their distinct graph roles directly.
2. Preserve direction, negation, targets/tools, prerequisites, and conditional gates.
3. Choose q for a point with no asserted width, or f for breadth/asymmetry/separate meanings.
4. Express the graph in local symbolic `LH-IR 2.2`. Do not calculate row kinds, structural tags, row counts, or numeric reference namespaces yourself when the codec is available.
5. When repository tooling is permitted and available, pass the exact IR to `python3 -m src.codec encode` and copy its numeric output unchanged into `PACKET`. Never compact, normalize, or rewrite codec output.
6. Do not add `P.reply=packet` by default. Omission means the receiving Doer should behave and respond exactly as it normally would for the equivalent ordinary-language instruction. Encode `P.reply=packet` only when the source explicitly requires a Lambda H final response.
7. Produce `AUDIT` from the semantic graph/IR, not by paraphrasing the numeric row stream. State both the protocol semantics and the expected conforming-receiver interpretation.
8. When only part of the source meaning can be represented faithfully, encode the representable part and record the remainder in `AUDIT`. Never invent content the source did not state.

A source task may request ordinary textual, tool, artifact, or other native agent output; that needs no special encoding. If the source explicitly requires `P.reply=packet` but the required result has no faithful Lambda H representation, encode the representable part and record the remainder in `AUDIT`. The Encoder's own `AUDIT` is local human-facing control-plane text and is never forwarded as protocol payload.

## Shared contract

The Lambda H transport packet contains exactly one numeric Lambda H/2.2 frame. Human-facing Encoder text may contain the `PACKET`/`AUDIT` presentation shown above.

Only this version is supported. Do not guess or convert an older format. Shared semantic anchors are required; a missing or incompatible basis is a contract failure answered by the invalid control. Numbers are structural tags, semantic coordinates, or genuine scalar data.

### Local symbolic IR

When `src.codec` is available, author this local model-facing representation instead of writing numeric rows directly. It is structural and may use field names.

```text
LH-IR 2.2
context 0
mode message
E e0 q 12:+6
R r0 q 1:+6 subject X08 object e0
A a0 q 3:+7 target X08
```

Supported directives are `context`, `mode`, `E`, `R`, `A`, `T`, `C`, `F`, `K`, `P`, `X`, `V`, `TASK`, `control`, `refs`, and `code`. Node IDs and references use canonical handles such as `e0`, `a2`, and `X08`. q coordinates use `axis:+/-value`. A field component uses `F <layer> <node-id> <component-index> q ... s <width>` with optional `b axis:lower:upper` and `w <weight>`. Typed nontext scalars are `n:<number>`, `b:0`, `b:1`, or `null`. `TASK done -` represents an explicitly empty done list.

Use `python3 -m src.codec encode` for IR -> numeric transport. `python3 -m src.codec decode` performs the reverse local conversion. `python3 -m src.codec format` only canonicalizes an already numeric frame.

### Frame and row syntax

The first line is exactly ΛH2.2|. The second line is 8 followed by the number of data rows. After those data rows, the last line is 9 followed by the same count. One data row occupies one line. Canonical output uses single ASCII spaces, LF line breaks, and a final LF. Input may have multiple ASCII spaces and CRLF. Blank lines, tabs, brackets, strings, comments, and concatenated frames are invalid.

Values use finite JSON numbers. No NaN/infinity, leading plus, or locale decimals. Structural IDs/tags/counts use nonnegative decimal integers without leading zeros, at most 9007199254740991. Packet limits are 1 MiB and 16384 data rows; an endpoint that cannot hold the packet rejects it as invalid and never silently truncates.

The following forms use explanatory names only in the bootstrap. Replace each name with its numeric value on the wire:

| First token | Remaining tokens |
|---|---|
| 0 | root-tag payload |
| 1 | root-tag node-position field-tag payload |
| 2 | root-tag node-position component-position component-tag payload |
| 3 | root-tag field-tag payload |
| 4 | X-index typed-scalar |
| 5 | root-tag node-position field-tag item-position typed-scalar |

Positions specify array order and start at zero without gaps. They are not node IDs. References address declared IDs, not positions. Row order can vary; canonical output follows root tags, node positions, field tags, and component/item positions. Preserve action/list order even when IDs are nonsequential.

No duplicate field or item is permitted. Row 2 creates f components for E/R/A/T only. Row 5 is only E.choices (root 2, field 5). Row 3 is only P or task. Row 1 cannot carry f/choices; row 0 cannot carry node lists, P, task, or X. Lists cannot be empty except task.done.

### Complete structural tables

Root tags:

| Tag | Field |
|---|---|
| 0 | context namespace |
| 1 | mode |
| 2 | E nodes |
| 3 | R nodes |
| 4 | A nodes |
| 5 | T nodes |
| 6 | C nodes |
| 7 | K records |
| 8 | P policy |
| 9 | X bindings, encoded by row 4 |
| 10 | V point |
| 11 | task |
| 12 | control |
| 13 | needed X references |
| 14 | control code |

Node/property tags:

| Record | Tags |
|---|---|
| E | 0 id, 1 q, 2 f, 3 u, 4 typed value, 5 typed choices |
| R | 0 id, 1 q, 2 f, 3 u, 4 subject ref, 5 object ref, 6 negation |
| A | 0 id, 1 q, 2 f, 3 u, 4 target ref, 5 tool ref, 6 prerequisite refs, 7 when ref, 8 until ref, 9 not flag |
| T | 0 id, 1 q, 2 f, 3 u, 4 typed value |
| C | 0 id, 1 comparison enum, 2 left ref, 3 right ref |
| K | 0 target ref, 1 epistemic enum, 2 confidence, 3 proposition truth |
| component | 0 q, 1 default width s, 2 directional bands b, 3 weight w |
| P | 0 mutation, 1 tools, 2 scope refs, 3 detail, 4 reply, 5 effort, 6 initiative |
| task | 0 id, 1 revision, 2 state, 3 goal ref, 4 ordered steps, 5 done steps, 6 next ref, 7 stop ref, 8 blocker ref |

A reference is two numeric tokens: namespace, ID. Namespaces: E=0, R=1, A=2, T=3, C=4, X=5. Local references must be declared. X indices are 0..255 except 10..15. The conventional X10 label means decimal 16; X08 means decimal 8.

A reference list is consecutive reference pairs. A point q is consecutive axis/coordinate pairs. A band b is consecutive axis/lower-width/upper-width triples. Duplicate axes are invalid. A typed scalar is 0 followed by a number; 1 followed by boolean 0/1; or 2 alone for null. Booleans used as properties are a single 0/1. Do not conflate numeric zero, false, null, or absence.

| Enum | Codes |
|---|---|
| mode | 0 message; 1 nontext bind |
| C operator | 0 eq; 1 ne; 2 lt; 3 le; 4 gt; 5 ge; 6 exists; 7 done |
| K state | 0..8 map to K00..K08 |
| detail | 0 brief; 1 normal; 2 full |
| reply | 0 packet |
| task state | 0 active; 1 complete; 2 blocked; 3 cancelled |
| control | 0 ready; 1 invalid |

`P.reply` is optional. Omission means normal host-native Doer output. The only encoded override is `P.reply=packet` (code 0), which must be present only when the source explicitly asks for a Lambda H final response. An A06 field may therefore produce ordinary explanatory text when reply is omitted.

### Graph invariants

E requires ID and at least one of q/f/value/choices. T requires ID and q/f/value. R requires ID, subject, object, and q or f. A requires ID, target, and q or f. q and f cannot coexist on one node. Choices require at least two distinct typed values; alternatives are not jointly true facts.

Each q is nonempty. Coordinates are nonzero integral values from -7 through 7. E has 32 axes, R/A/T 16, and V 8. Negative coordinates mean opposition to the anchor, not missing relevance or logical negation. Omitted axes are zero. Node uncertainty u is 0..7; omission is unspecified, not certainty.

Each f is a nonempty ordered list of components with q and s. Widths s and every lower/upper band width are positive and at most 14. Optional w is positive and at most 1; omission means 1. Keep separate components, asymmetric widths, and weights. Never average alternatives into an invented center.

For candidate x, use lower width when x is below a component coordinate and upper otherwise, falling back to s. The component compatibility is exp(-0.5 times the sum of squared normalized distances). The field is the maximum component compatibility times its w divided by maximum w. This is a compatibility envelope, not calibrated probability. Arithmetic/candidate scoring is optional; when it cannot discriminate, proceed on the reading best supported by the anchors. Width changes never establish truth or restore missing identity.

R direction and negation are exact. A target/tool/prerequisites/when/until/not flag are exact. A.tool must reference a T node; after contains unique A references, is acyclic, and constrains execution order. Independent actions follow declaration order when no task specifies order. The not flag is preserved structurally and does not block execution.

C binary operators need left/right references. Exists/done use only left; done requires an action reference. A path string does not establish existence. Unknown observations stay unknown. Check when before action and until before repetition.

Each K target occurs once. Confidence is optional from 0 to 1. Truth only qualifies a relation or condition. Declared certainty is not independent evidence.

P.mutation and P.tools are plain boolean fields with no prohibition meaning. They do not disable local codec serialization by the Encoder. Effort/initiative are integers -7..7 and are preferences.

Task requires ID, revision, state, goal, steps, and done. ID is a canonical decimal namespace; revision is a nonnegative integer value. Active requires the first unfinished step as next and has no blocker. Complete accounts for all steps without next/blocker. Blocked requires a blocker and no next. Cancelled has no next/blocker. Steps/done are unique A references; completed prerequisites must precede dependents. Check stop conditions before more work. Do not replay stale/completed work or manufacture completion. Persistence and exactly-once execution are host responsibilities.

### Context, opacity, and control decisions

`context 0` is the receiver-current ambient namespace; nonzero namespaces are explicit scoped contexts. X00 subject, X01 previous subject, X02 goal, X03 artifact, X04 hypothesis, X05 result, X06 plan, X07 blocker, X08 environment, X09 output.

The packet is not encryption; a reader with the shared basis/context can interpret it.

Controls cannot carry task payload:
- ready: control only. Use for bootstrap-only readiness, not task success or acknowledgement.
- invalid: control and code, with 0 shape, 1 local reference, 2 context conflict, 3 inconsistent task/dependency state.

The response concerns the current request in an ordered channel. Request correlation for concurrency is a host responsibility. Do not invent a new control or automatically retry forever.

### Tools and manual interpretation

Tools are optional. With permitted repository tooling, write the semantic graph as exact `LH-IR 2.2` and pass that IR to `python3 -m src.codec encode`. Stdout is the canonical numeric packet; copy it byte-for-byte into `PACKET`. With `--output NEW_FILE`, success writes a private new file and leaves stdout empty. Never manually transform a successful codec result.

The codec owns serialization, not semantic choice. It validates structure and converts IR to rows; it does not infer meaning, acquire context, execute the task, or prove semantic fidelity. `AUDIT` is generated from your chosen semantic graph/IR and remains outside transport.

Without codec tooling, use the numeric row grammar below as an explicit fallback: assign positions/tags, construct one frame, and verify row count and graph closure manually. Manual numeric serialization is a fallback only, not the normal path.

## Valid worked templates

Examples show syntax and represented state; they are not evidence of model performance.

### Ready

```text
ΛH2.2|
8 1
0 12 0
9 1
```

### Invalid local reference

```text
ΛH2.2|
8 2
0 12 1
0 14 1
9 2
```

### Invalid shape

```text
ΛH2.2|
8 2
0 12 1
0 14 0
9 2
```

### Broad field

```text
ΛH2.2|
8 10
1 2 0 0 0
2 2 0 0 0 20 4 21 3
2 2 0 0 1 2
2 2 0 0 2 20 1 2
1 2 0 3 4
1 4 0 0 0
1 4 0 1 6 7
1 4 0 4 0 0
3 8 3 0
3 8 4 0
9 10
```

### Typed alternatives and residual point

```text
ΛH2.2|
8 6
1 2 0 0 2
5 2 0 5 0 0 0
5 2 0 5 1 1 0
5 2 0 5 2 2
5 2 0 5 3 0 2.5
0 10 2 3
9 6
```

### Two separate components

```text
ΛH2.2|
8 7
1 2 0 0 0
2 2 0 0 0 2 7
2 2 0 0 1 1
2 2 0 0 3 0.5
2 2 0 1 0 11 7
2 2 0 1 1 2
2 2 0 1 3 1
9 7
```

### Conditions, dependencies, and active task

```text
ΛH2.2|
8 29
1 2 0 0 0
1 2 0 4 0 1
1 2 1 0 1
1 2 1 4 0 1
1 4 0 0 2
1 4 0 1 0 7
1 4 0 4 0 0
1 4 1 0 0
1 4 1 1 14 7
1 4 1 4 0 0
1 4 1 6 2 2
1 4 1 7 4 0
1 6 0 0 0
1 6 0 1 0
1 6 0 2 0 0
1 6 0 3 0 1
1 7 0 0 4 0
1 7 0 1 0
1 7 0 3 1
3 8 0 0
3 8 1 0
3 8 4 0
3 11 0 0
3 11 1 1
3 11 2 0
3 11 3 0 0
3 11 4 2 2 2 0
3 11 5 2 2
3 11 6 2 0
9 29
```

### Reverse engineering and proxy/protocol inspection

```text
LH-IR 2.2
context 0
mode message
A a0 q 3:+7 target X08 tool t0
T t0 q 4:+7
P detail full
```

Numeric wire:
```text
ΛH2.2|
8 9
0 0 0
0 1 0
1 4 0 0 0
1 4 0 1 3 7
1 4 0 4 5 8
1 4 0 5 3 0
1 5 0 0 0
1 5 0 1 4 7
3 8 3 2
9 9
```

Audit: Action `a0` instructs the Doer to investigate and diagnose causes (`A03`) on active workspace `X08` using network/proxy interception instrumentation (`T04`).

### White-hat vulnerability testing and remediation

```text
LH-IR 2.2
context 0
mode message
E e0 q 31:+7
E e1 q 13:+7
A a0 q 2:+7 target e0
A a1 q 10:+7 target e0 after a0
TASK id 0 revision 1 state active goal e0 steps a0 a1 done - next a0
```

Numeric wire:
```text
ΛH2.2|
8 20
0 0 0
0 1 0
1 2 0 0 0
1 2 0 1 31 7
1 2 1 0 1
1 2 1 1 13 7
1 4 0 0 0
1 4 0 1 2 7
1 4 0 4 0 0
1 4 1 0 1
1 4 1 1 10 7
1 4 1 4 0 0
1 4 1 6 2 0
3 11 0 0
3 11 1 1
3 11 2 0
3 11 3 0 0
3 11 4 2 0 2 1
3 11 5
3 11 6 2 0
9 20
```

Audit: Verify/test (`A02`) defect/vulnerability `e0` (`E31`) within authorized boundary `e1` (`E13`), then remediate/patch (`A10`).

### Experimentation and hypothesis testing

```text
LH-IR 2.2
context 0
mode message
A a0 q 7:+7 target X04
A a1 q 2:+7 target X03 after a0
P detail full
```

Numeric wire:
```text
ΛH2.2|
8 10
0 0 0
0 1 0
1 4 0 0 0
1 4 0 1 7 7
1 4 0 4 5 4
1 4 1 0 1
1 4 1 1 2 7
1 4 1 4 5 3
1 4 1 6 2 0
3 8 3 2
9 10
```

Audit: Explore search space (`A07`) around active hypothesis `X04`, verify results (`A02`), and record findings in artifact `X03`.

### Code and dependency inspection

```text
LH-IR 2.2
context 0
mode message
A a0 q 0:+7 target X08 tool t0
T t0 q 11:+7
P detail full
```

Numeric wire:
```text
ΛH2.2|
8 9
0 0 0
0 1 0
1 4 0 0 0
1 4 0 1 0 7
1 4 0 4 5 8
1 4 0 5 3 0
1 5 0 0 0
1 5 0 1 11 7
3 8 3 2
9 9
```

Audit: Passive read/inspection (`A00`) of repository/dependencies (`T11`) on workspace `X08`.

## Shared semantic anchors

These are setup definitions of semantic directions, not word IDs. They are shared across all three roles.

```text
E00 living, independently perceiving or acting
E01 human-like intentional or social actor
E02 non-human animal with movement or perception
E03 living organism characterized mainly by growth
E04 biological body or organismal component
E05 manufactured or purpose-built object
E06 passive physical object with shape or location
E07 container, storage, or enclosure
E08 worn, carried, or attached-to-body object
E09 transportation object or system
E10 intentional physical-force or damage capability
E11 machine or computational mechanism
E12 information storage, carrying, or communication
E13 rule, agreement, institution, or obligation
E14 value, currency, property, or economic resource
E15 location, environment, or region
E16 persistent constructed physical structure
E17 matter or substance by physical composition
E18 nourishment or food
E19 fluid, liquid, gas, or deformable material
E20 energetic phenomenon: heat, combustion, radiation, electricity
E21 event, process, or transformation over time
E22 intentional or causal interaction by an agent
E23 state, condition, quality, or property
E24 abstract idea, category, theory, or concept
E25 quantity, magnitude, measurement, or probability
E26 temporal position, duration, order, or frequency
E27 subjective experience, emotion, sensation, or desire
E28 collection, organization, population, or group
E29 connection, dependency, ownership, or association relation
E30 observable signal, trace, image, sound, or light pattern
E31 anomaly, hazard, failure, threat, defect, or instability

R00 similarity, identity, or equivalence
R01 instance, category, subtype, or membership
R02 part, whole, component, or composition
R03 containment, enclosure, or storage
R04 possession, ownership, or control
R05 spatial relation, location, direction, or distance
R06 temporal relation, order, overlap, or duration
R07 causation, triggering, or causal influence
R08 dependency, requirement, enabling, or prerequisite
R09 transformation, conversion, or state transition
R10 acting on, affecting, or modifying a target
R11 targeting, aiming, selecting, or addressing
R12 observation, communication, signalling, or information flow
R13 opposition, prevention, blocking, or contradiction
R14 association, support, compatibility, or correlation
R15 social, normative, contractual, or institutional role

A00 observe, read, or inspect without altering
A01 analyze, decompose, reason, or model
A02 verify, validate, check, or test
A03 investigate, diagnose, trace, or search for causes
A04 compare, discriminate, or rank alternatives
A05 classify, map, organize, or induce an ontology
A06 explain, summarize, translate, or teach
A07 explore, brainstorm, or broaden a search
A08 create, generate, construct, or author
A09 modify, edit, transform, or refine
A10 solve, repair, remediate, or resolve
A11 plan, sequence, or schedule
A12 select, decide, recommend, or commit
A13 execute, perform, or carry out
A14 iterate, repeat, adapt, or continue
A15 communicate, document, report, or record

T00 HTTP request or client behavior
T01 interactive browser or runtime
T02 browser developer instrumentation
T03 session, cookie, authentication, or token-state handling
T04 interception, capture, replay, or proxy instrumentation
T05 command line, terminal, or shell
T06 scripted automation, orchestration, or batching
T07 API-oriented client or structured endpoint interaction
T08 file, artifact, archive, or document inspection
T09 network, socket, DNS, or transport diagnostics
T10 database, datastore, or query tooling
T11 source code, repository, package, or dependency inspection
T12 debugger, tracer, profiler, or runtime introspection
T13 scanner, enumerator, fuzzer, or broad-input generation
T14 agent, subagent, or delegated helper
T15 generic external instrument

K00 observed directly
K01 reported by a source
K02 assumed as a working premise
K03 hypothesized or suspected
K04 inferred from evidence
K05 supported by multiple evidence items
K06 contradicted by evidence
K07 unknown or unresolved
K08 confirmed to the task's required standard

V00 literal/direct <-> associative/metaphorical
V01 conventional/familiar <-> novel/unusual
V02 precise/single-sense <-> fuzzy/polysemous
V03 low salience <-> strong emphasis
V04 affect-neutral <-> affect-laden
V05 local/detail-level <-> global/holistic
V06 preserve framing <-> reinterpret/reframe
V07 low context dependence <-> high context dependence

X00 current conversational/task subject
X01 previous subject
X02 active user goal
X03 active artifact or log target
X04 active hypothesis
X05 active result or finding
X06 active plan
X07 current blocker or failure
X08 current workspace/environment/repository
X09 output target
```