"""``sensor_influence`` answers connectivity; ``signed_influence`` answers gain (RBT-63).

``sensor_influence`` sums *absolute* weights and clips each link at 3.0, so it
can see neither the sign structure of a circuit nor a shortfall in its
magnitude.  Both limits have produced wrong published conclusions, so both are
pinned here against the two cases that caused them: a Braitenberg compass
against its common-mode twin, and a circuit that is wired but 32x too weak.
"""

import numpy as np

from rabbitstew.analysis import sensor_influence, signed_influence
from rabbitstew.fixed import drive_effector_units, pioneer_genotype, steering_throttle
from rabbitstew.synthesis import synthesize

N1, N2 = 3, 5  #: the food sensors on the left and right drive wheels


def _nosed_pioneer(motif: str, w: float = 1.0):
    """A nosed Pioneer carrying only a four-link nose-to-wheel motif.

    ``compass`` is the antisymmetric motif (one nose the same sign into both
    Effectors, the other the opposite), which on this body's antiparallel drive
    axes steers on ``n1 - n2``.  ``pirouette`` is the same four links all
    positive: the common mode, which spins on ``n1 + n2``.  They are negations
    of each other in half the links and nothing else.
    """
    ph = synthesize(pioneer_genotype(np.random.default_rng(0), sources=("contact", "food")))
    (e1,), (e2,) = drive_effector_units(ph)
    sign = -1.0 if motif == "compass" else 1.0
    ph.links = [(N1, e1, w), (N1, e2, w), (N2, e1, sign * w), (N2, e2, sign * w)]
    return ph, e1, e2


def _gains(ph) -> dict:
    return {(r["sensor"], r["effector"]): r["gain"] for r in signed_influence(ph)}


def test_sensor_influence_cannot_tell_a_compass_from_a_pirouette():
    """The two circuits differ by 2.4 items of yield and score identically here."""
    scores = []
    for motif in ("compass", "pirouette"):
        ph, _, _ = _nosed_pioneer(motif)
        inf = {r["unit"]: r["influence"] for r in sensor_influence(ph)}
        scores.append((inf[N1], inf[N2]))
    assert scores[0] == scores[1] == (2.0, 2.0)  # identical, and the two noses indistinguishable


def test_signed_influence_separates_them_on_the_steering_axis():
    compass, e1, e2 = _nosed_pioneer("compass")
    pirouette, _, _ = _nosed_pioneer("pirouette")
    cg, pg = _gains(compass), _gains(pirouette)
    # Steering is the effector sum on this body, so read each nose through it.
    c1 = steering_throttle(cg[(N1, e1)], cg[(N1, e2)])
    c2 = steering_throttle(cg[(N2, e1)], cg[(N2, e2)])
    assert c1 == (1.0, 0.0) and c2 == (-1.0, 0.0)  # opposed: steers on n1 - n2, a compass
    p1 = steering_throttle(pg[(N1, e1)], pg[(N1, e2)])
    p2 = steering_throttle(pg[(N2, e1)], pg[(N2, e2)])
    assert p1 == p2 == (1.0, 0.0)  # aligned: spins on n1 + n2, the common mode
    # Neither circuit drives at all: all four links land on the steering axis.
    assert all(t == 0.0 for _, t in (c1, c2, p1, p2))


def test_sensor_influence_saturates_where_signed_influence_tracks_the_gain():
    """A circuit 32x too weak is the finding of RBT-62; clipping at 3.0 per link hides it."""
    weak, e1, _ = _nosed_pioneer("compass", w=1.0)
    strong, _, _ = _nosed_pioneer("compass", w=32.0)
    unsigned = [{r["unit"]: r["influence"] for r in sensor_influence(ph)}[N1] for ph in (weak, strong)]
    assert unsigned == [2.0, 6.0]  # 32x the weight reads as 3x, and stops there whatever comes next
    assert _gains(weak)[(N1, e1)] == 1.0 and _gains(strong)[(N1, e1)] == 32.0


def test_signed_influence_omits_zero_gain_pairs_and_survives_cancellation():
    ph, e1, e2 = _nosed_pioneer("compass")
    chassis_nose = 1
    assert not [r for r in signed_influence(ph) if r["sensor"] == chassis_nose]  # unwired: no rows
    ph.links = [(N1, e1, 1.0), (N1, e1, -1.0)]  # two paths that cancel exactly
    assert _gains(ph) == {}
    assert {r["unit"]: r["influence"] for r in sensor_influence(ph)}[N1] == 2.0  # still connected


def test_signed_influence_reaches_through_hidden_neurons():
    """The Pioneer's real sensor-to-effector paths are two links long, so depth matters."""
    ph = synthesize(pioneer_genotype(np.random.default_rng(0)))
    rows = signed_influence(ph)
    assert rows and all(r["gain"] != 0.0 for r in rows)
    assert {r["sensor"] for r in rows} == {i for i, u in enumerate(ph.units) if u.unit.kind == "sensor"}
    assert len({r["effector"] for r in rows}) == 2
    assert signed_influence(ph, depth=1) == []  # no sensor links straight to an effector
