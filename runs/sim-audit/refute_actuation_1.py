"""REFUTATION CHECK for H5 / "the spike wired the wrong quadrant".

The audited finding makes three linked assertions:

  (i)  GEOMETRY.  The two drive hinges are antiparallel, so forward drive is the
       OPPOSITE-sign command pair and S = e1+e2 is the turn channel.
  (ii) MECHANISM.  Because the spike adds the SAME sign to both nose->wheel links,
       its circuit injects w*(n1+n2) into the turn channel: "at w=2 the circuit
       commands -1.24 rad/s, a full-rate spin in one fixed direction", and that is
       why the spike saw damage.
  (iii)CONSEQUENCE.  The spike's null is therefore "a null about the wrong circuit";
       the compass lives in the opposite-sign quadrant and should be re-derived.

(i) is cheap to re-verify and I do (part 1).  (ii) is a LINEAR prediction that ignores
tanh saturation and closed-loop feedback -- test it by measuring the ACTUAL paired
change in S and in yaw rate (part 2), and by running a smell-free twin of the spike's
circuit that injects exactly the same DC and nothing else ("dctwin").  If the twin
reproduces the spike condition, the circuit really is just its common mode; if the
spike condition is far below its linear prediction, the "-1.24 rad/s spin" story is
overstated.  (iii) is the load-bearing one -- test it by building the circuit the
finding says was never sampled: OPPOSITE-sign nose->wheel links with each nose's DC
removed at the bias, so the gradient goes into the turn channel and the common mode
goes nowhere.  Magnitude 10, chosen because the finding's own arithmetic says w~9.4
is what buys 0.2 rad/s of gradient-driven turn.

7 robots x 64 PAIRED seeds x 5 conditions.  Robot is the unit; CIs bootstrap over
robots.  No library code touched.
"""
from __future__ import annotations

import json
import time
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
SEED0 = 9000
NSEED = 64
LEFT, RIGHT = 1, 2
W_COMPASS = 10.0
W_SPIKE = 2.0

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def units(gen):
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg().synthesis)
    eff, nose = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (LEFT, RIGHT) and u.unit.kind == "effector":
            eff[u.part] = i
        if u.part in (LEFT, RIGHT) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
    return eff, nose


def yaw_of(sim):
    R = sim.data.xmat[sim.robots[0].root_body].reshape(3, 3)
    return float(np.arctan2(R[1, 0], R[0, 0]))


# --------------------------------------------------------------------- part 1 #
def open_loop(task):
    """Independent re-check of the geometry claim: constant ctrl pair, W zeroed."""
    seed, e1, e2 = task
    c = replace(cfg(), random_start=True, world=replace(cfg().world, terrain="flat"))
    g = Genotype.load(f"{RUN}/conventional/best_gen0590.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    eff, _ = units(590)
    b = sim.brains[0]
    b.W[:, :] = 0.0
    b.bias[:] = 0.0
    b.bias[eff[LEFT]] = float(np.arctanh(np.clip(e1, -0.999, 0.999)))
    b.bias[eff[RIGHT]] = float(np.arctanh(np.clip(e2, -0.999, 0.999)))
    idx = sim.robots[0]
    steps = int(round(c.duration / c.control_dt))
    yaw = yaw_of(sim)
    tot = 0.0
    p0 = sim.center_of_mass(0)[:2].copy()
    last = p0.copy()
    path = 0.0
    c1 = c2 = 0.0
    for _ in range(steps):
        sim.step()
        y = yaw_of(sim)
        tot += (y - yaw + np.pi) % (2 * np.pi) - np.pi
        yaw = y
        p = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(p - last))
        last = p.copy()
        c1 += float(sim.data.ctrl[idx.actuators[(LEFT, 0)]])
        c2 += float(sim.data.ctrl[idx.actuators[(RIGHT, 0)]])
    T = steps * c.control_dt
    return {"e1": e1, "e2": e2, "yaw_rate": tot / T, "net": float(np.linalg.norm(last - p0)),
            "path": path, "ctrl1": c1 / steps, "ctrl2": c2 / steps}


