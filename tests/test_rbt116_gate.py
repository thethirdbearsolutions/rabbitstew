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


def test_gate_fixture_is_the_registered_fixture():
    """gate.py's run-time copy of the one-nose fixture (its fixture cell) is test_rbt116_steer's, as Amendment 3 used it."""
    for k, (cfg, bat) in (("F2", F2), ("F3", F3)):
        gcfg, gbat = gate.FIXTURE_VARIANTS[k]
        assert json.dumps(gcfg.to_dict(), sort_keys=True) == json.dumps(cfg.to_dict(), sort_keys=True)
        assert gbat.to_dict() == bat.to_dict()
    assert gate.fixture_host().to_dict() == _pioneer(noses=(), throttle=0.8).to_dict()


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
    nose, pattern, best = gate.fixture_plant(cfg, bat)
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
    r = gate._g7_host((g.to_dict(), [2.0, 6.0], cfg.to_dict(), bat.to_dict()))
    assert len(r["base"]) == 2 and set(r["rungs"]) == {"2", "6"}
    for row in r["rungs"].values():
        assert set(row) == {k + s for k in gate.INTERMEDIATES for s in "+-"} and all(len(v) == 2 for v in row.values())


# --------------------------------------------------------------------------- #
# Decision rules
# --------------------------------------------------------------------------- #


def test_g1_rule_is_the_smallest_rung_whose_mean_F_is_bounded_above_zero():
    F = {2.0: [0.1, -0.2, 0.0, 0.05] * 4, 6.0: [0.5, 0.4, 0.6, 0.3] * 4, 16.0: [1.0] * 16, 32.0: [2.0] * 16}
    assert gate.g1_decide(F) == 6.0
    assert gate.g1_decide({a: [0.0, -0.1] * 8 for a in gate.RUNGS}) is None


def test_tuning_excludes_a_refused_theta():
    """F10: a screening draw whose decoy finds no clear theta is excluded from that variant's F, not fatal."""
    class S:
        def __init__(self, food):
            self.food = food

    def season(g, cfg, d, cond):
        if cond == "decoy" and g.name == "a" and d == 1:
            raise steer.ThetaRefused("no theta")
        return S({"a": 3.0, "b": 2.0}[g.name] if cond == "intact" else (0.0 if d == 0 else 1.0))

    ga, gb = Genotype(name="a"), Genotype(name="b")
    best, F, table = gate.tune([ga, gb], None, [0, 1], season)
    assert table == [("a", 3.0, 1), ("b", 1.5, 0)] and best is ga
    def all_refused(g, cfg, d, cond):
        raise steer.ThetaRefused("x")
    assert gate.tune([ga], None, [0, 1], all_refused)[1] == float("-inf")


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
        calls = {"a": [S, S, N, N], "b": [N] * 4, "c": [S, N, None, None] if j <= 18 else [N, None, N, N], "f": [S, N, N, None]}
        _write(os.path.join(out, "g8"), f"unit{j:02d}.json", {"calls": calls})
    _write(out, "g8_controls.json", {"d": [N] * 3, "e": [N] * 3})
    s = gate.g8_summary(out)
    assert s["SENS_C_P"] == 0.5 and s["a_pass"]  # 0.5 >= 0.6 x 0.5
    assert s["c_units"] == 18 and s["SENS_c"] == pytest.approx(18 / 96) and not s["c_pass"]  # 0.1875 < 0.20
    assert s["SENS_C_H"] == pytest.approx(min(18 / 96, 0.25))
    assert len(s["flagged"]) == 6 and not s["flag_pass"]  # units 19..24 have no (c) STEERS: > 4 flagged
    assert s["b_pass"] and s["de_pass"]


