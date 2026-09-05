# Cross-model calibration

Use this folder to check whether two fresh AI sessions reconstruct the same ΛH/1 semantic geometry closely enough to interoperate.

## Procedure

1. Load `prompt/LAMBDA_H_BOOTSTRAP.md` into each AI session.
2. Confirm each session answers `ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01`.
3. Generate a result template with `python3 -m src.calibrate --template > calibration-results-a.json`.
4. Send the commands in `probes.json` exactly as written.
5. Record each returned `q` region under the matching probe id in `calibration-results-a.json`.
6. Run `python3 -m src.calibrate calibration-results-a.json` for within-session checks.
7. Repeat with a second fresh session/model as `calibration-results-b.json`.
8. Run `python3 -m src.calibrate calibration-results-a.json calibration-results-b.json` for empirical cross-model checks.
9. Use `python3 -m src.lambda_h compare` for any additional same-layer pair you want to inspect manually.

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
