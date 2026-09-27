"""RBT-107 H1 adversary: re-derive the scored H1 lines from the committed garden files, print only.

    RBT107_GARDEN=<#376 checkout>/runs/RBT-107/garden/readout python runs/RBT-107/h1-adversary/rederive.py

Independent of readout.py and stats107.py: its own garden parser, its own Yuen (Wilcox 2012, 4.6: one-sample trimmed
mean, 20% trim, winsorized variance, se = s_w / ((1 - 2 trim) sqrt n) as the textbook has it AND the registered
h / n form), its own Student t cdf (Simpson's rule on the density, not the incomplete beta), its own Holm, its own
t intervals (quantile by bisection on that cdf).  The common set is re-derived from the files, not from line 398.
"""
import glob
import math
import os
import re

GARDEN = os.environ.get("RBT107_GARDEN", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "garden", "readout"))
SEEDS = range(11, 31)


def tpdf(x, df):
    return math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi) * (1 + x * x / df) ** (-(df + 1) / 2)


def tcdf(t, df, m=20000):
    a, h = abs(t), abs(t) / m
    s = tpdf(0, df) + tpdf(a, df) + sum((4 if i % 2 else 2) * tpdf(i * h, df) for i in range(1, m))
    area = s * h / 3
    return 0.5 + area if t >= 0 else 0.5 - area


def tq975(df):
    lo, hi = 0.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tcdf(mid, df, 4000) < 0.975 else (lo, mid)
    return (lo + hi) / 2


def yuen_greater(x, textbook=False):
    n = len(x)
    g = int(0.2 * n)
    xs = sorted(x)
    tm = sum(xs[g:n - g]) / (n - 2 * g)
    w = [min(max(v, xs[g]), xs[n - g - 1]) for v in xs]
    wm = sum(w) / n
    sw = math.sqrt(sum((v - wm) ** 2 for v in w) / (n - 1))
    h = n - 2 * g
    se = sw / (0.6 * math.sqrt(n)) if textbook else sw * math.sqrt(n) / h
    t = tm / se
    return tm, 1 - tcdf(t, h - 1)


def rows(label):
    p = os.path.join(GARDEN, label + ".txt")
    if not os.path.exists(p):
        return None
    out = [l.rstrip("\n").split("\t") for l in open(p) if l.strip() and not l.startswith("#")]
    return [(float(f[5]), float(f[6])) for f in out]


def mean(v):
    return sum(v) / len(v)


def G(label):
    r = rows(label)
    return (mean([a for a, _ in r]), mean([b for _, b in r])) if r else None


def con(seed, kind, d):
    S, B, N = (G(f"fresh-{a}-{seed}-{kind}-d{d}") for a in ("shift", "base", "cull20"))
    if not (S and B and N):
        return None
    return dict(SB=S[0] - B[0], SN=S[0] - N[0], I=(S[0] - S[1]) - (B[0] - B[1]), IN=(N[0] - N[1]) - (B[0] - B[1]))


def ci(v):
    n, m = len(v), mean(v)
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    hw = tq975(n - 1) * sd / math.sqrt(n)
    return m, m - hw, m + hw


def holm(ps, alpha=0.05):
    rej, k = [False] * len(ps), 0
    for i in sorted(range(len(ps)), key=lambda i: ps[i]):
        if ps[i] > alpha / (len(ps) - k):
            break
        rej[i], k = True, k + 1
    return rej


