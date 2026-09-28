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


def test_plant_b_is_sign_blind_thresholded_on_the_left_wheel_and_slows():
    g = Genotype.load(DESIGNED)
    nose, eff = planters.routed.unit_indices(g)
    assert len(planters.B_GRID) == 8  # q x k x s_T; s_B fixed to the slowing sign (the 07:10 ruling, S6)
    for sB in (planters.slowing_sign(False), planters.slowing_sign(True)):
        for q, k, sT in planters.B_GRID:
            b = planters.plant_b(g, q, k, sT, sB)
            assert b.validate() == []
            mag, thr = b.global_brain.units[-2:]
            assert (mag.func, thr.func, mag.bias, thr.bias) == ("abs", "relu", 0.0, -q)  # |reading|, thresholded at q
            n = len(b.global_brain.units)
            ins = [l for l in b.global_brain.links if l.dst.node is None and l.dst.index == n - 2]
            assert [(l.src.node, l.src.index, l.weight) for l in ins] == [(planters.LEFT, nose, k)]  # the LEFT wheel's nose
            for nd, side in ((planters.LEFT, +1.0), (planters.RIGHT, -1.0)):
                out = [l for l in b.nodes[nd].segment.brain.links if l.src.node is None and l.src.index == n - 1]
                assert [(l.dst.index, l.weight) for l in out] == [(eff, sT + side * sB * 0.5)]
    assert planters.slowing_sign(False) == -1.0 and planters.slowing_sign(True) == +1.0  # forward travel: brake is -throttle


def test_compass_sign_needs_agreement_and_maps_travel_to_sign():
    g = Genotype.load(DESIGNED)
    back_sign = +1.0 if planters.routed.mech.rs.PUBLISHED_IS_BACKWARD else -1.0
    assert planters.compass_sign(g, FIX_G, [True, True]) == back_sign
    assert planters.compass_sign(g, FIX_G, [False, False]) == -back_sign
    assert planters.compass_sign(g, FIX_G, [True, False]) is None
    assert planters.compass_sign(g, FIX_G, [None, None]) is None
    a = planters.plant_a(g, +1.0)
    k = len(a.global_brain.units) - 1
    outs = [l.weight for nd in planters.routed.WHEELS for l in a.nodes[nd].segment.brain.links if l.src.node is None and l.src.index == k]
    assert outs == [planters.W_RUNG] * 2 and planters.W_RUNG == 3.0 and planters.A_RUNG == 6.0  # a = 2w = 6


class _NS:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _stub(node_instances, lat, effector_nodes):
    """A stub body for c_layout: node -> instance parts, per-part lateral coordinates, and which Nodes carry Effectors."""
    nodes = [_NS(segment=_NS(brain=_NS(units=[_NS(kind="effector")] if nd in effector_nodes else [_NS(kind="sensor")])))
             for nd in range(max(node_instances) + 1)]
    return _NS(nodes=nodes), {"lat": np.array(lat, float), "phenotype": _NS(node_instances=node_instances)}


def test_c_layout_uses_single_instance_noses_and_one_sided_effectors():
    # Node 1 has two instances at the extremes (+2, -2); the single-instance extremes are Node 2 (+1) and Node 3 (-1)
    g, geom = _stub({0: [0], 1: [1, 2], 2: [3], 3: [4], 4: [5, 6]}, [0.0, 2.0, -2.0, 1.0, -1.0, 0.5, -0.5], {2, 3, 4})
    lay = planters.c_layout(g, geom)
    assert (lay["left"], lay["right"]) == (2, 3)
    assert lay["sides"] == {2: 1.0, 3: -1.0}  # Node 4's instances straddle the heading: left unwired
