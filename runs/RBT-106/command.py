"""RBT-106: the command line of one arm (PREREGISTRATION.md §7), built from RBT-104's copy of RBT-90
part 2's command (`seed_founders.PART2`, imported), so that the arms share it by construction:

  arm  founders (founders.py)        extra flags                        role
  P1   w = 1,  runs/RBT-106/founders-w1-SEED    --food-patches 3                  PRIMARY: S1-patchy (uniform twin: RBT-104's S1)
  P8   w = 1,  the same files                   --link-scale 8 --food-patches 3   factorial option: S8-patchy (uniform twin: RBT-104's S8)
  S1   w = 1,  the same files                   (none)                            RBT-104's S1, run here only under §7.3's contingency
  S8   w = 1,  the same files                   --link-scale 8                    RBT-104's S8, run here only under §7.3's contingency
  HU   w = 32, runs/RBT-106/founders-w32-SEED   (none)                            option H, uniform world
  HP   w = 32, the same files                   --food-patches 3                  option H, patchy world

PART2 is part 2's command with --seasons 600 and --workers 1; the arm's --workers is WORKERS (default
2, the house packing) and --seasons is SEASONS (default 600).  Workers do not change a run (RBT-90
ruling).  Printed NUL-separated for run_arm.sh.

Usage: command.py ARM SEED OUT
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_seed_founders", os.path.join(_ROOT, "runs", "RBT-104", "seed_founders.py"))

ARMS = {"P1": (1, ["--food-patches", "3"]), "P8": (1, ["--link-scale", "8", "--food-patches", "3"]),
        "S1": (1, []), "S8": (1, ["--link-scale", "8"]),
        "HU": (32, []), "HP": (32, ["--food-patches", "3"])}
UNIFORM_TWIN = {"P1": "S1", "P8": "S8", "HP": "HU"}


def part2():
    """seed_founders.PART2 without importing the simulator (it is a module constant; read by exec of
    the module would pull MuJoCo into the launcher, so the literal is parsed from the source)."""
    import ast
    src = open(_spec.origin).read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "PART2":
            call = node.value  # "...".split()
            return ast.literal_eval(call.func.value).split()
    raise RuntimeError("PART2 not found in RBT-104's seed_founders.py")


def command(arm, seed, out, workers="2", seasons="600"):
    w, extra = ARMS[arm]
    base = part2()
    base[base.index("--workers") + 1] = str(workers)
    base[base.index("--seasons") + 1] = str(seasons)
    founders = os.path.join("runs", "RBT-106", f"founders-w{w}-{seed}")
    return ["python", "-m", "rabbitstew.cli"] + base + ["--seed", str(seed), "--out", out,
                                                        "--from-conventional", founders] + extra


if __name__ == "__main__":
    arm, seed, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    if arm not in ARMS:
        sys.exit(f"unknown arm {arm}; one of {sorted(ARMS)}")
    sys.stdout.write("\0".join(command(arm, seed, out, os.environ.get("WORKERS", "2"), os.environ.get("SEASONS", "600"))))
