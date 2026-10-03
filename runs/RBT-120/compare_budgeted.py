"""RBT-120 Q3 (PREREGISTRATION.md §5.3): RBT-117's compare.py, UNCHANGED, on the budgeted B seed directories.

    compare_budgeted.py runs/RBT-120/B1/1 ... runs/RBT-120/B4/12  > compare.txt

The only substitution is the seed-set check's arm map (RBT-117's O1..O4 become RBT-120's B1..B4, the same seed
blocks).  compare.py's status line reads "registered before RBT-113's readout": for this run the governing
registration is RBT-120's, printed first.  The designed body's lines are the O arms' byte for byte (budget.py K2), so
the designed side of every quantity here equals RBT-117's; only the holistic side is new.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt117_compare", os.path.join(HERE, "..", "RBT-117", "compare.py"))
cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cmp)
sys.path.insert(0, HERE)
import world  # noqa: E402

cmp.ARM_OF = dict(world.ARM_OF)

if __name__ == "__main__":
    print("# RBT-120 Q3: RBT-117's compare.py (unchanged) on the B arms, registered by runs/RBT-120/PREREGISTRATION.md §5.3 "
          f"before any B arm ran; motor budget {world.MOTOR_BUDGET}")
    sys.exit(cmp.main(sys.argv[1:]))
