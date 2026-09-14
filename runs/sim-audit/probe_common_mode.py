"""H1 -- COMMON-MODE SWAMPING: does a DC-free compass earn what the plain crossed one could not?

The compass spike installed nose(wheel A) -> effector(wheel B) at weight w and found nothing.
The smell field it fed those links has mean 0.33 and a left-right differential of only 0.04, so
the crossed link delivered w*0.33 of common-mode drive for every w*0.04 of steering: 8:1 DC.
A real Braitenberg vehicle reads ~0 with no source nearby and gets the subtraction for free.

So: install the SAME crossed topology with the DC removed -- each wheel effector gets +w from the
opposite nose and -w from its own -- and sweep w far enough up to compensate the 8x smaller signal.

Two families, not one, because the spike's most diagnostic observation is unexplained: `crossed`
and `uncrossed` were behaviourally IDENTICAL (within +/-0.11 everywhere). That is what you see when
the two wheel motors run on MIRRORED sign conventions -- then a same-signed injection into both
effectors is a YAW command, not a forward one, and the crossed/uncrossed distinction collapses into
the (irrelevant) forward channel. Under mirrored motors the brief's circuit steers nothing at all.
So the differential (n1 - n2) is mapped onto the actuator pair TWO ways and both are swept:

  cmr_d :  dctrl1 = -w(n1-n2),  dctrl2 = +w(n1-n2)   <- the brief's circuit (+opposite, -own)
  cmr_c :  dctrl1 = +w(n1-n2),  dctrl2 = +w(n1-n2)   <- the same differential, same-signed

Both inject exactly zero common mode. They differ only in which actuator-space direction the smell
gradient is steered into, and a measured open-loop drive test (stage 0) predicts, in advance, which
of the two is the yaw axis. If the behavioural sweep agrees with that prediction, the sim can
express a compass and the spike's null was a wiring/DC artefact; if neither family earns, the null
is about the world, not the circuit.

Stages
  0  instrumentation + open-loop drive convention, ~free
  A  screen, full sweep, 7 robots x 8 seeds on a DISJOINT seed block (8000..) -- locates the regime,
     never a headline claim, and the settings it picks were chosen on seeds the headline never sees
  B  headline, 7 robots x 64 PAIRED seeds (9000.., the spike's own block so `crossed` is comparable
     row-for-row via runs/compass-spike/spike.json), bootstrap over the 7 robots

No library changes. usage: ./v/bin/python runs/sim-audit/probe_common_mode.py
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
SCREEN_GENS = (90, 290, 490, 590)   # the screen only has to pick settings; the headline uses all seven
MAGS = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0)
HEAD_SEED0 = 9000      # the spike's block -- paired with its baseline/crossed rows
SCREEN_SEED0 = 8000    # disjoint: selection happens here, never on the headline seeds

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def geno(gen):
    return Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")


def wiring(gen):
    """Phenotype indices of the two wheel noses and the two wheel effectors (same as the spike)."""
    ph = synthesize(geno(gen), cfg().synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return nose, eff


def install(brain, nose, eff, fam, sgn, m):
    """Add the circuit to the live brain. Every family injects zero common mode."""
    W = brain.W
    if fam == "baseline":
        return
    w = sgn * m
    if fam == "yawbias":   # sham: the same yaw-axis drive, constant, with no smell in it at all
        brain.bias[eff[1]] += w
        brain.bias[eff[2]] += w
        return
    if fam == "cmr_d":        # +w from the opposite nose, -w from its own  (the brief's circuit)
        W[eff[1], nose[2]] += w
        W[eff[1], nose[1]] -= w
        W[eff[2], nose[1]] += w
        W[eff[2], nose[2]] -= w
    elif fam == "cmr_c":      # the same differential (n1-n2), same-signed into both effectors
        W[eff[1], nose[1]] += w
        W[eff[1], nose[2]] -= w
        W[eff[2], nose[1]] += w
        W[eff[2], nose[2]] -= w
    else:
        raise ValueError(fam)


def label(c):
    fam, sgn, m = c
    return fam if sgn is None else f"{fam}{'+' if sgn > 0 else '-'}{m}"


# --------------------------------------------------------------------------- #
# stage 0: what the effectors are actually doing, and which way the motors run
# --------------------------------------------------------------------------- #
def heading(sim):
    R = sim.data.xmat[sim.robots[0].root_body].reshape(3, 3)
    return float(np.arctan2(R[1, 0], R[0, 0]))


def drive_test(task):
    """Open loop: kill the brain, clamp the two wheel ctrls, see what the body does."""
    gen, seed, c1, c2 = task
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = wiring(gen)
    b = sim.brains[0]
    b.W[:] = 0.0
    b.bias[:] = 0.0
    b.bias[eff[1]] = 4.0 * c1          # tanh(4) = 0.9993 -> ctrl ~= +/-1
    b.bias[eff[2]] = 4.0 * c2
    p0 = sim.center_of_mass(0)[:2].copy()
    h = heading(sim)
    yaw = 0.0
    for _ in range(200):               # 4 s
        sim.step()
        h2 = heading(sim)
        yaw += float(np.arctan2(np.sin(h2 - h), np.cos(h2 - h)))
        h = h2
    return {"gen": gen, "ctrl": (c1, c2), "yaw": yaw,
            "disp": float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0))}


def instrument(task):
    """Baseline bout, recording the noses and the effectors' pre-activation x (tanh input)."""
    gen, seed = task
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = wiring(gen)
    b = sim.brains[0]
    rec = {k: [] for k in ("n1", "n2", "x1", "x2", "a1", "a2")}
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        rec["n1"].append(b.activation[nose[1]])
        rec["n2"].append(b.activation[nose[2]])
        rec["x1"].append(b._prev_input[eff[1]])   # the x that produced this tick's effector output
        rec["x2"].append(b._prev_input[eff[2]])
        rec["a1"].append(b.activation[eff[1]])
        rec["a2"].append(b.activation[eff[2]])
    r = {k: np.asarray(v) for k, v in rec.items()}
    d = r["n1"] - r["n2"]
    gain1, gain2 = 1 - np.tanh(r["x1"]) ** 2, 1 - np.tanh(r["x2"]) ** 2
    return {"gen": gen, "seed": seed,
            "nose_mean": float(0.5 * (r["n1"] + r["n2"]).mean()),
            "diff_absmean": float(np.abs(d).mean()), "diff_absmax": float(np.abs(d).max()),
            "x1_absmean": float(np.abs(r["x1"]).mean()), "x2_absmean": float(np.abs(r["x2"]).mean()),
            "gain1": float(gain1.mean()), "gain2": float(gain2.mean()),
            "sat_frac": float(((np.abs(r["x1"]) > 2) | (np.abs(r["x2"]) > 2)).mean()),
            "a1_mean": float(r["a1"].mean()), "a2_mean": float(r["a2"].mean())}


