"""REFUTATION CHECK for probe_common_mode.py's headline (cmr_c, w=32, +0.897 items).

Lens: is the measurement like-for-like?

The probe's stage-0a instrumentation recorded diff_absmean = mean|n1-n2| = 0.0414 but NEVER
recorded the SIGNED mean of (n1-n2).  Its winning circuit adds w*(n1-n2) to the pre-tanh input of
BOTH wheel effectors, i.e. straight onto the measured yaw axis.  If the two wheel noses are
systematically unequal -- and the audit brief's own single-bout figures say they are (nose1 mean
0.3403 vs nose2 0.3163, a signed gap of 0.024 against mean|n1-n2| = 0.0399) -- then most of what
w*(n1-n2) delivers is a CONSTANT turn bias, not a gradient.  "Zero common mode" was verified for
the NOSE PAIR, never for the injected DRIVE.

The probe's only no-smell control ("yawbias") is a constant yaw bias of +/-1.325 = 32*mean|n1-n2|,
which overshoots the true DC (32*signed mean) and is therefore not magnitude-matched.

So: split the probe's own winning circuit, exactly, into the two pieces that sum to it pre-tanh.

  dc<w>  : bias[eff1] += w*mu ; bias[eff2] += w*mu          (mu = per-robot signed mean of n1-n2,
           estimated on a DISJOINT seed block; carries NO smell at all)
  ac<w>  : the probe's cmr_c links at w, then bias[eff] -= w*mu on both  (the smell-modulated
           fluctuation with its constant removed)

By construction ac<w> + dc<w> = cmr_c<w> in effector pre-activation.  If dc alone earns what
cmr_c earns and ac earns nothing, "the sim can express a compass" is a constant-turn artefact.
If ac carries it, the probe's headline survives this attack.

Also reported: in-disc path and in-disc dwell, to test whether the probe's supporting
"Delta items/m" is a real efficiency gain or path collapse.

usage: ./v/bin/python runs/sim-audit/refute_common-mode_0.py [--stage1] [--seeds 64]
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
HEAD_SEED0 = 9000     # the probe's / spike's own headline block
CAL_SEED0 = 8000      # disjoint: mu is estimated here, never on the headline seeds
W = 32.0

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def geno(gen):
    return Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")


def wiring(gen):
    """Identical to probe_common_mode.wiring / spike.wiring."""
    ph = synthesize(geno(gen), cfg().synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return nose, eff


def calib(task):
    """Baseline bout; record the SIGNED differential the probe never looked at."""
    gen, seed = task
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = wiring(gen)
    b = sim.brains[0]
    d = []
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        d.append(b.activation[nose[1]] - b.activation[nose[2]])
    d = np.asarray(d)
    return {"gen": gen, "seed": seed, "mean": float(d.mean()), "absmean": float(np.abs(d).mean()),
            "sd": float(d.std()), "boutmean": float(d.mean())}


def bout(task):
    gen, seed, cond, mu = task
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = wiring(gen)
    b = sim.brains[0]

    if cond != "baseline":
        if cond in ("cmr_c", "ac"):                     # the probe's winning links, verbatim
            b.W[eff[1], nose[1]] += W
            b.W[eff[1], nose[2]] -= W
            b.W[eff[2], nose[1]] += W
            b.W[eff[2], nose[2]] -= W
        if cond == "ac":                                # ... with its constant taken back out
            b.bias[eff[1]] -= W * mu
            b.bias[eff[2]] -= W * mu
        if cond == "dc":                                # only the constant, no smell whatsoever
            b.bias[eff[1]] += W * mu
            b.bias[eff[2]] += W * mu

    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_ticks = in_path = 0.0
    near = []
    for _ in range(steps):
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
    return {"gen": gen, "seed": seed, "cond": cond, "food": food,
            "in_disc": in_ticks / steps, "in_path": in_path,
            "items_per_m": food / in_path if in_path > 0.05 else 0.0,
            "near": float(np.mean(near)) if near else float("nan"),
            "exploded": bool(sim.exploded[0])}


def per_robot(by, cond, seeds, key="food"):
    out = []
    for g in GENS:
        d = [by[(g, s, cond)][key] - by[(g, s, "baseline")][key] for s in seeds]
        out.append(float(np.nanmean(d)))
    return out


def boot_ci(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))), float((m <= 0).mean())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--cal-seeds", type=int, default=16)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stage1", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    pool = Pool(args.workers)
    out = {"run": RUN, "gens": list(GENS), "w": W}

    # ---- stage 1: the signed decomposition of the differential -------------- #
    cseeds = [CAL_SEED0 + i for i in range(args.cal_seeds)]
    crows = pool.map(calib, [(g, s) for g in GENS for s in cseeds])
    MU = {}
    print(f"[stage 1] signed decomposition of (n1-n2), {len(GENS)} robots x {len(cseeds)} DISJOINT seeds")
    print("| robot | signed mean mu | mean|n1-n2| | |mu|/mean|d| | within-bout sd | w*mu (const yaw drive) |")
    print("|---|---|---|---|---|---|")
    for g in GENS:
        v = [r for r in crows if r["gen"] == g]
        mu = float(np.mean([r["mean"] for r in v]))
        am = float(np.mean([r["absmean"] for r in v]))
        sd = float(np.mean([r["sd"] for r in v]))
        MU[g] = mu
        print(f"| {g} | {mu:+.4f} | {am:.4f} | {abs(mu)/am:.2f} | {sd:.4f} | {W*mu:+.3f} |")
    amall = float(np.mean([r["absmean"] for r in crows]))
    muall = float(np.mean([r["mean"] for r in crows]))
    print(f"  pooled: signed mean {muall:+.4f}, mean|d| {amall:.4f}, "
          f"|signed|/|abs| = {abs(muall)/amall:.2f}")
    out["mu"] = MU
    out["calib_pooled"] = {"signed_mean": muall, "absmean": amall}
    print(f"  ({time.time()-t0:.0f}s)", flush=True)
    if args.stage1:
        pool.close()
        raise SystemExit

    # ---- stage 2: split the probe's winner into DC and AC ------------------- #
    hseeds = [HEAD_SEED0 + i for i in range(args.seeds)]
    conds = ["baseline", "cmr_c", "dc", "ac"]
    tasks = [(g, s, c, MU[g]) for g in GENS for s in hseeds for c in conds]
    print(f"\n[stage 2] {len(GENS)} robots x {len(hseeds)} PAIRED seeds x {len(conds)} conditions "
          f"= {len(tasks)} bouts", flush=True)
    rows = pool.map(bout, tasks, chunksize=8)
    pool.close()
    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}

    # pairing / determinism check against the spike's own baseline rows
    sby = {(r["gen"], r["seed"], r["cond"]): r for r in json.load(open("runs/compass-spike/spike.json"))["rows"]}
    agree = [abs(by[(g, s, "baseline")]["food"] - sby[(g, s, "baseline")]["food"])
             for g in GENS for s in hseeds if (g, s, "baseline") in sby]
    print(f"  baseline vs spike.json: max |diff| over {len(agree)} bouts = {max(agree):.3g}")
    out["baseline_reproduces_spike_max_abs_diff"] = float(max(agree))
    base = [float(np.mean([by[(g, s, "baseline")]["food"] for s in hseeds])) for g in GENS]
    print(f"  baseline {np.mean(base):.3f} items")

    print(f"\n| condition | Δ items | 95% CI | P(Δ≤0) | robots up | Δ items/m | Δ in-path m | Δ in-disc | Δ near | expl |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    res = {}
    for cnd in conds[1:]:
        d = per_robot(by, cnd, hseeds)
        m, ci, p = boot_ci(d)
        dm = float(np.mean(per_robot(by, cnd, hseeds, "items_per_m")))
        dp = float(np.mean(per_robot(by, cnd, hseeds, "in_path")))
        dd = float(np.mean(per_robot(by, cnd, hseeds, "in_disc")))
        dn = float(np.mean(per_robot(by, cnd, hseeds, "near")))
        ex = float(np.mean([by[(g, s, cnd)]["exploded"] for g in GENS for s in hseeds]))
        res[cnd] = {"delta": m, "ci": list(ci), "p_le_0": p, "per_robot": d,
                    "d_items_per_m": dm, "d_in_path": dp, "d_in_disc": dd, "d_near": dn,
                    "exploded": ex}
        print(f"| {cnd} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {p:.3f} | {sum(x>0 for x in d)}/7 "
              f"| {dm:+.4f} | {dp:+.2f} | {dd:+.3f} | {dn:+.3f} | {100*ex:.0f}% |")
    for cnd in conds[1:]:
        print(f"  {cnd:6s} per-robot Δ: {[round(x,3) for x in res[cnd]['per_robot']]}")
    # additivity: does dc + ac account for cmr_c?
    add = float(np.mean(res["dc"]["per_robot"]) + np.mean(res["ac"]["per_robot"]))
    print(f"\n  dc + ac = {add:+.3f}   vs   cmr_c = {res['cmr_c']['delta']:+.3f}")
    out["stage2"] = res
    out["baseline"] = float(np.mean(base))
    json.dump(out, open("runs/sim-audit/refute_common-mode_0.json", "w"), indent=1)
    print(f"\ntotal {time.time()-t0:.0f}s -> runs/sim-audit/refute_common-mode_0.json")
