"""RBT-112 readout adversary, attacks 1 and 6: could HELD fire under S = 0, and what does FALSIFIED exclude?

POST HOC, PRINT-ONLY.  Reads the committed held-300/599.txt of every HZ and HU arm through RBT-106's readout.py
parser, and power.py's own model functions (imported, unchanged).  Prints:
  (1) per seed and season: k_planted, n, mu, B, B / n (the share HELD needs), and the headroom n - B;
  (2) the power model re-run at each HZ arm's REALISED n and mean depth (not part 2's genealogy, not n = 40):
      q per seed, and P(#HELD(HZ) <= 1) over the ten seeds, at rho 0 / 0.10 (fit) / 0.30;
  (3) a direct reading of s from the arms themselves: the BetaBinomial log-likelihood of every observed k_planted
      (both seasons, the ten seeds) under x(d, s) = power.py's mutation-selection recursion, profiled over s, at
      rho 0.10 and 0.30, with rho also profiled.  The two seasons are treated as independent (they are not:
      an approximation, noted).
Usage: instrument.py
"""
import importlib.util
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(D))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


pw = _load("rbt112_power_adv", os.path.join(D, "power.py"))
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)


def held(arm, seed, season):
    d = os.path.join(ROOT, "runs", "RBT-106", f"HU-{seed}") if arm == "HU" else os.path.join(D, f"HZ-{seed}")
    t = open(os.path.join(d, f"held-{season}.txt")).read()
    m = re.search(r"^HELD seed \d+ season \d+: k_planted = (\d+), n = (\d+), mu = ([\d.]+), B = (\d+), k_bare = (\d+), "
                  r"depth = ([\d.]+|nan), roots = (\d+)", t, re.M)
    k, n, mu, B, kb = int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4)), int(m.group(5))
    return dict(k=k, n=n, mu=mu, B=B, kb=kb, d=float(m.group(6)), roots=int(m.group(7)))


def lbb(k, n, x, rho):
    """log BetaBinomial pmf (mean x, intra-class correlation rho; rho 0 = binomial)."""
    x = min(max(x, 1e-9), 1 - 1e-9)
    lc = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    if rho <= 0:
        return lc + k * math.log(x) + (n - k) * math.log(1 - x)
    ab = (1 - rho) / rho
    a, b = x * ab, (1 - x) * ab
    lB = lambda p, q: math.lgamma(p) + math.lgamma(q) - math.lgamma(p + q)
    return lc + lB(k + a, n - k + b) - lB(a, b)