def test_plant_c_on_a_holistic_body():
    h = Genotype.load(HOLISTIC)
    geom = planters.body_geometry(h, FIX_G, DRAWS[0])
    assert geom is not None and abs(np.linalg.norm(geom["heading"]) - 1.0) < 1e-9
    lay = planters.c_layout(h, geom)
    assert lay is not None and lay["left"] != lay["right"]
    assert geom["lat"][geom["phenotype"].node_instances[lay["left"]][0]] > 0 > geom["lat"][geom["phenotype"].node_instances[lay["right"]][0]]
    assert any(v > 0 for v in lay["sides"].values()) and any(v < 0 for v in lay["sides"].values())
    links = planters.c_links(h, lay)
    for sign in (+1.0, -1.0):
        c = planters.plant_c(h, lay, sign)
        assert c.validate() == [] and f"/{len(links)}" in c.name
        k = len(c.global_brain.units) - 1
        ins = sorted((l.src.node, l.weight) for l in c.global_brain.links if l.dst.index == k and l.dst.node is None)
        assert ins == sorted([(lay["left"], +1.0), (lay["right"], -1.0)])  # a difference unit: + left, - right
        outs = [(nd, l.weight) for nd, i, side in links for l in c.nodes[nd].segment.brain.links if l.src.node is None and l.src.index == k and l.dst.index == i]
        assert len(outs) == len(links) and sum(abs(w) for _, w in outs) == pytest.approx(planters.A_RUNG)  # total a = 6
        assert all(w == pytest.approx(sign * lay["sides"][nd] * planters.A_RUNG / len(links)) for nd, w in outs)
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


def _rec(call, c2=True, c3=True, cc2=True, cc3=True, F=0.1, confirm_key="confirm", unconfirmed=False):
    r = {"call": call, "stage": 3, "stage2": {"c2": c2, "c3": c3, "F": F}, "pass_unconfirmed": unconfirmed}
    if confirm_key:
        r[confirm_key] = {"c2": cc2, "c3": cc3}
    return r


def test_k3_seen_is_behavioural_and_repeated():
    """The 07:10 ruling, item 1: SEEN = stage-2 c2 and c3, repeated on the confirmation; F plays no part."""
    assert planters.seen(_rec(steer.NONE, F=0.05, confirm_key="k3_confirm"))  # F < F_MIN, not called STEERS: still seen
    assert planters.seen(_rec(steer.NONE, F=1.0, unconfirmed=True, cc2=True, cc3=True))  # pass_unconfirmed on F, behaviour repeats
    assert not planters.seen(_rec(steer.STEERS, c2=False))
    assert not planters.seen(_rec(steer.STEERS, c3=False))
    assert not planters.seen(_rec(steer.NONE, cc2=False))
    assert not planters.seen(_rec(steer.NONE, cc3=False))
    assert not planters.seen(_rec(steer.SMELL_USE, confirm_key=None))  # no confirmation run: not seen
    assert not planters.seen({"call": steer.NONE, "stage": 1})


def test_k3_k4():
    s, n = _rec(steer.NONE, F=0.05, confirm_key="k3_confirm"), {"call": steer.NONE, "stage": 1}
    ok = planters.k3_k4({"a": [s, s, n], "c": [s, s], "b": [n], "d": [n], "e": [n], "motors-off": [n]})
    assert ok["K3"] and ok["K4"] and ok["K3_seen"] == (2, 2) and "untested" in ok["K4_b_note"]
    assert not planters.k3_k4({"a": [s, s], "c": [s]})["K3"]  # 3 seen: below the 4-of-N bar
    assert not planters.k3_k4({"a": [s] * 4, "c": [n] * 8})["K3"]  # needs one of each kind
    st = _rec(steer.STEERS, F=1.0)
    assert not planters.k3_k4({"a": [s], "c": [s], "b": [st]})["K4"]
    assert planters.k3_k4({"b": [st]})["K4_b_testable"] == 1


