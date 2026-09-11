import json

import numpy as np
import pytest

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, EvolutionConfig, Experiment, initial_population, reproduce, BoutRunner, evaluate
from rabbitstew.fixed import LEFT_DRIVE, drive_straight_genotype, pioneer_genotype
from rabbitstew.genetics import MutationConfig, body_signature, crossover_controller, mutate, mutate_controller
from rabbitstew.genotype import Brain, BrainVocabulary, Connection, Effector, Genotype, JointType, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef, random_genotype
from rabbitstew.simulation import SimConfig, Simulation
from rabbitstew.synthesis import synthesize
from rabbitstew.trajectory import Trajectory
from rabbitstew.world import Spawn, WorldConfig, scenery


def box_with(sensors, connections=()):
    seg = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=list(sensors)))
    return Genotype(nodes=[Node(seg, list(connections))])


def test_rich_sensor_readings():
    g = box_with([Sensor("up", a) for a in range(3)] + [Sensor("height"), Sensor("target_distance"), Sensor("oscillator", freq=0.5, phase=0.0)] + [Sensor("velocity", a) for a in range(3)])
    sim = Simulation([g], SimConfig(), spawns=[Spawn((-2.0, 0.0, 0.0), 0.0)])
    sim.run(0.5)
    v = sim.sensor_values(0, sim.contact_bodies())
    assert np.allclose(v[0:3], (0, 0, 1), atol=0.02)  # resting flat: up is local z
    assert 0 < v[3] < 0.3  # tanh of a ~0.15 m centre height
    assert v[4] == pytest.approx(2.0 / 3.0, abs=0.02)  # d/(1+d) at 2 m
    assert v[5] == pytest.approx(np.sin(2 * np.pi * 0.5 * sim.time), abs=1e-6)
    assert np.allclose(v[6:9], 0, atol=0.05)  # not moving


def test_joint_sensors_and_position_servo():
    child = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Sensor("joint_angle"), Sensor("joint_velocity"), Effector(0, 5.0)]))
    conn = Connection(child=1, position=(1, 0, 0), joint_type=JointType.HINGE, axis=(0, 0, 1), joint_limit=1.0, motor="position", scale=0.6)
    g = Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))), Node(child)], root=0)
    g.nodes[0].connections.append(conn)
    sim = Simulation([g], SimConfig())
    assert sim.model.actuator(0).name.endswith("_a1_0")
    sim.run(2.0)
    v = sim.sensor_values(0, sim.contact_bodies())
    assert v[0] > 0.7  # the servo drove the joint towards +limit (effector saturates at +1)
    assert abs(v[1]) < 0.3  # and it has settled
    assert synthesize(g).parts[1].motor == "position"


def test_velocity_servo_spins_wheel():
    g = drive_straight_genotype(0.6)
    for c in g.nodes[0].connections[:2]:
        c.motor = "velocity"
    sim = Simulation([g], SimConfig(), spawns=[Spawn((-2, 0, 0), 0)])
    d0 = sim.distance_from_center(0)
    sim.run(3.0)
    assert sim.distance_from_center(0) < d0 - 0.5


def test_ball_joint_ignores_servo_modes():
    conn = Connection(child=1, joint_type=JointType.BALL, motor="position", scale=0.6)
    g = Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [conn]), Node(Segment(Shape.SPHERE, (1.0,), Brain(units=[Effector(1)])))])
    ph = synthesize(g)
    assert ph.parts[1].motor == "torque"
    Simulation([g], SimConfig())  # builds three torque motors without error


def test_neuron_functions():
    from rabbitstew.brain import RuntimeBrain

    units = [Sensor("contact")] + [Neuron(0.0, f) for f in ("tanh", "sin", "abs", "relu", "sign", "integrate", "differentiate")]
    seg = Segment(Shape.SPHERE, (1.0,), Brain(units=units))
    seg.brain.links = [Link(UnitRef(0, 0), UnitRef(0, k), -0.5) for k in range(1, 8)]
    ph = synthesize(Genotype(nodes=[Node(seg)]))
    b = RuntimeBrain(ph)
    b.step(np.array([1.0]))  # sensors latch
    b.step(np.array([1.0]))  # neurons see x = -0.5
    a = b.activation
    assert a[1] == pytest.approx(np.tanh(-0.5)) and a[2] == pytest.approx(np.sin(-0.5)) and a[3] == pytest.approx(np.tanh(0.5))
    assert a[4] == 0.0 and a[5] == -1.0
    assert a[6] == pytest.approx(0.2 * np.tanh(-0.5))
    assert a[7] == pytest.approx(np.tanh(-0.5 - 0.0))  # input changed from 0 to -0.5
    b.step(np.array([1.0]))
    assert b.activation[7] == pytest.approx(0.0, abs=1e-12)  # input unchanged now
    assert b.activation[6] == pytest.approx(0.9 * 0.2 * np.tanh(-0.5) + 0.2 * np.tanh(-0.5))