def _g7_files(out, paying_rung):
    for i in range(16):
        h = {"base": [0.0] * 16, "host": f"h{i}", "first_rung": 6.0, "rungs": {}}
        for r in gate.RUNGS:
            row = {k + s: list(np.random.default_rng(i).normal(-0.5, 0.2, 16)) for k in gate.INTERMEDIATES for s in "+-"}
            if r == paying_rung:
                row["throttle+"] = list(np.random.default_rng(100 + i).normal(0.4, 0.05, 16))
            h["rungs"][f"{r:g}"] = row
        _write(os.path.join(out, "g7"), f"host{i:02d}.json", h)


def test_g7_fails_on_a_paying_intermediate_at_the_first_paying_rung_only(tmp_path):
    """G7 decides at the first paying rung (here a = 6); every rung is the printed table (finding 8)."""
    _g7_files(str(tmp_path / "x"), 6.0)
    s = gate.g7_summary(str(tmp_path / "x"))
    assert not s["pass"] and s["first_rung"] == "6" and s["rows"]["throttle+"]["lb_hosts"] > 0
    assert set(s["table"]) == {"2", "6", "16", "32"} and s["table"]["2"]["throttle+"]["lb_hosts"] < 0
    assert s["rows"]["pirouette+"]["lb_hosts"] < 0 and 0 <= s["rows"]["pirouette+"]["power_0.10"] <= 1
    _g7_files(str(tmp_path / "y"), 32.0)  # an intermediate paying only at another rung is printed, and does not fail G7
    s = gate.g7_summary(str(tmp_path / "y"))
    assert s["pass"] and s["table"]["32"]["throttle+"]["lb_hosts"] > 0


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
    probes; the holistic hosts are the permutation's first N whatever they carry (F3), each with its (c) layout or a
    refusal (NONE for (c)), and its (f) nose and turning sense or a refusal."""
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
    monkeypatch.setattr(gate, "N_HOLISTIC", 6)
    cfg = replace(ONE_NOSE_WORLD, duration=3.0)
    r = gate._hosts_unit((1, cfg.to_dict(), base))
    assert len(r["designed"]) == 1 and r["designed"][0]["sign"] in (1.0, -1.0)
    assert len(r["holistic"]) == 6  # no carrying filter (F3)
    order = gate.host_perm(1, 1, 6)
    assert [h["file"] for h in r["holistic"]] == [os.path.join(gate.b_dir(1, "holistic", base), f"{i:03d}.json") for i in order]
    for i, h in zip(order, r["holistic"]):
        if i % 2 == 0:  # the wheeled bodies carry both plants
            assert h["f_nose"] in (1, 2) and h["f_pattern"] == "common" and set(h["layout"]) == {"left", "right", "sides"}
        else:
            assert h["layout"] is None  # a random founder never carries (c) ...
        if h["layout"] is None:  # ... and every refusal is recorded, for (c) and for (f) separately
            assert any(f == h["file"] and why.startswith("(c) NONE") for f, why in r["refused"])
        if h["f_nose"] is None:
            assert any(f == h["file"] and why.startswith("(f) NONE") for f, why in r["refused"])
        else:
            assert h["f_pattern"] in gate.F_PATTERNS and h["f_sides"]
    # F3's point: a host that cannot carry (c) still gets (f)
    assert any(h["layout"] is None and h["f_nose"] is not None for h in r["holistic"])
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
    # F7a: every script gate.py loads is pinned by blob; F4: only "no checkpoint" (3) is accepted from a restore
    for path in ("runs/RBT-116/gate/gate.py", "runs/RBT-116/world.py", "runs/RBT-116/steer.py", "runs/RBT-116/planters.py",
                 "runs/RBT-116/power.py", "runs/RBT-97/routed_p801.py", "runs/RBT-113/world.py"):
        blob = subprocess.run(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        assert f"{blob} {path}" in b
    assert '[ "$rr" = 0 ] || [ "$rr" = 3 ] ||' in b and "exit 7" in b and "DecoyRefused" in b
    assert "fixture" in open(os.path.join(d, "gate-a.sh")).read()


def test_every_cell_but_config_and_fixture_refuses_without_the_fixture_check(tmp_path):
    for cell in sorted(gate.CELLS):
        if cell in ("config", "fixture"):
            continue
        with pytest.raises(SystemExit, match="G8\\(f\\) planter check"):
            gate.main([cell, "--out", str(tmp_path)])
    _write(str(tmp_path), "fixture_check.json", {"pass": False})
    with pytest.raises(SystemExit, match="planter check"):
        gate.main(["g8", "--out", str(tmp_path)])


def test_readout_refuses_without_every_input(tmp_path):
    """F1, F10: no pilot.json, no G9 or no G5 timing under every option -> the readout refuses (non-zero)."""
    _write(str(tmp_path), "fixture_check.json", {"pass": True})
    with pytest.raises(SystemExit, match="pilot.json"):
        gate.main(["readout", "--out", str(tmp_path)])
    for f in gate.READOUT_INPUTS:
        if f != os.path.join("g9", "HP.json"):
            _write(os.path.dirname(os.path.join(str(tmp_path), f)), os.path.basename(f), {"D16": {}, "D8": {}, "DF16": {}} if f == "g5.json" else {})
    with pytest.raises(SystemExit, match="HP.json"):
        gate.main(["readout", "--out", str(tmp_path)])
    _write(os.path.join(str(tmp_path), "g9"), "HP.json", {})
    _write(str(tmp_path), "g5.json", {"D16": {}, "D8": {}})
    with pytest.raises(SystemExit, match="g5.json:DF16"):
        gate.main(["readout", "--out", str(tmp_path)])
    with pytest.raises(SystemExit, match="every draws option"):
        gate.main(["g6-pick", "--out", str(tmp_path)])


def test_no_K_meeting_the_rule_stops_for_a_ruling(monkeypatch):
    """F2: there is no fallback K."""
    noise = {"holistic": (0.336, 1.158), "conventional": (0.056, 1.343)}
    u = {"holistic": (0.146, 1), "conventional": (0.28, 1)}
    eps = {"holistic": {"EPS_C": 0.005}, "designed": {"EPS_C": 0.005}}
    monkeypatch.setattr(gate.power, "row", lambda *a, **k: ({"HOLISTIC MORE READILY": 10 ** 9}, 0.0))
    pw = gate.power_rerun(0.48, 0.32, eps, noise, u, 16, reps=2)
    assert pw["K"] is None and [k for k, _ in pw["K_table"]] == [3, 4, 5, 6, 7, 8, 9]


def test_cost_tables_print():
    t = lanes.cost_text()
    assert "TOTAL" in t and "DF16" in t and "D8" in t
    for opt in ("D16", "D8", "DF16"):
        c = lanes.arm_cost(opt)
        assert c["24 units"] == pytest.approx(24 * c["unit"])


def _complete_gate_dir(out, held=True):
    """Every cell's output for a passing synthetic W1 gate (shapes as the cells write them)."""
    _write(out, "fixture_check.json", {"pass": True})
    open(os.path.join(out, "screen.txt"), "w").write("host 0: x\nSCREEN PASS: 40 admissible of 64\n")
    _write(out, "g1.json", {"c_G1": 0.5, "G1": True, "G2": {"pass": True}, "first_rung": 6.0})
    open(os.path.join(out, "g1.txt"), "w").write("# G1\nG1 PASS: first paying rung 6.0\nG2 PASS: F 1.0 against 0.2\n")
    S, N = {"call": steer.STEERS, "stage2": {"F": 1.0}}, {"call": steer.NONE, "stage2": {"F": 0.0}}
    for j in W.UNITS:
        _write(os.path.join(out, "g8"), f"unit{j:02d}.json", {"calls": {"a": [S, S, N, N], "b": [N] * 4, "c": [S, N, None, N], "f": [S, N, N, None]}})
        _write(os.path.join(out, "g6_noise"), f"unit{j:02d}.json", {k: {"sb": 0.3, "sw": 1.2} for k in ("holistic", "conventional")})
    _write(out, "g8_controls.json", {"d": [N] * 3, "e": [N] * 3})
    for fauna in (0, 1):
        _write(os.path.join(out, "g4"), f"fauna{fauna}_0of1.json", {"calls": [N] * 199 + [S]})
    _write(os.path.join(out, "g6_u"), "parent0000.json", {"fauna": 0, "lost": 8, "n": 40})
    _write(os.path.join(out, "g6_u"), "parent0001.json", {"fauna": 1, "lost": 6, "n": 40})
    _write(out, "g5.json", {o: {"per_generation": 100.0} for o in W.DRAWS_OPTIONS})
    _write(out, "g6.json", {"chosen": "D16", "conditional": False})
    open(os.path.join(out, "g6.txt"), "w").write("G6 default: D16\n")
    _write(out, "pilot.json", {k: {"steers": 10 if held else 0, "n": 40} for k in ("conventional", "holistic")})
    _g7_files(out, 32.0)
    row = [[[2.0, 100.0, 1.0, 30, 6.0, 0.2]] * 16]
    groups = [f"{g}/{k}/intact" for g in ("founders", "r113-final", "burn-in-final") for k in ("holistic", "conventional")]
    groups += [f"r113-final/{k}/lesion" for k in ("holistic", "conventional")] + ["g8a/conventional/intact"]
    for w in gate.CENSUS_WORLDS:
        _write(os.path.join(out, "g9"), f"{w}.json", {g: row * 24 for g in groups})


