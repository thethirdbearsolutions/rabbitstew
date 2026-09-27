"""RBT-125: the perception pack -- the smell contrast channel and the eating rules (runs/RBT-125/DESIGN.md).

* Off (the defaults) is byte-identical: RBT-113's two tiny `evolve` runs, one of them in the foraging world, write
  the config.json, lineage.jsonl, history.json and state.json whose digests were recorded before RBT-113's hook,
  with every RBT-125 flag passed explicitly at its off value; and the legacy food reading is the squashed intensity.
* The contrast channel: a lone nose moving up a gradient reads > 0 (the temporal route), down it < 0, and standing
  still it reads 0; two symmetric noses in a symmetric field read exactly 0; a root nose is not zeroed.
* The eating rules: the Pioneer's root is its chassis; `sensor` eats from the chassis and the drive wheels; a
  caster eats only under `any`; `surface` eats by the part's surface and not in the air; `clear_from=geoms`.
"""
import json
import platform
from dataclasses import replace

import mujoco
import numpy as np
import pytest

from rabbitstew.cli import _sim_config, build_parser, evolve_config
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.fixed import CASTER, CHASSIS, LEFT_DRIVE, RIGHT_DRIVE, pioneer_genotype
from rabbitstew.genotype import Brain, Connection, Genotype, JointType, Node, Segment, Sensor, Shape, random_genotype
from rabbitstew.simulation import PERCEPTION_DEFAULTS, FoodConfig, SimConfig, Simulation
from rabbitstew.world import Spawn

from test_rbt113 import GOLDEN, A, B, _run, _sha

OFF = ["--smell-contrast", "0", "--smell-tau", "2", "--eat-from", "any", "--eat-rule", "centre", "--clear-from", "root"]
FORAGING = ("food", "contact")


def _cfg(**food):
    sc = SimConfig(settle_time=0.0, food=FoodConfig(**food))
    return sc


def _place(sim, x, y, yaw=0.0):
    """Put robot 0's root at (x, y) facing yaw, and recompute the kinematics (no physics step)."""
    adr = sim.robots[0].root_qpos_adr
    sim.data.qpos[adr:adr + 2] = (x, y)
    sim.data.qpos[adr + 3:adr + 7] = (np.cos(yaw / 2), 0.0, 0.0, np.sin(yaw / 2))
    mujoco.mj_forward(sim.model, sim.data)


def _body(root_nose: bool, side_noses: int) -> Genotype:
    """A box root with 0, 1 or 2 welded side spheres at +y / -y; each side sphere carries one food nose."""
    root = Segment(Shape.BOX, (1.0, 1.0, 1.0))
    root.brain.units = [Sensor("food")] if root_nose else [Sensor("contact")]
    nose = Segment(Shape.SPHERE, (1.0,))
    nose.brain.units = [Sensor("food")]
    conns = [Connection(child=1, position=(0.0, side, 0.0), orientation=(0.0, 0.0, 0.0), scale=0.4, joint_type=JointType.FIXED,
                        recursive_limit=1, joint_limit=None) for side in (1.0, -1.0)[:side_noses]]
    return Genotype(nodes=[Node(root, conns), Node(nose)], root=0, global_brain=Brain(), name="noses")


def _food(sim, pts):
    pts = np.asarray(pts, float).reshape(-1, 2)
    sim._install_spots(pts, np.ones(len(pts), bool), np.zeros(len(pts)), np.zeros((0, 2)))


def _food_readings(sim):
    ks = [k for k, s in enumerate(sim.brains[0].sensors) if s.source == "food"]
    v = sim.sensor_values(0, set())
    return v[ks]


# --- off is byte-identical ---------------------------------------------------------------------------------------

@pytest.mark.skipif(platform.machine() != "x86_64", reason="digests recorded on x86_64 (RBT-96)")
def test_off_is_byte_identical_to_the_pre_pack_code(tmp_path):
    _run(A + OFF, tmp_path / "a")
    _run(B + OFF, tmp_path / "b")
    assert {k: _sha(tmp_path / k) for k in GOLDEN} == GOLDEN


