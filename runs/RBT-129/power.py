"""RBT-129 (world sweep) power model, budget and staging arithmetic.  DESIGN ONLY: runs no simulator.

Four parts, each bounded by a floor and a ceiling (R11), with the noise taken from committed data:

  1. income   the per-point H - D income difference (side-by-side, and per member in the merged world).
              Noise: RBT-118's 29 paired histories (pool.txt, probe_terrain.txt): between-history SD of the
              last-100 H - D is 0.144 on random terrain, 0.334 on flat (ceiling).  Reported as a minimum
              detectable effect (MDE) and as the half-width of the UNDECIDED price band around a break-even,
              using the price slope d(H - D)/dp = kJ_D - kJ_H (RBT-118 §4/§4a: about 14-15 kJ a season before
              the fairness set; bounded here by 6 and 15.5 kJ, since effector_bias_sigma and the motor budget
              are expected to cut both bills).
  2. share    the merged-world head-to-head (merge_after = 60).  r2 (adversary M1): the statistic is the CHANGE
              y' = (mean holistic share of the pooled capacity over seasons 240-299) - (share at the merge).  An independent replica of Ecology.step's demography, adapted
              from runs/RBT-121/adversary/adv_demography.py (same rules: threshold 3, birth cost 1, max age 60,
              initial energy 3, crossover 0.3, gain Poisson(g) - 0.1, living cost 0.25), with two faunas that
              live apart until season 60 and then share 120 slots.  Swept over the regime (resident gross income
              g0), the breeding rule (lottery = committed; energy; leakx:lambda = RBT-126's `--energy-leak lambda`,
              recommended at 0.3 and not yet ruled), and the income edge.
              A per-seed spread of the edge (tau) stands in for history-to-history variation.
  3. perceive intact - decoy food per seed, from probing M living members on D draws each.  Noise:
              runs/RBT-121/adversary/noise_components.txt (between-member SD 0.563 / 0.212, member x draw SD
              1.469 / 0.945, holistic / designed).
  5. resolve section 6.2's RESOLVING check, tied to the income TIE margin (adversary M3), per rule.
  6. checks   merge-time composition (M1), CONTINGENT on a pooled per-kind null (M4), T4 at seed level (M9).
  4. budget   CPU-hours per stage from RBT-105's measured 10.2 s per arm-season at 2 cores (20 core-s),
              bounded above by 25 core-s for the fairness set's settle and the 4 m PW disc.

Multiplicity: every per-point call is made under Benjamini-Hochberg at q = 0.10 within its family.  The BH
threshold for one rejection lies between q/K (only one point rejects) and q (all do); both bounds are printed,
with K = 36 (Stage 1) and K = 72 (Stages 1 + 2).

python3 runs/RBT-129/power.py [reps]   (default reps 500; about 20 minutes on 4 cores)
"""
import math
import sys
from multiprocessing import Pool

import numpy as np

Q = 0.10
K_STAGE1, K_ALL = 36, 72
DELTA_I = 0.15   # income TIE margin (section 6.1)
DELTA_S = 0.10   # share TIE margin, on y'
RULES = ("lottery", "energy", "leakx:0.3")
SEEDS = (6, 8, 12, 16)


# ---------- Student t, without scipy ----------

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
        if abs(de - 1.0) < 1e-12:
            break
    return h


def _betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T > t)."""
    x = df / (df + t * t)
    p = 0.5 * _betainc(df / 2.0, 0.5, x)
    return p if t >= 0 else 1.0 - p


def t_crit(alpha_two_sided, df):
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 2 * t_sf(mid, df) > alpha_two_sided:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def power_t(effect, sd, n, alpha, reps=40000, rng=None):
    """P(two-sided one-sample t rejects, in the true direction) at a per-seed SD, by simulation."""
    rng = rng or np.random.default_rng(1290)
    x = rng.normal(effect, sd, size=(reps, n))
    t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n))
    c = t_crit(alpha, n - 1)
    return float(np.mean(t > c)) if effect >= 0 else float(np.mean(t < -c))


def tost(sd, n, margin, alpha, effect=0.0, reps=40000, rng=None):
    """P(the (1 - 2 alpha) CI lies inside +-margin): the TIE call's power at a true effect."""
    rng = rng or np.random.default_rng(1291)
    x = rng.normal(effect, sd, size=(reps, n))
    m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n)
    c = t_crit(2 * alpha, n - 1)
    return float(np.mean((m - c * se > -margin) & (m + c * se < margin)))