# --------------------------------------------------------------------------- #
# bouts
# --------------------------------------------------------------------------- #
def bout(task):
    gen, seed, cond = task
    fam, sgn, m = cond
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, eff = wiring(gen)
    install(sim.brains[0], nose, eff, fam, sgn, m)

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
    return {"gen": gen, "seed": seed, "cond": label(cond), "food": food,
            "in_disc": in_ticks / steps, "in_path": in_path,
            "items_per_m": food / in_path if in_path > 0.05 else 0.0,
            "near": float(np.mean(near)) if near else float("nan"),
            "exploded": bool(sim.exploded[0])}


def per_robot_delta(by, cond, gens, seeds, key="food"):
    out = []
    for g in gens:
        d = [by[(g, s, cond)][key] - by[(g, s, "baseline")][key]
             for s in seeds if (g, s, cond) in by and (g, s, "baseline") in by]
        if d:
            out.append(float(np.nanmean(d)))
    return out


def boot_ci(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))), float((m <= 0).mean())


def addendum(workers, nseeds):
    """Sham + dose-response, paired against the spike's baseline rows (bit-identical to ours)."""
    t0 = time.time()
    hseeds = [HEAD_SEED0 + i for i in range(nseeds)]
    yawmag = 1.325   # = 32 * mean|n1-n2| : the compass's own mean drive, made constant
    conds = [("cmr_c", +1, 16.0), ("yawbias", +1, yawmag), ("yawbias", -1, yawmag)]
    tasks = [(g, s, c) for g in GENS for s in hseeds for c in conds]
    print(f"[addendum] {len(GENS)} robots x {len(hseeds)} PAIRED seeds x {len(conds)} conditions "
          f"= {len(tasks)} bouts", flush=True)
    with Pool(workers) as p:
        rows = p.map(bout, tasks, chunksize=8)
    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    spike = json.load(open("runs/compass-spike/spike.json"))
    for r in spike["rows"]:
        if r["cond"] == "baseline":
            by[(r["gen"], r["seed"], "baseline")] = r
    print("\n| condition | Δ items | 95% CI | P(Δ≤0) | Δ items/m | Δ near-dist |")
    print("|---|---|---|---|---|---|")
    res = {}
    for c in conds:
        lab = label(c)
        d = per_robot_delta(by, lab, GENS, hseeds)
        m, ci, pv = boot_ci(d)
        dm = float(np.mean(per_robot_delta(by, lab, GENS, hseeds, "items_per_m")))
        dn = float(np.mean(per_robot_delta(by, lab, GENS, hseeds, "near")))
        res[lab] = {"delta": m, "ci": list(ci), "p_le_0": pv, "d_items_per_m": dm,
                    "d_near": dn, "per_robot": d}
        print(f"| {lab} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {pv:.3f} | {dm:+.4f} | {dn:+.3f} m |")
    j = json.load(open("runs/sim-audit/probe_common_mode.json"))
    j["addendum"] = res
    json.dump(j, open("runs/sim-audit/probe_common_mode.json", "w"), indent=1)
    print(f"\ntotal {time.time()-t0:.0f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--addendum", action="store_true")
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--screen-seeds", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if args.addendum:
        addendum(args.workers, args.seeds)
        raise SystemExit
    T0 = time.time()
    pool = Pool(args.workers)
    out = {"run": RUN, "gens": list(GENS), "mags": list(MAGS)}

    # ---- stage 0a: what the smell signal and the effectors look like ------- #
    tasks = [(g, HEAD_SEED0 + s) for g in GENS for s in range(4)]
    inst = pool.map(instrument, tasks)
    agg = {k: float(np.mean([r[k] for r in inst])) for k in inst[0] if k not in ("gen", "seed")}
    out["instrument"] = agg
    print(f"[stage 0a] noses+effectors, {len(GENS)} robots x 4 bouts")
    print(f"  nose common mode      {agg['nose_mean']:.4f}")
    print(f"  |n1-n2| mean / max    {agg['diff_absmean']:.4f} / {agg['diff_absmax']:.4f}"
          f"   ({100*agg['diff_absmean']/agg['nose_mean']:.1f}% of common mode)")
    print(f"  effector |x| (tanh input) mean  {agg['x1_absmean']:.2f} / {agg['x2_absmean']:.2f}")
    print(f"  effector tanh gain 1-tanh^2     {agg['gain1']:.3f} / {agg['gain2']:.3f}"
          f"   ({100*agg['sat_frac']:.0f}% of ticks with |x|>2)")
    print(f"  mean effector output            {agg['a1_mean']:+.3f} / {agg['a2_mean']:+.3f}", flush=True)

    # ---- stage 0b: open-loop drive convention ------------------------------ #
    combos = [(+1, +1), (-1, -1), (+1, -1), (-1, +1)]
    dtasks = [(g, HEAD_SEED0 + s, c1, c2) for g in GENS for s in range(2) for (c1, c2) in combos]
    drows = pool.map(drive_test, dtasks)
    dsum = {}
    for c1, c2 in combos:
        v = [r for r in drows if r["ctrl"] == (c1, c2)]
        dsum[f"{c1:+d},{c2:+d}"] = {"yaw": float(np.mean([r["yaw"] for r in v])),
                                    "absyaw": float(np.mean([abs(r["yaw"]) for r in v])),
                                    "disp": float(np.mean([r["disp"] for r in v]))}
    out["drive"] = dsum
    print(f"\n[stage 0b] open-loop drive, brain killed, ctrl clamped, 4 s, {len(GENS)} robots x 2 starts")
    print("  ctrl(w1,w2) | mean |yaw| rad | mean net displacement m")
    for k, v in dsum.items():
        print(f"  {k:11s} | {v['absyaw']:13.2f} | {v['disp']:.3f}")
    same = 0.5 * (dsum["+1,+1"]["absyaw"] + dsum["-1,-1"]["absyaw"])
    opp = 0.5 * (dsum["+1,-1"]["absyaw"] + dsum["-1,+1"]["absyaw"])
    same_d = 0.5 * (dsum["+1,+1"]["disp"] + dsum["-1,-1"]["disp"])
    opp_d = 0.5 * (dsum["+1,-1"]["disp"] + dsum["-1,+1"]["disp"])
    yaw_axis = "same" if same > opp else "opposite"
    predicted = "cmr_c" if yaw_axis == "same" else "cmr_d"
    out["yaw_axis"] = yaw_axis
    out["predicted_compass_family"] = predicted
    print(f"  SAME-signed ctrl:     |yaw| {same:.2f} rad, travel {same_d:.3f} m")
    print(f"  OPPOSITE-signed ctrl: |yaw| {opp:.2f} rad, travel {opp_d:.3f} m")
    print(f"  -> the YAW axis is the {yaw_axis.upper()}-signed ctrl direction; "
          f"the steering family is {predicted}", flush=True)

    # ---- stage A: screen, disjoint seeds ----------------------------------- #
    sseeds = [SCREEN_SEED0 + i for i in range(args.screen_seeds)]
    conds = [("baseline", None, 0.0)] + [(f, s, m) for f in ("cmr_d", "cmr_c") for m in MAGS for s in (+1, -1)]
    tasks = [(g, s, c) for g in SCREEN_GENS for s in sseeds for c in conds]
    print(f"\n[stage A] screen: {len(SCREEN_GENS)} robots x {len(sseeds)} DISJOINT seeds x {len(conds)} conditions "
          f"= {len(tasks)} bouts", flush=True)
    rows = pool.map(bout, tasks, chunksize=8)
    by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    print(f"  ({time.time()-T0:.0f}s elapsed)  baseline "
          f"{np.mean([by[(g,s,'baseline')]['food'] for g in SCREEN_GENS for s in sseeds]):.2f} items")
    print("  |   w |    cmr_d +   |    cmr_d -   |    cmr_c +   |    cmr_c -   |")
    screen = {}
    for m in MAGS:
        cells = []
        for fam in ("cmr_d", "cmr_c"):
            for s in (+1, -1):
                lab = label((fam, s, m))
                d = float(np.mean(per_robot_delta(by, lab, SCREEN_GENS, sseeds)))
                screen[lab] = d
                cells.append(f"{d:+.3f}")
        print(f"  | {m:4g} | " + " | ".join(f"{c:>12s}" for c in cells) + " |")
    out["screen"] = screen

    # ---- pick the headline conditions on the screen ------------------------ #
    other = "cmr_c" if predicted == "cmr_d" else "cmr_d"

    def parse(lab):
        fam = lab.split("+")[0].split("-")[0]
        rest = lab[len(fam):]
        return (fam, +1 if rest[0] == "+" else -1, float(rest[1:]))

    pred_l = sorted([label((predicted, s, m)) for m in MAGS for s in (+1, -1)], key=lambda l: -screen[l])
    best = pred_l[0]
    bf, bs, bm = parse(best)
    runner = next((l for l in pred_l[1:] if parse(l)[2] != bm), pred_l[1])   # a second magnitude
    mirror = label((bf, -bs, bm))                                            # the opposite sign
    other_best = max([label((other, s, m)) for m in MAGS for s in (+1, -1)], key=lambda l: screen[l])

    head_conds = [("baseline", None, 0.0)]
    for lab in dict.fromkeys([best, runner, mirror, other_best]):
        head_conds.append(parse(lab))
    print(f"\n[stage B] chosen on the screen's disjoint seeds: {[label(c) for c in head_conds[1:]]}")

    # ---- stage B: headline, 64 paired seeds -------------------------------- #
    hseeds = [HEAD_SEED0 + i for i in range(args.seeds)]
    tasks = [(g, s, c) for g in GENS for s in hseeds for c in head_conds]
    print(f"  {len(GENS)} robots x {len(hseeds)} PAIRED seeds x {len(head_conds)} conditions "
          f"= {len(tasks)} bouts", flush=True)
    hrows = pool.map(bout, tasks, chunksize=8)
    hby = {(r["gen"], r["seed"], r["cond"]): r for r in hrows}
    pool.close()

    # the spike's own rows: same run, same robots, same 64 seeds -> directly comparable
    spike = json.load(open("runs/compass-spike/spike.json"))
    sby = {(r["gen"], r["seed"], r["cond"]): r for r in spike["rows"]}
    agree = [abs(hby[(g, s, "baseline")]["food"] - sby[(g, s, "baseline")]["food"])
             for g in GENS for s in hseeds if (g, s, "baseline") in sby]
    print(f"\n  reproducibility check vs the spike's baseline rows: max |diff| over "
          f"{len(agree)} bouts = {max(agree):.3g}")
    out["baseline_reproduces_spike_max_abs_diff"] = float(max(agree))

    base = [float(np.mean([hby[(g, s, "baseline")]["food"] for s in hseeds])) for g in GENS]
    print(f"  baseline yield {np.mean(base):.3f} items (per robot {[round(b,2) for b in base]})")

    print(f"\n[result] paired vs baseline, {len(hseeds)} seeds, bootstrap over the {len(GENS)} robots\n")
    print("| condition | source | Δ items | 95% CI | P(Δ≤0) | Δ items/m | Δ near-dist |")
    print("|---|---|---|---|---|---|---|")
    res = {}

    def report(lab, src, table, tag):
        d = per_robot_delta(table, lab, GENS, hseeds)
        if not d:
            return
        m, ci, p = boot_ci(d)
        dm = float(np.mean(per_robot_delta(table, lab, GENS, hseeds, "items_per_m")))
        dn = float(np.mean(per_robot_delta(table, lab, GENS, hseeds, "near")))
        res[lab] = {"source": tag, "delta": m, "ci": list(ci), "p_le_0": p,
                    "d_items_per_m": dm, "d_near": dn, "per_robot": d}
        print(f"| {lab} | {src} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {p:.3f} | {dm:+.4f} | {dn:+.3f} m |")

    for c in head_conds[1:]:
        report(label(c), "this probe", hby, "probe")
    for lab in ("crossed+2.0", "crossed-2.0", "crossed+8.0", "crossed-8.0", "uncrossed+8.0", "blanked"):
        if (GENS[0], hseeds[0], lab) in sby:
            report(lab, "spike (same seeds)", sby, "spike")
    out["headline"] = res
    out["baseline_by_gen"] = {g: b for g, b in zip(GENS, base)}

    with open("runs/sim-audit/probe_common_mode.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\ntotal {time.time()-T0:.0f}s -> runs/sim-audit/probe_common_mode.json")