def main():
    print(f"garden: {os.path.normpath(GARDEN)} ({len(glob.glob(os.path.join(GARDEN, '*.txt')))} merged files)")
    c = {(s, k, d): con(s, k, d) for s in SEEDS for k in ("holistic", "conventional") for d in (110, 800)}
    for s in SEEDS:
        for k in ("holistic", "conventional"):
            n = [len(rows(f"fresh-{a}-{s}-{k}-d800") or []) for a in ("shift", "base", "cull20")]
            if 0 in n:
                print(f"  seed {s} {k}: rows at d800 shift/base/cull20 = {n}: no contrast")
    common = [s for s in SEEDS if c[(s, "holistic", 800)] and c[(s, "conventional", 800)]]
    print(f"common set at d800 (both faunas, SB and SN): n = {len(common)}, missing {sorted(set(SEEDS) - set(common))}")
    comp = {}
    for tag, key in (("DES A_SB", "SB"), ("DES A_SN", "SN")):
        comp[tag] = [c[(s, "conventional", 800)][key] for s in common]
    for tag, key in (("PAIR P", "SB"), ("PAIR P_N", "SN")):
        comp[tag] = [c[(s, "holistic", 800)][key] - c[(s, "conventional", 800)][key] for s in common]
    p = {}
    for tag, v in comp.items():
        direction = -1 if tag.startswith("DES") else +1
        tm, py = yuen_greater([direction * x for x in v])
        _, pyb = yuen_greater([direction * x for x in v], textbook=True)
        p[tag] = py
        print(f"  {tag:9s} n={len(v)} trimmed mean {direction * tm:+.3f}  Yuen p {py:.4f} (registered h/n se)  "
              f"[textbook (1-2 trim) se: {pyb:.4f}]")
    iut = {"DES": max(p["DES A_SB"], p["DES A_SN"]), "PAIR": max(p["PAIR P"], p["PAIR P_N"])}
    rej = holm([iut["DES"], iut["PAIR"]])
    print(f"  IUT p: DES {iut['DES']:.4f}, PAIR {iut['PAIR']:.4f}; Holm at 0.05: DES {'SUPPORTED' if rej[0] else 'NOT SUPPORTED'}, "
          f"PAIR {'SUPPORTED' if rej[1] else 'NOT SUPPORTED'}")
    alt = ("DES/PAIR, Holm floor 0.025: the smaller IUT p would need <= 0.025; it is "
           f"{min(iut.values()):.4f}")
    print("  " + alt)
    for half in ("DES", "PAIR"):
        if half == "DES":
            ii = [c[(s, "conventional", 800)]["I"] for s in common]
            iin = [c[(s, "conventional", 800)]["I"] - c[(s, "conventional", 800)]["IN"] for s in common]
            direction = -1
        else:
            ii = [c[(s, "holistic", 800)]["I"] - c[(s, "conventional", 800)]["I"] for s in common]
            iin = [(c[(s, "holistic", 800)]["I"] - c[(s, "holistic", 800)]["IN"]) - (c[(s, "conventional", 800)]["I"] - c[(s, "conventional", 800)]["IN"]) for s in common]
            direction = +1
        a, b = ci(ii), ci(iin)
        on_side = lambda x: (direction * x[1] > 0 and direction * x[2] > 0) if direction > 0 else (x[2] < 0)
        other = lambda x: (x[1] > 0) if direction < 0 else (x[2] < 0)
        reading = "SPECIFIC" if on_side(a) and on_side(b) else "OPPOSITE" if other(a) else "GENERAL"
        print(f"  {half} I {a[0]:+.3f} [{a[1]:+.3f}, {a[2]:+.3f}]; I - I_N {b[0]:+.3f} [{b[1]:+.3f}, {b[2]:+.3f}]; {reading}")
    full = [s for s in SEEDS if c[(s, "conventional", 800)] and c[(s, "conventional", 110)]]
    inc = [c[(s, "conventional", 800)]["SB"] - c[(s, "conventional", 110)]["SB"] for s in full]
    tm, py = yuen_greater(inc)
    print(f"  H-ALT increment (designed A_SB d800 - d110, > 0): n={len(inc)} trimmed mean {tm:+.3f} Yuen p {py:.4f}")
    sb = [c[(s, "conventional", 800)]["SB"] for s in full]
    m, lo, hi = ci(sb)
    print(f"  designed A_SB d800 on n={len(sb)}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")


if __name__ == "__main__":
    main()