# --------------------------------------------------------------------- part 2 #
def bout(task):
    gen, seed, cond, nb1, nb2 = task
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    eff, nose = units(gen)
    br = sim.brains[0]
    W, B = br.W, br.bias
    w = W_COMPASS
    if cond == "spike2":            # exactly runs/compass-spike/spike.py, crossed +2
        W[eff[RIGHT], nose[LEFT]] += W_SPIKE
        W[eff[LEFT], nose[RIGHT]] += W_SPIKE
    elif cond == "dctwin":          # smell-free twin: same mean DC, zero smell content
        B[eff[LEFT]] += W_SPIKE * nb2
        B[eff[RIGHT]] += W_SPIKE * nb1
    elif cond == "compass":         # opposite-sign links, each nose's DC removed
        W[eff[LEFT], nose[LEFT]] -= w
        B[eff[LEFT]] += w * nb1
        W[eff[RIGHT], nose[RIGHT]] += w
        B[eff[RIGHT]] -= w * nb2
    elif cond == "anti":            # same thing, other orientation
        W[eff[LEFT], nose[LEFT]] += w
        B[eff[LEFT]] -= w * nb1
        W[eff[RIGHT], nose[RIGHT]] -= w
        B[eff[RIGHT]] += w * nb2

    idx = sim.robots[0]
    aL, aR = idx.actuators[(LEFT, 0)], idx.actuators[(RIGHT, 0)]
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    e1s, e2s, n1s, n2s, dy = [], [], [], [], []
    yaw = yaw_of(sim)
    tot = 0.0
    last = sim.center_of_mass(0)[:2].copy()
    in_path = 0.0
    near = []
    for _ in range(steps):
        sim.step()
        e1s.append(float(sim.data.ctrl[aL]))
        e2s.append(float(sim.data.ctrl[aR]))
        n1s.append(float(br.activation[nose[LEFT]]))
        n2s.append(float(br.activation[nose[RIGHT]]))
        y = yaw_of(sim)
        d = (y - yaw + np.pi) % (2 * np.pi) - np.pi
        tot += d
        yaw = y
        dy.append(d / c.control_dt)
        p = sim.center_of_mass(0)[:2]
        if float(np.linalg.norm(p)) <= disc:
            in_path += float(np.linalg.norm(p - last))
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
        last = p.copy()
    e1, e2 = np.array(e1s), np.array(e2s)
    n1, n2 = np.array(n1s), np.array(n2s)
    S = e1 + e2
    dy = np.array(dy)
    g_ = n1 - n2
    ct = float(np.corrcoef(dy, g_)[0, 1]) if dy.std() > 1e-9 and g_.std() > 1e-9 else float("nan")
    return {"gen": gen, "seed": seed, "cond": cond,
            "food": float(sim.food_eaten[0]),
            "S_mean": float(S.mean()), "S_std": float(S.std()),
            "D_mean": float((e1 - e2).mean()),
            "yaw_rate": tot / (steps * c.control_dt),
            "abs_yaw": float(np.abs(dy).mean()),
            "n1": float(n1.mean()), "n2": float(n2.mean()),
            "ndiff": float(np.abs(g_).mean()), "ncommon": float((n1 + n2).mean()),
            "corr_turn_gradient": ct,
            "sat1": float(np.mean(np.abs(e1) > 0.99)), "sat2": float(np.mean(np.abs(e2) > 0.99)),
            "in_path": in_path, "near": float(np.mean(near)) if near else float("nan"),
            "exploded": bool(sim.exploded[0])}


