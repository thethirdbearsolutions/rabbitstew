"""RBT-107 H-REP readout adversary: every scored p-value re-derived from the committed garden and tables, independently.

    python runs/RBT-107/hrep/adversary/rederive.py [HREP_DIR]       (default runs/RBT-107/hrep; stdlib only, no scipy)

Imports nothing from readout.py, stats107.py or RBT-92: its own parser for garden/*.txt, seasons.txt and lineage-last.txt,
its own Student t cdf (adaptive Simpson on the density, not stats107's incomplete-beta continued fraction), its own exact
Wilcoxon signed-rank (enumeration over doubled ranks, zeros dropped, midranks), its own Yuen 20% (one-sample, with the
se stats107.yuen's code uses; yuen_se.py prints the other two conventions), Holm and the IUT.  It reads only files under HREP_DIR, all of which stop at season 470.

Scored as registered (A2.1, A2.8): per component, Yuen 20% one-sided; a Yuen p in (0.04, 0.05] counts only if the exact
Wilcoxon p is also <= 0.05; IUT p = the larger component p; Holm over (DES, PAIR) at alpha 0.05.  DES tests designed
A_SB < 0 and A_SN < 0; PAIR tests P = A_SB^co - A_SB^des > 0 and P_N = A_SN^co - A_SN^des > 0.
Two seed sets are scored, because the registration gives two:
  PER-FAUNA  (A1.2's prose, #338's hrep_readout.py): DES on seeds with the designed fauna read, PAIR on seeds with both;
  COMMON     (readout.py's registered confirmatory(), f53b1e8/6828154): both on the seeds with all four contrasts.
Also three band conventions for the component p when Yuen is in (0.04, 0.05] (the registration says only "counts only
if"): max(Yuen, Wilcoxon) (readout.py's scored_p), Yuen if Wilcoxon passes else 1, Wilcoxon's own p.
"""
import math
import os
import sys

HREP = sys.argv[1] if len(sys.argv) > 1 else os.path.join("runs", "RBT-107", "hrep")
SEEDS = range(11, 31)
ARMS = ("base", "shift", "cull20")
CO, DE = "holistic", "conventional"
READ = 470


# ------------------------------------------------------------------ distributions, from scratch
def t_pdf(x, df):
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    return c * (1 + x * x / df) ** (-(df + 1) / 2)


def _simpson(f, a, b, fa, fm, fb, whole, eps, depth):
    m = (a + b) / 2
    lm, rm = (a + m) / 2, (m + b) / 2
    flm, frm = f(lm), f(rm)
    left = (m - a) / 6 * (fa + 4 * flm + fm)
    right = (b - m) / 6 * (fm + 4 * frm + fb)
    if depth <= 0 or abs(left + right - whole) <= 15 * eps:
        return left + right + (left + right - whole) / 15
    return (_simpson(f, a, m, fa, flm, fm, left, eps / 2, depth - 1) +
            _simpson(f, m, b, fm, frm, fb, right, eps / 2, depth - 1))


def t_sf(t, df):
    """P(T >= t) = 1/2 - integral_0^t pdf (t >= 0), by adaptive Simpson; symmetric for t < 0."""
    if t < 0:
        return 1 - t_sf(-t, df)
    f = lambda x: t_pdf(x, df)
    fa, fb, fm = f(0.0), f(t), f(t / 2)
    return 0.5 - _simpson(f, 0.0, t, fa, fm, fb, t / 6 * (fa + 4 * fm + fb), 1e-13, 60)


def yuen_greater(x, g=0.2):
    n = len(x)
    k = int(math.floor(g * n))
    s = sorted(x)
    tm = sum(s[k:n - k]) / (n - 2 * k)
    w = [min(max(v, s[k]), s[n - k - 1]) for v in s]
    wm = sum(w) / n
    sw2 = sum((v - wm) ** 2 for v in w) / (n - 1)
    h = n - 2 * k
    se = math.sqrt(sw2) * math.sqrt(n) / h  # = s_w / ((h/n) sqrt n): the registered stats107.yuen's code (yuen_se.py has the others)
    t = tm / se
    return tm, t, h - 1, t_sf(t, h - 1)


def t_greater(x):
    n = len(x)
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
    return m, sd, t_sf(m / (sd / math.sqrt(n)), n - 1)


def t_ci(x):
    n = len(x)
    m, sd, _ = t_greater(x)
    lo, hi = 0.0, 50.0  # t_{0.975, n-1} by bisection on our own sf
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_sf(mid, n - 1) > 0.025 else (lo, mid)
    q = (lo + hi) / 2
    return m, m - q * sd / math.sqrt(n), m + q * sd / math.sqrt(n)


