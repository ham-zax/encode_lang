# ΛH/1 Project Notes

## Mission

Create a prompt-portable semantic interchange language that can be loaded into a fresh AI session without external model weights or a word lookup table.

The design is inspired by the idea of constructing task-specific representations and preserving structured state rather than relying only on surface wording. The project deliberately separates semantic kinds instead of forcing everything into one vector.

## Architecture decision

ΛH/1 uses:

```text
E + R + A + T + K + P + X + V
```

This separation is intentional:

- nouns/concepts belong primarily in `E`;
- directional structure belongs in `R`;
- requested operations belong in `A`;
- instruments belong in `T`;
- truth status belongs in `K`;
- execution preferences belong in `P`;
- shared references belong in `X`;
- leftover nuance belongs in `V`.

## Prompt-only tradeoff

The basis is defined in natural language, so two AI instances will not necessarily produce bit-identical vectors. The protocol therefore targets **geometric agreement**: similar concepts should remain nearby and compositional relations should be reconstructed consistently.

If deterministic coordinates become a requirement, the next architecture step is a shared embedding model or an explicit calibration transform.

## Source of truth

- Modular basis definitions: `semantics/*.yaml`
- Single authoritative AI bootstrap and compact/control grammar: `prompt/LAMBDA_H_BOOTSTRAP.md`
- `PROMPT.md` is a redirect only and must never contain an independent protocol copy.
- Canonical machine packet contract: `schema/lambda_h_packet.schema.json`
- Stdlib validation behavior: `src/validate_packet.py`
- Deterministic score/compact codec and region metrics: `src/lambda_h.py`
- Cross-model calibration probes: `calibration/probes.json`
- Cross-model calibration evaluator: `src/calibrate.py`
- `semantics.json` is retained as the earlier aggregate snapshot for compatibility.

When changing anchor order or meaning, increment the affected basis version instead of silently changing `01`.

## Known limitations

1. Prompt-only scoring is fuzzy across model families.
2. Session-local handles require synchronization.
3. Relation/action/tool bases are semantic anchors, not guarantees that every model will infer exactly the same projection.
4. Compact chat syntax is deterministic but intentionally narrower than JSON; free-form epistemic targets remain JSON-only.
5. `validate_packet.py` and `lambda_h.py` validate structure/transport, not semantic correctness.
6. The 32-dimensional entity basis is deliberately coarse. Nearby concepts can occupy almost the same region even when lexical identity differs.

## Planned contrastive entity residual

Do not solve the entity-resolution limit by adding a secret word dictionary. The intended future direction is versioned two-level entity representation:

```text
E = E0 + EΔ
```

`E0` is the current universal B_E/01 region. `EΔ` would be a task/session-induced contrastive subregion created only when several live concepts occupy the same coarse neighborhood. This is architectural work for a later protocol version, not part of ΛH/1 v1.0.

