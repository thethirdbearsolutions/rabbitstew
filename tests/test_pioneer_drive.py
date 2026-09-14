"""The Pioneer's drive sign convention (RBT-64).

Both drive wheels hinge about their own outward normal, so the two hinge axes
are antiparallel and the effector *sum* is the steering axis while their
*difference* is the throttle.  Four separate agents have written controllers
against the opposite assumption, so the convention is pinned here: these tests
fail if the geometry is ever changed out from under a controller or an
analysis.
"""

import math

import numpy as np
import pytest

from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE, drive_commands, drive_effector_units, drive_straight_genotype, pioneer_genotype, steering_throttle
from rabbitstew.simulation import SimConfig, Simulation
from rabbitstew.synthesis import synthesize
from rabbitstew.world import Spawn


def _drive_genotype(left: float, right: float, power: float = 0.6):
    """A Pioneer whose two drive Effectors are held at ``power`` times the given signs."""
    g = pioneer_genotype(np.random.default_rng(0), hidden=1)
    for _, brain in g.brains():
        for link in brain.links:
            link.weight = 0.0
    g.global_brain.units[0].bias = 10.0  # saturates to +1
    for wheel, sign in ((LEFT_DRIVE, left), (RIGHT_DRIVE, right)):
        brain = g.nodes[wheel].segment.brain
        brain.units[0].bias = 0.0
        brain.links[0].weight = sign * math.atanh(power)
    return g


def _bout(left: float, right: float, duration: float = 2.0):
    """``(displacement, |yaw change|)`` of the chassis over a solo bout on flat ground."""
    sim = SimConfig()
    s = Simulation([_drive_genotype(left, right)], sim, spawns=[Spawn()])
    idx = s.robots[0]

    def yaw():
        w, x, y, z = s.data.xquat[idx.root_body]
        return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

    y0 = yaw()
    p0 = s.center_of_mass(0)[:2].copy()
    s.run(duration)
    dyaw = (yaw() - y0 + math.pi) % (2 * math.pi) - math.pi
    return float(np.linalg.norm(s.center_of_mass(0)[:2] - p0)), dyaw


def test_the_two_drive_hinge_axes_are_antiparallel():
    """The geometric fact the whole convention rests on."""
    g = pioneer_genotype(np.random.default_rng(0))
    s = Simulation([g], SimConfig(), spawns=[Spawn()])
    idx = s.robots[0]
    axes = [np.array(s.data.xaxis[j]) for j in idx.joints if j >= 0]
    assert len(axes) == 4  # two drive wheels, two casters
    left, right = axes[0], axes[1]
    assert float(left @ right) == pytest.approx(-1.0, abs=1e-12)  # not merely opposed: antiparallel
    assert abs(float(left @ np.array([0.0, 1.0, 0.0]))) == pytest.approx(1.0, abs=1e-12)  # and along the body's y


def test_the_difference_throttles_and_the_sum_steers():
    """Same magnitude on both wheels, opposite conclusions, purely from the sign."""
    moved, turned = _bout(1.0, -1.0)  # difference: throttle
    assert moved > 1.0 and abs(math.degrees(turned)) < 5.0
    spun_distance, spun_yaw = _bout(1.0, 1.0)  # sum: steering
    assert spun_distance < 0.2 and abs(math.degrees(spun_yaw)) > 45.0
    assert spun_yaw < 0  # a positive sum yaws clockwise seen from above, to the robot's right


def test_steering_throttle_round_trips_and_agrees_with_the_straight_driver():
    assert steering_throttle(0.6, -0.6) == (0.0, 0.6)  # pure throttle
    assert steering_throttle(0.6, 0.6) == (0.6, 0.0)  # pure steering
    assert drive_commands(0.0, 0.6) == (0.6, -0.6)
    for left, right in ((0.3, -0.7), (-1.0, 0.25), (0.0, 0.0)):
        assert drive_commands(*steering_throttle(left, right)) == pytest.approx((left, right))
    # the sanity-check driver is pure throttle under this convention
    g = drive_straight_genotype(0.6)
    weights = [g.nodes[w].segment.brain.links[0].weight for w in (LEFT_DRIVE, RIGHT_DRIVE)]
    steering, throttle = steering_throttle(*(math.tanh(w) for w in weights))
    assert abs(steering) < 1e-12 and throttle > 0.5


def test_drive_effector_units_finds_left_and_right():
    ph = synthesize(pioneer_genotype(np.random.default_rng(0)))
    left, right = drive_effector_units(ph)
    assert len(left) == 1 and len(right) == 1
    assert ph.parts[ph.units[left[0]].part].attach_pos[1] > 0  # +y is the robot's left
    assert ph.parts[ph.units[right[0]].part].attach_pos[1] < 0
