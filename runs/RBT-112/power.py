"""RBT-112: matched-null power of the arm's verdicts (PREREGISTRATION.md §6.3), re-derived.

The design adversary's rough figures (RBT-104 readout adversary §5.1(i)) were ">= 0.95 for >= 5/10 primary FD if H
holds under S = 0" and "0.6-0.8 on ATTRIBUTION".  They assumed that every seed holds the compass at mutation-selection
balance 1 - u/s = 0.84.  Here the chain is modelled in four layers, from committed numbers only, with no scipy.

LAYER 0, the null (measured, not modelled): the false-positive rate of HELD (k_planted > B at both 300 and 599) under
  the arm's own operator with crossover on part 2's ten real genealogies: null/xnull-w32-S0-SEED.txt (S = 0) and
  null/xnull-w32-SEED.txt (the default, which reproduces the RBT-106 adversary's).  Parsed with the adversary's
  pool_xnull.parse, scored as amended (k_planted = k - k_bare).

LAYER 1, HELD on one seed, given a selective advantage s per generation of a paying compass-signed carrier.
  * The carrier share among the planted-rooted living follows mutation-selection: x' = x(1 + s)(1 - u) / (1 + s x),
    with x0 = 1.  u is the operator's measured loss (erasure.txt: 0.282 by default, 0.089 at S = 0).
  * The planted-rooted living, n, and their depth d at seasons 300 and 599 are part 2's real genealogy, per seed
    (genealogy.txt).  This is the null's own genealogy, so no selection has thinned or grown n.
  * k_planted ~ BetaBinomial(n, x(d), rho): the living are clustered by descent.  rho is calibrated so that at s = 0
    the model's two-season false-positive rate matches layer 0's.  It is printed, with rho = 0 and 0.6 beside it.
  * HELD at a season iff k_planted > B = binom_q95(n, mu(d)), with mu from the operator's own table (baseline/).
    Both seasons must read HELD, taken as independent given x.
  * q(s) is the mean over the ten seeds' (n, d) of P(HELD at both).

LAYER 2, the HELD verdicts over n_usable seeds (Poisson-binomial over the per-seed q):
  SUPPORTED iff #HELD(HZ) >= 5 and #HELD(HZ) - #HELD(HU) >= 3;  FALSIFIED iff #HELD(HZ) <= 1.
  #HELD(HU) is known at launch: the arm runs only if RBT-106's H read the compass not held.  So SUPPORTED's power is
  P(#HELD(HZ) >= max(5, #HELD(HU) + 3)), printed for #HELD(HU) = 0, 1, 2, 3.

LAYER 3, function per line (readout (b) as RBT-106 §10.4 counts it, patchy-scored; uniform beside it).  Seven bodies
  per line, each a working-compass carrier with probability p:
  * a carrier body's (gain, retained decoy) is drawn from the a = 64 install control's committed seven per-body rows:
    patchy runs/RBT-106/controls/function-patchy-801.txt, uniform runs/RBT-104/function-controls-801.txt;
  * a non-carrier body has gain 0 and F ~ N(0.10, 0.20) (RBT-106 power.py's bare body);
  * zero counts are binomial over 64 seeds at each class's committed zero fraction.
  The primary call is FD iff the t(6) interval of F is above 0 and the zero veto passes.  The ATTRIBUTION call (a
  COMPASS line) is FD iff the primary is FD, the gain's t(6) interval is above 0, the decoy retains < 25% of the
  mean gain, and gain - decoy excludes 0.  Both are function.py's rules.
  Then the counts over ten seeds, with a seed's champions carrying at p_held (share x at the window, or 6/7 if the
  bests are enriched for carriers) when the seed HOLDS, and at 1/7 when it does not.

Usage: power.py > power.txt
"""
import importlib.util
import math
import os
import re
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


px = _load("rbt106_pool_xnull_p", os.path.join(_ROOT, "runs", "RBT-106", "adversary", "pool_xnull.py"))
peek = _load("rbt104_peek_p", os.path.join(_ROOT, "runs", "RBT-104", "peek.py"))

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
U = {"default": 0.282, "S0": 0.089}          # erasure.txt, primary u(8), pooled
TAB = {"default": "baseline-w32-{}.txt", "S0": "baseline-w32-S0-{}.txt"}
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
SUPPORT_MIN, SUPPORT_GAP, FEW = 5, 3, 1
# a = 64 install control, per body (gain = intact - lesioned, retained decoy = rotated - lesioned), seven bodies each
PATCHY = dict(gain=[1.469, 3.734, 2.281, 4.641, 4.234, 1.438, 0.469], dec=[-0.234, 0.266, -0.016, 0.531, 0.469, -0.172, -0.469],
              z_pos=135 / 448, z_neg=275 / 448)       # runs/RBT-106/controls/function-patchy-801.txt
