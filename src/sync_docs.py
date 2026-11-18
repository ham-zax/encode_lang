"""Single-source-of-truth synchronization and drift checker for Lambda H/2.2.

Synchronizes generated documentation artifacts from code and semantics:
1. ``schema/lambda_h_packet.schema.json`` from ``src.protocol.schema()``.
2. ``## Shared semantic anchors`` in ``prompt/{ENCODER,DOER,DECODER}.md`` from
   ``semantics/basis.json`` in canonical layer order (E, R, A, T, K, V, X).
3. Verifies structural/documentation invariants across ``SPEC.md`` and the three
   role prompts (no active ``refs`` directive / root tag 13 reserved; 20-axis R/A;
   per-node ``v``; ``A.goal``; and ``C`` operators ``holds``, ``not``, ``all``, ``any``).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .protocol import LAYERS, schema

ROOT = Path(__file__).resolve().parents[1]
BASIS_PATH = ROOT / "semantics" / "basis.json"
SCHEMA_PATH = ROOT / "schema" / "lambda_h_packet.schema.json"
SPEC_PATH = ROOT / "SPEC.md"
ROLE_PROMPTS = (
    ROOT / "prompt" / "ENCODER.md",
    ROOT / "prompt" / "DOER.md",
    ROOT / "prompt" / "DECODER.md",
)

ANCHOR_ORDER = ("E", "R", "A", "T", "K", "V", "X")
EXPECTED_LAYER_COUNTS = {
    "E": LAYERS["E"],
    "R": LAYERS["R"],
    "A": LAYERS["A"],
    "T": LAYERS["T"],
    "K": 9,
    "V": LAYERS["V"],
    "X": 10,
}
ANCHORS_HEADING = "## Shared semantic anchors"


def expected_schema_text() -> str:
    """Return canonical JSON text for ``src.protocol.schema()``."""
    return json.dumps(schema(), ensure_ascii=False, indent=2) + "\n"


def load_basis(path: Path = BASIS_PATH) -> dict[str, dict[str, str]]:
    """Load and validate ``semantics/basis.json`` against expected axis counts."""
    basis = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(basis, dict):
        raise TypeError(f"{path}: root must be a JSON object")
    for layer in ANCHOR_ORDER:
        section = basis.get(layer)
        if not isinstance(section, dict):
            raise TypeError(f"{path}: missing or invalid layer {layer!r}")
        expected_keys = [f"{layer}{i:02d}" for i in range(EXPECTED_LAYER_COUNTS[layer])]
        actual_keys = list(section.keys())
        if actual_keys != expected_keys:
            raise ValueError(
                f"{path}: layer {layer} keys mismatch; expected {expected_keys[0]}..{expected_keys[-1]}, "
                f"got {actual_keys[:3]}..{actual_keys[-3:]}"
            )
        for key, desc in section.items():
            if not isinstance(desc, str) or not desc.strip():
                raise ValueError(f"{path}: empty description for {key}")
    return basis


def render_anchors_section(basis: dict[str, dict[str, str]]) -> str:
    """Render the deterministic ``## Shared semantic anchors`` markdown block."""
    blocks: list[str] = []
    for layer in ANCHOR_ORDER:
        lines = [f"{key} {basis[layer][key]}" for key in basis[layer]]
        blocks.append("\n".join(lines))
    body = "\n\n".join(blocks)
    return (
        f"{ANCHORS_HEADING}\n\n"
        "These are setup definitions of semantic directions, not word IDs. "
        "They are shared across all three roles.\n\n"
        "```text\n"
        f"{body}\n"
        "```\n"
    )


def _sync_file(path: Path, expected: str, *, check: bool, label: str) -> list[str]:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == expected:
        return []
    if check:
        return [f"{label}: out of sync with single source of truth ({path.relative_to(ROOT)})"]
    path.write_text(expected, encoding="utf-8")
    return []


def sync_schema(*, check: bool) -> list[str]:
    """Check or update ``schema/lambda_h_packet.schema.json``."""
    return _sync_file(SCHEMA_PATH, expected_schema_text(), check=check, label="schema")


