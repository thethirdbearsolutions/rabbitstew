"""The trajectory-preserving null for foraging yield (RBT-39)."""

import numpy as np

from rabbitstew.fixed import drive_straight_genotype
from rabbitstew.forage_null import (body_line_rate, draw_layout, gait_null, in_disc_path, replay,
                                    replay_many, swept_width, world_layouts, world_spot_fn)
from rabbitstew.simulation import FoodConfig, SimConfig, Simulation
from rabbitstew.world import Spawn


def _recorded_bout(regrow=True, items=14, radius=2.5, eat=0.5, duration=6.0, seed=3):
    cfg = SimConfig(duration=duration, score="food",
                    food=FoodConfig(items=items, radius=radius, eat_radius=eat, regrow=regrow, clearance=0.0))
    sim = Simulation([drive_straight_genotype(0.6)], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.set_food_seed(seed)
    sim.start_recording(every=1)
    sim.run()
    return sim, cfg


def test_replay_reproduces_the_simulators_own_eating():
    """The null is only worth anything if its eat rule is the simulator's. Replaying the recorded
    per-frame food positions must recover the recorded events exactly, frame for frame."""
    for regrow in (True, False):
        sim, cfg = _recorded_bout(regrow=regrow)
        traj = sim.trajectory
        geoms = traj.as_array()[:, :, :2]
        found = []
        for f in range(1, len(geoms)):
            live = np.asarray(traj.food[f - 1], dtype=float)
            ok = np.isfinite(live).all(axis=1)
            if not ok.any():
                continue
            d = np.linalg.norm(geoms[f][:, None, :] - live[ok][None, :, :], axis=2).min(axis=0)
            found.extend([f] * int((d < cfg.food.eat_radius).sum()))
        assert len(found) == int(sim.food_eaten[0]) > 0
        assert found == sorted(e.frame for e in traj.food_events)


def test_replay_eats_on_any_geom_not_only_the_centre():
    """The defect this null exists to remove: eating is min-over-geoms, so a body clears ground its
    centre never crosses."""
    eat = 0.3
    geoms = np.array([[[0.0, 0.0], [0.0, 1.0]]])          # two geoms, one metre apart
    on_far_geom = np.array([[0.0, 1.0]])
    eaten, _ = replay(geoms, on_far_geom, eat)
    assert eaten == 1                                      # taken by the far geom
    centre_only = np.linalg.norm(geoms.mean(axis=1)[0] - on_far_geom[0])
    assert centre_only > eat                               # the centre is nowhere near it


def test_swept_width_exceeds_the_point_robot_corridor():
    sim, cfg = _recorded_bout()
    geoms = sim.trajectory.as_array()[:, :, :2]
    assert swept_width(geoms, cfg.food.eat_radius) > 2 * cfg.food.eat_radius


def test_a_still_body_meets_almost_nothing_and_a_moving_one_meets_more():
    """The null tracks the gait: covering ground raises what you meet by accident, which is exactly
    the confound the old floor could not see."""
    eat, radius, n = 0.35, 3.0, 24
    still = np.zeros((300, 1, 2))
    moving = np.stack([np.array([[x, 0.0]]) for x in np.linspace(-2.5, 2.5, 300)])
    a = gait_null(still, observed=0, n_items=n, eat_radius=eat, radius=radius, draws=40, seed=1)
    b = gait_null(moving, observed=0, n_items=n, eat_radius=eat, radius=radius, draws=40, seed=1)
    assert b.null_mean > a.null_mean


def test_a_planted_layout_beats_the_gaits_own_expectation():
    """A robot whose items sit on its path should read above its null; the same path against random
    layouts should not."""
    eat, radius, n = 0.35, 3.0, 24
    path = np.stack([np.array([[x, 0.0]]) for x in np.linspace(-2.5, 2.5, 300)])
    planted = np.stack([np.linspace(-2.4, 2.4, n), np.zeros(n)], axis=1)
    observed, _ = replay(path, planted, eat, regrow=False)
    res = gait_null(path, observed=observed, n_items=n, eat_radius=eat, radius=radius, draws=60, regrow=False, seed=2)
    assert res.observed == n                               # every planted item is on the line
    assert res.ratio > 1.5 and res.z > 2
    assert res.verdict() == "above its own gait's expectation"


def test_a_random_layout_reads_as_its_own_gait():
    """The null's own draws must not read as a compass against it: an unplanted layout sits inside
    the spread, whichever way the gait wanders."""
    eat, radius, n = 0.35, 3.0, 24
    rng = np.random.default_rng(5)
    path = np.stack([np.array([[x, 0.3 * np.sin(3 * x)]]) for x in np.linspace(-2.5, 2.5, 300)])
    observed, _ = replay(path, draw_layout(n, rng, radius), eat, regrow=False)
    res = gait_null(path, observed=observed, n_items=n, eat_radius=eat, radius=radius, draws=80, regrow=False, seed=3)
    assert abs(res.z) < 3
    assert res.verdict(margin=3.0) == "indistinguishable from its own gait"


def test_in_disc_path_ignores_ground_covered_outside_the_disc():
    out_and_back = np.stack([np.array([[x, 0.0]]) for x in np.linspace(0.0, 6.0, 61)])
    assert in_disc_path(out_and_back, radius=3.0) < 3.2    # only the part inside counts


def test_replay_many_agrees_with_replay_draw_for_draw():
    """The stacked replay is only an optimisation, so it must give the one-at-a-time answer."""
    eat, radius, n = 0.35, 3.0, 20
    rng = np.random.default_rng(11)
    path = np.stack([np.array([[x, 0.4 * np.sin(2 * x)], [x, 0.4 * np.sin(2 * x) + 0.3]])
                     for x in np.linspace(-2.8, 2.8, 240)])
    layouts = np.array([draw_layout(n, rng, radius) for _ in range(6)])
    one = [replay(path, lay, eat, regrow=False)[0] for lay in layouts]
    many = replay_many(path, layouts, eat, regrow=False)
    assert list(many) == one
    assert any(v > 0 for v in one)


def test_the_null_draws_food_the_way_the_world_does_and_puts_the_bout_back():
    """The null has to describe *this* world, so its layouts come from the world's own generator --
    and drawing them must leave the real bout's layout untouched.  The clearance rule is applied
    against wherever the robots stand, so the draws belong at the spawn, before any stepping; do it
    afterwards and the restore is no longer exact, which is why the harness draws first."""
    cfg = SimConfig(duration=6.0, score="food",
                    food=FoodConfig(items=14, radius=2.5, eat_radius=0.5, regrow=True, clearance=0.8))
    sim = Simulation([drive_straight_genotype(0.6)], cfg, spawns=[Spawn((0.0, 0.0, 0.0), 0.0)])
    sim.set_food_seed(3)
    before = sim.food_pos.copy()
    draws = world_layouts(sim, [500000, 500001, 500002, 500003])
    sim.set_food_seed(3)
    assert np.array_equal(sim.food_pos, before)              # the bout is back, bit for bit
    assert draws.shape == (4, cfg.food.items, 2)
    assert not np.array_equal(draws[0], before)
    assert (np.linalg.norm(draws, axis=2) <= cfg.food.radius + 1e-9).all()


def test_a_regrown_spot_comes_from_the_world_not_a_uniform_guess():
    """``world_spot_fn`` routes regrowth through the simulator, so a patchy world regrows in
    patches and the clearance rule is the world's own."""
    sim, cfg = _recorded_bout()
    fn = world_spot_fn(sim)
    frame = sim.trajectory.as_array()[0, :, :2]
    spots = np.array([fn(frame) for _ in range(200)])
    assert (np.linalg.norm(spots, axis=1) <= cfg.food.radius + 1e-9).all()
    assert (np.linalg.norm(spots - frame[0], axis=1) >= cfg.food.clearance - 1e-9).all()


def test_replaying_the_starting_layout_reproduces_a_depleting_bout_exactly():
    """End to end, with no recorded food positions to lean on: the initial layout replayed past the
    recorded path must give the simulator's own total.  It pins the frame offset -- frame 0 is the
    spawn, recorded before any step and never tested for eating, so the replay starts at frame 1.
    Include it and a wide body can take an item the simulator never offered it.
    """
    sim, cfg = _recorded_bout(regrow=False, seed=7)
    traj = sim.trajectory
    geoms = traj.as_array()[:, :, :2]
    start = np.asarray(traj.food[0], dtype=float)
    eaten, events = replay(geoms[1:], start, cfg.food.eat_radius, regrow=False)
    assert eaten == int(sim.food_eaten[0]) > 0
    assert [f + 1 for f, _, _ in events] == sorted(e.frame for e in traj.food_events)


def test_a_wider_body_sweeping_a_straight_line_beats_the_point_robot_floor():
    """The one direction the ticket's asymmetry argument gets right: hold the path straight and
    fresh, and widening the body can only raise what it meets.  A point reproduces the textbook
    floor; a two-geom body a metre across clears it."""
    eat, radius, n = 0.35, 3.0, 24
    rng = np.random.default_rng(19)
    layouts = np.array([draw_layout(n, rng, radius) for _ in range(120)])
    floor = 2 * eat * n / (np.pi * radius ** 2)
    point = body_line_rate(np.zeros((1, 2)), layouts, eat, radius, regrow=False)
    wide = body_line_rate(np.array([[0.0, -0.5], [0.0, 0.5]]), layouts, eat, radius, regrow=False)
    assert abs(point - floor) < 0.25 * floor          # the formula is the point-robot rate
    assert wide > point * 1.5                         # and a real body is not a point
