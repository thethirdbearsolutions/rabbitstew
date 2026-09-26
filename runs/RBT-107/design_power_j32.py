"""RBT-107 Amendment 2 (F3, F4): the null and the power at J = 32, before any arm.

    python runs/RBT-107/design_power_j32.py > runs/RBT-107/design_power_j32.txt

Reads garden/j32/ (design_j32.sh; no C4 shift arm is read):
  c0-SEED-KIND, base-SEED-KIND-s599, cull20-SEED-KIND-s599 on 32 worlds (0..7 + 8..15 + 16..31), the ten old seeds
  aa105-SEED-bK-holistic-s599 on 32 worlds: RBT-105's founder-sharing replicates (K = 1, 2; 8 seeds)
and the parts (garden/parts/, garden/) for the split-halves.
1. ARITHMETIC: Delta0 per seed and fauna at J = 32, with its world-sampling term (split-half 0..15 against 16..31; the
   world effect is common to every seed, so the t interval across seeds does not contain it).
2. THE NULL AT d ~ 240: A_NB = G_cull20^flat - G_base^flat at 599, per seed and fauna, and the paired null
   P_NB = A_NB(co) - A_NB(des).  Split into measurement (from the split-half: var of (half1 - half2)/2 per seed, which is
   the variance of a J = 32 mean's world-and-grouping noise for one population, times 2 for a contrast) and drift (the rest).
3. THE DEEP NULL, co-evolved (F3): RBT-105's replicates at 599 diverged from season 0 (~17 events at the base rate,
   depth.txt), so A_AA = G_rep^flat - G_orig^flat is an A/A at about the depth of T + 600.  Its drift part is scaled to
   T + 800 by 800/600 (variance); the designed fauna has no deep A/A (byte-identical across RBT-105's replicates), so its
   drift part is scaled from the d ~ 240 cull20 null by 800/240.  Both scalings are of the DRIFT part only.  The ratio of
   the co-evolved deep A/A's drift to the cull20 drift scaled the same way is printed as a check of the sqrt(d) model.
4. POWER, one-sided alpha 0.05, by the adversary's method (probe_power.py): each simulated seed is one of the ten null rows
   (co, des kept together), resampled with replacement, one random sign flip per row, smoothed (Silverman), then rescaled
   so its variance matches the target null of 3.; H1 adds the effect.  Tests: Yuen 20% (PRIMARY), t, Wilcoxon; for H1-DES and
   H1-PAIR together the Holm step (the scored rule).  Also the Gaussian worst case at the full RMS.  n = 10, 20, 30.
   H-REP (T + 110): the drift part scaled 110/240, measurement kept.
"""
import glob
import importlib.util
import math
import os
import re
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("stats107", os.path.join(HERE, "stats107.py"))
ST = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ST)
J32 = os.path.join(HERE, "garden", "j32")
PARTS = os.path.join(HERE, "garden", "parts")
OLD = [801, 804, 805, 806, 807, 1, 2, 3, 4, 7]
KINDS = ("holistic", "conventional")
REPS = 3000


def rows(path):
    out = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        out[f[4]] = (float(f[5]), float(f[6]))
    return out


def G(path):
    if not os.path.exists(path):
        return None
    r = rows(path)
    return statistics.fmean(v[0] for v in r.values()), statistics.fmean(v[1] for v in r.values())


def halves(label):
    """(G over worlds 0..15, G over worlds 16..31): 0..7 from garden/, 8..15 and 16..31 from parts/ (or 0..15 for aa105)."""
    if label.startswith("aa105"):
        a, b = os.path.join(PARTS, f"{label}.w00-15.txt"), os.path.join(PARTS, f"{label}.w16-31.txt")
        return G(a), G(b)
    a0, a1, b = os.path.join(HERE, "garden", f"{label}.txt"), os.path.join(PARTS, f"{label}.w08-15.txt"), os.path.join(PARTS, f"{label}.w16-31.txt")
    g0, g1, gb = G(a0), G(a1), G(b)
    if not (g0 and g1 and gb):
        return None, None
    return ((g0[0] + g1[0]) / 2, (g0[1] + g1[1]) / 2), gb


def fmt(v):
    n = len(v)
    m = statistics.fmean(v)
    hw = 2.262 * statistics.stdev(v) / math.sqrt(n) if n == 10 else (statistics.stdev(v) * {7: 2.447, 8: 2.365, 9: 2.306, 11: 2.228, 12: 2.201, 13: 2.179, 14: 2.160, 15: 2.145, 16: 2.131}.get(n, 2.0) / math.sqrt(n))
    return f"{m:+.3f} [{m - hw:+.3f}, {m + hw:+.3f}] {sum(x > 0 for x in v)}/{n} positive"


def rms(v):
    return math.sqrt(statistics.fmean(x * x for x in v))


