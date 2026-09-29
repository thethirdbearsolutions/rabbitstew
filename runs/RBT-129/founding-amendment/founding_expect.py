"""RBT-129 founding amendment: expected valid seeds per Stage-1 point at n = 8, P(PARTIAL), income power and
Stage-1 cost, per founding option.  DATA-INFORMED: reads the committed Stage-0 census / Stage-P outputs only
(stageP0-readout/founders.txt, stageP0-readout-adversary/founders.txt); runs no simulator.  Pure stdlib.

Model (stated in AMENDMENT-FOUNDING.md section 3):
  * a seed is valid at the merge at a point when both faunas are alive at season 59 there (DESIGN 6.1);
  * designed at seeds 129001-129003: known from the census (the holistic salt does not move the designed stream);
    at 129004 known at the pilot's Stage-1 points; elsewhere Bernoulli(pD), pD = the point's census rate (k of 3);
  * holistic at 129001: known (salt 0).  A draw that founds at the anchor W118-b is alive at 59 at a Stage-1 point
    with pH = that point's record over the founded draws seen there (129001 census; 129004 at the pilot points).
    The 'shrunk' row uses the Jeffreys mean (k + 0.5) / (m + 1) for BOTH p_H and p_D (adversary #494 SHOULD 8).
    On class A the plug-in p_H is 1 BY CONSTRUCTION (class A is defined by 129001's record, which is also p_H's
    source): the plug-in row assumes perfect transfer and is the top of a range, not an estimate (MUST 2);
  * income validity needs survival to 239; the census stops at 59, so every power here is an UPPER BOUND.  The
    family-pooled and count-threshold (T = 10, 30) models are in founding-amendment-adversary/rederive.txt;
  * holistic draws 129002, 3, 7, 8 are extinct everywhere unless redrawn (known: dead by season 14 at W118-b, and
    129002-3 at all 150 census points);
  * H and D independent within a seed before the merge (separate ecologies and streams; the shared terrain stream
    is ignored);
  * EXCLUDED needs extinction by 299; extinction by 59 is used, so P(EXCLUDED) here is a lower bound.
"""
import math, os, re
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
FOUNDERS = os.path.join(HERE, "..", "stageP0-readout", "founders.txt")

# ---- exact noncentral t: P(|T| > c) = E_Z[P(chi2_df < df (Z + delta)^2 / c^2)] ----------------------------------
# (the chi-square-grid quadrature used before, inherited from power_eff.py, is wrong at df = 1: n = 2 gave 0.148 / 0.185
#  against the correct 0.108 / 0.129; adversary #494 SHOULD 7)
def Phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def _gser(a, x):
    s = t = 1.0 / a; ap = a
    for _ in range(1000):
        ap += 1; t *= x / ap; s += t
        if abs(t) < abs(s) * 1e-15: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
def _gcf(a, x):
    b = x + 1 - a; c = 1e300; d = 1 / b; h = d
    for i in range(1, 1000):
        an = -i * (i - a); b += 2; d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c; d = 1 / d; e = d * c; h *= e
        if abs(e - 1) < 1e-15: break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
def chi2_cdf(x, k):
    if x <= 0: return 0.0
    a = k / 2; x = x / 2
    return _gser(a, x) if x < a + 1 else 1 - _gcf(a, x)
def _EZ(f, m=2400, lo=-12.0, hi=12.0):
    h = (hi - lo) / m; tot = 0.0
    for i in range(m + 1):
        z = lo + i * h; w = 1 if i in (0, m) else (4 if i % 2 else 2)
        tot += w * f(z) * math.exp(-z * z / 2)
    return tot * h / 3 / math.sqrt(2 * math.pi)
def p_abs_t(c, df, delta): return _EZ(lambda z: chi2_cdf(df * (z + delta) ** 2 / c ** 2, df))
_TC = {}
def tcrit(a2, df):
    if (a2, df) in _TC: return _TC[a2, df]
    lo, hi = 0.0, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if p_abs_t(mid, df, 0.0) > a2: lo = mid
        else: hi = mid
    _TC[a2, df] = (lo + hi) / 2; return _TC[a2, df]
_PW = {}
def power(effect, sd, n, alpha=0.05):
    if n < 2: return 0.0
    k = (effect, sd, n)
    if k not in _PW: _PW[k] = p_abs_t(tcrit(alpha, n - 1), n - 1, effect / (sd / math.sqrt(n)))
    return _PW[k]

# ---- data ----------------------------------------------------------------------------------------------------
pts = {}
for line in open(FOUNDERS):
    m = re.match(r"\s+(c\d-p\d{3}-\w+-[LG])\s+129001: H\s*(\d+) D\s*(\d+) \| 129002: H\s*(\d+) D\s*(\d+) \| 129003: H\s*(\d+) D\s*(\d+)", line)
    if m:
        v = [int(x) for x in m.groups()[1:]]
        pts[m.group(1)] = {"H": [v[0] > 0, v[2] > 0, v[4] > 0], "D": [v[1] > 0, v[3] > 0, v[5] > 0]}
