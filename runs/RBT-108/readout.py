"""The pre-registered readout for RBT-108: the arena's A/A null at n = 16, from the committed summaries only.

RBT-96's instrument, twelve new A/A seeds (205-216) beside its first four (201-204).  Per seed, d = s1 - s0,
the final-fifth holistic mean champion fitness of the salt-1 arm minus the salt-0 arm, read from the
committed generations.txt through RBT-85's summary() exactly as runs/RBT-96/readout.py reads it.

Registered readouts (the RBT-108 ticket's pre-registration, items 1-5, and its three predictions):
1. out of sample: RMS d over the 12 new seeds, 95% chi-square CI on 12 df; RBT-96's null replicates iff
   the CI contains 0.128;
2. pooled over 16: RMS d, h = t(4) * RMS / sqrt 4, and the seeds needed for a 95% half-width of 0.10;
3. the tail: |d| >= 0.20 among the 12, Clopper-Pearson 95%, with what the summaries hold on each such seed;
4. the pairing check per pair;
5. RBT-74, RBT-85 and RBT-94 against the pooled h (clears or not; no re-scoring).
Then, separately and labelled post hoc: mean d with a t CI, the sign count with an exact sign test, and
RMS^2 decomposed as mean^2 + variance.

    python runs/RBT-108/readout.py

Pure Python, no simulation and no new dependency: the t, chi-square and beta quantiles are computed here
from the regularised incomplete gamma and beta functions and checked against tabled values on import.
"""
import importlib.util
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "..")
RBT96 = os.path.join(RUNS, "RBT-96")
_spec = importlib.util.spec_from_file_location("rbt96_readout", os.path.join(RBT96, "readout.py"))
r96 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r96)
r85 = r96.r85

OLD = (201, 202, 203, 204)
NEW = tuple(range(205, 217))
RBT96_RMS = 0.128  # RBT-96's registered point, runs/RBT-96/REPORT.md section 3
TAIL = 0.20


# --- distributions -----------------------------------------------------------------------------

