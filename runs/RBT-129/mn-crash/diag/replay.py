"""Replay one saved physics state (trace.py dump) in isolation.

    python replay.py DUMP K step              # set state_K, mj_step once (SIGSEGV here = reproduced)
    python replay.py DUMP K only G1 G2        # contacts disabled for every geom but G1, G2; then mj_step
    python replay.py DUMP K pairs             # print the broadphase candidate geom pairs of state_K (no narrowphase)
    python replay.py DUMP K info G1 G2        # geom types, sizes, world poses, margins of G1 and G2 at state_K
    python replay.py DUMP K finite            # are qpos/qvel/xpos/xmat finite at state_K (after mj_kinematics)?
    python replay.py DUMP K stepopt KEY=VAL.. # mj_step with model options changed (ccd_iterations=, ccd_tolerance=,
                                              # nativeccd=0, margin=)
Asserts MuJoCo 3.14.0 unless ALLOW_MJ is set.  Prints physics only (no ecology output exists here).
"""
import os
import sys

import numpy as np
import mujoco

if not os.environ.get("ALLOW_MJ"):
    assert mujoco.__version__ == "3.14.0", mujoco.__version__

dump, k, cmd, rest = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4:]
m = mujoco.MjModel.from_binary_path(os.path.join(dump, "model.mjb"))
d = mujoco.MjData(m)
SPEC = mujoco.mjtState.mjSTATE_INTEGRATION
mujoco.mj_setState(m, d, np.load(os.path.join(dump, f"state_{k}.npy")), SPEC)
TYPES = {int(v): k[7:].lower() for k, v in mujoco.mjtGeom.__members__.items()}


def geom_info(g):
    return {"id": g, "type": TYPES[int(m.geom_type[g])], "size": m.geom_size[g].round(6).tolist(),
            "body_is_world": bool(m.geom_bodyid[g] == 0), "margin": float(m.geom_margin[g]),
            "pos": d.geom_xpos[g].round(6).tolist(), "mat": d.geom_xmat[g].round(6).tolist()}


if cmd == "step":
    mujoco.mj_step(m, d)
    print("stepped without fault; ncon", d.ncon)
elif cmd == "only":
    keep = {int(x) for x in rest}
    for g in range(m.ngeom):
        if g not in keep:
            m.geom_contype[g] = 0
            m.geom_conaffinity[g] = 0
    mujoco.mj_step(m, d)
    print("stepped without fault; ncon", d.ncon)
elif cmd == "stepopt":
    for kv in rest:
        key, val = kv.split("=")
        if key == "nativeccd" and val == "0":
            m.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_NATIVECCD)
        elif key == "margin":
            m.geom_margin[:] = float(val)
        else:
            setattr(m.opt, key, type(getattr(m.opt, key))(val))
    mujoco.mj_step(m, d)
    print("stepped without fault; ncon", d.ncon)
elif cmd in ("pairs", "info", "finite"):
    mujoco.mj_kinematics(m, d)
    mujoco.mj_comPos(m, d)
    if cmd == "finite":
        for n in ("qpos", "qvel", "xpos", "xmat", "geom_xpos", "geom_xmat"):
            print(n, bool(np.all(np.isfinite(getattr(d, n)))), float(np.nanmax(np.abs(getattr(d, n)))))
    elif cmd == "info":
        for g in map(int, rest):
            print(geom_info(g))
    else:  # candidate pairs by bounding sphere + margin (the broadphase's superset), contype/affinity filtered
        r = m.geom_rbound
        for a in range(m.ngeom):
            for b in range(a + 1, m.ngeom):
                if m.geom_bodyid[a] == m.geom_bodyid[b]:
                    continue
                if not ((m.geom_contype[a] & m.geom_conaffinity[b]) or (m.geom_contype[b] & m.geom_conaffinity[a])):
                    continue
                if r[a] == 0 or r[b] == 0:  # plane: let the caller test it via `only`
                    print(a, b, TYPES[int(m.geom_type[a])], TYPES[int(m.geom_type[b])], "plane")
                    continue
                dist = np.linalg.norm(d.geom_xpos[a] - d.geom_xpos[b])
                if dist <= r[a] + r[b] + m.geom_margin[a] + m.geom_margin[b]:
                    print(a, b, TYPES[int(m.geom_type[a])], TYPES[int(m.geom_type[b])], round(float(dist), 6))
