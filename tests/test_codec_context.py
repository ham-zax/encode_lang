"""Tests for src.codec (API + CLI) and src.context resolution/isolation."""
from __future__ import annotations

import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.codec import (
    RECIPES,
    explain_packet,
    fix_packet,
    format_packet,
    lint_packet,
    parse_packet,
    preflight_packet,
    recipe_packet,
)
from src.context import (
    AMBIENT_REFS,
    AMBIENT_ROLES,
    CURRENT_CONTEXT,
    HostContext,
    ambient_ref,
    load_host_context,
    preflight_context,
    resolve_context,
)
from src.ir import format_ir, parse_ir
from src.protocol import PROTOCOL, ProtocolError
from src.rows import parse_rows

ROOT = Path(__file__).resolve().parents[1]


def _run_codec(*args: str, stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "src.codec", *args],
        input=stdin_text,
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=False,
    )


class TestCodecPythonApiAndCli(unittest.TestCase):
    def test_python_api_round_trips_and_commands(self) -> None:
        field_lh = (ROOT / "examples" / "field.lh").read_text(encoding="utf-8")
        pkt = parse_packet(field_lh)
        self.assertEqual(format_packet(pkt), field_lh)

        ir_text = format_ir(pkt)
        self.assertEqual(parse_ir(ir_text), pkt)

        lint_out = lint_packet(field_lh)
        self.assertTrue(lint_out.startswith("OK: 10 data rows"))

        # Broken frame counts repaired by fix_packet.
        broken = field_lh.replace("8 10", "8 99").replace("9 10", "9 42")
        self.assertEqual(fix_packet(broken), field_lh)

        # Recipes all produce valid numeric packets.
        for name in RECIPES:
            with self.subTest(recipe=name):
                rec_rows = recipe_packet(name)
                rec_pkt = parse_packet(rec_rows)
                self.assertEqual(format_packet(rec_pkt), rec_rows)
        with self.assertRaises(ProtocolError):
            recipe_packet("not-a-recipe")

        # preflight_packet accepts both numeric rows and LH-IR 2.2.
        bounty_lh = (ROOT / "examples" / "bounty-continue.lh").read_text(encoding="utf-8")
        host_ctx = HostContext("1", {"X02": "finish-audit"})
        pf_rows = json.loads(preflight_packet(bounty_lh, host_context=host_ctx))
        pf_ir = json.loads(preflight_packet(format_ir(parse_packet(bounty_lh)), host_context=host_ctx))
        self.assertEqual(pf_rows, pf_ir)
        self.assertEqual(pf_rows["classifications"]["X02"], "host-ambient-resolvable")
        self.assertEqual(pf_rows["resolved"]["X02"], "finish-audit")
        self.assertTrue(pf_rows["complete"])
        self.assertEqual(pf_rows["unresolved"], [])

    def test_cli_all_subcommands_succeed(self) -> None:
        field_path = ROOT / "examples" / "field.lh"
        field_lh = field_path.read_text(encoding="utf-8")
        continue_path = ROOT / "examples" / "continue.lh"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            ir_path = tmp_dir / "sample.ir"
            ctx_path = tmp_dir / "ctx.json"
            ir_path.write_text(format_ir(parse_packet(field_lh)), encoding="utf-8")
            ctx_path.write_text(json.dumps({"context": "1", "bindings": {"X02": "/tmp/goal"}}), encoding="utf-8")

            # encode
            enc = _run_codec("encode", str(ir_path))
            self.assertEqual(enc.returncode, 0, enc.stderr)
            self.assertEqual(enc.stdout, field_lh)

            # decode
            dec = _run_codec("decode", str(field_path))
            self.assertEqual(dec.returncode, 0, dec.stderr)
            self.assertEqual(parse_ir(dec.stdout), parse_packet(field_lh))

            # format
            fmt = _run_codec("format", "-", stdin_text=field_lh)
            self.assertEqual(fmt.returncode, 0, fmt.stderr)
            self.assertEqual(fmt.stdout, field_lh)

            # explain with --context
            exp = _run_codec("explain", str(continue_path), "--context", str(ctx_path))
            self.assertEqual(exp.returncode, 0, exp.stderr)
            self.assertIn("X02 [host-ambient-resolvable]: '/tmp/goal'", exp.stdout)

            # lint with --context
            lnt = _run_codec("lint", str(continue_path), "--context", str(ctx_path))
            self.assertEqual(lnt.returncode, 0, lnt.stderr)
            self.assertIn("X bindings: complete", lnt.stdout)

            # fix
            broken = field_lh.replace("8 10", "8 2")
            fx = _run_codec("fix", "-", stdin_text=broken)
            self.assertEqual(fx.returncode, 0, fx.stderr)
            self.assertEqual(fx.stdout, field_lh)

            # recipe
            rcp = _run_codec("recipe", "diagnose")
            self.assertEqual(rcp.returncode, 0, rcp.stderr)
            self.assertTrue(rcp.stdout.startswith("ΛH2.2|\n"))

            # preflight
            pf = _run_codec("preflight", str(continue_path), "--context", str(ctx_path))
            self.assertEqual(pf.returncode, 0, pf.stderr)
            pf_json = json.loads(pf.stdout)
            self.assertTrue(pf_json["complete"])
            self.assertEqual(pf_json["resolved"], {"X02": "/tmp/goal"})

    def test_cli_error_path_stdout_purity(self) -> None:
        malformed_rows = "ΛH2.2|\n8 1\n0 99 1\n9 1\n"
        malformed_ir = "LH-IR 2.2\nunknown_directive 1\n"

        for cmd, stdin_text, extra in (
            ("decode", malformed_rows, ()),
            ("explain", malformed_rows, ()),
            ("lint", malformed_rows, ()),
            ("fix", malformed_rows, ()),
            ("preflight", malformed_rows, ()),
            ("recipe", None, ("no_such_recipe",)),
        ):
            with self.subTest(cmd=cmd):
                arg = extra[0] if extra else "-"
                proc = _run_codec(cmd, arg, stdin_text=stdin_text)
                self.assertEqual(proc.returncode, 2)
                self.assertIn("ERROR", proc.stderr)
                self.assertEqual(proc.stdout, "")

        for cmd, stdin_text, expected_code in (
            ("encode", malformed_ir, 0),
            ("format", malformed_rows, 0),
            # format on unbound local ref reports RowError code 1 in control frame
            ("format", "ΛH2.2|\n8 3\n1 4 0 0 0\n1 4 0 1 0 1\n1 4 0 4 0 99\n9 3\n", 1),
        ):
            with self.subTest(cmd=cmd, expected_code=expected_code):
                proc = _run_codec(cmd, "-", stdin_text=stdin_text)
                self.assertEqual(proc.returncode, 2)
                self.assertIn("ERROR", proc.stderr)
                self.assertTrue(proc.stdout.startswith("ΛH2.2|\n"))
                ctrl = parse_rows(proc.stdout)
                self.assertEqual(
                    ctrl,
                    {"protocol": PROTOCOL, "control": "invalid", "code": expected_code},
                )

    def test_cli_output_flag_permissions_and_no_overwrite(self) -> None:
        field_lh = (ROOT / "examples" / "field.lh").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            out_path = tmp_dir / "out.lh"
            proc = _run_codec("format", str(ROOT / "examples" / "field.lh"), "--output", str(out_path))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout, "")
            self.assertEqual(out_path.read_text(encoding="utf-8"), field_lh)
            self.assertEqual(stat.S_IMODE(out_path.stat().st_mode), 0o600)

            # Refuses to overwrite existing file and leaves existing contents intact.
            out_path.write_text("sentinel", encoding="utf-8")
            proc2 = _run_codec("format", str(ROOT / "examples" / "field.lh"), "--output", str(out_path))
            self.assertEqual(proc2.returncode, 2)
            self.assertIn("ERROR", proc2.stderr)
            self.assertEqual(out_path.read_text(encoding="utf-8"), "sentinel")