assert len(pts) == 36, len(pts)
# pilot seed 129004 at the pilot's Stage-1 points (stageP0_readout.txt, READOUT-STAGEP0 section 8): alive at 59?
# c1-p030-PW-G corrected (adversary #494 MUST 1): holistic last alive 16, designed last alive 93
PILOT4 = {"c1-p030-U-L": (True, True), "c1-p030-PW-G": (False, True), "c2-p030-PW-G": (False, False)}

def rates(p, shrunk):
    kH, mH = int(p["H"][0]), 1
    kD, mD = sum(p["D"]), 3
    if p["id"] in PILOT4:
        h4, d4 = PILOT4[p["id"]]; kH += h4; mH += 1; kD += d4; mD += 1
    pH = (kH + 0.5) / (mH + 1) if shrunk else kH / mH
    pD = (kD + 0.5) / (mD + 1) if shrunk else kD / mD
    return pH, pD

def seed_probs(p, option, shrunk):
    """P(valid at the merge) for seeds 1..8 at point p under an option."""
    pH, pD = rates(p, shrunk)
    D = [float(p["D"][0]), float(p["D"][1]), float(p["D"][2])] + [pD] * 5
    if p["id"] in PILOT4: D[3] = float(PILOT4[p["id"]][1])
    H1 = float(p["H"][0])
    H4 = float(PILOT4[p["id"]][0]) if p["id"] in PILOT4 else pH
    if option == "registered":   # draws 2, 3, 7, 8 dead; 1 known; 4 known at pilot points; 5, 6 founded at W118-b
        H = [H1, 0, 0, H4, pH, pH, 0, 0]
    elif option == "a":          # per-seed screen at W118-b: every seed's holistic draw founds there
        H = [H1, pH, pH, H4, pH, pH, pH, pH]
    elif option == "d":          # failing draws replaced by new seed numbers that found at W118-b: designed re-drawn too
        H = [H1, pH, pH, H4, pH, pH, pH, pH]
        D = [D[0], pD, pD, D[3], pD, pD, pD, pD]
    elif option == "c":          # per-point screen, <= 20 redraws at the point itself
        q = pH if pH > 0 else 0.05  # a point where no founded draw lived: assume a 5% per-draw chance (stated)
        H = [1 - (1 - q) ** 21] * 8
    return [h * d for h, d in zip(H, D)]

def dist(ps):
    d = {0: 1.0}
    for q in ps:
        nd = {}
        for k, v in d.items():
            nd[k + 1] = nd.get(k + 1, 0) + v * q
            nd[k] = nd.get(k, 0) + v * (1 - q)
        d = nd
    return d

SDS = (0.334, 0.275)
def summarise(option, shrunk):
    rows = []
    for pid, p in pts.items():
        p["id"] = pid
        d = dist(seed_probs(p, option, shrunk))
        ev = sum(k * v for k, v in d.items())
        partial = sum(v for k, v in d.items() if k < 6)
        excl = sum(v for k, v in d.items() if 8 - k >= 5)  # lower bound (by 59): >= 5 of 8 invalid
        pw = [sum(v * power(0.4, sd, k) for k, v in d.items()) for sd in SDS]
        rows.append((pid, ev, partial, excl, pw))
    return rows

def cls(pid):
    p = pts[pid]; return "A" if p["H"][0] and p["D"][0] else "B"

print(__doc__)
print("## Income power at |H - D| = 0.4, BH half, exact noncentral t, by valid n (SD 0.334 / 0.275)")
print("  " + "  ".join(f"n{n} {power(0.4, 0.334, n):.3f}/{power(0.4, 0.275, n):.3f}" for n in range(2, 9)))
OPTS = (("registered", "registered (no amendment)"), ("a", "(a) per-seed screen at W118-b"),
        ("d", "(d) replace failing draws by new seed numbers"), ("c", "(c) per-point screen"))
for shrunk in (False, True):
    print(f"\n## {'PESSIMISTIC: transfer rate p_H AND designed rate p_D shrunk (Jeffreys)' if shrunk else 'PLUG-IN rates (class A: p_H = 1 by construction; the top of the range)'}")
    for key, label in OPTS:
        rows = summarise(key, shrunk)
        print(f"\n### {label}")
        for c in ("A", "B"):
            sub = [r for r in rows if cls(r[0]) == c]
            n = len(sub)
            print(f"  class {c} ({n} points; A = 129001 has both faunas at 59): mean E[valid] {sum(r[1] for r in sub)/n:.2f};"
                  f" expected points not PARTIAL {max(0.0, sum(1 - r[2] for r in sub)):.1f} of {n};"
                  f" expected EXCLUDED-by-59 (lower bound) {sum(r[3] for r in sub):.1f};"
                  f" mean E[power] {sum(r[4][0] for r in sub)/n:.3f} / {sum(r[4][1] for r in sub)/n:.3f}")
        if not shrunk and key in ("registered", "a"):
            print("  per point: E[valid]  P(PARTIAL)  E[power] sd .334 / .275")
            for pid, ev, pa, ex, pw in rows:
                print(f"    {pid:14s} {cls(pid)}  {ev:4.2f}  {pa:4.2f}  {pw[0]:.3f} / {pw[1]:.3f}")

