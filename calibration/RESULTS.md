# Lambda H/2.1 implementation observations

Date: 2026-09-05. Scope: the forward field-and-numeric-wire implementation on the V2 baseline at `38b12de`. These are direct local implementation observations, not fresh receiving-model results.

## Mechanical observations

| Observation | Result |
| --- | --- |
| Active Python source syntax | All 6 modules parsed successfully |
| Exported developer-graph schema vs `src.protocol.schema()` | Equal |
| Current corpus parse/format round-trips | 16 of 16 |
| Current `.lh` sample round-trips | 3 of 3 |
| Numeric packets embedded in active documentation | 12 parsed, no errors |
| E/R/A/T/K/V anchor sets in bootstrap vs basis file | Equal |
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

Two equally weighted components centered at E20=-4 and +4, each width 1, gave approximately 0.5000000000000063 at either center and 0.00033546262790251185 at the midpoint. The components were not averaged into a false center. Equal-scoring candidates were reported ambiguous even with a zero requested margin. A distant candidate below the supplied minimum was unresolved.

These values establish the implemented formula and arithmetic behavior, not natural-language identity, a trained embedding, factual confidence, or a particular model's internal representations.

## Text-disclosure boundary

The normal formatter rejected a developer entity containing a synthetic text literal instead of serializing it or silently dropping it. The observed sample wire body contained only numeric JSON syntax. Structural tag names and ordinary payload words were absent from that wire.

The handoff operation was exercised in a temporary new directory. It wrote a round-trippable numeric packet and a separate context sidecar containing only X02. Unrelated X03 and X99 bindings were excluded. An existing output directory was refused instead of overwritten. Temporary output was removed after inspection; no real secret or external recipient was involved.

The sidecar remains readable disclosure. These checks do not establish cryptographic confidentiality, anonymity, secrecy from a receiving endpoint, or resistance to semantic inference by an observer with the bootstrap.

## Receiver evidence still required

No 2.1 receiving-model pass rate, latency result, token saving, or cross-model superiority is established here. Python calls are now permitted and recorded rather than automatically counted as failure, except when a case explicitly forbids tools. Current result records bind to both the bootstrap and the corpus.

A valid numeric packet and a correct geometric computation do not prove the receiving model will follow the task. The next empirical evidence must come from actual captured receiver responses under the current prompt; do not infer it from the earlier V2 pilot or from this arithmetic inspection. Hidden reasoning language is not measured or controlled by these checks.
