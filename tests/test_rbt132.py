"""RBT-132: steer.py at RBT-129's points (τ per point), their draw pools, the planted set in the tree, the probe driver
and the probe power.  Fixture worlds and committed bodies only: no RBT-129 or RBT-116 arm, gate cell or pool season.
RBT-116's own tests (tests/test_rbt116_steer.py) are unchanged and must still pass: W1 is byte-identical."""
import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import replace

import numpy as np
import pytest

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import FoodConfig, SimConfig

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "runs", "RBT-116")


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, RUNS)
planters = _load("planters", os.path.join(RUNS, "planters.py"))
steer = planters.steer
probe_members = _load("probe_members", os.path.join(RUNS, "probe_members.py"))
probe_power = _load("probe_power", os.path.join(RUNS, "probe_power.py"))

G_POINT, L_POINT = "c1-p030-PW-G", "c1-p030-U-L"
#: a small fixture world under RBT-129's channel (G 2.5, τ 2 s) and eating block
FIX_G = SimConfig(duration=4.0, random_start=True, start_distance_range=(1.0, 1.5),
                  food=FoodConfig(items=6, radius=2.0, decay=1.0, smell_contrast=2.5, smell_tau=2.0, eat_from="root", eat_rule="surface"))
DESIGNED = os.path.join(ROOT, "runs", "RBT-19", "P-801", "conventional", "best_gen0590.json")
HOLISTIC = os.path.join(ROOT, "runs", "RBT-19", "P-801", "holistic", "best_gen0590.json")
DRAWS = [steer.Draw(300 + i, 400 + i) for i in range(12)]


# --------------------------------------------------------------------------- #
# Item 1: τ per point; W1 unchanged
# --------------------------------------------------------------------------- #


def test_w1_is_unchanged():
    assert steer.SMELL_TAU == 1.0 == steer.registered_tau() == steer.registered_tau("W1")
    assert steer.REGISTERED_POINTS["W1"] == {"smell_contrast": 2.5, "smell_tau": 1.0, "eat_from": "root", "eat_rule": "surface",
                                             "clear_from": "root", "eat_radius": 0.35}
    assert steer.POOL_KEY["W1"] == (116, 64, 1)
    tau2 = replace(FIX_G, food=replace(FIX_G.food, smell_tau=2.0))
    with pytest.raises(ValueError, match="smell_tau"):
        steer.assert_registered_channel(tau2)  # the default point is W1: τ 2 s is still refused there
    steer.assert_registered_channel(replace(FIX_G, food=replace(FIX_G.food, smell_tau=1.0)))


def test_tau_is_checked_against_each_points_own_registration():
    steer.assert_registered_channel(FIX_G, G_POINT)  # τ 2 s at a G point
    with pytest.raises(ValueError, match="smell_tau"):
        steer.assert_registered_channel(replace(FIX_G, food=replace(FIX_G.food, smell_tau=1.0)), G_POINT)
    with pytest.raises(ValueError, match="channel off"):  # a channel at an L point, which registers none
        steer.assert_registered_channel(FIX_G, L_POINT)
    steer.assert_registered_channel(replace(FIX_G, food=replace(FIX_G.food, smell_contrast=0.0)), L_POINT)
    with pytest.raises(KeyError):
        steer.assert_registered_channel(FIX_G, "c9-p999-XX-G")
    with pytest.raises(ValueError, match="smell_tau"):  # through the season, as the point's season function
        steer.point_season(G_POINT)(Genotype.load(DESIGNED), replace(FIX_G, food=replace(FIX_G.food, smell_tau=3.0)), DRAWS[0], "intact")
    s = steer.point_season(G_POINT)(Genotype.load(DESIGNED), replace(FIX_G, duration=0.2), DRAWS[0], "intact")
    assert s.condition == "intact"


def test_rbt129_points_match_their_committed_blocks():
    """Every registered RBT-129 point equals its committed worlds/<id>.config.json, and carries the fair marker."""
    assert len(steer.RBT129_POINTS) == 18 and set(steer.RBT129_POINTS) == set(steer.FAIR_POINTS)
    for pid in steer.RBT129_POINTS:
        raw = json.load(open(os.path.join(ROOT, "runs", "RBT-129", "worlds", f"{pid}.config.json")))
        cfg = SimConfig.from_dict(raw["sim"])
        steer.assert_world_point(cfg, pid)
        steer.assert_registered_channel(cfg, pid)
        steer.assert_fair_config(raw, pid)
        with pytest.raises(ValueError, match="fair"):
            steer.assert_fair_config({**raw, "fairness": None}, pid)
    steer.assert_fair_config({}, "W1")  # W1 needs no marker (its block predates --fair)