def main():
    print(__doc__.split("\n\n")[0])
    print("\n== 1. ARITHMETIC at J = 32: Delta0 = G_C0^flat - G_C0^random")
    for k in KINDS:
        d0, sh = [], []
        for s in OLD:
            g = G(os.path.join(J32, f"c0-{s}-{k}.txt"))
            h1, h2 = halves(f"c0-{s}-{k}")
            if g:
                d0.append(g[0] - g[1])
                print(f"seed {s:>4} {k:12s} C0 flat {g[0]:+.3f} random {g[1]:+.3f} Delta0 {g[0] - g[1]:+.3f}"
                      + (f"  halves {h1[0] - h1[1]:+.3f} / {h2[0] - h2[1]:+.3f}" if h1 and h2 else ""))
            if h1 and h2:
                sh.append((h1[0] - h1[1]) - (h2[0] - h2[1]))
        if d0:
            print(f"DELTA0 {k:12s} {fmt(d0)}; world-sampling term: split-half difference {fmt(sh)} -> the level's common-world "
                  f"sd ~ {abs(statistics.fmean(sh)) / 2:.3f} (mean half-difference / 2), per-seed ~ {rms(sh) / 2:.3f}")
    print("\n== 2. THE NULL at d ~ 240 (J = 32): A_NB = G_cull20^flat - G_base^flat at 599; drift and measurement")
    null = {}
    parts = {}
    for k in KINDS:
        ab, meas = [], []
        for s in OLD:
            n, b = G(os.path.join(J32, f"cull20-{s}-{k}-s599.txt")), G(os.path.join(J32, f"base-{s}-{k}-s599.txt"))
            if not (n and b):
                continue
            ab.append(n[0] - b[0])
            (n1, n2), (b1, b2) = halves(f"cull20-{s}-{k}-s599"), halves(f"base-{s}-{k}-s599")
            if n1 and n2 and b1 and b2:
                meas.append(((n1[0] - b1[0]) - (n2[0] - b2[0])) / 2)  # half-difference / 2: the J=32 contrast's noise
            print(f"seed {s:>4} {k:12s} A_NB {n[0] - b[0]:+.3f}")
        if ab:
            vt, vm = statistics.fmean(x * x for x in ab), statistics.fmean(x * x for x in meas) if meas else 0.0
            null[k], parts[k] = ab, (vt, vm)
            print(f"NULL {k:12s} A_NB {fmt(ab)}; RMS {math.sqrt(vt):.3f}; measurement RMS (split-half) {math.sqrt(vm):.3f} "
                  f"= {100 * vm / vt:.0f}% of the variance; drift RMS {math.sqrt(max(vt - vm, 0)):.3f}")
    if all(k in null for k in KINDS):
        pn = [a - b for a, b in zip(null["holistic"], null["conventional"])]
        print(f"NULL paired P_NB {fmt(pn)}; RMS {rms(pn):.3f}; r(co, des) {statistics.correlation(null['holistic'], null['conventional']):+.2f}")
    print("\n== 3. THE DEEP NULL: RBT-105's replicates at 599 (co-evolved, ~17 events from season 0, J = 32)")
    aa, aam = [], []
    for p in sorted(glob.glob(os.path.join(J32, "aa105-*.txt"))):
        m = re.match(r"aa105-(\d+)-b(\d)-holistic-s599", os.path.basename(p)[:-4])
        o = os.path.join(J32, f"base-{m.group(1)}-holistic-s599.txt")
        g, go = G(p), G(o)
        if g and go:
            aa.append(g[0] - go[0])
            (r1, r2), (o1, o2) = halves(os.path.basename(p)[:-4]), halves(f"base-{m.group(1)}-holistic-s599")
            if r1 and r2 and o1 and o2:
                aam.append(((r1[0] - o1[0]) - (r2[0] - o2[0])) / 2)
            print(f"{os.path.basename(p)[:-4]:30s} A_AA {g[0] - go[0]:+.3f}")
    target = {}
    if aa and "holistic" in parts:
        va, vam = statistics.fmean(x * x for x in aa), statistics.fmean(x * x for x in aam) if aam else 0.0
        drift_aa = max(va - vam, 0.0)
        vt, vm = parts["holistic"]
        drift_c20 = max(vt - vm, 0.0)
        print(f"DEEP A/A co-evolved {fmt(aa)}; RMS {math.sqrt(va):.3f}; measurement {math.sqrt(vam):.3f}; drift {math.sqrt(drift_aa):.3f}")
        print(f"CHECK of the sqrt(d) model (co-evolved): deep A/A drift variance {drift_aa:.4f} (600 seasons) against the cull20 "
              f"drift variance scaled to 600, {drift_c20 * 600 / 240:.4f} (ratio {drift_aa / (drift_c20 * 600 / 240) if drift_c20 else float('nan'):.2f})")
        target["holistic"] = (drift_aa * 800 / 600, vm)
    if "conventional" in parts:
        vt, vm = parts["conventional"]
        target["conventional"] = (max(vt - vm, 0.0) * 800 / 240, vm)
    for k, (vd, vm) in target.items():
        print(f"TARGET NULL at T+800 (MEASURED: co-evolved from the deep A/A) {k:12s}: drift {math.sqrt(vd):.3f} + measurement "
              f"{math.sqrt(vm):.3f} -> RMS {math.sqrt(vd + vm):.3f}")
    if len(target) < 2:
        print("POWER: not computed (the J = 32 rows are incomplete)")
        return
    # the conservative alternative: the co-evolved drift from the cull20 null scaled 800/240, like the designed
    vt, vm = parts["holistic"]
    conservative = {"holistic": (max(vt - vm, 0.0) * 800 / 240, vm), "conventional": target["conventional"]}
    print(f"TARGET NULL at T+800 (CONSERVATIVE: co-evolved from cull20 scaled 800/240) holistic    : drift "
          f"{math.sqrt(conservative['holistic'][0]):.3f} + measurement {math.sqrt(vm):.3f} -> RMS {math.sqrt(sum(conservative['holistic'])):.3f}")

    print("\n== 4. POWER (one-sided alpha 0.05; Yuen 20% PRIMARY; the Holm pair is the scored rule)")
    rng = np.random.default_rng(1074)
    base = np.array([[a, b] for a, b in zip(null["holistic"], null["conventional"])])
    cur = base.var(0) + base.mean(0) ** 2  # mean square per fauna

    def draw(n, scale, gauss=False):
        idx = rng.integers(0, len(base), size=(REPS, n))
        x = base[idx]
        if gauss:
            x = rng.normal(0, np.sqrt(cur), size=(REPS, n, 2))
        else:
            x = x * rng.choice([-1, 1], size=(REPS, n, 1))
            bw = 0.9 * np.minimum(base.std(0, ddof=1), (np.percentile(base, 75, 0) - np.percentile(base, 25, 0)) / 1.34) * len(base) ** -0.2
            x = x + rng.normal(0, 1, size=x.shape) * bw
        return x * scale

    def p_of(test, v):
        if test == "yuen":
            return ST.yuen(list(v))[3]
        if test == "t":
            return ST.t_test(list(v))[3]
        return ST.wilcoxon(list(v))[1]

    for tag, factor, tg in (("T+800 MEASURED", 1.0, target), ("T+800 CONSERVATIVE", 1.0, conservative),
                            ("T+110 (H-REP) MEASURED", 110 / 800, target), ("T+110 (H-REP) CONSERVATIVE", 110 / 800, conservative)):
        scale = np.array([math.sqrt((tg[k][0] * factor + tg[k][1]) / cur[i]) for i, k in enumerate(KINDS)])
        print(f"-- {tag}: null RMS co-evolved {math.sqrt(tg['holistic'][0] * factor + tg['holistic'][1]):.3f}, "
              f"designed {math.sqrt(tg['conventional'][0] * factor + tg['conventional'][1]):.3f}")
        for n in (10, 20, 30):
            for des_eff, pair_eff in ((-0.22, 0.27), (-0.15, 0.15), (-0.10, 0.10)):
                for gauss in (False, True):
                    x = draw(n, scale, gauss)
                    des = -(x[:, :, 1] + des_eff)                  # H1-DES: designed A_SB < 0, tested as "greater" on -x
                    pair = (x[:, :, 0] - x[:, :, 1]) + pair_eff    # H1-PAIR: P > 0 (the paired effect added whole)
                    out = []
                    for test in ("yuen", "t", "wilcoxon"):
                        pd = np.array([p_of(test, r) for r in des])
                        pp = np.array([p_of(test, r) for r in pair])
                        rej = np.array([ST.holm([a, b]) for a, b in zip(pd, pp)])
                        out.append(f"{test} DES {np.mean(pd <= 0.05):.2f} PAIR {np.mean(pp <= 0.05):.2f} Holm DES {rej[:, 0].mean():.2f} PAIR {rej[:, 1].mean():.2f}")
                    if des_eff == -0.22 or not gauss:
                        print(f"POWER {tag} n={n:>2} des {des_eff:+.2f} pair {pair_eff:+.2f} {'GAUSS' if gauss else 'EMPIRICAL'}: " + " | ".join(out))
        # size check
        x = draw(20, scale)
        pd = np.array([ST.yuen(list(-r[:, 1]))[3] for r in x])
        pp = np.array([ST.yuen(list(r[:, 0] - r[:, 1]))[3] for r in x])
        print(f"SIZE {tag} n=20 Yuen under H0: DES {np.mean(pd <= 0.05):.3f} PAIR {np.mean(pp <= 0.05):.3f}")


if __name__ == "__main__":
    main()
