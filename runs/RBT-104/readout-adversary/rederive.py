"""RBT-104 readout adversary: an independent re-derivation of the SCORED counts, without importing readout.py.

Reads the committed per-arm files (default: the checkout's runs/RBT-104) with its own parsers:
  seasons.txt       viability (never 0 alive, reaches 599, window mean alive >= 30), window income, births
  rbt102.txt        readout (a)'s positive control ("positive control: PASSED"), paying own / in host (re-signed)
  function-pc.txt   readout (b)'s install control: the PRIMARY 'the champion' row must say FOOD-DEPENDENT
  function.txt      the champions' PRIMARY verdict and the ATTRIBUTION 'compass:' verdict
  peek-a3-*.txt     the WINDOW line's k (k_planted), B
and prints the usable counts, the verdict branch, and readout (a)'s held count on usable seeds and on all ten.

  rederive.py [RBT104_DIR]
"""
import math
import os
import re
import sys

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
T = {1: 12.7062, 2: 4.3027, 8: 2.3060, 9: 2.2622}


def tint(xs):
    n = len(xs); m = sum(xs) / n
    if n < 2:
        return m, float("nan"), float("nan")
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    h = T[n - 1] * sd / math.sqrt(n)
    return m, m - h, m + h


def seasons(p):
    lines = open(p).read().splitlines()
    head = lines[0].split("\t")
    rows = [dict(zip(head, l.split("\t"))) for l in lines[1:]]
    rows = [r for r in rows if r["population"] == "conventional"]
    win = [r for r in rows if 300 <= int(r["season"]) <= 599]
    alive = sum(int(r["alive"]) for r in win) / len(win)
    ok = max(int(r["season"]) for r in rows) >= 599 and min(int(r["alive"]) for r in rows) > 0 and alive >= 30
    return ok, sum(float(r["mean_lifetime_score"]) for r in win) / len(win), sum(int(r["births"]) for r in rows)


def primary(p):
    t = open(p).read()
    m = re.search(r"^\s+the champion\s+F\s+(\S+) \[\s*(\S+),\s*(\S+)\]\s+(.+?)\s+\(zeros", t, re.M)
    c = re.search(r"^\s+compass: (.+?)\s+\(exploded", t, re.M)
    return float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4), c.group(1)


def window(p):
    if not os.path.exists(p):
        return None
    m = re.search(r"^WINDOW seed \d+ season \d+: k = (\d+), n = (\d+), B = (\d+) -> .*k_bare = (\d+)", open(p).read(), re.M)
    return None if not m else tuple(int(x) for x in m.groups())


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    A = {}
    for s in SEEDS:
        for arm in ("S1", "S8"):
            r = os.path.join(d, f"{arm}-{s}")
            v, inc, births = seasons(os.path.join(r, "seasons.txt"))
            pca = "positive control: PASSED" in open(os.path.join(r, "rbt102.txt")).read()
            pc = primary(os.path.join(r, "function-pc.txt"))
            fb = primary(os.path.join(r, "function.txt"))
            A[(arm, s)] = dict(viable=v, income=inc, births=births, pca=pca, pc=pc, fb=fb,
                               usable=v and pca and pc[3] == "FOOD-DEPENDENT")
            if arm == "S8":
                A[(arm, s)]["w"] = [window(os.path.join(r, f"peek-a3-{w}.txt")) for w in (300, 599)]
    print("# RBT-104 readout adversary: independent re-derivation of the scored counts (not importing readout.py)\n")
    print("| seed | arm | viable | births | pc(a) | pc(b) F [95%] verdict | usable | champion F verdict | compass |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s in SEEDS:
        for arm in ("S1", "S8"):
            a = A[(arm, s)]; pc, fb = a["pc"], a["fb"]
            print(f"| {s} | {arm} | {a['viable']} | {a['births']} | {'PASS' if a['pca'] else 'FAIL'} | "
                  f"{pc[0]:+.3f} [{pc[1]:+.3f}, {pc[2]:+.3f}] {pc[3]} | {a['usable']} | {fb[0]:+.3f} {fb[3]} | {fb[4]} |")
    u = {arm: [s for s in SEEDS if A[(arm, s)]["usable"]] for arm in ("S1", "S8")}
    print(f"\nusable: S1 {len(u['S1'])}/10 {u['S1']}; S8 {len(u['S8'])}/10 {u['S8']}")
    print(f"  S1 not usable: {[(s, A[('S1', s)]['pc'][3]) for s in SEEDS if s not in u['S1']]}")
    fd = {arm: [s for s in u[arm] if A[(arm, s)]['fb'][3] == 'FOOD-DEPENDENT'] for arm in u}
    cfd = {arm: [s for s in u[arm] if A[(arm, s)]['fb'][4] == 'FOOD-DEPENDENT'] for arm in u}
    print(f"primary FD on usable: S1 {fd['S1']}, S8 {fd['S8']}; compass FD on usable: S1 {cfd['S1']}, S8 {cfd['S8']}")
    held = lambda s: all(w is not None and w[0] > w[2] for w in A[("S8", s)]["w"])
    print(f"held (k_planted > B at 300 and 599): usable S8 {[s for s in u['S8'] if held(s)]}; all ten {[s for s in SEEDS if held(s)]}")
    print(f"single-season readings above B, all ten S8: {sum(w[0] > w[2] for s in SEEDS for w in A[('S8', s)]['w'])}/20")
    inc = [A[("S8", s)]["income"] - A[("S1", s)]["income"] for s in SEEDS]
    print("income S8 - S1, t(9): %+.3f [%+.3f, %+.3f]" % tint(inc))
    print(f"births S8 > S1 on {sum(A[('S8', s)]['births'] > A[('S1', s)]['births'] for s in SEEDS)}/10")
    both = [s for s in SEEDS if s in u["S1"] and s in u["S8"]]
    print(f"F S8 - S1 on seeds usable in both {both}: " + "%+.3f [%+.3f, %+.3f]" % tint([A[('S8', s)]['fb'][0] - A[('S1', s)]['fb'][0] for s in both]))
    pcd = [A[("S8", s)]["pc"][0] - A[("S1", s)]["pc"][0] for s in SEEDS]
    print("POST HOC P1 re-derived: install-control F, S8 host - S1 host, t(9): %+.3f [%+.3f, %+.3f]" % tint(pcd))
    n8 = len(u["S8"])
    verdict = ("VOID" if n8 < 7 else "SUPPORTED/FALSIFIED/NOT DECIDED per 6.1")
    print(f"\nVERDICT (6.1, first rule that applies): S8 usable {n8} < 7 -> {verdict}")


if __name__ == "__main__":
    main()
