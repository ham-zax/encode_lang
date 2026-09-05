# ΛH/1 Project Notes

## Mission

Create a prompt-portable semantic interchange language that can be loaded into a fresh AI session without external model weights or a word lookup table.

The design is inspired by the idea of constructing task-specific representations and preserving structured state rather than relying only on surface wording. The project deliberately separates semantic kinds instead of forcing everything into one opaque vector.

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
- Full AI bootstrap: `prompt/LAMBDA_H_BOOTSTRAP.md`
- Canonical machine packet contract: `schema/lambda_h_packet.schema.json`
- Stdlib validation behavior: `src/validate_packet.py`
- Deterministic score/compact codec: `src/lambda_h.py`
- `semantics.json` is retained as the earlier aggregate snapshot for compatibility.

When changing anchor order or meaning, increment the affected basis version instead of silently changing `01`.

## Known limitations

1. Prompt-only scoring is fuzzy across model families.
2. Opaque codes are not encryption.
3. Session-local handles require synchronization.
4. Relation/action/tool bases are semantic anchors, not guarantees that every model will infer exactly the same projection.
5. Compact chat syntax is deterministic but intentionally narrower than JSON; free-form epistemic targets remain JSON-only.
6. `validate_packet.py` and `lambda_h.py` validate structure/transport, not semantic correctness.

## Safety invariant

Representation does not change policy treatment. Encoded intent carries exactly the same authorization and safety requirements as equivalent plain language.
