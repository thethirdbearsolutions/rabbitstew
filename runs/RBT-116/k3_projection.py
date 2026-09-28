"""RBT-132, the fix-check ruling's item 2: project K3's per-plant SEEN share at larger stage-2 / confirmation counts.

    python runs/RBT-116/k3_projection.py OUT/planted.json [OUT2/planted.json ...]

The rule (coordinator on #459, fixed pre-data): if the measured SEEN share at the calibration cells is below 0.45 for
(a) or (c), the probe battery's stage-2 and confirmation counts are raised together, for plants and members alike, to
the smallest power of 2 at which the **projected** per-plant SEEN share reaches 0.6 for both kinds; the cap is 64, and
above it the perception layer is declared unreadable at a = 6.

**The projection.**
- A plant's ΔT on one draw is taken as Normal(μ, σ²), with μ and σ its measured per-plant ΔT mean and SD.
- c2 on a battery of n draws is ``steer.lower_bound`` > 0, the one-sided 95% t bound that ``battery_stats`` uses:
  mean − t(0.95, n − 1)·s/√n > 0.  Its probability is exact under that model:
  P = E_V[Φ(δ − t·√(V/(n − 1)))], with δ = μ√n/σ and V ~ χ²(n − 1), integrated numerically.
- SEEN (the 07:10 ruling) is c2 ∧ c3 on stage 2, repeated on the confirmation, two independent batteries of n draws:
  P(SEEN) = P(c2 at n)².  The veto c3 is taken as passing: it passed on every plant in the fix-check's measurement
  (FIX-CHECK-RBT132.md §4), and a plant whose calibration veto failed is entered with ``veto=False`` (P(SEEN) = 0).
- A kind's projected share is the mean of its plants' P(SEEN).

**Inputs.** Per plant, ``(mu, sd)`` or ``(mu, sd, veto)``.  From a ``planted`` run, :func:`from_planted` reads each (a)
and (c) plant's stage-2 record: μ is its ``dT``, and σ is recovered exactly from its bound,
σ = (dT − lbdT)·√n / t(0.95, n − 1), so ``steer.py`` is untouched.  A plant stopped at stage 1 has no stage-2 record: it
enters as never SEEN (it cannot be projected without a new measurement), listed, not dropped.

**The measured share** (the rule's first branch) is read by :func:`measured`: each (a) and (c) plant's K3 verdict,
``planters.seen``, pooled over the calibration cells given; ≥ 0.45 for both kinds launches the probe leg as registered.

Synthetic inputs only in the tests; nothing here runs a season.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planters  # noqa: E402

steer = planters.steer

COUNTS = (16, 32, 64)  #: the powers of 2 the rule may choose; 16 is the registered count, 64 the cap
TARGET = 0.6  #: the projected per-plant SEEN share each kind must reach
MEASURED_BAR = 0.45  #: the measured share at which the probe leg launches as registered
UNREADABLE = "unreadable"


def p_c2(mu: float, sd: float, n: int, grid: int = 4001) -> float:
    """P(``steer.lower_bound`` of n Normal(mu, sd²) draws > 0), exact up to the quadrature."""
    if sd <= 0:
        return 1.0 if mu > 0 else 0.0
    df = n - 1
    t = steer.t_quantile(0.95, df)
    delta = mu * math.sqrt(n) / sd
    # V ~ chi2(df), integrated on a grid wide enough to hold all but ~1e-12 of its mass
    hi = df + 40.0 * math.sqrt(2.0 * df) + 40.0
    v = np.linspace(1e-12, hi, grid)
    logpdf = (df / 2 - 1) * np.log(v) - v / 2 - (df / 2) * math.log(2) - math.lgamma(df / 2)
    w = np.exp(logpdf)
    z = delta - t * np.sqrt(v / df)
    phi = 0.5 * (1.0 + np.vectorize(math.erf)(z / math.sqrt(2.0)))
    return float(np.clip(_trapezoid(w * phi, v) / _trapezoid(w, v), 0.0, 1.0))


def _trapezoid(y, x):
    return float(np.sum((y[1:] + y[:-1]) * np.diff(x)) / 2.0)


def p_seen(plant, n: int) -> float:
    mu, sd = plant[0], plant[1]
    veto = plant[2] if len(plant) > 2 else True
    return p_c2(mu, sd, n) ** 2 if veto else 0.0


def share(plants, n: int) -> float:
    return float(np.mean([p_seen(p, n) for p in plants])) if plants else 0.0


def project(kinds: dict, counts=COUNTS, target: float = TARGET) -> dict:
    """``kinds``: {"a": [(mu, sd[, veto]), ...], "c": [...]}.  Returns the projected shares per count and the rule's
    answer: the smallest count at which every kind reaches ``target``, or ``UNREADABLE``."""
    shares = {n: {k: share(v, n) for k, v in kinds.items()} for n in counts}
    pick = next((n for n in counts if all(s >= target for s in shares[n].values())), UNREADABLE)
    return {"shares": shares, "counts": pick}


def sd_from_stats(s2: dict) -> float:
    """σ from a ``battery_stats`` record: its bound is dT − t·σ/√n (``steer.lower_bound``)."""
    n = s2["n"]
    if s2["lbdT"] == s2["dT"]:
        return 0.0
    return (s2["dT"] - s2["lbdT"]) * math.sqrt(n) / steer.t_quantile(0.95, n - 1)


def from_planted(paths) -> dict:
    """The (a) and (c) plants of one or more ``planted.json`` files, as (mu, sd, veto) per plant."""
    kinds = {"a": [], "c": []}
    for path in paths:
        calls = json.load(open(path))["calls"]
        for k in kinds:
            for rec in calls.get(k, []):
                s2 = rec.get("stage2")
                if not s2 or not math.isfinite(s2["lbdT"]):
                    kinds[k].append((0.0, 1.0, False))
                else:
                    kinds[k].append((s2["dT"], sd_from_stats(s2), bool(s2["c3"])))
    return kinds


def measured(paths) -> dict:
    """The measured SEEN share per kind, pooled over the calibration cells: (seen, plants)."""
    out = {"a": [0, 0], "c": [0, 0]}
    for path in paths:
        calls = json.load(open(path))["calls"]
        for k in out:
            for rec in calls.get(k, []):
                out[k][0] += int(planters.seen(rec))
                out[k][1] += 1
    return {k: tuple(v) for k, v in out.items()}


def report(kinds: dict, seen_counts: dict = None) -> str:
    res = project(kinds)
    lines = ["# K3 projection (RBT-132, the fix-check ruling's item 2): per-plant SEEN = P(c2 at n)^2, t bound as battery_stats"]
    if seen_counts is not None:
        ok = all(n and s / n >= MEASURED_BAR for s, n in seen_counts.values())
        lines.append("measured SEEN: " + ", ".join(f"({k}) {s} of {n}" for k, (s, n) in seen_counts.items())
                     + f" -> {'>= ' + str(MEASURED_BAR) + ' for both kinds: the probe leg launches as registered' if ok else 'below ' + str(MEASURED_BAR) + ': the projection decides'}")
    for k, v in kinds.items():
        lines.append(f"({k}) {len(v)} plants: " + "; ".join(f"dT {m:+.3f} sd {s:.3f}{'' if (len(p) < 3 or p[2]) else ' veto failed'}"
                                                      for p in v for m, s in [p[:2]]))
    for n, sh in res["shares"].items():
        lines.append(f"n {n:3d}: " + ", ".join(f"({k}) {s:.3f}" for k, s in sh.items()))
    c = res["counts"]
    lines.append(f"RULE: {'stage-2 and confirmation counts ' + str(c) if c != UNREADABLE else 'UNREADABLE at a = 6 (the cap 64 does not reach ' + str(TARGET) + ')'}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(from_planted(sys.argv[1:]), measured(sys.argv[1:])))
