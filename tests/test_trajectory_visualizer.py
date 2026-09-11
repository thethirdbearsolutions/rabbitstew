import numpy as np

from rabbitstew import quat
from rabbitstew.fixed import drive_straight_genotype
from rabbitstew.genotype import Shape
from rabbitstew.simulation import SimConfig, Simulation
from rabbitstew.trajectory import Trajectory, UnitSpec
from rabbitstew.visualizer import cylinder_end_position, orientation_axes, to_html, write_html
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
