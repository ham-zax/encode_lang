# A focus with directional falloff

The implemented model is a semantic activation field, not a word lookup. It makes the user's center-and-fading-neighborhood idea explicit while retaining exact directed task structure.

## What is represented

Each f component has a sparse q center, positive default width s, optional per-axis b bands `[lower,upper]`, and optional relative peak weight w (default 1). This implementation retains quantized -7..7 center/candidate coordinates; widths can be fractional. An omitted coordinate is neutral zero. Multiple components represent separate live neighborhoods rather than a single averaged identity.

For component j, choose sigma on each axis from its lower or upper side according to the sign of `x_i-q_ji`. An unspecified band uses s. Let `w_max` be the largest component weight, with omitted w treated as 1. The component response and combined field are:

```text
k_j(x) = exp(-0.5 * sum_i ((x_i-q_ji)/sigma_ji)^2)
F(x)   = max_j ((w_j/w_max) * k_j(x))
```

Since each k lies in [0,1] and normalized relative weights are in (0,1], F lies in [0,1]. The max-envelope treats components as alternative semantic neighborhoods: overlapping support can broaden coverage but cannot add into a stronger synthetic midpoint. It is a weighted compatibility score, not a normalized probability density. An asymmetric lower/upper component is only Gaussian-shaped on each side; it is not a general covariance-matrix Gaussian or an oscillating physical light wave.

Moving q moves the focus. Scaling s/b changes the spread. Changing a cutoff changes acceptance, not the focus. Narrowing a field is a modeling choice and does not produce new observations, factual certainty or exact lexical identity.

## An observed arithmetic example

The shipped field is centered at E20=4, E21=3. On E20, its lower width is 1 and upper width is 2; other widths are 2. Keeping E21 at 3, the implemented scorer returns:

| Candidate E20 | Activation |
| --- | --- |
| 4, the center | 1.0 |
| 2, lower by 2 | 0.1353352832 |
| 6, higher by 2 | 0.6065306597 |
| 1, lower by 3 | 0.0111089965 |

These are observations from the local geometric calculation, not receiving-model results. The different lower/upper values demonstrate directional falloff. Nothing in this calculation identifies an English word.

## Separate meanings, exact directions

Multiple components retain distinct modes rather than averaging their centers or summing their tails into a new stronger region. Equal-weight components each contribute a unit peak at their own center. Weights are relative peak emphasis, not proof that a particular sense is true; after normalization by the largest weight, a lower-weight component contributes a proportionally lower peak.

Relationship arguments, action targets, instruments, prerequisites, negation, permissions and completion remain exact graph structure. A soft region does not reverse subject/object order or relax a prohibition. Node uncertainty u and epistemic K annotations remain separate from geometric breadth.

## Using the Python helpers

`make_field` constructs a component. `activation` evaluates supplied coordinates. `focus_field` changes widths without moving centers. `shift_field` moves every component while preserving widths and separation. Invalid resulting fields are rejected, not silently clamped.

`rank_candidates` compares only the numerical candidates supplied by the caller. It returns all scores and applies an explicit minimum and margin; ties remain ambiguous even at a zero margin. There is no hidden vocabulary, universal nearest-word operation, model API request or learned embedding database in these helpers.

## What this does not establish

This geometry does not measure, control or reveal an LLM's hidden reasoning language or internal semantic space. Shared interpretation and task fidelity still require actual receiver evidence. Density/distribution-based semantic representations have research precedents, but those works learn representations; this project does not claim to reproduce their empirical results. The ordinary squared-exponential form motivates the falloff, while the split directional widths here are an explicit prototype design choice.

## Related primary sources

- Vilnis and McCallum, *Word Representations via Gaussian Embedding*: https://arxiv.org/abs/1412.6623
- Athiwaratkun and Wilson, *Multimodal Word Distributions*: https://arxiv.org/abs/1704.08424
- scikit-learn official RBF definition and length-scale discussion: https://scikit-learn.org/stable/modules/gaussian_process.html#radial-basis-function-rbf-kernel

The runtime uses only the Python standard library; these sources are conceptual references, not dependencies.