def wilcoxon_greater(x):
    v = [a for a in x if a != 0]
    idx = sorted(range(len(v)), key=lambda i: abs(v[i]))
    r2 = [0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and abs(v[idx[j + 1]]) == abs(v[idx[i]]):
            j += 1
        for q in range(i, j + 1):
            r2[idx[q]] = i + j + 2  # doubled midrank
        i = j + 1
    wp2 = sum(r for r, a in zip(r2, v) if a > 0)
    counts = {0: 1}
    for r in r2:
        nxt = dict(counts)
        for s, c in counts.items():
            nxt[s + r] = nxt.get(s + r, 0) + c
        counts = nxt
    tot = 2 ** len(v)
    return wp2 / 2, sum(c for s, c in counts.items() if s >= wp2) / tot


def holm(ps, alpha=0.05):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    rej = [False] * len(ps)
    for rank, i in enumerate(order):
        if ps[i] <= alpha / (len(ps) - rank):
            rej[i] = True
        else:
            break
    return rej


# ------------------------------------------------------------------ data, from the committed files
def garden(arm, seed, kind):
    p = os.path.join(HREP, "garden", f"fresh-{arm}-{seed}-{kind}-d110.txt")
    rows = {}
    for line in open(p):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        assert f[0] == f"fresh-{arm}-{seed}-{kind}-d110" and int(f[1]) == seed and f[2] == kind and int(f[3]) == READ
        rows[f[4]] = (float(f[5]), float(f[6]))
    return rows


def G(rows):
    if not rows:
        return None
    return (sum(v[0] for v in rows.values()) / len(rows), sum(v[1] for v in rows.values()) / len(rows))


def contrasts(seed, kind):
    g = {a: G(garden(a, seed, kind)) for a in ARMS}
    if any(v is None for v in g.values()):
        return None
    (Sf, Sr), (Bf, Br), (Nf, Nr) = g["shift"], g["base"], g["cull20"]
    return dict(SB=Sf - Bf, SN=Sf - Nf, NB=Nf - Bf, I=(Sf - Sr) - (Bf - Br), IN=(Nf - Nr) - (Bf - Br),
                RSB=Sr - Br, RSN=Sr - Nr)


# ------------------------------------------------------------------ scoring
def component(x, direction, band):
    y = [direction * v for v in x]
    tm, t, df, py = yuen_greater(y)
    _, _, pt = t_greater(y)
    _, pw = wilcoxon_greater(y)
    if 0.04 < py <= 0.05:
        p = {"max": max(py, pw), "yuen-or-1": (py if pw <= 0.05 else 1.0), "wilcoxon": pw}[band]
    else:
        p = py
    return p, direction * tm, py, pt, pw


def fmt_ci(x):
    m, lo, hi = t_ci(x)
    return f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}] {sum(v > 0 for v in x)}/{len(x)} positive"


def interval_side(x):
    _, lo, hi = t_ci(x)
    return "above" if lo > 0 else "below" if hi < 0 else "contains 0"


def spec(ii, iin, direction):
    a = interval_side([direction * v for v in ii])
    b = interval_side([direction * v for v in iin])
    return "SPECIFIC" if a == "above" and b == "above" else "OPPOSITE" if a == "below" else "GENERAL"


def score(label, sd, sp, C, band, verbose):
    dsb = [C[s][DE]["SB"] for s in sd]
    dsn = [C[s][DE]["SN"] for s in sd]
    pb = [C[s][CO]["SB"] - C[s][DE]["SB"] for s in sp]
    pn = [C[s][CO]["SN"] - C[s][DE]["SN"] for s in sp]
    out = []
    ps = []
    for name, comps, direction in (("H-REP-DES", (("A_SB", dsb), ("A_SN", dsn)), -1),
                                   ("H-REP-PAIR", (("P", pb), ("P_N", pn)), +1)):
        cp = []
        for cname, x in comps:
            p, tm, py, pt, pw = component(x, direction, band)
            cp.append(p)
            out.append(f"    {name} {cname} ({'<' if direction < 0 else '>'} 0) n={len(x)} trimmed mean {tm:+.4f}: "
                       f"Yuen p {py:.4f}, t p {pt:.4f}, Wilcoxon p {pw:.4f} -> component p {p:.4f}")
        ps.append(max(cp))
    rej = holm(ps)
    head = (f"  [{label}; band = {band}] DES n={len(sd)} IUT p {ps[0]:.4f} -> {'SUPPORTED' if rej[0] else 'NOT SUPPORTED'}; "
            f"PAIR n={len(sp)} IUT p {ps[1]:.4f} -> {'SUPPORTED' if rej[1] else 'NOT SUPPORTED'} "
            f"(Holm: min p {min(ps):.4f} vs 0.025)")
    print(head)
    if verbose:
        print("\n".join(out))
    return ps, rej


