"""RBT-129 amendment F (PR #493) adversary: independent re-derivation of the amendment's validity, power, screen and
Stage-1 cost numbers, plus the corrections and sensitivities in ADVERSARY.md.  Pure stdlib; reads committed text only
(stageP0-readout/founders.txt, stageP0-readout-adversary/founders.txt, stageP0-readout/stageP0_readout.txt); runs no
simulator.  About 3 s.

Differences from founding_expect.py, on purpose:
  * power: two-sided P(|T| > c) = E_Z[ F_chi2_df( df (Z + delta)^2 / c^2 ) ], Simpson over Z, regularised incomplete
    gamma for F (founding_expect.py integrates over the chi-square and keeps the upper tail only);
  * the pilot's seed-129004 outcomes are parsed from the committed files, not typed in;
  * alive-at-59 can be read at a count threshold T (T = 1 is the registered rule; T = 10 / 30 are proxies for
    'survives to 239', which the income test needs, DESIGN 6.1);
  * the transfer rate p_H can be estimated per point (the amendment's) or pooled by food layout.
"""
import math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..")

# ---------------- exact noncentral t, independent route ----------------
def _gser(a, x):
    s = term = 1.0 / a; n = a
    for _ in range(10000):
        n += 1; term *= x / n; s += term
        if abs(term) < abs(s) * 1e-15: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
def _gcf(a, x):  # upper, Lentz
    tiny = 1e-300; b = x + 1 - a; c = 1 / tiny; d = 1 / b; h = d
    for i in range(1, 10000):
        an = -i * (i - a); b += 2
        d = an * d + b; d = tiny if abs(d) < tiny else d
        c = b + an / c; c = tiny if abs(c) < tiny else c
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-15: break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
def chi2_cdf(x, k):
    if x <= 0: return 0.0
    a, y = k / 2, x / 2
    return _gser(a, y) if y < a + 1 else 1 - _gcf(a, y)
def _E_Z(f, lo=-12.0, hi=12.0, m=3000):
    h = (hi - lo) / m; s = f(lo) + f(hi)
    for i in range(1, m):
        s += (4 if i % 2 else 2) * f(lo + i * h)
    return s * h / 3
phi = lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
def p_abs_t_exceeds(c, df, delta):
    return _E_Z(lambda z: phi(z) * chi2_cdf(df * (z + delta) ** 2 / c ** 2, df), lo=-delta - 12, hi=-delta + 12)
_C = {}
def crit(alpha, df):
    if (alpha, df) not in _C:
        lo, hi = 0.0, 100.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if p_abs_t_exceeds(mid, df, 0.0) > alpha else (lo, mid)
        _C[alpha, df] = (lo + hi) / 2
    return _C[alpha, df]
_P = {}
def power(n, sd, eff=0.4, alpha=0.05):  # BH half = q/2 = 0.05 two-sided (power.py part 1)
    if n < 2: return 0.0
    if (n, sd) not in _P:
        _P[n, sd] = p_abs_t_exceeds(crit(alpha, n - 1), n - 1, eff / (sd / math.sqrt(n)))
    return _P[n, sd]

# ---------------- data ----------------
PTS = {}
for line in open(os.path.join(R, "stageP0-readout", "founders.txt")):
    m = re.match(r"\s+(c\d-p\d{3}-\w+-[LG])\s+129001: H\s*(\d+) D\s*(\d+) \| 129002: H\s*(\d+) D\s*(\d+) \| 129003: H\s*(\d+) D\s*(\d+)", line)
    if m:
        v = list(map(int, m.groups()[1:]))
        PTS[m.group(1)] = {"H": v[0::2], "D": v[1::2]}
assert len(PTS) == 36
PILOT = {}  # (point, seed) -> (holistic last alive, designed last alive)
for line in open(os.path.join(R, "stageP0-readout-adversary", "founders.txt")):
    m = re.match(r"pilot (\S+) (\d+) holi alive@239\s+\d+ lastlive\s+(\d+) \| conv alive@239\s+\d+ lastlive\s+(\d+)", line)
    if m: PILOT[m.group(1), int(m.group(2))] = (int(m.group(3)), int(m.group(4)))
for line in open(os.path.join(R, "stageP0-readout", "stageP0_readout.txt")):
    m = re.match(r"\s+(c\S+)/(\d+): EXTINCT pre-merge at season (\d+): .*both faunas extinct", line)
    if m: PILOT.setdefault((m.group(1), int(m.group(2))), (int(m.group(3)), int(m.group(3))))
P4 = {p: (PILOT[p, 129004][0] >= 59, PILOT[p, 129004][1] >= 59) for p in PTS if (p, 129004) in PILOT}
P4_AMENDMENT = {"c1-p030-U-L": (True, True), "c1-p030-PW-G": (True, True), "c2-p030-PW-G": (False, False)}
cls = lambda p: "A" if PTS[p]["H"][0] and PTS[p]["D"][0] else "B"
fam = lambda p: "PW" if "-PW-" in p else "UHP"

