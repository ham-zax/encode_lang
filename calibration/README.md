# Cross-model calibration

Use this folder to check whether independent project-side semantic projectors produce ΛH/1 geometry consistently enough for receiver sessions to interoperate.

## Procedure

1. Generate a result template with `python3 -m src.calibrate --template > calibration-results-a.json`.
2. Feed each `command` string in `probes.json` to the **project-side semantic projector under test**. The field name is retained for file-format compatibility; these strings are source text, not receiver-session commands.
3. Record each returned `q` region under the matching probe id in `calibration-results-a.json`.
4. Run `python3 -m src.calibrate calibration-results-a.json` for within-projector checks.
5. Repeat with a second projector/model implementation as `calibration-results-b.json` if you want an empirical cross-implementation comparison.
6. Run `python3 -m src.calibrate calibration-results-a.json calibration-results-b.json` for the pair comparison.
7. Use `python3 -m src.lambda_h compare` for any additional same-layer pair you want to inspect manually.

`prompt/LAMBDA_H_BOOTSTRAP.md` is not used to ask the receiver AI to generate these regions. Its job is only to make a receiver understand packets that the project has already produced.

Example:

```bash
python3 -m src.lambda_h compare E   D5E4C387777453674974479543387479   D5E4C387777453674974479543387479
```

The command reports:

- `mean_abs_delta` — average coordinate disagreement; lower is closer.
- `rmse` — root-mean-square coordinate disagreement; lower is closer.
- `cosine` — directional similarity of the signed semantic vectors; higher is closer. `null` means one region is the all-neutral vector.

## What counts as success

Do not require bit-identical vectors. Prompt-only ΛH/1 is intentionally judged by qualitative geometry.

The important checks in `probes.json` are relationships such as:

```text
sim(cat, dog) > sim(cat, hat)
sim(cat, rat) > sim(cat, hat)
sim(shirt, hat) > sim(shirt, bird)
```

Contextual senses such as combustion `fire` versus employment `fire`, animal `mouse` versus computer-device `mouse`, and financial `bank` versus river `bank` should not collapse to the same region.

For a two-result comparison, sense separation uses an empirical floor rather than an arbitrary fixed threshold. For each sense pair, the evaluator measures same-sense cross-model drift and requires within-session sense separation to exceed the larger same-sense drift. This asks whether the semantic distinction is stronger than ordinary model-to-model projection noise.

If a model repeatedly violates these relationships, treat that model/session as poorly calibrated for the current prompt-defined basis. Do not repair interoperability by inventing a word-to-token dictionary; adjust the shared basis in a new version or use an explicit calibration transform.

## Recording results

A simple result file can be maintained per model/session:

```json
{
  "protocol": "ΛH/1",
  "model": "example-model",
  "basis": {"E": "01", "T": "01"},
  "regions": {
    "cat": "<32-digit-q>",
    "dog": "<32-digit-q>",
    "curl": "<16-digit-q>"
  }
}
```

Keep model name, prompt version, and basis versions with the results so comparisons are reproducible.

`python3 -m src.calibrate` exits `0` when all configured qualitative checks pass, `1` when a populated check fails, and `2` for malformed or incomplete calibration input.