def _gammainc_lower(a, x):
    """Regularised lower incomplete gamma P(a, x) (Numerical Recipes gser / gcf)."""
    if x <= 0:
        return 0.0
    gln = math.lgamma(a)
    if x < a + 1:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(10000):
            ap += 1
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return s * math.exp(-x + a * math.log(x) - gln)
    b, c, d = x + 1 - a, 1e300, 1 / (x + 1 - a)
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return 1 - math.exp(-x + a * math.log(x) - gln) * h


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (1e-300 if abs(d) < 1e-300 else d)
    h = d
    for m in range(1, 10000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        d = 1 / (1e-300 if abs(d) < 1e-300 else d)
        c = 1 + aa / c
        c = 1e-300 if abs(c) < 1e-300 else c
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        d = 1 / (1e-300 if abs(d) < 1e-300 else d)
        c = 1 + aa / c
        c = 1e-300 if abs(c) < 1e-300 else c
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def _bisect(f, target, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def t_cdf(t, df):
    p = 0.5 * betainc(df / 2, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def t_q(p, df):
    return _bisect(lambda t: t_cdf(t, df), p, -1e3, 1e3)


def t_p2(t, df):
    return 2 * (1 - t_cdf(abs(t), df))


def chi2_q(p, df):
    return _bisect(lambda x: _gammainc_lower(df / 2, x / 2), p, 0.0, 1e4)


def beta_q(p, a, b):
    return _bisect(lambda x: betainc(a, b, x), p, 0.0, 1.0)


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else beta_q(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta_q(1 - alpha / 2, k + 1, n - k)
    return lo, hi


def sign_test_p2(k, n):
    """Exact two-sided sign test: twice the smaller binomial(n, 1/2) tail, capped at 1."""
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def sign_flip_p2(xs):
    """Exact two-sided sign-flip (randomisation) test on the mean: under a pure A/A the arms are exchangeable,
    so each d is symmetric about 0 whatever its tail. Enumerates all 2^n sign assignments."""
    obs = abs(sum(xs))
    n, hit = len(xs), 0
    for mask in range(2 ** n):
        s = sum(-x if mask >> i & 1 else x for i, x in enumerate(xs))
        hit += abs(s) >= obs - 1e-12
    return hit / 2 ** n, hit, 2 ** n


# tabled values; a wrong quantile would move every verdict, so it is checked, not trusted
for got, want in ((t_q(0.975, 4), 2.776445), (t_q(0.975, 3), 3.182446), (t_q(0.975, 7), 2.364624),
                  (t_q(0.975, 11), 2.200985), (t_q(0.975, 15), 2.131450),
                  (chi2_q(0.025, 12), 4.403789), (chi2_q(0.975, 12), 23.336664),
                  (chi2_q(0.025, 16), 6.907664), (chi2_q(0.975, 16), 28.845351)):
    assert abs(got - want) < 1e-5, (got, want)
_cp = clopper_pearson(1, 12)
assert abs(_cp[0] - 0.002107) < 1e-5 and abs(_cp[1] - 0.384796) < 1e-5, _cp
assert sign_flip_p2([1.0, 2.0, 3.0])[1:] == (2, 8)  # only all-positive and all-negative reach |6|


# --- data ---------------------------------------------------------------------------------------

def load(seed):
    a = r85.summary(os.path.join(RBT96, f"s0-{seed}"), True)
    b = r85.summary(os.path.join(RBT96, f"s1-{seed}"), True)
    da = r96.read_digests(os.path.join(RBT96, f"s0-{seed}"), True)
    db = r96.read_digests(os.path.join(RBT96, f"s1-{seed}"), True)
    oa = r96.read_opponent(os.path.join(RBT96, f"s0-{seed}"), True)
    ob = r96.read_opponent(os.path.join(RBT96, f"s1-{seed}"), True)
    n = min(len(a["environment"]), len(b["environment"]))
    pair = {
        "conv_same": da["conventional"] == db["conventional"],
        "conv": da["conventional"],
        "hol_differs": da["holistic"][0] != db["holistic"][0],
        "env_same": a["environment"][:n] == b["environment"][:n],
        "gens": n,
        "complete": a["complete"] and b["complete"],
    }
    pair["ok"] = pair["conv_same"] and pair["hol_differs"] and pair["env_same"]
    return {"s0": a["final_fifth"], "s1": b["final_fifth"], "d": b["final_fifth"] - a["final_fifth"],
            "pair": pair, "opp": (oa, ob)}


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def rms_ci(r, k):
    """95% chi-square CI on sigma from an RMS on k df (true mean 0)."""
    return r * math.sqrt(k / chi2_q(0.975, k)), r * math.sqrt(k / chi2_q(0.025, k))


def seeds_for(r, half=0.10):
    """Smallest n with t(n-1) * r / sqrt n <= half: RBT-96's convention (9 seeds at 0.128)."""
    n = 2
    while t_q(0.975, n - 1) * r / math.sqrt(n) > half:
        n += 1
    return n


def committed_mean(path, pattern):
    """A verdict's paired mean and its verdict word, read from the committed readout lines that state them."""
    for i, line in enumerate(open(path).read().splitlines(), 1):
        m = re.search(pattern, line)
        if m:
            lines = open(path).read().splitlines()
            v = next((re.search(r"verdict by the pre-registered rule: (\w+)", x).group(1) for x in lines[i:] if "verdict by the pre-registered rule" in x), "?")
            return float(m.group(1)), i, v
    raise ValueError(f"{path}: no line matches {pattern}")


def main():
    rows = {s: load(s) for s in OLD + NEW}
    new = [rows[s]["d"] for s in NEW]
    allv = [rows[s]["d"] for s in OLD + NEW]
    fmt = lambda xs: ", ".join(f"{x:+.3f}" for x in xs)

    print("RBT-108 readout, from the committed summaries under runs/RBT-96/{s0,s1}-SEED/ only (generations.txt, opponent.txt, conventional-digest.txt)")
    print("d = s1 - s0, final-fifth holistic mean champion fitness (RBT-85's summary(), as runs/RBT-96/readout.py)\n")
    print("seed   s0      s1      d        set")
    for s in OLD + NEW:
        r = rows[s]
        print(f"{s}   {r['s0']:.3f}   {r['s1']:.3f}   {r['d']:+.3f}   {'RBT-96' if s in OLD else 'new'}")

    print("\n=== REGISTERED READOUTS (RBT-108 pre-registration) ===")

    r12 = rms(new)
    lo12, hi12 = rms_ci(r12, 12)
    rep = lo12 <= RBT96_RMS <= hi12
    print("\n1. out of sample: the 12 new seeds (205-216)")
    print(f"d: {fmt(new)}")
    print(f"RMS d = {r12:.4f}   95% chi-square CI on 12 df [{lo12:.4f}, {hi12:.4f}]   contains RBT-96's 0.128: {rep}")
    print(f"RBT-96's null {'REPLICATES' if rep else 'DOES NOT REPLICATE'} by the registered criterion")
    k12 = (math.sqrt(12 / chi2_q(0.975, 12)), math.sqrt(12 / chi2_q(0.025, 12)))
    print(f"  note (readout adversary F2): the criterion passes any 12-seed RMS in [{RBT96_RMS / k12[1]:.3f}, {RBT96_RMS / k12[0]:.3f}], so it is weak evidence")

    r16 = rms(allv)
    lo16, hi16 = rms_ci(r16, 16)
    t4 = t_q(0.975, 4)
    h = t4 * r16 / math.sqrt(4)
    n10 = seeds_for(r16)
    print("\n2. pooled over 16 seeds (201-216)")
    print(f"RMS d = {r16:.4f}   (95% chi-square CI on 16 df [{lo16:.4f}, {hi16:.4f}])")
    print(f"h a 4-seed mean must clear: t(4) * RMS / sqrt 4 = {t4:.4f} * {r16:.4f} / 2 = {h:.4f}   (RBT-96, n = 4: 0.178)")
    print(f"  note (readout adversary F2): t(4) is the registered convention and is kept; at the null's own 16 df,"
          f" t(16) * RMS / 2 = {t_q(0.975, 16) * r16 / 2:.4f}. No committed verdict lies between the two.")
    print("fresh-terrain analogue: NOT COMPUTED. The champions probe (runs/RBT-96/adversary/champions.txt) covers seeds 201-204 only;")
    print("  it was not repeated for 205-216, and no committed file holds a fresh-terrain d for them.")
    print(f"seeds for a 95% half-width of 0.10 (smallest n with t(n-1) * RMS / sqrt n <= 0.10): {n10}"
          f"   (t({n10 - 1}) * RMS / sqrt {n10} = {t_q(0.975, n10 - 1) * r16 / math.sqrt(n10):.4f};"
          f" at n = {n10 - 1}: {t_q(0.975, n10 - 2) * r16 / math.sqrt(n10 - 1):.4f})")
    print(f"  same rule at the pooled CI's ends: {seeds_for(lo16)} seeds at RMS {lo16:.4f}, {seeds_for(hi16)} at {hi16:.4f}")

    tail = [s for s in NEW if abs(rows[s]["d"]) >= TAIL]
    k = len(tail)
    cp = clopper_pearson(k, len(NEW))
    print(f"\n3. the tail: |d| >= {TAIL:.2f} among the 12 new seeds")
    print(f"count {k}/12 ({', '.join(str(s) for s in tail) or 'none'})   rate {k / 12:.3f}   Clopper-Pearson 95% [{cp[0]:.4f}, {cp[1]:.4f}]")
    old_tail = [s for s in OLD if abs(rows[s]['d']) >= TAIL]
    print(f"(for reference, RBT-96's four: {len(old_tail)}/4 ({', '.join(map(str, old_tail))}); pooled {k + len(old_tail)}/16,"
          f" Clopper-Pearson 95% [{clopper_pearson(k + len(old_tail), 16)[0]:.4f}, {clopper_pearson(k + len(old_tail), 16)[1]:.4f}])")
    for s in tail:
        oa, ob = rows[s]["opp"]
        print(f"seed {s}: d {rows[s]['d']:+.3f} (s0 {rows[s]['s0']:.3f}, s1 {rows[s]['s1']:.3f})")
        print("  holistic s1/s0 solo steering: NOT AVAILABLE in the summaries (opponent.txt carries the holistic side's solo approach and")
        print("  terrain success only; steering was measured for 201 by the RBT-96 adversary from the bulk, which is on ckpt/rbt-96-SEED-ARM)")
        print(f"  what the summaries do hold, s0 / s1: holistic solo approach {oa['holistic_approach']:+.2f} / {ob['holistic_approach']:+.2f} m,"
              f" holistic terrain success {oa['holistic_terrain']:.3f} / {ob['holistic_terrain']:.3f};"
              f" the wheeled opponent (identical in both arms): approach {oa['approach']:+.2f} m, steering {oa['steering']:.2f} of 3")

    print("\n4. pairing check per pair (conventional lineage hash identical, holistic lineage differs, terrain+start seeds identical)")
    print("seed   conventional sha256 (n)   conv identical   holistic differs   terrain+start identical (gens)   complete   PASS")
    for s in OLD + NEW:
        p = rows[s]["pair"]
        print(f"{s}   {p['conv'][0][:12]} ({p['conv'][1]})     {str(p['conv_same']):15}  {str(p['hol_differs']):17}  {str(p['env_same']):5} ({p['gens']})"
              f"                    {str(p['complete']):9}  {p['ok']}")
    npass = sum(rows[s]["pair"]["ok"] for s in NEW)
    print(f"new seeds: {npass}/12 pass;  all sixteen: {sum(rows[s]['pair']['ok'] for s in OLD + NEW)}/16")

    print(f"\n5. earlier verdicts against the pooled null (a 4-seed mean clears iff |mean| > h = {h:.4f}; no verdict is re-scored)")
    v74 = committed_mean(os.path.join(RUNS, "RBT-74", "readout.txt"), r"^n = 4 .*?\bmean ([+-]?\d+\.\d+)")
    v85 = committed_mean(os.path.join(RUNS, "RBT-85", "readout-from-summaries.txt"), r"^n = 4 .*?\bmean ([+-]?\d+\.\d+)")
    se4 = r16 / math.sqrt(4)
    print("verdict   committed mean   file:line                                  n   verdict by its rule   t(4) vs null   p      |mean| > h?")
    for name, (m, ln, verdict), f in (("RBT-74", v74, "runs/RBT-74/readout.txt"), ("RBT-85", v85, "runs/RBT-85/readout-from-summaries.txt")):
        t = m / se4
        print(f"{name}    {m:+.4f}          {f + ':' + str(ln):42} 4   {verdict.lower():20}  {t:+.2f}          {t_p2(t, 4):.3f}  {'clears' if abs(m) > h else 'does not clear'}")
    t7 = t_q(0.975, 7)
    print(f"RBT-94    none: never run (backlog proposal, coordinator 2026-09-19); runs/RBT-94/ does not exist, so there is no verdict to re-read.")
    print(f"          its registered size, 8 seeds, would carry a 95% half-width t(7) * RMS / sqrt 8 = {t7 * r16 / math.sqrt(8):.4f} against this null")
    print(f"          (RBT-85's |mean| {abs(v85[0]):.4f} {'would' if abs(v85[0]) > t7 * r16 / math.sqrt(8) else 'would not'} clear it)")

    print("\nregistered predictions")
    preds = (
        ("12-seed RMS in [0.07, 0.16]", f"{r12:.4f}", 0.07 <= r12 <= 0.16),
        ("1-4 of 12 seeds with |d| >= 0.20", f"{k}", 1 <= k <= 4),
        ("pooled n for +-0.10 in [6, 14]", f"{n10}", 6 <= n10 <= 14),
    )
    for p, v, ok in preds:
        print(f"  {p:36} {v:>8}   {'RIGHT' if ok else 'WRONG'}")

    print("\n=== POST HOC DIAGNOSTIC (not registered; asked by the coordinator after the d values were posted) ===")
    print("An A/A null centres on zero by construction. Is the mean of d resolved away from 0?")
    no_tail = [rows[s]["d"] for s in OLD + NEW if s not in (201, 212)]
    for label, xs in (("12 new", new), ("all 16", allv), ("16 without the tail seeds 201 and 212", no_tail), ("RBT-96's 4", [rows[s]["d"] for s in OLD])):
        n = len(xs)
        m, sd = st.mean(xs), st.stdev(xs)
        tq = t_q(0.975, n - 1)
        t = m / (sd / math.sqrt(n))
        pos, neg = sum(x > 0 for x in xs), sum(x < 0 for x in xs)
        var = st.pvariance(xs)
        r2 = sum(x * x for x in xs) / n
        print(f"\n{label} (n = {n})")
        print(f"  mean d {m:+.4f}   SD {sd:.4f} ({n - 1} df)   95% t({n - 1}) CI [{m - tq * sd / math.sqrt(n):+.4f}, {m + tq * sd / math.sqrt(n):+.4f}]"
              f"   t = {t:+.2f}, two-sided p = {t_p2(t, n - 1):.4f}")
        pf, hit, tot = sign_flip_p2(xs)
        print(f"  exact two-sided sign-flip test on the mean (valid under the heavy tail): p = {pf:.4f} ({hit}/{tot})")
        print(f"  sign count: {pos} positive, {neg} negative, {n - pos - neg} zero   exact two-sided sign-test p = {sign_test_p2(pos, pos + neg):.4f}")
        print(f"  RMS^2 = mean^2 + variance (divisor n): {r2:.5f} = {m * m:.5f} + {var:.5f}   ({100 * m * m / r2:.0f}% mean^2, {100 * var / r2:.0f}% variance)"
              f"   RMS {math.sqrt(r2):.4f}; with the mean removed, sqrt(variance) {math.sqrt(var):.4f}")
    ha = {s: rows[s]["opp"][1]["holistic_approach"] - rows[s]["opp"][0]["holistic_approach"] for s in OLD + NEW}
    ht = {s: rows[s]["opp"][1]["holistic_terrain"] - rows[s]["opp"][0]["holistic_terrain"] for s in OLD + NEW}
    print("\n  the same question of the solo measures in opponent.txt (holistic final-fifth champions alone, s1 - s0), descriptive only:")
    for label, ss in (("12 new", NEW), ("all 16", OLD + NEW)):
        a, t_ = [ha[s] for s in ss], [ht[s] for s in ss]
        pa, pt = sum(x > 0 for x in a), sum(x > 0 for x in t_)
        print(f"  {label}: solo approach d mean {st.mean(a):+.3f} m, {pa}/{len(a)} positive (sign p {sign_test_p2(pa, sum(x != 0 for x in a)):.4f});"
              f"  terrain success d mean {st.mean(t_):+.3f}, {pt}/{len(t_)} positive, {sum(x == 0 for x in t_)} zero (sign p {sign_test_p2(pt, sum(x != 0 for x in t_)):.4f})")
    print(f"  corr(d, solo approach d) over 16 = {r85.corr(allv, [ha[s] for s in OLD + NEW]):+.2f}: the solo lean is the same lineage outcome, not a second test")
    g0 = []
    for s in OLD + NEW:
        v = []
        for arm in ("s0", "s1"):
            lines = open(os.path.join(RBT96, f"{arm}-{s}", "generations.txt")).read().splitlines()
            head, row = lines[0].split("\t"), lines[1].split("\t")
            assert row[0] == "0"
            v.append(float(row[head.index("champ_holistic_mean")]))
        g0.append(v[1] - v[0])
    print(f"  at founding (generation 0's champion row, s1 - s0, 16 seeds): mean {st.mean(g0):+.4f}, {sum(x > 0 for x in g0)}/16 positive,"
          f" exact sign-flip p = {sign_flip_p2(g0)[0]:.4f}")
    m16, sd16, pv16 = st.mean(allv), st.stdev(allv), math.sqrt(st.pvariance(allv))
    print(f"\n  pooled, for comparison with section 2 (not a replacement for it): h from the spread about the mean instead of the RMS:"
          f" SD {sd16:.4f} (divisor n-1) gives t(4) * SD / 2 = {t4 * sd16 / 2:.4f}; {pv16:.4f} (divisor n) gives {t4 * pv16 / 2:.4f}"
          f" (against {h:.4f}); seeds for +-0.10 on the SD: {seeds_for(sd16)}")


if __name__ == "__main__":
    main()
