"""RBT-91 adversary probe: re-derive the decision's magnitude arithmetic on the motif the
encoding can actually hold.

The decision (docs/rbt-91-weight-scale-decision.md) says that because the routed motif reads
``a = 2w`` (RBT-87), ``a = 16`` needs "two coordinated links at |w| >= 8 -- about 4e-4 before
signs even at the asymptote". That is the arithmetic for the motif *as installed*: the install
pins the two nose->interneuron links at +/-1 and puts ``w`` on the two interneuron->effector
links (scripts/genotype_motif.py::install). An *evolved* copy of the same structure has all
four link weights free, and its linearised gain is a product, not a single weight:

    a = (u_L - u_R) * (v_L + v_R) / 2 * sech^2(b)

with ``u`` the nose->interneuron weights, ``v`` the interneuron->effector weights and ``b`` the
interneuron's bias (the tanh slope at the operating point; the nose differential is ~0.056,
RBT-67, so the interneuron sees a small signal and ``sech^2(b)`` is the slope that applies).
So the magnitude a = 16 can be reached by four links at |w| ~ 2.8 as well as by two at 8, and
the decision's figure is one corner of that region.  This probe measures the whole region.

Pure arithmetic on the operator's own scalar process (the decision's section 3, same
construction) and on the committed weights (its section 1); no simulation, no world.

Three measurements:

1. The stationary tail at the thresholds the routed motif actually needs (sqrt(8) = 2.83 per
   link if the four are equal), which the decision's table does not print.
2. P(|a| >= 16) for four weights drawn independently from (i) the operator's stationary
   distribution, (ii) the operator at the runs' realised depth, (iii) the committed bests'
   own weights -- with the bias slope ignored (upper bound) and with it included.
3. The interneuron bias.  ``mutate_weights`` steps biases with no reset and no clamp
   (genetics.py lines 106-108), so unlike weights they have NO stationary distribution:
   variance grows as weight_rate * sigma^2 * depth without bound.  The slope sech^2(b) of a
   tanh interneuron therefore collapses with depth, which is a barrier the decision does not
   name and which runs the opposite way to "run length" from the weight asymptote.

Usage: adversary.py [n_draws]
"""
import glob
import sys

import numpy as np

from rabbitstew.genetics import MutationConfig
from rabbitstew.genotype import Genotype

THRESH = (2.0, 2.83, 4.0, 8.0, 16.0)


def tail_line(label, w):
    w = np.abs(np.asarray(w, float))
    return f"{label:44s} n={len(w):>7}  rms={np.sqrt((w ** 2).mean()):5.3f}  " + "  ".join(
        f">={t:g}: {100 * (w >= t).mean():6.3f}%" for t in THRESH)


def scalar_process(cfg, n, mutations, rng, w0=None):
    """The operator's own scalar weight process (the decision's section 3, same construction)."""
    w = rng.normal(0.0, 1.0, n) if w0 is None else np.array(w0, float)
    for _ in range(mutations):
        touched = rng.random(n) < cfg.weight_rate
        reset = touched & (rng.random(n) < cfg.weight_reset_rate)
        w = np.where(reset, rng.normal(0.0, 1.0, n),
                     w + np.where(touched & ~reset, rng.normal(0.0, cfg.weight_sigma, n), 0.0))
    return w


def bias_process(cfg, n, mutations, rng, b0=None):
    """The operator's bias process: a step with no reset (genetics.py 106-108)."""
    b = np.zeros(n) if b0 is None else np.array(b0, float)
    for _ in range(mutations):
        touched = rng.random(n) < cfg.weight_rate
        b = b + np.where(touched, rng.normal(0.0, cfg.weight_sigma, n), 0.0)
    return b


def routed_gain(pool, rng, n, bias=None):
    """|a| for four weights drawn independently from ``pool`` (signs as drawn), optionally
    times the tanh slope at a bias drawn from ``bias``."""
    uL, uR, vL, vR = (rng.choice(pool, n) for _ in range(4))
    a = np.abs((uL - uR) * (vL + vR) / 2.0)
    if bias is not None:
        a = a / np.cosh(rng.choice(bias, n)) ** 2
    return a


