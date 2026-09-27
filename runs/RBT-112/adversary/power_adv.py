"""RBT-112 design adversary: an independent power model in which the genealogy is not fixed but made by the
same selection that acts on the compass (the design's §6.3 takes n from part 2's neutral genealogy, or fixes n = 40).

Model (discrete generations; one generation = one birth along a lineage, the baseline's "depth"):
  * N = 60 designed-body individuals; generation 0 is 30 planted founders (carrying a paying compass) and 30 bare.
  * Each generation a uniform breeding pool of M is drawn (the drift), and each of the 60 children takes its parents[0]
    from the pool with weight 1 + s if that breeder carries a paying compass, else 1 (the selection; so the expected
    carrier share follows the design's x(1 + s)/(1 + s x)).  The root (planted-rooted or not) follows parents[0], as
    held.py roots genomes.
  * Crossover as the ecology's designed-body operator: with probability 0.3 a child has a mate (drawn as parents[0] is),
    and with probability 0.5 it takes the mate's global brain, i.e. the mate's compass state (crossover_controller).
  * Mutation: a paying compass is lost with probability u per birth (erasure.txt: 0.282 default, 0.089 at S = 0);
    a lost compass never returns (the tables are monotone to the third decimal).
  * Readings at depth D300 = 10 and D599 = 19 (genealogy.txt's mean depths, 9.9 and 18.8): k_planted = paying
    among planted-rooted, n = planted-rooted, mu = the operator's pooled no-selection table at that depth (baseline/),
    B = binom_q95(n, mu) (RBT-104 peek.py's), HELD iff k_planted > B at both readings (RBT-106 §10.2).
  * M (the breeding pool, i.e. the drift) is calibrated at s = 0 to part 2's neutral genealogy: the spread of the
    planted-rooted share at seasons 300 and 599 over the ten seeds (genealogy.txt), and the design's measured nulls
    (1.0% default, 1.5% S = 0) are printed beside the model's.
Then per s: q_U, q_Z, the probability that the planted roots are all lost by 599, and the verdict layer over ten
(and twenty) seeds, including the gating premise, under the registered rule and alternatives.

Usage: power_adv.py > power_adv.txt      (numpy only; no scipy)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("RBT112_BASELINE", os.path.join(HERE, "..", "baseline"))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
U = {"U": 0.282, "Z": 0.089}
D300, D599 = 10, 19
N, HALF = 60, 30
REPS = int(os.environ.get("REPS", "4000"))
GEN = {801: (37, 11), 804: (40, 48), 805: (8, 10), 806: (45, 60), 807: (0, 0), 1: (42, 55), 2: (3, 0), 3: (3, 0), 4: (50, 52), 7: (7, 6)}


def pooled(tag):
    num, den = {}, {}
    for s in SEEDS:
        head = None
        for line in open(os.path.join(BASE, f"baseline-w32{tag}-{s}.txt")):
            if line.startswith("# depth"):
                head = line[2:].split()
            elif not line.startswith("#"):
                r = dict(zip(head, line.split()))
                d = int(r["depth"])
                num[d] = num.get(d, 0) + int(r["pay32"])
                den[d] = den.get(d, 0) + int(r["lineages"]) if "lineages" in r else den.get(d, 0)
    return num, den


def table(tag):
    """Pooled pay32 fraction by depth, read by column name."""
    out = {}
    tot = {}
    for s in SEEDS:
        head = None
        for line in open(os.path.join(BASE, f"baseline-w32{tag}-{s}.txt")):
            if line.startswith("# depth"):
                head = line[2:].split()
            elif not line.startswith("#") and head:
                r = dict(zip(head, line.split()))
                d = int(r["depth"])
                out[d] = out.get(d, 0.0) + float(r["pay32_frac"])
                tot[d] = tot.get(d, 0) + 1
    return {d: out[d] / tot[d] for d in out}


def binom_q95(n, mu):
    acc = 0.0
    for c in range(n + 1):
        acc += math.comb(n, c) * mu ** c * (1 - mu) ** (n - c)
        if acc >= 0.95:
            return c
    return n


MU = {"U": table(""), "Z": table("-S0")}
BQ = {op: {d: np.array([binom_q95(n, MU[op][d]) if n else 0 for n in range(N + 1)]) for d in (D300, D599)} for op in MU}


def simulate(s, u, M, rng, reps=REPS, op="Z"):
    """Returns per replicate: (n300, k300, n599, k599, kbare599)."""
    planted = np.zeros((reps, N), bool)
    planted[:, :HALF] = True
    pay = planted.copy()
    out = {}
    for g in range(1, D599 + 1):
        rows = np.arange(reps)[:, None]
        # drift: a uniform breeding pool of M; selection: each child picks its parents[0] among the breeders with weight
        # 1 + s for a paying carrier (with replacement), so E[x'] = x(1 + s)/(1 + s x) as in the design's recursion
        breeders = np.argsort(rng.random((reps, N)), axis=1)[:, :M]
        w = 1.0 + s * pay[rows, breeders]
        cw = np.cumsum(w, 1)
        pick = lambda: breeders[rows, ((rng.random((reps, N)) * cw[:, -1:])[..., None] > cw[:, None, :]).sum(-1).clip(0, M - 1)]
        p0 = pick()
        mate = pick()
        take = (rng.random((reps, N)) < 0.3) & (rng.random((reps, N)) < 0.5)
        rows = np.arange(reps)[:, None]
        new_planted = planted[rows, p0]
        new_pay = np.where(take, pay[rows, mate], pay[rows, p0])
        new_pay &= rng.random((reps, N)) >= u
        planted, pay = new_planted, new_pay
        if g in (D300, D599):
            n = planted.sum(1)
            k = (planted & pay).sum(1)
            kb = (~planted & pay).sum(1)
            out[g] = (n, k, kb, k > BQ[op][g][n], pay.sum(1))
    return out


def calibrate(rng):
    target = np.array([GEN[s][1] for s in SEEDS]) / N
    t3 = np.array([GEN[s][0] for s in SEEDS]) / N
    print("## Calibration of the breeding pool M at s = 0 (part 2's neutral genealogy, genealogy.txt)\n")
    print(f"part 2: planted-rooted share at 300: mean {t3.mean():.2f}, sd {t3.std(ddof=1):.2f}, seeds with 0: {int((t3 == 0).sum())}/10; "
          f"at 599: mean {target.mean():.2f}, sd {target.std(ddof=1):.2f}, seeds with 0: {int((target == 0).sum())}/10\n")
    print("| M | share sd at 300 | share sd at 599 | P(no planted root at 599) | model null, default operator | model null, S = 0 operator |")
    print("|---|---|---|---|---|---|")
    best, bd, bestn, bdn = None, 9, None, 9
    for M in (6, 8, 10, 12, 15, 20, 30, 40, 50, 60):
        o = simulate(0.0, U["Z"], M, rng, op="Z")
        ou = simulate(0.0, U["U"], M, rng, op="U")
        sd3 = (o[D300][0] / N).std()
        sd = (o[D599][0] / N).std()
        p0 = (o[D599][0] == 0).mean()
        nz = (o[D300][3] & o[D599][3]).mean()
        nu = (ou[D300][3] & ou[D599][3]).mean()
        print(f"| {M} | {sd3:.2f} | {sd:.2f} | {p0:.2f} | {nu:.2%} | {nz:.2%} |")
        dist = abs(sd - target.std(ddof=1)) + abs(sd3 - t3.std(ddof=1))
        if dist < bd:
            best, bd = M, dist
        if abs(nz - 0.015) < bdn:
            bestn, bdn = M, abs(nz - 0.015)
    print(f"\nfitted M = {best} (closest share spread at 300 and 599); M = {bestn} matches the measured S = 0 null (1.5%, 3/200; default 1.0%, 2/200)."
          " No single M fits both: part 2's roots drift like M ~ 15, while its compass clades are less overdispersed than the"
          " model's (the model's null at M = 15 is ~3x the measured one), so small-s power in the M = 15 rows is partly the model's own false positives\n")
    return best, bestn


def pois_binom_ge(q, k):
    """P(sum of Bernoulli(q_i) >= k)."""
    dist = np.zeros(len(q) + 1)
    dist[0] = 1.0
    for p in q:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return dist[k:].sum(), dist


def main():
    rng = np.random.default_rng(1120)
    print("# RBT-112 design adversary: power with a genealogy made by the same selection (power_adv.py)\n")
    print(f"tables: {BASE}; u default {U['U']}, S = 0 {U['Z']}; readings at depth {D300} and {D599}; {REPS} replicates per cell\n")
    M, Mn = calibrate(rng)
    for Mx in (M, Mn):
        print(f"## M = {Mx}{' (fitted to the genealogy spread)' if Mx == M else ' (fitted to the measured null)'}\n")
        nz0 = simulate(0.0, U["Z"], Mx, rng, reps=20000, op="Z")
        thr = {g_: np.quantile(nz0[g_][4], 0.95) for g_ in (D300, D599)}
        both0 = ((nz0[D300][4] > thr[D300]) & (nz0[D599][4] > thr[D599])).mean()
        print(f"HELD-ALL (checked, not proposed: no better than the registered call here): all carriers k_all = k_planted + k_bare above the 95th percentile of the arm's own full-operator null at both "
              f"readings (here the model's: {thr[D300]:.0f} and {thr[D599]:.0f} of 60); its per-seed null {both0:.3f}; count rule >= 4 of 10 "
              f"(null {sum(math.comb(10, j) * both0 ** j * (1 - both0) ** (10 - j) for j in range(4, 11)):.1e})\n")
        print("| s | q_U | q_Z | n599 HZ mean (P lost) | x599 HZ | P(#HU<=1) | P(#HU<=2) | registered SUPPORTED given #HU<=2 | alt: #HZ-#HU>=3 given #HU<=2 | FALSIFIED (#HZ<=1) given #HU<=2 | 20 HZ seeds: #HZ>=6 of 20 | HELD-ALL q_Z | HELD-ALL >= 4 of 10 | x_all599 HZ |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s in (0.0, 0.05, 0.089, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0):
            oz = simulate(s, U["Z"], Mx, rng, op="Z")
            ou = simulate(s, U["U"], Mx, rng, op="U")
            hz = oz[D300][3] & oz[D599][3]
            hu = ou[D300][3] & ou[D599][3]
            qz, qu = hz.mean(), hu.mean()
            # ten independent seeds each; joint over (HU count, HZ count)
            B = 200000
            cu = rng.binomial(10, qu, B)
            cz = rng.binomial(10, qz, B)
            gate = cu <= 2
            reg = ((cz >= 5) & (cz - cu >= 3))[gate].mean() if gate.any() else float("nan")
            alt = ((cz - cu) >= 3)[gate].mean() if gate.any() else float("nan")
            fal = (cz <= 1)[gate].mean() if gate.any() else float("nan")
            c20 = rng.binomial(20, qz, B)
            n599 = oz[D599][0]
            x599 = (oz[D599][1][n599 > 0] / n599[n599 > 0]).mean() if (n599 > 0).any() else float("nan")
            qa = ((oz[D300][4] > thr[D300]) & (oz[D599][4] > thr[D599])).mean()
            ca = rng.binomial(10, qa, B)
            print(f"| {s:.3f} | {qu:.3f} | {qz:.3f} | {n599.mean():.1f} ({(n599 == 0).mean():.2f}) | {x599:.2f} | {(cu <= 1).mean():.2f} | "
                  f"{gate.mean():.2f} | {reg:.3f} | {alt:.3f} | {fal:.3f} | {(c20 >= 6).mean():.3f} | {qa:.3f} | {(ca[gate] >= 4).mean():.3f} | {oz[D599][4].mean() / N:.2f} |")
        print()
    # nulls of the alternative rules, at the measured per-seed rate and its upper 95% bound (3/200 -> 4.3%)
    print("## The null of the counts, per-seed false-positive rate q0 (measured 3/200 = 1.5%; exact 95% upper bound 4.3%)\n")
    print("| q0 | P(#HZ >= 5 of 10) | P(#HZ >= 3 of 10) | P(#HZ >= 6 of 20) | P(#HZ >= 5 of 20) |")
    print("|---|---|---|---|---|")
    for q0 in (0.015, 0.043, 0.08):
        f = lambda n, k: sum(math.comb(n, j) * q0 ** j * (1 - q0) ** (n - j) for j in range(k, n + 1))
        print(f"| {q0} | {f(10, 5):.2e} | {f(10, 3):.2e} | {f(20, 6):.2e} | {f(20, 5):.2e} |")


if __name__ == "__main__":
    main()
