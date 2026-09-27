"""RBT-111 design adversary, re-check of F1 and F2 on the amended design (#257 head b6012db).

    python runs/RBT-111/adversary/recheck.py SCRATCH     -> recheck.txt   (pure Python; run on #257's tree)
"""
import importlib.util
import os
import random
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..")
spec = importlib.util.spec_from_file_location("ro111", os.path.join(HERE, "..", "readout.py"))
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)
sys.path.insert(0, HERE)
import perm  # noqa: E402  (the adversary's reference implementation, unchanged)
import synthetic  # noqa: E402

rng = random.Random(262)
print("RBT-111 design adversary: re-check of F1 and F2 on #257's amended readout (recheck.py)")

print("\nF2. readout.perm_c0_p against the adversary's perm.py (and, n <= 4, the 6^n brute force)")
worst, same = 0.0, 0
for i in range(300):
    n = rng.choice((1, 2, 3, 4, 5, 8, 12, 16))
    rows = [tuple(rng.gauss(0, 0.07) + (0.25 if rng.random() < 1 / 16 else 0) - (0.05 if j == 0 else 0) for j in range(3)) for _ in range(n)]
    a, b = ro.perm_c0_p(rows), perm.perm_c0_p(rows)
    same += a[1:] == b[1:]
    worst = max(worst, abs(a[0] - b[0]))
    if n <= 4:
        assert abs(a[0] - perm._brute(rows)) < 1e-12
print(f"   300 random sets, n in 1..16: counts identical in {same}/300, max |p diff| {worst:.1e}; brute force agrees at n <= 4")
fails = 0
for i in range(30):
    rows = [tuple(rng.gauss(0.0, 0.08) - (0.04 if j == 0 else 0) for j in range(3)) for _ in range(16)]
    if ro.perm_c0_ci(rows) != perm.perm_c0_ci(rows):
        fails += 1
print(f"   perm_c0_ci equals perm.py's on 30 random 16-seed sets: {30 - fails}/30")
for n in (1, 2, 3):
    print(f"   perm_c0_ci at n = {n}: {tuple(round(v, 3) for v in ro.perm_c0_ci(rows[:n]))}")
print(f"   sign_flip_ci removed from readout.py: {not hasattr(ro, 'sign_flip_ci')}")

print("\nF1. drive.sh's per-slot call and the full readout on slot-shaped partial roots")
scratch = sys.argv[1]
for slot, present in ((2, ["s0-217", "s1-217", "s2-217", "s0-218"]), (3, ["s0-217", "s1-217", "s2-217", "s0-218", "s1-218", "s2-218"])):
    root = os.path.join(scratch, f"slot{slot}")
    synthetic.make(root, {"s0": 0, "s1": 0, "s2": 0}, 0.062, seeds=(217, 218))
    for d in os.listdir(root):
        if d not in present:
            shutil.rmtree(os.path.join(root, d))
    for flag in ("--summaries-only", "--from-summaries"):
        cmd = [sys.executable, os.path.join(ROOT, "runs", "RBT-111", "readout.py"), flag, "--seeds", "217,218", "--root", root]
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            res = f"returned {r.returncode} in {time.time() - t0:.1f} s"
            if flag == "--from-summaries":
                res += "; " + next((l.strip() for l in r.stdout.splitlines() if l.startswith("4.")), "no interval line")
        except subprocess.TimeoutExpired:
            res = "STILL RUNNING after 120 s"
        print(f"   after slot {slot} ({len(present)} arms), {flag}: {res}")
grep = open(os.path.join(ROOT, "runs", "RBT-111", "drive.sh")).read()
print(f"   drive.sh calls --summaries-only: {'readout.py --summaries-only' in grep}; still calls --write-summaries: {'--write-summaries' in grep}")

print("\nF2 end to end: the synthetic cases on the amended readout")
synthetic.main(os.path.join(scratch, "syn"))