def model(pid, p4, T=1, ph="point", jeff_h=False, jeff_d=False, option="a"):
    P = PTS[pid]; H = [x >= T for x in P["H"]]; D = [x >= T for x in P["D"]]
    kD, mD = sum(D), 3
    h4 = d4 = None
    if pid in p4:
        h4, d4 = p4[pid]
        kD += d4; mD += 1
    if ph == "point":
        kH, mH = int(H[0]) + (int(h4) if h4 is not None else 0), 1 + (h4 is not None)
    else:  # pooled over every Stage-1 point of the same food family, over the founded draws seen there
        kH = mH = 0
        for q in PTS:
            if fam(q) != fam(pid): continue
            kH += PTS[q]["H"][0] >= T; mH += 1
            if q in p4: kH += p4[q][0]; mH += 1
        kH, mH = kH / mH * 2, 2  # two distinct founded draws carry it (R11): pseudo-counts on m = 2
    pH = (kH + 0.5) / (mH + 1) if jeff_h else kH / mH
    pD = (kD + 0.5) / (mD + 1) if jeff_d else kD / mD
    Dv = [float(D[0]), float(D[1]), float(D[2])] + [pD] * 5
    if d4 is not None: Dv[3] = float(d4)
    H4 = float(h4) if h4 is not None else pH
    Hv = {"registered": [float(H[0]), 0, 0, H4, pH, pH, 0, 0], "a": [float(H[0]), pH, pH, H4, pH, pH, pH, pH]}[option]
    return [h * d for h, d in zip(Hv, Dv)]

def dist(ps):
    d = [1.0]
    for q in ps:
        d = [(d[k] if k < len(d) else 0) * (1 - q) + (d[k - 1] * q if k else 0) for k in range(len(d) + 1)]
    return d

def summary(**kw):
    out = {}
    for c in "AB":
        pts = [p for p in PTS if cls(p) == c]
        ev = notp = pw1 = pw2 = 0.0
        for p in pts:
            d = dist(model(p, **kw))
            ev += sum(k * v for k, v in enumerate(d)); notp += sum(v for k, v in enumerate(d) if k >= 6)
            pw1 += sum(v * power(k, 0.334) for k, v in enumerate(d)); pw2 += sum(v * power(k, 0.275) for k, v in enumerate(d))
        out[c] = (ev / len(pts), notp, pw1 / len(pts), pw2 / len(pts), len(pts))
    return out

def show(label, **kw):
    s = summary(**kw); a, b = s["A"], s["B"]
    print(f"  {label:66s} A: E[valid] {a[0]:.2f}  not-PARTIAL {a[1]:4.1f}/24  power {a[2]:.3f}/{a[3]:.3f} | B: E[valid] {b[0]:.2f}  not-PARTIAL {b[1]:.1f}/12")

print(__doc__)
print("## 1. Income power, |H - D| = 0.4, alpha 0.05 two-sided, exact noncentral t (independent route)")
print("  n : " + "  ".join(f"{n}: {power(n, 0.334):.3f}/{power(n, 0.275):.3f}" for n in range(2, 9)))

print("\n## 2. Pilot seed 129004, parsed (last season alive, holistic / designed; alive at 59 = last alive >= 59)")
for (p, s), v in sorted(PILOT.items()):
    if s == 129004: print(f"  {p:14s} H last {v[0]:3d}  D last {v[1]:3d}   parsed alive@59 {P4.get(p)}   amendment's PILOT4 {P4_AMENDMENT.get(p)}")

print("\n## 3. Expected validity at n = 8 (valid = both faunas alive at 59 at count >= T), classes as in the amendment")
print("  (A = the 24 points where 129001 has both faunas at 59; B = the other 12)")
show("amendment, plug-in (its PILOT4)", p4=P4_AMENDMENT)
show("amendment, pessimistic (its PILOT4; Jeffreys on p_H only)", p4=P4_AMENDMENT, jeff_h=True)
show("registered (its PILOT4)", p4=P4_AMENDMENT, option="registered")
print("  -- corrected: 129004's holistic fauna is dead by season 16 at c1-p030-PW-G --")
show("corrected, plug-in", p4=P4)
show("corrected, Jeffreys on p_H", p4=P4, jeff_h=True)
show("corrected, Jeffreys on p_H and p_D", p4=P4, jeff_h=True, jeff_d=True)
show("corrected, p_H pooled by food family (U/HP vs PW), plug-in", p4=P4, ph="family")
show("corrected, p_H pooled by family, Jeffreys on p_H and p_D", p4=P4, ph="family", jeff_h=True, jeff_d=True)
print("  -- income validity needs survival to 239; count at 59 as a proxy --")
for T in (10, 30):
    show(f"corrected, T = {T}, plug-in (per point)", p4=P4, T=T)
    show(f"corrected, T = {T}, pooled by family, Jeffreys on both", p4=P4, T=T, ph="family", jeff_h=True, jeff_d=True)

