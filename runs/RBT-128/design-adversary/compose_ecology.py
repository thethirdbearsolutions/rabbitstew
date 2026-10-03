"""RBT-128 design adversary: does --fair compose with RBT-125/126/130's ecology flags in a real config.json?

    python runs/RBT-128/design-adversary/compose_ecology.py > runs/RBT-128/design-adversary/compose_ecology.txt

The PR tests composition on `evolve`'s config and on `ecology`'s parsed args only.  Here two tiny ecology runs (1
season) with every strip set: A = `--fair`, B = the six preset flags given explicitly + `--unfair-i-know`.  Their
config.json files must differ in the fairness key alone, and every strip's value must be written.
"""
import json
import math
import os
import tempfile
import contextlib
import io

from rabbitstew.cli import main

STRIPS = ["--seasons", "1", "--capacity", "4", "--group-size", "2", "--duration", "0.2", "--brain-model", "foraging", "--challenge", "foraging",
          "--food-items", "4", "--smell-contrast", "2.5", "--smell-tau", "2", "--eat-from", "root", "--eat-rule", "surface", "--clear-from", "geoms",
          "--terrain", "random", "--obstacle-radius", "2.0", "--breed-rule", "leakx:0.3", "--breed-stream", "1", "--sweep-log",
          "--work-cost", "0.03", "--effector-bias-sigma", "0"]
EXPLICIT = ["--mass-budget", "15.34", "--motor-budget", "1.77", "--ball-cone", repr(math.pi / 2), "--hinge-range", repr(math.pi / 2),
            "--settle-until-rest", "0.01", "--settle-max", "10"]


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        out.update(flat(v, f"{p}{k}.") if isinstance(v, dict) else {f"{p}{k}": v})
    return out


def main_():
    t = tempfile.mkdtemp()
    a, b = os.path.join(t, "a"), os.path.join(t, "b")
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        main(["ecology", "--fair"] + STRIPS + ["--out", a])
        main(["ecology", "--unfair-i-know"] + STRIPS + EXPLICIT + ["--out", b])
    A, B = (flat(json.load(open(os.path.join(x, "config.json")))) for x in (a, b))
    diff = sorted(k for k in set(A) | set(B) if A.get(k) != B.get(k))
    print(f"keys that differ between --fair and explicit+bypass: {diff}")
    for k in sorted(A):
        if any(s in k for s in ("smell", "eat_", "clear_from", "random_radius", "breed", "sweep_log", "work_cost", "effector_bias", "motor_budget",
                                "mass_budget", "ball_cone", "hinge_range", "settle", "fairness")):
            print(f"  {k} = {A[k]!r}")


if __name__ == "__main__":
    main_()