def test_pools_are_registered_distinct_and_stable():
    pools = {pid: steer.draw_pool(pid) for pid in ("W1",) + steer.RBT129_POINTS}
    assert all(len(p) == 64 for p in pools.values())
    firsts = {p[0] for p in pools.values()}
    assert len(firsts) == len(pools)  # every point has its own pool
    assert pools["W1"][:2] == [steer.Draw(994215827, 1544761483), steer.Draw(1144233029, 653913764)]  # W1's, unchanged
    for pid in steer.RBT129_POINTS:
        assert steer.POOL_KEY[pid] == (116, 64, 129, steer.RBT129_POINTS.index(pid) + 1)
        assert steer.draw_pool(pid, extended=True)[:64] == pools[pid]


def test_the_screen_runs_at_the_points_own_tau():
    """screen_draws at an RBT-129 point checks the channel against that point's τ, not W1's."""
    g = Genotype.load(DESIGNED)
    with pytest.raises(ValueError, match="smell_tau"):  # W1's season on a τ 2 s world is refused
        steer.screen_draws([g], FIX_G, "W1")
    # the default season at an RBT-129 point is that point's
    cfg = replace(FIX_G, duration=0.1)
    r = steer.screen_draws([g], cfg, G_POINT)
    assert len(r["table"]) == 96 and r["passed"] is False  # nothing eats in 0.1 s: extended once, then the gate fails


# --------------------------------------------------------------------------- #
# Item 3: the planters
# --------------------------------------------------------------------------- #


def test_tumblers_are_smell_blind_and_read_none_at_stage1():
    season = steer.point_season(G_POINT)
    small = steer.Battery(DRAWS[:4], DRAWS[4:6], DRAWS[6:8])
    for joint in ("rod", "hinge", "ball"):
        for noses in (False, True):
            g = planters.tumbler(joint, noses)
            assert sum(u.kind == "sensor" for _, b in g.brains() for u in b.units) == (2 if noses else 0)
            rec = steer.call_genome(g, FIX_G, small, season)
            assert rec["call"] == steer.NONE and rec["stage"] == 1, (g.name, rec)


def test_motors_off_body_never_actuates():
    g = planters.plant_a(Genotype.load(DESIGNED), +1.0)
    off = planters.motors_off(g)
    s = steer.point_season(G_POINT)(off, FIX_G, DRAWS[0], "intact")
    assert s.work == 0.0 and s.disp < 0.05
    rec = steer.call_genome(off, FIX_G, steer.Battery(DRAWS[:4], DRAWS[4:6], DRAWS[6:8]), steer.point_season(G_POINT))
    assert rec["call"] == steer.NONE and rec["stage"] == 1


def test_plant_a_is_the_routed_compass_and_is_signed():
    g = Genotype.load(DESIGNED)
    sign = planters.compass_sign(g, FIX_G)
    assert sign in (+1.0, -1.0)
    a = planters.plant_a(g, sign)
    assert a.validate() == [] and len(a.global_brain.units) == len(g.global_brain.units) + 1
    assert planters.plant_a(g, sign).to_dict() == a.to_dict()  # deterministic


def test_plant_b_is_sign_blind_and_valid():
    g = Genotype.load(DESIGNED)
    for v in planters.B_GRID:
        b = planters.plant_b(g, *v)
        assert b.validate() == []
        funcs = [u.func for u in b.global_brain.units[-2:]]
        assert funcs == ["abs", "relu"]  # keyed on |reading| (R5-3), thresholded
    assert len(planters.B_GRID) == 16


def test_plant_c_on_a_holistic_body():
    h = Genotype.load(HOLISTIC)
    geom = planters.body_geometry(h, FIX_G, DRAWS[0])
    assert geom is not None and abs(np.linalg.norm(geom["heading"]) - 1.0) < 1e-9
    lay = planters.c_layout(h, geom)
    assert lay is not None and lay["left"] != lay["right"]
    assert geom["lat"][geom["phenotype"].node_instances[lay["left"]][0]] > 0 > geom["lat"][geom["phenotype"].node_instances[lay["right"]][0]]
    assert any(v > 0 for v in lay["sides"].values()) and any(v < 0 for v in lay["sides"].values())
    for sign in (+1.0, -1.0):
        c = planters.plant_c(h, lay, sign)
        assert c.validate() == []
        nf = sum(u.kind == "sensor" and u.source == "food" for _, b in c.brains() for u in b.units)
        assert nf == sum(u.kind == "sensor" and u.source == "food" for _, b in h.brains() for u in b.units) + 2
    s = steer.point_season(G_POINT)(planters.plant_c(h, lay, 1.0), FIX_G, DRAWS[1], "intact")
    assert s.food_abs_max > 0  # the new noses read the channel