def test_host_pool_is_a_fixed_permutation(tmp_path):
    for seed in planters.HOST_SEEDS:
        for kind in ("holistic", "conventional"):
            d = tmp_path / "O1" / str(seed) / "U" / kind / "final"
            d.mkdir(parents=True)
            for i in range(5):
                (d / f"{i:03d}.json").write_text("{}")
    a, b = planters.host_pool(str(tmp_path), "holistic"), planters.host_pool(str(tmp_path), "holistic")
    assert a == b and len(a) == 15 and sorted(a) != a
    base = lambda ps: [os.path.relpath(p, str(tmp_path)).replace("conventional", "K").replace("holistic", "K") for p in ps]
    assert base(planters.host_pool(str(tmp_path), "conventional")) != base(a)  # each fauna has its own permutation


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
    assert probe_power.null_max(80)[0] <= 0.05 and probe_power.null_max(160)[0] <= 0.05  # Fisher is level
    assert probe_power.perceives(80, 0.25, 0.40, 0.005) < probe_power.perceives(80, 0.25, 0.48, 0.005)
    assert probe_power.reject(80)[0][0] is False and probe_power.reject(80)[0][6] is True
    out = subprocess.run([sys.executable, os.path.join(RUNS, "probe_power.py")], capture_output=True, text=True, cwd=ROOT)
    assert out.stdout == open(os.path.join(RUNS, "probe_power.txt")).read()
    assert "tau 2 s" in planters.power_line(G_POINT) and "legacy" in planters.power_line(L_POINT)
    assert planters.power_line(G_POINT) == "# power at this point: " + probe_power.line(2.0)


# --------------------------------------------------------------------------- #
# S1: the committed sim block per point
# --------------------------------------------------------------------------- #


def test_every_point_is_pinned_to_its_committed_sim_block():
    raws = {pid: json.load(open(os.path.join(ROOT, "runs", "RBT-129", "worlds", f"{pid}.config.json"))) for pid in steer.RBT129_POINTS}
    for pid, raw in raws.items():
        steer.assert_point_world(raw, pid)
        assert steer.sim_hash(raw["sim"]) == steer.POINT_SIM_HASH[pid]
    with pytest.raises(ValueError, match="committed block"):  # a G config run under another G point's label and pool
        steer.assert_point_world(raws["c1-p030-U-G"], "c1-p030-HP-G")
    with pytest.raises(ValueError, match="committed block"):
        steer.assert_point_world(raws["c0-p030-U-L"], "c1-p030-U-L")
    steer.assert_point_world({"sim": {}}, "W1")  # W1 has no committed block: unchanged


# --------------------------------------------------------------------------- #
# M3: end to end, at a TEST-ONLY point (no RBT-129 pool season runs)
# --------------------------------------------------------------------------- #

T_POINT = "T132-G"
#: the test world: dense food, short seasons, RBT-129's channel (τ 2 s) and eating block
FIX_E2E = SimConfig(duration=3.0, random_start=True, start_distance_range=(1.0, 1.5),
                    food=FoodConfig(items=16, radius=2.0, decay=1.0, clearance=0.5, smell_contrast=2.5, smell_tau=2.0,
                                    eat_from="root", eat_rule="surface", clear_from="root", eat_radius=0.35))
P801 = os.path.join(ROOT, "runs", "RBT-19", "P-801")
DESIGNED_HOSTS = ["best_gen0500.json", "best_gen0550.json", "best_gen0590.json", "best_gen0580.json"]
HOLISTIC_HOSTS = ["best_gen0000.json", "best_gen0330.json", "best_gen0390.json", "best_gen0450.json", "best_gen0480.json", "best_gen0510.json"]


@pytest.fixture
def t_point(monkeypatch, tmp_path):
    """Register a test-only point in steer's registries (monkeypatched: nothing persists), shrink the battery and pool,
    and write a fair-marked config for it."""
    raw = {"fairness": "fair", "sim": FIX_E2E.to_dict()}
    monkeypatch.setitem(steer.REGISTERED_POINTS, T_POINT, {"smell_contrast": 2.5, "smell_tau": 2.0, "eat_from": "root",
                                                           "eat_rule": "surface", "clear_from": "root", "eat_radius": 0.35})
    monkeypatch.setitem(steer.POOL_KEY, T_POINT, (116, 64, 999))
    monkeypatch.setitem(steer.POINT_SIM_HASH, T_POINT, steer.sim_hash(raw["sim"]))
    monkeypatch.setattr(steer, "FAIR_POINTS", steer.FAIR_POINTS | {T_POINT})
    for k, v in (("N_STAGE1", 2), ("N_STAGE2", 4), ("N_CONFIRM", 4), ("N_BATTERY", 10), ("POOL_SIZE", 16), ("POOL_EXTENSION", 8)):
        monkeypatch.setattr(steer, k, v)
    monkeypatch.setattr(planters, "N_HOSTS", 2)
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps(raw))
    hosts = tmp_path / "hosts"
    for i, seed in enumerate(planters.HOST_SEEDS):
        for kind, src, files in (("conventional", "conventional", DESIGNED_HOSTS), ("holistic", "holistic", HOLISTIC_HOSTS)):
            d = hosts / "O1" / str(seed) / "U" / kind / "final"
            d.mkdir(parents=True)
            for j, f in enumerate(files[i::3] if kind == "holistic" else files[i % len(files):][:2]):
                (d / f"{j:03d}.json").write_text(open(os.path.join(P801, src, f)).read())
    return {"config": str(cfg), "raw": raw, "hosts": str(hosts), "tmp": tmp_path}


