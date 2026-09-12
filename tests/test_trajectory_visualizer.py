import json

import numpy as np

from rabbitstew import quat
from rabbitstew.fixed import drive_straight_genotype
from rabbitstew.genotype import Shape
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation
from rabbitstew.trajectory import EATEN, FoodEvent, Trajectory, UnitSpec
from rabbitstew.visualizer import cylinder_end_position, food_payload, food_totals, orientation_axes, to_html, write_html
from rabbitstew.world import Spawn


def test_trajectory_roundtrip(tmp_path):
    t = Trajectory(dt=0.02, units=[UnitSpec(Shape.BOX, (0.1, 0.2, 0.3)), UnitSpec(Shape.SPHERE, (0.05,)), UnitSpec(Shape.CYLINDER, (0.04, 0.2))], robots=[2, 1])
    rng = np.random.default_rng(0)
    for _ in range(5):
        fr = rng.normal(size=(3, 7))
        fr[:, 3:] /= np.linalg.norm(fr[:, 3:], axis=1, keepdims=True)
        t.frames.append(fr)
    path = tmp_path / "t.traj"
    t.write(path)
    t2 = Trajectory.read(path)
    assert t2.dt == t.dt and t2.robots == [2, 1]
    assert [u.shape for u in t2.units] == [Shape.BOX, Shape.SPHERE, Shape.CYLINDER]
    assert np.allclose(t2.as_array(), t.as_array(), atol=1e-6)
    assert t2.robot_of_unit(2) == 1
    assert t2.duration == 0.02 * 4


def test_header_matches_paper_layout(tmp_path):
    t = Trajectory(dt=0.1, units=[UnitSpec(Shape.SPHERE, (0.5,))], robots=[1], frames=[np.array([[0, 0, 0.5, 1, 0, 0, 0]], float)])
    path = tmp_path / "t.traj"
    t.write(path)
    lines = path.read_text().splitlines()
    assert lines[0] == "rabbitstew-trajectory 1"
    assert lines[4] == "1 0.5"  # shape code then dimensions
    assert lines[5] == "frames"
    assert len(lines[6].split()) == 7  # position + quaternion per unit


def test_orientation_axes_follow_mujoco():
    g = drive_straight_genotype(0.6)
    sim = Simulation([g], SimConfig(), spawns=[Spawn((0, 0, 0), 0.7)])
    sim.start_recording(every=1)
    sim.run(0.5)
    frame = sim.trajectory.frames[-1]
    for k, gid in enumerate(sim.robots[0].geoms):
        axis, up = orientation_axes(frame[k, 3:])
        R = sim.data.geom_xmat[gid].reshape(3, 3)
        assert np.allclose(axis, R[:, 0], atol=1e-6)
        assert np.allclose(up, R[:, 1], atol=1e-6)


def test_cylinder_end_position():
    q = quat.from_axis_angle((0, 1, 0), np.pi / 2)  # local Z -> world X
    end = cylinder_end_position((1.0, 0.0, 0.0), q, 2.0)
    assert np.allclose(end, (0.0, 0.0, 0.0), atol=1e-12)


def test_html_export(tmp_path):
    g = drive_straight_genotype(0.6)
    sim = Simulation([g, g], SimConfig())
    sim.start_recording()
    sim.run(0.3)
    html = to_html(sim.trajectory, title="Test replay")
    assert "<title>Test replay</title>" in html
    assert '"units":[' in html and '"frames":[' in html
    out = tmp_path / "r.html"
    write_html(sim.trajectory, out)
    assert out.stat().st_size > 1000


def test_food_roundtrip_keeps_items_events_and_the_eaten_marker(tmp_path):
    t = Trajectory(
        dt=0.05,
        units=[UnitSpec(Shape.SPHERE, (0.1,))],
        robots=[1],
        frames=[np.array([[0, 0, 0.1, 1, 0, 0, 0]], float), np.array([[0.2, 0, 0.1, 1, 0, 0, 0]], float)],
        food=[np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[EATEN, EATEN], [3.0, 4.0]])],
        food_radius=0.35,
        food_events=[FoodEvent(1, 0, 1.0, 2.0)],
    )
    path = tmp_path / "f.traj"
    t.write(path)
    assert path.read_text().splitlines()[0] == "rabbitstew-trajectory 2"  # food asks for the newer layout
    back = Trajectory.read(path)
    assert back.n_food == 2 and back.food_radius == 0.35
    assert np.allclose(back.as_array(), t.as_array(), atol=1e-6)
    assert np.allclose(back.food[0], t.food[0], atol=1e-6)
    assert np.isnan(back.food[1][0]).all() and np.allclose(back.food[1][1], (3.0, 4.0))
    assert [(e.frame, e.robot, e.x, e.y) for e in back.food_events] == [(1, 0, 1.0, 2.0)]


def test_a_bout_without_food_still_writes_version_one(tmp_path):
    t = Trajectory(dt=0.1, units=[UnitSpec(Shape.SPHERE, (0.5,))], robots=[1], frames=[np.array([[0, 0, 0.5, 1, 0, 0, 0]], float)])
    path = tmp_path / "t.traj"
    t.write(path)
    assert path.read_text().splitlines()[0] == "rabbitstew-trajectory 1"
    assert not t.has_food and Trajectory.read(path).n_food == 0


def test_recording_a_foraging_bout_carries_the_food():
    g = drive_straight_genotype(0.6)
    cfg = SimConfig(duration=2.0, score="food", food=FoodConfig(items=6, radius=1.0, eat_radius=0.5))
    sim = Simulation([g, g], cfg)
    sim.set_food_seed(3)
    sim.start_recording()
    sim.run(2.0)
    traj = sim.trajectory
    assert traj.food_radius == 0.5
    assert len(traj.food) == traj.n_frames and traj.n_food == 6
    assert len(traj.food_events) == int(sim.food_eaten.sum()) > 0
    for e in traj.food_events:
        assert 0 <= e.frame < traj.n_frames  # every event lands in a frame the replay can show
        assert e.robot in (0, 1)
    # the item is gone from the spot by the frame the event is shown in: it regrew elsewhere
    e = traj.food_events[0]
    assert not np.isclose(traj.food[e.frame], (e.x, e.y)).all(axis=1).any()


def test_a_depleting_arena_marks_eaten_items_as_gone():
    g = drive_straight_genotype(0.6)
    cfg = SimConfig(duration=2.0, score="food", food=FoodConfig(items=6, radius=1.0, eat_radius=0.5, regrow=False))
    sim = Simulation([g, g], cfg)
    sim.set_food_seed(3)
    sim.start_recording()
    sim.run(2.0)
    traj = sim.trajectory
    eaten = int(sim.food_eaten.sum())
    assert eaten > 0
    assert np.isnan(traj.food[-1]).any(axis=1).sum() == eaten  # one NaN row per item taken out of the arena
    payload = food_payload(traj)
    assert payload["frames"][-1].count(None) == 2 * eaten  # NaN travels to the page as null, not as invalid JSON
    assert json.loads(json.dumps(payload)) == payload
    assert food_totals(traj) == [int(n) for n in sim.food_eaten]


def test_food_payload_is_absent_for_a_bout_without_food():
    g = drive_straight_genotype(0.6)
    sim = Simulation([g], SimConfig(duration=0.5))
    sim.start_recording()
    sim.run(0.5)
    assert food_payload(sim.trajectory) is None
    assert '"food":null' in to_html(sim.trajectory)
