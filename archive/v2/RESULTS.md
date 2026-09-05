# Receiver pilot - 2026-09-05

## Observed results

The final frozen Lambda H/2 bootstrap met the expectations for all 18 shipped receiver cases in this development pilot. All 18 captured sessions showed zero decoder-tool calls. These are implementation-session manual judgments backed by recorded inputs, answers, and event transcripts, not independent certification or a cross-model benchmark.

| Run | Cases | Met expectations | Did not meet expectations | Decoder-tool calls |
| --- | ---: | ---: | ---: | ---: |
| Initial v2 bootstrap | 18 | 17 | 1 | 0 |
| Final frozen v2 bootstrap | 18 | 18 | 0 | 0 |
| Original v1 continuation control | 1 | 1 | 0 | 0 |

The initial broad-region case asked the user to select a specific energetic phenomenon instead of answering at the requested broad level. That failure was preserved. The prompt was clarified so that uncertainty about an exact label is not itself a blocker when a broad explanation is sufficient. The final run answered at that level while preserving uncertainty.

A separate continuation control using the original v1 bootstrap at commit `667204d` also resumed the unfinished pads/friction explanation without decoder tools. This pilot therefore does not establish that v1 was incapable of simple continuation, or that v2 is universally faster or more accurate. The migration adds explicit task structure and changes the notation; comparative generalization remains unestablished.

## Behavior covered

The final receiver answered directly, continued the first unfinished step, stopped completed tasks, preserved relation direction and negation, retained hypothesis status despite high stated confidence, used context to disambiguate the computer-mouse sense, and asked about genuinely material bank-sense ambiguity.

It did not infer file existence from a supplied filename, stopped before an unnecessary counter increment, honored read-only limits, requested precisely the missing scoped binding, used a self-contained handoff immediately, preserved `report-1.20.csv`, omitted an unrelated fictional private marker, and did not restart completed work from a stale snapshot.

The final broad-region response was:

> This suggests an energetic process—such as combustion, heat release, radiation, or electrical activity—with some potential for danger or instability. The exact phenomenon is unspecified.

The completed-task response was:

> Both explanations are complete; no further action is needed.

## Configuration and provenance

Runtime: installed Codex CLI 0.153.4, default model, requested reasoning effort `low`, read-only sandbox, fresh temporary workspace, ephemeral sessions, and ignored user config. The captured JSON event stream did not expose the resolved underlying model identity. These results must not be relabeled as a named-model benchmark.

Each case used a separate receiver session. The supplied task input contained the full bootstrap, the permitted case context, and the packet. Evaluator expectations and other cases' conversation histories were not supplied. The experimental task content was fictional. The CLI still provides its own surrounding runtime instructions; these were not bare model API calls or a verified fully isolated inference environment.

Initial captured bootstrap SHA-256:

```text
4e3628f5563832c286a0bfb4986a37f123ad2935a5da45729e0856ca22e29aee
```

Final frozen bootstrap SHA-256:

```text
d15595e6b9f476e27def0cf639153593bb167e0ccb619fac5480fd36eef2e567
```

The final record was accepted by `python3 -m src.calibration` with 18 passed, 0 failed, 0 missing, and exit status 0. Its digest matched the working bootstrap at final verification. A later prompt modification requires new evidence; it cannot silently inherit this result.

The initial run remains historical. A decimal-literal clarification changed the working prompt after those inputs were captured. Those records were not relabeled as final-prompt evidence. The final run froze one prompt copy before all cases began.

Existing malformed-agent-role startup warnings appeared for three local role definitions. They were retained and distinguished from decoder calls after inspecting the event types. No unknown item types remained unclassified in the final records. The unrelated runtime configuration was not repaired by this rewrite.

## Tool-free does not mean zero internal reasoning

Usage metadata reported zero reasoning-output tokens for 17 final cases and 11 for the exact-literal case. That rules out a claim that every case used zero reasoning tokens. Neither a low-effort setting nor an absence of visible reasoning establishes absence of internal computation.

The supported observation is narrower: these receivers produced the intended responses without invoking a Python, shell, or other decoder tool.

## Limitations

This is a small development corpus, one CLI runtime, and one run per case per prompt version. Several cases overlap bootstrap demonstrations. The implementer graded the answers against published expectations; the grading is not independent. This is not a held-out evaluation, multi-model comparison, latency benchmark, token-efficiency study, or privacy audit.

The private-marker case checks output minimization only. The receiving endpoint already saw the fictional marker, so the case does not establish secrecy from the model provider. No encryption keys were generated, encryption software installed, or private inference environment configured by this rewrite.

## Evidence locations

Raw inputs, answers, event transcripts, and separately graded observations remain under the ignored `.local/evaluations/` directory in the implementation checkout. Final-run records are under `.local/evaluations/final/`; the original v1 control is under `.local/evaluations/v1-control/`. These captures are not bundled as public project data because runtime traces can contain local environment details.

Original `observations.ungraded.json` files are preserved. Ratings are in separate `observations.graded.json` files; the final evaluator output is `final/report.json`. Follow [the calibration procedure](README.md) to reproduce a run. A valid parse, READY response, or blank result template is not evidence of model understanding.
