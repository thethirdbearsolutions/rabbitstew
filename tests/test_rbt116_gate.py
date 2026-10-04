"""RBT-116's W1 gate runner (runs/RBT-116/gate/gate.py, lanes.py) and world block (runs/RBT-116/world.py).

The registered planter check (Amendment 2/3: "gate.py's planter must be shown to build a steerer on the fixture world
(a test in its PR) before any gate cell") is ``test_g8f_planter_steers_on_the_fixture_world``.  Every simulated test
runs fixture worlds and fixture bodies; none runs W1's pool, an RBT-116 host or an arm.
"""
import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import replace

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-116", "gate"))

import gate  # noqa: E402
import lanes  # noqa: E402
from test_rbt116_steer import BATTERY, DRAWS, ONE_NOSE_WORLD, _pioneer  # noqa: E402

from rabbitstew.cli import build_parser, evolve_config  # noqa: E402
from rabbitstew.fixed import pioneer_genotype  # noqa: E402
from rabbitstew.genotype import BrainVocabulary, Genotype, random_genotype  # noqa: E402

steer, planters, W = gate.steer, gate.planters, gate.W
D2 = [steer.Draw(100 + i, 200 + i) for i in range(40, 76)]
#: Amendment 3's fixture variants: F2 (W1's eating block, the test battery) and F3 (a second test battery)
F2 = (replace(ONE_NOSE_WORLD, food=replace(ONE_NOSE_WORLD.food, eat_from="root", eat_rule="surface", clear_from="root")), BATTERY)
F3 = (ONE_NOSE_WORLD, steer.Battery(D2[:4], D2[4:20], D2[20:36]))


def _plant_f_tuned(cfg, bat):
    host = _pioneer(noses=(), throttle=0.8)  # the one-nose fixture's host, without its nose
    d0 = bat.stage1[0]
    lay = planters.c_layout(host, planters.body_geometry(host, cfg, d0))
    nose = gate.f_nose(host, cfg, d0)
    pattern = gate.turning_pattern(host, lay, cfg, d0)
    best, F, _ = planters.tune(gate.f_variants(host, nose, lay, pattern), cfg, bat.stage1, steer.run_season)
    return host, lay, nose, pattern, best


# --------------------------------------------------------------------------- #
# G8(f): the registered planter check
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("fx", [F2, F3], ids=["F2-W1-eating", "F3-second-battery"])
def test_g8f_planter_steers_on_the_fixture_world(fx):
    """gate.py's G8(f) planter, applied to the one-nose fixture's Pioneer with no nose, chooses its nose (the
    most-moving single-instance Part), measures its turning sense, tunes the 8 registered builds on the screening draws
    and is called STEERS on the full 4 + 16 + 16 battery -- on F2 and F3, a majority of Amendment 3's three fixture
    variants (on F1 its tuned build, (32, 16), is the one g8f_rule_probe.txt reads NONE there, confirmation F lb -0.20)."""
    cfg, bat = fx
    host, lay, nose, pattern, best = _plant_f_tuned(cfg, bat)
    assert nose in (1, 2) and pattern == "common"  # a drive wheel; the Pioneer's steering axis (the same command to both)
    rec = steer.call_genome(best, cfg, bat)
    assert rec["call"] == steer.STEERS, steer.format_call(best.name, rec)


def test_plant_f_builds_the_registered_unit():
    host = _pioneer(noses=())
    lay = {"left": 1, "right": 2, "sides": {1: 1.0, 2: -1.0}}
    links = planters.c_links(host, lay)
    for pattern in gate.F_PATTERNS:
        vs = gate.f_variants(host, 1, lay, pattern)
        assert len(vs) == 8
        for v, (gin, w, s) in zip(vs, [(g_, w_, s_) for g_, w_ in gate.F_BUILDS for s_ in (+1.0, -1.0)]):
            gb = v.global_brain
            assert gb.units[-1].func == "relu"
            k = len(gb.units) - 1
            ins = [l for l in gb.links if l.dst.node is None and l.dst.index == k]
            assert len(ins) == 1 and ins[0].weight == -gin and ins[0].src.node == 1
            assert v.nodes[1].segment.brain.units[ins[0].src.index].source == "food"
            outs = [(nd, l.weight) for nd, n in enumerate(v.nodes) for l in n.segment.brain.links if l.src.node is None and l.src.index == k]
            want = sorted((nd, s * w * (side if pattern == "diff" else 1.0)) for nd, _, side in links)
            assert sorted(outs) == want
    with pytest.raises(Exception):
        gate.plant_f(host, 99, lay, "common", 1.0, 32.0, 16.0)