# ---------- Part 1: income ----------

def part_income():
    print("## 1. Income difference H - D per point (seed = unit; t test; BH q = 0.10)")
    print("#   per-seed SD: floor 0.144 (RBT-118 random terrain, n 29), ceiling 0.334 (flat, n 29)")
    print("#   MDE80 = the true |H - D| detected with power 0.80; band = MDE80 / (kJ_D - kJ_H) in $/kJ,")
    print("#   i.e. the half-width of the price interval around a break-even inside which a point stays UNDECIDED")
    for label, alpha in (("BH worst (q/K, K=36)", Q / K_STAGE1), ("BH worst (q/K, K=72)", Q / K_ALL), ("BH half (q/2)", Q / 2)):
        for sd in (0.144, 0.334):
            row = []
            for n in SEEDS:
                c = t_crit(alpha, n - 1)
                # MDE by the noncentral approximation, then checked by simulation below
                mde = (c + 1.0) * sd / math.sqrt(n)
                for _ in range(30):
                    p = power_t(mde, sd, n, alpha, reps=6000)
                    mde *= 1.0 + 0.5 * (0.80 - p)
                band_lo, band_hi = mde / 15.5, mde / 6.0
                row.append(f"n={n:2d}: MDE80 {mde:.3f}  band {band_lo:.4f}-{band_hi:.4f}")
            print(f"  {label:22s} sd {sd:.3f} | " + " | ".join(row))
    for margin in (0.10, 0.15):
        print(f"#   TIE (TOST, margin {margin:.2f} items a season) at a true difference of 0, BH worst K=36 / q/2:")
        for sd in (0.144, 0.334):
            print("   sd %.3f: " % sd + "  ".join(
                f"n={n}: {tost(sd, n, margin, Q / K_STAGE1):.2f} / {tost(sd, n, margin, Q / 2):.2f}" for n in SEEDS))
    print("#   Prior map (RBT-118 §4/§4a static arithmetic, pre-fairness; for orientation, not a prediction):")
    print("#   H - D(p, clutter c) = dfood(c) + p (kJ_D - kJ_H); dfood(0) = -0.76, dfood(1) = -0.19 (medians);")
    print("#   kJ_D - kJ_H = 14.7.  Linear in c, clamped at the designed body's food floor for c = 2 (not measured).")
    for c in (0.0, 0.5, 1.0, 1.5, 2.0):
        dfood = -0.76 + 0.57 * c
        cells = []
        for p in (0.01, 0.018, 0.03, 0.053, 0.08):
            cells.append(f"{p:5.3f}: {dfood + p * 14.7:+.2f}")
        be = -dfood / 14.7
        print(f"   clutter {c:3.1f}x  " + "  ".join(cells) + f"   break-even {be:+.3f}/kJ")
    print()


# ---------- Part 2: merged-world share ----------

THR, BCOST, AGE, INIT, XRATE, COST, WORK = 3.0, 1.0, 60, 3.0, 0.3, 0.25, 0.1


def _leak(rule):
    return float(rule.split(":")[1]) if rule.startswith("leakx:") else 0.0


def _season(rng, pop, g_of, rule="lottery"):
    lam = _leak(rule)
    for p in pop:
        if lam and p[1] > THR:  # RBT-126 leakx: energy above the threshold leaks before the gain
            p[1] -= lam * (p[1] - THR)
        p[1] += rng.poisson(g_of[p[0]]) - WORK - COST
        p[2] += 1
    return [p for p in pop if p[1] > 0 and p[2] < AGE]


def _breed(rng, pop, cap, rule, kinds):
    elig = [p for p in pop if p[1] >= THR and p[0] in kinds]
    rng.shuffle(elig)
    if rule == "energy" or rule.startswith("leakx:"):
        elig.sort(key=lambda p: -p[1])  # stable: ties keep the shuffle
    for p in elig:
        if len(pop) >= cap:
            break
        # breeding stays within a fauna (ecology.py); crossover only swaps partners of the same kind: no type change
        p[1] -= BCOST
        pop.append([p[0], BCOST, 0])
    return pop


