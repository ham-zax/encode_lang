"""Tests for protocol schema/validation, numeric wire/rows, and symbolic IR."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.ir import IRError, format_ir, parse_ir
from src.protocol import PROTOCOL, ProtocolError, require_valid, schema, validate_packet
from src.rows import (
    MAX_BYTES,
    MAX_ROWS,
    RowCapacityError,
    RowError,
    format_rows,
    parse_rows,
    validate_rows_graph,
)
from src.wire import decode_graph, encode_graph

ROOT = Path(__file__).resolve().parents[1]


class TestProtocolSchemaAndExamples(unittest.TestCase):
    def test_schema_matches_checked_in_json(self) -> None:
        checked_in = json.loads((ROOT / "schema" / "lambda_h_packet.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema(), checked_in)

    def test_examples_round_trip_rows_and_ir(self) -> None:
        lh_files = sorted((ROOT / "examples").glob("*.lh"))
        self.assertTrue(lh_files, "expected at least one example .lh file")
        for path in lh_files:
            with self.subTest(example=path.name):
                text = path.read_text(encoding="utf-8")
                pkt = parse_rows(text)
                self.assertEqual(format_rows(pkt), text)
                self.assertEqual(parse_rows(format_rows(pkt)), pkt)
                ir_text = format_ir(pkt)
                self.assertEqual(parse_ir(ir_text), pkt)


class TestExtendedAxesFramingAndGoal(unittest.TestCase):
    def test_extended_r_a_axes_node_v_and_a_goal_round_trip(self) -> None:
        ir_text = (
            "LH-IR 2.2\n"
            "context 0\n"
            "mode message\n"
            "E e0 q 0:+3 31:-2 v 0:+1 7:-4\n"
            "R r0 q 16:+1 19:-7 subject e0 object X00 v 1:-2 6:+5\n"
            "A a0 q 16:+2 19:+7 target X08 goal e0 v 0:+3 7:+2\n"
            "T t0 q 0:+4 15:-3 v 2:+6 5:-1\n"
            "V 0:+2 7:-1\n"
        )
        pkt = parse_ir(ir_text)
        rows_text = format_rows(pkt)
        pkt_from_rows = parse_rows(rows_text)
        self.assertEqual(pkt_from_rows, pkt)
        ir_from_rows = format_ir(pkt_from_rows)
        self.assertEqual(parse_ir(ir_from_rows), pkt)
        self.assertEqual(pkt_from_rows["R"][0]["q"], {"R16": 1, "R19": -7})
        self.assertEqual(pkt_from_rows["A"][0]["q"], {"A16": 2, "A19": 7})
        self.assertEqual(pkt_from_rows["A"][0]["goal"], "e0")
        self.assertEqual(pkt_from_rows["E"][0]["v"], {"V00": 1, "V07": -4})
        self.assertEqual(pkt_from_rows["R"][0]["v"], {"V01": -2, "V06": 5})
        self.assertEqual(pkt_from_rows["A"][0]["v"], {"V00": 3, "V07": 2})
        self.assertEqual(pkt_from_rows["T"][0]["v"], {"V02": 6, "V05": -1})

    def test_out_of_range_extended_axes_rejected(self) -> None:
        for bad_ir in (
            "LH-IR 2.2\nE e0 q 0:+1\nR r0 q 20:+1 subject e0 object e0\n",
            "LH-IR 2.2\nE e0 q 0:+1\nA a0 q 20:+1 target e0\n",
            "LH-IR 2.2\nE e0 q 0:+1 v 8:+1\n",
        ):
            with self.subTest(bad_ir=bad_ir), self.assertRaises(IRError):
                parse_ir(bad_ir)


class TestConditionOperatorsAndCycles(unittest.TestCase):
    def test_all_condition_operators_round_trip(self) -> None:
        ir_text = (
            "LH-IR 2.2\n"
            "context 0\n"
            "mode message\n"
            "E e0 q 0:+1 value n:10\n"
            "E e1 q 1:+1 value n:20\n"
            "R r0 q 0:+2 subject e0 object e1\n"
            "A a0 q 0:+3 target e0 when c10 until c11\n"
            "C c0 op eq left e0 right e1\n"
            "C c1 op ne left e0 right e1\n"
            "C c2 op lt left e0 right e1\n"
            "C c3 op le left e0 right e1\n"
            "C c4 op gt left e0 right e1\n"
            "C c5 op ge left e0 right e1\n"
            "C c6 op exists left X00\n"
            "C c7 op done left a0\n"
            "C c8 op holds left r0\n"
            "C c9 op not left c6\n"
            "C c10 op all args c0 c2 c8\n"
            "C c11 op any args c7 c9\n"
        )
        pkt = parse_ir(ir_text)
        rows = format_rows(pkt)
        recovered = parse_rows(rows)
        self.assertEqual(recovered, pkt)
        self.assertEqual(parse_ir(format_ir(recovered)), pkt)

    def test_wrong_condition_operand_arity_and_types_rejected(self) -> None:
        base_nodes = {
            "protocol": PROTOCOL,
            "E": [{"id": "e0", "q": {"E00": 1}}],
            "R": [{"id": "r0", "q": {"R00": 1}, "subject": "e0", "object": "e0"}],
            "A": [{"id": "a0", "q": {"A00": 1}, "target": "e0"}],
        }
        invalid_cases = [
            [{"id": "c0", "op": "holds", "left": "e0"}],
            [{"id": "c0", "op": "holds", "left": "a0"}],
            [{"id": "c0", "op": "done", "left": "r0"}],
            [{"id": "c0", "op": "done", "left": "e0"}],
            [{"id": "c0", "op": "not", "left": "e0"}],
            [{"id": "c0", "op": "not", "left": "a0"}],
            [{"id": "c0", "op": "exists", "left": "e0"}, {"id": "c1", "op": "all", "args": ["c0"]}],
            [{"id": "c0", "op": "exists", "left": "e0"}, {"id": "c1", "op": "any", "args": ["c0"]}],
            [{"id": "c0", "op": "exists", "left": "e0"}, {"id": "c1", "op": "all", "left": "c0", "right": "c0"}],
            [{"id": "c0", "op": "exists", "left": "e0"}, {"id": "c1", "op": "all", "args": ["c0", "c0"]}],
            [{"id": "c0", "op": "exists", "left": "e0"}, {"id": "c1", "op": "eq", "left": "e0"}],
            [{"id": "c0", "op": "exists", "left": "e0"}, {"id": "c1", "op": "eq", "args": ["c0", "c0"]}],
            [{"id": "c0", "op": "exists", "left": "e0", "right": "e0"}],
        ]
        for conds in invalid_cases:
            pkt = {**base_nodes, "C": conds}
            with self.subTest(conds=conds):
                self.assertTrue(validate_packet(pkt))
                with self.assertRaises(ProtocolError):
                    require_valid(pkt)
                with self.assertRaises(RowError):
                    validate_rows_graph(pkt)

    def test_cyclic_conditions_rejected_with_code_3(self) -> None:
        pkt = {
            "protocol": PROTOCOL,
            "E": [{"id": "e0", "q": {"E00": 1}}],
            "C": [
                {"id": "c0", "op": "not", "left": "c1"},
                {"id": "c1", "op": "all", "args": ["c0", "c2"]},
                {"id": "c2", "op": "exists", "left": "e0"},
            ],
        }
        errors = validate_packet(pkt)
        self.assertTrue(any("C.cycle:" in err for err in errors), errors)
        with self.assertRaises(ProtocolError):
            require_valid(pkt)
        with self.assertRaises(RowError) as ctx:
            validate_rows_graph(pkt)
        self.assertEqual(ctx.exception.code, 3)

        ir_cycle = (
            "LH-IR 2.2\n"
            "E e0 q 0:+1\n"
            "C c0 op not left c1\n"
            "C c1 op all args c0 c2\n"
            "C c2 op exists left e0\n"
        )
        with self.assertRaises(IRError):
            parse_ir(ir_cycle)

        # Also verify raw numeric rows with cyclic conditions fail parse_rows with RowError(code=3).
        raw_rows = (
            "ΛH2.2|\n"
            "8 11\n"
            "1 2 0 0 0\n"
            "1 2 0 1 0 1\n"
            "1 6 0 0 0\n"
            "1 6 0 1 9\n"
            "1 6 0 2 4 1\n"
            "1 6 1 0 1\n"
            "1 6 1 1 10\n"
            "1 6 1 4 4 0 4 2\n"
            "1 6 2 0 2\n"
            "1 6 2 1 6\n"
            "1 6 2 2 0 0\n"
            "9 11\n"
        )
        with self.assertRaises(RowError) as row_ctx:
            parse_rows(raw_rows)
        self.assertEqual(row_ctx.exception.code, 3)


class TestActionCyclesTaskInvariantsAndRowCodes(unittest.TestCase):
    def _base_actions_and_entities(self) -> dict:
        return {
            "protocol": PROTOCOL,
            "E": [{"id": "e0", "q": {"E00": 1}}, {"id": "e1", "q": {"E01": 2}}],
            "A": [
                {"id": "a0", "q": {"A00": 1}, "target": "e0"},
                {"id": "a1", "q": {"A01": 1}, "target": "e0", "after": ["a0"]},
            ],
        }

    def test_valid_task_states_round_trip(self) -> None:
        base = self._base_actions_and_entities()
        valid_tasks = [
            {"id": "1", "revision": 0, "state": "active", "goal": "e0", "steps": ["a0", "a1"], "done": [], "next": "a0"},
            {"id": "1", "revision": 1, "state": "active", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"], "next": "a1"},
            {"id": "1", "revision": 2, "state": "complete", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0", "a1"]},
            {"id": "1", "revision": 2, "state": "blocked", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"], "blocker": "e1"},
            {"id": "1", "revision": 3, "state": "cancelled", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"]},
        ]
        for task in valid_tasks:
            pkt = {**base, "task": task}
            with self.subTest(state=task["state"], done=task["done"]):
                rows = format_rows(pkt)
                self.assertEqual(parse_rows(rows), pkt)
                self.assertEqual(parse_ir(format_ir(pkt)), pkt)

    def test_invalid_task_invariants_raise_row_error_code_3(self) -> None:
        base = self._base_actions_and_entities()
        invalid_tasks = [
            # active missing next
            {"id": "1", "revision": 0, "state": "active", "goal": "e0", "steps": ["a0", "a1"], "done": []},
            # active wrong next
            {"id": "1", "revision": 0, "state": "active", "goal": "e0", "steps": ["a0", "a1"], "done": [], "next": "a1"},
            # active with blocker
            {"id": "1", "revision": 0, "state": "active", "goal": "e0", "steps": ["a0", "a1"], "done": [], "next": "a0", "blocker": "e1"},
            # complete with missing done step
            {"id": "1", "revision": 1, "state": "complete", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"]},
            # complete with next
            {"id": "1", "revision": 1, "state": "complete", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0", "a1"], "next": "a1"},
            # blocked missing blocker
            {"id": "1", "revision": 1, "state": "blocked", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"]},
            # blocked with next
            {"id": "1", "revision": 1, "state": "blocked", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"], "next": "a1", "blocker": "e1"},
            # cancelled with next
            {"id": "1", "revision": 1, "state": "cancelled", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"], "next": "a1"},
            # cancelled with blocker
            {"id": "1", "revision": 1, "state": "cancelled", "goal": "e0", "steps": ["a0", "a1"], "done": ["a0"], "blocker": "e1"},
            # prerequisite order violated in steps
            {"id": "1", "revision": 0, "state": "active", "goal": "e0", "steps": ["a1", "a0"], "done": [], "next": "a1"},
            # done step missing prerequisite
            {"id": "1", "revision": 1, "state": "active", "goal": "e0", "steps": ["a0", "a1"], "done": ["a1"], "next": "a0"},
            # done contains action outside steps
            {"id": "1", "revision": 1, "state": "complete", "goal": "e0", "steps": ["a0"], "done": ["a0", "a1"]},
        ]
        for task in invalid_tasks:
            pkt = {**base, "task": task}
            with self.subTest(task=task):
                with self.assertRaises(RowError) as ctx:
                    validate_rows_graph(pkt)
                self.assertEqual(ctx.exception.code, 3)

    def test_action_after_cycle_raises_row_error_code_3(self) -> None:
        pkt = {
            "protocol": PROTOCOL,
            "E": [{"id": "e0", "q": {"E00": 1}}],
            "A": [
                {"id": "a0", "q": {"A00": 1}, "target": "e0", "after": ["a1"]},
                {"id": "a1", "q": {"A01": 1}, "target": "e0", "after": ["a0"]},
            ],
        }
        with self.assertRaises(RowError) as ctx:
            validate_rows_graph(pkt)
        self.assertEqual(ctx.exception.code, 3)

        raw_rows = (
            "ΛH2.2|\n"
            "8 10\n"
            "1 2 0 0 0\n"
            "1 2 0 1 0 1\n"
            "1 4 0 0 0\n"
            "1 4 0 1 0 1\n"
            "1 4 0 4 0 0\n"
            "1 4 0 6 2 1\n"
            "1 4 1 0 1\n"
            "1 4 1 1 1 1\n"
            "1 4 1 4 0 0\n"
            "1 4 1 6 2 0\n"
            "9 10\n"
        )
        with self.assertRaises(RowError) as row_ctx:
            parse_rows(raw_rows)
        self.assertEqual(row_ctx.exception.code, 3)

    def test_row_error_codes_0_and_1(self) -> None:
        unbound_pkt = {
            "protocol": PROTOCOL,
            "A": [{"id": "a0", "q": {"A00": 1}, "target": "e99"}],
        }
        with self.assertRaises(RowError) as ctx1:
            validate_rows_graph(unbound_pkt)
        self.assertEqual(ctx1.exception.code, 1)

        raw_unbound = (
            "ΛH2.2|\n"
            "8 3\n"
            "1 4 0 0 0\n"
            "1 4 0 1 0 1\n"
            "1 4 0 4 0 99\n"
            "9 3\n"
        )
        with self.assertRaises(RowError) as row_ctx1:
            parse_rows(raw_unbound)
        self.assertEqual(row_ctx1.exception.code, 1)

        shape_pkt = {"protocol": PROTOCOL, "E": []}
        with self.assertRaises(RowError) as ctx0:
            validate_rows_graph(shape_pkt)
        self.assertEqual(ctx0.exception.code, 0)

        with self.assertRaises(RowError) as row_ctx0:
            parse_rows("ΛH2.2|\n8 1\n0 0 1\n9 2\n")
        self.assertEqual(row_ctx0.exception.code, 0)


class TestReservedTagsDeadDirectivesAndLimits(unittest.TestCase):
    def test_root_tag_13_rejected_on_wire_and_rows(self) -> None:
        with self.assertRaises(ProtocolError):
            decode_graph([[13, [[5, 0]]]])
        with self.assertRaises(RowError):
            parse_rows("ΛH2.2|\n8 1\n0 13 5 0\n9 1\n")

    def test_dead_refs_directive_rejected_in_parse_ir(self) -> None:
        with self.assertRaises(IRError):
            parse_ir("LH-IR 2.2\ncontext 0\nrefs X00\nE e0 q 0:+1\n")

    def test_capacity_limits_max_rows_and_max_bytes(self) -> None:
        with self.assertRaises(RowCapacityError):
            parse_rows("ΛH2.2|\n8 0\n" + ("0 0 1\n" * (MAX_ROWS + 1)) + "9 0\n")
        with self.assertRaises(RowCapacityError):
            parse_rows(f"ΛH2.2|\n8 {MAX_ROWS + 1}\n9 {MAX_ROWS + 1}\n")
        with self.assertRaises(RowCapacityError):
            parse_rows("ΛH2.2|\n" + ("x" * (MAX_BYTES + 1)))

        many_entities = [{"id": f"e{i}", "q": {"E00": 1}} for i in range(MAX_ROWS // 2 + 10)]
        with self.assertRaises(RowCapacityError):
            format_rows({"protocol": PROTOCOL, "E": many_entities})

    def test_lexical_limits_leading_zeros_nonfinite_blank_lines_duplicate_tags(self) -> None:
        # Leading zeros in rows and IR
        for bad_rows in (
            "ΛH2.2|\n8 01\n0 0 1\n9 01\n",
            "ΛH2.2|\n8 1\n0 00 1\n9 1\n",
            "ΛH2.2|\n8 1\n0 14 01\n9 1\n",
        ):
            with self.subTest(bad_rows=bad_rows), self.assertRaises(RowError):
                parse_rows(bad_rows)

        for bad_ir in (
            "LH-IR 2.2\ncontext 01\nE e0 q 0:+1\n",
            "LH-IR 2.2\nE e0 q 0:+1 value n:01\n",
        ):
            with self.subTest(bad_ir=bad_ir), self.assertRaises(IRError):
                parse_ir(bad_ir)

        # Non-finite numbers in rows, IR, and wire
        for bad_rows in (
            "ΛH2.2|\n8 1\n0 14 NaN\n9 1\n",
            "ΛH2.2|\n8 1\n0 14 Infinity\n9 1\n",
        ):
            with self.subTest(bad_rows=bad_rows), self.assertRaises(RowError):
                parse_rows(bad_rows)
        for bad_ir in (
            "LH-IR 2.2\nE e0 q 0:+1 value n:NaN\n",
            "LH-IR 2.2\nE e0 q 0:+1 value n:Infinity\n",
        ):
            with self.subTest(bad_ir=bad_ir), self.assertRaises(IRError):
                parse_ir(bad_ir)
        with self.assertRaises(ProtocolError):
            decode_graph([[12, 1], [14, float("nan")]])
        with self.assertRaises(ProtocolError):
            encode_graph({"protocol": PROTOCOL, "E": [{"id": "e0", "q": {"E00": 1}, "value": float("inf")}]})

        # Blank line in data rows
        with self.assertRaises(RowError):
            parse_rows("ΛH2.2|\n8 2\n0 0 1\n\n9 2\n")

        # Duplicate tags in rows and wire
        with self.assertRaises(RowError):
            parse_rows("ΛH2.2|\n8 2\n0 0 1\n0 0 2\n9 2\n")
        with self.assertRaises(ProtocolError):
            decode_graph([[12, 0], [12, 0]])

    def test_unreferenced_inline_x_message_vs_bind_mode(self) -> None:
        unreferenced_msg = {
            "protocol": PROTOCOL,
            "context": "0",
            "mode": "message",
            "E": [{"id": "e0", "q": {"E00": 1}}],
            "X": {"X00": 42},
        }
        with self.assertRaises(ProtocolError):
            encode_graph(unreferenced_msg)
        with self.assertRaises(ProtocolError):
            format_rows(unreferenced_msg)

        bind_pkt = {
            "protocol": PROTOCOL,
            "context": "0",
            "mode": "bind",
            "X": {"X00": 42, "X1A": True, "XFF": None},
        }
        wire = encode_graph(bind_pkt)
        self.assertEqual(decode_graph(wire), bind_pkt)
        rows = format_rows(bind_pkt)
        self.assertEqual(parse_rows(rows), bind_pkt)
        self.assertEqual(parse_ir(format_ir(bind_pkt)), bind_pkt)

        bad_bind = {
            "protocol": PROTOCOL,
            "context": "0",
            "mode": "bind",
            "E": [{"id": "e0", "q": {"E00": 1}}],
            "X": {"X00": 42},
        }
        with self.assertRaises(ProtocolError):
            require_valid(bad_bind)


if __name__ == "__main__":
    unittest.main()
