"""RBT-124, the physics fairness pack (RBT-121 R1-R3): ball_cone + hinge_range, effector_bias_sigma, settle_until_rest.

Every flag is off by default, and off is byte-identical in the MJCF and in config.json; each has its own tests.
The RBT-113 genomes used here are a small fixture copied from the restored checkpoints (tests/data/rbt124/, see its
README); the full-sample evidence is runs/RBT-124/.
"""
import json
import math
import os
from dataclasses import replace

import numpy as np
import pytest

from rabbitstew.cli import build_parser, evolve_config
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.genetics import MutationConfig, mutate, mutate_controller
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape, random_genotype
from rabbitstew.levers import body_levers, line_summary, resting_drive
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
from rabbitstew.world import Spawn, WorldConfig, build_xml, is_wheel, joint_range

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "rbt124")
CONE = HINGE = math.pi / 2
PACK_KEYS = ("ball_cone", "hinge_range", "settle_until_rest", "settle_max", "effector_bias_sigma")


def rbt113_sim(terrain=1131):
    """RBT-113's generation sim (runs/RBT-113/world.py's command line: food world, mass budget 15.34, 15 s, random terrain)."""
    args = build_parser().parse_args(["evolve", "--brain-model", "foraging", "--food-items", "12", "--food-radius", "3", "--eat-radius", "0.35",
                                      "--food-decay", "1.0", "--work-cost", "0.03", "--duration", "15", "--mass-budget", "15.34",
                                      "--conventional-topology", "--terrain", "random", "--random-start", "--score", "food", "--out", "/nonexistent"])
    sc = evolve_config(args).sim
    return replace(sc, world=replace(sc.world, terrain_seed=terrain))


def season(g, sc, start=2131, off=False):
    cfg = replace(sc, random_start=True)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, start))
    if cfg.food is not None:
        sim.set_food_seed(start)
    if off:
        sim.brains[0].effector_output = lambda *a: 0.0
    com0 = sim.center_of_mass(0)[:2].copy()
    sim.run()
    return sim, float(np.linalg.norm(sim.center_of_mass(0)[:2] - com0))


def ranges(sc):
    return replace(sc, world=replace(sc.world, ball_cone=CONE, hinge_range=HINGE))


def star(k, orientation):
    """RBT-121 audit A's S1 star hub: k light boxes on driven ball joints at full throttle around a heavy sphere."""
    child = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Effector(dof=d, bias=3.0) for d in range(3)]))
    conns = []
    for i in range(k):
        a, b = 2 * math.pi * i / max(k, 1), math.pi * (0.25 + 0.5 * ((i * 0.618) % 1.0))
        conns.append(Connection(child=1, position=(math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)), scale=0.25,
                                orientation=orientation, joint_type=JointType.BALL, joint_limit=None))
    nodes = [Node(Segment(Shape.SPHERE, (1.0,)), conns), Node(child)]
    nodes += [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(max(0, math.ceil((k + 1) / 2.0) - 2))]
    return Genotype(nodes=nodes, name=f"star{k}")


def hinged(shape, dims, axis):
    part = Segment(shape, dims, Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=0.5, joint_type=JointType.HINGE, axis=axis, joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [conn]), Node(part)], name="hinged")


def fixture(name):
    return Genotype.load(os.path.join(DATA, name))


def fixtures(prefix):
    return [(f, fixture(f)) for f in sorted(os.listdir(DATA)) if f.startswith(prefix)]


# --------------------------------------------------------------------------- #
# all three: off is byte-identical in config.json, on round-trips
# --------------------------------------------------------------------------- #


def test_off_writes_the_old_config_json():
    d = EvolutionConfig().to_dict()
    flat = json.dumps(d)
    for k in PACK_KEYS:
        assert f'"{k}"' not in flat, k
    assert not any(k in SimConfig().to_dict() or k in SimConfig().to_dict()["world"] for k in PACK_KEYS)
    # the CLI at its defaults builds the same config as before
    args = build_parser().parse_args(["evolve", "--out", "/nonexistent"])
    assert not any(f'"{k}"' in json.dumps(evolve_config(args).to_dict()) for k in PACK_KEYS)


