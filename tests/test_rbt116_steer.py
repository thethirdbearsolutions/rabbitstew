"""RBT-116's STEERS battery (runs/RBT-116/steer.py): planted positives and negatives (R7, R10), the lesion constant,
the decoy's rotation and spawn-clearance re-draw, the draw screen, the K / K + 2 reading, and determinism.

Every simulated test runs on a FIXTURE world (flat, 4 items in a 2 m disc, 10 s seasons, the merged contrast channel at
G = 2.5, τ = 2 s; the one-nose positive on the same world with 8 items and 15 s seasons) on fixed test draws.  None runs W1, its draw pool, or any RBT-116 host: no RBT-116 outcome is read.
"""
import importlib.util
import os
import sys
from dataclasses import replace

import mujoco
import numpy as np
import pytest

from rabbitstew.fixed import CHASSIS, LEFT_DRIVE, RIGHT_DRIVE, pioneer_genotype
from rabbitstew.genotype import Link, Neuron, Sensor, UnitRef
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, run_group, spawn_layout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("rbt116_steer", os.path.join(ROOT, "runs", "RBT-116", "steer.py"))
steer = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = steer
_spec.loader.exec_module(steer)

FIXTURE = SimConfig(duration=10.0, random_start=True, start_distance_range=(1.0, 1.5),
                    food=FoodConfig(items=4, radius=2.0, decay=1.0, smell_contrast=2.5, smell_tau=2.0))
#: the one-nose route pays less per season (R5-2), so its fixture is richer and longer: 8 items, 15 s
ONE_NOSE_WORLD = replace(FIXTURE, duration=15.0, food=replace(FIXTURE.food, items=8))
DRAWS = [steer.Draw(100 + i, 200 + i) for i in range(40)]
BATTERY = steer.Battery(DRAWS[:4], DRAWS[4:20], DRAWS[20:36])


# --------------------------------------------------------------------------- #
# Planted bodies (test-only planters; the registered G8 planters are gate.py's)
# --------------------------------------------------------------------------- #


def _pioneer(noses=(), throttle=0.6, seed=0, weights=0.0):
    """A Pioneer with food sensors only on ``noses`` (wheel Nodes), a constant forward throttle from the drive
    Effectors' biases (left − right is forward), and every evolved link at ``weights`` (0: silent)."""
    g = pioneer_genotype(np.random.default_rng(seed), hidden=0 if weights == 0.0 else 6, sources=("contact",))
    for _, b in g.brains():
        for link in b.links:
            link.weight = weights * link.weight if weights else 0.0
    for nd in noses:
        g.nodes[nd].segment.brain.units.append(Sensor("food"))
    g.nodes[LEFT_DRIVE].segment.brain.units[0].bias = +throttle
    g.nodes[RIGHT_DRIVE].segment.brain.units[0].bias = -throttle
    return g


def _unit(g, func):
    gb = g.global_brain
    gb.units.append(Neuron(0.0, func))
    return len(gb.units) - 1


def two_nose_steerer(w=8.0):
    """A compass: tanh(n_L − n_R) into the steering axis (the SUM of the drive commands; fixed.py's sign note)."""
    g = _pioneer(noses=(LEFT_DRIVE, RIGHT_DRIVE))
    k = _unit(g, "tanh")
    g.global_brain.links += [Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), -1.0), Link(UnitRef(RIGHT_DRIVE, 1), UnitRef(None, k), +1.0)]
    for nd in (LEFT_DRIVE, RIGHT_DRIVE):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    assert g.is_valid(), g.validate()
    return g


def one_nose_steerer(a=128.0, w=2.0, throttle=0.8):
    """Run-and-tumble on ONE nose (the body's only food sensor, on the left drive wheel): turn hard while the temporal
    contrast falls, run straight while it rises."""
    g = _pioneer(noses=(LEFT_DRIVE,), throttle=throttle)
    k = _unit(g, "relu")
    g.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), -a))
    for nd in (LEFT_DRIVE, RIGHT_DRIVE):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    assert g.is_valid(), g.validate()
    return g


def sensorless_mover(seed=3):
    """No food sensor at all; random evolved weights, so it moves (G8(d)'s kind)."""
    g = pioneer_genotype(np.random.default_rng(seed), sources=("contact",))
    g.nodes[LEFT_DRIVE].segment.brain.units[0].bias = +0.5
    g.nodes[RIGHT_DRIVE].segment.brain.units[0].bias = -0.5
    return g


