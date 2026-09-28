"""RBT-132 item 5, as ruled at 07:10: the power of RBT-129's probe calls at τ = 2 s beside τ = 1 s (exact; no simulation).

    python runs/RBT-116/probe_power.py > runs/RBT-116/probe_power.txt

**PERCEIVES' STEERS clause** (ruled, item 2): a **one-sided Fisher exact test at α = 0.05** of the pooled evolved
confirmed-STEERS count against the pooled founders' count, with the same members per seed (N each).  The founders' count
is Binomial(N, ε), and the evolved count is Binomial(N, q·SENS + (1 − q)·ε), where q is the share of evolved members
that truly steer.  The null rate (q = 0) is computed over a grid of ε, and the power at each q; nothing is a literal.

**K3's false-VOID** (ruled, item 1): of 8 (a) and 8 (c) plants, K3 needs ≥ 4 pooled SEEN with ≥ 1 of each kind.  A
plant is SEEN when stage 2's veto and ΔT bound hold and the confirmation battery repeats both; F plays no part.  It is
printed at two SEEN shares, and the second one governs (the fix-check ruling on #459, M1):
- the caricature's (``k3_seen_probe.txt``): a kinematic idealisation with no body, terrain or motor noise, so its
  per-plant ΔT bound clears where a real plant's does not; its false-VOID (about 0) is **not** a prediction;
- the fixture measurement (``design-adversary/rbt132_seen_real.txt``): ``planters.py``'s own (a) and (c) plants on
  RBT-113 O1's committed finals, two fixture worlds at τ 2 s, **1 of 32 SEEN** ((a) 1 of 16, (c) 0 of 16); its
  false-VOID is about 1.0.  K3 is not loosened: the calibration lane measures the share at two PAYS cells first, and
  ``k3_projection.py`` applies the pre-data rule to it.

**The null** is computed, and is at most 0.028 at N 80 and 0.033 at N 160 for ε ≤ 0.10 (``EPS_GRID``).  Over any ε it
is below 0.05: the Fisher test is exact conditionally on the pooled count, so its level holds at every ε (the wide
table, ``EPS_WIDE``, shows 0.036–0.039 at ε 0.3).

The priors (``design-adversary/tau_probe.txt``, ``k3_seen_probe.txt``) are the design-stage caricature's: two-nose
confirmed 0.48 / 0.40 and one-nose 0.32 / 0.24 at τ 1 / 2 s.  Every point measures its own rates with K3 and K5.
"""
import functools
import math

PRIORS = {1.0: {"two": 0.48, "one": 0.32}, 2.0: {"two": 0.40, "one": 0.24}}  #: confirmed STEERS shares (tau_probe.txt)
#: K3's SEEN share per plant (k3_seen_probe.txt; the (a) plant is a two-nose compass, and the (c) plant is a two-nose plant)
SEEN = {1.0: {"two": 1.00, "one": 1.00}, 2.0: {"two": 1.00, "one": 0.96}}  #: steer2-k6, steer1-k32 rows
EPS_GRID = (0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10)  #: the founders' confirmed false-STEERS rate (K5's cap is 0.05)
EPS_WIDE = (0.2, 0.3, 0.5)  #: beyond K5's cap, to show the level holds (N1)
#: K3's SEEN share as measured on planters.py's own plants on real O1 hosts (fix-check, rbt132_seen_real.txt): (seen, of)
FIXTURE_SEEN = {"a": (1, 16), "c": (0, 16)}
CARICATURE_CAVEAT = ("the caricature is a kinematic idealisation (no body, terrain or motor noise): its K3 false-VOID "
                     "is not a prediction")
QS = (0.10, 0.25, 0.50)
NS = (80, 160)  #: the pilot's 4 seeds × 20, and 8 × 20
ALPHA = 0.05
LEGACY = ("legacy channel (an L point, no contrast): RBT-116 has no caricature prior for it; the point's own K3 and K5 "
          "measure the instrument's sensitivity and false rate there, and no power is claimed")


