"""RBT-67 follow-up: is it still chemotaxis at a = 384?  The travel-frame manipulation check.

The ladder (compass_dose_response.py) read the compass's yield past a = 64 and found it still
rising at 384, with items per in-disc metre tripling on flat path.  That is what a compass
would do, but it is a yield-side reading.  RBT-69 established the manipulation itself --
the circuit aims the robot at food, and the gain collapses when the smell is decoupled from
the items -- at a = 64 only.  This repeats both checks at 384, on the source population.

Conditions, W4b-801, the published sign (their compass), 7 robots x 64 paired seeds from 7000:

* ``base``         nothing installed
* ``compass 64``   the anchor, for comparison with RBT-69's travel-frame numbers
* ``compass 384``  the top of the ladder
* ``phantom 64``, ``phantom 384``
                   the motif installed exactly as above, but the food SENSORS smell a decoy
                   layout drawn from seed + 5000 while the real items stay put and stay
                   edible.  The steering signal keeps its statistics and loses its
                   correlation with the food on the ground.  If the gain survives this it is
                   a gait perturbation, not a food-direction circuit (RBT-69's control).
* ``antimotif 384`` the opposite sign at the top rung: what the same magnitude does when it
                   is an anti-compass.

Every steering quantity is in the TRAVEL frame -- against the direction the centre of mass
actually moves this tick, never against chassis yaw (standing rule (b); this population
drives backward).  Reported per condition:

  bearing_grad   mean |bearing of steepest smell ascent - travel azimuth|, rad.  The circuit
                 climbs the summed field, so this is its target.  Lower is better aimed.
  bearing_near   the same against the nearest live item.
  turn_toward    sign(bearing_grad) x yaw rate, rad/s: > 0 turns the travel direction toward
                 the ascent, < 0 away.
  centroid_d     mean distance to the centroid of the live items, m.
  work           actuator work, J; score = items - work_cost x work / 1000 is the ecology's
                 own fitness quantity, reported because a pinned-effector fraction that the
                 item count does not charge for would show up here.

Usage: python docs/artifacts/RBT-67/manipulation_384.py [n_seeds=64] [workers=4]
"""

import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "docs", "artifacts", "RBT-67"))

import numpy as np

import compass_dose_response as cdr
import compass_replication as cr
from rabbitstew.fixed import drive_effector_units
from rabbitstew.simulation import Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

POP = "w4b"
GENS = cdr.POPULATIONS[POP]["gens"]
SIGN = cdr.POPULATIONS[POP]["sign"]
CONDS = (("base", 0.0), ("compass", 64.0), ("compass", 384.0), ("phantom", 64.0), ("phantom", 384.0), ("antimotif", 384.0))
PARKED = 1e5
OUT = os.path.join("docs", "artifacts", "RBT-67")


class DecoySmell(Simulation):
    """Food sensors smell ``_decoy`` instead of the real items.  Only the food branch of
    sensor_values passes ``self.food_pos`` as ``sources`` (simulation.py); eating, regrowth
    and every other sensor are untouched."""
    _decoy = None

    def _intensity(self, point, sources):
        if self._decoy is not None and sources is self.food_pos:
            sources = self._decoy
        return super()._intensity(point, sources)


def wrap(a: float) -> float:
    return float((a + math.pi) % (2 * math.pi) - math.pi)


def ascent_bearing(pos: np.ndarray, live: np.ndarray, decay: float):
    """Bearing of steepest ascent of sum_i exp(-d_i / decay) at ``pos``."""
    d = live - pos
    r = np.linalg.norm(d, axis=1)
    ok = r > 1e-9
    if not ok.any():
        return None
    g = ((np.exp(-r[ok] / decay) / r[ok])[:, None] * d[ok]).sum(axis=0)
    if np.linalg.norm(g) < 1e-12:
        return None
    return float(math.atan2(g[1], g[0]))


