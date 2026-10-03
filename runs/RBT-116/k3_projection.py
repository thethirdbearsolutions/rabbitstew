"""RBT-132, the fix-check ruling's item 2: project K3's per-plant SEEN share at larger stage-2 / confirmation counts.

    python runs/RBT-116/k3_projection.py CELL1/planted.json CELL2/planted.json            (the 16-draw calibration)
    python runs/RBT-116/k3_projection.py --pooled CELL1/planted.json CELL2/planted.json   (its second stage, #471 S2)

One ``planted.json`` per calibration cell (``c0-p030-PW-G``, ``c0-p030-HP-G``).  ``--pooled`` reads a second-stage run
(``planters.py planted --calibration``: the confirmation on every (a) and (c) plant) and projects each plant on its 32
draws, stage 2 and the confirmation pooled; that re-projection is final (#471's ruling, S2).

The rule (coordinator on #459, fixed pre-data): if the measured SEEN share at the calibration cells is below 0.45 for
(a) or (c), the probe battery's stage-2 and confirmation counts are raised together, for plants and members alike, to
the smallest power of 2 at which the **projected** per-plant SEEN share reaches 0.6 for both kinds; the cap is 64, and
above it the perception layer is declared unreadable at a = 6.

**The projection.**
- A plant's ΔT on one draw is taken as Normal(μ, σ²), with μ and σ its measured per-plant ΔT mean and SD.
- c2 on a battery of n draws is ``steer.lower_bound`` > 0, the one-sided 95% t bound that ``battery_stats`` uses:
  mean − t(0.95, n − 1)·s/√n > 0.  Its probability is exact under that model:
  P = E_V[Φ(δ − t·√(V/(n − 1)))], with δ = μ√n/σ and V ~ χ²(n − 1), integrated numerically.
- c3 (the veto: the trajectories differ on more than half the draws) is projected from the plant's per-draw differ rate
  q = differ / n (#471's ruling, N1): P(c3 at n) = P(Binomial(n, q) > n / 2).
- SEEN (the 07:10 ruling) is c2 ∧ c3 on stage 2, repeated on the confirmation, two independent batteries of n draws:
  P(SEEN) = [P(c2 at n) · P(c3 at n)]².
- A kind's projected share is the mean of its plants' P(SEEN).

**Inputs.** Per plant, ``(mu, sd)``, ``(mu, sd, q)`` or ``(mu, sd, q, refused)``; q defaults to 1 (a certain veto pass),
and a bool q reads as 1 or 0.  From a ``planted`` run, :func:`from_planted` reads each (a) and (c) plant's stage-2
record: μ is its ``dT``; σ is recovered exactly from its bound, σ = (dT − lbdT)·√n / t(0.95, n − 1); q is its
``differ`` / n; and ``refused`` is the plant's θ refusals (#471 N2: printed beside its ΔT, since the projection
assumes every draw usable at the new count).  A plant stopped at stage 1 has no stage-2 record: it enters as never SEEN
(q = 0), listed, not dropped.  With ``pooled``, the plant's stage-2 and confirmation records are pooled exactly (the
combined mean, SD and differ count of both batteries' draws); a plant with no confirmation record is refused there.

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


def p_c3(q: float, n: int) -> float:
    """P(the veto passes on n draws): more than half of n Bernoulli(q) draws differ."""
    q = float(q)
    return float(sum(math.comb(n, k) * q ** k * (1.0 - q) ** (n - k) for k in range(n // 2 + 1, n + 1)))


def p_seen(plant, n: int) -> float:
    mu, sd = plant[0], plant[1]
    q = plant[2] if len(plant) > 2 else 1.0
    return (p_c2(mu, sd, n) * p_c3(q, n)) ** 2


def share(plants, n: int) -> float:
    return float(np.mean([p_seen(p, n) for p in plants])) if plants else 0.0


def project(kinds: dict, counts=COUNTS, target: float = TARGET) -> dict:
    """``kinds``: {"a": [(mu, sd[, veto]), ...], "c": [...]}.  Returns the projected shares per count and the rule's
    answer: the smallest count at which every kind reaches ``target``, or ``UNREADABLE``."""
    shares = {n: {k: share(v, n) for k, v in kinds.items()} for n in counts}
    pick = next((n for n in counts if all(s >= target for s in shares[n].values())), UNREADABLE)
    return {"shares": shares, "counts": pick}


sd_from_stats = planters.dT_sd  #: σ from a battery_stats record (its bound is dT − t·σ/√n)


def pool_stats(a: dict, b: dict) -> dict:
    """Two batteries' ΔT records pooled exactly: the combined n, mean, SD (from each battery's mean and SD) and differ."""
    n1, n2 = a["n"], b["n"]
    m1, m2 = a["dT"], b["dT"]
    s1, s2 = sd_from_stats(a), sd_from_stats(b)
    n = n1 + n2
    m = (n1 * m1 + n2 * m2) / n
    ss = (n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2 + n1 * (m1 - m) ** 2 + n2 * (m2 - m) ** 2
    return {"n": n, "dT": m, "sd": math.sqrt(ss / (n - 1)), "differ": a["differ"] + b["differ"]}


def _plant(rec: dict, pooled: bool) -> tuple:
    refused = int(rec.get("theta_refused", 0))
    s2 = rec.get("stage2")
    conf = rec.get("confirm") or rec.get("k3_confirm")
    if pooled:
        if conf is None:
            raise ValueError("a pooled projection needs every (a) and (c) plant's confirmation (planted --calibration)")
        parts = [x for x in (s2, conf) if x and x["n"] >= 2 and math.isfinite(x["lbdT"])]
        if not parts:
            return (0.0, 1.0, 0.0, refused)
        if len(parts) == 1:
            x = parts[0]
            return (x["dT"], sd_from_stats(x), x["differ"] / x["n"], refused)
        p = pool_stats(*parts)
        return (p["dT"], p["sd"], p["differ"] / p["n"], refused)
    if not s2 or not math.isfinite(s2["lbdT"]):
        return (0.0, 1.0, 0.0, refused)
    return (s2["dT"], sd_from_stats(s2), s2["differ"] / s2["n"], refused)


def from_planted(paths, pooled: bool = False) -> dict:
    """The (a) and (c) plants of one or more ``planted.json`` files, as (mu, sd, q, refused) per plant."""
    kinds = {"a": [], "c": []}
    for path in paths:
        calls = json.load(open(path))["calls"]
        for k in kinds:
            kinds[k] += [_plant(rec, pooled) for rec in calls.get(k, [])]
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


#: the probe leg's size (RBT-129 stages.py probe_jobs: blocks.PILOT's 4 points × PILOT_SEEDS' 4 seeds × seasons 0 and
#: 300 × 2 faunas × 20 members; a planted set per point: 8 (a), 8 (b), 8 (c), 3 (d), 3 (e), 8 motors-off, 16 screen hosts)
PROBE = {"points": 4, "seeds": 4, "seasons": 2, "faunas": 2, "members": 20, "plants": 38, "screen_hosts": 16}
CORE_S = 0.36  #: core-seconds per 15 s season (RBT-125 §B's measured cost; RBT129's points run 15 s seasons)
#: #476's fix-check N-1: measured by wall-clock (process CPU time) in this repo's container, 40 intact and decoy 15 s
#: seasons of committed RBT-19 P-801 bodies in W1's block on fixture draws (median 0.50, range 0.44-0.73); printed beside
#: CORE_S, not instead of it
CORE_S_MEASURED = 0.51


def probe_cost(n: int) -> dict:
    """The probe leg's seasons and core-hours at stage-2 / confirmation count n (#471's ruling, M1(d)), an upper bound:
    every call run to its confirmation (stage 1: 4 draws × 2 conditions; stage 2: n × 4; the confirmation: n × 2), plus
    each point's screen over its extended pool.  Members stopped at stage 1 cost 8 seasons, so the real cost is lower."""
    per_call = 2 * steer.N_STAGE1 + 4 * n + 2 * n
    z = steer.sizes_at(n)
    z_ext = z["pool"] + z["extension"]
    P = PROBE
    members = P["points"] * P["seeds"] * P["seasons"] * P["faunas"] * P["members"]
    seasons = members * per_call + P["points"] * (P["plants"] * per_call + z_ext * P["screen_hosts"])
    return {"n": n, "members": members, "seasons": seasons, "core_h": seasons * CORE_S / 3600.0,
            "core_h_measured": seasons * CORE_S_MEASURED / 3600.0}