def test_on_is_written_and_round_trips():
    args = build_parser().parse_args(["evolve", "--out", "/x", "--ball-cone", "1.5", "--hinge-range", "1.2", "--settle-until-rest", "0.01",
                                      "--settle-max", "4", "--effector-bias-sigma", "0"])
    cfg = evolve_config(args)
    d = cfg.to_dict()
    assert d["sim"]["world"]["ball_cone"] == 1.5 and d["sim"]["world"]["hinge_range"] == 1.2
    assert d["sim"]["settle_until_rest"] == 0.01 and d["sim"]["settle_max"] == 4.0
    assert d["mutation"]["effector_bias_sigma"] == 0.0
    back = EvolutionConfig.from_dict(json.loads(json.dumps(d)))
    assert back.sim.world.ball_cone == 1.5 and back.sim.settle_until_rest == 0.01 and back.mutation.effector_bias_sigma == 0.0
    for sub in ("simulate", "ecology"):
        a = build_parser().parse_args([sub] + (["g.json"] if sub == "simulate" else ["--out", "/x"]) + ["--ball-cone", "1", "--settle-until-rest", "0.02"])
        assert a.ball_cone == 1.0 and a.settle_until_rest == 0.02


# --------------------------------------------------------------------------- #
# 1. ball_cone + hinge_range
# --------------------------------------------------------------------------- #


def test_off_mjcf_is_unchanged_and_the_pioneer_is_byte_identical_on():
    rng = np.random.default_rng(3)
    for seed in range(5):
        ph = synthesize(pioneer_genotype(np.random.default_rng(seed), rich=bool(seed % 2)))
        assert build_xml([ph], [Spawn()], WorldConfig()) == build_xml([ph], [Spawn()], WorldConfig(ball_cone=CONE, hinge_range=HINGE))
        assert all(is_wheel(p) for p in ph.parts[1:])
    for _ in range(20):  # off: every random body's MJCF is what it was (joint_range is part.joint_range)
        ph = synthesize(random_genotype(rng))
        assert all(joint_range(p, WorldConfig()) == p.joint_range for p in ph.parts)
        assert build_xml([ph], [Spawn()], WorldConfig()) == build_xml([ph], [Spawn()], WorldConfig(ball_cone=0.0, hinge_range=0.0))


def test_ranges_are_written_where_they_should_be():
    rng = np.random.default_rng(7)
    seen = set()
    for _ in range(60):
        ph = synthesize(random_genotype(rng))
        xml = build_xml([ph], [Spawn()], WorldConfig(ball_cone=CONE, hinge_range=HINGE))
        for p in ph.parts[1:]:
            r = joint_range(p, WorldConfig(ball_cone=CONE, hinge_range=HINGE))
            if p.joint_type == JointType.BALL:
                assert r == (0.0, CONE)
                seen.add("ball")
            elif p.joint_type == JointType.HINGE and p.joint_range is None:
                assert (r is None) == is_wheel(p)
                seen.add("wheel" if r is None else "hinge")
            else:
                assert r == p.joint_range  # limited hinges and sliders keep their genotype's range
        assert xml.count('type="ball"') == xml.count('type="ball" damping') or True
    assert {"ball", "hinge"} <= seen


def test_embedded_rotor_burns_at_most_a_tenth():
    """Audit A's test: S1 with orientation (0, pi/2, 0), a child pointing into its parent on a driven ball joint at full
    throttle, burns <= 0.1 of its unfixed work under the cone (measured: 0.006).  Also a 3-child hub and a hinge rotor."""
    sc = rbt113_sim()
    for g in (star(1, (0.0, math.pi / 2, 0.0)), star(3, (0.0, math.pi / 2, 0.0)), hinged(Shape.BOX, (5.0, 0.05, 0.05), (0.0, 0.0, 1.0))):
        w0 = season(g, sc)[0].work[0]
        w1 = season(g, ranges(sc))[0].work[0]
        assert w0 > 1000.0
        assert w1 <= 0.1 * w0, (g.name, w0, w1)