def unwired_noses():
    """Two food sensors that nothing reads (G8(e)'s kind)."""
    return _pioneer(noses=(LEFT_DRIVE, RIGHT_DRIVE))


def _food_readings(sim):
    ks = [k for k, s in enumerate(sim.brains[0].sensors) if s.source == "food"]
    return sim.sensor_values(0, sim.contact_bodies())[ks]


# --------------------------------------------------------------------------- #
# Planted positives and negatives: the call can fire, and can stay silent (R7, R10)
# --------------------------------------------------------------------------- #


def test_two_nose_steerer_reads_steers():
    rec = steer.call_genome(two_nose_steerer(), FIXTURE, BATTERY)
    assert rec["call"] == steer.STEERS, steer.format_call("two-nose", rec)
    assert rec["stage2"]["F"] >= steer.F_MIN and rec["confirm"]["F"] >= steer.F_MIN


def test_one_nose_steerer_reads_steers():
    g = one_nose_steerer()
    assert sum(u.kind == "sensor" and u.source == "food" for _, b in g.brains() for u in b.units) == 1
    rec = steer.call_genome(g, ONE_NOSE_WORLD, BATTERY)
    assert rec["call"] == steer.STEERS, steer.format_call("one-nose", rec)


@pytest.mark.parametrize("make", [sensorless_mover, unwired_noses], ids=["no-food-sensor", "unwired-noses"])
def test_smell_blind_genomes_have_identical_trajectories_and_read_none(make):
    g = make()
    for d in DRAWS[:4]:
        runs = {c: steer.run_season(g, FIXTURE, d, c) for c in ("intact", "decoy", "lesion")}
        assert runs["intact"].disp > 0.05  # it moves, so the identity is not a body standing still
        assert not steer.trajectories_differ(runs["intact"], runs["decoy"])
        assert not steer.trajectories_differ(runs["intact"], runs["lesion"])
        assert runs["intact"].food == runs["decoy"].food == runs["lesion"].food
        assert runs["intact"].traj_hash == runs["decoy"].traj_hash
    rec = steer.call_genome(g, FIXTURE, BATTERY)
    assert rec["call"] == steer.NONE and rec["stage"] == 1 and rec["stage1_identical"] == steer.N_STAGE1


def test_decoy_takes_the_steerers_income_away():
    """The planted steerer's F comes from information: under the decoy it eats less, and its path differs."""
    g = two_nose_steerer()
    I = [steer.run_season(g, FIXTURE, d, "intact") for d in DRAWS[4:12]]
    D = [steer.run_season(g, FIXTURE, d, "decoy") for d in DRAWS[4:12]]
    assert np.mean([s.food for s in I]) - np.mean([s.food for s in D]) >= steer.F_MIN
    assert all(steer.trajectories_differ(a, b) for a, b in zip(I, D))


# --------------------------------------------------------------------------- #
# The lesion is the transform's zero-information constant (Amendment 1, item 5)
# --------------------------------------------------------------------------- #


def test_lesion_is_the_transforms_zero_information_constant():
    g = one_nose_steerer()
    cfg = replace(FIXTURE, settle_time=0.0)
    sim = Simulation([g], cfg, spawns=spawn_layout(2, cfg, 5)[:1])
    sim.set_food_seed(5)
    # a nose at its own baseline reads tanh(G · 0): on the first tick a lone nose is exactly there
    assert _food_readings(sim).tolist() == [steer.LESION_CONSTANT] == [float(np.tanh(cfg.food.smell_contrast * 0.0))]
    for _ in range(50):
        sim.step()
    assert _food_readings(sim)[0] != 0.0  # the intact nose is live once it moves
    lcfg = replace(cfg, food=replace(cfg.food, smell_lesion=True))
    sim = Simulation([two_nose_steerer()], lcfg, spawns=spawn_layout(2, lcfg, 5)[:1])
    sim.set_food_seed(5)
    for _ in range(100):
        assert _food_readings(sim).tolist() == [steer.LESION_CONSTANT] * 2
        sim.step()


def test_several_noses_read_their_spatial_offset_on_the_first_tick():
    """Amendment 1, item 3: only a lone nose reads 0 at the first reading; two noses read ±their offset."""
    cfg = replace(FIXTURE, settle_time=0.0)
    sim = Simulation([two_nose_steerer()], cfg, spawns=spawn_layout(2, cfg, 5)[:1])
    sim.set_food_seed(5)
    r = _food_readings(sim)
    assert r[0] != 0.0 and r[0] == pytest.approx(-r[1], abs=1e-12)