def test_planted_end_to_end_at_a_test_point(t_point):
    out = t_point["tmp"] / "planted"
    assert planters.planted(T_POINT, t_point["config"], str(out), t_point["hosts"]) == 0
    log = (out / "planted.txt").read_text()
    pool = steer.draw_pool(T_POINT)
    assert f"tuning draws {[(d.terrain_seed, d.start_seed) for d in pool[:planters.N_TUNE]]}" in log  # the first 4 pool draws
    assert "tau 2.0 (registered 2.0)" in log and "carrying share" in log and "output links" in log
    table = json.loads((out / "reachability.json").read_text())
    assert all(row["hosts"] == 4 for row in table)  # the screen's hosts: 2 (a) + 2 (c)
    res = json.loads((out / "planted.json").read_text())
    assert {k: len(v) for k, v in res["calls"].items()} == {"a": 2, "b": 2, "c": 2, "d": 3, "e": 3, "motors-off": 2}
    assert all(r["call"] == steer.NONE and r["stage"] == 1 for k in ("d", "e", "motors-off") for r in res["calls"][k])
    bat = json.loads((out / "battery.json").read_text())
    assert [len(bat[k]) for k in ("stage1", "stage2", "confirm")] == [2, 4, 4]
    assert "# power at this point: tau 2 s" in log


def test_planted_refuses_when_too_few_hosts_carry_and_on_an_unfair_config(t_point, monkeypatch):
    monkeypatch.setattr(planters, "N_HOSTS", 3)  # only 2 holistic hosts carry G8(c) in the fixture pool's first walk? refuse if short
    import shutil
    for seed in planters.HOST_SEEDS:  # leave one holistic host per seed that cannot carry G8(c) (a tumbler)
        d = os.path.join(t_point["hosts"], "O1", str(seed), "U", "holistic", "final")
        shutil.rmtree(d)
        os.makedirs(d)
        planters.tumbler("rod").save(os.path.join(d, "000.json"))
    assert planters.planted(T_POINT, t_point["config"], str(t_point["tmp"] / "p2"), t_point["hosts"]) == 7
    assert "REFUSED: too few hosts" in (t_point["tmp"] / "p2" / "planted.txt").read_text()
    unfair = t_point["tmp"] / "unfair.json"
    unfair.write_text(json.dumps({**t_point["raw"], "fairness": None}))
    with pytest.raises(ValueError, match="fair"):
        planters.planted(T_POINT, str(unfair), str(t_point["tmp"] / "p3"), t_point["hosts"])


def _fake_run(root, n_holistic, n_designed, seasons=3):
    """A fake S run with committed bodies: founders by name, finals, history, cohorts."""
    run = root / "unit" / "S"
    counts = {"holistic": n_holistic, "conventional": n_designed}
    srcs = {"holistic": HOLISTIC_HOSTS, "conventional": DESIGNED_HOSTS}
    names = {}
    for kind, n in counts.items():
        (run / kind / "genomes").mkdir(parents=True)
        (run / kind / "final").mkdir(parents=True)
        names[kind] = [f"{kind[0]}{i}" for i in range(n)]
        for i, nm in enumerate(names[kind]):
            body = open(os.path.join(P801, kind, srcs[kind][i % len(srcs[kind])])).read()
            (run / kind / "genomes" / f"{nm}.json").write_text(body)
            (run / kind / "final" / f"{i:03d}.json").write_text(body)
    (run / "cohorts.jsonl").write_text(json.dumps({"season": 0, "groups": [[{"name": nm, "kind": k} for nm in names[k]] for k in counts]}) + "\n")
    (run / "history.json").write_text(json.dumps({"history": [{"season": s, "population": k} for s in range(seasons) for k in counts]}))
    return run


