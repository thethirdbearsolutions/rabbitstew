"""RBT-97 adversary: RBT-67's committed per-seed data, re-signed per robot, re-derived independently.

Written without reading the author's script (runs/RBT-97/resign_rbt67.py).  Inputs, all committed:

  docs/artifacts/RBT-67/{w4b,p801}.json   RBT-67's ladder: per robot, per rung a, the 64 paired
                                          per-seed differences (motif minus the robot's own
                                          baseline, seeds 7000..7063), installed with ONE sign per
                                          population (w4b +1 published, p801 -1)
  docs/runs/RBT-69-travel-direction.txt   RBT-69's per-generation direction of travel on P-801
                                          (an implementation independent of travel_direction.py)
  docs/artifacts/RBT-67/travel_direction_{w4b,p801}.txt   RBT-67's own measurement, same bodies

Per robot the compass sign is +1 (published) if it drives BACKWARD (|offset| > 90 deg) and -1 if
FORWARD.  A robot is CORRECTLY SIGNED when its population's installed sign equals its own compass
sign, INVERTED otherwise.  The two direction readouts are both parsed and must agree on every
robot, or the script stops.

Printed per rung (a = 2w, so a = 32 is installed w = 16 and a = 64 is w = 32; RBT-67 has no a = 16
rung, i.e. nothing at w = 8):
  per robot: mean paired delta, its 95% t-interval over the 64 seeds (t_63 = 1.998), paired t,
  +/-/zero counts and the exact two-sided sign test over non-zero seeds;
  per group (correct / inverted): k/n robots with mean > 0, k/n with the seed interval above 0,
  and the group mean with a 95% t-interval over ROBOTS (the lineage is the unit, RBT-45 s6.5).

Usage: python runs/RBT-97/adversary_resign.py [> runs/RBT-97/adversary_resign.txt]
"""
import json
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)

import numpy as np

# two-sided 95% t quantiles, from tables (no scipy in the project)
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 10: 2.228, 11: 2.201, 13: 2.160, 63: 1.998}


def tint(v):
    v = np.asarray(v, float)
    n = len(v)
    m = float(v.mean())
    if n < 2:
        return m, float("nan"), float("nan"), float("nan")
    se = float(v.std(ddof=1)) / math.sqrt(n)
    h = T975[n - 1] * se
    return m, m - h, m + h, (m / se if se > 0 else float("inf"))


def sign_p(pos, neg):
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def parse_rbt69(path):
    out = {}
    for line in open(path):
        m = re.match(r"\s*gen\s+(\d+):\s+offset\s+([+-][\d.]+)\s+deg", line)
        if m:
            out[int(m.group(1))] = float(m.group(2))
    return out


def parse_rbt67(path):
    out = {}
    for line in open(path):
        m = re.match(r"\|\s*(\d+)\s*\|\s*([+-][\d.]+)\s*\|", line)
        if m:
            out[int(m.group(1))] = float(m.group(2))
    return out


def compass_sign(offset):
    if abs(offset) > 90:
        return +1.0
    if abs(offset) < 90:
        return -1.0
    raise ValueError("sideways")


def main():
    dirs = {
        "w4b": {"RBT-67": parse_rbt67("docs/artifacts/RBT-67/travel_direction_w4b.txt")},
        "p801": {"RBT-67": parse_rbt67("docs/artifacts/RBT-67/travel_direction_p801.txt"),
                 "RBT-69": parse_rbt69("docs/runs/RBT-69-travel-direction.txt")},
    }
    L = []
    P = L.append
    P("RBT-97 adversary: RBT-67's committed per-seed differences, re-signed per robot (independent script)")
    P("")
    groups = {}  # (a, group) -> list of (pop, gen, mean, lo, hi)
    for pop in ("w4b", "p801"):
        d = json.load(open(f"docs/artifacts/RBT-67/{pop}.json"))
        inst = float(d["sign"])
        P(f"== {pop}: installed sign {inst:+.0f} on every robot, seeds {d['seed0']}..{d['seed0'] + d['n_seeds'] - 1}")
        verdict = {}
        for gen in d["gens"]:
            readings = {src: v[gen] for src, v in dirs[pop].items()}
            ss = {src: compass_sign(o) for src, o in readings.items()}
            assert len(set(ss.values())) == 1, f"direction readouts disagree on {pop} g{gen}: {readings}"
            s = next(iter(ss.values()))
            verdict[gen] = "correct" if s == inst else "INVERTED"
            P(f"   g{gen:<4d} offsets " + ", ".join(f"{k} {v:+.1f}" for k, v in readings.items()) +
              f"  -> compass sign {s:+.0f} -> {verdict[gen]}")
        for c in d["cells"]:
            a = float(c["a"])
            if a == 0:
                continue
            P(f"   a = {a:.0f} (installed w = {a / 2:g})")
            for r in c["robots"]:
                diffs = np.asarray(r["diffs"], float)
                m, lo, hi, t = tint(diffs)
                pos, neg = int((diffs > 0).sum()), int((diffs < 0).sum())
                zero = int((diffs == 0).sum())
                assert abs(m - r["delta"]) < 1e-9, "per-seed list does not reproduce the stored delta"
                P(f"      g{r['gen']:<4d} {verdict[r['gen']]:8s} {m:+7.3f} [{lo:+7.3f}, {hi:+7.3f}] t {t:+6.2f}"
                  f"  +{pos:<2d} -{neg:<2d} 0:{zero:<2d} sign p {sign_p(pos, neg):.2g}")
                groups.setdefault((a, verdict[r["gen"]]), []).append((pop, r["gen"], m, lo, hi))
        P("")
    P("== grouped over both populations, per rung (unit = robot)")
    P(f"   {'a':>4s} {'group':8s} {'n':>2s} {'mean>0':>7s} {'seed-CI>0':>9s} {'seed-CI<0':>9s}  mean over robots [95% t, df n-1]")
    for (a, g) in sorted(groups):
        rows = groups[(a, g)]
        n = len(rows)
        m, lo, hi, _ = tint([r[2] for r in rows])
        P(f"   {a:4.0f} {g:8s} {n:2d} {sum(r[2] > 0 for r in rows):>3d}/{n:<3d} {sum(r[3] > 0 for r in rows):>5d}/{n:<3d}"
          f" {sum(r[4] < 0 for r in rows):>5d}/{n:<3d}  {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    P("")
    P("== per population, correctly signed robots only, at a = 32 and 64 (the w = 16, 32 rungs)")
    for pop in ("w4b", "p801"):
        for a in (32.0, 64.0):
            rows = [r for r in groups[(a, "correct")] if r[0] == pop]
            m, lo, hi, _ = tint([r[2] for r in rows])
            P(f"   {pop:5s} a={a:.0f}: {len(rows)} robots, mean {m:+.3f} [{lo:+.3f}, {hi:+.3f}], "
              f"seed-CI > 0 on {sum(r[3] > 0 for r in rows)}/{len(rows)}")
    txt = "\n".join(L) + "\n"
    sys.stdout.write(txt)


if __name__ == "__main__":
    main()
