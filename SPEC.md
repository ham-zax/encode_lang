# Lambda H/2.2 specification

## 1. Scope and authorities

Lambda H/2.2 is the only active runtime protocol. `src/protocol.py` owns the graph and invariants, `src/wire.py` owns structural mappings, `src/rows.py` owns public row framing, `src/geometry.py` owns field arithmetic, and `semantics/basis.json` owns semantic directions.

The three standalone role prompts reproduce the same contract for endpoints without tools. Python is optional. Runtime protocol output contains one numeric packet and no prose, developer JSON, audit, code fence, or natural-language reconstruction.

The protocol does not infer meaning, execute actions, authenticate senders, persist task state, guarantee exactly-once effects, control hidden reasoning, or provide encryption.

## 2. Frame and lexical grammar

```text
ΛH2.2|
8 N
N data rows
9 N
```

The marker is literal. The two framing rows do not count as data. Each data row occupies one physical line. Canonical output uses one ASCII space, LF endings, and one final LF. Input permits multiple ASCII spaces and CRLF. Blank lines, tabs, comments, brackets, strings, concatenated frames, and trailing data are invalid.

Numbers use finite JSON number syntax. Structural tags, positions, list indices, IDs, and counts are canonical nonnegative decimal integers bounded by 9007199254740991. No leading plus or leading-zero aliases. Coordinates are nonzero integers from -7 through 7.

An endpoint accepts at most 1 MiB and 16384 data rows. It must abstain for insufficient capacity, never truncate.

## 3. Data rows

| Kind | Numeric row |
|---|---|
| 0 | `0 root-tag payload` |
| 1 | `1 root-tag node-position field-tag payload` |
| 2 | `2 root-tag node-position component-position component-tag payload` |
| 3 | `3 root-tag field-tag payload` |
| 4 | `4 X-index typed-scalar` |
| 5 | `5 root-tag node-position field-tag item-position typed-scalar` |

Node positions preserve declaration order independently of semantic IDs. Positions are zero-based and contiguous within their list. Row order is irrelevant to parsing; canonical output sorts by structural owner and position while preserving semantic array order.

Each property occurs once. Duplicate fields, duplicate item positions, missing positions, wrong row ownership, unknown tags, and wrong payload arity are invalid. Row 2 is only for E/R/A/T field components. Row 3 is only P/task. Row 4 is only X. Row 5 is only E choices.

## 4. Structural tags

Root tags:

```text
0 context   1 mode      2 E       3 R       4 A
5 T         6 C         7 K       8 P       9 X
10 V        11 task     12 control 13 refs   14 code
```

Record tags:

```text
E: 0 id, 1 q, 2 f, 3 u, 4 value, 5 choices
R: 0 id, 1 q, 2 f, 3 u, 4 subject, 5 object, 6 not
A: 0 id, 1 q, 2 f, 3 u, 4 target, 5 tool, 6 after,
   7 when, 8 until, 9 not
T: 0 id, 1 q, 2 f, 3 u, 4 value
C: 0 id, 1 op, 2 left, 3 right
K: 0 target, 1 state, 2 confidence, 3 truth
component: 0 q, 1 s, 2 b, 3 w
P: 0 mutation, 1 tools, 2 scope, 3 detail, 4 reply,
   5 effort, 6 initiative
task: 0 id, 1 revision, 2 state, 3 goal, 4 steps,
      5 done, 6 next, 7 stop, 8 blocker
```

References are `namespace ID`, with E=0, R=1, A=2, T=3, C=4, X=5. Local references must resolve. X indices are at most 255; 10 through 15 are reserved. X identities conventionally written as hexadecimal in the developer graph appear as decimal numbers in rows.

A reference list is consecutive reference pairs. A point is consecutive axis/coordinate pairs. A directional band is consecutive axis/lower-width/upper-width triples. A typed scalar is `0 number`, `1 boolean-code`, or `2` for null. Strings cannot be scalar payloads.

Enums:

```text
mode: message=0, bind=1
condition: eq=0, ne=1, lt=2, le=3, gt=4, ge=5, exists=6, done=7
epistemic: K00..K08 = 0..8
detail: brief=0, normal=1, full=2
reply: packet=0
task: active=0, complete=1, blocked=2, cancelled=3
control: ready=0, need=1, invalid=2, abstain=3
```