def main():
    print("# RBT-112 readout adversary: the HELD instrument under S = 0 (POST HOC, print-only)\n")
    print("## (1) What HELD needed, per seed: k_planted / n / mu / B, the share B/n that k_planted had to exceed, headroom n - B\n")
    print("| seed | arm | 300: k/n, mu, B, B/n, n-B, depth | 599: k/n, mu, B, B/n, n-B, depth | HELD | larger shortfall (the deciding reading) |")
    print("|---|---|---|---|---|---|")
    obs = {}
    for s in SEEDS:
        for arm in ("HU", "HZ"):
            h = {se: held(arm, s, se) for se in (300, 599)}
            obs[(arm, s)] = h
            cell = lambda r: (f"{r['k']}/{r['n']}, {r['mu']:.3f}, {r['B']}, {r['B'] / r['n']:.2f}, {r['n'] - r['B']}, {r['d']:.1f}"
                              if r["n"] else f"{r['k']}/0, -, {r['B']}, -, 0, -")
            hd = all(h[se]["k"] > h[se]["B"] for se in (300, 599))
            miss = min((h[se]["k"] - h[se]["B"] - 1, se) for se in (300, 599))
            print(f"| {s} | {arm} | {cell(h[300])} | {cell(h[599])} | {hd} | "
                  f"{'held' if hd else f'short by {-miss[0]} at {miss[1]}'} |")
    z = [obs[("HZ", s)] for s in SEEDS]
    bn3 = [r[300]["B"] / r[300]["n"] for r in z if r[300]["n"] >= 10]
    bn5 = [r[599]["B"] / r[599]["n"] for r in z if r[599]["n"] >= 10]
    print(f"\nHZ, seeds with n >= 10: B/n at 300 {min(bn3):.2f}-{max(bn3):.2f} (mean {np.mean(bn3):.2f}); at 599 {min(bn5):.2f}-{max(bn5):.2f} "
          f"(mean {np.mean(bn5):.2f})")
    ceil = [s for s in SEEDS if min(obs[("HZ", s)][se]["n"] - obs[("HZ", s)][se]["B"] for se in (300, 599)) <= 1]
    print(f"HZ seeds where HELD was unreachable or needed every planted-rooted genome (n - B <= 1 at a reading): {ceil}")
    print("HZ within 5 of B at a reading it failed: " + ", ".join(
        f"{s} ({se}: k {obs[('HZ', s)][se]['k']} vs B {obs[('HZ', s)][se]['B']})" for s in SEEDS for se in (300, 599)
        if 0 <= obs[("HZ", s)][se]["B"] - obs[("HZ", s)][se]["k"] <= 5 and obs[("HZ", s)][se]["n"] > 0))

    print("\n## (2) power.py's model at the arms' REALISED n and depth (HZ's own held files), S = 0 operator\n")
    G = {(s, se): (obs[("HZ", s)][se]["n"], obs[("HZ", s)][se]["d"] if obs[("HZ", s)][se]["n"] else float("nan"))
         for s in SEEDS for se in (300, 599)}
    grid = (0.0, 0.05, 0.089, 0.10, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5)
    print("| s | x(d=10) / x(d=20) | mean q_Z, rho 0 / 0.10 / 0.30 | P(#HELD(HZ) <= 1), rho 0 / 0.10 / 0.30 | E#HELD(HZ) at rho 0.10 | per-seed q at rho 0.10 (801,4,804,805,806,807,1,2,3,7) |")
    print("|---|---|---|---|---|---|")
    for s_ in grid:
        qs = {r: [pw.q_seed(sd, s_, "S0", r, G) for sd in SEEDS] for r in (0.0, 0.1, 0.3)}
        pf = {r: float(pw.poibin(qs[r])[:2].sum()) for r in qs}
        print(f"| {s_:.3f} | {pw.x_of(10, s_, pw.U['S0']):.3f} / {pw.x_of(20, s_, pw.U['S0']):.3f} | "
              + " / ".join(f"{np.mean(qs[r]):.3f}" for r in (0.0, 0.1, 0.3)) + " | "
              + " / ".join(f"{pf[r]:.3f}" for r in (0.0, 0.1, 0.3)) + f" | {sum(qs[0.1]):.2f} | "
              + ", ".join(f"{q:.2f}" for q in qs[0.1]) + " |")
    print("\n(the balance point: with u = 0.089, x can stay above 0 only if (1 + s)(1 - u) > 1, i.e. s > u / (1 - u) = "
          f"{pw.U['S0'] / (1 - pw.U['S0']):.3f}; below it the share decays towards 0 whatever s is)")

    print("\n## (3) s read from the arms: profile log-likelihood of the observed k_planted under x(d, s) (both seasons, ten seeds)\n")
    sgrid = np.round(np.arange(0.0, 1.0001, 0.01), 3)
    rows = [(r[se]["k"], r[se]["n"], r[se]["d"]) for r in z for se in (300, 599) if r[se]["n"] > 0]
    for rho in (0.1, 0.3, "profile"):
        rhos = (0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7) if rho == "profile" else (rho,)
        ll = []
        for s_ in sgrid:
            xs = {d: pw.x_of(d, s_, pw.U["S0"]) for _, _, d in rows}
            ll.append(max(sum(lbb(k, n, xs[d], r) for k, n, d in rows) for r in rhos))
        ll = np.array(ll)
        i = int(ll.argmax())
        inside = sgrid[ll >= ll.max() - 1.92]
        at = lambda v: ll[int(np.argmin(np.abs(sgrid - v)))] - ll.max()
        print(f"  rho {rho}: MLE s = {sgrid[i]:.2f}; 95% profile interval (drop 1.92) s in [{inside.min():.2f}, {inside.max():.2f}]"
              f"{' (upper end at the grid edge)' if inside.max() >= sgrid[-1] else ''}; "
              f"log-lik drop at s = 0.15 / 0.20 / 0.30: {at(0.15):+.2f} / {at(0.2):+.2f} / {at(0.3):+.2f}")
    if True:
        best = max(((sum(lbb(k, n, pw.x_of(d, 0.0, pw.U['S0']), r) for k, n, d in rows), r)
                    for r in (0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)))
        print(f"  rho that best fits the arms at s = 0: {best[1]} (the power model's fit to the part-2 null: 0.10)")
    print("\n  HZ observed share k_planted/n against the no-selection mu, per reading (n > 0): " + "; ".join(
        f"{s}@{se}: {obs[('HZ', s)][se]['k'] / obs[('HZ', s)][se]['n']:.2f} vs {obs[('HZ', s)][se]['mu']:.2f}"
        for s in SEEDS for se in (300, 599) if obs[("HZ", s)][se]["n"]))
    ex = [math.log((r[se]["k"] + 1) / (r[se]["n"] * r[se]["mu"] + 1)) for r in z for se in (599,) if r[se]["n"]]
    print(f"  HZ log-excess log((k+1)/(n mu+1)) at 599, seeds with n > 0: mean {np.mean(ex):+.3f} "
          f"[{np.mean(ex) - pw.T975[len(ex) - 1] * np.std(ex, ddof=1) / math.sqrt(len(ex)):+.3f}, "
          f"{np.mean(ex) + pw.T975[len(ex) - 1] * np.std(ex, ddof=1) / math.sqrt(len(ex)):+.3f}] (t({len(ex) - 1}))")


if __name__ == "__main__":
    main()