UNIFORM = dict(gain=[0.891, 0.578, 0.875, 0.672, 0.578, 1.578, 0.859], dec=[0.172, -0.094, 0.172, 0.281, 0.125, 0.453, 0.344],
               z_pos=129 / 448, z_neg=213 / 448)      # runs/RBT-104/function-controls-801.txt
rng = np.random.default_rng(112)


def table(op, seed):
    head, p = None, {}
    for line in open(os.path.join(_HERE, "baseline", TAB[op].format(seed))):
        if line.startswith("# depth"):
            head = line[2:].strip().split("\t")
        elif not line.startswith("#"):
            r = dict(zip(head, line.split()))
            p[int(r["depth"])] = float(r["pay32_frac"])
    return p


def genealogy(n_fixed=None):
    """(n, depth) per (seed, season) from genealogy.txt.  n_fixed replaces n (depth kept; where the genealogy has
    no planted-rooted genome, the mean depth of the other seeds at that season): the optimistic scenario in
    which selection keeps n planted-rooted genomes alive, as H0's gate saw (n = 41 and 48 at season 150)."""
    g = {}
    for line in open(os.path.join(_HERE, "genealogy.txt")):
        if line.startswith("#") or line.startswith("seed"):
            continue
        s, season, living, n, d = line.split()
        g[(int(s), int(season))] = (int(n), float(d))
    if n_fixed is not None:
        for season in (150, 300, 599):
            md = float(np.nanmean([g[(s, season)][1] for s in SEEDS]))
            for s in SEEDS:
                d = g[(s, season)][1]
                g[(s, season)] = (n_fixed, d if np.isfinite(d) else md)
    return g


def null_rate(tag):
    rows = []
    for s in SEEDS:
        rows += px.parse(os.path.join(_HERE, "null", f"xnull-w32{tag}-{s}.txt"))["x"]
    held = [[c["k"] - c["kb"] > c["B"] for c in r] for r in rows]
    both = sum(h[1] and h[2] for h in held)
    gate = sum(h[0] for h in held)
    return both, len(held), gate


def betabinom_sf(k, n, x, rho):
    """P(K > k) for K ~ BetaBinomial(n, mean x, intra-class correlation rho); rho = 0 is the binomial."""
    x = min(max(x, 1e-12), 1 - 1e-12)
    if rho <= 0:
        return sum(math.comb(n, j) * x ** j * (1 - x) ** (n - j) for j in range(k + 1, n + 1))
    ab = (1 - rho) / rho
    a, b = x * ab, (1 - x) * ab
    lbeta = lambda p, q: math.lgamma(p) + math.lgamma(q) - math.lgamma(p + q)
    return sum(math.exp(math.log(math.comb(n, j)) + lbeta(j + a, n - j + b) - lbeta(a, b)) for j in range(k + 1, n + 1))


def x_of(d, s, u):
    if not np.isfinite(d):
        return float("nan")
    x = 1.0
    for _ in range(int(round(d))):
        x = x * (1 + s) * (1 - u) / (1 + s * x)
    return x


def q_seed(seed, s, op, rho, G):
    tab = table(op, seed)
    p = 1.0
    for season in (300, 599):
        n, d = G[(seed, season)]
        if n == 0:
            return 0.0   # no planted-rooted genome alive: HELD cannot fire
        mu = tab[min(int(round(d)), 40)]
        B = peek.binom_q95(n, mu)
        p *= betabinom_sf(B, n, x_of(d, s, U[op]), rho)
    return p


def poibin(qs):
    """P(count = j) for independent Bernoullis with probabilities qs."""
    dist = np.zeros(len(qs) + 1)
    dist[0] = 1.0
    for q in qs:
        dist[1:] = dist[1:] * (1 - q) + dist[:-1] * q
        dist[0] *= 1 - q
    return dist