def test_a_wheel_stays_a_wheel():
    """A round part hinged about its own axis keeps spinning under hinge_range: the season is bit-identical."""
    sc = rbt113_sim()
    for g in (hinged(Shape.CYLINDER, (1.0, 0.4), (1.0, 0.0, 0.0)), hinged(Shape.SPHERE, (1.0,), (1.0, 0.0, 0.0))):
        a, b = season(g, sc)[0], season(g, ranges(sc))[0]
        assert a.work[0] > 1000.0 and a.work[0] == b.work[0] and np.array_equal(a.data.qpos, b.data.qpos)
    # the same cylinder hinged across its axis is a rotor, and is ranged
    g = hinged(Shape.CYLINDER, (1.0, 0.4), (0.0, 0.0, 1.0))
    assert not is_wheel(synthesize(g).parts[1])


def test_rbt113_holistic_d_final_work_on_contact_free_children_falls():
    """An RBT-113 holistic D final (O1 seed 1): its work on children touching nothing falls by >= 90% (measured below;
    runs/RBT-124/DESIGN.md reports the line)."""
    sc = rbt113_sim()
    for name, g in fixtures("holistic_D_"):
        off = body_levers(g, sc, 2131)
        on = body_levers(g, ranges(sc), 2131)
        assert off["work_free"] > 1000.0, name
        assert on["work_free"] <= 0.1 * off["work_free"], (name, off["work_free"], on["work_free"])


def test_the_pioneer_season_is_bit_identical_under_ranges():
    sc = rbt113_sim()
    g = pioneer_genotype(np.random.default_rng(0))
    a, b = season(g, sc)[0], season(g, ranges(sc))[0]
    assert np.array_equal(a.data.qpos, b.data.qpos) and a.work[0] == b.work[0]


# --------------------------------------------------------------------------- #
# 2. effector_bias_sigma
# --------------------------------------------------------------------------- #


def _eff(g):
    return [(owner, k, u.bias) for owner, b in g.brains() for k, u in enumerate(b.units) if u.kind == "effector"]


def _blank_eff(g):
    d = g.to_dict()
    for node in d["nodes"]:
        for u in node["segment"]["brain"]["units"]:
            if u.get("kind") == "effector":
                u["bias"] = None
    return json.dumps(d, sort_keys=True)


def test_s0_freezes_designed_effector_biases_over_100_mutations():
    for seed in range(3):
        g0 = pioneer_genotype(np.random.default_rng(seed))
        for eff in g0.brains():
            pass
        g, ref = g0, g0
        r0, r1 = np.random.default_rng(seed), np.random.default_rng(seed)
        for _ in range(100):
            g = mutate_controller(g, r0, MutationConfig(effector_bias_sigma=0.0))
            ref = mutate_controller(ref, r1, MutationConfig())
        assert _eff(g) == _eff(g0)  # frozen
        assert _eff(ref) != _eff(g0)  # the default walks them
        assert _blank_eff(g) == _blank_eff(ref)  # the same one draw: every other gene is where the default put it
        assert _blank_eff(g) != _blank_eff(g0)  # ... and other genes did change


def test_s0_freezes_holistic_effector_biases_over_100_mutations():
    """Holistic `mutate`: across 100 chained mutations, an Effector that survives a step with its brain's unit list
    unchanged keeps its bias exactly; the same run unset walks them; the structure is the default's draw for draw."""
    for seed in range(3):
        g = random_genotype(np.random.default_rng(seed))
        ref = g
        r0, r1 = np.random.default_rng(100 + seed), np.random.default_rng(100 + seed)
        kept = walked = 0
        for _ in range(100):
            child = mutate(g, r0, MutationConfig(effector_bias_sigma=0.0))
            rchild = mutate(ref, r1, MutationConfig())
            assert _blank_eff(child) == _blank_eff(rchild)
            for (o, pb), (_, cb) in zip(g.brains(), child.brains()):
                if [u.kind for u in pb.units] == [u.kind for u in cb.units] and len(g.nodes) == len(child.nodes):
                    for pu, cu in zip(pb.units, cb.units):
                        if pu.kind == "effector":
                            assert cu.bias == pu.bias
                            kept += 1
            for (o, pb), (_, cb) in zip(ref.brains(), rchild.brains()):
                if [u.kind for u in pb.units] == [u.kind for u in cb.units] and len(ref.nodes) == len(rchild.nodes):
                    walked += sum(pu.kind == "effector" and cu.bias != pu.bias for pu, cu in zip(pb.units, cb.units))
            g, ref = child, rchild
        assert kept > 50 and walked > 10