def main():
    C = {s: {k: contrasts(s, k) for k in (CO, DE)} for s in SEEDS}
    unread = {k: [s for s in SEEDS if C[s][k] is None] for k in (CO, DE)}
    print(f"UNREAD (no garden population in some arm): co-evolved {unread[CO]}, designed {unread[DE]}")
    for s in unread[CO] + unread[DE]:
        for k in (CO, DE):
            print(f"  seed {s} {k}: garden n by arm " + ", ".join(f"{a} {len(garden(a, s, k))}" for a in ARMS))
    per_fauna_des = [s for s in SEEDS if C[s][DE]]
    both = [s for s in SEEDS if C[s][DE] and C[s][CO]]
    print("\n== The contrasts (t intervals)")
    print(f"  designed A_SB n=20 {fmt_ci([C[s][DE]['SB'] for s in per_fauna_des])}")
    print(f"  designed A_SN n=20 {fmt_ci([C[s][DE]['SN'] for s in per_fauna_des])}")
    print(f"  paired P    n={len(both)} {fmt_ci([C[s][CO]['SB'] - C[s][DE]['SB'] for s in both])}")
    print(f"  paired P_N  n={len(both)} {fmt_ci([C[s][CO]['SN'] - C[s][DE]['SN'] for s in both])}")
    print("\n== Scored lines, both registered seed sets, three band conventions")
    res = {}
    for label, sd, sp in (("PER-FAUNA (#338)", per_fauna_des, both), ("COMMON (registered readout.py)", both, both)):
        for band in ("max", "yuen-or-1", "wilcoxon"):
            res[(label, band)] = score(label, sd, sp, C, band, verbose=(band == "max"))
    print("\n== A2.9 specialisation beside each line (t intervals; direction-aware; a label, not a test)")
    for label, sd, sp in (("PER-FAUNA", per_fauna_des, both), ("COMMON", both, both)):
        ii = [C[s][DE]["I"] for s in sd]
        iin = [C[s][DE]["I"] - C[s][DE]["IN"] for s in sd]
        print(f"  {label} DES:  I {fmt_ci(ii)}; I - I_N {fmt_ci(iin)}; {spec(ii, iin, -1)}")
        pi = [C[s][CO]["I"] - C[s][DE]["I"] for s in sp]
        pin = [(C[s][CO]["I"] - C[s][DE]["I"]) - (C[s][CO]["IN"] - C[s][DE]["IN"]) for s in sp]
        print(f"  {label} PAIR: I {fmt_ci(pi)}; I - I_N {fmt_ci(pin)}; {spec(pi, pin, +1)}")
    print("\n== Printed, not scored (post hoc A2.9 point 3), for the record")
    for label, sd in (("PER-FAUNA", per_fauna_des), ("COMMON", both)):
        print(f"  {label} designed RESPONSE_random {fmt_ci([C[s][DE]['RSB'] for s in sd])}; "
              f"net of the null {fmt_ci([C[s][DE]['RSN'] for s in sd])}")
    print("\n== Sensitivity, not registered: seed 29's co-evolved fauna coded as earning 0 in every arm (contrasts 0)")
    ext = {s: dict(SB=0.0, SN=0.0) for s in unread[CO]}
    pb = [((C[s][CO] or ext[s])["SB"]) - C[s][DE]["SB"] for s in SEEDS]
    pn = [((C[s][CO] or ext[s])["SN"]) - C[s][DE]["SN"] for s in SEEDS]
    p1 = component(pb, +1, "max")[0]
    p2 = component(pn, +1, "max")[0]
    print(f"  PAIR n=20: P {fmt_ci(pb)} p {p1:.4f}; P_N {fmt_ci(pn)} p {p2:.4f}; IUT p {max(p1, p2):.4f}")
    print("\n== Self-checks of the from-scratch distributions")
    print(f"  t_sf(2.093024, 19) = {t_sf(2.093024, 19):.6f} (0.025 textbook); t_sf(1.729133, 19) = {t_sf(1.729133, 19):.6f} (0.05)")
    print(f"  Wilcoxon n=10 all positive: p = {wilcoxon_greater(list(range(1, 11)))[1]:.6f} (1/1024 = {1/1024:.6f})")
    import itertools
    x = [0.5, -1.0, 1.0, 2.0, -2.5, 3.0, 3.0, -4.0, 5.0, 6.0, -0.5, 7.0]  # ties and a sign-split tie
    ab = sorted(abs(v) for v in x)
    rk = {a: (ab.index(a) + 1 + len(ab) - ab[::-1].index(a)) / 2 for a in set(ab)}  # midrank, 1-based
    wp = sum(rk[abs(v)] for v in x if v > 0)
    brute = sum(sum(rk[abs(v)] for v, sg in zip(x, sgn) if sg) >= wp - 1e-9
                for sgn in itertools.product((0, 1), repeat=len(x))) / 2 ** len(x)
    print(f"  Wilcoxon with ties, n=12: DP p {wilcoxon_greater(x)[1]:.6f}; brute force over 4096 sign vectors {brute:.6f}")


if __name__ == "__main__":
    main()
