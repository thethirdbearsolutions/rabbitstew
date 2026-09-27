"""RBT-108 readout adversary: an independent re-derivation of the readout and the post hoc offset tests.

Pure Python (no numpy, no scipy), written without reference to runs/RBT-108/readout.py: its own parser of
runs/RBT-96/{s0,s1}-SEED/generations.txt, its own incomplete-beta / incomplete-gamma quantiles (checked against
tabled values below), exact sign-flip and signed-rank enumerations, and a seeded bootstrap.

    python runs/RBT-108/readout-adversary/rederive.py > runs/RBT-108/readout-adversary/rederive.txt
"""
import itertools
import math
import os
import random
import statistics as st

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-96")
OLD = list(range(201, 205))
NEW = list(range(205, 217))
ALL = OLD + NEW
G = 250


# ----------------------------------------------------------------------------- distributions
def betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return h


def ibeta(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * betacf(a, b, x) / a
    return 1 - math.exp(lb) * betacf(b, a, 1 - x) / b


def gammainc(a, x):
    """Regularized lower incomplete gamma P(a, x)."""
    if x <= 0:
        return 0.0
    if x < a + 1:
        s = term = 1 / a
        n = a
        for _ in range(1000):
            n += 1
            term *= x / n
            s += term
            if abs(term) < abs(s) * 1e-16:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c, d = x + 1 - a, 1e300, 1 / (x + 1 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = b + an / c if abs(b + an / c) > 1e-300 else 1e-300
        h *= d * c
        if abs(d * c - 1) < 1e-16:
            break
    return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def bisect(f, target, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * ibeta(df / 2, 0.5, x)
    return 1 - p if t > 0 else p


def t_q(p, df):
    return bisect(lambda t: t_cdf(t, df), p, -100, 100)


def chi2_q(p, df):
    return bisect(lambda x: gammainc(df / 2, x / 2), p, 0, 500)


def beta_q(p, a, b):
    return bisect(lambda x: ibeta(a, b, x), p, 0, 1)


def binom_two_sided(k, n):
    """Exact two-sided sign test at p = 1/2 (double the smaller tail, capped at 1)."""
    lo = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(lo + 1)) / 2 ** n)


for got, want, what in [(t_q(0.975, 4), 2.7764, "t(4)"), (t_q(0.975, 11), 2.2010, "t(11)"), (t_q(0.975, 15), 2.1314, "t(15)"),
                        (t_q(0.975, 7), 2.3646, "t(7)"), (chi2_q(0.025, 12), 4.4038, "chi2 12 lo"), (chi2_q(0.975, 12), 23.3367, "chi2 12 hi"),
                        (chi2_q(0.025, 16), 6.9077, "chi2 16 lo"), (chi2_q(0.975, 16), 28.8454, "chi2 16 hi")]:
    assert abs(got - want) < 1e-3, (what, got, want)


# ----------------------------------------------------------------------------- data
def read(run):
    lines = open(os.path.join(ROOT, run, "generations.txt")).read().splitlines()
    cols = lines[0].split("\t")
    rows = [dict(zip(cols, l.split("\t"))) for l in lines[1:]]
    return rows


def champs(run):
    return [(int(r["generation"]), float(r["champ_holistic_mean"])) for r in read(run) if r.get("champ_holistic_mean")]


def fifth(run, i):
    return st.mean(v for g, v in champs(run) if i * G / 5 <= g < (i + 1) * G / 5)


def final_fifth(run):
    return st.mean(v for g, v in champs(run) if g >= 0.8 * G)


def opp(run):
    lines = open(os.path.join(ROOT, run, "opponent.txt")).read().split()
    return dict(zip(lines[:5], map(float, lines[5:10])))


d = {s: final_fifth(f"s1-{s}") - final_fifth(f"s0-{s}") for s in ALL}


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def out(*a):
    print(*a)


out("RBT-108 readout adversary: independent re-derivation (pure Python; own parser, own quantiles)")
out("d = s1 - s0, mean champ_holistic_mean over checkpoints at generation >= 200 (11 per arm), from generations.txt")
out("seed  " + "  ".join(f"{s}:{d[s]:+.4f}" for s in ALL))
out()

# ----------------------------------------------------------------------------- registered items
out("=== registered items ===")
x12 = [d[s] for s in NEW]
r12 = rms(x12)
lo, hi = r12 * math.sqrt(12 / chi2_q(0.975, 12)), r12 * math.sqrt(12 / chi2_q(0.025, 12))
out(f"1. 12 new: RMS {r12:.4f}  chi2(12) 95% CI [{lo:.4f}, {hi:.4f}]  contains 0.128: {lo <= 0.128 <= hi}")
x16 = [d[s] for s in ALL]
r16 = rms(x16)
lo16, hi16 = r16 * math.sqrt(16 / chi2_q(0.975, 16)), r16 * math.sqrt(16 / chi2_q(0.025, 16))
h = t_q(0.975, 4) * r16 / 2
out(f"2. 16 pooled: RMS {r16:.4f}  chi2(16) CI [{lo16:.4f}, {hi16:.4f}]  h = t(4) RMS / 2 = {h:.4f}")


def n_for(r, w=0.10):
    return next(n for n in range(2, 1000) if t_q(0.975, n - 1) * r / math.sqrt(n) <= w)


out(f"   seeds for +-0.10 (smallest n, t(n-1) RMS / sqrt n <= 0.10): {n_for(r16)}  (at CI ends: {n_for(lo16)}, {n_for(hi16)})")
out(f"   [adversary] h with the null's own df, t(16) RMS / 2 = {t_q(0.975, 16) * r16 / 2:.4f}; normal-theory z RMS / 2 = {1.959964 * r16 / 2:.4f}")
k = sum(abs(v) >= 0.20 for v in x12)
cp = (beta_q(0.025, k, 12 - k + 1) if k else 0.0, beta_q(0.975, k + 1, 12 - k))
out(f"3. tail: |d| >= 0.20 in {k}/12 ({[s for s in NEW if abs(d[s]) >= 0.20]})  Clopper-Pearson 95% [{cp[0]:.4f}, {cp[1]:.4f}]")
k16 = sum(abs(v) >= 0.20 for v in x16)
out(f"   pooled {k16}/16  CP [{beta_q(0.025, k16, 16 - k16 + 1):.4f}, {beta_q(0.975, k16 + 1, 16 - k16):.4f}]")
ok = []
for s in ALL:
    a, b = read(f"s0-{s}"), read(f"s1-{s}")
    env = [(r["generation"], r["terrain_seed"], r["start_seed"]) for r in a] == [(r["generation"], r["terrain_seed"], r["start_seed"]) for r in b]
    da = dict(l.split("\t")[:2] for l in open(os.path.join(ROOT, f"s0-{s}", "conventional-digest.txt")).read().splitlines())
    db = dict(l.split("\t")[:2] for l in open(os.path.join(ROOT, f"s1-{s}", "conventional-digest.txt")).read().splitlines())
    conv = [r[k2] for r in a for k2 in ("c_best", "c_mean")] == [r[k2] for r in b for k2 in ("c_best", "c_mean")]
    ok.append((s, env and len(a) == G, da["conventional"] == db["conventional"], da["holistic"] != db["holistic"], conv))
out("4. pairing: seed (env identical over 250 rows, conv digest identical, holistic digest differs, conventional columns identical)")
out("   " + "  ".join(f"{s}:{'PASS' if all(t[1:]) else 'FAIL'}" for s, *t in [(o[0], *o[1:]) for o in ok]))
out(f"   pass {sum(all(o[1:]) for o in ok if o[0] in NEW)}/12 new, {sum(all(o[1:]) for o in ok)}/16")
out("5. re-read (4-seed mean against the pooled null): t = mean / (RMS / 2), df 4")
for name, m in (("RBT-74", 0.0640), ("RBT-85", -0.0485)):
    t = m / (r16 / 2)
    out(f"   {name}  mean {m:+.4f}  t(4) {t:+.2f}  p {2 * (1 - t_cdf(abs(t), 4)):.3f}  clears h {h:.4f}: {abs(m) > h}   "
        f"clears spread-only h {t_q(0.975, 4) * math.sqrt(sum((v - st.mean(x16)) ** 2 for v in x16) / 16) / 2:.4f}: "
        f"{abs(m) > t_q(0.975, 4) * math.sqrt(sum((v - st.mean(x16)) ** 2 for v in x16) / 16) / 2}")
out()

# ----------------------------------------------------------------------------- post hoc: is the mean resolved?
out("=== post hoc offset: exact and resampling tests (d symmetric about 0 is EXACT under a pure A/A: the arms are exchangeable) ===")


def signflip(xs):
    obs = abs(sum(xs))
    n = len(xs)
    hits = sum(1 for signs in itertools.product((1, -1), repeat=n) if abs(sum(s * v for s, v in zip(signs, xs))) >= obs - 1e-12)
    return hits / 2 ** n, hits, 2 ** n


def signed_rank(xs):
    ranks = sorted(range(len(xs)), key=lambda i: abs(xs[i]))
    r = [0] * len(xs)
    for rk, i in enumerate(ranks, 1):
        r[i] = rk
    w = sum(r[i] for i in range(len(xs)) if xs[i] > 0)
    n = len(xs)
    tot = n * (n + 1) // 2
    obs = abs(w - tot / 2)
    hits = sum(1 for signs in itertools.product((0, 1), repeat=n) if abs(sum(rk for rk, sg in zip(range(1, n + 1), signs) if sg) - tot / 2) >= obs - 1e-12)
    return w, hits / 2 ** n


def boot(xs, B=100000, seed=108):
    rng = random.Random(seed)
    n = len(xs)
    ms = sorted(st.mean(rng.choices(xs, k=n)) for _ in range(B))
    pct = (ms[int(0.025 * B)], ms[int(0.975 * B) - 1])
    # BCa
    m0 = st.mean(xs)
    z0 = _ninv(sum(m < m0 for m in ms) / B)
    jack = [st.mean(xs[:i] + xs[i + 1:]) for i in range(n)]
    jm = st.mean(jack)
    num = sum((jm - j) ** 3 for j in jack)
    den = 6 * sum((jm - j) ** 2 for j in jack) ** 1.5
    a = num / den if den else 0.0
    def adj(q):
        z = _ninv(q)
        return _ncdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
    bca = (ms[max(0, int(adj(0.025) * B))], ms[min(B - 1, int(adj(0.975) * B))])
    p_le0 = sum(m <= 0 for m in ms) / B
    return pct, bca, p_le0


def _ncdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _ninv(p):
    return bisect(_ncdf, p, -10, 10)


sets = [("12 new (205-216)", NEW), ("all 16 (201-216)", ALL), ("RBT-96's 4 (201-204)", OLD),
        ("16 without the two tail seeds 201, 212", [s for s in ALL if s not in (201, 212)]),
        ("12 new without 212", [s for s in NEW if s != 212])]
for name, ss in sets:
    xs = [d[s] for s in ss]
    n = len(xs)
    m, sd = st.mean(xs), st.stdev(xs)
    tq = t_q(0.975, n - 1)
    t = m / (sd / math.sqrt(n))
    pf, hits, tot = signflip(xs)
    w, pw = signed_rank(xs)
    pos = sum(v > 0 for v in xs)
    pct, bca, ple0 = boot(xs)
    out(f"{name}  n={n}")
    out(f"  mean {m:+.4f}  t CI [{m - tq * sd / math.sqrt(n):+.4f}, {m + tq * sd / math.sqrt(n):+.4f}]  t p {2 * (1 - t_cdf(abs(t), n - 1)):.4f}")
    out(f"  exact sign-flip (randomization) test on the mean, two-sided: p = {pf:.4f}  ({hits}/{tot} sign patterns at least as extreme)")
    out(f"  exact Wilcoxon signed-rank W+ = {w}, two-sided p = {pw:.4f};  sign test {pos}/{n - pos}: p = {binom_two_sided(pos, n):.4f}")
    out(f"  bootstrap (100000, random.Random(108)) 95% percentile [{pct[0]:+.4f}, {pct[1]:+.4f}]  BCa [{bca[0]:+.4f}, {bca[1]:+.4f}]  share of resampled means <= 0: {ple0:.4f}")
    srt = sorted(xs)
    tm = st.mean(srt[2:-2]) if n >= 8 else float("nan")
    out(f"  median {st.median(xs):+.4f}   20%-trimmed mean {tm:+.4f}")
out()

# ----------------------------------------------------------------------------- when does the offset appear?
out("=== when does the offset appear? per fifth of the run (50 generations, champion checkpoints), s1 - s0 over 16 seeds ===")
out("fifth      mean d    SD      RMS     positive   exact sign-flip p")
for i in range(5):
    xs = [fifth(f"s1-{s}", i) - fifth(f"s0-{s}", i) for s in ALL]
    out(f"g{50 * i:3d}-{50 * i + 49:<3d}  {st.mean(xs):+.4f}  {st.stdev(xs):.4f}  {rms(xs):.4f}  {sum(v > 0 for v in xs):2d}/16      {signflip(xs)[0]:.4f}")
xs = [champs(f"s1-{s}")[0][1] - champs(f"s0-{s}")[0][1] for s in ALL]
out(f"gen 0 only (founders, before any reproduction): mean d {st.mean(xs):+.4f}  SD {st.stdev(xs):.4f}  positive {sum(v > 0 for v in xs)}/16  sign-flip p {signflip(xs)[0]:.4f}")
xs = [float(read(f"s1-{s}")[0]["h_mean"]) - float(read(f"s0-{s}")[0]["h_mean"]) for s in ALL]
out(f"gen 0 population mean fitness (h_mean, self-play): mean d {st.mean(xs):+.4f}  positive {sum(v > 0 for v in xs)}/16  sign-flip p {signflip(xs)[0]:.4f}")
out()

# ----------------------------------------------------------------------------- the solo measures are not independent evidence
out("=== the solo measures as corroboration: are they independent of d? ===")
ap = [opp(f"s1-{s}")["holistic_approach"] - opp(f"s0-{s}")["holistic_approach"] for s in ALL]
te = [opp(f"s1-{s}")["holistic_terrain"] - opp(f"s0-{s}")["holistic_terrain"] for s in ALL]


def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


out(f"corr(d, holistic solo approach d) {corr(x16, ap):+.2f};  corr(d, terrain d) {corr(x16, te):+.2f}  (16 seeds)")
out(f"solo approach d: {sum(v > 0 for v in ap)}/16 positive, exact sign-flip p {signflip(ap)[0]:.4f}; seeds with d > 0 and approach d > 0: "
    f"{sum(a > 0 and b > 0 for a, b in zip(x16, ap))}; with d <= 0 and approach d > 0: {sum(a <= 0 and b > 0 for a, b in zip(x16, ap))}")
out()

# ----------------------------------------------------------------------------- the decisive test: power
out("=== design (c): power by simulation, random.Random(96), 4000 trials per cell; the test is the one-sample t on the per-seed contrast")
out("    at 5% two-sided (a stand-in for the exact sign-flip test, which has the same size under exchangeability) ===")
out("arm value = mu_seed + a_salt + e.  'code' hypothesis: a_0 = -delta, every non-zero salt 0.  'chance': all a = 0.")
out("noise models for e (one run):  N62 normal sd 0.062 (= the spread about the mean, 0.088 / sqrt 2);")
out("  N81 normal sd 0.081 (= RMS 0.115 / sqrt 2, the pure-chance reading);  T normal sd 0.040 plus a +0.25 discovery w.p. 1/16 (2 of 32 runs)")
out("designs:  T2  fresh seeds, arms at salts 0 and 2 (a replication with a different non-zero salt);   contrast s2 - s0")
out("          T3  fresh seeds, arms at salts 0, 1, 2;  c0 = (s1 + s2)/2 - s0 (salt 0 against non-zero), c12 = s2 - s1 (two non-zero salts)")
out("          R2  the 12 new seeds' committed s0, s1 plus one salt-2 arm each;  s2 - (s0 + s1)/2  (orthogonal to the observed s1 - s0)")

NOISE = {"N62": (0.062, 0.0), "N81": (0.081, 0.0), "T": (0.040, 1 / 16)}


def e_draw(rng, model):
    sd, q = NOISE[model]
    return rng.gauss(0, sd) + (0.25 if q and rng.random() < q else 0.0)


def power(design, N, delta, model, trials=4000, seed=96):
    rng = random.Random(seed)
    tq = t_q(0.975, N - 1)
    hits = [0, 0]
    for _ in range(trials):
        cs = [[], []]
        for _ in range(N):
            s0, s1, s2 = -delta + e_draw(rng, model), e_draw(rng, model), e_draw(rng, model)
            if design == "T2":
                cs[0].append(s2 - s0)
            elif design == "T3":
                cs[0].append((s1 + s2) / 2 - s0)
                cs[1].append(s2 - s1)
            else:
                cs[0].append(s2 - (s0 + s1) / 2)
        for j, c in enumerate(cs):
            if c:
                m, sd = st.mean(c), st.stdev(c)
                hits[j] += sd > 0 and abs(m) / (sd / math.sqrt(N)) > tq
    return hits[0] / trials, hits[1] / trials


COST = {"T2": 2, "T3": 3, "R2": 1}
out("design  N   arms  pair-slots  delta   power N62  power N81  power T   (T3: c0 | c12, c12 should hold its 5% size)")
for design, Ns in (("T2", (8, 12, 16)), ("T3", (8, 12, 16)), ("R2", (12,))):
    for N in Ns:
        for delta in (0.0, 0.05, 0.082):
            ps = [power(design, N, delta, m) for m in ("N62", "N81", "T")]
            cell = "   ".join(f"{p[0]:.3f}" + (f" | {p[1]:.3f}" if design == "T3" else "        ") for p in ps)
            out(f"{design}      {N:2d}  {COST[design] * N:4d}  {COST[design] * N / 2:6.0f}      {delta:.3f}   {cell}")
out("a pair-slot is two arms run concurrently at --workers 2 on a four-core session, about 40-60 min (RBT-108's runners: 2 seeds in 2-2.5 h)")
