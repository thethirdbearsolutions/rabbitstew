"""RBT-129 crash diagnosis: resume an ecology run in-process with every mj_step counted (and, in dump mode, the
physics state before each of the last steps of one simulation saved), so the faulting step can be found after a
native SIGSEGV.

    python trace.py count RUN_DIR COUNTER              # mmap counter: [sim id, mj_step within sim, total steps]
    python trace.py dump  RUN_DIR COUNTER SIM STEP OUT # also save OUT/model.mjb and OUT/state_<k>.npy for steps
                                                       # STEP-8 .. STEP of simulation SIM (k = step within the sim)

RUN_DIR must be a scratch copy (it is resumed in place).  Nothing here prints any ecology output: stdout and stderr of
the run go to RUN_DIR/trace.log, which is deleted unread by the caller.  Asserts MuJoCo 3.14.0 unless ALLOW_MJ is set.
"""
import os
import sys

import numpy as np
import mujoco

if not os.environ.get("ALLOW_MJ"):
    assert mujoco.__version__ == "3.14.0", mujoco.__version__

mode, run_dir, counter = sys.argv[1], sys.argv[2], sys.argv[3]
target_sim = int(sys.argv[4]) if mode == "dump" else -1
target_step = int(sys.argv[5]) if mode == "dump" else -1
out = sys.argv[6] if mode == "dump" else None
KEEP = 8

cnt = np.memmap(counter, dtype=np.int64, mode="w+", shape=(3,))
cnt[:] = (-1, 0, 0)

import rabbitstew.simulation as simmod  # noqa: E402

_real_step = mujoco.mj_step
SPEC = mujoco.mjtState.mjSTATE_INTEGRATION


class _Shim:
    """Stands in for the ``mujoco`` module inside rabbitstew.simulation: counts mj_step, delegates the rest."""

    def __getattr__(self, name):
        return getattr(mujoco, name)

    @staticmethod
    def mj_step(m, d, *a):
        cnt[1] += 1
        cnt[2] += 1
        if cnt[0] == target_sim and target_step - KEEP <= cnt[1] <= target_step:
            if not os.path.exists(os.path.join(out, "model.mjb")):
                mujoco.mj_saveModel(m, os.path.join(out, "model.mjb"), None)
            st = np.empty(mujoco.mj_stateSize(m, SPEC))
            mujoco.mj_getState(m, d, st, SPEC)
            np.save(os.path.join(out, f"state_{int(cnt[1])}.npy"), st)
        return _real_step(m, d, *a)


simmod.mujoco = _Shim()
_init = simmod.Simulation.__init__


def _counted_init(self, *a, **k):
    cnt[0] += 1
    cnt[1] = 0
    return _init(self, *a, **k)


simmod.Simulation.__init__ = _counted_init

if out:
    os.makedirs(out, exist_ok=True)
log = os.open(os.path.join(run_dir, "trace.log"), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
os.dup2(log, 1)
os.dup2(log, 2)
import faulthandler  # noqa: E402

faulthandler.enable()
from rabbitstew import cli  # noqa: E402

sys.argv = ["rabbitstew", "ecology", "--resume", "--seasons", "300", "--workers", "1", "--out", run_dir]
cli.main(sys.argv[1:])