def merged_run(rng, gH, gD, rule, merge=60, horizon=300, window=(240, 300), cap=60, keep_H=None, keep_D=None):
    """Two faunas apart for `merge` seasons (60 slots each), then one arena of 2 * cap.  keep_H / keep_D, if set,
    cull that fauna to that count at the merge (the adversary's composition probe).  Returns (window share, share at
    the merge, holistic alive at the merge, designed alive at the merge, fixed)."""
    g_of = {0: gD, 1: gH}
    pops = {k: [[k, INIT, int(rng.integers(0, AGE))] for _ in range(cap)] for k in (0, 1)}
    for s in range(merge):
        for k in (0, 1):
            pops[k] = _season(rng, pops[k], g_of, rule)
            pops[k] = _breed(rng, pops[k], cap, rule, (k,))
    for k, keep in ((1, keep_H), (0, keep_D)):
        if keep is not None and len(pops[k]) > keep:
            idx = rng.permutation(len(pops[k]))[:keep]
            pops[k] = [pops[k][i] for i in idx]
    nH, nD = len(pops[1]), len(pops[0])
    pop = pops[0] + pops[1]
    s0 = nH / max(1, nH + nD)
    shares = []
    for s in range(merge, horizon):
        pop = _season(rng, pop, g_of, rule)
        pop = _breed(rng, pop, 2 * cap, rule, (0, 1))
        if window[0] <= s < window[1]:
            shares.append(sum(p[0] for p in pop) / (2 * cap))
    fixed = (not any(p[0] == 1 for p in pop)) or (not any(p[0] == 0 for p in pop))
    return float(np.mean(shares)), s0, nH, nD, fixed


def merged_history(rng, gH, gD, rule, merge=60, horizon=300, window=(240, 300), cap=60):
    """r1's interface (kept for the adversary's probes): (window share, fixed)."""
    r = merged_run(rng, gH, gD, rule, merge, horizon, window, cap)
    return r[0], r[4]


def _cell(args):
    """One replica cell: `reps` seeds at (rule, g0, edge, tau, keep_H); returns arrays of y' and of the raw share."""
    rule, g0, edge, tau, keep_H, reps, seed = args
    rng = np.random.default_rng(seed)
    yp, raw, both = [], [], []
    for _ in range(reps):
        e = edge + (rng.normal(0, tau) if tau else 0.0)
        sh, s0, nH, nD, _ = merged_run(rng, g0 + e / 2, max(0.0, g0 - e / 2), rule, keep_H=keep_H)
        yp.append(sh - s0)
        raw.append(sh - 0.5)
        both.append(nH > 0 and nD > 0)
    return np.array(yp), np.array(raw), np.array(both)


def _t(x):
    n = x.shape[-1]
    return x.mean(-1) / (x.std(-1, ddof=1) / math.sqrt(n) + 1e-12)


def call_rate(y, n, alpha, sign, margin=0.0, B=4000, seed=1):
    """P(the WIN call: t over n resampled seeds rejects at alpha in direction `sign`, and |mean| >= margin).
    sign 0 counts either direction (a false-call rate)."""
    rng = np.random.default_rng(seed)
    x = y[rng.integers(0, len(y), size=(B, n))]
    t, m = _t(x), x.mean(1)
    c = t_crit(alpha, n - 1)
    if sign == 0:
        return float(np.mean((np.abs(t) > c) & (np.abs(m) >= margin)))
    return float(np.mean((sign * t > c) & (sign * m >= margin)))


def tie_rate(y, n, alpha, margin, B=4000, seed=2):
    rng = np.random.default_rng(seed)
    x = y[rng.integers(0, len(y), size=(B, n))]
    m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n)
    c2 = t_crit(2 * alpha, n - 1)
    return float(np.mean((m - c2 * se > -margin) & (m + c2 * se < margin)))


