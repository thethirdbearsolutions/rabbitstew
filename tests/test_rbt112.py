"""RBT-112's design scripts: the arm is one flag from HU; the S = 0 arm is read against its own operator's table;
F12's resting drive; the pre-registered rules (runs/RBT-112/)."""
import importlib.util
import json
import math
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "runs", "RBT-112")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_hz_is_hu_plus_exactly_one_flag():
    c112 = _load("t112_command", "runs/RBT-112/command.py")
    c106 = _load("t112_c106", "runs/RBT-106/command.py")
    for seed in (801, 4):
        hz = c112.command("HZ", seed, "OUT")
        hu = c106.command("HU", seed, "OUT")
        assert hz[:len(hu)] == hu and hz[len(hu):] == ["--global-bias-sigma", "0"]
    from rabbitstew.cli import build_parser
    a = build_parser().parse_args(c112.command("HZ", 801, "OUT")[3:])
    assert a.global_bias_sigma == 0.0 and a.crossover == 0.3 and a.link_scale == 1.0


def test_held_reads_the_arm_against_its_own_operator(tmp_path):
    h = _load("t112_held", "runs/RBT-112/held.py")
    for gbs, want in ((None, os.path.join("RBT-106", "baseline", "baseline-w32-801.txt")),
                      (0.0, os.path.join("RBT-112", "baseline", "baseline-w32-S0-801.txt"))):
        run = tmp_path / f"r{gbs}"
        run.mkdir()
        mut = {} if gbs is None else {"global_bias_sigma": gbs}
        (run / "config.json").write_text(json.dumps({"mutation": mut}))
        path = h.table_for(str(run))(801, 32.0)
        assert path.endswith(want) and os.path.exists(path)
    run = tmp_path / "r2"
    run.mkdir()
    (run / "config.json").write_text(json.dumps({"mutation": {"global_bias_sigma": 0.2}}))
    with pytest.raises(SystemExit):
        h.table_for(str(run))


def test_s0_table_holds_longer_than_the_default_at_every_depth():
    """The committed baseline: at S = 0 the pay32 column never falls below the default's (paired lineages)."""
    er = _load("t112_erasure", "runs/RBT-112/erasure.py")
    Dt, Z = er.load(""), er.load("-S0")
    for d in range(41):
        assert er.f(Z, "pay32", d) >= er.f(Dt, "pay32", d)
    assert er.decide(0.089).startswith("u <= 0.12") and er.decide(0.12).startswith("u <= 0.12")
    assert er.decide(0.2).startswith("u >= 0.20") and "GREY" in er.decide(0.15)


def test_resting_drive_transfer_and_read():
    r = _load("t112_resting", "runs/RBT-112/resting.py")
    assert r.transfer("tanh", 0.0) == 0.0 and math.isclose(r.transfer("tanh", 0.3), math.tanh(0.3))
    assert r.transfer("differentiate", 0.7) == 0.0 and r.transfer("integrate", 2.0) == 1.0
    assert r.transfer("relu", -1.0) == 0.0 and math.isclose(r.transfer("abs", -0.5), math.tanh(0.5))


def test_resting_on_the_planted_founders_reads_bias_zero_and_a_drifted_bias_saturates(tmp_path):
    """On RBT-106's w = 32 founders (regenerated here), every planted founder reads a paying predicate unit with
    b = 0 and resting drive 0; move that unit's bias to 0.3 and the resting drive is |v| tanh(0.3) > 1 (F12)."""
    fd = _load("t112_founders", "runs/RBT-106/founders.py")
    out = tmp_path / "f"
    fd.write(801, 32, str(out))
    assert fd.digest_of(str(out)) == fd.committed(32.0)[801]
    r = _load("t112_resting2", "runs/RBT-112/resting.py")
    from rabbitstew.genotype import Genotype
    from rabbitstew.simulation import SimConfig
    from rabbitstew.synthesis import synthesize
    cfg = json.load(open(os.path.join(ROOT, "runs", "RBT-90", "forage-801", "config.json")))
    sim = SimConfig.from_dict(cfg["sim"])
    g = Genotype.load(str(out / "conventional" / "000.json"))
    x = r.read(synthesize(g, sim.synthesis))
    assert x is not None and x["pay"] and x["b"] == 0.0 and x["rest"] == 0.0 and abs(x["vL"]) > 20
    ph = synthesize(g, sim.synthesis)
    ph.units[x["k"]].unit.bias = 0.3
    y = r.read(ph)
    assert y["rest"] > 1.0 and math.isclose(y["nominal"], 32 * math.tanh(0.3))


def test_verdict_rules_are_the_registered_ones():
    ro = _load("t112_readout", "runs/RBT-112/readout.py")
    assert ro.verdict(0, 5, 10).startswith("SUPPORTED")
    assert ro.verdict(2, 5, 10).startswith("SUPPORTED")
    assert ro.verdict(3, 5, 10).startswith("NOT DECIDED")        # the gap of 3 is required
    assert ro.verdict(0, 4, 10).startswith("NOT DECIDED")        # and at least 5 held
    assert ro.verdict(0, 1, 10).startswith("FALSIFIED") and ro.verdict(0, 0, 7).startswith("FALSIFIED")
    assert ro.verdict(0, 9, 6).startswith("VOID")
    assert ro.function_verdict(3, 0.1) == "FUNCTION FOLLOWS" and ro.function_verdict(3, -0.1) == "FUNCTION UNDECIDED"
    assert ro.function_verdict(1, -0.1) == "FUNCTION DOES NOT FOLLOW"
    m, lo, hi = ro.t_int([1.0, 2.0, 3.0])
    assert m == 2.0 and math.isclose(hi - m, 4.303 * 1.0 / math.sqrt(3))


def test_readout_parses_the_f12_line_and_the_certification(tmp_path):
    ro = _load("t112_readout2", "runs/RBT-112/readout.py")
    d = tmp_path / "HZ-1"
    d.mkdir()
    (d / "resting.txt").write_text("RESTING HZ-1: paying planted-unit carriers 5 of 7 champions; with resting drive > 1 "
                                   "(the Effector saturates, F12's masking route) 0; frozen-bias faults 0\n")
    assert ro.resting(str(d)) == dict(carriers=5, of=7, drifted=0, faults=0)
    assert not ro.certified(None) and not ro.certified(dict(commit="0" * 40, tree="x"))


def test_the_launcher_refuses_without_certification_and_prelaunch():
    s = open(os.path.join(D, "run_arm.sh")).read()
    assert 'exit 6' in s and "CROSS-TICKET HU-801: SAME RUN (prefix)" in s and "CROSS-TICKET HU-4: SAME RUN (prefix)" in s
    assert 'exit 7' in s and "PRELAUNCH: PASS" in s and "runs/RBT-112/command.py" in s


def test_power_model_pieces():
    p = _load("t112_power", "runs/RBT-112/power.py")
    assert p.x_of(10, 0.0, 0.1) == pytest.approx(0.9 ** 10)
    s_, u = 0.5, 0.089
    assert p.x_of(200, s_, u) == pytest.approx(((1 + s_) * (1 - u) - 1) / s_, abs=1e-6)   # mutation-selection balance
    assert p.betabinom_sf(3, 10, 0.3, 0.0) == pytest.approx(sum(math.comb(10, j) * 0.3 ** j * 0.7 ** (10 - j) for j in range(4, 11)))
    assert p.betabinom_sf(3, 10, 0.3, 0.5) > p.betabinom_sf(8, 10, 0.3, 0.5)
    dist = p.poibin([0.5, 0.5])
    assert list(dist) == pytest.approx([0.25, 0.5, 0.25])