def test_probe_end_to_end_at_a_test_point(t_point, monkeypatch):
    monkeypatch.setattr(probe_members, "N_PROBE", 2)
    bat = steer.Battery(steer.draw_pool(T_POINT)[:2], steer.draw_pool(T_POINT)[2:6], steer.draw_pool(T_POINT)[6:10])
    bpath = t_point["tmp"] / "battery.json"
    bpath.write_text(json.dumps(bat.to_dict()))
    run = _fake_run(t_point["tmp"], n_holistic=6, n_designed=3)  # designed: fewer than N_MIN (5) -> MISSING
    out = t_point["tmp"] / "probes-3"
    assert probe_members.probe(str(run), 3, 129001, 129301, T_POINT, str(out), str(bpath), t_point["config"]) == 0
    res = json.loads((out / "probes.json").read_text())
    assert res["summary"]["conventional"] == {"status": "MISSING", "n": 3}
    assert res["summary"]["holistic"]["status"] == "PROBED" and res["summary"]["holistic"]["n"] == 2
    assert "# power at this point: tau 2 s" in (out / "probes.txt").read_text()
    with pytest.raises(ValueError, match="last completed season"):  # S2: a season that is neither 0 nor the last
        probe_members.probe(str(run), 2, 129001, 129301, T_POINT, str(t_point["tmp"] / "x"), str(bpath), t_point["config"])
    unfair = t_point["tmp"] / "unfair.json"
    unfair.write_text(json.dumps({**t_point["raw"], "fairness": None}))
    with pytest.raises(ValueError, match="fair"):
        probe_members.probe(str(run), 3, 129001, 129301, T_POINT, str(t_point["tmp"] / "y"), str(bpath), str(unfair))
    (run.parent / "EXTINCT.txt").write_text("EXTINCT pre-merge at season 41: ...\n")
    out2 = t_point["tmp"] / "probes-ext"
    assert probe_members.probe(str(run), 3, 129001, 129301, T_POINT, str(out2), str(bpath), t_point["config"]) == 0
    assert json.loads((out2 / "probes.json").read_text())["summary"]["holistic"]["status"] == "EXTINCT"


def test_probe_f_is_on_the_first_8_stage2_draws_and_shares_the_calls_seasons(t_point, monkeypatch):
    bat = steer.Battery(steer.draw_pool(T_POINT)[:2], steer.draw_pool(T_POINT)[2:14], steer.draw_pool(T_POINT)[14:16])
    pays = {(d.terrain_seed, d.start_seed) for d in bat.stage2[4:8]}  # intact pays on stage-2 draws 5-8 only
    calls = []

    def fake(point):
        def season(genome, cfg, draw, cond):
            calls.append(((draw.terrain_seed, draw.start_seed), cond))
            food = 1.0 if cond == "intact" and (draw.terrain_seed, draw.start_seed) in pays else 0.0
            return steer.Season(cond, draw, food, 0.0, food, False, 1, np.zeros((2, 2)), np.ones(1), np.ones(1), np.ones(1, bool))
        return season

    monkeypatch.setattr(probe_members.steer, "point_season", fake)
    f, rec = probe_members._probe((planters.tumbler("rod").to_dict(), FIX_E2E.to_dict(), bat.to_dict(), T_POINT))
    assert f == 0.5  # mean over the first 8 stage-2 draws (4 of 8 pay 1)
    assert len(calls) == len(set(calls))  # no season is run twice: f's seasons are the call's


def test_draw_members_is_the_registered_rng():
    paths = [f"m{i}" for i in range(30)]
    got = probe_members.draw_members(paths, 129301)
    assert got == [paths[i] for i in np.random.default_rng(129301).choice(30, 20, replace=False)]
    assert probe_members.N_PROBE == 20 and probe_members.N_MIN == 5 and probe_members.N_F == 8


# --------------------------------------------------------------------------- #
# The CLI at a registered point
# --------------------------------------------------------------------------- #