def line_calls(p, W, n=40000):
    """(P(primary FD), P(COMPASS line)) for a line whose seven bodies each carry with probability p."""
    carry = rng.random((n, 7)) < p
    idx = rng.integers(0, 7, (n, 7))
    gain = np.where(carry, np.asarray(W["gain"])[idx], 0.0)
    fbare = rng.normal(0.10, 0.20, (n, 7))
    dec = np.where(carry, np.asarray(W["dec"])[idx], -fbare)
    F = gain - dec
    z = rng.binomial(64, np.where(carry, W["z_pos"], W["z_neg"])).sum(1)
    t = T975[6]
    lo = lambda v: v.mean(1) - t * v.std(1, ddof=1) / math.sqrt(7)
    hi = lambda v: v.mean(1) + t * v.std(1, ddof=1) / math.sqrt(7)
    prim = (lo(F) > 0) & (z <= 7 * 64 / 2)
    mg = gain.mean(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        frac = np.where(np.abs(mg) > 1e-9, dec.mean(1) / mg, np.nan)
    comp = prim & (lo(gain) > 0) & (frac < 0.25) & ((lo(F) > 0) == (hi(F) > 0))
    return float(prim.mean()), float(comp.mean())


def main():
    G = genealogy()
    print("# RBT-112: matched-null power, re-derived (PREREGISTRATION.md §6.3); every input a committed file\n")
    print("## Layer 0: the measured null (the arm's operator with crossover, part 2's ten genealogies, 20 replicates each; amended rule)\n")
    nb = {}
    for tag, name in (("", "default (RBT-106's H operator)"), ("-S0", "S = 0 (the arm's operator)")):
        both, tot, gate = null_rate(tag)
        nb[tag] = both / tot
        print(f"  {name}: HELD at 300 and 599 in {both}/{tot} = {100 * both / tot:.1f}%; at 150 alone {gate}/{tot} = {100 * gate / tot:.1f}%")
    r0 = nb["-S0"]
    print(f"  P(SUPPORTED's count, #HELD(HZ) >= {SUPPORT_MIN} of 10 | no selection, S = 0) = "
          f"{float(poibin([r0] * 10)[SUPPORT_MIN:].sum()):.2e}; P(FALSIFIED's count <= {FEW}) = {float(poibin([r0] * 10)[:FEW + 1].sum()):.3f}")
    print("\n## The genealogy (genealogy.txt): planted-rooted living n and mean depth d at 300 / 599\n")
    print("  " + "; ".join(f"{s}: {G[(s, 300)][0]}/{G[(s, 300)][1]:.1f}, {G[(s, 599)][0]}/{G[(s, 599)][1]:.1f}" for s in SEEDS))
    print("\n## Calibrating rho: the model at s = 0 against layer 0's measured two-season rate\n")
    rho_fit = {}
    for op, tag in (("default", ""), ("S0", "-S0")):
        best = None
        for rho in (0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
            m = float(np.mean([q_seed(s, 0.0, op, rho, G) for s in SEEDS]))
            print(f"  {op}: rho {rho:.2f} -> model null {100 * m:.2f}% (measured {100 * nb[tag]:.1f}%)")
            if best is None or abs(m - nb[tag]) < abs(best[1] - nb[tag]):
                best = (rho, m)
        rho_fit[op] = best[0]
    rho = rho_fit["S0"]
    print(f"  fitted: default {rho_fit['default']:.2f}, S0 {rho_fit['S0']:.2f}.  Used below: rho = {rho:.2f}, the fit to the arm's own")
    print("  operator (at the default the model cannot reach the measured 1.0% at any rho: the real null's excess there")
    print("  comes from clades the model does not have), with rho = 0 and 0.6 beside it")
    for scen, GG in (("GENEALOGY: n and depth as part 2's genealogy has them (4 seeds have no planted-rooted genome at 599)", G),
                     ("n = 40: every seed keeps 40 planted-rooted genomes at 300 and 599 (selection keeps planted roots alive)", genealogy(40))):
        print(f"\n# Scenario {scen}")
        scenario(GG, rho)


def scenario(G, rho):
    print("\n## Layer 1: P(a seed reads HELD at 300 and 599 | s), per operator (mean over the ten seeds' genealogy)\n")
    print("| s | x at window, default / S = 0 | q_U (default operator), rho 0 / fit / 0.6 | **q_Z (S = 0)**, rho 0 / fit / 0.6 |")
    print("|---|---|---|---|")
    grid = (0.0, 0.05, 0.089, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0)
    Q = {}
    dwin = float(np.nanmean([G[(s, 599)][1] for s in SEEDS]))
    for s_ in grid:
        qu = [float(np.mean([q_seed(sd, s_, "default", r, G) for sd in SEEDS])) for r in (0.0, rho, 0.6)]
        qz = [float(np.mean([q_seed(sd, s_, "S0", r, G) for sd in SEEDS])) for r in (0.0, rho, 0.6)]
        Q[s_] = ([q_seed(sd, s_, "default", rho, G) for sd in SEEDS], [q_seed(sd, s_, "S0", rho, G) for sd in SEEDS])
        print(f"| {s_:.3f} | {x_of(dwin, s_, U['default']):.3f} / {x_of(dwin, s_, U['S0']):.3f} | "
              f"{qu[0]:.3f} / {qu[1]:.3f} / {qu[2]:.3f} | **{qz[0]:.3f} / {qz[1]:.3f} / {qz[2]:.3f}** |")
    print(f"\n(x at the window: the carrier share at the ten seeds' mean depth at 599, d = {dwin:.1f})")
    print("\n## Layer 2: the HELD verdicts at rho fit, n = 10 usable seeds (n = 7 in brackets)\n")
    print("| s | E#HELD(HU) | P(#HELD(HU) <= 1) (the gating premise) | P(SUPPORTED) at #HELD(HU) = 0 / 1 / 2 / 3 | P(FALSIFIED: #HELD(HZ) <= 1) |")
    print("|---|---|---|---|---|")
    for s_ in grid:
        qu, qz = Q[s_]
        du, dz = poibin(qu), poibin(qz)
        dz7 = poibin(qz[:7])
        sup = [float(dz[max(SUPPORT_MIN, h + SUPPORT_GAP):].sum()) for h in (0, 1, 2, 3)]
        sup7 = [float(dz7[max(SUPPORT_MIN, h + SUPPORT_GAP):].sum()) for h in (0, 1, 2, 3)]
        print(f"| {s_:.3f} | {sum(qu):.2f} | {float(du[:2].sum()):.3f} | " + " / ".join(f"{a:.3f} ({b:.3f})" for a, b in zip(sup, sup7))
              + f" | {float(dz[:FEW + 1].sum()):.3f} ({float(dz7[:FEW + 1].sum()):.3f}) |")
    print("\n## Layer 3: function per line, P(primary FD) / P(COMPASS line), seven bodies each carrying with probability p\n")
    print("| p | patchy-scored (the primary scoring) | uniform-scored |")
    print("|---|---|---|")
    LC = {}
    for p in (0.0, 1 / 7, 2 / 7, 3 / 7, 4 / 7, 5 / 7, 6 / 7, 1.0):
        a, b = line_calls(p, PATCHY), line_calls(p, UNIFORM)
        LC[round(p, 4)] = a
        print(f"| {p:.2f} | {a[0]:.3f} / {a[1]:.3f} | {b[0]:.3f} / {b[1]:.3f} |")
    print("\n## Layer 3 over ten seeds (patchy-scored): P(>= 3 COMPASS lines) (FUNCTION FOLLOWS's count), "
          "P(>= 5 primary FD) (the adversary's figure), P(<= 1 COMPASS line)\n")
    print("| s | q_Z | champions carrying when held: x at window / enriched 6/7 | P(COMPASS >= 3) | P(primary FD >= 5) | P(COMPASS <= 1) |")
    print("|---|---|---|---|---|---|")
    for s_ in (0.0, 0.089, 0.12, 0.15, 0.2, 0.3, 0.5, 1.0):
        qz = Q[s_][1]
        xw = x_of(dwin, s_, U["S0"])
        out = []
        for ph in (xw, 6 / 7):
            pc_h = line_calls(ph, PATCHY)
            pc_n = LC[round(1 / 7, 4)]
            prim = [q * pc_h[0] + (1 - q) * pc_n[0] for q in qz]
            comp = [q * pc_h[1] + (1 - q) * pc_n[1] for q in qz]
            out.append((float(poibin(comp)[3:].sum()), float(poibin(prim)[5:].sum()), float(poibin(comp)[:2].sum())))
        print(f"| {s_:.3f} | {np.mean(qz):.3f} | {xw:.2f} / 0.86 | {out[0][0]:.3f} / {out[1][0]:.3f} | {out[0][1]:.3f} / {out[1][1]:.3f} | "
              f"{out[0][2]:.3f} / {out[1][2]:.3f} |")
    print("\nThe adversary's case (every seed holds at balance, p = 6/7):  P(primary FD) per line "
          f"{LC[round(6 / 7, 4)][0]:.3f}, P(COMPASS) {LC[round(6 / 7, 4)][1]:.3f};  over ten seeds P(primary FD >= 5) "
          f"{float(poibin([LC[round(6 / 7, 4)][0]] * 10)[5:].sum()):.3f}, P(COMPASS >= 5) {float(poibin([LC[round(6 / 7, 4)][1]] * 10)[5:].sum()):.3f}, "
          f"P(COMPASS >= 3) {float(poibin([LC[round(6 / 7, 4)][1]] * 10)[3:].sum()):.3f}")


if __name__ == "__main__":
    main()