def test_lesion_season_changes_only_the_food_readings():
    g = sensorless_mover()
    a, b = steer.run_season(g, FIXTURE, DRAWS[0], "intact"), steer.run_season(g, FIXTURE, DRAWS[0], "lesion")
    assert not steer.trajectories_differ(a, b) and a.food == b.food and a.work == b.work


# --------------------------------------------------------------------------- #
# The decoy: rotation before the transform, spawn clearance, rotation invariance
# --------------------------------------------------------------------------- #


def test_theta_stream_is_registered_and_in_range():
    a = [th for _, th in zip(range(50), steer.theta_stream(12345))]
    b = [th for _, th in zip(range(50), steer.theta_stream(12345))]
    assert a == b and a != [th for _, th in zip(range(50), steer.theta_stream(12346))]
    assert all(np.radians(30) <= th <= np.radians(330) for th in a)


def test_decoy_redraws_theta_for_spawn_clearance():
    seed, root = 777, np.array([1.2, -0.4])
    th0 = next(steer.theta_stream(seed))
    blocker = steer.rotate(root[None, :], -th0)  # an item the first θ would rotate onto the root
    far = np.array([[0.0, 0.1]])  # an item near the origin, never within 0.8 m of the root under any rotation
    th, k = steer.draw_theta(seed, np.vstack([blocker, far]), root, 0.8)
    assert k >= 1 and th != th0
    assert np.linalg.norm(steer.rotate(np.vstack([blocker, far]), th) - root, axis=1).min() >= 0.8
    # with no blocker the first θ stands
    assert steer.draw_theta(seed, far, root, 0.8) == (th0, 0)


def test_decoy_season_clears_the_root_and_rotates_before_the_transform():
    g = two_nose_steerer()
    for d in DRAWS[:8]:
        s = steer.run_season(g, FIXTURE, d, "decoy")
        cfg = replace(steer.draw_sim(FIXTURE, d), opponent_proxy=True)
        sim = Simulation([g], cfg, spawns=[spawn_layout(2, cfg, d.start_seed)[0]])
        sim.set_food_seed(d.start_seed)
        root = sim.data.xpos[sim.robots[0].root_body][:2]
        assert np.linalg.norm(steer.rotate(sim.food_pos, s.theta) - root, axis=1).min() >= cfg.food.clearance
    # the decoy reads the rotated layout through the contrast channel, and eats from the real one
    cfg = replace(FIXTURE, settle_time=0.0)
    sp = spawn_layout(2, cfg, 9)[:1]
    real = Simulation([g], cfg, spawns=sp)
    real.set_food_seed(9)
    dec = steer.DecoySimulation([g], cfg, spawns=sp)
    dec.set_food_seed(9)
    dec._rot = 2.0
    moved = Simulation([g], cfg, spawns=sp)
    moved.set_food_seed(9)
    moved.food_pos = steer.rotate(moved.food_pos, 2.0)
    for sim in (real, dec, moved):
        sim.data.qpos[:2] += 0.05
        mujoco.mj_forward(sim.model, sim.data)
    rd = _food_readings(dec)
    assert rd.tolist() == _food_readings(moved).tolist() and rd.tolist() != _food_readings(real).tolist()
    assert np.array_equal(dec.food_pos, real.food_pos)  # the real items are untouched
    # the legacy reading is rotated too, so the decoy cannot fall back to the true layout under either
    lcfg = replace(cfg, food=replace(cfg.food, smell_contrast=0.0))
    a, b = Simulation([g], lcfg, spawns=sp), steer.DecoySimulation([g], lcfg, spawns=sp)
    a.set_food_seed(9)
    b.set_food_seed(9)
    b._rot = 2.0
    assert _food_readings(a).tolist() != _food_readings(b).tolist()


def test_rotation_invariance_is_asserted():
    steer.assert_rotation_invariant(FIXTURE, steer.DecoySimulation)

    class Skewed(steer.DecoySimulation):
        def _food_spot(self, avoid=None):
            return np.array([1.0, 0.0])

    with pytest.raises(ValueError, match="rotation invariance"):
        steer.assert_rotation_invariant(FIXTURE, Skewed)
    with pytest.raises(ValueError):
        steer.assert_rotation_invariant(replace(FIXTURE, food=None))


def test_motors_off_holds_every_command_at_zero():
    s = steer.run_season(two_nose_steerer(), FIXTURE, DRAWS[0], "motors-off")
    assert s.work == 0.0 and s.disp < 0.05


