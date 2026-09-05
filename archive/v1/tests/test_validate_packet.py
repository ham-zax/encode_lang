from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "src" / "validate_packet.py"
spec = importlib.util.spec_from_file_location("lambda_validate_packet", MODULE)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class ValidatePacketTests(unittest.TestCase):
    def test_valid_minimal_entity_packet(self):
        packet = {
            "protocol": "ΛH/1",
            "basis": {"E": "01"},
            "E": [{"handle": "η00", "q": "7" * 32, "u": 1}],
            "X": ["X02"],
        }
        self.assertEqual(validator.validate_packet(packet), [])

    def test_rejects_reserved_f_digit(self):
        packet = {
            "protocol": "ΛH/1",
            "E": [{"handle": "η00", "q": "F" + "7" * 31, "u": 1}],
        }
        errors = validator.validate_packet(packet)
        self.assertTrue(any("0-E" in error for error in errors))

    def test_rejects_unbound_relation_argument(self):
        packet = {
            "protocol": "ΛH/1",
            "E": [{"handle": "η00", "q": "7" * 32, "u": 1}],
            "R": [{
                "handle": "ρ00",
                "q": "7" * 16,
                "u": 1,
                "subject": "η00",
                "object": "η01",
            }],
        }
        errors = validator.validate_packet(packet)
        self.assertTrue(any("unbound entity handle η01" in error for error in errors))

    def test_rejects_bad_policy_width(self):
        packet = {"protocol": "ΛH/1", "P": {"q": "7" * 11, "u": 1}}
        errors = validator.validate_packet(packet)
        self.assertTrue(any("exactly 12" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