print("\n## 4. Per point, class A, corrected: P(PARTIAL) plug-in | Jeffreys both | family+Jeffreys | T=30 family+Jeffreys")
for p in PTS:
    if cls(p) != "A": continue
    row = []
    for kw in (dict(p4=P4), dict(p4=P4, jeff_h=True, jeff_d=True), dict(p4=P4, ph="family", jeff_h=True, jeff_d=True),
               dict(p4=P4, T=30, ph="family", jeff_h=True, jeff_d=True)):
        d = dist(model(p, **kw)); row.append(sum(v for k, v in enumerate(d) if k < 6))
    P = PTS[p]
    print(f"  {p:14s} 129001 H{P['H'][0]:3d} D{P['D'][0]:3d}; D on 2,3: {P['D'][1]:2d},{P['D'][2]:2d}   " + "  ".join(f"{x:.2f}" for x in row))

print("\n## 5. Screen: cap and stop")
for q in (0.157, 0.25, 0.5):
    pc_known, pc_new = (1 - q) ** 20, (1 - q) ** 21
    d16 = dist([pc_known] * 4 + [pc_new] * 8)
    d8 = dist([pc_known] * 4)
    print(f"  q {q:.3f}: P(capped) known-failing seed {pc_known:.4f}, new seed {pc_new:.4f}; P(>= 3 of 16 capped) {sum(d16[3:]):.5f};"
          f" P(>= 2 of seeds 1-8 capped) {sum(d8[2:]):.5f}")
lo = hi = None  # Clopper-Pearson 4/8 by bisection on the binomial
def binom_cdf(k, n, p): return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
a, b = 0.0, 1.0
for _ in range(60):
    m = (a + b) / 2; a, b = (m, b) if 1 - binom_cdf(3, 8, m) < 0.025 else (a, m)
lo = a; a, b = 0.0, 1.0
for _ in range(60):
    m = (a + b) / 2; a, b = (m, b) if binom_cdf(4, 8, m) > 0.025 else (a, m)
print(f"  Clopper-Pearson 95% for 4 of 8: {lo:.3f}-{a:.3f}")

print("\n## 6. Screen cost (core-h); single-fauna core-s 13.6 (W118-b, 129003 S, holistic dead: cost.txt) or 23.35")
for cs1 in (13.6, 23.35):
    h = lambda seasons: seasons * cs1 / 3600
    for q in (0.5, 0.157):
        ef = (1 - q) / q
        e = 4 * (ef * h(15) + h(60)) + 8 * (ef * h(15) + h(60)) + 8 * h(60)
        print(f"  {cs1} core-s, q {q}: expected {e:.1f} (failed attempts die by 15)")
    n_att = 4 * 20 + 8 * 21 + 8 * 21
    print(f"  {cs1} core-s: amendment's 'worst' 20 x (20 x 15 + 60) seasons = {20 * (20 * h(15) + h(60)):.1f};"
          f" true worst ({n_att} capped attempts, each alive to 59) {n_att * h(60):.1f};"
          f" every seed capped but deaths by 15: {n_att * h(15):.1f}")
    print(f"  {cs1} core-s: salt-0 re-run of seeds 1-8 alone (4 H to 59, 4 H to 15, 8 D to 59) {(4*60 + 4*15 + 8*60) * cs1 / 3600:.1f}")
print("  two-fauna S 0-59 at W118-b at (s_j, t_j) as the anchor-fallback fork source (F5/T7), 8 / 16 seeds:"
      f" {8 * 60 * 23.35 / 3600:.1f} / {16 * 60 * 23.35 / 3600:.1f} (23.35) ; {8 * 60 * 43.72 / 3600:.1f} / {16 * 60 * 43.72 / 3600:.1f} (43.72)")

print("\n## 7. Stage 1 at n = 8, gated (DESIGN 11.2 formula: S 300 + probes; M 240 at <= 12 pts; N 0.57 at 20 core-s at <= 4 pts; plants 0.8/pt)")
for cs in (23.35, 43.72):
    h = lambda seasons: seasons * cs / 3600
    for pr in (0.46, 0.83):
        S = 36 * 8 * (h(300) + pr); M = 12 * 8 * h(240); N = 4 * 8 * 0.57 * cs / 20; pl = 36 * 0.8
        g = S + M + N + pl
        cr3, cr1 = 36 * 3 * h(60), 36 * 1 * h(60)
        print(f"  {cs} core-s probes {pr}: S {S:.0f} M {M:.0f} N {N:.0f} plants {pl:.0f} -> {g:.0f}; registered credit -{cr3:.0f} -> {g - cr3:.0f};"
              f" amended -{cr1:.0f} -> {g - cr1:.0f}; M+N that T5 re-admits {M + N:.0f}")
    # what the credit really is at 129001: no S arm to resume where 129001 is extinct pre-merge in both faunas
    dead = [p for p in PTS if PTS[p]["H"][0] == 0 and PTS[p]["D"][0] == 0]
    print(f"  {cs} core-s: 129001 has both faunas dead by 59 at {len(dead)} points ({', '.join(dead)}): no S 60-299 there at all")