## 5. Graph and fields

E requires an ID and q, f, numeric/boolean/null value, or at least two distinct typed choices. T requires ID and q, f, or typed value. R requires ID, q/f, subject, and object. A requires ID, q/f, and target. C requires ID, operator, and left; binary comparisons also require right. K requires target and state.

A semantic node carries q or f, never both. q is a nonempty sparse coordinate map. Axis widths are E32, R16, A16, T16, and V8. Omitted coordinates are neutral zero. Negative coordinates mean opposition to an anchor, not logical negation.

Each f component requires q and positive default width s no greater than 14. Optional b provides positive lower/upper widths per axis, each no greater than 14. Optional w is positive and no greater than 1; omission means 1. Components retain order and separate semantic neighborhoods.

For candidate x and component j, choose the lower width where x is below q and the upper width otherwise, falling back to s:

```text
k_j(x) = exp(-0.5 * sum_i ((x_i - q_ji) / sigma_ji)^2)
F(x)   = max_j ((w_j / max(w)) * k_j(x))
```

F is compatibility under supplied geometry, not probability, truth, lexical identity, or a learned embedding. Uncertainty u is independently 0..7.

## 6. Exact operations and state

R subject/object order and negation are exact. A target, tool, prerequisite order, when/until gates, and prohibition are exact. Prerequisites must be acyclic. A tool references T; conditions reference C. Prohibited actions cannot be task steps.

Binary C operators require right. Exists and done omit right; done references an action. Unknown evidence stays unknown. A declared resource or action is not proof of existence or completion.

K states retain observed, reported, assumed, hypothesized, inferred, multiply supported, contradicted, unknown, and confirmed-to-required-standard. Confidence is 0..1. Truth applies only to R/C. Packet assertions are not independent evidence.

P false flags prohibit mutation/tool use. True stays within external authority. Scope can narrow but never expand authority. Effort and initiative are -7..7 preferences. Reply has only packet output.

Task requires canonical numeric ID, revision, state, goal, ordered steps, and done. Active requires the first unfinished step as next. Complete accounts for all steps. Blocked requires blocker. Non-active tasks have no next. Done steps include completed prerequisites. Stop is checked before more execution.

## 7. Context and opacity

Context IDs identify scoped state; they do not authenticate it. X00..X09 mean subject, previous subject, goal, artifact, hypothesis, result, plan, blocker, environment, and output. These names are bootstrap semantics, not automatic bindings.

Bind mode contains only protocol, mode, context, and nonempty nontext X values. Ordinary packets reject unreferenced inline bindings. A missing X binding produces need; a conflicting binding produces invalid code 2. Exact text is neither carried by the wire nor disguised as numbers.

Opacity means ordinary wording is absent. Shared anchors, packet shape, repetition, traffic metadata, and established context may still reveal meaning. Use external authenticated encryption when confidentiality is required.

## 8. Controls

Controls carry no task payload:

| Control | Fields | Codes |
|---|---|---|
| ready | control | none |
| need | context, control, refs | exact missing X references |
| invalid | control, code | shape=0, local-reference=1, context-conflict=2, state=3 |
| abstain | control, code | ambiguity=0, unrepresentable=1, text-output=2, contract=3, capacity/capability=4 |

Ready is bootstrap readiness, not execution success. Abstention reports inability to continue faithfully; it does not label a valid input malformed.

## 9. Canonicality and fidelity

For a supported wire-exportable graph G, parser P, and formatter F:

```text
P(F(G)) ≡ G
F(P(F(G))) = F(G)
```

Equivalence preserves fields, omission, arrays, scalar types, and numeric equality. Formatting never renumbers IDs, reorders semantic lists, inserts defaults, merges components, repairs malformed state, or hides text.

Structural round-trips prove serialization fidelity only. Semantic fidelity requires separate model behavior evidence. Tool-assisted and tool-free results must be reported separately.

## 10. Worked controls

Ready:

```text
ΛH2.2|
8 1
0 12 0
9 1
```

Need X03 in context 7:

```text
ΛH2.2|
8 3
0 0 7
0 12 1
0 13 5 3
9 3
```

Material ambiguity:

```text
ΛH2.2|
8 2
0 12 3
0 14 0
9 2
```