def boot(v, n=20000, seed=5):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    rng = np.random.default_rng(seed)
    m = rng.choice(v, size=(n, len(v))).mean(axis=1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


if __name__ == "__main__":
    t0 = time.time()
    out = {}
    seeds = [SEED0 + i for i in range(NSEED)]

    print("=" * 76)
    print("1.  INDEPENDENT RE-CHECK OF THE GEOMETRY CLAIM (open loop, flat, 6 seeds)")
    print("=" * 76)
    corners = [(1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0)]
    with Pool(4) as p:
        r1 = p.map(open_loop, [(SEED0 + s, a, b) for a, b in corners for s in range(6)])
    out["geometry"] = {}
    print(f"   {'e1':>5s} {'e2':>5s} | {'ctrl1':>6s} {'ctrl2':>6s} | {'yaw rate':>9s} {'net':>7s} {'path':>7s}")
    for a, b in corners:
        rs = [r for r in r1 if r["e1"] == a and r["e2"] == b]
        v = {k: float(np.mean([r[k] for r in rs])) for k in ("yaw_rate", "net", "path", "ctrl1", "ctrl2")}
        out["geometry"][f"{a}|{b}"] = v
        print(f"   {a:5.1f} {b:5.1f} | {v['ctrl1']:6.3f} {v['ctrl2']:6.3f} | {v['yaw_rate']:9.3f} "
              f"{v['net']:6.2f}m {v['path']:6.2f}m")

    print()
    print("=" * 76)
    print(f"2.  BASELINE PASS ({len(GENS)} robots x {NSEED} paired seeds) -> per-robot nose DC")
    print("=" * 76)
    with Pool(4) as p:
        rb = p.map(bout, [(g, s, "baseline", 0.0, 0.0) for g in GENS for s in seeds], chunksize=8)
    nb = {g: (float(np.mean([r["n1"] for r in rb if r["gen"] == g])),
              float(np.mean([r["n2"] for r in rb if r["gen"] == g]))) for g in GENS}
    for g in GENS:
        rs = [r for r in rb if r["gen"] == g]
        print(f"   gen {g}: food {np.mean([r['food'] for r in rs]):.3f}  n1bar {nb[g][0]:.4f}  "
              f"n2bar {nb[g][1]:.4f}  mean|n1-n2| {np.mean([r['ndiff'] for r in rs]):.4f}  "
              f"S {np.mean([r['S_mean'] for r in rs]):+.3f}  yaw {np.mean([r['yaw_rate'] for r in rs]):+.3f}")
    out["nose_dc"] = {str(g): nb[g] for g in GENS}

    CONDS = ("spike2", "dctwin", "compass", "anti")
    tasks = [(g, s, c, nb[g][0], nb[g][1]) for g in GENS for s in seeds for c in CONDS]
    print(f"\n   running {len(tasks)} injected bouts ...", flush=True)
    with Pool(4) as p:
        ri = p.map(bout, tasks, chunksize=8)
    rows = rb + ri
    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}

    def per_robot(cond, key):
        return [float(np.nanmean([by[(g, s, cond)][key] for s in seeds])) for g in GENS]

    def paired(cond, key):
        return [float(np.nanmean([by[(g, s, cond)][key] - by[(g, s, "baseline")][key] for s in seeds]))
                for g in GENS]

    print()
    print("=" * 76)
    print("3.  LEVELS  (robot is the unit; 64 paired seeds each)")
    print("=" * 76)
    print(f"   {'cond':>9s} | {'food':>6s} {'S mean':>7s} {'yawrate':>8s} {'|yaw|':>6s} "
          f"{'sat1':>5s} {'sat2':>5s} {'|n1-n2|':>8s} {'corr(yaw,n1-n2)':>16s}")
    lev = {}
    for cond in ("baseline",) + CONDS:
        v = {k: float(np.mean(per_robot(cond, k))) for k in
             ("food", "S_mean", "yaw_rate", "abs_yaw", "sat1", "sat2", "ndiff", "ncommon",
              "corr_turn_gradient", "in_path", "near")}
        lev[cond] = v
        print(f"   {cond:>9s} | {v['food']:6.3f} {v['S_mean']:+7.3f} {v['yaw_rate']:+8.3f} "
              f"{v['abs_yaw']:6.3f} {v['sat1']:5.2f} {v['sat2']:5.2f} {v['ndiff']:8.4f} "
              f"{v['corr_turn_gradient']:16.4f}")
    out["levels"] = lev

    print()
    print("=" * 76)
    print("4.  PAIRED DELTAS vs BASELINE  (bootstrap over the 7 robots)")
    print("=" * 76)
    out["deltas"] = {}
    for cond in CONDS:
        out["deltas"][cond] = {}
        line = []
        for key in ("food", "S_mean", "yaw_rate", "abs_yaw", "corr_turn_gradient"):
            m, lo, hi = boot(paired(cond, key))
            out["deltas"][cond][key] = {"mean": m, "ci": [lo, hi]}
            line.append(f"{key}={m:+.3f}[{lo:+.3f},{hi:+.3f}]")
        print(f"   {cond:>9s}  " + "  ".join(line))

    print()
    print("=" * 76)
    print("5.  DOES THE FINDING'S LINEAR MECHANISM PREDICT WHAT spike2 ACTUALLY DID?")
    print("=" * 76)
    nc = lev["baseline"]["ncommon"]
    kS_flat, kS_rand = -0.6223, -0.4239
    pred_dS = W_SPIKE * nc
    dS = out["deltas"]["spike2"]["S_mean"]["mean"]
    dyaw = out["deltas"]["spike2"]["yaw_rate"]["mean"]
    print(f"   claim: spike w=2 injects  dS = w*mean(n1+n2) = {pred_dS:+.3f}")
    print(f"          -> dyaw = {kS_flat:.4f}*dS = {kS_flat * pred_dS:+.3f} rad/s (flat gain, the claim's headline)")
    print(f"          -> dyaw = {kS_rand:.4f}*dS = {kS_rand * pred_dS:+.3f} rad/s (random-terrain gain, the run's own world)")
    print(f"   MEASURED paired dS   = {dS:+.3f}  ({100 * dS / pred_dS:.0f}% of the linear prediction)")
    print(f"   MEASURED paired dyaw = {dyaw:+.3f} rad/s "
          f"({100 * dyaw / (kS_flat * pred_dS):.0f}% of the claim's -1.24)")
    dtw = out["deltas"]["dctwin"]
    print(f"   smell-free DC twin: dS = {dtw['S_mean']['mean']:+.3f}, dyaw = {dtw['yaw_rate']['mean']:+.3f}, "
          f"d food = {dtw['food']['mean']:+.3f} [{dtw['food']['ci'][0]:+.3f},{dtw['food']['ci'][1]:+.3f}]")
    print(f"   spike2            : d food = {out['deltas']['spike2']['food']['mean']:+.3f} "
          f"[{out['deltas']['spike2']['food']['ci'][0]:+.3f},{out['deltas']['spike2']['food']['ci'][1]:+.3f}]")
    dd = [a - b for a, b in zip(paired("spike2", "food"), paired("dctwin", "food"))]
    m, lo, hi = boot(dd)
    print(f"   spike2 MINUS its smell-free twin: d food = {m:+.3f} [{lo:+.3f},{hi:+.3f}] "
          f"<- how much of the spike's damage needed smell at all")
    out["mechanism"] = {"pred_dS": pred_dS, "meas_dS": dS, "meas_dyaw": dyaw,
                        "pred_dyaw_flat": kS_flat * pred_dS, "pred_dyaw_random": kS_rand * pred_dS,
                        "spike_minus_twin_food": {"mean": m, "ci": [lo, hi]}}

    print()
    print("=" * 76)
    print("6.  THE CIRCUIT THE FINDING SAYS WAS NEVER SAMPLED  (opposite sign, DC removed, w=10)")
    print("=" * 76)
    print(f"   predicted gradient turn amplitude = |kS| * w * mean|n1-n2| = "
          f"{abs(kS_rand) * W_COMPASS * lev['baseline']['ndiff']:.3f} rad/s (random-terrain gain)")
    for cond in ("compass", "anti"):
        d = out["deltas"][cond]
        print(f"   {cond:>8s}: d food = {d['food']['mean']:+.3f} [{d['food']['ci'][0]:+.3f},{d['food']['ci'][1]:+.3f}]"
              f"   d corr(yaw,n1-n2) = {d['corr_turn_gradient']['mean']:+.4f} "
              f"[{d['corr_turn_gradient']['ci'][0]:+.4f},{d['corr_turn_gradient']['ci'][1]:+.4f}]"
              f"   d|yaw| = {d['abs_yaw']['mean']:+.3f}")
    cm = [a - b for a, b in zip(per_robot("compass", "corr_turn_gradient"),
                                per_robot("anti", "corr_turn_gradient"))]
    m2, lo2, hi2 = boot(cm)
    print(f"   compass MINUS anti, corr(yawrate, n1-n2) = {m2:+.4f} [{lo2:+.4f},{hi2:+.4f}] "
          f"<- must be > 0 if the wiring steers by smell at all")
    fd = [a - b for a, b in zip(per_robot("compass", "food"), per_robot("anti", "food"))]
    m3, lo3, hi3 = boot(fd)
    print(f"   compass MINUS anti, food                 = {m3:+.3f} [{lo3:+.3f},{hi3:+.3f}]")
    out["orientation_test"] = {"corr_diff": {"mean": m2, "ci": [lo2, hi2]},
                               "food_diff": {"mean": m3, "ci": [lo3, hi3]}}

    ex = float(np.mean([r["exploded"] for r in rows]))
    out["exploded_frac"] = ex
    out["n_bouts"] = len(rows)
    print(f"\n   {len(rows)} bouts, exploded fraction {100 * ex:.2f}%, "
          f"elapsed {time.time() - t0:.0f}s")
    with open("runs/sim-audit/refute_actuation_1.json", "w") as f:
        json.dump({"out": out, "rows": rows}, f, indent=1)
    print("wrote runs/sim-audit/refute_actuation_1.json")