def gain_line(label, a):
    return f"{label:44s} P(|a|>=16) = {100 * (a >= 16).mean():8.4f}%   P(|a|>=32) = {100 * (a >= 32).mean():8.4f}%   median |a| = {np.median(a):6.3f}"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    cfg = MutationConfig()
    rng = np.random.default_rng(20260919)

    print("# RBT-91 adversary: the routed motif's magnitude is a product of four weights and a slope\n")
    print("  a = (u_L - u_R)(v_L + v_R)/2 * sech^2(b); the install fixes u = +/-1 and reads a = 2w (RBT-87).")
    print("  Evolved copies have u, v and b free.  Everything below is the operator's own process or the")
    print("  committed weights; nothing is simulated.\n")

    # --- committed weights and biases (the decision's census population) --------------------
    paths = sorted(glob.glob("runs/**/best_gen*.json", recursive=True))
    gs = [Genotype.load(p) for p in paths]
    evolved_w = np.array([l.weight for g in gs for _, br in g.brains() for l in br.links])
    evolved_b = np.array([u.bias for g in gs for _, br in g.brains() for u in br.units if u.kind != "sensor"])
    print(f"## 1. Tails at the thresholds the routed motif needs ({len(paths)} committed bests, {len(evolved_w)} links)\n")
    print(tail_line("committed bests (as evolved)", evolved_w))
    w_d20 = scalar_process(cfg, n, 20, rng)
    print(tail_line("operator from N(0,1), 20 mutations (realised depth)", w_d20))
    w_inf = scalar_process(cfg, n, 2000, rng)
    print(tail_line("operator asymptote (2,000 mutations)", w_inf))
    print("  (2.83 = sqrt(8): four equal links at 2.83 give a = 2 * 2.83^2 = 16; the decision's table stops at >=2 and >=4.)\n")

    # --- the four-weight gain ------------------------------------------------------------------
    print("## 2. P(|a| >= 16) for four independent weights, bias slope ignored (an upper bound on the magnitude barrier)\n")
    p8 = (np.abs(w_inf) >= 8).mean()
    print(f"  the decision's figure: two links at |w| >= 8, asymptote: {p8:.4f}^2 = {100 * p8 ** 2:.4f}%  (u pinned at +/-1)")
    a_inf = routed_gain(w_inf, rng, n)
    a_d20 = routed_gain(w_d20, rng, n)
    a_ev = routed_gain(evolved_w, rng, n)
    print(gain_line("four free weights, asymptote", a_inf))
    print(gain_line("four free weights, depth 20 from N(0,1)", a_d20))
    print(gain_line("four free weights, committed bests' distribution", a_ev))
    print("  Signs are as drawn, so these count anti-compasses too; the correctly signed fraction is half of each (the sign of a is one bit).\n")

    # --- the bias --------------------------------------------------------------------------------
    print("## 3. The interneuron bias has no stationary distribution; the tanh slope collapses with depth\n")
    print(f"  bias step: p = {cfg.weight_rate}, sigma = {cfg.weight_sigma}, no reset, no clamp  =>  var(b) = {cfg.weight_rate * cfg.weight_sigma ** 2:.3f} * depth")
    print(f"  committed bests' non-sensor units ({len(evolved_b)}): median |b| {np.median(np.abs(evolved_b)):.3f}, p90 {np.percentile(np.abs(evolved_b), 90):.3f}, max {np.abs(evolved_b).max():.3f}; median slope sech^2(b) {np.median(1 / np.cosh(evolved_b) ** 2):.3f}")
    print(f"  {'depth':>8s}  {'sd(b) predicted':>16s}  {'sd(b) measured':>15s}  {'median sech^2(b)':>17s}  {'P(slope >= 0.5)':>15s}")
    for d in (20, 50, 200, 1000, 2000):
        b = bias_process(cfg, n, d, rng)
        slope = 1 / np.cosh(b) ** 2
        print(f"  {d:8d}  {np.sqrt(cfg.weight_rate * cfg.weight_sigma ** 2 * d):16.3f}  {b.std():15.3f}  {np.median(slope):17.3f}  {100 * (slope >= 0.5).mean():14.1f}%")
    print()
    print("## 4. P(|a| >= 16) with the slope included, four weights and a bias at the same depth\n")
    for d, w in ((20, w_d20), (2000, w_inf)):
        b = bias_process(cfg, n, d, rng)
        print(gain_line(f"four free weights + bias, depth {d}", routed_gain(w, rng, n, bias=b)))
    print(gain_line("committed bests' weights + their biases", routed_gain(evolved_w, rng, n, bias=evolved_b)))
    print("\n  Read: the weight asymptote makes the magnitude easier with depth (section 2); the bias walk makes")
    print("  the slope harder with depth (section 3).  Which wins is section 4.  Selection on the bias is not")
    print("  in this arithmetic and is the caveat against it: the committed bests' biases are what selection left.")


if __name__ == "__main__":
    main()