def test_readout_end_to_end_on_synthetic_inputs(tmp_path, monkeypatch):
    fake = {"Q_H": 0.7, "Q_P": 0.5, "EPS_C": 0.005, "K_table": [(3, 0.5), (4, 0.02), (5, 0.005)], "K": 5,
            "detect_at_K": 0.85, "detect_headlined": 0.81, "stronger_no": True}
    monkeypatch.setattr(gate, "power_rerun", lambda *a, **k: dict(fake))
    out = str(tmp_path / "pass")
    _complete_gate_dir(out)
    assert gate.main(["readout", "--out", out]) == 0
    txt = open(os.path.join(out, "GATE.txt")).read()
    assert "W1 GATE: PASS" in txt and "G6 conditional_sentence: no" in txt and "regrow_delay of 0" in txt
    assert "a =  6 throttle+" in txt and "<- decides" in txt and "K = 5" in txt and "REGISTERED" in txt
    g = json.load(open(os.path.join(out, "gate.json")))
    assert "G6-pilot" not in g["ok"] and g["conditional_sentence"] is False  # F1: the pilot is not a pass/fail row
    out = str(tmp_path / "unheld")
    _complete_gate_dir(out, held=False)
    assert gate.main(["readout", "--out", out]) == 0  # still a PASS: an unheld pilot only sets the conditional sentence
    assert json.load(open(os.path.join(out, "gate.json")))["conditional_sentence"] is True
    monkeypatch.setattr(gate, "power_rerun", lambda *a, **k: {"Q_H": 0.7, "Q_P": 0.5, "EPS_C": 0.005, "K_table": [(k, 0.5) for k in range(3, 10)], "K": None})
    assert gate.main(["readout", "--out", out]) == 13  # F2
    assert "STOPPED FOR A RULING" in open(os.path.join(out, "GATE.txt")).read()


