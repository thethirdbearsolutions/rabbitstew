"""RBT-120: the opt-in motor budget (`--motor-budget C`, WorldConfig.motor_budget) and the motor-capacity report.

* Off (the default, or C = 0) is byte-identical: RBT-113's two tiny `evolve` runs write the config.json,
  lineage.jsonl, history.json and state.json whose digests were recorded before RBT-113's hook, and every
  robot's MJCF is unchanged.
* On at the registered C = 1.77, the designed Pioneer (Sum gear / (motor_strength x mass) = 1.7605) is inside the
  budget and byte-identical: its MJCF string, a simulated bout, and every conventional row of a whole solo
  `evolve` run.  The same checks fail at C = 1.7 (the tests can fail).
* A body over budget has every driven gear scaled by one factor to the cap, and its driven-joint damping with
  it, so each motor keeps its free-spin speed and its power (gear^2 / damping) falls with its gear.
"""
import hashlib
import json
import os
import platform
from dataclasses import replace

import numpy as np
import pytest

from rabbitstew import motors
from rabbitstew.cli import _sim_config, build_parser, evolve_config
from rabbitstew.evolution import EvolutionConfig, Experiment
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.genotype import random_genotype
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation
from rabbitstew.synthesis import synthesize
from rabbitstew.world import Spawn, WorldConfig, build_model, build_xml, dof_gears, motor_scale

from test_rbt113 import GOLDEN, A, B, _run, _sha, _lineage

C = 1.77  # the registered budget: the Pioneer's 1.7605 rounded UP, as the mass budget rounds its 15.3367 kg to 15.34
PIONEER_RATIO = 108.0 / (4.0 * 15.33666)
OVER = 66  # random_genotype(default_rng(66)) under the 15.34 kg mass budget: Sum gear / (4 x mass) = 3.24


def _sim(budget=0.0, mass_budget=15.34):
    sc = SimConfig()
    sc.synthesis.mass_budget = mass_budget
    sc.world.motor_budget = budget
    return sc


def _pioneer():
    return pioneer_genotype(np.random.default_rng(3))


def _over():
    return random_genotype(np.random.default_rng(OVER))


# --- off is byte-identical -------------------------------------------------------------------------------------

@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
@pytest.mark.parametrize("extra", [["--motor-budget", "0"]])
def test_off_is_byte_identical_to_the_pre_budget_code(tmp_path, extra):
    _run(A + extra, tmp_path / "a")
    _run(B + extra, tmp_path / "b")
    got = {k: _sha(tmp_path / k) for k in GOLDEN}
    assert got == GOLDEN


def test_off_writes_no_motor_budget_key_and_on_round_trips():
    off = evolve_config(build_parser().parse_args(["evolve"] + B + ["--out", "/nonexistent"]))
    assert "motor_budget" not in off.to_dict()["sim"]["world"]
    assert "motor_budget" not in off.sim.to_dict()["world"]
    on = evolve_config(build_parser().parse_args(["evolve"] + B + ["--motor-budget", str(C), "--out", "/nonexistent"]))
    d = on.to_dict()
    assert d["sim"]["world"]["motor_budget"] == C
    assert EvolutionConfig.from_dict(json.loads(json.dumps(d))).sim.world.motor_budget == C
    assert SimConfig.from_dict(on.sim.to_dict()).world.motor_budget == C
    assert EvolutionConfig.from_dict(json.loads(json.dumps(off.to_dict()))).sim.world.motor_budget == 0.0


@pytest.mark.parametrize("cmd", ["evolve", "simulate", "ecology"])
def test_the_flag_reaches_the_world_from_every_command(cmd):
    extra = ["g.json"] if cmd == "simulate" else []
    args = build_parser().parse_args([cmd] + extra + ["--motor-budget", "1.77"])
    assert _sim_config(args).world.motor_budget == 1.77
    args = build_parser().parse_args([cmd] + extra)
    assert _sim_config(args).world.motor_budget == 0.0


