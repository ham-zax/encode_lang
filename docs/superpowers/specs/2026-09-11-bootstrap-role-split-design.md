# Lambda H/2.1 Bootstrap Role Split Design

## Goal

Split the current all-in-one Lambda H/2.1 bootstrap into two standalone role-specific prompts so a sending agent only learns encoding behavior and a receiving agent only learns decoding/execution behavior. Keep the default `prompt/BOOTSTRAP.md` receiver-first because current calibration and usage already treat it as the receiving bootstrap.

## Why this change

The current bootstrap teaches both directions plus validation, field arithmetic, task execution, context handling, and reply behavior in one prompt. That increases prompt load for weak or fast receivers and asks them to infer a decoding procedure from reference tables. The protocol should instead make the common receiver path explicit and mechanically ordered while preserving the same wire, graph, field, context, and policy contract.

## Architecture

### Receiver bootstrap: `prompt/BOOTSTRAP.md`

`prompt/BOOTSTRAP.md` remains the canonical standalone receiving bootstrap and the file hashed by the calibration framework. It contains only what a receiver needs to consume Lambda H/2.1 packets and act on their represented meaning.

Its operational procedure is explicit:

1. Verify the `ΛH2.1|` prefix and numeric tagged-array shape.
2. Unpack root record tags using the fixed structural table.
3. Unpack node/component records using the layer-specific structural tables.
4. Resolve numeric references into exact graph edges and preserve subject/object, action target/tool, dependencies, negation, conditions, policy, and task state exactly.
5. Interpret `q` or `f` directly against the shared semantic directions. For `f`, preserve separate components and their widths/weights; do not average alternatives into one meaning.
6. Resolve only the X bindings actually required by referenced nodes. If a required binding is absent, return the numeric need control instead of inventing it.
7. Apply hard conditions, prohibitions, permissions, epistemic state, and task continuation before acting.
8. Perform the represented task or answer it. Do not require reconstruction of an English source sentence as an intermediate representation.

Python remains optional for mechanical unpacking, validation, and field arithmetic when tools are permitted. The bootstrap must be usable without Python as well. It must not claim to control or observe hidden reasoning language, treat opacity as encryption, or use the notation to bypass provider safety systems.

The receiver bootstrap does not teach how to construct a new packet from ordinary language. `DECODE:` may explicitly request a natural-language reconstruction for debugging, but normal bare packet handling executes or answers the represented task.

### Encoder bootstrap: `prompt/ENCODER.md`

`prompt/ENCODER.md` is a new standalone sending-agent prompt. It shares the same protocol version, structural tags, enum values, semantic basis, context roles, and field contract as the receiver, but its operational procedure runs in the opposite direction:

1. Identify the intended semantic entities/concepts, directed relations, actions, conditions, epistemic state, permissions, context references, and task state.
2. Keep exact operational structure exact; do not encode directionality, permissions, prerequisites, or task progress as approximate semantic geometry.
3. Choose `q` for a compact semantic point when no width is asserted; choose `f` when breadth, asymmetric falloff, or multiple live semantic regions matter.
4. Keep distinct plausible meanings as distinct field components. Do not manufacture a midpoint.
5. Use X references only for exact identity/text that genuinely must be supplied outside the numeric wire. Include only bindings required by the packet.
6. Convert the developer graph to the numeric tagged-array transport using the fixed structural tables. Do not create lexical codebooks, character-number encodings, base64 disguises, or arbitrary word-token maps.
7. Validate graph invariants and verify every wire leaf after the prefix is numeric and finite.
8. Emit only the packet unless the requested workflow explicitly calls for developer JSON or a separate context sidecar.

The encoder does not execute the task it encodes. It does not need receiving-task continuation instructions except enough contract knowledge to encode task state correctly.

## Shared contract and duplication policy

Both prompts are standalone. They therefore duplicate the stable wire tables and shared semantic directions rather than requiring a third prompt fragment at runtime. `src/protocol.py`, `src/wire.py`, `src/geometry.py`, and `semantics/basis.json` remain the implementation authorities; prompt duplication is synchronized documentation, not a second protocol implementation.

The split must not change the Lambda H/2.1 wire format or developer graph. A packet produced under the encoder bootstrap must be consumable by the decoder bootstrap without translation through ordinary message wording.

## Calibration and documentation

`src/calibration.py` continues hashing `prompt/BOOTSTRAP.md`, because receiver benchmarks measure the receiver bootstrap. `calibration/README.md` should call this the decoder/receiver bootstrap explicitly.

`PROMPT.md` and `README.md` should distinguish the two roles:

- Receiving/acting on packets -> `prompt/BOOTSTRAP.md`.
- Encoding a message/task into Lambda H/2.1 -> `prompt/ENCODER.md`.

Existing numeric examples, protocol specification, and developer tooling remain compatible. No old V2 results become evidence for either new prompt.

## Error handling and low-capacity behavior

The receiver procedure should favor deterministic structural steps over prose interpretation. Unknown tags, malformed numeric shape, invalid local references, context conflicts, and inconsistent task state map to the existing invalid controls/codes. Missing X context maps to the existing need control. Semantic ambiguity that materially changes the requested action remains unresolved instead of being guessed.

The encoder should reject input it cannot encode without losing required exact information. When an exact string/identifier is required, it should create an X reference and require deliberate context binding rather than silently substitute approximate semantics.

## Acceptance criteria

- `prompt/BOOTSTRAP.md` is receiver/decoder-only in operational instructions and includes an explicit ordered decoding/execution procedure.
- `prompt/ENCODER.md` exists and is encoder-only in operational instructions with an explicit ordered encoding procedure.
- Both are standalone and agree on Lambda H/2.1 wire tables, enum tables, field contract, semantic directions, context roles, and policy/task semantics.
- The split does not alter `src/protocol.py`, `src/wire.py`, or the wire representation solely to support the prompt roles.
- Current calibration continues to bind only to the receiver bootstrap.
- Documentation points users/agents to the correct prompt for each role.
- Neither prompt requires an English sentence reconstruction step before semantic action.
- Neither prompt claims access to hidden reasoning language, cryptographic secrecy, or safety-policy bypass.
