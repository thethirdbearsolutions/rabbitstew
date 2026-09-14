"""The trajectory-preserving null for foraging yield (RBT-39)."""

import numpy as np

from rabbitstew.fixed import drive_straight_genotype
from rabbitstew.forage_null import draw_layout, gait_null, in_disc_path, replay, swept_width
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