def test_off_leaves_every_mjcf_unchanged():
    for s in range(40):
        ph = synthesize(random_genotype(np.random.default_rng(s)), _sim().synthesis)
        assert motor_scale(ph, WorldConfig()) == 1.0
        assert build_xml([ph], [Spawn()], WorldConfig()) == build_xml([ph], [Spawn()], WorldConfig(motor_budget=0.0))


# --- on: the Pioneer is inside and unchanged; the check can fail ------------------------------------------------

def test_pioneer_ratio_is_1_76_and_inside_the_budget():
    ph = synthesize(_pioneer(), _sim().synthesis)
    total = sum(dof_gears(ph, WorldConfig()).values())
    mass = sum(p.mass for p in ph.parts)
    assert total == pytest.approx(108.0)
    assert total / (4.0 * mass) == pytest.approx(PIONEER_RATIO, abs=1e-4)
    assert 1.76 < total / (4.0 * mass) < C
    assert motor_scale(ph, WorldConfig(motor_budget=C)) == 1.0
    assert motor_scale(ph, WorldConfig(motor_budget=1.7)) < 1.0  # a budget below it would bind


@pytest.mark.parametrize("budget,same", [(C, True), (2.0, True), (1.7, False)])
def test_pioneer_mjcf_and_bout_are_byte_identical_under_the_budget(budget, same):
    g = _pioneer()
    ph = synthesize(g, _sim().synthesis)
    assert (build_xml([ph], [Spawn()], WorldConfig()) == build_xml([ph], [Spawn()], WorldConfig(motor_budget=budget))) is same
    runs = []
    for b in (0.0, budget):
        sc = _sim(b)
        sc.duration = 2.0
        sim = Simulation([g], sc)
        sim.run()
        runs.append((sim.data.qpos.tobytes(), float(sim.work[0])))
    assert (runs[0] == runs[1]) is same


def _conventional(out):
    return [{k: v for k, v in r.items()} for r in _lineage(out, "conventional")]


@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
def test_designed_body_is_byte_identical_through_a_whole_solo_run_under_the_budget(tmp_path):
    """RBT-113's solo foraging run B: every conventional lineage row (fitness, distance, body) is unchanged at
    C = 1.77; the holistic side, whose founders include bodies over budget, is not."""
    _run(B, tmp_path / "off")
    _run(B + ["--motor-budget", str(C)], tmp_path / "on")
    assert _sha(tmp_path / "off" / "lineage.jsonl") == GOLDEN["b/lineage.jsonl"]
    assert _conventional(tmp_path / "off") == _conventional(tmp_path / "on")
    assert _lineage(tmp_path / "off", "holistic") != _lineage(tmp_path / "on", "holistic")
    _run(B + ["--motor-budget", "1.7"], tmp_path / "tight")  # can fail: a budget below the Pioneer's ratio moves it
    assert _conventional(tmp_path / "off") != _conventional(tmp_path / "tight")


# --- on: a body over budget ------------------------------------------------------------------------------------

def _actuated(model):
    """(gear, damping) per actuator from a compiled single-robot model (torque motors)."""
    out = []
    for a in range(model.nu):
        j = model.actuator_trnid[a, 0]
        k = int(np.argmax(np.abs(model.actuator_gear[a, :3])))
        dof = model.jnt_dofadr[j] + (k if model.jnt_type[j] == 1 else 0)  # mjJNT_BALL == 1
        out.append((abs(float(model.actuator_gear[a, k])), float(model.dof_damping[dof]), int(model.actuator_biastype[a])))
    return out


