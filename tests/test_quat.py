import numpy as np

from rabbitstew import quat


def test_rotate_matches_matrix():
    rng = np.random.default_rng(0)
    for _ in range(20):
        q = quat.normalize(rng.normal(size=4))
        v = rng.normal(size=3)
        assert np.allclose(quat.rotate(q, v), quat.to_matrix(q) @ v)
        assert np.allclose(quat.inverse_rotate(q, quat.rotate(q, v)), v)


def test_from_matrix_roundtrip():
    rng = np.random.default_rng(1)
    for _ in range(20):
        q = quat.normalize(rng.normal(size=4))
        q2 = quat.from_matrix(quat.to_matrix(q))
        assert np.allclose(q, q2) or np.allclose(q, -q2)


def test_align_x_to():
    for d in [(0, 1, 0), (0, 0, 1), (-1, 0, 0), (1, 1, 1), (0.3, -0.2, 0.9)]:
        q = quat.align_x_to(d)
        assert np.allclose(quat.rotate(q, (1, 0, 0)), np.asarray(d, float) / np.linalg.norm(d))


def test_euler_axes():
    q = quat.from_euler(0, 0, np.pi / 2)
    assert np.allclose(quat.rotate(q, (1, 0, 0)), (0, 1, 0), atol=1e-12)