def report(paths, pooled: bool = False) -> str:
    cells = measured(paths)
    per_cell = {p: from_planted([p], pooled) for p in paths}
    lines = ["# K3 projection (RBT-132; #471's ruling): per-plant SEEN = [P(c2 at n) P(c3 at n)]^2, t bound as battery_stats"
             + ("; POOLED: stage 2 and the confirmation, 32 draws per plant (the second stage, final)" if pooled else "")]
    for path in paths:
        kinds, res = per_cell[path], project(per_cell[path])
        lines.append(f"## {path}: measured SEEN " + ", ".join(f"({k}) {s} of {n}" for k, (s, n) in cells[path].items()))
        for k, v in kinds.items():
            lines.append(f"({k}) {len(v)} plants: " + "; ".join(
                f"dT {pl[0]:+.3f} sd {pl[1]:.3f} veto {pl[2]:.2f} refused {pl[3]}" + (" (never SEEN)" if pl[2] == 0 else "") for pl in v))
        for n, sh in res["shares"].items():
            lines.append(f"projected n {n:3d}: " + ", ".join(f"({k}) {x:.3f}" for k, x in sh.items()))
        lines.append(f"this cell: {res['counts']}")
    c = rule(per_cell)
    if launches_as_registered(cells) and not pooled:
        lines.append(f"RULE: measured SEEN >= {MEASURED_BAR} for both kinds at every cell: the probe leg launches as registered (16 draws)")
        c = steer.N_STAGE2
    else:
        head = ("RULE (second stage, final: the 32-draw re-projection): " if pooled
                else f"RULE: measured SEEN below {MEASURED_BAR} somewhere; ")
        lines.append(head
                     + (f"stage-2 and confirmation counts raised to {c}, for plants and members alike" if c != UNREADABLE
                        else f"UNREADABLE at a = 6 (64 draws do not reach {TARGET} at every cell): no probe leg"))
        if not pooled and c in (64, UNREADABLE):
            lines.append("SECOND STAGE due (#471 S2): run planters.py planted --calibration at both cells, then --pooled; that is final")
    for n in ([c] if c != UNREADABLE else []) + ([steer.N_STAGE2] if c != steer.N_STAGE2 else []):
        k = probe_cost(n)
        lines.append(f"COST at n {n}: the probe leg's {k['members']} member calls + planted sets, at most {k['seasons']:,} seasons, "
                     f"about {k['core_h']:.1f} core-h at {CORE_S} core-s per season ({k['core_h_measured']:.1f} at the measured "
                     f"{CORE_S_MEASURED}; members stopped at stage 1 cost less)")
    return "\n".join(lines)


if __name__ == "__main__":
    args = sys.argv[1:]
    print(report([a for a in args if a != "--pooled"], pooled="--pooled" in args))