def bout(args) -> dict:
    cond, a, gen, seed = args
    cfg = cdr.config(POP)
    g = cdr.genotype(POP, gen)
    ph = synthesize(g, cfg.synthesis)
    sim = DecoySmell([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    if cond == "phantom":
        probe = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
        probe.set_food_seed(seed + 5000)
        sim._decoy = np.array(probe.food_pos, dtype=float).reshape(-1, 2).copy()
    sign = {"base": 0.0, "compass": SIGN, "phantom": SIGN, "antimotif": -SIGN}[cond]
    cr.install(sim.brains[0], ph, "compass", sign * cdr.k_of(a))
    brain = sim.brains[0]
    left_e, right_e = drive_effector_units(ph)
    idx = sim.robots[0]
    decay = cfg.food.decay
    dt = cfg.control_dt
    steps = int(round(cfg.duration / dt))
    last = sim.center_of_mass(0)[:2].copy()
    yaw_last = cr._yaw(sim.data.xquat[idx.root_body])
    b_grad, b_near, toward, cent = [], [], [], []
    path = in_path = 0.0
    rail = 0
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2].copy()
        step = p - last
        d = float(np.linalg.norm(step))
        path += d
        if float(np.linalg.norm(p)) <= cfg.food.radius:
            in_path += d
        yaw = cr._yaw(sim.data.xquat[idx.root_body])
        rate = wrap(yaw - yaw_last) / dt
        yaw_last = yaw
        act = brain.activation
        l = float(np.clip(act[left_e].sum(), -1.0, 1.0))
        r = float(np.clip(act[right_e].sum(), -1.0, 1.0))
        if abs(l) > cdr.RAIL and abs(r) > cdr.RAIL and (l > 0) == (r > 0):
            rail += 1
        live = sim.food_pos[np.max(np.abs(sim.food_pos), axis=1) < PARKED] if len(sim.food_pos) else np.zeros((0, 2))
        if len(live):
            cent.append(float(np.linalg.norm(live.mean(axis=0) - p)))
        if d > 1e-3 and len(live) and not sim.exploded[0]:
            travel = math.atan2(step[1], step[0])
            ab = ascent_bearing(p, live, decay)
            if ab is not None:
                bg = wrap(ab - travel)
                b_grad.append(abs(bg))
                toward.append(np.sign(bg) * rate)
            j = int(np.argmin(np.linalg.norm(live - p, axis=1)))
            b_near.append(abs(wrap(math.atan2(live[j, 1] - p[1], live[j, 0] - p[0]) - travel)))
        last = p
    f = lambda v: float(np.mean(v)) if v else float("nan")
    return {"cond": cond, "a": a, "gen": gen, "seed": seed,
            "food": float(sim.food_eaten[0]), "work": float(sim.work[0]), "score": float(sim.score(0)),
            "bearing_grad": f(b_grad), "bearing_near": f(b_near), "turn_toward": f(toward), "centroid_d": f(cent),
            "path": path, "in_path": in_path, "both_rail": rail / steps, "exploded": bool(sim.exploded[0])}


def main() -> None:
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    seeds = [cdr.SEED0 + s for s in range(n_seeds)]
    jobs = [(c, a, g, s) for c, a in CONDS for g in GENS for s in seeds]
    with ProcessPoolExecutor(workers) as pool:
        rows = list(pool.map(bout, jobs, chunksize=8))
    by = {(r["cond"], r["a"], r["gen"], r["seed"]): r for r in rows}
    rng = np.random.default_rng(5)

    def boot(v):
        v = np.asarray(v, float)
        m = np.array([rng.choice(v, len(v)).mean() for _ in range(20000)])
        return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

    L = [f"RBT-67 manipulation check at the top of the ladder -- {POP} ({cdr.POPULATIONS[POP]['run']}), "
         f"{len(GENS)} robots x {n_seeds} seeds from {cdr.SEED0} x {len(CONDS)} conditions = {len(jobs)} bouts",
         f"direction of travel {cdr.POPULATIONS[POP]['drives']}; every bearing is in the travel frame; work_cost {cdr.config(POP).food.work_cost}",
         "",
         f"{'condition':14s} {'a':>4s} | {'items':>6s} {'delta':>7s} {'95% CI (robots)':>17s} {'better':>6s} | {'score':>6s} {'d score':>8s} {'work J':>7s} | "
         f"{'bear grad':>9s} {'bear near':>9s} {'turn toward':>11s} {'centroid m':>10s} | {'in-disc m':>9s} {'rail%':>5s} {'expl':>4s}"]
    summary = {}
    for cond, a in CONDS:
        per, per_s, sub = [], [], []
        for gen in GENS:
            R = [by[(cond, a, gen, s)] for s in seeds]
            B = [by[("base", 0.0, gen, s)] for s in seeds]
            sub += R
            per.append(float(np.mean([r["food"] - b["food"] for r, b in zip(R, B)])))
            per_s.append(float(np.mean([r["score"] - b["score"] for r, b in zip(R, B)])))
        m, lo, hi = boot(per)
        ms, _, _ = boot(per_s)
        g = lambda k: float(np.nanmean([r[k] for r in sub]))
        summary[f"{cond}:{a:g}"] = {"delta": m, "ci": [lo, hi], "per_robot": per, "delta_score": ms,
                                    **{k: g(k) for k in ("food", "score", "work", "bearing_grad", "bearing_near", "turn_toward", "centroid_d", "in_path", "both_rail")},
                                    "exploded": int(sum(r["exploded"] for r in sub))}
        L.append(f"{cond:14s} {a:4.0f} | {g('food'):6.3f} {m:+7.3f} [{lo:+6.3f}, {hi:+6.3f}] {sum(d > 0 for d in per):>3d}/{len(GENS)} | "
                 f"{g('score'):6.3f} {ms:+8.3f} {g('work'):7.1f} | {g('bearing_grad'):9.3f} {g('bearing_near'):9.3f} {g('turn_toward'):+11.4f} {g('centroid_d'):10.3f} | "
                 f"{g('in_path'):9.2f} {100 * g('both_rail'):5.1f} {int(sum(r['exploded'] for r in sub)):4d}")
    L.append("")
    L.append("delta and d score are paired against base on the same seeds, mean over robots, CI bootstrapped over robots.")
    L.append("bear grad / bear near: mean |bearing - travel azimuth| to the smell ascent / the nearest item, rad (pi/2 = 1.571 is")
    L.append("sideways, chance-level for a non-steerer is about 1.57).  turn toward: sign(bearing) x yaw rate, rad/s.  centroid m:")
    L.append("distance to the live-item centroid.  score: items - work_cost x work / 1000, the ecology's fitness quantity.")
    text = "\n".join(L)
    print(text)
    with open(os.path.join(OUT, "manipulation_384.txt"), "w") as f:
        f.write(text + "\n")
    with open(os.path.join(OUT, "manipulation_384.json"), "w") as f:
        json.dump({"population": POP, "seeds": seeds, "conds": CONDS, "summary": summary}, f, indent=1)


if __name__ == "__main__":
    main()