# --------------------------------------------------------------------------- #
# RBT116-PILOT-10: the pilot pooled over every unit (D), and its refusal (A)
# --------------------------------------------------------------------------- #


def _pilot_dir(out, holistic_paying=24, base=None):
    """A synthetic gate directory for pilot-prep: hosts, g8 records (with genomes and recorded stage-2 F), g1.json, and
    PILOT_UNIT's burn-in populations.  Designed (a) plant of unit j, host k has F = 0.25 + 0.01 (j + k) except where
    set; holistic (c) plants: host 0 carries with F (j - 12) / 10 for the first ``holistic_paying`` units' order, host
    1 cannot carry (c) (F3: None), host 2's call stopped at stage 1 (no recorded F)."""
    g = _forager()
    host_file = os.path.join(out, "host.json")
    os.makedirs(out, exist_ok=True)
    g.save(host_file)
    h = random_genotype(np.random.default_rng(3), vocab=BrainVocabulary.named("foraging"))
    for j in W.UNITS:
        _write(os.path.join(out, "hosts"), f"unit{j:02d}.json", {"unit": j, "designed": [{"file": host_file, "sign": 1.0, "backward": False}] * 2,
               "holistic": [{"file": host_file}] * 3, "refused": []})
        a_plants, a_calls = [], []
        for k in range(2):
            p = g.copy()
            p.name = f"c12-{k}+a6+"  # as in the gate: host names repeat across units
            a_plants.append(p.to_dict())
            a_calls.append({"call": steer.NONE, "stage2": {"F": 0.25 + 0.01 * (j + k) if (j, k) != (3, 0) else -0.5}})
        c0 = h.copy()
        c0.name = "h12-0+c32/2+"
        F_c = (j - 12) / 10 if j <= holistic_paying else -1.0
        c2 = h.copy()
        c2.name = "h12-2+c8/2-"
        _write(os.path.join(out, "g8"), f"unit{j:02d}.json", {"unit": j, "rung": 6.0,
               "calls": {"a": a_calls, "b": [], "c": [{"call": steer.NONE, "stage2": {"F": F_c}}, None, {"call": steer.NONE, "stage": 1}], "f": []},
               "plants": {"a": a_plants, "b": [], "c": [c0.to_dict(), None, c2.to_dict()], "f": []}})
    _write(out, "g1.json", {"hosts": [[1, host_file]], "rows": {"2": {"F": [0.30]}, "6": {"F": [0.27]}, "16": {"F": [None]}, "32": {"F": [-0.1]}}})
    for kind in ("conventional", "holistic"):
        d = gate.b_dir(gate.PILOT_UNIT, kind, base)
        os.makedirs(d, exist_ok=True)
        for i in range(10):
            (g if kind == "conventional" else h).save(os.path.join(d, f"{i:03d}.json"))
    _write(out, "fixture_check.json", {"pass": True})