def part_share(pool, reps):
    print("## 2. Merged-world head-to-head, r2 statistic y' = share(240-299) - share(merge), by rule and regime")
    print("#   replica of Ecology.step; g0 = resident gross income a season (net = g0 - 0.35); edge = gH - gD, items a season;")
    print("#   tau = per-seed SD of the edge.  WIN: t on y' rejects and |mean y'| >= 0.10 (delta_s).  TIE: TOST on y' at +-0.10.")
    print("#   columns: mean y', per-seed SD, then WIN n8 [q/K36, q/2] n16 [q/K72, q/2], TIE n16 at q/2.")
    cells = []
    for rule in RULES:
        for g0 in (0.5, 0.8, 1.0, 1.3):
            for edge in (0.0, 0.05, 0.10, 0.15, 0.20, 0.40):
                for tau in ((0.0, 0.1) if edge in (0.0, 0.10) else (0.0,)):
                    cells.append((rule, g0, edge, tau, None, reps, hash((rule, g0, edge, tau)) % 2**31))
    res = pool.map(_cell, cells)
    out = {}
    for cell, (yp, raw, both) in zip(cells, res):
        rule, g0, edge, tau = cell[:4]
        sign = 0 if edge == 0 else 1
        w8 = [call_rate(yp, 8, a, sign, DELTA_S) for a in (Q / K_STAGE1, Q / 2)]
        w16 = [call_rate(yp, 16, a, sign, DELTA_S) for a in (Q / K_ALL, Q / 2)]
        tie16 = tie_rate(yp, 16, Q / 2, DELTA_S)
        out[(rule, g0, edge, tau)] = (float(yp.mean()), float(yp.std(ddof=1)))
        print(f"  {rule:10s} g0 {g0:.1f} edge {edge:+.2f} tau {tau:.1f}: y' {yp.mean():+.3f} sd {yp.std(ddof=1):.3f}"
              f" | WIN n8 [{w8[0]:.2f}, {w8[1]:.2f}] n16 [{w16[0]:.2f}, {w16[1]:.2f}] | TIE n16 {tie16:.2f}", flush=True)
    print()
    return out


def part_resolvable(pool, reps):
    print("## 5. RESOLVING (section 6.2, adversary M3): at the point's g0 (run at both 90% bounds), rule and n, RESOLVING iff")
    print("#   P(share TIE | income edge = delta_i = 0.15) <= 0.05  AND  P(share WIN | edge 0.15) >= 0.80, both at q/2 on y'.")
    print("#   columns per g0: P(TIE|0.15) / P(WIN|0.15) at n 8 ; n 16 ; R = RESOLVING at n 8 / n 16")
    grid = (0.5, 0.65, 0.8, 0.9, 1.0, 1.1, 1.3)
    cells = [(rule, g0, DELTA_I, 0.0, None, reps, 9000 + i) for i, (rule, g0) in
             enumerate((r, g) for r in RULES for g in grid)]
    res = pool.map(_cell, cells)
    table = {}
    for cell, (yp, raw, both) in zip(cells, res):
        rule, g0 = cell[:2]
        r = []
        for n in (8, 16):
            tie = tie_rate(yp, n, Q / 2, DELTA_S)
            win = call_rate(yp, n, Q / 2, 1, DELTA_S)
            r.append((tie, win, tie <= 0.05 and win >= 0.80))
        table[(rule, g0)] = r
    for rule in RULES:
        print(f"  {rule:10s} " + "  ".join(
            f"g0 {g0:.2f}: {table[(rule, g0)][0][0]:.2f}/{table[(rule, g0)][0][1]:.2f} ; {table[(rule, g0)][1][0]:.2f}/{table[(rule, g0)][1][1]:.2f}"
            f" {'Y' if table[(rule, g0)][0][2] else 'n'}/{'Y' if table[(rule, g0)][1][2] else 'n'}" for g0 in grid), flush=True)
    print()
    return table


def resolvable(g0, rule, n, reps=1500, seed=12906):
    """Section 6.2's check for one point, after Stage 1: g0 = the lower 90% bound over seeds of the point's resident
    gross income (mean season net income of the living, faunas pooled, M arm seasons 180-299, + 0.35), the ruled rule,
    the point's n.  Returns (P(TIE | edge delta_i), P(WIN | edge delta_i), RESOLVING)."""
    yp, _, _ = _cell((rule, g0, DELTA_I, 0.0, None, reps, seed))
    tie, win = tie_rate(yp, n, Q / 2, DELTA_S), call_rate(yp, n, Q / 2, 1, DELTA_S)
    return tie, win, tie <= 0.05 and win >= 0.80


