"""RBT-120: run an RBT-121 per-line lever probe, UNCHANGED, on budgeted B seed directories (RUNNER.md §6 step 7).

    levers_budgeted.py PROBE.py [probe args] runs/RBT-120/B<k>/<seed> [...]  > levers_<probe>_B.txt

The RBT-121 probes (physics/probe_static.py, adversary/phys_ghost.py, adversary/phys_passive.py) build each seed
directory's config with `world.evolution_config`, importing `world` from runs/RBT-113.  Here RBT-120's world.py (the
same command line plus --motor-budget 1.77) is imported first under that name, and the probe is executed in this
process's __main__ (so its worker functions pickle), so the probe measures the bodies under the physics they evolved
in.  On the O directories the probes run directly, unbudgeted.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402,F401  RBT-120's, cached under the name the probes import

assert world.MOTOR_BUDGET == 1.77

if __name__ == "__main__":
    probe = os.path.abspath(sys.argv[1])
    sys.argv = [probe] + sys.argv[2:]
    g = sys.modules["__main__"].__dict__
    g["__file__"] = probe
    exec(compile(open(probe).read(), probe, "exec"), g)
    assert sys.modules["world"] is world, "the probe must measure under RBT-120's world"