def test_turning_pattern_probe_drives_both_senses():
    host = _pioneer(noses=())
    lay = {"left": 1, "right": 2, "sides": {1: 1.0, 2: -1.0}}
    links = planters.c_links(host, lay)
    common, diff = gate._drive(host, links, "common", 1.0, 4.0), gate._drive(host, links, "diff", 1.0, 4.0)
    w = lambda g: sorted(l.weight for n in g.nodes for l in n.segment.brain.links if l.src.node is None)  # noqa: E731
    assert w(common) == [4.0, 4.0] and w(diff) == [-4.0, 4.0]


# --------------------------------------------------------------------------- #
# G7's intermediates
# --------------------------------------------------------------------------- #


def _forager():
    voc = BrainVocabulary.named("foraging")
    return pioneer_genotype(np.random.default_rng(4), rich=True, sources=voc.sensor_sources)


def test_g7_intermediates_are_the_four_one_step_shapes():
    g = _forager()
    nose, eff = planters.routed.unit_indices(g)
    L, R = planters.routed.WHEELS
    want = {"pirouette": ([L], {L: 1, R: 1}), "throttle": ([L], {L: 1, R: -1}), "same-sign": ([L, R], {L: 1, R: 1}), "one-wheel": ([L], {L: 1})}
    for kind, (ins, outs) in want.items():
        for s in (+1.0, -1.0):
            p = gate.plant_g7(g, kind, s, 3.0)
            k = len(p.global_brain.units) - 1
            assert p.global_brain.units[k].func == "tanh"
            got_in = sorted(l.src.node for l in p.global_brain.links if l.dst.node is None and l.dst.index == k)
            assert got_in == sorted(ins)
            got_out = {nd: l.weight for nd, n in enumerate(p.nodes) for l in n.segment.brain.links if l.src.node is None and l.src.index == k}
            assert got_out == {nd: s * v * 3.0 for nd, v in outs.items()}
            assert all(l.dst.index == eff for nd, n in enumerate(p.nodes) for l in n.segment.brain.links if l.src.node is None and l.src.index == k)


def test_g7_host_pairs_each_intermediate_with_the_unmodified_host():
    g = _forager()
    cfg = replace(ONE_NOSE_WORLD, duration=3.0)
    bat = steer.Battery(DRAWS[:1], DRAWS[1:3], DRAWS[3:4])
    r = gate._g7_host((g.to_dict(), 1.0, 6.0, cfg.to_dict(), bat.to_dict()))
    assert len(r["base"]) == 2 and set(r) == {"base"} | {k + s for k in gate.INTERMEDIATES for s in "+-"}
    assert all(len(v) == 2 for v in r.values())


# --------------------------------------------------------------------------- #
# Decision rules
# --------------------------------------------------------------------------- #


def test_g1_rule_is_the_smallest_rung_whose_mean_F_is_bounded_above_zero():
    F = {2.0: [0.1, -0.2, 0.0, 0.05] * 4, 6.0: [0.5, 0.4, 0.6, 0.3] * 4, 16.0: [1.0] * 16, 32.0: [2.0] * 16}
    assert gate.g1_decide(F, {}) == 6.0
    assert gate.g1_decide({a: [0.0, -0.1] * 8 for a in gate.RUNGS}, {}) is None


def test_g4_cap_is_about_four_of_two_hundred():
    assert gate.exact_upper(4, 200) <= 0.05 < gate.exact_upper(5, 200)


def test_noise_components_are_noise_py_arithmetic():
    rng = np.random.default_rng(0)
    A = rng.normal(0, 1, (40, 6)) + rng.normal(0, 0.5, (40, 1)) + rng.normal(0, 2, (1, 6))
    sb, sw = gate.noise_components(A)
    nd = 6
    sw_ref = np.sqrt((A - A.mean(axis=0)).var(axis=1, ddof=1).mean() * nd / (nd - 1))
    sb_ref = np.sqrt(max(A.mean(axis=1).var(ddof=1) - sw_ref ** 2 / nd, 0.0))
    assert (sb, sw) == pytest.approx((sb_ref, sw_ref))
    assert sw == pytest.approx(1.0, abs=0.2) and sb == pytest.approx(0.5, abs=0.25)