class TestExplainPacket(unittest.TestCase):
    def test_explain_renders_field_components_on_field_lh(self) -> None:
        field_lh = (ROOT / "examples" / "field.lh").read_text(encoding="utf-8")
        out = explain_packet(field_lh)
        self.assertIn("Field[0] (s=2):", out)
        self.assertIn("E20 (+4):", out)
        self.assertIn("E21 (+3):", out)
        self.assertIn("Bands (b): E20=[1, 2]", out)
        self.assertIn("Uncertainty: u=4/7", out)

    def test_explain_renders_rich_nodes_fields_conditions_framing_and_x(self) -> None:
        ir_text = (
            "LH-IR 2.2\n"
            "context 0\n"
            "mode message\n"
            "E e0 q 0:+3 u 2 value n:12.5 v 0:+1\n"
            "E e1 choices n:1 n:2 b:1 u 5 v 1:-3\n"
            "F E e1 0 q 2:+4 3:-2 s 2 b 2:1:3 w 0.75\n"
            "R r0 q 0:+2 subject e0 object X00 v 2:+4\n"
            "T t0 q 5:+6 u 1 value b:1 v 3:-2\n"
            "A a0 q 0:+4 u 3 target X08 goal e0 tool t0 when c3 until c4 v 4:+5\n"
            "C c0 op exists left X00\n"
            "C c1 op holds left r0\n"
            "C c2 op not left c0\n"
            "C c3 op all args c0 c1\n"
            "C c4 op any args c1 c2\n"
            "X X00 n:99\n"
            "V 0:+2 7:-5\n"
        )
        rows = format_packet(parse_ir(ir_text))
        host_ctx = HostContext.current({"X08": "/srv/repo"})
        out = explain_packet(rows, host_context=host_ctx)

        # Field components q, s, b, w
        self.assertIn("Field[0] (s=2, w=0.75):", out)
        self.assertIn("E02 (+4):", out)
        self.assertIn("E03 (-2):", out)
        self.assertIn("Bands (b): E02=[1, 3]", out)

        # u, per-node v, root V
        self.assertIn("Uncertainty: u=2/7", out)
        self.assertIn("Uncertainty: u=5/7", out)
        self.assertIn("Uncertainty: u=1/7", out)
        self.assertIn("Uncertainty: u=3/7", out)
        self.assertIn("Framing (V):", out)
        self.assertIn("V00 (+1):", out)
        self.assertIn("V01 (-3):", out)
        self.assertIn("V02 (+4):", out)
        self.assertIn("V03 (-2):", out)
        self.assertIn("V04 (+5):", out)
        self.assertIn("V07 (-5):", out)

        # E.value, E.choices, T.value
        self.assertIn("Value: 12.5", out)
        self.assertIn("Choices: 1, 2, True", out)
        self.assertIn("Value: True", out)

        # A.goal, A.when, A.until
        self.assertIn("Goal: e0 [", out)
        self.assertIn("When: c3 [all(c0, c1)]", out)
        self.assertIn("Until: c4 [any(c1, c2)]", out)

        # C operators
        self.assertIn("Condition c0: exists(X00)", out)
        self.assertIn("Condition c1: holds(r0)", out)
        self.assertIn("Condition c2: not(c0)", out)
        self.assertIn("Condition c3: all(c0, c1)", out)
        self.assertIn("Condition c4: any(c1, c2)", out)

        # X bindings and HostContext resolution
        self.assertIn("Packet X Bindings:", out)
        self.assertIn("X00 = 99", out)
        self.assertIn("X00 [packet-bound]: 99", out)
        self.assertIn("X08 [host-ambient-resolvable]: '/srv/repo'", out)

    def test_explain_renders_unresolved_and_namespace_mismatch(self) -> None:
        bounty_lh = (ROOT / "examples" / "bounty-continue.lh").read_text(encoding="utf-8")
        out_no_ctx = explain_packet(bounty_lh)
        self.assertIn("Unresolved X refs: X02", out_no_ctx)

        wrong_ns = HostContext("7", {"X02": "other-goal"})
        out_mismatch = explain_packet(bounty_lh, host_context=wrong_ns)
        self.assertIn("Namespace mismatch: packet context=1 != host namespace=7", out_mismatch)
        self.assertIn("Unresolved X refs: X02", out_mismatch)