def sync_prompt_anchors(path: Path, rendered_section: str, *, check: bool) -> list[str]:
    """Check or update the ``## Shared semantic anchors`` block of a role prompt."""
    rel = path.relative_to(ROOT)
    if not path.exists():
        return [f"{rel}: file not found"]
    text = path.read_text(encoding="utf-8")
    idx = text.find(ANCHORS_HEADING)
    if idx == -1:
        return [f"{rel}: missing {ANCHORS_HEADING!r} heading"]
    if idx > 0 and text[idx - 1] != "\n":
        return [f"{rel}: {ANCHORS_HEADING!r} must start at a line boundary"]
    expected = text[:idx] + rendered_section
    return _sync_file(path, expected, check=check, label=str(rel))


def verify_doc_invariants(path: Path) -> list[str]:
    """Verify structural tables and removed-directive invariants in spec/prompts."""
    rel = path.relative_to(ROOT)
    if not path.exists():
        return [f"{rel}: file not found"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if re.search(r"(?m)^\s*refs\b", text):
        errors.append(f"{rel}: advertises removed 'refs' IR directive line")
    if re.search(r"`refs`", text):
        errors.append(f"{rel}: mentions removed `refs` directive")
    if re.search(r"\b13\b[^\n]*(?:needed X references|\brefs\b)", text, re.IGNORECASE):
        errors.append(f"{rel}: documents root tag 13 as refs instead of reserved")
    if not re.search(r"\b13\b[^\n]*reserved", text, re.IGNORECASE):
        errors.append(f"{rel}: missing root tag 13 reserved documentation")

    if re.search(r"\bR/A/T\s*16\b|\bR16,\s*A16\b|\b(?:R|A)(?:\s+and\s+(?:R|A))?\s+(?:has|have)\s+16\b|\b(?:R16|A16)\s+axes\b", text):
        errors.append(f"{rel}: contains stale 16-axis reference for R or A")
    if not re.search(r"R\s+and\s+A\s+(?:have\s+)?20\b|R20,\s*A20", text):
        errors.append(f"{rel}: does not document 20 axes for R and A")

    # Join indented continuation lines (e.g. wrapped record rows in SPEC.md).
    unwrapped = re.sub(r"\n[ \t]+(?=[0-9]+ )", " ", text)
    node_checks = (
        ("E per-node v", r"E\s*[:|][^\n]*\b6\s+v\b"),
        ("R per-node v", r"R\s*[:|][^\n]*\b7\s+v\b"),
        ("A per-node v", r"A\s*[:|][^\n]*\b10\s+v\b"),
        ("A.goal", r"A\s*[:|][^\n]*\b11\s+goal(?:\s+ref)?\b"),
        ("T per-node v", r"T\s*[:|][^\n]*\b5\s+v\b"),
        ("C.args", r"C\s*[:|][^\n]*\b4\s+args(?:\s+refs)?\b"),
    )
    for label, pattern in node_checks:
        if not re.search(pattern, unwrapped):
            errors.append(f"{rel}: missing {label} in record tag table")

    cond_lines = [
        line for line in text.splitlines()
        if re.search(r"(?:condition\s*:|\|\s*C operator\s*\|)", line)
    ]
    if not cond_lines:
        errors.append(f"{rel}: missing C operator / condition enum definition")
    else:
        cond_text = "\n".join(cond_lines)
        for op_code, op_name in ((8, "holds"), (9, "not"), (10, "all"), (11, "any")):
            pattern = rf"(?:\b{op_code}\s+{op_name}\b|\b{op_name}\s*=\s*{op_code}\b)"
            if not re.search(pattern, cond_text):
                errors.append(f"{rel}: missing C operator '{op_name}' (code {op_code}) in condition enum")

    if not re.search(r"\bholds\b", text) or not re.search(r"\bargs\b", text):
        errors.append(f"{rel}: missing documentation for C combinators/holds")

    return errors


def run_sync(*, check: bool) -> list[str]:
    """Run all sync and invariant checks; return a list of diagnostics."""
    errors: list[str] = []
    basis = load_basis()
    rendered_anchors = render_anchors_section(basis)

    errors.extend(sync_schema(check=check))
    for prompt_path in ROLE_PROMPTS:
        errors.extend(sync_prompt_anchors(prompt_path, rendered_anchors, check=check))

    for doc_path in (SPEC_PATH, *ROLE_PROMPTS):
        errors.extend(verify_doc_invariants(doc_path))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify synchronization and doc invariants without modifying files",
    )
    args = parser.parse_args(argv)
    try:
        errors = run_sync(check=args.check)
    except (OSError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for err in errors:
            print(f"DRIFT: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