def pmf(n, p):
    if p <= 0:
        return [1.0] + [0.0] * n
    if p >= 1:
        return [0.0] * n + [1.0]
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


@functools.lru_cache(maxsize=None)
def reject(n):
    """reject[x0][x1]: the one-sided Fisher exact test rejects (evolved x1 of n more than founders x0 of n) at ALPHA."""
    out = []
    for x0 in range(n + 1):
        row = []
        for x1 in range(n + 1):
            t = x0 + x1
            denom = math.comb(2 * n, t)
            p = sum(math.comb(n, k) * math.comb(n, t - k) for k in range(x1, min(n, t) + 1)) / denom
            row.append(p <= ALPHA)
        out.append(row)
    return out


def perceives(n, q, sens, eps):
    """P(the clause fires): the founders at ε, the evolved at q·sens + (1 − q)·ε."""
    R = reject(n)
    f0, f1 = pmf(n, eps), pmf(n, q * sens + (1 - q) * eps)
    return sum(a * b for x0, a in enumerate(f0) if a > 1e-15 for x1, b in enumerate(f1) if R[x0][x1])


def null_max(n, grid=EPS_GRID):
    return max((perceives(n, 0.0, 0.0, e), e) for e in grid)


def fixture_false_void():
    """K3's false-VOID at the fixture measurement's SEEN shares (the rate that governs; M1)."""
    (sa, na), (sc, nc) = FIXTURE_SEEN["a"], FIXTURE_SEEN["c"]
    return k3_false_void(sa / na, sc / nc)


def k3_false_void(pa, pc, n=8):
    ok = 0.0
    for na, xa in enumerate(pmf(n, pa)):
        for nc, xc in enumerate(pmf(n, pc)):
            if na + nc >= 4 and na >= 1 and nc >= 1:
                ok += xa * xc
    return 1.0 - ok


def seen_prior(tau, route):
    """K3's per-plant SEEN share: the caricature's measurement, else (not measured) the confirmed share, a lower bound
    (a confirmed STEERS plant is SEEN)."""
    s = SEEN[tau][route]
    return (s, "measured") if s is not None else (PRIORS[tau][route], "lower bound: confirmed share")


@functools.lru_cache(maxsize=None)
def line(tau, n=80, eps=0.005):
    """The one line printed beside every planted and probe call at a point with this τ."""
    pr = PRIORS[tau]
    two = [perceives(n, q, pr["two"], eps) for q in QS]
    one = [perceives(n, q, pr["one"], eps) for q in QS]
    fa, fc = FIXTURE_SEEN["a"], FIXTURE_SEEN["c"]
    return (f"tau {tau:g} s, N {n}, founders' eps {eps}: PERCEIVES' STEERS clause (one-sided Fisher exact, alpha 0.05) "
            f"null <= {null_max(80)[0]:.3f} at N 80, <= {null_max(160)[0]:.3f} at N 160, for eps <= {max(EPS_GRID):g}; "
            f"below 0.05 at every eps; power at q {' / '.join(f'{q:.2f}' for q in QS)}: "
            f"{' / '.join(f'{x:.2f}' for x in two)} two-nose (SENS {pr['two']}), {' / '.join(f'{x:.2f}' for x in one)} "
            f"one-nose (SENS {pr['one']}) (caricature priors, not measurements). K3 false-VOID about "
            f"{fixture_false_void():.1f} on real plants ({fa[0] + fc[0]} of {fa[1] + fc[1]} SEEN on O1 hosts in fixture worlds at "
            f"tau 2 s; {CARICATURE_CAVEAT}); K3 is not loosened: the calibration lane measures it first (k3_projection.py).")


