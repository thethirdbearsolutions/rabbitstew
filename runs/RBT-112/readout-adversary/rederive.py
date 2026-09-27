"""RBT-112 readout adversary, attack 2: every registered number, re-derived with independent code.

POST HOC, PRINT-ONLY.  Its own parsers and arithmetic, standard library only (no numpy, no readout.py import): the
committed held-300/599.txt, function-patchy/uniform.txt and seasons.txt of the ten HU (runs/RBT-106/HU-SEED) and ten
HZ (runs/RBT-112/HZ-SEED) arms.  Prints HELD per arm, #HELD, #LOST, the COMPASS counts, the paired F intervals and
the side effects, each beside the value readout.txt printed.
Usage: rederive.py
"""
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(D))
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
T = {9: 2.262}


def adir(arm, s):
    return os.path.join(ROOT, "runs", "RBT-106", f"HU-{s}") if arm == "HU" else os.path.join(D, f"HZ-{s}")


def held(arm, s, season):
    t = open(os.path.join(adir(arm, s), f"held-{season}.txt")).read()
    k = int(re.search(r"hits: k_planted = (\d+)", t).group(1))
    n = int(re.search(r"with a planted root (\d+)", t).group(1))
    B = int(re.search(r"95th percentile B = (\d+)", t).group(1))
    return k, n, B


def line(arm, s, world):
    t = open(os.path.join(adir(arm, s), f"function-{world}.txt")).read()
    m = re.search(r"^LINE \S+: (.+?)\s+F ([+-][\d.]+) \[.*?\]\s+compass (.+?)\s+bodies", t, re.M)
    return m.group(1) == "FOOD-DEPENDENT", float(m.group(2)), m.group(3)


def window(arm, s):
    rows = [l.split("\t") for l in open(os.path.join(adir(arm, s), "seasons.txt")).read().splitlines()]
    h = rows[0]
    c = [dict(zip(h, r)) for r in rows[1:] if r[1] == "conventional"]
    w = [r for r in c if 300 <= int(r["season"]) <= 599]
    return (st.mean(float(r["mean_lifetime_score"]) for r in w), st.mean(int(r["alive"]) for r in w), sum(int(r["births"]) for r in c))


def ti(v):
    m = st.mean(v)
    h = T[len(v) - 1] * st.stdev(v) / math.sqrt(len(v))
    return f"{m:+.3f} [{m - h:+.3f}, {m + h:+.3f}]"


def main():
    print("# RBT-112 readout adversary: independent re-derivation (POST HOC, print-only, stdlib only)\n")
    H, L, C, dF, dFu, inc, alive, births = {"HU": 0, "HZ": 0}, 0, {"HU": 0, "HZ": 0}, [], [], [], [], []
    for s in SEEDS:
        for arm in ("HU", "HZ"):
            a, b = held(arm, s, 300), held(arm, s, 599)
            H[arm] += a[0] > a[2] and b[0] > b[2]
            fd, F, att = line(arm, s, "patchy")
            C[arm] += fd and att == "FOOD-DEPENDENT"
            if arm == "HZ":
                L += a[1] == 0 or b[1] == 0
                print(f"HZ-{s}: k/n/B {a[0]}/{a[1]}/{a[2]}, {b[0]}/{b[1]}/{b[2]} -> "
                      f"{'LOST' if a[1] == 0 or b[1] == 0 else 'HELD' if a[0] > a[2] and b[0] > b[2] else 'NOT HELD'}; "
                      f"patchy {'FD' if fd else '-'} {att}")
        dF.append(line("HZ", s, "patchy")[1] - line("HU", s, "patchy")[1])
        dFu.append(line("HZ", s, "uniform")[1] - line("HU", s, "uniform")[1])
        wz, wu = window("HZ", s), window("HU", s)
        inc.append(wz[0] - wu[0]); alive.append(wz[1] - wu[1]); births.append(wz[2] - wu[2])
    print(f"\nHELD: HU {H['HU']}, HZ {H['HZ']}   (readout.txt: HU 0, HZ 1)")
    print(f"#LOST(HZ): {L}   (readout.txt: 1)")
    print(f"COMPASS lines, patchy: HU {C['HU']}, HZ {C['HZ']}   (readout.txt: HU 0, HZ 5)")
    print(f"paired F patchy {ti(dF)}, uniform {ti(dFu)}   (readout.txt: +1.654 [+0.785, +2.523], +0.468 [+0.290, +0.646])")
    print(f"SE-Z income {ti(inc)}; alive {st.mean(alive):+.3f}; births {ti(births)}   "
          f"(readout.txt: +0.160 [+0.050, +0.271]; +0.000; +6.300 [-44.560, +57.160])")


if __name__ == "__main__":
    main()