def test_pilot_candidates_pool_every_unit_with_recorded_F_only(tmp_path):
    out = str(tmp_path / "gate")
    _pilot_dir(out, base=str(tmp_path / "base"))
    c = gate.pilot_candidates(out, gate.all_hosts(out))
    # designed: 24 units x 2 hosts of g8 (a), plus G1 host (1, 0) at rungs 2 and 32 (rung 6 is the g8 plant itself; rung 16
    # has no recorded F); holistic: host 0 only (host 1 cannot carry (c); host 2 has no recorded F) -- F3, without error
    assert len(c[0]) == 48 + 2 and len(c[1]) == 24
    assert all(key[1] == 0 for key, _, _ in c[1]) and [key for key, _, _ in c[0]] == sorted(key for key, _, _ in c[0])
    assert gate.c_w({"name": "x+c32/2+"}) == 16.0 and gate.c_w({"name": "y+c8/2-"}) == 4.0


def test_pilot_pick_is_the_8_nearest_F_MIN_above_0_ties_in_fixed_order():
    mk = lambda key, F: (key, F, {"name": str(key)})  # noqa: E731
    cands = [mk((2, 0, 6.0), 0.30), mk((1, 1, 6.0), 0.20), mk((1, 0, 6.0), 0.30), mk((5, 0, 6.0), -0.25),
             mk((4, 0, 6.0), 0.0), mk((3, 0, 6.0), 0.25)] + [mk((9, k, 6.0), 1.0 + k) for k in range(5)]
    got = [key for key, _, _ in gate.pick_pilot(cands)]
    # 0.25 first; then 0.30, 0.30 and 0.20 (all 0.05 away: the fixed (unit, host, rung) order); F <= 0 never
    assert got == [(3, 0, 6.0), (1, 0, 6.0), (1, 1, 6.0), (2, 0, 6.0), (9, 0, 6.0), (9, 1, 6.0), (9, 2, 6.0), (9, 3, 6.0)]
    assert gate.pick_pilot(list(reversed(cands))) == gate.pick_pilot(cands)  # deterministic whatever the input order