class TestHostContextAndResolution(unittest.TestCase):
    def test_host_context_loaders_and_ambient_ref(self) -> None:
        for role, ref in AMBIENT_ROLES.items():
            self.assertEqual(ambient_ref(role), ref)
            self.assertIn(ref, AMBIENT_REFS)
        with self.assertRaises(ValueError):
            ambient_ref("unknown-role")

        raw = load_host_context({"X00": "subj", "X08": "/repo"})
        self.assertEqual(raw.namespace, CURRENT_CONTEXT)
        self.assertEqual(dict(raw.bindings), {"X00": "subj", "X08": "/repo"})

        structured = load_host_context({"context": "42", "bindings": {"X02": "goal"}})
        self.assertEqual(structured.namespace, "42")
        self.assertEqual(dict(structured.bindings), {"X02": "goal"})

        with self.assertRaises(ProtocolError):
            load_host_context({"context": "1", "namespace": "2", "bindings": {"X00": 1}})
        with self.assertRaises(ProtocolError):
            load_host_context({"bindings": {"X00": 1}, "extra": 1})
        with self.assertRaises(ProtocolError):
            load_host_context({"bad_key": 1})

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            valid_file = tmp_dir / "ctx.json"
            valid_file.write_text(json.dumps({"namespace": "3", "bindings": {"X00": "v"}}), encoding="utf-8")
            loaded = HostContext.from_file(valid_file)
            self.assertEqual(loaded.namespace, "3")
            self.assertEqual(loaded.bindings["X00"], "v")

            dup_file = tmp_dir / "dup.json"
            dup_file.write_text('{"X00": 1, "X00": 2}', encoding="utf-8")
            with self.assertRaises(ProtocolError):
                HostContext.from_file(dup_file)

            nan_file = tmp_dir / "nan.json"
            nan_file.write_text('{"X00": NaN}', encoding="utf-8")
            with self.assertRaises(ProtocolError):
                HostContext.from_file(nan_file)

    def test_context_precedence_order(self) -> None:
        def make_pkt(*, inline_x: dict | None = None, context: str = "0") -> dict:
            pkt: dict = {
                "protocol": PROTOCOL,
                "context": context,
                "A": [{"id": "a0", "q": {"A00": 1}, "target": "X00"}],
            }
            if inline_x is not None:
                pkt["X"] = inline_x
            return pkt

        host = HostContext.current({"X00": "from-host"})

        # 1. packet-bound > host-ambient-resolvable > conversation-ambient-resolvable
        pf1 = preflight_context(make_pkt(inline_x={"X00": 123}), host, current_subject="from-conv")
        res1 = resolve_context(make_pkt(inline_x={"X00": 123}), host, current_subject="from-conv")
        self.assertEqual(dict(pf1.classifications), {"X00": "packet-bound"})
        self.assertEqual(dict(res1.resolved), {"X00": 123})
        self.assertTrue(pf1.complete and res1.complete)

        # 2. host-ambient-resolvable > conversation-ambient-resolvable
        pf2 = preflight_context(make_pkt(), host, current_subject="from-conv")
        res2 = resolve_context(make_pkt(), host, current_subject="from-conv")
        self.assertEqual(dict(pf2.classifications), {"X00": "host-ambient-resolvable"})
        self.assertEqual(dict(res2.resolved), {"X00": "from-host"})

        # 3. conversation-ambient-resolvable > unresolved
        pf3 = preflight_context(make_pkt(), HostContext.current({}), current_subject="from-conv")
        res3 = resolve_context(make_pkt(), HostContext.current({}), current_subject="from-conv")
        self.assertEqual(dict(pf3.classifications), {"X00": "conversation-ambient-resolvable"})
        self.assertEqual(dict(res3.resolved), {"X00": "from-conv"})

        # 4. unresolved
        pf4 = preflight_context(make_pkt(), None)
        res4 = resolve_context(make_pkt(), None)
        self.assertEqual(dict(pf4.classifications), {"X00": "unresolved"})
        self.assertEqual(pf4.unresolved, ("X00",))
        self.assertEqual(res4.missing, ("X00",))
        self.assertFalse(pf4.complete or res4.complete)

    def test_strict_nonzero_namespace_isolation(self) -> None:
        pkt = {
            "protocol": PROTOCOL,
            "context": "5",
            "A": [
                {"id": "a0", "q": {"A00": 1}, "target": "X00"},
                {"id": "a1", "q": {"A01": 1}, "target": "X08"},
            ],
            "X": {"X08": 7},
        }
        # Host namespace 0 and current_subject must NOT bleed into nonzero packet namespace 5.
        host_zero = HostContext.current({"X00": "ambient-zero", "X08": "wrong"})
        pf_iso = preflight_context(pkt, host_zero, current_subject="conv-zero")
        res_iso = resolve_context(pkt, host_zero, current_subject="conv-zero")
        self.assertEqual(dict(pf_iso.classifications), {"X08": "packet-bound", "X00": "unresolved"})
        self.assertEqual(pf_iso.unresolved, ("X00",))
        self.assertEqual(dict(res_iso.resolved), {"X08": 7})
        self.assertEqual(res_iso.missing, ("X00",))

        # Host namespace 5 resolves X00, while packet-bound X08 still takes precedence.
        host_five = HostContext("5", {"X00": "ns5-subj", "X08": "ns5-ignored"})
        pf_match = preflight_context(pkt, host_five, current_subject="conv-zero")
        res_match = resolve_context(pkt, host_five, current_subject="conv-zero")
        self.assertEqual(
            dict(pf_match.classifications),
            {"X08": "packet-bound", "X00": "host-ambient-resolvable"},
        )
        self.assertTrue(pf_match.complete and res_match.complete)
        self.assertEqual(dict(res_match.resolved), {"X08": 7, "X00": "ns5-subj"})

        # Control packet requires no X bindings.
        ctrl = {"protocol": PROTOCOL, "control": "ready"}
        self.assertTrue(preflight_context(ctrl, host_zero).complete)
        self.assertEqual(dict(resolve_context(ctrl, host_zero).resolved), {})


if __name__ == "__main__":
    unittest.main()
