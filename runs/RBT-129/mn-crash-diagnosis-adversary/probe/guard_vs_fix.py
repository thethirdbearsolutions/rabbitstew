import sys, numpy as np, mujoco
assert mujoco.__version__ == "3.14.0"
D, k = sys.argv[1], int(sys.argv[2])
m = mujoco.MjModel.from_binary_path(D + "/model.mjb"); d = mujoco.MjData(m)
mujoco.mj_setState(m, d, np.load(f"{D}/state_{k}.npy"), mujoco.mjtState.mjSTATE_INTEGRATION)
mujoco.mj_step(m, d)
for i in range(d.ncon):
    c = d.contact[i]
    if {int(c.geom1), int(c.geom2)} == {30, 32}:
        print("pair", int(c.geom1), int(c.geom2), "dist %.6f" % c.dist, "pos", np.round(c.pos, 5).tolist(), "n", np.round(c.frame[:3], 4).tolist())
st = np.empty(mujoco.mj_stateSize(m, mujoco.mjtState.mjSTATE_INTEGRATION)); mujoco.mj_getState(m, d, st, mujoco.mjtState.mjSTATE_INTEGRATION)
np.save(sys.argv[3], st); print("ncon", d.ncon)