def test_pilot_prep_plants_8_pooled_steerers_into_the_pilot_unit(tmp_path):
    out, base = str(tmp_path / "gate"), str(tmp_path / "base")
    _pilot_dir(out, base=base)
    _write(out, "pilot.json", {"refused": True})  # a stale refusal is replaced
    assert gate.main(["pilot-prep", "--out", out, "--base", base]) == 0
    assert not os.path.exists(os.path.join(out, "pilot.json"))
    prep = json.load(open(os.path.join(out, "pilot", "pilot_prep.json")))
    assert prep["paying"] == {"designed": 48, "holistic": 12}
    for kind, fauna in (("conventional", "0"), ("holistic", "1")):
        files = sorted(os.listdir(os.path.join(out, "pilot", "start", kind)))
        assert len(files) == 10
        names = [json.load(open(os.path.join(out, "pilot", "start", kind, f)))["name"] for f in files]
        assert all(n.startswith("pilot") for n in names[:8]) and not any(n.startswith("pilot") for n in names[8:])
        assert [p[0] for p in prep["picked"][fauna]] == [n.split("-", 1)[1] for n in names[:8]]
        assert len({tuple(p[2]) for p in prep["picked"][fauna]}) == 8  # 8 distinct (unit, host, rung or w)
    assert all(abs(F - 0.25) <= 0.08 for _, F, _ in prep["picked"]["0"])  # the designed picks hug F_MIN
    assert "rabbitstew.cli" in gate.pilot_command(out, "D16")


def test_pilot_refusal_counts_both_faunas_and_sets_the_conditional_sentence(tmp_path, monkeypatch):
    out, base = str(tmp_path / "gate"), str(tmp_path / "base")
    _pilot_dir(out, holistic_paying=19, base=base)  # holistic F > 0 only for units 13..19: 7 paying, fewer than 8
    assert gate.main(["pilot-prep", "--out", out, "--base", base]) == 0
    pil = json.load(open(os.path.join(out, "pilot.json")))
    assert pil["refused"] is True and pil["paying"] == {"designed": 48, "holistic": 7}  # both faunas counted
    assert not os.path.exists(os.path.join(out, "pilot", "start"))
    cmd = gate.pilot_command(out, "D16")
    assert "rabbitstew.cli" not in cmd and cmd[cmd.index("--generations") + 1] == "0"  # the lane's evolve step is a no-op
    assert subprocess.run(cmd).returncode == 0
    assert gate.main(["pilot-probe", "--out", out]) == 0 and json.load(open(os.path.join(out, "pilot.json"))) == pil
    # the readout: the refused pilot is the registered "Otherwise": the conditional sentence, no pass/fail row
    fake = {"Q_H": 0.7, "Q_P": 0.5, "EPS_C": 0.005, "K_table": [(5, 0.005)], "K": 5, "detect_at_K": 0.85, "detect_headlined": 0.81, "stronger_no": True}
    monkeypatch.setattr(gate, "power_rerun", lambda *a, **k: dict(fake))
    r = str(tmp_path / "readout")
    _complete_gate_dir(r)
    _write(r, "pilot.json", pil)
    assert gate.main(["readout", "--out", r]) == 0
    txt = open(os.path.join(r, "GATE.txt")).read()
    assert "could not be built" in txt and "G6 conditional_sentence: YES" in txt and "W1 GATE: PASS" in txt
    g = json.load(open(os.path.join(r, "gate.json")))
    assert g["conditional_sentence"] is True and "G6-pilot" not in g["ok"]
    os.remove(os.path.join(r, "pilot.json"))
    with pytest.raises(SystemExit, match="pilot.json"):  # F10 kept: a MISSING pilot.json still refuses
        gate.main(["readout", "--out", r])
