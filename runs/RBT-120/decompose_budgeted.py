"""RBT-120: RBT-113's decompose.py, UNCHANGED, run on the B seed directories under the budget.

    decompose_budgeted.py [--workers W] runs/RBT-120/B<k>/<seed> [...]  > decompose.txt

decompose.py builds each seed directory's scoring config with `world.evolution_config`, importing `world` from its own
directory.  Here RBT-120's world.py (RBT-113's command line plus `--motor-budget 1.77`) is imported first under that
name, so decompose.py re-scores founders and final/ populations under the budget, the physics they evolved in.  A
guard refuses a seed directory whose config.json does not carry the registered budget.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "RBT-113"))
sys.path.insert(0, HERE)
import world  # noqa: E402  RBT-120's (first on the path)
import decompose  # noqa: E402  RBT-113's, unchanged

assert decompose.world is world and world.MOTOR_BUDGET == 1.77, "decompose.py must score under RBT-120's world"


def main(argv):
    for d in (x for x in argv if not x.startswith("-") and not x.isdigit()):
        got = json.load(open(os.path.join(d, "U", "config.json")))["sim"]["world"].get("motor_budget")
        if got != world.MOTOR_BUDGET:
            raise SystemExit(f"{d}: config motor_budget {got}, registered {world.MOTOR_BUDGET}")
    return decompose.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
