from __future__ import annotations

import unittest

from src.lambda_h import compare_q, format_compact, parse_compact


class LambdaHCodecTests(unittest.TestCase):
    def test_compare_q_identity(self):
        q = "D5E4C387777453674974479543387479"
        metrics = compare_q(q, q, width=32)
        self.assertEqual(metrics["mean_abs_delta"], 0.0)
        self.assertEqual(metrics["rmse"], 0.0)
        self.assertEqual(metrics["cosine"], 1.0)

    def test_full_compact_round_trip_with_k(self):
        e = "7" * 32
        r = "7" * 16
        a = "7" * 16
        t = "7" * 16
        p = "7" * 12
        v = "7" * 8
        wire = (
            f"ΛH1|E=00.{e}.1,01.{e}.2|"
            f"R=00.{r}.1(01,00),01.{r}.2(00,01)|"
            f"A=00.{a}.1|T=00.{t}.1|K=R00:K03:0.42|"
            f"P={p}.2|X=02|V={v}.1"
        )
        packet = parse_compact(wire)
        self.assertEqual(packet["K"][0]["target"], "ρ00")
        self.assertEqual(format_compact(packet), wire)

    def test_multi_relation_parser_preserves_argument_order(self):
        e = "7" * 32
        r = "7" * 16
        wire = (
            f"ΛH1|E=00.{e}.1,01.{e}.1,02.{e}.1|"
            f"R=00.{r}.1(01,00),01.{r}.1(01,02)"
        )
        packet = parse_compact(wire)
        self.assertEqual(len(packet["R"]), 2)
        self.assertEqual(packet["R"][0]["subject"], "η01")
        self.assertEqual(packet["R"][0]["object"], "η00")
        self.assertEqual(packet["R"][1]["subject"], "η01")
        self.assertEqual(packet["R"][1]["object"], "η02")

    def test_control_frames_round_trip(self):
        e = "7" * 32
        frames = [
            "ΛH1|SYNC?",
            f"ΛH1|SYNC|E=00.{e}.1",
            "ΛH1|ACK|E=00,01|R=00(01,00)|A=00|T=00",
            "ΛH1|READY|BE=01|BR=01|BA=01|BT=01|BP=02|BV=01",
            "ΛH1|CALFAIL",
        ]
        for frame in frames:
            with self.subTest(frame=frame):
                self.assertEqual(format_compact(parse_compact(frame)), frame)

    def test_legacy_bracketed_ack_is_accepted_but_canonicalized(self):
        packet = parse_compact("ΛH1|ACK|E=[00,01]|R=[00(01,00)]")
        self.assertEqual(format_compact(packet), "ΛH1|ACK|E=00,01|R=00(01,00)")


if __name__ == "__main__":
    unittest.main()
