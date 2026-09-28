"""RBT-132 item 5: the power of RBT-129's probe calls at τ = 2 s, beside τ = 1 s (exact binomial; no simulation).

    python runs/RBT-116/probe_power.py > runs/RBT-116/probe_power.txt      (also writes probe_power.json)

The confirmed-share priors are the design-stage caricature's (``design-adversary/tau_probe.txt``, r5's PW caricature
and call): two-nose steerer 0.48 at τ 1 s, 0.40 at τ 2 s; one-nose 0.32 and 0.24; the single-battery PASS shares
0.64 / 0.52 (two-nose) and 0.52 / 0.44 (one-nose).  They are priors: every rate is measured per point by the planted
set (K3) and the founders (K5).

The calls (RBT-129 §6.3, §5.5):
1. **PERCEIVES' STEERS clause**, per fauna and point: the pooled count of confirmed STEERS members over the point's
   seeds (N = 80 at the pilot's 4 seeds × 20; 160 at 8) must exceed the upper 95% binomial bound of the count the
   founders' own confirmed false-STEERS rate predicts.  The founders are N members too, so their rate is estimated
   (Binomial(N, EPS)); the evolved count is Binomial(N, q·SENS + (1 − q)·EPS), q the share of members that truly
   steer.  Power = P(evolved count > the bound), exactly, summed over both.
2. **K3's false-VOID rate** (the planted positives): of 8 (a) and 8 (c) plants, ≥ 4 pooled are seen (veto, ΔT bound,
   SMELL-USE or STEERS) with ≥ 1 of each; a plant is seen at least at its single-battery PASS share.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRIORS = {1.0: {"two": 0.48, "one": 0.32, "pass_two": 0.64, "pass_one": 0.52},
          2.0: {"two": 0.40, "one": 0.24, "pass_two": 0.52, "pass_one": 0.44}}
EPS = (0.005, 0.05)  #: the founders' confirmed false-STEERS rate: G4's point target, and K5's cap
QS = (0.10, 0.25, 0.50)  #: the share of evolved members that truly steer
NS = (80, 160)


def pmf(n, p):
    if p <= 0:
        return [1.0] + [0.0] * n
    if p >= 1:
        return [0.0] * n + [1.0]
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def upper_bound(k, n, alpha=0.05):
    """The upper 95% bound on the count a rate k/n predicts: the smallest c with P(Binomial(n, k/n) > c) <= alpha."""
    pr = pmf(n, k / n)
    tail = 1.0
    for c in range(n + 1):
        tail -= pr[c]
        if tail <= alpha:
            return c
    return n


def cp_upper(k, n, alpha=0.05):
    """The exact (Clopper-Pearson) one-sided upper 95% bound on a rate from k of n."""
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if sum(pmf(n, mid)[: k + 1]) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def upper_bound_cp(k, n, alpha=0.05):
    """The count bound with the founders' rate at its exact upper 95% bound (the alternative reading)."""
    pr = pmf(n, cp_upper(k, n))
    tail = 1.0
    for c in range(n + 1):
        tail -= pr[c]
        if tail <= alpha:
            return c
    return n


def perceives_power(n, q, sens, eps, bound=None):
    """P(evolved confirmed count > the founders' upper bound), exactly."""
    bound = bound or upper_bound
    founders = pmf(n, eps)
    evolved = pmf(n, q * sens + (1 - q) * eps)
    cum = [0.0] * (n + 2)  # cum[c] = P(evolved > c)
    s = 0.0
    for c in range(n, -1, -1):
        cum[c] = s
        s += evolved[c]
    return sum(pf * cum[bound(k, n)] for k, pf in enumerate(founders) if pf > 1e-15)


def false_positive(n, eps, bound=None):
    """PERCEIVES' STEERS clause under the null (q = 0): the evolved and founders' rates equal."""
    return perceives_power(n, 0.0, 0.0, eps, bound)


def k3_false_void(pa, pc, n=8):
    ok = 0.0
    for na, xa in enumerate(pmf(n, pa)):
        for nc, xc in enumerate(pmf(n, pc)):
            if na + nc >= 4 and na >= 1 and nc >= 1:
                ok += xa * xc
    return 1.0 - ok


