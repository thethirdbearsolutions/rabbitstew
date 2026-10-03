"""Compare builds at the overflow event (adversary MAJOR 4).

    python compare_fix.py step DUMP K G1 G2 OUT.npy    # (run under each build's venv) one mj_step from state_K; print the
                                                       # G1-G2 contacts; save the post-step state to OUT.npy
    python compare_fix.py delta DUMP A.npy B.npy [N]   # compare two post-step states; then step both N more times
                                                       # (under the current build) and report the divergence

Prints physics only.  Asserts MuJoCo 3.14.0 unless ALLOW_MJ is set.
"""
import os
import sys

import numpy as np
import mujoco

if not os.environ.get("ALLOW_MJ"):
    assert mujoco.__version__ == "3.14.0", mujoco.__version__
SPEC = mujoco.mjtState.mjSTATE_INTEGRATION
cmd, dump = sys.argv[1], sys.argv[2]
m = mujoco.MjModel.from_binary_path(os.path.join(dump, "model.mjb"))


def state(d):
    st = np.empty(mujoco.mj_stateSize(m, SPEC))
    mujoco.mj_getState(m, d, st, SPEC)
    return st


def load(path):
    d = mujoco.MjData(m)
    mujoco.mj_setState(m, d, np.load(path), SPEC)
    return d


if cmd == "step":
    k, g1, g2, out = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    d = load(os.path.join(dump, f"state_{k}.npy"))
    mujoco.mj_step(m, d)
    for i in range(d.ncon):
        c = d.contact[i]
        if {int(c.geom1), int(c.geom2)} == {g1, g2}:
            print(f"contact {int(c.geom1)}-{int(c.geom2)} dist {c.dist:.6f} pos {np.round(c.pos, 5).tolist()} "
                  f"normal {np.round(c.frame[:3], 5).tolist()}")
    print("ncon", d.ncon, "max|qvel|", round(float(np.abs(d.qvel).max()), 4))
    np.save(out, state(d))
else:
    a, b = load(sys.argv[3]), load(sys.argv[4])
    n = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    for t in range(n + 1):
        if t:
            mujoco.mj_step(m, a)
            mujoco.mj_step(m, b)
        if t in (0, 1, 10, 50, n):
            dq = np.abs(a.qpos - b.qpos).max()
            dv = np.abs(a.qvel - b.qvel).max()
            print(f"after +{t} steps: max|dqpos| {dq:.5f}  max|dqvel| {dv:.4f}  identical {bool(dq == 0 and dv == 0)}")