def test_off_writes_no_perception_key_and_on_round_trips():
    off = evolve_config(build_parser().parse_args(["evolve"] + B + OFF + ["--out", "/nonexistent"]))
    for d in (off.to_dict()["sim"]["food"], off.sim.to_dict()["food"]):
        assert not set(PERCEPTION_DEFAULTS) & set(d)
    on = evolve_config(build_parser().parse_args(["evolve"] + B + ["--smell-contrast", "2.5", "--smell-tau", "3", "--eat-from", "root",
                                                                    "--eat-rule", "surface", "--clear-from", "geoms", "--out", "/nonexistent"]))
    d = json.loads(json.dumps(on.to_dict()))
    assert d["sim"]["food"]["smell_contrast"] == 2.5 and d["sim"]["food"]["eat_from"] == "root"
    f = EvolutionConfig.from_dict(d).sim.food
    assert (f.smell_contrast, f.smell_tau, f.eat_from, f.eat_rule, f.clear_from) == (2.5, 3.0, "root", "surface", "geoms")
    assert SimConfig.from_dict(on.sim.to_dict()).food == on.sim.food


@pytest.mark.parametrize("cmd", ["evolve", "simulate", "ecology"])
def test_the_flags_reach_the_food_config_from_every_command(cmd):
    extra = ["--out", "/nonexistent"] if cmd != "simulate" else ["g.json"]
    args = build_parser().parse_args([cmd, "--food-items", "12", "--smell-contrast", "10", "--eat-from", "sensor"] + extra)
    f = _sim_config(args).food
    assert f.smell_contrast == 10.0 and f.eat_from == "sensor"


@pytest.mark.parametrize("bad", [dict(eat_from="mouth"), dict(eat_rule="edge"), dict(clear_from="all"), dict(smell_contrast=-1.0), dict(smell_tau=0.0)])
def test_bad_values_are_refused(bad):
    with pytest.raises(ValueError):
        FoodConfig(**bad)