def part_checks(pool, reps):
    print("## 6. Checks on the r2 statistics")
    print("#  6a (M1) merge-time composition, no body edge: the holistic fauna holds k of 60 at the merge.")
    print("#      columns: raw share - 0.5 at the window, false D-WIN n8 q/2 on the RAW statistic, and false WIN (either")
    print("#      sign) n8 q/2 on y'.")
    cells = [(rule, g0, 0.0, 0.0, k, reps, 7000 + i) for i, (rule, g0, k) in
             enumerate((r, g, k) for r in RULES for g in (0.8, 1.3) for k in (60, 45, 30, 15))]
    res = pool.map(_cell, cells)
    for cell, (yp, raw, both) in zip(cells, res):
        rule, g0, k = cell[0], cell[1], cell[4]
        print(f"   {rule:10s} g0 {g0:.1f} k {k:2d}: raw {raw.mean():+.3f}  false D-WIN raw {call_rate(raw, 8, Q / 2, -1, DELTA_S):.2f}"
              f"  false WIN y' {call_rate(yp, 8, Q / 2, 0, DELTA_S):.2f}", flush=True)
    print("#  6b (M4) CONTINGENT: F = var(y') / pooled per-kind null variance; the null pools 36 points x 4 seeds per kind")
    print("#      (df 108) at Stage 1.  F(0.99; n-1, 108) and the firing rate at the replica's history spread (tau 0.1):")
    for rule in RULES:
        for g0 in (0.8, 1.3):
            y0, _, _ = _cell((rule, g0, 0.0, 0.0, None, reps, 6100))
            yt, _, _ = _cell((rule, g0, 0.0, 0.1, None, reps, 6200))
            v0 = y0.var(ddof=1)
            row = []
            for n in (8, 16):
                fcrit = f_crit(0.01, n - 1, 108)
                rng = np.random.default_rng(3)
                x = yt[rng.integers(0, len(yt), size=(4000, n))]
                fires = float(np.mean(x.var(1, ddof=1) / v0 > fcrit))
                x0 = y0[rng.integers(0, len(y0), size=(4000, n))]
                false = float(np.mean(x0.var(1, ddof=1) / v0 > fcrit))
                row.append(f"n {n}: Fcrit {fcrit:.2f} fires {fires:.2f} (false {false:.3f})")
            print(f"   {rule:10s} g0 {g0:.1f}: sd null {math.sqrt(v0):.3f}, sd tau0.1 {yt.std(ddof=1):.3f} | " + " | ".join(row), flush=True)
    print("#  6c (M9) T4 at seed level in PW: per seed, the mean over the 3 PW points (c 1; p 0.01, 0.03, 0.08) of")
    print("#      f_G - f_L; seeds are common across points, so the test is a paired t over n seeds.  Per-point per-seed SD")
    print("#      of f is 0.14-0.23 (section 3's range); the two smell levels are independent histories.")
    for sd in (0.14, 0.23):
        sd_seed = math.sqrt(2) * sd / math.sqrt(3)
        row = []
        for d in (0.10, 0.25, 0.40):
            row.append(f"delta {d:.2f}: {power_t(d, sd_seed, 8, 0.0125):.2f} / {power_t(d, sd_seed, 8, 0.05):.2f}")
        print(f"   per-point sd {sd:.2f} (per-seed sd {sd_seed:.3f}), n 8, Holm first / last step: " + "  ".join(row))
    print()


def f_crit(alpha, d1, d2, B=400000, seed=5):
    rng = np.random.default_rng(seed)
    f = (rng.chisquare(d1, B) / d1) / (rng.chisquare(d2, B) / d2)
    return float(np.quantile(f, 1 - alpha))


# ---------- Part 3: perception ----------