# ---- screen: redraws needed -----------------------------------------------------------------------------------
print("\n## Screen: P(a seed hits the redraw cap R) = (1 - q)^R, q = per-draw founding rate at W118-b (4 of 8 known)")
for q in (0.16, 0.25, 0.5, 0.84):
    print(f"  q {q:.2f}: " + "  ".join(f"R{R} {(1 - q) ** R:.4f}" for R in (8, 12, 16, 20))
          + f"   E[redraws | not capped at 20] {(1 - q) / q:.2f}")
# P(>= 3 of the 4 known failing seeds + 8 R-B seeds hit the cap), the programme stop, at q
for q in (0.16, 0.25, 0.5):
    pc = (1 - q) ** 20
    # seeds screened: 2, 3, 7, 8 (known failing at salt 0) and 9-16 (unknown: fail at salt 0 w.p. 1 - q, then need the cap)
    probs = [pc] * 4 + [(1 - q) * pc] * 8
    dd = dist(probs)
    d8 = dist([pc] * 4)  # seeds 1-8: only 2, 3, 7, 8 can be capped (1, 4, 5, 6 pass at salt 0)
    print(f"  q {q:.2f}: P(>= 3 of 16 capped) {sum(v for k, v in dd.items() if k >= 3):.5f};"
          f" P(>= 2 of seeds 1-8 capped) {sum(v for k, v in d8.items() if k >= 2):.5f}; P(stop) <= the sum")

# ---- cost ----------------------------------------------------------------------------------------------------
print("\n## Cost (core-h), at the pilot's 23.35 / 43.72 core-s per two-fauna arm-season; single-fauna 13.6 / 23.35")
for cs, cs1 in ((23.35, 13.6), (43.72, 23.35)):
    h = lambda s, c=cs: s * c / 3600
    # screen: holistic-only S 0-59 at W118-b.  Seeds needing it: 2, 3, 7, 8 and 9-16 (holistic), 9-16 (designed).
    fail = 15 * cs1 / 3600; ok = 60 * cs1 / 3600
    for q in (0.5, 0.16):
        ef = (1 - q) / q
        exp_scr = 12 * (ef * fail + ok) + 8 * ok        # 12 holistic screens (4 known failing + 8 new), 8 designed checks
        if_die15 = 12 * (20 * fail + ok) + 8 * (20 * fail + ok)
        true_worst = (12 * 21 + 8 * 21 - 4) * ok  # every attempt alive to 59, every screened seed to the cap
        print(f"  {cs} core-s, q {q}: screen expected {exp_scr:.1f}; <= {if_die15:.1f} IF failed attempts die by season 15;"
              f" true bound (every attempt to 59, every seed capped) {true_worst:.1f}")
    rerun = (4 * 60 + 4 * 15 + 8 * 60) * cs1 / 3600
    fork8, fork16 = 8 * h(60), 16 * h(60)
    print(f"  {cs} core-s: REQUIRED salt-0 single-fauna re-run, seeds 1-8 {rerun:.1f};"
          f" two-fauna fork source S 0-59 at W118-b, 8 / 16 seeds {fork8:.1f} / {fork16:.1f}")
    for probes in (0.46, 0.83):
        S = 36 * 8 * (h(300) + probes)
        M = 12 * 8 * h(240); N = 4 * 8 * 0.57 * cs / 20; plants = 36 * 0.8
        credit_reg = 36 * 3 * h(60); credit_a = 36 * 1 * h(60)
        g = S + M + N + plants
        print(f"  {cs} core-s, probes {probes}: Stage 1 gated (36 x 8, M <= 12, N <= 4) {g:.0f};"
              f" minus resume credit: registered (129001-3) {g - credit_reg:.0f}, amended (129001 only) {g - credit_a:.0f}"
              f" (+{credit_reg - credit_a:.0f}); of which M + N re-admitted by T5 {M + N:.0f}")
    Sonly = 36 * 8 * h(300)
    print(f"  {cs} core-s: S arms only {Sonly:.0f}; ungated power.py-style Stage 1 (S + M + half N + probes)"
          f" {36 * (8 * (h(300) + h(240) + 0.5 * h(240) * 0.85 + 0.46) + 0.8):.0f}-{36 * (8 * (h(300) + h(240) + 0.5 * h(240) * 0.85 + 0.83) + 0.8):.0f}")
