"""RBT-129 (world sweep) power model, budget and staging arithmetic.  DESIGN ONLY: runs no simulator.

Four parts, each bounded by a floor and a ceiling (R11), with the noise taken from committed data:

  1. income   the per-point H - D income difference (side-by-side, and per member in the merged world).
              Noise: RBT-118's 29 paired histories (pool.txt, probe_terrain.txt): between-history SD of the
              last-100 H - D is 0.144 on random terrain, 0.334 on flat (ceiling).  Reported as a minimum
              detectable effect (MDE) and as the half-width of the UNDECIDED price band around a break-even,
              using the price slope d(H - D)/dp = kJ_D - kJ_H (RBT-118 §4/§4a: about 14-15 kJ a season before
              the fairness set; bounded here by 6 and 15.5 kJ, since effector_bias_sigma and the motor budget
              are expected to cut both bills).
  2. share    the merged-world head-to-head (merge_after = 60, read = mean holistic share of the pooled
              capacity over seasons 240-299).  An independent replica of Ecology.step's demography, adapted
              from runs/RBT-121/adversary/adv_demography.py (same rules: threshold 3, birth cost 1, max age 60,
              initial energy 3, crossover 0.3, gain Poisson(g) - 0.1, living cost 0.25), with two faunas that
              live apart until season 60 and then share 120 slots.  Swept over the regime (resident gross income
              g0), the breeding rule (lottery = committed; energy = RBT-126's candidate), and the income edge.
              A per-seed spread of the edge (tau) stands in for history-to-history variation.
  3. perceive intact - decoy food per seed, from probing M living members on D draws each.  Noise:
              runs/RBT-121/adversary/noise_components.txt (between-member SD 0.563 / 0.212, member x draw SD
              1.469 / 0.945, holistic / designed).
  4. budget   CPU-hours per stage from RBT-105's measured 10.2 s per arm-season at 2 cores (20 core-s),
              bounded above by 25 core-s for the fairness set's settle and the 4 m PW disc.

Multiplicity: every per-point call is made under Benjamini-Hochberg at q = 0.10 within its family.  The BH
threshold for one rejection lies between q/K (only one point rejects) and q (all do); both bounds are printed,
with K = 36 (Stage 1) and K = 72 (Stages 1 + 2).

python3 runs/RBT-129/power.py [reps]   (default reps 600; about 15 minutes)
"""
import math
import sys

import numpy as np

Q = 0.10
K_STAGE1, K_ALL = 36, 72
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


def _season(rng, pop, g_of):
    for p in pop:
        p[1] += rng.poisson(g_of[p[0]]) - WORK - COST
        p[2] += 1
    return [p for p in pop if p[1] > 0 and p[2] < AGE]


def _breed(rng, pop, cap, rule, kinds):
    elig = [p for p in pop if p[1] >= THR and p[0] in kinds]
    rng.shuffle(elig)
    if rule == "energy":
        elig.sort(key=lambda p: -p[1])
    for p in elig:
        if len(pop) >= cap:
            break
        # breeding stays within a fauna (ecology.py); crossover only swaps partners of the same kind: no type change
        p[1] -= BCOST
        pop.append([p[0], BCOST, 0])
    return pop


def merged_history(rng, gH, gD, rule, merge=60, horizon=300, window=(240, 300), cap=60):
    """Two faunas apart for `merge` seasons (60 slots each), then one arena of 2 * cap.  Returns the mean holistic
    share of the pooled capacity over the window, and whether either fauna reached 0."""
    g_of = {0: gD, 1: gH}
    pops = {k: [[k, INIT, int(rng.integers(0, AGE))] for _ in range(cap)] for k in (0, 1)}
    for s in range(merge):
        for k in (0, 1):
            pops[k] = _season(rng, pops[k], g_of)
            pops[k] = _breed(rng, pops[k], cap, rule, (k,))
    pop = pops[0] + pops[1]
    shares = []
    for s in range(merge, horizon):
        pop = _season(rng, pop, g_of)
        pop = _breed(rng, pop, 2 * cap, rule, (0, 1))
        if window[0] <= s < window[1]:
            shares.append(sum(p[0] for p in pop) / (2 * cap))
    fixed = (not any(p[0] == 1 for p in pop)) or (not any(p[0] == 0 for p in pop))
    return float(np.mean(shares)), fixed


