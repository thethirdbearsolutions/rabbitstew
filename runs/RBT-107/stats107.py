"""RBT-107 Amendment 2: the one-sided tests of §5.5, with no scipy (the containers have numpy only).

    tcdf(x, df)              Student t cdf, by the regularized incomplete beta (continued fraction, Numerical Recipes 6.4)
    t_test(x)                one-sample t against 0, one-sided "greater": (mean, t, df, p)
    yuen(x, trim=0.2)        Yuen's one-sample trimmed-mean t, one-sided "greater": (trimmed mean, t, df, p);
                             g = floor(trim n), h = n - 2g, winsorized sd s_w, se = s_w / ((h / n) sqrt n) = s_w sqrt n / h,
                             df = h - 1.  (h / n equals 1 - 2 trim only when trim n is an integer, e.g. n = 20; at
                             n = 19 h / n = 13/19, not 0.6.  The code is the registered object: RBT-107 ruling 05:50,
                             adversary F2; docstring corrected, code unchanged.)
    wilcoxon(x)              Wilcoxon signed-rank, exact null (zeros dropped, average ranks for ties), one-sided "greater":
                             (W+, p)
    holm(ps, alpha)          Holm's step-down: list of reject flags in the input order
Every test is "greater"; a "less" hypothesis is tested on -x.  `python stats107.py` runs the self-checks.
"""
import math


def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c
        c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c
        c = c if abs(c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-14:
            break
    return h


def betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def tcdf(t, df):
    p = 0.5 * betai(df / 2.0, 0.5, df / (df + t * t))
    return 1.0 - p if t > 0 else p


def t_test(x):
    n = len(x)
    m = sum(x) / n
    sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
    if sd == 0:  # a degenerate sample: certain only if its mean is off 0 in the tested direction
        return m, (math.inf if m > 0 else -math.inf if m < 0 else 0.0), n - 1, (0.0 if m > 0 else 1.0)
    t = m / (sd / math.sqrt(n))
    return m, t, n - 1, 1.0 - tcdf(t, n - 1)


def yuen(x, trim=0.2):
    n = len(x)
    g = int(math.floor(trim * n))
    xs = sorted(x)
    core = xs[g:n - g]
    tm = sum(core) / len(core)
    w = [min(max(v, xs[g]), xs[n - g - 1]) for v in xs]
    wm = sum(w) / n
    sw = math.sqrt(sum((v - wm) ** 2 for v in w) / (n - 1))
    h = n - 2 * g
    se = sw / ((h / n) * math.sqrt(n))
    df = h - 1
    if se == 0:
        return tm, (math.inf if tm > 0 else -math.inf if tm < 0 else 0.0), df, (0.0 if tm > 0 else 1.0)
    t = tm / se
    return tm, t, df, 1.0 - tcdf(t, df)


def wilcoxon(x):
    v = [a for a in x if a != 0]
    n = len(v)
    order = sorted(range(n), key=lambda i: abs(v[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(v[order[j + 1]]) == abs(v[order[i]]):
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    wplus = sum(r for r, a in zip(ranks, v) if a > 0)
    # exact null on doubled ranks (integers even with half-ranks); cached per n when there are no ties
    r2 = [int(round(2 * r)) for r in ranks]
    if sorted(r2) == list(range(2, 2 * n + 1, 2)):
        if n not in _WCACHE:
            _WCACHE[n] = _wdist(r2)
        dist, tot = _WCACHE[n]
        return wplus, sum(dist[int(round(2 * wplus)):]) / tot
    dist, tot = _wdist(r2)
    return wplus, sum(dist[int(round(2 * wplus)):]) / tot


_WCACHE = {}


def _wdist(r2):
    top = sum(r2)
    dist = [0] * (top + 1)
    dist[0] = 1
    for r in r2:
        new = dist[:]
        for s in range(top - r, -1, -1):
            if dist[s]:
                new[s + r] += dist[s]
        dist = new
    return dist, sum(dist)


def holm(ps, alpha=0.05):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    rej = [False] * len(ps)
    for k, i in enumerate(order):
        if ps[i] <= alpha / (len(ps) - k):
            rej[i] = True
        else:
            break
    return rej


if __name__ == "__main__":
    # self-checks against textbook values
    assert abs(tcdf(2.262, 9) - 0.975) < 5e-4, tcdf(2.262, 9)
    assert abs(tcdf(1.833, 9) - 0.95) < 5e-4
    assert abs(tcdf(-1.0, 5) - 0.18161) < 1e-4
    _, p = wilcoxon([1, 2, 3, 4, 5])          # all positive, n = 5: p = 1/32
    assert abs(p - 1 / 32) < 1e-12, p
    _, p = wilcoxon([1, -2, 3, 4, 5, 6])      # W+ = 19 of 21, n = 6: P(W+ >= 19) = 3/64
    assert abs(p - 3 / 64) < 1e-12, p
    tm, t, df, p = yuen([-0.3, 0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 3.0])
    assert df == 5 and abs(tm - 0.3333333) < 1e-6, (tm, df)
    tm, t, df, p = yuen([v - 9 for v in range(1, 20)])  # n = 19: g = 3, h = 13, winsorized 4..16, s_w^2 = 398/18
    se = math.sqrt(398 / 18) * math.sqrt(19) / 13          # the coded se, s_w sqrt n / h (not s_w / (0.6 sqrt n))
    assert df == 12 and abs(tm - 1.0) < 1e-12 and abs(t - 1.0 / se) < 1e-12, (tm, t, df)
    assert yuen([0.0] * 10)[3] == 1.0 and t_test([0.0] * 10)[3] == 1.0 and wilcoxon([0.0] * 10 + [1.0])[1] == 0.5
    assert holm([0.01, 0.04]) == [True, True] and holm([0.03, 0.04]) == [False, False] and holm([0.02, 0.06]) == [True, False]
    print("stats107 self-checks PASS: tcdf, wilcoxon exact, yuen trimmed mean, df and se (n = 19), holm")