def test_cli_runs_at_the_points_tau_and_refuses_unfair_and_foreign_configs(t_point, capsys):
    bat = t_point["tmp"] / "bat.json"
    pool = steer.draw_pool(T_POINT)
    bat.write_text(json.dumps(steer.Battery(pool[:2], pool[2:6], pool[6:10]).to_dict()))
    g = t_point["tmp"] / "g.json"
    planters.tumbler("rod").save(str(g))
    assert steer.main(["--config", t_point["config"], "--battery", str(bat), "--world", T_POINT, str(g)]) == 0
    assert "NONE" in capsys.readouterr().out
    unfair = t_point["tmp"] / "unfair.json"
    unfair.write_text(json.dumps({**t_point["raw"], "fairness": None}))
    with pytest.raises(ValueError, match="fair"):
        steer.main(["--config", str(unfair), "--battery", str(bat), "--world", T_POINT, str(g)])
    other = t_point["tmp"] / "other.json"
    other.write_text(json.dumps({"fairness": "fair", "sim": replace(FIX_E2E, duration=4.0).to_dict()}))
    with pytest.raises(ValueError, match="committed block"):
        steer.main(["--config", str(other), "--battery", str(bat), "--world", T_POINT, str(g)])


def test_planted_and_probe_refuse_a_config_that_is_not_the_points_block(t_point):
    other = t_point["tmp"] / "other.json"
    other.write_text(json.dumps({"fairness": "fair", "sim": replace(FIX_E2E, duration=4.0).to_dict()}))
    with pytest.raises(ValueError, match="committed block"):
        planters.planted(T_POINT, str(other), str(t_point["tmp"] / "p"), t_point["hosts"])
    bat = t_point["tmp"] / "b.json"
    pool = steer.draw_pool(T_POINT)
    bat.write_text(json.dumps(steer.Battery(pool[:2], pool[2:6], pool[6:10]).to_dict()))
    run = _fake_run(t_point["tmp"], 6, 6)
    with pytest.raises(ValueError, match="committed block"):
        probe_members.probe(str(run), 3, 1, 1, T_POINT, str(t_point["tmp"] / "o"), str(bat), str(other))


def test_planted_call_runs_the_confirmation_k3_needs(monkeypatch):
    """A plant with stage-2 c2 and c3 but no confirmation (F < F_MIN) gets the confirmation battery's c2 and c3."""
    base = {"call": steer.NONE, "stage": 2, "stage2": {"c1": False, "c2": True, "c3": True, "F": 0.05}}
    monkeypatch.setattr(planters.steer, "call_genome", lambda *a, **k: dict(base))
    monkeypatch.setattr(planters.steer, "_pairs", lambda *a, **k: ({"intact": [1, 2], "decoy": [1, 2]}, []))
    monkeypatch.setattr(planters.steer, "battery_stats", lambda runs: {"c2": True, "c3": True})
    bat = steer.Battery(DRAWS[:2], DRAWS[2:4], DRAWS[4:6]).to_dict()
    rec = planters._call(({}, FIX_G.to_dict(), bat, G_POINT, True))
    assert rec["k3_confirm"] == {"c2": True, "c3": True} and planters.seen(rec)
    assert "k3_confirm" not in planters._call(({}, FIX_G.to_dict(), bat, G_POINT, False))  # (b), (d), (e): not needed


def test_holistic_pays_F_leg_at_a_test_point(t_point):
    """S7(c): holistic F = the mean over hosts of each host's stage-2 F, with a one-sided t bound over hosts."""
    out = t_point["tmp"] / "pays"
    assert planters.main(["pays", T_POINT, t_point["config"], str(out), "--hosts", t_point["hosts"]]) == 0
    res = json.loads((out / "holistic" / "pays.json").read_text())
    assert len(res["F"]) == 2 and res["mean"] == pytest.approx(np.mean(res["F"]))
    assert res["lb"] == pytest.approx(steer.lower_bound(res["F"]))
    txt = (out / "holistic" / "pays.txt").read_text()
    assert "carrying share" in txt and "HOLISTIC F" in txt and "two single-instance noses" in txt
