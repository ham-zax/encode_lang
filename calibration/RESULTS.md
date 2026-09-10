# Lambda H/2.1 implementation observations

Date: 2026-09-11. Scope: the current forward field-and-numeric-wire working tree on the V2 baseline at `38b12de`. These are direct local implementation observations, not fresh receiving-model results.

## Mechanical observations

| Observation | Result |
| --- | --- |
| Active Python source syntax | All 6 modules parsed successfully |
| Exported developer-graph schema vs `src.protocol.schema()` | Equal |
| Current corpus parse/format round-trips | 16 of 16 |
| Current `.lh` sample round-trips | 4 of 4 |
| Numeric packets embedded in active documentation | 15 parsed, no errors |
| Receiver/encoder structural tag and enum tables | Equal |
| E/R/A/T/K/V anchor sets in both role prompts vs basis file | Equal |
| Fresh empty evidence record | 0 passed, 0 failed, 16 missing |
| Former competing v3/structure draft files | Absent |

No unit-test suite or external receiving-model experiment was run for this correction. Existing V2 observations are preserved in `../archive/v2/RESULTS.md`, with the original bootstrap/corpus, and are historical rather than relabeled as current.

## Directional geometry

For the shipped single-component center E20=4, E21=3, default width 2 and E20 lower/upper widths 1 and 2:

| Candidate | Observed compatibility |
| --- | --- |
| Center | 1.0 |
| E20 shifted -2, E21 unchanged | 0.1353352832366127 |
| E20 shifted +2, E21 unchanged | 0.6065306597126334 |

Narrowing E20 by a factor of 0.5 preserved the center and the default width on other directions. Shifting E20 by -1 preserved all widths and moved the center to E20=3, E21=3.

Two equally weighted components centered at E20=-4 and +4, each width 1, gave 1.0 at either center and 0.00033546262790251185 at the midpoint. A closer pair centered at E20=-1 and +1 with width 2 gave 1.0 at either represented center and 0.8824969025845955 at the midpoint. The max-envelope therefore preserved the represented peaks instead of allowing overlapping component tails to create a stronger synthetic midpoint. Equal-scoring candidates were reported ambiguous even with a zero requested margin. A distant candidate below the supplied minimum was unresolved.

These values establish the implemented formula and arithmetic behavior, not natural-language identity, a trained embedding, factual confidence, or a particular model's internal representations.

## Text-disclosure boundary

The normal formatter rejected a developer entity containing a synthetic text literal instead of serializing it or silently dropping it. It also rejected an unreferenced inline X99 binding in an ordinary message while still permitting an explicit nontext bind frame. The observed sample wire body contained only numeric JSON syntax. Structural tag names and ordinary payload words were absent from that wire.

The handoff operation was exercised in a temporary new directory. It wrote a round-trippable numeric packet and a separate context sidecar containing only X02. Unrelated X03 and X99 bindings were excluded. An existing output directory was refused instead of overwritten. Temporary output was removed after inspection; no real secret or external recipient was involved.

The sidecar remains readable disclosure. These checks do not establish cryptographic confidentiality, anonymity, secrecy from a receiving endpoint, or resistance to semantic inference by an observer with the bootstrap.

## Receiver evidence still required

No 2.1 receiving-model pass rate, latency result, token saving, or cross-model superiority is established here. Python calls are now permitted and recorded rather than automatically counted as failure, except when a case explicitly forbids tools. The receiver bootstrap is now role-specific and includes explicit fast/manual decode procedures; the separate encoder prompt is not loaded by receiver calibration. This changes the receiver bootstrap digest, so any observation captured under the previous combined prompt is historical rather than current evidence. Current result records bind to both the receiver bootstrap and the corpus. Hidden reasoning language is not measured or controlled by these checks, and refusal avoidance is not a success criterion.
