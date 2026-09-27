"""RBT-113 pre-launch controls (PREREGISTRATION.md §6), run on the tree the arms will run.  Writes
runs/RBT-113/controls/prelaunch.txt, which run_arm.sh requires to read `PRELAUNCH: PASS` on this rabbitstew/ tree.

  1. tests/test_rbt113.py passes (default byte-identical to the pre-hook code; the three lines select as specified;
     the operator leaves the holistic side alone; the salt moves only the holistic side; resume is byte-exact).
  2. A tiny benchmark through the real pipeline (world.py's command line at population 12, 5 generations, 1 draw):
     a default arm and a Z arm at seed 1, each U, D, C; readout.py on the pair must exit 0 with every per-arm control
     PASS (the pairing, the configs, the pool membership of every parent, the manipulation check) and the
     cross-arm operator pairing intact.  This is the smoke run of the readout.
  3. The positive and null controls, by simulation through the readout's own statistics (power.py's model) at the
     planned design: P(RESPONDS) >= 0.8 at planted h2 = 0.05 for a designed-body unit (one arm), and
     P(RESPONDS) <= 0.10 at h2 = 0, both in the gaussian and the floor scenario (100 simulated benchmarks each).

Usage: prelaunch.py WORKDIR   (WORKDIR: scratch space for the tiny runs, outside the checkout)
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import power  # noqa: E402
import readout as ro  # noqa: E402
import world  # noqa: E402


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main(work):
    out = []
    ok = True
    say = out.append
    say("# RBT-113 pre-launch controls (runs/RBT-113/prelaunch.py)")
    say(f"commit {git('rev-parse', 'HEAD')}")
    say(f"rabbitstew_tree {git('rev-parse', 'HEAD:rabbitstew')}")
    import mujoco
    import platform
    say(f"platform {platform.machine()} mujoco {mujoco.__version__} numpy {np.__version__}")

    t = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_rbt113.py"], cwd=ROOT, capture_output=True, text=True)
    last = [l for l in t.stdout.splitlines() if l.strip()][-1]
    say(f"\n1. tests/test_rbt113.py: {last}")
    ok &= t.returncode == 0

    say("\n2. tiny benchmark (population 12, 5 generations, 1 draw; default and Z arms at seed 1)")
    arms = []
    for op in ("", "Z"):
        arm = os.path.join(work, f"{op}1")
        arms.append(arm)
        for L in ro.LINES:
            d = os.path.join(arm, L)
            if not os.path.exists(os.path.join(d, "history.json")):
                cmd = world.command(L, op, 1, d, workers=os.environ.get("WORKERS", "4"), population=12, generations=5, draws=1)
                cmd[0] = sys.executable
                subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "readout.py"), *arms], cwd=ROOT, capture_output=True, text=True)
    with open(os.path.join(HERE, "controls", "smoke-readout.txt"), "w") as f:
        f.write(r.stdout)
    ctl = [l for l in r.stdout.splitlines() if l.startswith("arm ") or "pairing" in l]
    for l in ctl:
        say("   " + l)
    passed = r.returncode == 0 and all("PASS" in l for l in ctl if l.startswith("arm ")) and len(ctl) == 2
    say(f"   readout exit {r.returncode}; controls {'PASS' if passed else 'FAIL'} (full output: controls/smoke-readout.txt)")
    ok &= passed

    say("\n3. positive and null controls by simulation (power.py's model, 12 units, 100 benchmarks each)")
    rng = np.random.default_rng(1130)
    for floor in (False, True):
        for h2, need in ((0.0, "<= 0.10"), (0.05, ">= 0.80")):
            vs = [power.verdict([power.sim_arm(h2, rng, floor) for _ in range(12)]) for _ in range(100)]
            pr = vs.count("R") / 100
            good = pr <= 0.10 if h2 == 0 else pr >= 0.80
            ok &= good
            say(f"   {'floor' if floor else 'gaussian':8s} h2 {h2:.2f}: P(RESPONDS) {pr:.2f} (needs {need}) {'ok' if good else 'FAIL'}")

    say(f"\nPRELAUNCH: {'PASS' if ok else 'FAIL'}")
    txt = "\n".join(out) + "\n"
    with open(os.path.join(HERE, "controls", "prelaunch.txt"), "w") as f:
        f.write(txt)
    print(txt)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
