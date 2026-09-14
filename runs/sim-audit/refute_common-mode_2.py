"""REFUTATION of H1 (common-mode swamping) -- probe_common_mode.py, verdict DEFECT_CONFIRMED.

The claim: the smell field's DC (0.42) swamps its left-right differential (0.041), the spike's
crossed links therefore delivered ~10x more common-mode drive than steering, and REMOVING THE DC
should let a compass earn.  Evidence offered: a zero-common-mode circuit `cmr_c`, which puts
+w*(n1-n2) into BOTH wheel effectors (the yaw axis, since the motors are mirrored), earns
+0.897 items on a 1.516 baseline at w=32, unanimously over 7 robots, with a sign reversal and a
constant-yaw sham both going the other way.

Two things in that argument are untested, and this probe tests them.

(1) IS IT A COMPASS AT ALL?  The winning circuit adds a large, ZERO-MEAN, SLOWLY-VARYING yaw
    wobble (mean |drive| 32*0.041 = 1.3, into effectors whose own |x| is 1.4-2.6).  The only
    "no-smell" control run was a CONSTANT yaw bias, which makes the robot circle -- that is not
    the right null for an oscillating one.  A zero-mean wobble of the same size and the same
    timescale is a classic area-restricted-search / anti-straight-line perturbation that can pay
    in a 3 m disc with no directional information in it whatsoever.
    NULL USED HERE (`surro`): the exact (n1-n2) trace recorded from the paired baseline bout of
    the same robot on the same seed, circularly shifted by half a bout and played back open loop.
    Identical marginal amplitude distribution, identical autocorrelation, still made of smell --
    but no instantaneous relation to where the food is.  If `surro` earns what `grad` earns, the
    result is a wobble, not a compass, and H1's DC story is beside the point.
    Second null (`klino`): the same yaw axis driven by the COMMON mode (n1+n2)/2 minus a constant,
    gain-matched -- smell-modulated turning that carries zero left-right information.

(2) DOES THE DC ACTUALLY MATTER?  H1 says the DC is what breaks the circuit.  Then adding the DC
    back onto the WORKING circuit should break it.  `dcadd` = grad + a constant equal to the
    circuit's own mean drive (1.325), i.e. the same yaw axis carrying signal + DC at 1:1.  If the
    compass survives that, the DC is not the mechanism H1 says it is.

Design: 7 robots (RBT-23/W4b-801 gens 90..590) x 64 PAIRED seeds 9000.. -- the spike's own block,
so baselines come from runs/compass-spike/spike.json and are verified bit-exact against a re-run.
Bootstrap over the 7 robots.  All circuits are injected as a per-tick addition to the effector
bias, which is algebraically identical to the probe's W[dst,src] links (both read the previous
tick's nose activation); `grad` reproducing the probe's per-robot deltas exactly is the check.

No library changes.  usage: ./v/bin/python runs/sim-audit/refute_common-mode_2.py
"""

from __future__ import annotations

import argparse
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
W = 32.0          # the probe's winning magnitude
CBAR = 0.4242     # the probe's measured nose common mode
YAWSHAM = 1.325   # = 32 * mean|n1-n2| : the compass's own mean drive

_CFG = None
_GENO = {}


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def geno(gen):
    if gen not in _GENO:
        _GENO[gen] = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    return _GENO[gen]


