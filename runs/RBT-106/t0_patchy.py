"""RBT-106 §3.3: the seeded founders at t = 0 in the PATCHY world, for the factorial's four cells.

RBT-104's design adversary's `founders_t0.py`, imported and run unchanged, with its world constant
RUN pointed at `runs/RBT-106/world-patchy` (part 2's config with patches = 3) instead of part 2's own:
the same 30 planted founders per seed, their bare twins, K = 1 and K = 8, 16 paired seeds from 7000,
real smell and RBT-97's rotated decoy.  Its uniform-world twin is RBT-104's committed
`runs/RBT-104/founders-t0-SEED.txt` (the same script in part 2's world), so the pair of files is the
t = 0 row of the 2 x 2.

Usage: t0_patchy.py SEED [--seeds 16] [--procs 4]
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_founders_t0", os.path.join(_ROOT, "runs", "RBT-104", "adversary", "founders_t0.py"))
ft0 = importlib.util.module_from_spec(_spec)
sys.modules["rbt104_founders_t0"] = ft0
_spec.loader.exec_module(ft0)

if __name__ == "__main__":
    ft0.RUN = os.path.join(_HERE, "world-patchy")
    print(f"# RBT-106: RBT-104 adversary founders_t0.py, unchanged, in the world of {ft0.RUN}/config.json (patches 3)")
    ft0.main()
