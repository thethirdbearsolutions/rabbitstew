"""RBT-132: RBT-116 at W1 is byte-identical after the per-point change.

    python runs/RBT-116/rbt132_w1_identity.py BASE_SHA > runs/RBT-116/rbt132_w1_identity.txt

Loads ``runs/RBT-116/steer.py`` as committed at BASE_SHA (the integration commit RBT-132 branches from) and as it is
now, and runs both on the same W1-shaped fixture (G 2.5, τ 1 s, root + surface eating) and draws: every condition's
season for a planted two-nose steerer and a smell-blind mover, and the full call of each on a small battery.  Every
recorded field must be equal, array for array.  Fixture only: no W1 pool draw, no RBT-116 host.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    base = sys.argv[1]
    src = subprocess.run(["git", "show", f"{base}:runs/RBT-116/steer.py"], capture_output=True, text=True, cwd=ROOT, check=True).stdout
    tmp = os.path.join(tempfile.mkdtemp(), "steer_base.py")
    open(tmp, "w").write(src)
    old = load("steer_base", tmp)
    new = load("steer_now", os.path.join(HERE, "steer.py"))
    T = load("t116", os.path.join(ROOT, "tests", "test_rbt116_steer.py"))
    w1 = replace(T.FIXTURE, food=replace(T.FIXTURE.food, eat_from="root", eat_rule="surface"))
    bodies = {"two-nose steerer": T.two_nose_steerer(), "smell-blind mover": T.sensorless_mover()}
    fields = ("food", "work", "net", "exploded", "cells", "traj", "speed", "proj", "grad", "pen", "disp", "theta", "redraws", "food_abs_max")
    n_eq = 0
    print(f"# rbt132_w1_identity.py: steer.py at {base} against the working tree, on a W1-shaped fixture (tau {w1.food.smell_tau} s)")
    for label, g in bodies.items():
        for d in T.DRAWS[:6]:
            for c in new.CONDITIONS:
                a, b = old.run_season(g, w1, old.Draw(d.terrain_seed, d.start_seed), c), new.run_season(g, w1, d, c)
                for f in fields:
                    x, y = getattr(a, f), getattr(b, f)
                    same = np.array_equal(x, y) if isinstance(x, np.ndarray) else x == y
                    if not same:
                        print(f"DIFFERS: {label} draw {d} {c} field {f}")
                        return 1
                    n_eq += 1
        bat_old = old.Battery([old.Draw(x.terrain_seed, x.start_seed) for x in T.DRAWS[4:8]],
                              [old.Draw(x.terrain_seed, x.start_seed) for x in T.DRAWS[8:12]],
                              [old.Draw(x.terrain_seed, x.start_seed) for x in T.DRAWS[12:16]])
        bat_new = new.Battery(T.DRAWS[4:8], T.DRAWS[8:12], T.DRAWS[12:16])
        ra, rb = old.call_genome(g, w1, bat_old), new.call_genome(g, w1, bat_new)
        if ra != rb:
            print(f"DIFFERS: {label} call record")
            return 1
        print(f"{label}: 6 draws x {len(new.CONDITIONS)} conditions x {len(fields)} fields equal; call record equal ({rb['call']}, stage {rb['stage']})")
    print(f"# IDENTICAL: {n_eq} season fields and 2 call records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
