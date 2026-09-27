"""RBT-112 (adversary F12, ruling 03:32): the frozen-bias FAULT, tested at birth.

The fault the flag can actually commit is a global bias that changes after birth.  So, over every designed-body
genome the arm saved at birth: the child's global-unit biases (a multiset) must come from its parents' global biases,
plus at most one new value, a unit the operator added at that birth (born with its own drawn bias, which it then
keeps).  A birth with more than one new value is a FAULT.  This is byte_identity.py check 4's test (imported), run on
the arm's own genomes.  resting.py's per-champion b stays as information only: a paying unit added under S = 0
legitimately carries its birth bias.

Usage: freeze.py RUN_DIR   > RUN_DIR/freeze.txt      (exit 1 on any fault)
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt112_byte_identity", os.path.join(_HERE, "byte_identity.py"))
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)


def main():
    run = sys.argv[1].rstrip("/")
    births, bad = bi.novel_biases(run)
    print(f"# RBT-112 birth-level freeze test on {run}: designed-body births whose global biases are not their parents' "
          f"plus at most one added unit's")
    print(f"FREEZE {os.path.basename(run)}: births {births}, faults {bad} -> {'PASS' if bad == 0 and births > 0 else 'FAULT'}")
    sys.exit(0 if bad == 0 and births > 0 else 1)


if __name__ == "__main__":
    main()
