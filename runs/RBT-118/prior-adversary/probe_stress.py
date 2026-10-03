"""RBT-118 prior ADVERSARY probe: claim 3. Which base history each stress arm forks from, each fauna's fewest alive after
the onset, and whether the pre-onset seasons equal RBT-90's (so RBT-99 and RBT-100 share their base histories).

    python runs/RBT-118/prior-adversary/probe_stress.py > runs/RBT-118/prior-adversary/probe_stress.txt
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SEEDS = (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)


def rows(p):
    return [l.split("\t") for l in open(os.path.join(ROOT, p)).read().splitlines()[1:]]


print("# RBT-118 prior ADVERSARY, probe_stress.py: EXPLORATORY, descriptive")
print(f"{'arm':22s} {'onset':>5s} {'pre-onset == RBT-90':>19s} {'D min after':>11s} {'D extinct':>9s} {'H min after':>11s}")
hist = {}
for arm in ("RBT-99", "RBT-100"):
    for s in SEEDS:
        d = f"runs/{arm}/shift-{s}"
        T = json.load(open(os.path.join(ROOT, d, "config.json")))["ecology"]["shift_at"]
        R = rows(f"{d}/seasons.txt")
        B = rows(f"runs/RBT-90/forage-{s}/seasons.txt")
        pre = [r[:7] for r in R if int(r[0]) < T] == [r[:7] for r in B if int(r[0]) < T]
        dmin = min(int(r[2]) for r in R if r[1] == "conventional" and int(r[0]) >= T)
        hmin = min(int(r[2]) for r in R if r[1] == "holistic" and int(r[0]) >= T)
        dext = next((int(r[0]) for r in R if r[1] == "conventional" and int(r[2]) == 0), None)
        if dext is not None:
            hist.setdefault(s, []).append(arm)
        print(f"{d:22s} {T:5d} {str(pre):>19s} {dmin:11d} {str(dext or ''):>9s} {hmin:11d}")
print(f"\ndesigned extinctions: {sum(len(v) for v in hist.values())} arms on {len(hist)} distinct base histories of 10: {hist}")