def wiring(gen):
    ph = synthesize(geno(gen), cfg().synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.unit.kind == "sensor" and u.unit.source == "food" and u.part in (0, 1, 2):
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return nose, eff


def make_sim(gen, seed):
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    return sim, c


def run(gen, seed, drive):
    """One bout.  `drive(t, n0, n1, n2)` -> the yaw-axis drive s added to BOTH wheel effectors.

    s is added to the effector biases before the tick, using the previous tick's nose
    activations -- exactly what W[eff, nose] links do inside brain.step().
    """
    sim, c = make_sim(gen, seed)
    nose, eff = wiring(gen)
    b = sim.brains[0]
    e1, e2 = eff[1], eff[2]
    b1, b2 = float(b.bias[e1]), float(b.bias[e2])
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_ticks = in_path = 0.0
    near = []
    gtrace = np.zeros(steps)
    strace = np.zeros(steps)
    for t in range(steps):
        n0 = float(b.activation[nose[0]])
        n1 = float(b.activation[nose[1]])
        n2 = float(b.activation[nose[2]])
        gtrace[t] = n1 - n2
        s = 0.0 if drive is None else float(drive(t, n0, n1, n2))
        strace[t] = s
        b.bias[e1] = b1 + s
        b.bias[e2] = b2 + s
        sim.step()
        p = sim.center_of_mass(0)[:2]
        r = float(np.linalg.norm(p))
        in_path += float(np.linalg.norm(p - last)) if r <= disc else 0.0
        last = p.copy()
        if r <= disc:
            in_ticks += 1
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
    food = float(sim.food_eaten[0])
    return {"food": food, "in_disc": in_ticks / steps, "in_path": in_path,
            "items_per_m": food / in_path if in_path > 0.05 else 0.0,
            "near": float(np.mean(near)) if near else float("nan"),
            "gtrace": gtrace, "s_absmean": float(np.abs(strace).mean()),
            "s_mean": float(strace.mean()), "s_std": float(strace.std())}


# --------------------------------------------------------------------------- #
def bout(task):
    gen, seed, cond, k = task
    if cond == "base":
        r = run(gen, seed, None)
    elif cond == "grad":
        r = run(gen, seed, lambda t, n0, n1, n2: W * (n1 - n2))
    elif cond == "dcadd":
        r = run(gen, seed, lambda t, n0, n1, n2: W * (n1 - n2) + YAWSHAM)
    elif cond == "klino":
        r = run(gen, seed, lambda t, n0, n1, n2: k * (0.5 * (n1 + n2) - CBAR))
    elif cond == "surro":
        g = run(gen, seed, None)["gtrace"]          # the paired baseline's own gradient trace
        n = len(g)
        sh = np.roll(g, n // 2)
        r = run(gen, seed, lambda t, n0, n1, n2: W * sh[t])
    else:
        raise ValueError(cond)
    r.pop("gtrace", None)
    r.update(gen=gen, seed=seed, cond=cond)
    return r


def calib(task):
    gen, seed = task
    sim, c = make_sim(gen, seed)
    nose, eff = wiring(gen)
    b = sim.brains[0]
    g, cm = [], []
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        g.append(b.activation[nose[1]] - b.activation[nose[2]])
        cm.append(0.5 * (b.activation[nose[1]] + b.activation[nose[2]]))
    g = np.asarray(g)
    cm = np.asarray(cm)
    n = len(g)

    def ac(x, lag):
        x = x - x.mean()
        return float((x[:-lag] * x[lag:]).sum() / (x * x).sum())
    return {"g_absmean": float(np.abs(g).mean()), "g_std": float(g.std()),
            "g_ac1": ac(g, 1), "g_ac25": ac(g, 25), "g_ac375": ac(g, n // 2),
            "cm_mean": float(cm.mean()),
            "cmdev_absmean": float(np.abs(cm - CBAR).mean()), "cmdev_std": float((cm - CBAR).std())}


def boot(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))), float((m <= 0).mean())


def per_robot(by, cond, seeds, key="food"):
    out = []
    for g in GENS:
        d = [by[(g, s, cond)][key] - by[(g, s, "base")][key]
             for s in seeds if (g, s, cond) in by]
        if d:
            out.append(float(np.nanmean(d)))
    return out


def klino_sweep(workers, nseeds):
    """Is the common-mode null only losing because it was overdriven?  Sweep its gain down.

    `klino` is what the spike's CROSSED circuit would deliver to the yaw axis in a DC-free
    world: the common mode with its offset removed.  If no gain of it earns, then removing the
    DC from the field would not have rescued the crossed circuit.
    """
    seeds = [SEED0 + i for i in range(nseeds)]
    spike = json.load(open("runs/compass-spike/spike.json"))
    sby = {(r["gen"], r["seed"], r["cond"]): r for r in spike["rows"]}
    by = {(g, s, "base"): sby[(g, s, "baseline")] for g in GENS for s in seeds}
    gains = (2.0, 4.0, 8.0)
    tasks = [(g, s, "klino", k) for g in GENS for s in seeds for k in gains]
    print(f"[klino gain sweep] {len(GENS)} robots x {len(seeds)} paired seeds x {len(gains)} gains")
    with Pool(workers) as p:
        rows = p.map(bout, tasks, chunksize=8)
    for r, t in zip(rows, tasks):
        by[(r["gen"], r["seed"], f"k{t[3]:g}")] = r
    print("| klino gain | mean|yaw drive| | Δ items | 95% CI |")
    print("|---|---|---|---|")
    res = {}
    for k in gains:
        lab = f"k{k:g}"
        d = per_robot(by, lab, seeds)
        m, ci, _ = boot(d)
        sa = float(np.mean([by[(g, s, lab)]["s_absmean"] for g in GENS for s in seeds]))
        res[lab] = {"gain": k, "s_absmean": sa, "delta": m, "ci": list(ci), "per_robot": d}
        print(f"| {k:g} | {sa:.3f} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] |")
    j = json.load(open("runs/sim-audit/refute_common-mode_2.json"))
    j["klino_sweep"] = res
    json.dump(j, open("runs/sim-audit/refute_common-mode_2.json", "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--klino-sweep", action="store_true")
    args = ap.parse_args()
    if args.klino_sweep:
        klino_sweep(args.workers, args.seeds)
        raise SystemExit
    T0 = time.time()
    pool = Pool(args.workers)
    seeds = [SEED0 + i for i in range(args.seeds)]
    out = {"run": RUN, "gens": list(GENS), "seeds": [seeds[0], seeds[-1]], "w": W}

    # ---- stage 0: what the gradient signal looks like in time -------------- #
    crows = pool.map(calib, [(g, SEED0 + s) for g in GENS for s in range(4)])
    ca = {k: float(np.mean([r[k] for r in crows])) for k in crows[0]}
    out["calib"] = ca
    print(f"[stage 0] baseline gradient statistics, {len(GENS)} robots x 4 bouts")
    print(f"  n1-n2 : mean|.| {ca['g_absmean']:.4f}  std {ca['g_std']:.4f}"
          f"  ac(1) {ca['g_ac1']:.3f}  ac(25 = 0.5 s) {ca['g_ac25']:.3f}  ac(375 = half bout) {ca['g_ac375']:+.3f}")
    print(f"  common mode mean {ca['cm_mean']:.4f} ; |cm - {CBAR}| mean {ca['cmdev_absmean']:.4f}")
    KL = YAWSHAM / max(ca["cmdev_absmean"], 1e-9)   # gain-match the klinotaxis null to the compass
    out["klino_gain"] = KL
    print(f"  -> klinotaxis null gain k = {KL:.2f} so its mean |yaw drive| matches the compass's {YAWSHAM}")
    print(f"  -> the half-bout shift decorrelates the gradient (ac {ca['g_ac375']:+.3f}), so `surro`"
          f" keeps the amplitude and the timescale and loses the direction", flush=True)

    # ---- stage 1: bit-exactness of this harness against the spike ---------- #
    spike = json.load(open("runs/compass-spike/spike.json"))
    sby = {(r["gen"], r["seed"], r["cond"]): r for r in spike["rows"]}
    chk = pool.map(bout, [(g, SEED0 + s, "base", 0.0) for g in GENS for s in range(8)])
    dif = max(abs(r["food"] - sby[(r["gen"], r["seed"], "baseline")]["food"]) for r in chk)
    out["harness_matches_spike_max_abs_diff"] = float(dif)
    print(f"\n[stage 1] bias-injection harness vs the spike's baseline rows: max |diff| over "
          f"{len(chk)} bouts = {dif:.3g}")

    by = {}
    for g in GENS:
        for s in seeds:
            r = sby[(g, s, "baseline")]
            by[(g, s, "base")] = r
    base = [float(np.mean([by[(g, s, 'base')]["food"] for s in seeds])) for g in GENS]
    print(f"  baseline {np.mean(base):.3f} items  (per robot {[round(b, 2) for b in base]})")

    # ---- stage 2: the compass and its nulls -------------------------------- #
    conds = ["grad", "surro", "klino", "dcadd"]
    tasks = [(g, s, c, KL) for g in GENS for s in seeds for c in conds]
    print(f"\n[stage 2] {len(GENS)} robots x {len(seeds)} PAIRED seeds x {len(conds)} conditions "
          f"= {len(tasks)} bouts (+{len(GENS)*len(seeds)} recording passes for surro)", flush=True)
    rows = pool.map(bout, tasks, chunksize=8)
    pool.close()
    for r in rows:
        by[(r["gen"], r["seed"], r["cond"])] = r

    print(f"  ({time.time()-T0:.0f}s)\n")
    print("| condition | mean|yaw drive| | Δ items | 95% CI | P(Δ≤0) | Δ items/m | Δ near-dist | Δ in-disc |")
    print("|---|---|---|---|---|---|---|---|")
    res = {}
    for c in conds:
        d = per_robot(by, c, seeds)
        m, ci, p = boot(d)
        sa = float(np.mean([by[(g, s, c)]["s_absmean"] for g in GENS for s in seeds]))
        dm = float(np.mean(per_robot(by, c, seeds, "items_per_m")))
        dn = float(np.mean(per_robot(by, c, seeds, "near")))
        di = float(np.mean(per_robot(by, c, seeds, "in_disc")))
        res[c] = {"delta": m, "ci": list(ci), "p_le_0": p, "s_absmean": sa,
                  "d_items_per_m": dm, "d_near": dn, "d_in_disc": di, "per_robot": d}
        print(f"| {c} | {sa:.3f} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {p:.3f} | "
              f"{dm:+.4f} | {dn:+.3f} m | {di:+.4f} |")
    out["result"] = res

    # ---- the contrasts that decide it -------------------------------------- #
    print("\n[contrasts] paired per robot, bootstrap over the 7 robots\n")
    print("| contrast | mean | 95% CI | P(≤0) |")
    print("|---|---|---|---|")
    con = {}
    for a, b_, name in (("grad", "surro", "compass minus matched-wobble null"),
                        ("grad", "klino", "compass minus lateral-info-free null"),
                        ("dcadd", "grad", "cost of adding the DC back onto the compass")):
        v = [x - y for x, y in zip(per_robot(by, a, seeds), per_robot(by, b_, seeds))]
        m, ci, p = boot(v)
        con[f"{a}_minus_{b_}"] = {"mean": m, "ci": list(ci), "p_le_0": p, "per_robot": v}
        print(f"| {a} - {b_} : {name} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {p:.3f} |")
    out["contrasts"] = con

    probe = json.load(open("runs/sim-audit/probe_common_mode.json"))
    ref = probe["headline"]["cmr_c+32.0"]["per_robot"]
    mine = per_robot(by, "grad", seeds)
    out["reproduces_probe_cmr_c32"] = {"probe": ref, "mine": mine,
                                       "max_abs_diff": float(max(abs(a - b_) for a, b_ in zip(ref, mine)))}
    print(f"\n[reproduction] my `grad` vs the probe's cmr_c+32 per-robot deltas: "
          f"max |diff| = {out['reproduces_probe_cmr_c32']['max_abs_diff']:.4g}")

    with open("runs/sim-audit/refute_common-mode_2.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\ntotal {time.time()-T0:.0f}s -> runs/sim-audit/refute_common-mode_2.json")