def test_tune_picks_the_largest_F():
    calls = []

    def season(g, cfg, d, cond):
        calls.append((g.name, cond))
        food = {"x": 2.0, "y": 3.0}[g.name] if cond == "intact" else 1.0
        return steer.Season(cond, d, food, 0.0, food, False, 1, np.zeros((2, 2)), np.ones(1), np.ones(1), np.ones(1, bool))

    gx, gy = planters.tumbler("rod"), planters.tumbler("hinge")
    gx.name, gy.name = "x", "y"
    best, F, table = planters.tune([gx, gy], FIX_G, DRAWS[:4], season)
    assert best is gy and F == 2.0 and table == [("x", 1.0), ("y", 2.0)]


def test_k3_k4():
    seen = {"call": steer.SMELL_USE, "stage2": {"c3": True, "lbdT": 0.1, "F": 0.1}}
    steers = {"call": steer.STEERS, "stage2": {"c3": True, "lbdT": 0.2, "F": 1.0}}
    none = {"call": steer.NONE, "stage": 1}
    ok = planters.k3_k4({"a": [steers, seen, none], "c": [seen, seen], "b": [none], "d": [none], "e": [none], "motors-off": [none]})
    assert ok["K3"] and ok["K4"] and ok["K3_seen"] == (2, 2) and "untested" in ok["K4_b_note"]
    assert not planters.k3_k4({"a": [steers] * 4, "c": [none] * 8})["K3"]  # needs one of each kind
    assert not planters.k3_k4({"a": [seen], "c": [seen], "b": [steers]})["K4"]


def test_host_pool_is_a_fixed_permutation(tmp_path):
    for seed in planters.HOST_SEEDS:
        for kind in ("holistic", "conventional"):
            d = tmp_path / "O1" / str(seed) / "U" / kind / "final"
            d.mkdir(parents=True)
            for i in range(5):
                (d / f"{i:03d}.json").write_text("{}")
    a, b = planters.host_pool(str(tmp_path), "holistic"), planters.host_pool(str(tmp_path), "holistic")
    assert a == b and len(a) == 15 and sorted(a) != a
    assert planters.host_pool(str(tmp_path), "conventional") != [p.replace("conventional", "holistic") for p in a]


# --------------------------------------------------------------------------- #
# The probe driver
# --------------------------------------------------------------------------- #


def test_probe_members_season0_and_final(tmp_path):
    run = tmp_path / "S"
    for kind in probe_members.KINDS:
        (run / kind / "genomes").mkdir(parents=True)
        (run / kind / "final").mkdir(parents=True)
        for i in range(30):
            (run / kind / "genomes" / f"{kind[0]}{i}.json").write_text("{}")
        for i in range(25):
            (run / kind / "final" / f"{i:03d}.json").write_text("{}")
        (run / kind / "final" / "config.json").write_text("{}")
    rows = [{"season": 0, "groups": [[{"name": f"{k[0]}{i}", "kind": k} for i in range(30)] for k in probe_members.KINDS]},
            {"season": 1, "groups": [[{"name": "h99", "kind": "holistic"}]]}]
    (run / "cohorts.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    f0 = probe_members.members(str(run), 0, "holistic")
    assert len(f0) == 30 and all("/genomes/h" in p for p in f0)
    fin = probe_members.members(str(run), 300, "conventional")
    assert len(fin) == 25 and not any(p.endswith("config.json") for p in fin)
    d1, d2 = probe_members.draw_members(f0, 129301), probe_members.draw_members(f0, 129301)
    assert d1 == d2 and len(d1) == 20 and len(set(d1)) == 20 and d1 != probe_members.draw_members(f0, 129302)
    assert probe_members.draw_members(f0[:7], 1) == f0[:7]


# --------------------------------------------------------------------------- #
# Item 5: the probe power
# --------------------------------------------------------------------------- #


def test_probe_power_is_exact_and_committed():
    assert probe_power.pmf(3, 0.5) == pytest.approx([0.125, 0.375, 0.375, 0.125])
    assert probe_power.upper_bound(0, 80) == 0  # the plug-in bound at a zero founders' count: the null issue
    assert probe_power.false_positive(80, 0.005) == pytest.approx(0.221, abs=0.002)
    assert probe_power.false_positive(80, 0.005, probe_power.upper_bound_cp) < 0.05
    assert probe_power.perceives_power(80, 0.25, 0.40, 0.005) < probe_power.perceives_power(80, 0.25, 0.48, 0.005)
    out = subprocess.run([sys.executable, os.path.join(RUNS, "probe_power.py")], capture_output=True, text=True, cwd=ROOT)
    assert out.stdout == open(os.path.join(RUNS, "probe_power.txt")).read()
    table = json.load(open(os.path.join(RUNS, "probe_power.json")))
    assert set(table["by_tau"]) == {"1.0", "2.0"}
    assert "tau 2 s" in planters.power_line(G_POINT) and "legacy" in planters.power_line(L_POINT)