def part_perceive():
    print("## 3. Perception: intact - decoy food per member-draw, averaged per seed; call needs mean >= F_MIN = 0.25")
    print("#   and a BH-significant t over seeds.  Per-seed SE = sqrt(2(1 - rho) s_md^2 / (M D) + s_b,diff^2 / M) with")
    print("#   s_md the member x draw SD, rho the intact/decoy correlation on shared draws, s_b,diff the between-member")
    print("#   SD of the member's own effect (assumed 0.5 x the between-member SD of food); tau_p between-seed SD.")
    for fauna, s_b, s_md in (("holistic", 0.563, 1.469), ("designed", 0.212, 0.945)):
        for M, D in ((20, 8), (40, 8)):
            for rho in (0.0, 0.5):
                for tau_p in (0.05, 0.15):
                    se_seed = math.sqrt(2 * (1 - rho) * s_md ** 2 / (M * D) + (0.5 * s_b) ** 2 / M)
                    sd = math.sqrt(se_seed ** 2 + tau_p ** 2)
                    row = []
                    for n in (8, 12):
                        row.append(f"n={n}: P(call | 0.25) {power_t(0.25, sd, n, Q / K_STAGE1, reps=20000):.2f}"
                                   f" / {power_t(0.25, sd, n, Q / 2, reps=20000):.2f}"
                                   f"  P(call | 0.40) {power_t(0.40, sd, n, Q / K_STAGE1, reps=20000):.2f}")
                    print(f"  {fauna:8s} M {M} D {D} rho {rho:.1f} tau_p {tau_p:.2f}: per-seed SD {sd:.3f} | " + " | ".join(row))
    print("#   Floor: F = 0 (committed worlds; RBT-113 holistic U -0.080, designed +0.021, probe_food.txt).")
    print("#   Ceiling: a finished nose in PW at G 2.5, +1.77 items (kinematic, probe_gprop.txt; M5: not a real-body")
    print("#   number, used only as the bound).  Any population effect above 0.4 is called at n 8 under either bound.")
    print()


# ---------- Part 4: budget ----------

def part_budget():
    print("## 4. Budget (core-hours), r2.  Arm cost 20 core-s per arm-season (RBT-105 measured), ceiling 25.")
    print("#   r2 (adversary S12): M and N fork from S's season-59 checkpoint (240 seasons each); probes re-costed at")
    print("#   0.46-0.83 core-h a seed (RBT-116 section 9's 0.35 CPU-s per solo season; 80 members a seed; the")
    print("#   intact - decoy battery reuses STEERS' 16 stage-2 draws); the planted set at 0.8 a point (>= 8 hosts a plant,")
    print("#   M7d); the pilot adds c2-p030-PW-G and runs N on all 4 seeds; the census's R4/PAYS cells are 18 (c 0, 1, 2)")
    print("#   under the sweep's block with a holistic plant beside the designed one, about 2.5 core-h each.")
    print("#   wall = total / 40 cores (ten 4-core sessions, two arms of different seeds per session at WORKERS=2)")
    for cs in (20.0, 25.0):
        h = lambda seasons: seasons * cs / 3600.0
        for probes in (0.46, 0.83):
            side, merged = h(300), h(240)
            null = 0.5 * h(240) * 0.85  # N on half the seeds; one fauna cloned (holistic bouts ~0.8x)
            per_seed = side + merged + null + probes
            plants = 0.8
            census_pt = 3 * h(60)
            pilot = 4 * 4 * (side + merged + h(240) * 0.85 + probes) + 4 * plants
            census = 150 * census_pt + 18 * 2.5
            print(f"  @ {cs:.0f} core-s, probes {probes:.2f}: per seed-point {per_seed:.2f} (side {side:.2f}, merged {merged:.2f},"
                  f" null {null:.2f}); census point {census_pt:.2f}")
            for label, n1, n2 in (("registered (n 8, R-B to 16)", 8, 8), ("lean (n 6, R-B to 12)", 6, 6)):
                s1 = 36 * (n1 * per_seed + plants)
                s2a = 16 * (n1 * per_seed + plants)
                s2b = 20 * n2 * per_seed
                total = pilot + census + s1 + s2a + s2b
                print(f"     {label:28s} P {pilot:5.0f} | 0 {census:5.0f} | 1 {s1:6.0f} | 2a <= {s2a:5.0f} | 2b <= {s2b:5.0f}"
                      f" | total <= {total:6.0f} (wall about {total / 40:.0f} h)")
            print(f"     full factorial, n 8, no extension: {150 * (8 * per_seed + plants):6.0f}")
    print("  Sub-studies, not in the total: RBT-116 about 420 core-h per world point at D = 16 (240 at D = 8; PR #400 r5);")
    print("  RBT-118 per its own design (at n = 20, 1200 seasons, side + merged + half null: about 20 x 15 = 300 per point).")
    print()


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    print("# RBT-129 power.py r2: DESIGN ONLY (no simulator run).  reps =", reps, " rules =", ", ".join(RULES))
    print()
    part_income()
    part_perceive()
    part_budget()
    with Pool(4) as pool:
        part_resolvable(pool, 3 * reps)
        part_checks(pool, reps)
        part_share(pool, reps)