def test_g6_rule_per_draws_option():
    noise = {"holistic": (0.336, 1.158), "conventional": (0.056, 1.343)}  # power.py's priors
    u = {"holistic": (0.146, 100), "conventional": (0.28, 100)}
    rows = {r["option"]: r for r in gate.g6_table(noise, u, {})}
    assert rows["DF16"]["D"] == 20  # s acts at the truncation boundary, on 4 + 16 draws
    for r in rows.values():
        for k in ("holistic", "conventional"):
            sb, sw = noise[k]
            s = 1.27 * 0.25 / np.sqrt(sb ** 2 + sw ** 2 / r["D"])
            assert r[k]["s"] == pytest.approx(s) and r[k]["growth"] == pytest.approx((1 + s) * (1 - u[k][0]))
    # power.txt part 1 on the priors: D 16 passes (1.39 designed, 1.47 holistic), D 8 does not (designed 1.20)
    assert rows["D16"]["passes"] and not rows["D8"]["passes"]
    assert rows["D16"]["conventional"]["growth"] == pytest.approx(1.39, abs=0.01)


def test_power_rerun_reads_K_and_the_stronger_no():
    noise = {"holistic": (0.336, 1.158), "conventional": (0.056, 1.343)}
    u = {"holistic": (0.146, 1), "conventional": (0.28, 1)}
    eps = {"holistic": {"EPS_C": 0.005}, "designed": {"EPS_C": 0.005}}
    pw = gate.power_rerun(0.48, 0.32, eps, noise, u, 16, reps=20)
    assert pw["K"] in (3, 4, 5, 6, 7, 8, 9) and [k for k, _ in pw["K_table"]][0] == 3
    assert 0.0 <= pw["detect_headlined"] <= pw["detect_at_K"] <= 1.0
    assert pw["stronger_no"] == (pw["detect_headlined"] >= 0.8)


def test_census_summary_and_asymmetry_flag():
    rows = lambda net, food: [[[food, 1.0, net, 10, 10 * food, 0.2]] * 2] * 3  # noqa: E731
    res = {"R113": {"r113-final/holistic/intact": rows(1.0, 2.0), "r113-final/conventional/intact": rows(1.0, 2.0)},
           "W1": {"r113-final/holistic/intact": rows(0.5, 1.0), "r113-final/conventional/intact": rows(1.0, 2.0)}}
    summ = {w: gate.census_summary(v) for w, v in res.items()}
    assert summ["W1"]["r113-final/holistic/intact"]["solvency"] == 1.0
    flags = gate.asymmetric_moves(summ)
    assert any(f.startswith("food") for f in flags) and any(f.startswith("net") for f in flags)
    assert not any(f.startswith("work") for f in flags)


def _write(d, name, obj):
    os.makedirs(d, exist_ok=True)
    json.dump(obj, open(os.path.join(d, name), "w"))


def test_g8_summary_applies_every_registered_bar(tmp_path):
    out = str(tmp_path)
    _write(out, "g1.json", {"c_G1": 0.5})
    S, N = {"call": steer.STEERS, "stage2": {"F": 1.0}}, {"call": steer.NONE, "stage2": {"F": 0.0}}
    for j in W.UNITS:
        calls = {"a": [S, S, N, N], "b": [N] * 4, "c": [S, N, N, N] if j <= 18 else [N] * 4, "f": [S, N, N, N]}
        _write(os.path.join(out, "g8"), f"unit{j:02d}.json", {"calls": calls})
    _write(out, "g8_controls.json", {"d": [N] * 3, "e": [N] * 3})
    s = gate.g8_summary(out)
    assert s["SENS_C_P"] == 0.5 and s["a_pass"]  # 0.5 >= 0.6 x 0.5
    assert s["c_units"] == 18 and s["SENS_c"] == pytest.approx(18 / 96) and not s["c_pass"]  # 0.1875 < 0.20
    assert s["SENS_C_H"] == pytest.approx(min(18 / 96, 0.25))
    assert len(s["flagged"]) == 6 and not s["flag_pass"]  # units 19..24 have no (c) STEERS: > 4 flagged
    assert s["b_pass"] and s["de_pass"]


