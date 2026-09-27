"""RBT-112: the command line of the arm HZ (PREREGISTRATION.md §3): RBT-106's HU command, built by RBT-106's
own `command.py` (imported, so the two share it by construction), plus exactly one flag:

  arm  founders                                extra flags                 role
  HZ   w = 32, runs/RBT-106/founders-w32-SEED  --global-bias-sigma 0       the arm; its paired control is RBT-106's HU-SEED

WORKERS (default 2) and SEASONS (default 600) as RBT-106's.  Printed NUL-separated for run_arm.sh.

Usage: command.py HZ SEED OUT
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt106_command", os.path.join(_ROOT, "runs", "RBT-106", "command.py"))
c106 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c106)

ARMS = {"HZ": ("HU", ["--global-bias-sigma", "0"])}


def command(arm, seed, out, workers="2", seasons="600"):
    twin, extra = ARMS[arm]
    return c106.command(twin, seed, out, workers, seasons) + extra


if __name__ == "__main__":
    arm, seed, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    if arm not in ARMS:
        sys.exit(f"unknown arm {arm}; one of {sorted(ARMS)}")
    sys.stdout.write("\0".join(command(arm, seed, out, os.environ.get("WORKERS", "2"), os.environ.get("SEASONS", "600"))))
