import numpy as np
import pytest

from rabbitstew.brain import RuntimeBrain
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE, drive_straight_genotype, is_same_morphology, pioneer_genotype
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Link, Neuron, Node, Segment, Sensor, Shape, UnitRef, random_genotype
from rabbitstew.simulation import SimConfig, Simulation, default_spawns, run_bout, zero_sum_fitness
from rabbitstew.synthesis import synthesize
from rabbitstew.world import Spawn, build_model


def test_world_has_one_body_geom_joint_per_part(rng):
    g = random_genotype(rng)
    ph = synthesize(g)
    model, data, (idx,) = build_model([ph], [Spawn()])
    assert len(idx.bodies) == len(ph.parts) == len(idx.geoms)
    n_joints = sum(1 for p in ph.parts if p.parent is not None and p.joint_type != JointType.FIXED)
    assert sum(1 for j in idx.joints if j >= 0) == n_joints
    n_dofs = sum(p.joint_type.ndof for p in ph.parts if p.parent is not None)
    assert len(idx.actuators) == n_dofs == model.nu


def test_robots_start_resting_on_the_ground(rng):
    for _ in range(5):
        sim = Simulation([random_genotype(rng), pioneer_genotype(rng)], SimConfig())
        lowest = min(float(sim.data.geom_xpos[g][2] - sim.model.geom_rbound[g]) for idx in sim.robots for g in idx.geoms)
        assert lowest > 0.0
        assert lowest < 0.05


def test_pioneer_drives_towards_the_centre():
    g = drive_straight_genotype(0.6)
    sim = Simulation([g], SimConfig(), spawns=[Spawn((-2.0, 0.0, 0.0), 0.0)])
    d0 = sim.distance_from_center(0)
    sim.run(3.0)
    assert sim.distance_from_center(0) < d0 - 0.5
    assert not sim.exploded[0]


def test_pioneer_spins_with_equal_wheel_commands():
    g = drive_straight_genotype(0.6)
    g.nodes[RIGHT_DRIVE].segment.brain.links[0].weight = g.nodes[LEFT_DRIVE].segment.brain.links[0].weight
    sim = Simulation([g], SimConfig(), spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.run(3.0)
    assert sim.distance_from_center(0) < 0.3  # stayed put
    yaw = 2 * np.arctan2(sim.data.xquat[sim.robots[0].root_body][3], sim.data.xquat[sim.robots[0].root_body][0])
    assert abs(yaw) > 0.5  # but turned


def test_contact_and_direction_sensors():
    seg = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Sensor("contact")] + [Sensor("target", a) for a in range(3)] + [Sensor("opponent", a) for a in range(3)]))
    g = Genotype(nodes=[Node(seg)])
    sim = Simulation([g, g], SimConfig(start_distance=2.0))
    sim.run(0.5)
    touching = sim.contact_bodies()
    vals = sim.sensor_values(0, touching)
    assert vals[0] == 1.0  # resting on the floor
    # Robot 0 spawns at (-2, 0) facing +x: the centre and the opponent are straight ahead in its
    # frame (the centre is on the ground, so its direction dips slightly below the box's own centre).
    assert vals[1] > 0.98 and abs(vals[2]) < 0.02 and -0.2 < vals[3] < 0.0
    assert vals[4] > 0.98 and abs(vals[5]) < 0.02 and abs(vals[6]) < 0.05
    assert np.allclose(np.linalg.norm(vals[1:4]), 1.0, atol=1e-6)


def test_runtime_brain_updates_synchronously():
    seg = Segment(Shape.SPHERE, (1.0,), Brain(units=[Sensor("contact"), Neuron(0.0), Effector(0, 0.0)]))
    seg.brain.links = [Link(UnitRef(0, 0), UnitRef(0, 1), 2.0), Link(UnitRef(0, 1), UnitRef(0, 2), 2.0)]
    g = Genotype(nodes=[Node(seg, [Connection(child=0, recursive_limit=2, scale=0.5)])])
    ph = synthesize(g)
    brain = RuntimeBrain(ph)
    assert (1, 0) in brain.effectors  # the child instance's effector drives its hinge
    assert (0, 0) not in brain.effectors  # the root has no parent joint
    brain.step(np.array([1.0, 1.0]))  # sensors latch; neurons still see the zero initial state
    assert brain.effector_output(1, 0) == 0.0
    brain.step(np.array([1.0, 1.0]))  # neurons respond to the sensors; effectors still see zero
    assert brain.effector_output(1, 0) == 0.0
    brain.step(np.array([1.0, 1.0]))  # effectors respond to the neurons: one tick of delay per hop
    assert brain.effector_output(1, 0) == pytest.approx(np.tanh(2 * np.tanh(2.0)))


def test_zero_sum_fitness():
    assert zero_sum_fitness([1.0, 3.0], [False, False]) == [0.75, 0.25]
    assert zero_sum_fitness([1.0, 3.0], [True, False]) == [0.0, 1.0]
    assert zero_sum_fitness([0.0, 0.0], [False, False]) == [0.5, 0.5]


def test_run_bout_is_symmetric_under_swap(quick_sim):
    a = drive_straight_genotype(0.6)
    b = pioneer_genotype(np.random.default_rng(0))
    r1 = run_bout(a, b, quick_sim)
    r2 = run_bout(a, b, quick_sim, swap=True)
    assert r1.fitness[0] + r1.fitness[1] == pytest.approx(1.0)
    assert r1.fitness[0] > 0.5  # the driver gets closer than a random controller
    assert r2.fitness[0] > 0.5


def test_random_bouts_run_and_record(rng, quick_sim):
    for _ in range(3):
        res = run_bout(random_genotype(rng), random_genotype(rng), quick_sim, record=True)
        assert res.trajectory is not None
        assert res.trajectory.n_frames == int(round(quick_sim.duration / quick_sim.control_dt)) // quick_sim.record_every + 1
        assert all(np.isfinite(res.distances))


def test_static_robot_is_welded(rng):
    block = Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)))])
    sim = Simulation([block, drive_straight_genotype(0.8)], SimConfig(), spawns=[Spawn((0, 0, 0), 0, static=True), Spawn((-1.0, 0, 0), 0)])
    sim.run(2.0)
    assert np.allclose(sim.data.xpos[sim.robots[0].root_body][:2], (0, 0))
    assert sim.robots[0].root_qpos_adr == -1


def test_default_spawns_face_centre():
    s = default_spawns(2, 2.0)
    assert np.allclose(s[0].position[:2], (-2, 0)) and np.isclose(s[0].yaw, 0.0)
    assert np.allclose(s[1].position[:2], (2, 0), atol=1e-12) and np.isclose(abs(s[1].yaw), np.pi)