def test_g7_summary_fails_on_any_paying_intermediate(tmp_path):
    out = str(tmp_path)
    for i in range(16):
        h = {"base": [0.0] * 16, "host": f"h{i}", "rung": 6.0}
        for k in gate.INTERMEDIATES:
            for s in "+-":
                h[k + s] = list(np.random.default_rng(i).normal(-0.5, 0.2, 16))
        if i < 16:
            h["throttle+"] = list(np.random.default_rng(100 + i).normal(0.4, 0.05, 16))
        _write(os.path.join(out, "g7"), f"host{i:02d}.json", h)
    s = gate.g7_summary(out)
    assert not s["pass"] and s["rows"]["throttle+"]["lb_hosts"] > 0
    assert s["rows"]["pirouette+"]["lb_hosts"] < 0 and 0 <= s["rows"]["pirouette+"]["power_0.10"] <= 1


# --------------------------------------------------------------------------- #
# Keys, hosts, children, world
# --------------------------------------------------------------------------- #


def test_registered_draws_of_hosts_and_members_are_fixed():
    perm = gate.host_perm(5, 1, 40)
    assert perm == gate.host_perm(5, 1, 40) and sorted(perm) == list(range(40)) and perm != gate.host_perm(5, 0, 40)
    hs = {j: {"designed": [{"file": f"d{j}-{k}"} for k in range(4)]} for j in W.UNITS}
    units = [j for j, _ in gate.g1_hosts(hs)]
    assert len(set(units)) == 16 and units == [j for j, _ in gate.g1_hosts(hs)]


def test_g4_members_are_200_distinct_burn_in_finals(tmp_path):
    base = str(tmp_path)
    for j in W.UNITS:
        for kind in ("conventional", "holistic"):
            d = gate.b_dir(j, kind, base)
            os.makedirs(d)
            for i in range(40):
                open(os.path.join(d, f"{i:03d}.json"), "w").write("{}")
    for fauna in (0, 1):
        m = gate.g4_members(base, fauna)
        assert len(m) == 200 == len(set(m)) and m == gate.g4_members(base, fauna)
        assert all(("conventional" if fauna == 0 else "holistic") in f for f in m)


def test_children_use_each_faunas_mutation_operator_at_crossover_0():
    mut = W.evolution_config("U").mutation
    assert mut.effector_bias_sigma == 0.0  # --fair's frozen Effector-bias walk
    p = _forager()
    kids = gate.children(p, 0, 3, 1, mut)
    assert len(kids) == 40 and len({json.dumps(k.to_dict(), sort_keys=True) for k in kids}) > 1
    from rabbitstew.genetics import body_signature

    assert all(body_signature(k) == body_signature(p) for k in kids)
    again = gate.children(p, 0, 3, 1, mut)
    assert [k.to_dict() for k in kids] == [k.to_dict() for k in again]
    h = random_genotype(np.random.default_rng(2), vocab=BrainVocabulary.named("foraging"))
    assert len(gate.children(h, 1, 3, 1, mut)) == 40