def test_terrain_blocks_the_wheeled_body():
    for terrain in ("plateau", "rails"):
        cfg = SimConfig(world=WorldConfig(terrain=terrain))
        sim = Simulation([drive_straight_genotype(0.8)], cfg, spawns=[Spawn((-2, 0, 0), 0)])
        sim.run(6.0)
        assert sim.distance_from_center(0) > 0.9
        assert sim.center_of_mass(0)[2] < 0.28  # never got on top (that would put its centre near 0.29 m)
    flat = Simulation([drive_straight_genotype(0.8)], SimConfig(), spawns=[Spawn((-2, 0, 0), 0)])
    flat.run(6.0)
    assert flat.center_of_mass(0)[0] > 0.0  # it crossed the centre on flat ground
    assert SimConfig(world=WorldConfig(terrain="plateau")).effective_target()[2] == pytest.approx(0.15)


def test_scenery_roundtrips_through_trajectory(tmp_path):
    cfg = SimConfig(world=WorldConfig(terrain="rails"))
    sim = Simulation([drive_straight_genotype(0.5)], cfg, spawns=[Spawn((-2, 0, 0), 0)])
    sim.start_recording()
    sim.run(0.2)
    assert len(sim.trajectory.scenery) == 6 == len(scenery(cfg.world))
    path = tmp_path / "t.traj"
    sim.trajectory.write(path)
    t = Trajectory.read(path)
    assert len(t.scenery) == 6 and t.scenery[0].shape == Shape.BOX and t.scenery[0].dims == pytest.approx((0.06, 6.0, 0.1))
    from rabbitstew.visualizer import to_html

    assert '"scenery":[' in to_html(t)


def test_rich_random_genotypes_and_mutation(rng):
    vocab = BrainVocabulary.rich()
    cfg = MutationConfig(vocab=vocab, motor_rate=0.5, func_rate=0.5)
    g = random_genotype(rng, vocab=vocab)
    for _ in range(30):
        g = mutate(g, rng, cfg)
        assert g.is_valid()
    sources = {u.source for _, b in g.brains() for u in b.units if u.kind == "sensor"}
    assert sources  # something survived
    Simulation([g], SimConfig(duration=0.2)).run()


def test_controller_mutation_keeps_body(rng):
    base = pioneer_genotype(rng, rich=True)
    cfg = MutationConfig(vocab=BrainVocabulary.rich(), add_unit_rate=0.9, remove_unit_rate=0.3, add_link_rate=0.9, remove_link_rate=0.3, func_rate=0.5)
    g = base
    for _ in range(40):
        g = mutate_controller(g, rng, cfg)
        assert g.is_valid()
        assert body_signature(g) == body_signature(base)
    assert len(g.global_brain.units) != len(base.global_brain.units) or {u.func for u in g.global_brain.units} != {"tanh"}
    other = mutate_controller(base, rng, cfg)
    child = crossover_controller(g, other, rng)
    assert child.is_valid() and body_signature(child) == body_signature(base)


def test_conventional_topology_population(rng):
    cfg = EvolutionConfig(population_size=4, elites=1, sim=SimConfig(duration=0.3), brain_model="rich", conventional_topology=True)
    assert cfg.mutation.vocab.neuron_funcs == BrainVocabulary.rich().neuron_funcs
    pop = initial_population(CONVENTIONAL, cfg, rng)
    assert any(getattr(u, "source", None) == "joint_velocity" for u in pop.members[0].nodes[LEFT_DRIVE].segment.brain.units)
    evaluate(pop, BoutRunner(cfg.sim), rng, cfg)
    new = reproduce(pop, rng, cfg)
    assert all(body_signature(m) == body_signature(pop.members[0]) for m in new.members)


def test_resume_continues_identically(tmp_path):
    cfg = EvolutionConfig(population_size=3, generations=4, elites=1, champion_interval=2, champions=1, seed=9, sim=SimConfig(duration=0.3), brain_model="rich")
    full = Experiment(cfg, out_dir=str(tmp_path / "full"), log=None).run()
    cfg2 = EvolutionConfig(population_size=3, generations=2, elites=1, champion_interval=2, champions=1, seed=9, sim=SimConfig(duration=0.3), brain_model="rich")
    Experiment(cfg2, out_dir=str(tmp_path / "part"), log=None).run()
    assert (tmp_path / "part" / "state.json").exists()
    resumed = Experiment.resume(str(tmp_path / "part"), generations=4, log=None)
    assert resumed.config.brain_model == "rich"
    out = resumed.run()
    assert [e["best_fitness"] for e in out["history"]] == [e["best_fitness"] for e in full["history"]]
    assert json.load(open(tmp_path / "part" / "config.json"))["generations"] == 4