# --------------------------------------------------------------------------- #
# The season, T, and determinism
# --------------------------------------------------------------------------- #


def test_intact_season_is_the_selection_season():
    g = two_nose_steerer()
    for d in DRAWS[:3]:
        s = steer.run_season(g, FIXTURE, d, "intact")
        r = run_group([g], steer.draw_sim(FIXTURE, d), d.start_seed)[0]
        assert (s.food, s.work) == (r["food"], r["work"])


def test_chemotaxis_index_speed_bar_and_flag():
    s = steer.run_season(two_nose_steerer(), FIXTURE, DRAWS[1], "intact")
    t, flagged, excl = steer.chemotaxis_index(s, s.v_min())
    assert -1.0 <= t <= 1.0 and not flagged and 0.0 <= excl < 1.0
    t, flagged, excl = steer.chemotaxis_index(s, 1e9)  # no tick passes the bar
    assert (t, flagged, excl) == (0.0, True, 1.0)


def test_determinism():
    g = two_nose_steerer()
    for c in steer.CONDITIONS:
        a, b = steer.run_season(g, FIXTURE, DRAWS[2], c), steer.run_season(g.to_dict(), FIXTURE, DRAWS[2], c)
        assert np.array_equal(a.traj, b.traj) and a.food == b.food and a.theta == b.theta and np.array_equal(a.speed, b.speed)
    small = steer.Battery(DRAWS[4:6], DRAWS[6:8], DRAWS[8:10])
    assert steer.call_genome(g, FIXTURE, small) == steer.call_genome(g, FIXTURE, small)


# --------------------------------------------------------------------------- #
# The call's logic, on synthetic seasons
# --------------------------------------------------------------------------- #


def _season(cond, draw, food, proj_share, moved=True):
    n = 20
    traj = np.zeros((n + 1, 2))
    if moved:
        traj[:, 0] = np.linspace(0, 1, n + 1) + (0.5 if cond == "decoy" else 0.0)
    speed = np.ones(n)
    return steer.Season(cond, draw, float(food), 0.0, float(food), False, 10, traj, speed, speed * proj_share, np.ones(n, bool))


def _fake(table):
    """season(genome, cfg, draw, condition) from {condition: (food(draw), T(draw), moved)}."""
    def season(genome, cfg, draw, cond):
        f, t, moved = table.get(cond, table["intact"])
        return _season(cond, draw, f(draw), t(draw), moved)
    return season


def _jit(d):
    return (d.start_seed % 5) * 0.05


def test_call_logic_steers_smell_use_and_none():
    good = {"intact": (lambda d: 2.0 + _jit(d), lambda d: 0.5 + _jit(d), True), "decoy": (lambda d: 1.0, lambda d: 0.1, True)}
    assert steer.call_genome(None, FIXTURE, BATTERY, _fake(good))["call"] == steer.STEERS
    # food from smell but no net approach beyond the decoy's: SMELL-USE
    use = dict(good, decoy=(lambda d: 1.0, lambda d: 0.5 + _jit(d), True))
    assert steer.call_genome(None, FIXTURE, BATTERY, _fake(use))["call"] == steer.SMELL_USE
    # F below F_MIN: NONE
    weak = dict(good, decoy=(lambda d: 1.9 + _jit(d), lambda d: 0.1, True))
    assert steer.call_genome(None, FIXTURE, BATTERY, _fake(weak))["call"] == steer.NONE
    # identical trajectories on every stage-1 draw: stopped at stage 1
    same = {"intact": (lambda d: 2.0, lambda d: 0.5, False), "decoy": (lambda d: 1.0, lambda d: 0.1, False)}
    rec = steer.call_genome(None, FIXTURE, BATTERY, _fake(same))
    assert rec["call"] == steer.NONE and rec["stage"] == 1


def test_trajectory_veto_needs_more_than_half_the_draws():
    ids = {d.start_seed for d in BATTERY.stage2[:8]}  # differ on exactly half the stage-2 draws, and on stage 1
    ok = {d.start_seed for d in BATTERY.stage1}

    def season(genome, cfg, draw, cond):
        moved = draw.start_seed in ids or draw.start_seed in ok
        return _season(cond, draw, (2.0 + _jit(draw)) if cond == "intact" else 1.0, 0.5 if cond == "intact" else 0.1, moved)

    rec = steer.call_genome(None, FIXTURE, BATTERY, season)
    assert rec["stage2"]["differ"] == 8 and not rec["stage2"]["c3"] and rec["call"] == steer.NONE