def test_world_block_and_the_three_runs():
    cfg = W.w1_sim_config()
    steer.assert_world_point(cfg, "W1")
    steer.assert_registered_channel(cfg, "W1")
    assert steer.sim_hash(cfg.to_dict()) == gate.W1_SIM_HASH
    f = cfg.food
    assert (f.items, f.patches, f.patch_radius, f.radius, f.regrow_delay, f.decay, f.work_cost) == (12, 2, 0.4, 4.0, 60.0, 1.5, 0.03)
    assert cfg.world.terrain == "random" and cfg.random_start and cfg.duration == 15.0
    b, u, n = (W.evolution_config(r, 7, "D16") for r in ("B", "U", "N"))
    assert b.sim.food.smell_lesion and not u.sim.food.smell_lesion and n.sim.food.smell_decoy == "rotate"
    for c in (b, u, n):
        assert (c.crossover_rate, c.truncation, c.line, c.elites, c.population_size, c.save_every, c.seed, c.fairness) == (0.0, 0.25, "up", 0, 40, 12, 116007, "fair")
        assert c.locomotion_phase == c.generations and c.conventional_topology and c.brain_model == "foraging"
    assert (b.generations, u.generations) == (13, 49)
    assert b.from_population["holistic"].endswith(os.path.join("O3", "7", "U", "holistic", "final"))
    assert u.from_population == n.from_population and u.from_population["conventional"].endswith(os.path.join("unit07", "B", "conventional", "gen0012"))
    # I2: U and N differ only in the decoy
    du, dn = u.to_dict(), n.to_dict()
    dn["sim"]["food"].pop("smell_decoy")
    assert du == dn
    df = W.evolution_config("U", 7, "DF16")
    assert (df.draws, df.draws_final) == (4, 16)
    assert W.unit_start(24).endswith(os.path.join("Z4", "Z12", "U")) and W.unit_start(13).endswith(os.path.join("Z1", "Z1", "U"))


def test_hosts_unit_on_fixture_bodies(tmp_path, monkeypatch):
    """The hosts cell's per-unit work on fixture bodies in a fixture world: designed hosts are signed by both direction
    probes, holistic hosts carry a G8(c) layout, an f nose and a turning sense."""
    base = str(tmp_path)
    voc = BrainVocabulary.named("foraging")
    for kind in ("conventional", "holistic"):
        d = gate.b_dir(1, kind, base)
        os.makedirs(d)
        for i in range(6):
            if kind == "conventional":
                g = pioneer_genotype(np.random.default_rng(i), rich=True, sources=voc.sensor_sources)
            else:  # random founders never carry a two-sided layout; a moving wheeled body does
                g = random_genotype(np.random.default_rng(50 + i), vocab=voc) if i % 2 else _pioneer(noses=(), throttle=0.8)
            g.save(os.path.join(d, f"{i:03d}.json"))
    monkeypatch.setattr(gate, "N_DESIGNED", 1)
    monkeypatch.setattr(gate, "N_HOLISTIC", 1)
    cfg = replace(ONE_NOSE_WORLD, duration=3.0)
    r = gate._hosts_unit((1, cfg.to_dict(), base))
    assert len(r["designed"]) == 1 and r["designed"][0]["sign"] in (1.0, -1.0)
    assert len(r["holistic"]) == 1
    h = r["holistic"][0]
    assert h["f_nose"] in (1, 2) and h["f_pattern"] == "common" and set(h["layout"]) == {"left", "right", "sides"}
    assert r == gate._hosts_unit((1, cfg.to_dict(), base))  # deterministic


# --------------------------------------------------------------------------- #
# Lanes: emitted, never launched
# --------------------------------------------------------------------------- #


def test_lanes_emit_and_refuse_without_the_go(tmp_path):
    d = str(tmp_path / "lanes")
    lanes.emit(d)
    names = sorted(f for f in os.listdir(d) if f.endswith(".sh"))
    assert len(names) == 8 + 3 + 6 + 4 + 2 + 1 + 8 + 1 + 1
    for f in names:
        p = os.path.join(d, f)
        assert subprocess.run(["bash", "-n", p]).returncode == 0
        txt = open(p).read()
        assert 'RBT116_GATE_GO:-}" = 1 ]' in txt and "NOT LAUNCHED" in txt
    env = {k: v for k, v in os.environ.items() if k != "RBT116_GATE_GO"}
    r = subprocess.run(["bash", os.path.join(d, "b-O1.sh")], env=env, capture_output=True, text=True)
    assert r.returncode == 4 and "no GO" in r.stderr
    b = open(os.path.join(d, "b-O3.sh")).read()
    for j in (7, 8, 9):
        assert f"unit{j:02d}/B" in b and f"--seed {116000 + j}" in b
    assert "--smell-decoy zero" in b and "--crossover-rate 0" in b and "--generations 13" in b


def test_cost_tables_print():
    t = lanes.cost_text()
    assert "TOTAL" in t and "DF16" in t and "D8" in t
    for opt in ("D16", "D8", "DF16"):
        c = lanes.arm_cost(opt)
        assert c["24 units"] == pytest.approx(24 * c["unit"])