def main():
    print("# probe_power.py: RBT-129 probe calls as ruled at 07:10; exact; priors from the caricature (tau_probe.txt, k3_seen_probe.txt)")
    print("# PERCEIVES' STEERS clause: one-sided Fisher exact test at 0.05, evolved against founders' pooled confirmed-STEERS counts")
    print("## null rate (q = 0), by the founders' rate eps")
    print(f"{'N':>4s} | " + " ".join(f"eps {e:<5g}" for e in EPS_GRID) + " | max    | " + " ".join(f"eps {e:<5g}" for e in EPS_WIDE))
    for n in NS:
        row = [perceives(n, 0.0, 0.0, e) for e in EPS_GRID]
        wide = [perceives(n, 0.0, 0.0, e) for e in EPS_WIDE]
        print(f"{n:4d} | " + " ".join(f"{x:9.4f}" for x in row) + f" | {max(row):.4f} | " + " ".join(f"{x:9.4f}" for x in wide))
    print("## power, by tau, route, N and eps")
    print(f"{'tau':>4s} {'route':6s} {'SENS':>5s} {'N':>4s} {'eps':>6s} | " + " ".join(f"q {q:.2f}" for q in QS))
    for tau, pr in PRIORS.items():
        for route in ("two", "one"):
            for n in NS:
                for eps in (0.005, 0.05):
                    pw = [perceives(n, q, pr[route], eps) for q in QS]
                    print(f"{tau:4.1f} {route:6s} {pr[route]:5.2f} {n:4d} {eps:6.3f} | " + " ".join(f"{x:6.3f}" for x in pw))
    print("## K3 false-VOID: P(fewer than 4 of 8 (a) + 8 (c) SEEN, or none of one kind)")
    (sa, na), (sc, nc) = FIXTURE_SEEN["a"], FIXTURE_SEEN["c"]
    print(f"GOVERNS: real plants (planters.py's (a) and (c) on O1 hosts, fixture worlds, tau 2 s; fix-check "
          f"rbt132_seen_real.txt): (a) SEEN {sa} of {na}, (c) SEEN {sc} of {nc}: false-VOID {fixture_false_void():.4f}")
    print("# the caricature's rows below are NOT predictions: " + CARICATURE_CAVEAT)
    for tau in PRIORS:
        for route_c in ("two", "one"):
            sa, how_a = seen_prior(tau, "two")
            sc, how_c = seen_prior(tau, route_c)
            print(f"tau {tau:g} s: (a) SEEN {sa:.2f} ({how_a}), (c) SEEN {sc:.2f} as a {route_c}-nose plant ({how_c}): "
                  f"false-VOID {k3_false_void(sa, sc):.4f}")
    for tau in PRIORS:
        print("# " + line(tau))
    print("# " + LEGACY)
    print("""
# Reading (RBT-132 item 5, as ruled).
# - The Fisher test holds the clause at or below 0.05 at every founders' rate (the null table), which the ruled reading
#   requires; the old plug-in reading fired on 12-25% of null points.
# - What the probe leg CAN conclude at tau 2 s: PERCEIVES where a quarter or more of the evolved members steer through
#   two noses, or about half through one nose, at the pilot's N 80 (the power table). What it CANNOT: an absence where
#   steerers are rare (q about 0.1), or one-nose steering at a quarter; there NONE means "not detected at this
#   sensitivity", and the point's own K3 says whether the instrument could see steering there at all.
# - The null is at most 0.028 at N 80 and 0.033 at N 160 for eps <= 0.10, and below 0.05 at every eps (the wide
#   columns): the test is exact given the pooled count.
# - K3 under the ruled SEEN (the fix-check ruling, M1): on real plants, 1 of 32 were SEEN, and K3's false-VOID there is
#   about 1.0; it is reported before launch, not absorbed, and K3 is not loosened. The caricature's 0.000 is withdrawn:
#   the caricature has no body, terrain or motor noise, so its per-plant dT bound clears where a real plant's does not.
#   The calibration lane (planted at c0-p030-PW-G and c0-p030-HP-G) measures the share; below 0.45 for either kind,
#   k3_projection.py picks the stage-2 / confirmation counts (16, 32 or 64) or declares the layer unreadable at a = 6.
# - RBT-116's own 0.397 (power_tau2.txt) is a different quantity: the line-level crossing count at K + 2 over 24 units.""")


if __name__ == "__main__":
    main()
