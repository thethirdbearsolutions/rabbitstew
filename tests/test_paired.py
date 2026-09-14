import numpy as np
import pytest

from rabbitstew.paired import ci95, difference_of_differences, paired


def test_paired_se_is_smaller_than_unpaired_when_the_modes_move_together():
    # the same seed helps or hurts both modes, which is exactly why the comparison is paired
    a = [3.0, 5.0, 9.0, 1.0, 7.0, 4.0, 8.0, 2.0]
    b = [x - 1.0 for x in a]
    r = paired(a, b)
    assert r.mean == pytest.approx(1.0)
    assert r.paired_se == pytest.approx(0.0, abs=1e-12)  # every difference identical
    assert r.unpaired_se > 1.0  # the old error term sees only the spread between seeds


def test_zero_count_veto_names_a_sparse_effect_rather_than_a_bias():
    # RBT-22's season-300 Pioneer in miniature: mostly bit-identical, one big seed
    diffs = [0, 0, 0, -1, 0, 4, 0, 0, 0, 0, 0, 0, 0, -1, 2, 0]
    r = paired([10.0 + d for d in diffs], [10.0] * len(diffs))
    assert r.zeros == 12 and r.n == 16
    assert r.zero_fraction > 0.5
    assert r.verdict(t_threshold=0.0) == "sparse, not a bias"  # passes any t and is still vetoed


def test_a_dense_consistent_effect_is_separable():
    rng = np.random.default_rng(0)
    d = rng.normal(2.0, 0.5, 64)
    r = paired(d, np.zeros(64))
    assert r.zeros == 0 and abs(r.t) > 2.5
    assert r.verdict() == "separable"
    lo, hi = ci95(r)
    assert lo > 0


def test_no_effect_is_not_separable():
    rng = np.random.default_rng(1)
    a = rng.normal(0.0, 1.0, 64)
    r = paired(a, a + rng.normal(0.0, 1.0, 64) * 0.01)
    assert r.verdict() == "not separable" or abs(r.t) < 2.5


def test_sign_test_and_permutation_agree_that_all_positive_is_unlikely():
    r = paired([1.0] * 12 + [2.0] * 4, [0.0] * 16)
    assert r.positive == 16 and r.negative == 0
    assert r.sign_p < 0.001 and r.perm_p < 0.01


def test_everything_zero_is_not_an_effect():
    r = paired([1.0] * 8, [1.0] * 8)
    assert r.zeros == 8 and r.perm_p == 1.0 and r.sign_p == 1.0
    assert r.verdict() == "not separable"


def test_difference_of_differences_separates_opposite_signs():
    rng = np.random.default_rng(2)
    up = paired(rng.normal(1.0, 0.3, 64), np.zeros(64))
    down = paired(rng.normal(-1.0, 0.3, 64), np.zeros(64))
    dod = difference_of_differences(up, down)
    assert dod.mean > 1.5 and abs(dod.t) > 2.5 and dod.perm_p < 0.01


def test_difference_of_differences_does_not_separate_two_nulls():
    rng = np.random.default_rng(3)
    a = paired(rng.normal(0.0, 1.0, 64), np.zeros(64))
    b = paired(rng.normal(0.0, 1.0, 64), np.zeros(64))
    dod = difference_of_differences(a, b)
    assert abs(dod.t) < 2.5 and dod.perm_p > 0.05


def test_mismatched_lengths_are_refused():
    with pytest.raises(ValueError):
        paired([1.0, 2.0], [1.0])