def test_a_pass_the_confirmation_does_not_repeat_is_none():
    conf = {d.start_seed for d in BATTERY.confirm}

    def season(genome, cfg, draw, cond):
        gain = 0.0 if draw.start_seed in conf else 1.0
        return _season(cond, draw, (1.0 + gain + _jit(draw)) if cond == "intact" else 1.0, (0.1 + 0.4 * gain + _jit(draw)) if cond == "intact" else 0.1)

    rec = steer.call_genome(None, FIXTURE, BATTERY, season)
    assert rec["stage2"]["passes"] and rec["call"] == steer.NONE and rec["pass_unconfirmed"] and rec["stage"] == 3


def test_t_quantile_and_lower_bound():
    assert steer.t_quantile(0.95, 15) == pytest.approx(1.7530503557, abs=1e-8)
    assert steer.t_quantile(0.95, 1) == pytest.approx(6.3137515147, abs=1e-6)
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert steer.lower_bound(x) == pytest.approx(2.5 - 2.3533634348 * x.std(ddof=1) / 2, abs=1e-8)
    assert steer.lower_bound([0.5] * 16) == 0.5 and steer.lower_bound([1.0]) == -np.inf


# --------------------------------------------------------------------------- #
# The draw screen (M1)
# --------------------------------------------------------------------------- #


def test_pool_is_registered_and_extension_keeps_the_first_64():
    p, q = steer.draw_pool("W1"), steer.draw_pool("W1", extended=True)
    assert len(p) == 64 and len(q) == 96 and q[:64] == p and len(set(p)) == 64
    assert p[0] == steer.draw_pool("W1")[0]
    with pytest.raises(KeyError):
        steer.draw_pool("W9")


def _screen_season(ok):
    def season(host, cfg, draw, cond):
        assert cond == "intact"
        return _season(cond, draw, 1.0 if ok(host, draw) else 0.0, 0.0)
    return season


def test_screen_admits_by_half_the_hosts_and_assigns_in_pool_order():
    pool = steer.draw_pool("W1")
    bad = set(pool[::3])  # every third draw: only one of four hosts eats
    r = steer.screen_draws([0, 1, 2, 3], FIXTURE, "W1", _screen_season(lambda h, d: h < (2 if d not in bad else 1)))
    adm = [d for d in pool if d not in bad]
    assert r["passed"] and not r["extended"] and r["admissible"] == len(adm) == 42
    assert r["battery"].stage1 == adm[:4] and r["battery"].stage2 == adm[4:20] and r["battery"].confirm == adm[20:36]
    assert len(r["table"]) == 64 and sum(row["admissible"] for row in r["table"]) == 42


def test_screen_extends_once_then_fails():
    pool = steer.draw_pool("W1", extended=True)
    first = set(pool[:30])
    r = steer.screen_draws([0, 1], FIXTURE, "W1", _screen_season(lambda h, d: d in first or d in set(pool[64:69])))
    assert r["extended"] and not r["passed"] and r["battery"] is None and r["admissible"] == 35 and len(r["table"]) == 96
    r = steer.screen_draws([0, 1], FIXTURE, "W1", _screen_season(lambda h, d: d in first or d in set(pool[64:70])))
    assert r["extended"] and r["passed"] and r["battery"].confirm[-1] == pool[69]


# --------------------------------------------------------------------------- #
# Lines: K and K + 2, and the SMELL-USE print (R6-1)
# --------------------------------------------------------------------------- #


def test_line_reading_at_k_and_k_plus_2():
    S, U, N = steer.STEERS, steer.SMELL_USE, steer.NONE
    u = [S] * 6 + [U] * 4 + [N] * 30
    n = [S] * 1 + [U] * 1 + [N] * 38
    r = steer.line_reading(u, n)
    assert (r["K"], r["K2"]) == (5, 7)
    assert r["crossed_K"] and not r["crossed_K2"]
    assert r["smell_use_share_diff"] == pytest.approx(3 / 40)
    assert steer.line_reading([S] * 8 + [N] * 32, [N] * 40)["crossed_K2"]
    assert not steer.line_reading([S] * 5 + [N] * 35, [S] * 1 + [N] * 39)["crossed_K"]  # ≥ K, but not ≥ K above N
    line = steer.smell_use_print("unit 3 gen 48 holistic", r)
    assert "SMELL-USE U 0.100 N 0.025 U−N +0.075" in line and "K=5 yes, K+2=7 no" in line
