"""Quaternion helpers.

Quaternions are ``(w, x, y, z)`` arrays, the convention shared by ODE and
MuJoCo.  A quaternion ``q`` rotates a vector ``v`` as ``q * (0, v) * q'`` where
``q'`` is the conjugate.
"""

from __future__ import annotations

import numpy as np

IDENTITY = np.array([1.0, 0.0, 0.0, 0.0])


def normalize(q):
    q = np.asarray(q, dtype=float)
    n = np.linalg.norm(q)
    if n == 0.0:
        return IDENTITY.copy()
    return q / n


def multiply(a, b):
    """Hamilton product ``a * b``."""
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ]
    )


def conjugate(q):
    w, x, y, z = q
    return np.array([w, -x, -y, -z])


def rotate(q, v):
    """Rotate vector ``v`` by quaternion ``q`` (``q v q'``)."""
    v = np.asarray(v, dtype=float)
    p = np.array([0.0, v[0], v[1], v[2]])
    return multiply(multiply(q, p), conjugate(q))[1:]


def inverse_rotate(q, v):
    """Rotate ``v`` by the inverse of ``q`` (world frame -> body frame)."""
    return rotate(conjugate(q), v)


def from_axis_angle(axis, angle):
    axis = np.asarray(axis, dtype=float)
    n = np.linalg.norm(axis)
    if n == 0.0:
        return IDENTITY.copy()
    axis = axis / n
    half = 0.5 * angle
    return np.concatenate(([np.cos(half)], np.sin(half) * axis))


def from_euler(rx, ry, rz):
    """Quaternion for successive rotations about the fixed X, Y then Z axes."""
    qx = from_axis_angle((1, 0, 0), rx)
    qy = from_axis_angle((0, 1, 0), ry)
    qz = from_axis_angle((0, 0, 1), rz)
    return multiply(qz, multiply(qy, qx))


def yaw(angle):
    return from_axis_angle((0, 0, 1), angle)


def to_matrix(q):
    w, x, y, z = normalize(q)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def from_matrix(m):
    """Convert a rotation matrix to a quaternion (Shepperd's method)."""
    m = np.asarray(m, dtype=float)
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        w = 0.25 * s
        x = (m[2, 1] - m[1, 2]) / s
        y = (m[0, 2] - m[2, 0]) / s
        z = (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w = (m[2, 1] - m[1, 2]) / s
        x = 0.25 * s
        y = (m[0, 1] + m[1, 0]) / s
        z = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w = (m[0, 2] - m[2, 0]) / s
        x = (m[0, 1] + m[1, 0]) / s
        y = 0.25 * s
        z = (m[1, 2] + m[2, 1]) / s
    else:
        s = np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w = (m[1, 0] - m[0, 1]) / s
        x = (m[0, 2] + m[2, 0]) / s
        y = (m[1, 2] + m[2, 1]) / s
        z = 0.25 * s
    return normalize([w, x, y, z])


def align_x_to(direction):
    """Quaternion rotating the +X axis onto ``direction``."""
    d = np.asarray(direction, dtype=float)
    n = np.linalg.norm(d)
    if n == 0.0:
        return IDENTITY.copy()
    d = d / n
    x = np.array([1.0, 0.0, 0.0])
    c = float(np.dot(x, d))
    if c > 1.0 - 1e-9:
        return IDENTITY.copy()
    if c < -1.0 + 1e-9:
        return from_axis_angle((0, 0, 1), np.pi)
    axis = np.cross(x, d)
    return from_axis_angle(axis, np.arccos(np.clip(c, -1.0, 1.0)))