def test_off_reading_is_the_legacy_squashed_intensity():
    """With the contrast off, a food sensor reads S / (1 + S) (sum mode), written out here independently."""
    sim = Simulation([_body(True, 2)], _cfg(), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
    _food(sim, [(1.0, 0.3), (-2.0, 1.0)])
    got = _food_readings(sim)
    for k, v in zip([k for k, s in enumerate(sim.brains[0].sensors) if s.source == "food"], got):
        p = sim.data.geom_xpos[sim.robots[0].geoms[sim.brains[0].sensors[k].part]][:2]
        S = sum(np.exp(-np.linalg.norm(np.array(q) - p)) for q in [(1.0, 0.3), (-2.0, 1.0)])
        assert v == pytest.approx(S / (1 + S), abs=1e-12)
    assert sim._smell_base == [None]  # the baseline is never touched when the channel is off


def test_explicit_off_values_equal_the_defaults_bitwise():
    """The flags passed at their off values run the same bout, bit for bit, as the defaults (the RBT-125 adversary's
    C3: this is not the pre-pack proof -- `test_off_is_byte_identical_to_the_pre_pack_code` carries that)."""
    g = pioneer_genotype(np.random.default_rng(5), sources=FORAGING)
    base = SimConfig(food=FoodConfig(), random_start=True)
    off = SimConfig(food=FoodConfig(**PERCEPTION_DEFAULTS), random_start=True)
    runs = []
    for cfg in (base, off):
        sim = Simulation([g], cfg, spawns=[Spawn(position=(1.0, 0.5, 0.0), yaw=0.3)])
        sim.set_food_seed(4)
        sim.run(3.0)
        runs.append((sim.data.qpos.copy(), sim.food_eaten.copy(), sim.work.copy(), sim.food_pos.copy()))
    for a, b in zip(*runs):
        assert np.array_equal(a, b)


# --- the contrast channel ----------------------------------------------------------------------------------------

def test_a_lone_nose_reads_the_temporal_gradient():
    """One nose (on the root), one item at the origin. Moving towards it the nose reads > 0, and more the faster it
    moves; moving away it reads < 0; stopped, the reading decays to 0 (the baseline catches up)."""
    cfg = _cfg(smell_contrast=2.5, decay=1.5)
    sim = Simulation([_body(True, 0)], cfg, spawns=[Spawn(position=(3.0, 0.0, 0.5))])
    _food(sim, [(0.0, 0.0)])
    x = 3.0
    _place(sim, x, 0.0)
    assert _food_readings(sim)[0] == 0.0  # the first reading starts the baseline at itself
    ups = []
    for _ in range(50):  # 1 s at 0.5 m/s towards the item
        x -= 0.5 * cfg.control_dt
        _place(sim, x, 0.0)
        ups.append(_food_readings(sim)[0])
    assert min(ups) > 0 and ups[-1] > ups[0]
    for _ in range(500):  # stand still for 10 s = 5 tau
        still = _food_readings(sim)[0]
    assert 0 <= still < 0.01
    downs = []
    for _ in range(50):
        x += 0.5 * cfg.control_dt
        _place(sim, x, 0.0)
        downs.append(_food_readings(sim)[0])
    assert max(downs) < 0


def test_the_lone_nose_signal_is_g_times_tau_times_the_log_slope():
    """At steady speed v up a slope s = d ln S / dx = 1 / decay, the EMA lags by v s tau: the reading tends to
    tanh(G v tau / decay) (DESIGN.md's parity table)."""
    G, tau, decay, v = 2.5, 2.0, 1.5, 0.25
    cfg = _cfg(smell_contrast=G, smell_tau=tau, decay=decay)
    sim = Simulation([_body(True, 0)], cfg, spawns=[Spawn(position=(9.0, 0.0, 0.5))])
    _food(sim, [(0.0, 0.0)])
    x = 9.0
    for _ in range(int(8 * tau / cfg.control_dt)):
        x -= v * cfg.control_dt
        _place(sim, x, 0.0)
        r = _food_readings(sim)[0]
    assert r == pytest.approx(np.tanh(G * v * tau / decay), rel=0.02)


def test_two_symmetric_noses_in_a_symmetric_field_read_zero():
    """Two noses at +y / -y and no root nose; items on the body's x axis, so the field is the same at both noses.
    At rest both read exactly 0, from the first reading on.  Moving along the axis they read the same value (the
    common, temporal term), so their difference -- what a two-nose steerer turns on -- stays exactly 0."""
    sim = Simulation([_body(False, 2)], _cfg(smell_contrast=10.0, decay=1.5), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
    _food(sim, [(2.0, 0.0), (-1.0, 0.0), (3.5, 0.0)])
    _place(sim, 0.0, 0.0)
    for _ in range(3):
        r = _food_readings(sim)
        assert len(r) == 2 and np.all(r == 0.0)
    for x in (0.1, 0.2, 0.3):
        _place(sim, x, 0.0)
        left, right = _food_readings(sim)
        assert left == right and left != 0.0
    # an arena with nothing standing (every item parked): 0 again at rest
    sim = Simulation([_body(False, 2)], _cfg(smell_contrast=10.0), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
    _food(sim, np.full((3, 2), 1e6))
    _place(sim, 0.0, 0.0)
    assert np.all(_food_readings(sim) == 0.0)


def test_two_noses_read_the_spatial_contrast_with_gain_g():
    """An item off to the left: the left nose reads > 0 > the right, and L - R ~ G (ln S_L - ln S_R) while small."""
    G = 2.5
    sim = Simulation([_body(False, 2)], _cfg(smell_contrast=G, decay=1.5), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
    _food(sim, [(0.5, 4.0)])
    _place(sim, 0.0, 0.0)
    left, right = _food_readings(sim)  # +y first
    assert left > 0 > right and left == pytest.approx(-right, rel=1e-9)
    pl, pr = (sim.data.geom_xpos[g][:2] for g in sim.robots[0].geoms[1:3])
    dx = (np.linalg.norm(pr - (0.5, 4.0)) - np.linalg.norm(pl - (0.5, 4.0))) / 1.5
    assert left - right == pytest.approx(2 * np.tanh(G * dx / 2), rel=1e-9)


def test_a_root_nose_is_not_zeroed():
    """The refused design (root-centring) reads a root nose as identically 0; the running baseline does not."""
    sim = Simulation([_body(True, 2)], _cfg(smell_contrast=2.5, decay=1.5), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
    _food(sim, [(3.0, 0.0)])  # ahead of the root, on the axis: the root nose is the nearest
    _place(sim, 0.0, 0.0)
    root, left, right = _food_readings(sim)
    assert root != 0.0 and left == right
    # and it moves with the root's own path: 1 s towards the item raises it
    for i in range(50):
        _place(sim, 0.01 * (i + 1), 0.0)
        now = _food_readings(sim)[0]
    assert now > root


def test_the_pioneer_carries_three_noses_under_the_contrast_and_steers_on_the_wheel_difference():
    g = pioneer_genotype(np.random.default_rng(5), sources=FORAGING)
    sim = Simulation([g], _cfg(smell_contrast=2.5), spawns=[Spawn(position=(0.0, 0.0, 0.0))])
    parts = [s.part for s in sim.brains[0].sensors if s.source == "food"]
    nodes = [sim.phenotypes[0].parts[p].node for p in parts]
    assert sorted(nodes) == [CHASSIS, LEFT_DRIVE, RIGHT_DRIVE]
    _food(sim, [(1.0, 3.0)])  # ahead and to the left
    r = dict(zip(nodes, _food_readings(sim)))
    assert r[LEFT_DRIVE] > r[RIGHT_DRIVE]


def test_the_contrast_ignores_the_smell_mode():
    """sum and mean differ by a constant in ln S, and log is not used: the contrast reads the same under all three."""
    out = []
    for mode in ("sum", "mean", "log"):
        sim = Simulation([_body(True, 2)], _cfg(smell_contrast=2.5, smell=mode), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
        _food(sim, [(1.0, 2.0), (-2.0, 0.5)])
        _place(sim, 0.0, 0.0)
        _food_readings(sim)
        _place(sim, 0.05, 0.02)
        out.append(_food_readings(sim))
    assert np.array_equal(out[0], out[1]) and np.array_equal(out[0], out[2])


def test_the_baseline_restarts_with_every_simulation():
    sims = []
    for _ in range(2):
        sim = Simulation([_body(True, 0)], _cfg(smell_contrast=2.5), spawns=[Spawn(position=(2.0, 0.0, 0.5))])
        _food(sim, [(0.0, 0.0)])
        _place(sim, 2.0, 0.0)
        sims.append(_food_readings(sim)[0])
    assert sims == [0.0, 0.0]


# --- the eating rules --------------------------------------------------------------------------------------------

def _pioneer_sim(**food):
    g = pioneer_genotype(np.random.default_rng(5), sources=FORAGING)
    return Simulation([g], _cfg(**food), spawns=[Spawn(position=(0.0, 0.0, 0.0))])


def _nodes(sim, geoms):
    part_of = {gid: p for p, gid in enumerate(sim.robots[0].geoms)}
    return sorted(sim.phenotypes[0].parts[part_of[g]].node for g in geoms)


def test_the_pioneers_root_is_its_chassis():
    sim = _pioneer_sim(eat_from="root")
    root = sim.phenotypes[0].parts[0]
    assert _nodes(sim, sim._eat_geoms[0]) == [CHASSIS]
    assert root.node == CHASSIS and root.parent is None and root.shape == Shape.BOX
    assert sim.robots[0].bodies[0] == sim.robots[0].root_body  # the body with the free joint
    assert np.allclose(sorted(root.dims), sorted(sim.phenotypes[0].parts[0].dims))


def test_the_root_of_a_holistic_body_is_part_zero_of_its_root_node():
    for seed in range(6):
        g = random_genotype(np.random.default_rng(seed))
        sim = Simulation([g], _cfg(eat_from="root"), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
        assert sim._eat_geoms[0] == [sim.robots[0].geoms[0]]
        assert sim.phenotypes[0].parts[0].node == g.root and sim.phenotypes[0].parts[0].parent is None


def test_sensor_eating_on_the_pioneer_is_the_chassis_and_the_drive_wheels():
    assert _nodes(_pioneer_sim(eat_from="sensor"), _pioneer_sim(eat_from="sensor")._eat_geoms[0]) == [CHASSIS, LEFT_DRIVE, RIGHT_DRIVE]
    assert _nodes(_pioneer_sim(), _pioneer_sim()._eat_geoms[0]) == [CHASSIS, LEFT_DRIVE, RIGHT_DRIVE, CASTER, CASTER]


def test_a_body_with_no_food_sensor_eats_nothing_under_sensor():
    sim = Simulation([_body(False, 0)], _cfg(eat_from="sensor"), spawns=[Spawn(position=(0.0, 0.0, 0.5))])
    _food(sim, [(0.0, 0.0)])
    sim._eat()
    assert sim._eat_geoms[0] == [] and sim.food_eaten[0] == 0


@pytest.mark.parametrize("rule,eats", [("any", True), ("root", False), ("sensor", False)])
def test_an_item_under_a_caster_is_eaten_only_under_any(rule, eats):
    sim = _pioneer_sim(eat_from=rule)
    caster = [g for g, p in zip(sim.robots[0].geoms, sim.phenotypes[0].parts) if p.node == CASTER][0]
    c = sim.data.geom_xpos[caster][:2]
    others = [sim.data.geom_xpos[g][:2] for g, p in zip(sim.robots[0].geoms, sim.phenotypes[0].parts) if p.node != CASTER]
    u = (c - sim.data.geom_xpos[sim.robots[0].geoms[0]][:2]) / np.linalg.norm(c - sim.data.geom_xpos[sim.robots[0].geoms[0]][:2])
    item = c + 0.3 * u  # just beyond the caster, away from the chassis
    assert np.linalg.norm(item - c) < sim.config.food.eat_radius
    assert min(np.linalg.norm(o - item) for o in others) > sim.config.food.eat_radius  # the caster alone reaches it
    _food(sim, [item])
    sim._eat()
    assert sim.food_eaten[0] == (1 if eats else 0)


def test_surface_eating_reaches_from_the_surface_and_not_from_the_air():
    long = Segment(Shape.BOX, (5.0, 0.2, 0.2))
    g = Genotype(nodes=[Node(long)], root=0, global_brain=Brain(), name="rod")
    for rule, z, item, eats in (("centre", 0.1, (1.1, 0.0), False), ("surface", 0.1, (1.1, 0.0), True),
                                ("centre", 1.5, (0.0, 0.0), True), ("surface", 1.5, (0.0, 0.0), False)):
        sim = Simulation([g], _cfg(eat_rule=rule), spawns=[Spawn(position=(0.0, 0.0, z))])
        adr = sim.robots[0].root_qpos_adr
        sim.data.qpos[adr + 2] = z
        mujoco.mj_forward(sim.model, sim.data)
        half = sim.model.geom_size[sim.robots[0].geoms[0]][0]
        assert half > 1.1 and 1.1 > sim.config.food.eat_radius  # the item at x = 1.1 is under the rod, far from its centre
        _food(sim, [item])
        sim._eat()
        assert sim.food_eaten[0] == (1 if eats else 0), (rule, z)


@pytest.mark.parametrize("shape,dims", [(Shape.SPHERE, (1.0,)), (Shape.CYLINDER, (1.0, 0.4)), (Shape.BOX, (1.0, 2.0, 0.5))])
def test_surface_distance_matches_a_brute_force_surface_sample(shape, dims):
    g = Genotype(nodes=[Node(Segment(shape, dims))], root=0, global_brain=Brain(), name="one")
    sim = Simulation([g], _cfg(eat_rule="surface"), spawns=[Spawn(position=(0.2, -0.1, 0.4), yaw=0.7)])
    adr = sim.robots[0].root_qpos_adr
    sim.data.qpos[adr + 3:adr + 7] = np.array([0.9, 0.2, -0.3, 0.25]) / np.linalg.norm([0.9, 0.2, -0.3, 0.25])
    mujoco.mj_forward(sim.model, sim.data)
    gid = sim.robots[0].geoms[0]
    pts = np.random.default_rng(0).uniform(-1.5, 1.5, (40, 2))
    got = sim._surface_distance([gid], pts)
    loc = (np.c_[pts, np.zeros(len(pts))] - sim.data.geom_xpos[gid]) @ sim.data.geom_xmat[gid].reshape(3, 3)
    size = sim.model.geom_size[gid]
    rng = np.random.default_rng(1)
    for i, q in enumerate(loc):
        # the nearest point of the solid: clamp (box), project (sphere), clamp radially and axially (cylinder)
        if shape == Shape.BOX:
            near = np.clip(q, -size, size)
        elif shape == Shape.SPHERE:
            n = np.linalg.norm(q)
            near = q if n <= size[0] else q * size[0] / n
        else:
            r = np.linalg.norm(q[:2])
            xy = q[:2] if r <= size[0] else q[:2] * size[0] / r
            near = np.r_[xy, np.clip(q[2], -size[1], size[1])]
        assert got[i] == pytest.approx(np.linalg.norm(q - near), abs=1e-9)
        # and no random point of the solid is nearer
        u = rng.uniform(-1, 1, (4000, 3)) * (size if shape == Shape.BOX else np.r_[size[0], size[0], size[1] if shape == Shape.CYLINDER else size[0]])
        if shape == Shape.SPHERE:
            u = u[np.linalg.norm(u, axis=1) <= size[0]]
        elif shape == Shape.CYLINDER:
            u = u[np.linalg.norm(u[:, :2], axis=1) <= size[0]]
        assert np.linalg.norm(u - q, axis=1).min() >= got[i] - 1e-9


def test_clearance_from_geoms_keeps_every_new_item_off_every_geom():
    sim = _pioneer_sim(clear_from="geoms", items=40)
    pts = sim._clearance_points()
    assert len(pts) == len(sim.robots[0].geoms)
    sim.set_food_seed(3)
    d = np.linalg.norm(sim.food_pos[:, None, :] - pts[None, :, :], axis=2)
    assert d.min() >= sim.config.food.clearance
    root = _pioneer_sim(items=40)
    assert len(root._clearance_points()) == 1


# --- the gate adversary's code findings (coordinator ruling on #418) ----------------------------------------------

def _motionless_rod(length):
    """runs/RBT-125/adversary/probe_static_reach.py's rod: a 0.3 m cube with one box arm on a hinge, effector bias 0
    and no sensor, so it cannot move: every item it eats is static reach."""
    from rabbitstew.genotype import Effector
    arm = Segment(Shape.BOX, ((length / 0.3) ** 1.5, 1.0, 1.0), Brain(units=[Effector(dof=0, bias=0.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[])), [conn]), Node(arm)], name="rod")


def _static_food(rule, clear, seeds=range(2131, 2141)):
    import json as _json
    import os as _os
    from rabbitstew.simulation import spawn_layout
    here = _os.path.dirname(_os.path.abspath(__file__))
    base = SimConfig.from_dict(_json.load(open(_os.path.join(here, "..", "runs", "RBT-125", "gate", "worlds", "U-G0", "config.json")))["sim"])
    base = replace(base, world=replace(base.world, terrain="flat"))
    cfg = replace(base, food=replace(base.food, eat_rule=rule, clear_from=clear))
    n = 0.0
    for seed in seeds:
        sim = Simulation([_motionless_rod(6.46)], cfg, spawns=spawn_layout(1, cfg, seed))
        sim.set_food_seed(seed)
        sim.run()
        n += sim.food_eaten[0]
    return n


def test_surface_clearance_closes_the_static_reach_leak():
    """C1: under eat_rule = surface, clear_from = geoms measures from every geom's surface, so a motionless 6.46 m rod
    eats nothing; with the clearance from the root (the leak) the same rod eats (the test can fail)."""
    assert _static_food("surface", "root") > 0
    assert _static_food("surface", "geoms") == 0


def test_surface_clearance_keeps_every_new_item_off_every_surface():
    g = _motionless_rod(6.46)
    sim = Simulation([g], _cfg(eat_rule="surface", clear_from="geoms", items=40), spawns=[Spawn(position=(0.0, 0.0, 0.3))])
    sim.set_food_seed(5)
    d = sim._surface_distance(list(sim.robots[0].geoms), sim.food_pos)
    assert d.min() >= sim.config.food.clearance


BASE_ARGS = ["evolve", "--food-items", "12", "--out", "/nonexistent"]
MOTOR = ["--motor-budget", "1.77"]
PACK = ["--smell-contrast", "2.5", "--smell-tau", "1", "--eat-from", "root"]


@pytest.mark.parametrize("extra", [[], MOTOR, PACK, MOTOR + PACK], ids=["off/off", "budget on", "pack on", "both on"])
def test_both_config_strips_together(extra):
    """C2 (runs/RBT-125/adversary/probe_strips.py): RBT-120's motor-budget strip and RBT-125's perception strip write
    exactly the key families that are on, on both to_dicts, and both round-trip."""
    e = evolve_config(build_parser().parse_args(BASE_ARGS + extra))
    for d in (e.to_dict()["sim"], e.sim.to_dict()):
        d = json.loads(json.dumps(d))
        assert ("motor_budget" in d["world"]) == (MOTOR[0] in extra)
        assert bool(set(PERCEPTION_DEFAULTS) & set(d["food"])) == (PACK[0] in extra)
        rt = SimConfig.from_dict(d)
        assert rt.world.motor_budget == e.sim.world.motor_budget and rt.food == e.sim.food
    rt = EvolutionConfig.from_dict(json.loads(json.dumps(e.to_dict())))
    assert rt.sim.food == e.sim.food and rt.sim.world.motor_budget == e.sim.world.motor_budget


def test_a_run_with_the_channel_on_states_its_tau():
    """G5: smell_tau is written whenever smell_contrast > 0, even at its default; the off case writes nothing."""
    on = evolve_config(build_parser().parse_args(BASE_ARGS + ["--smell-contrast", "2.5"]))
    for d in (on.to_dict()["sim"]["food"], on.sim.to_dict()["food"]):
        assert d["smell_tau"] == 2.0 and d["smell_contrast"] == 2.5
    off = evolve_config(build_parser().parse_args(BASE_ARGS + ["--smell-tau", "2"]))
    assert "smell_tau" not in off.to_dict()["sim"]["food"]