def part_share(reps):
    print("## 2. Merged-world head-to-head: holistic share of the 120 pooled slots, mean over seasons 240-299")
    print("#   replica of Ecology.step (see docstring); the null is edge 0 (a relabelled copy of one fauna).")
    print("#   g0 = resident gross income a season; living cost 0.25; saturation is g0 >~ 0.8 (RBT-121 adversary §4).")
    print("#   edge = gH - gD in items a season; tau = per-seed SD of the edge (history-to-history).")
    print("#   columns: mean share, per-seed SD, fixations; then power of the share call (t on share - 0.5) and of TIE")
    print("#   (TOST, margin 0.10) at n = 8 / 12, at BH worst (q/K, K = 36) and BH half (q/2).")
    rng = np.random.default_rng(129)
    out = {}
    for rule in ("lottery", "energy"):
        for g0 in (0.5, 0.8, 1.3):
            for edge in (0.0, 0.05, 0.1, 0.2, 0.4):
                for tau in ((0.0, 0.1) if edge in (0.0, 0.1) else (0.0,)):
                    res = []
                    for _ in range(reps):
                        e = edge + (rng.normal(0, tau) if tau else 0.0)
                        res.append(merged_history(rng, g0 + e / 2, g0 - e / 2, rule))
                    sh = np.array([r[0] for r in res])
                    fx = np.mean([r[1] for r in res])
                    sd = float(sh.std(ddof=1))
                    eff = float(sh.mean() - 0.5)
                    # power by resampling the simulated seeds (a bootstrap of the replica's own distribution)
                    pw = []
                    for n in (8, 12):
                        for alpha in (Q / K_STAGE1, Q / 2):
                            idx = rng.integers(0, reps, size=(4000, n))
                            x = sh[idx] - 0.5
                            t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n) + 1e-12)
                            c = t_crit(alpha, n - 1)
                            if edge == 0.0:
                                call = float(np.mean(np.abs(t) > c))  # false-call rate, either direction
                            else:
                                call = float(np.mean(t > c)) if eff >= 0 else float(np.mean(t < -c))
                            m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n)
                            c2 = t_crit(2 * alpha, n - 1)
                            tie = float(np.mean((m - c2 * se > -0.10) & (m + c2 * se < 0.10)))
                            pw.append(f"{call:.2f}/{tie:.2f}")
                    out[(rule, g0, edge, tau)] = (eff, sd)
                    print(f"  {rule:7s} g0 {g0:.1f} edge {edge:+.2f} tau {tau:.1f}: share {0.5 + eff:.3f} sd {sd:.3f} fix {fx:.2f}"
                          f" | call/tie n8 [{pw[0]}, {pw[1]}] n12 [{pw[2]}, {pw[3]}]", flush=True)
    print()
    return out


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
    print("## 4. Budget (core-hours).  Arm cost 20 core-s per arm-season (RBT-105 measured), ceiling 25.")
    print("#   wall = total / 40 cores (ten 4-core sessions, two arms of different seeds per session at WORKERS=2)")
    for cs in (20.0, 25.0):
        h = lambda seasons: seasons * cs / 3600.0
        side, merged = h(300), h(300)
        null = 0.5 * h(300) * 0.85  # null arms on half the seeds; one fauna cloned (holistic bouts ~0.8x)
        probes = 0.40  # perception (intact/decoy/lesion/motors-off, STEERS staged 4+16+16) + R8 levers, per seed
        per_seed = side + merged + null + probes
        plants = 0.25  # planted positives and negatives per point, not per seed
        census_pt = 3 * h(60)
        pilot = 3 * 4 * per_seed + 3 * plants
        census = 150 * census_pt + 12 * 2.0  # + R4 margins on real bodies at 12 cells, ~2 core-h each
        print(f"  @ {cs:.0f} core-s: per seed-point {per_seed:.2f} (side {side:.2f}, merged {merged:.2f}, null {null:.2f},"
              f" probes {probes:.2f}); census point {census_pt:.2f}")
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


def resolvable(g0, rule, n, reps=400, seed=12906):
    """Section 6.2's check: power, at BH half (q/2), to call a 1.25x income edge at resident gross income g0 under the
    breeding rule, from n seeds of the replica.  A point is RESOLVING when this is >= 0.80.  Run per point after
    Stage 1 with the point's measured g0 (RBT-126 readout, M arm, seasons 180-299, faunas pooled)."""
    rng = np.random.default_rng(seed)
    edge = 0.25 * g0
    sh = np.array([merged_history(rng, g0 + edge / 2, g0 - edge / 2, rule)[0] for _ in range(reps)])
    idx = rng.integers(0, reps, size=(4000, n))
    x = sh[idx] - 0.5
    t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n) + 1e-12)
    return float(np.mean(t > t_crit(Q / 2, n - 1)))


def part_resolvable():
    print("## 5. Resolvability (section 6.2): power to call a 1.25x income edge at q/2, by regime, rule and n")
    for rule in ("lottery", "energy"):
        row = []
        for g0 in (0.4, 0.5, 0.65, 0.8, 1.0, 1.3):
            row.append(f"g0 {g0:.2f}: " + "/".join(f"{resolvable(g0, rule, n, reps=300):.2f}" for n in (8, 16)))
        print(f"  {rule:7s} (n 8/16) " + "  ".join(row), flush=True)
    print()


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    print("# RBT-129 power.py: DESIGN ONLY (no simulator run).  reps =", reps)
    print()
    part_income()
    part_perceive()
    part_budget()
    part_resolvable()
    part_share(reps)