def test_a_body_over_budget_is_scaled_to_the_cap_with_its_damping():
    ph = synthesize(_over(), _sim().synthesis)
    raw = sum(dof_gears(ph, WorldConfig()).values())
    mass = sum(p.mass for p in ph.parts)
    assert raw / (4 * mass) > 3.0
    s = motor_scale(ph, WorldConfig(motor_budget=C))
    assert s == pytest.approx(C * 4 * mass / raw)
    m0, _, _ = build_model([ph], [Spawn()], WorldConfig())
    m1, _, _ = build_model([ph], [Spawn()], WorldConfig(motor_budget=C))
    a0, a1 = _actuated(m0), _actuated(m1)
    assert len(a0) == len(a1) > 0
    for (g0, d0, bt), (g1, d1, _) in zip(a0, a1):
        assert g1 == pytest.approx(s * g0, rel=1e-5)  # one factor for every motor: proportions kept
        if bt == 0:
            assert g1 / d1 == pytest.approx(g0 / d0, rel=1e-5)  # free-spin speed kept (gear / damping = 1 / joint_damping)
            assert g1 * g1 / d1 == pytest.approx(s * g0 * g0 / d0, rel=1e-5)  # power falls with the gear
    cap = motors.capacity(_over(), _sim(C))
    assert cap.ratio == pytest.approx(C, rel=1e-5)
    assert cap.unbudgeted_ratio == pytest.approx(raw / (4 * mass))
    assert cap.budget_scale == pytest.approx(s)
    # geometry and mass are untouched: only actuators and driven-joint damping differ
    assert np.array_equal(m0.body_mass, m1.body_mass) and np.array_equal(m0.geom_size, m1.geom_size)


def test_the_budget_caps_the_free_spin_ceiling_at_the_designed_bodys_per_kg():
    """Under the damping rule (driven damping = joint_damping x gear) the torque motors' ceiling is Sum gear / joint_damping,
    so capping Sum gear per kg caps power per kg: no budgeted body out-spins the Pioneer by more than C / 1.7605 per kg."""
    sc = _sim(C)
    sc.duration = 15.0
    sc.food = FoodConfig(work_cost=0.03)
    pio = motors.capacity(_pioneer(), sc)
    assert pio.ceiling_yield == pytest.approx(0.972)
    for s in range(60):
        c = motors.capacity(random_genotype(np.random.default_rng(s)), sc)
        assert c.ratio <= C * (1 + 1e-5)
        assert c.ceiling_yield / c.mass <= pio.ceiling_yield / pio.mass * C / pio.ratio * (1 + 1e-5)


def test_a_negative_budget_is_refused():
    ph = synthesize(_pioneer(), _sim().synthesis)
    with pytest.raises(ValueError):
        motor_scale(ph, WorldConfig(motor_budget=-1.0))


# --- the report ------------------------------------------------------------------------------------------------

def test_report_prints_the_pioneer_at_1_76_and_flags_a_body_over_budget(tmp_path):
    for name, g in (("designed", _pioneer()), ("over", _over())):
        d = tmp_path / name
        d.mkdir()
        g.save(str(d / "000.json"))
    cfg = tmp_path / "config.json"
    json.dump(evolve_config(build_parser().parse_args(["evolve"] + B + ["--out", "/nonexistent"])).to_dict(), open(cfg, "w"))
    text = motors.report({"designed": [_pioneer()], "over": [_over()]}, motors.load_sim(str(cfg)))
    rows = {line.split()[0]: line.split() for line in text.splitlines() if not line.startswith("#") and not line.startswith("line")}
    assert rows["designed"][7] == "1.76" and rows["designed"][-1] == "0.00"
    assert float(rows["over"][7]) > 3.0
    budgeted = motors.report({"over": [_over()]}, replace(motors.load_sim(str(cfg)), world=replace(motors.load_sim(str(cfg)).world, motor_budget=C)))
    assert "C = 1.77" in budgeted
    row = [line.split() for line in budgeted.splitlines() if line.startswith("over")][0]
    assert row[7] == "1.77" and row[-1] == "1.00"
    assert motors.main([f"designed={tmp_path / 'designed'}", f"over={tmp_path / 'over'}", "--motor-budget", str(C)]) == 0