def main():
    out = {"by_tau": {}, "legacy": {}}
    print("# probe_power.py: RBT-129 probe calls, exact binomial; priors from design-adversary/tau_probe.txt (caricature)")
    print("# PERCEIVES' STEERS clause: P(pooled confirmed STEERS count > the founders' upper 95% bound), per fauna and point")
    print("# left: the registered reading (the founders' rate plugged in); right: the founders' rate at its exact upper 95% bound")
    print(f"{'tau':>4s} {'route':6s} {'SENS':>5s} {'N':>4s} {'EPS':>6s} | " + " ".join(f"q {q:.2f}" for q in QS) + " | null (q 0)"
          + "   || " + " ".join(f"q {q:.2f}" for q in QS) + " | null")
    for tau, pr in PRIORS.items():
        rows = {}
        for route in ("two", "one"):
            for n in NS:
                for eps in EPS:
                    pw = [perceives_power(n, q, pr[route], eps) for q in QS]
                    fp = false_positive(n, eps)
                    rows[(route, n, eps)] = pw
                    pc = [perceives_power(n, q, pr[route], eps, upper_bound_cp) for q in QS]
                    fc = false_positive(n, eps, upper_bound_cp)
                    print(f"{tau:4.1f} {route:6s} {pr[route]:5.2f} {n:4d} {eps:6.3f} | " + " ".join(f"{x:6.3f}" for x in pw) + f" | {fp:.3f}"
                          f"   || exact-bound reading: " + " ".join(f"{x:6.3f}" for x in pc) + f" | {fc:.3f}")
        fv = k3_false_void(pr["pass_two"], pr["pass_two"])
        fv1 = k3_false_void(pr["pass_two"], pr["pass_one"])
        print(f"{tau:4.1f} K3 false-VOID: {fv:.4f} (two-nose (a) and (c)); {fv1:.4f} if (c) sees only at the one-nose share")
        key = rows[("two", 80, 0.005)]
        key1 = rows[("one", 80, 0.005)]
        cp = [perceives_power(80, q, pr["two"], 0.005, upper_bound_cp) for q in QS]
        cp1 = [perceives_power(80, q, pr["one"], 0.005, upper_bound_cp) for q in QS]
        line = (f"tau {tau:g} s, the pilot's N 80, founders' EPS 0.005, q 0.10 / 0.25 / 0.50: PERCEIVES' STEERS clause as registered "
                f"{key[0]:.2f} / {key[1]:.2f} / {key[2]:.2f} two-nose (SENS {pr['two']}), {key1[0]:.2f} / {key1[1]:.2f} / {key1[2]:.2f} "
                f"one-nose (SENS {pr['one']}), null 0.22; with the founders' rate at its exact upper bound {cp[0]:.2f} / {cp[1]:.2f} / "
                f"{cp[2]:.2f} and {cp1[0]:.2f} / {cp1[1]:.2f} / {cp1[2]:.2f}, null 0.00; K3 false-VOID {fv:.3f}. Caricature priors.")
        out["by_tau"][str(tau)] = {"line": line, "rows": {f"{r}/{n}/{e}": v for (r, n, e), v in rows.items()}, "k3_false_void": fv}
        print("# " + line)
    out["legacy"] = {"line": "legacy channel (an L point, no contrast): RBT-116 has no caricature prior for it; the point's own K3 "
                             "and K5 measure the instrument's sensitivity and false rate there, and no power is claimed"}
    print("# " + out["legacy"]["line"])
    print("""
# Reading (RBT-132 item 5).
# - FIRST, a finding about RBT-129's rule, not about tau: read literally (the founders' confirmed rate plugged in as the
#   rate, its upper 95% count bound the threshold), the STEERS clause fires on 22-25% of null points. With few
#   false STEERS the founders' count is usually 0, the bound is then 0, and a single evolved STEERS passes it. Taking the
#   founders' rate at its exact upper 95% bound (right-hand columns) holds the null near 0.05 or below, at a power cost
#   shown beside it. PERCEIVES also needs f BH-significant with mean f >= F_MIN, which limits the damage, but the clause
#   alone is not a 5% test. This is RBT-129's registration to rule on; RBT-132 does not change it.
# - Under the exact-bound reading, tau 2 s costs the probe leg a real share of its power: at N 80 and q 0.25, two-nose
#   0.79 -> 0.63 and one-nose 0.41 -> 0.19 (tau 1 s -> 2 s); at q 0.50 it keeps 0.99 (two-nose) and 0.78 (one-nose).
#   Under the registered (plug-in) reading the numbers look better (0.98 / 0.89 at q 0.25) only because that test is
#   not held at 5%.
# - What the probe leg CAN conclude at tau 2 s: PERCEIVES where about half the evolved members steer (either route),
#   or a quarter steer through two noses at the pilot's 4 seeds. What it CANNOT: an absence where steerers are rare
#   (q about 0.1: power under 0.1 on the exact reading), or one-nose steering at q below about 0.5. There NONE means
#   "not detected at this sensitivity", and the point's own K3 (the planted (a) and (c) seen; false-VOID 0.01 at tau 2)
#   says whether the instrument could see steering there at all.
# - RBT-116's own 0.397 (power_tau2.txt) is a different quantity: the line-level crossing count at K + 2 over 24 units.
#   The probe calls are pooled counts against the founders, so they lose less.""")
    with open(os.path.join(HERE, "probe_power.json"), "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
