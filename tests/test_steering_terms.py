"""``steering_terms`` reports the depth-1 compass term, a balance ratio and a sign (RBT-81).

Two defects were found in the same instrument on one night.  The depth-4 signed
path sum that ``runs/RBT-45/motif.py`` and ``runs/compass-gain/steering_gain.py``
reported as the "realised" steering coefficient is a truncation of a series that
diverges on every committed Pioneer best (spectral radius 1.57-4.92; RBT-67's
adversary), so its value is set by where the counting stopped.  And the
``|a| > |c|`` "gradient-dominant" filter is algebraically ``s_L * s_R < 0``: a sign
test with no magnitude in it (RBT-78's adversary).  These pin the replacement:
the depth-1 term is exact whatever ``depth`` is asked for, the balance ratio
carries the magnitude the sign test dropped, and the sign is reported as a sign.
"""

import numpy as np

from rabbitstew.analysis import steering_terms
from rabbitstew.fixed import drive_effector_units, pioneer_genotype
from rabbitstew.synthesis import synthesize


def _nosed_pioneer():
    """A nosed Pioneer with every link removed, plus the unit indices a motif needs."""
    ph = synthesize(pioneer_genotype(np.random.default_rng(0), sources=("contact", "food")))
    ph.links = []
    (e1,), (e2,) = drive_effector_units(ph)
    n_left, n_right = steering_terms(ph)["noses"]
    return ph, n_left, n_right, e1, e2


def _motif(n_left, n_right, e1, e2, w, sign=-1.0):
    """Four links: one nose the same sign into both Effectors, the other ``sign`` times that."""
    return [(n_left, e1, w), (n_left, e2, w), (n_right, e1, sign * w), (n_right, e2, sign * w)]


def test_antisymmetric_motif_round_trips_at_depth_one():
    ph, nl, nr, e1, e2 = _nosed_pioneer()
    for w in (1.0, 8.0, 32.0):
        ph.links = _motif(nl, nr, e1, e2, w)
        t = steering_terms(ph)
        assert t["a"] == 2 * w and t["c"] == 0.0  # a = 2w: the calibration every installed motif is quoted in
        assert t["balance"] == 1.0 and t["opposed"] == -1
        assert t["rho"] == 0.0  # no recurrence: the path sum is exact here too
        assert t["path"] == {"a": 2 * w, "c": 0.0}


def test_common_mode_has_the_same_balance_and_the_opposite_sign():
    """The balance ratio alone cannot tell a compass from a pirouette; the sign is what separates them."""
    ph, nl, nr, e1, e2 = _nosed_pioneer()
    ph.links = _motif(nl, nr, e1, e2, 8.0, sign=+1.0)
    t = steering_terms(ph)
    assert t["a"] == 0.0 and t["c"] == 16.0
    assert t["balance"] == 1.0 and t["opposed"] == +1


def test_single_wired_nose_is_half_compass_half_pirouette_and_balance_zero():
    ph, nl, nr, e1, e2 = _nosed_pioneer()
    ph.links = [(nl, e1, 10.0)]
    t = steering_terms(ph)
    assert abs(t["a"]) == abs(t["c"]) == 5.0
    assert t["balance"] == 0.0 and t["opposed"] == 0


def test_the_retired_dominance_test_was_a_sign_test():
    """``|a| > |c|`` iff ``s_L * s_R < 0``: +100 against -0.001 passes it.  The balance says 1e-5."""
    ph, nl, nr, e1, e2 = _nosed_pioneer()
    ph.links = [(nl, e1, 100.0), (nr, e1, -0.001)]
    t = steering_terms(ph)
    assert abs(t["a"]) > abs(t["c"])  # the old filter admits it
    assert t["opposed"] == -1
    assert abs(t["balance"] - 1e-5) < 1e-15  # and this is what it is worth as a pair
    rng = np.random.default_rng(0)
    s1, s2 = rng.normal(size=10000) * 10 ** rng.uniform(-3, 3, 10000), rng.normal(size=10000) * 10 ** rng.uniform(-3, 3, 10000)
    a, c = (s1 - s2) / 2, (s1 + s2) / 2
    assert np.array_equal(np.abs(a) > np.abs(c), s1 * s2 < 0)


def test_depth_argument_never_moves_the_reported_term_on_a_divergent_brain():
    """A self-loop of -1.83 on a drive Effector -- W4b-801 g490's -- puts the radius above 1."""
    ph, nl, nr, e1, e2 = _nosed_pioneer()
    q = -1.83
    ph.links = _motif(nl, nr, e1, e2, 8.0) + [(e1, e1, q)]
    reported, path = [], {}
    for depth in (1, 4, 8, 12):
        t = steering_terms(ph, depth=depth)
        reported.append((t["a"], t["c"], t["balance"], t["opposed"]))
        path[depth] = t["path"]["a"]
        assert t["rho"] > 1.0
    assert len(set(reported)) == 1 and reported[0] == (16.0, 0.0, 1.0, -1)
    # the truncated path sum is the geometric series through the loop: w (2 + q + q^2 + q^3) at depth 4
    assert abs(path[4] - 8.0 * (2 + q + q ** 2 + q ** 3)) < 1e-9
    assert path[1] == 16.0 and abs(path[4]) != 16.0
    assert abs(path[12]) > abs(path[8]) > abs(path[4])  # and it keeps growing: not a bound on anything


def test_returns_none_without_a_nose_on_both_wheels():
    assert steering_terms(synthesize(pioneer_genotype(np.random.default_rng(0)))) is None  # no food noses at all
    ph, nl, nr, e1, e2 = _nosed_pioneer()
    assert steering_terms(ph, source="agent") is None  # this body has no agent noses
    assert steering_terms(ph)["a"] == 0.0  # noses present, nothing wired: a quantity, not an absence
