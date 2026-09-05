"""Reusable Python package for the ΛH/1 semantic-transfer codec."""

from __future__ import annotations

from typing import Any

__all__ = [
    "CodecError",
    "compare_q",
    "decode_q",
    "encode_scores",
    "format_compact",
    "parse_compact",
    "validate_packet",
]


def __getattr__(name: str) -> Any:
    if name == "validate_packet":
        from .validate_packet import validate_packet

        return validate_packet
    if name in {"CodecError", "compare_q", "decode_q", "encode_scores", "format_compact", "parse_compact"}:
        from . import lambda_h

        return getattr(lambda_h, name)
    raise AttributeError(name)