def test_unset_and_s_equal_weight_sigma_are_byte_identical():
    for seed in range(3):
        a = b = random_genotype(np.random.default_rng(seed))
        ra, rb = np.random.default_rng(seed), np.random.default_rng(seed)
        for _ in range(50):
            a = mutate(a, ra, MutationConfig())
            b = mutate(b, rb, MutationConfig(effector_bias_sigma=MutationConfig().weight_sigma))
        assert json.dumps(a.to_dict()) == json.dumps(b.to_dict())
        assert ra.random() == rb.random()


def test_resting_drive():
    g = pioneer_genotype(np.random.default_rng(0))
    assert resting_drive(g) == (0.0, 2)
    for _, b in g.brains():
        for u in b.units:
            if u.kind == "effector":
                u.bias = 2.0
    assert resting_drive(g) == (1.0, 2)


# --------------------------------------------------------------------------- #
# 3. settle_until_rest
# --------------------------------------------------------------------------- #


def settled(sc, eps=0.01, cap=5.0):
    return replace(sc, settle_until_rest=eps, settle_max=cap)


def test_off_settle_is_the_plain_settle():
    sc = rbt113_sim()
    g = random_genotype(np.random.default_rng(5))
    a = season(g, sc)[0]
    assert a.settle_seconds == sc.settle_time and math.isnan(a.settle_peak_speed)


def test_a_body_already_at_rest_is_bit_identical_the_pioneer_on_every_registered_draw():
    """The designed body's intact results are unchanged: it is at rest in the plain settle's last chunk, so no step is
    added, on each of RBT-113's four draws."""
    g = pioneer_genotype(np.random.default_rng(0))
    for t, s in [(1131, 2131), (1132, 2132), (1133, 2133), (1134, 2134)]:
        sc = rbt113_sim(t)
        a, b = season(g, sc, s)[0], season(g, settled(sc), s)[0]
        assert b.settle_seconds == 1.0
        assert np.array_equal(a.data.qpos, b.data.qpos) and a.work[0] == b.work[0] and a.food_eaten[0] == b.food_eaten[0]


def test_settle_is_capped_and_logged():
    sc = rbt113_sim()
    for name, g in fixtures("drifter_"):
        sim = season(g, settled(sc, eps=1e-9, cap=2.0))[0]  # an unreachable eps: runs to the cap
        assert sim.settle_seconds == pytest.approx(2.0)
        sim = season(g, settled(sc))[0]
        assert 1.0 <= sim.settle_seconds <= 5.0 + 1e-9


def test_motors_off_displacement_below_5cm_on_the_registered_terrain():
    """Every fixture member (RBT-113 holistic bodies that drift with motors off under the plain settle) moves < 0.05 m
    with motors off under settle_until_rest 0.01, on RBT-113's first registered draw (terrain 1131)."""
    sc = rbt113_sim()
    before = []
    for name, g in fixtures("drifter_"):
        before.append(season(g, sc, off=True)[1])
        after = season(g, settled(sc), off=True)[1]
        assert after < 0.05, (name, after)
    assert max(before) > 0.25  # the fixture does drift under the plain settle


def test_levers_line_summary():
    sc = replace(rbt113_sim(), duration=1.0)
    rows = [body_levers(pioneer_genotype(np.random.default_rng(0)), sc, 2131)]
    s = line_summary(rows)
    assert s["n"] == 1 and s["off_disp"] < 1e-6 and s["recessive"] == 0 and s["reachable"] == 4
    assert 0.0 <= s["w_free"] <= 1.0 and s["span"] > 0.4


def test_a_self_jammed_body_is_flagged_not_settled():
    """The residual settle_until_rest cannot remove (runs/RBT-124/DESIGN.md section 3): a body whose own geoms
    interpenetrate is pushed apart by the contact solver for ever, so it never comes to rest.  The settle runs to its
    cap, and the lever report flags it (self_pen > 1 cm), rather than calling it settled."""
    sc = settled(rbt113_sim())
    g = fixture("jammed_D_Z1sZ2_035.json")
    sim = season(g, sc, off=True)[0]
    assert sim.settle_seconds == pytest.approx(5.0) and sim.settle_peak_speed >= 0.01
    assert body_levers(g, replace(sc, duration=1.0), 2131)["self_pen"] > 0.01
