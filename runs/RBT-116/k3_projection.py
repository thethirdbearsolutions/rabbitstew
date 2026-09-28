"""RBT-132, the fix-check ruling's item 2: project K3's per-plant SEEN share at larger stage-2 / confirmation counts.

    python runs/RBT-116/k3_projection.py CELL1/planted.json CELL2/planted.json

One ``planted.json`` per calibration cell (``c0-p030-PW-G``, ``c0-p030-HP-G``).

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
``planters.seen``, per calibration cell; ≥ 0.45 for both kinds **at every cell** launches the probe leg as registered
(:func:`launches_as_registered`).  Otherwise each cell is projected on its own plants and the battery takes the largest
count any cell needs (:func:`rule`): "for both kinds" is read at every cell, as the first branch is.

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


sd_from_stats = planters.dT_sd  #: σ from a battery_stats record (its bound is dT − t·σ/√n)


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
    """The measured SEEN count per calibration cell and kind: {path: {"a": (seen, plants), "c": (...)}}."""
    out = {}
    for path in paths:
        calls = json.load(open(path))["calls"]
        out[path] = {k: (sum(int(planters.seen(r)) for r in calls.get(k, [])), len(calls.get(k, []))) for k in ("a", "c")}
    return out


def launches_as_registered(cells: dict) -> bool:
    """The rule's first branch: the measured SEEN share is ≥ 0.45 for both kinds **at every calibration cell**."""
    return bool(cells) and all(n and s / n >= MEASURED_BAR for kinds in cells.values() for s, n in kinds.values())


def rule(per_cell: dict) -> object:
    """The rule's second branch over the calibration cells: each cell's projection picks its count, and the battery takes
    the largest (a count must reach 0.6 for both kinds **at every cell**, as the first branch reads "at both cells");
    ``UNREADABLE`` if any cell is."""
    picks = [project(kinds)["counts"] for kinds in per_cell.values()]
    if not picks or UNREADABLE in picks:
        return UNREADABLE
    return max(picks)


def report(paths) -> str:
    cells = measured(paths)
    per_cell = {p: from_planted([p]) for p in paths}
    lines = ["# K3 projection (RBT-132, the fix-check ruling's item 2): per-plant SEEN = P(c2 at n)^2, t bound as battery_stats"]
    for path in paths:
        kinds, res = per_cell[path], project(per_cell[path])
        lines.append(f"## {path}: measured SEEN " + ", ".join(f"({k}) {s} of {n}" for k, (s, n) in cells[path].items()))
        for k, v in kinds.items():
            lines.append(f"({k}) {len(v)} plants: " + "; ".join(f"dT {pl[0]:+.3f} sd {pl[1]:.3f}{'' if (len(pl) < 3 or pl[2]) else ' (never SEEN)'}"
                                                          for pl in v))
        for n, sh in res["shares"].items():
            lines.append(f"projected n {n:3d}: " + ", ".join(f"({k}) {x:.3f}" for k, x in sh.items()))
        lines.append(f"this cell: {res['counts']}")
    if launches_as_registered(cells):
        lines.append(f"RULE: measured SEEN >= {MEASURED_BAR} for both kinds at every cell: the probe leg launches as registered (16 draws)")
    else:
        c = rule(per_cell)
        lines.append(f"RULE: measured SEEN below {MEASURED_BAR} somewhere; "
                     + (f"stage-2 and confirmation counts raised to {c}, for plants and members alike" if c != UNREADABLE
                        else f"UNREADABLE at a = 6 (64 draws do not reach {TARGET} at every cell): no probe leg"))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(sys.argv[1:]))
