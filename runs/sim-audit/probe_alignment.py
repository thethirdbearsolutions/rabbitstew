"""H3 -- IS THE WHEEL-NOSE DIFFERENTIAL ALIGNED WITH THE DIRECTION TO FOOD?

The compass spike installed crossed nose->wheel links and earned nothing.  The
already-measured field statistics say the left-right differential is only 12% of the
common mode, which is small but not zero.  Small is survivable (turn the gain up);
MISALIGNED is not.  A Braitenberg compass needs sign(n1 - n2) to track which side of
the robot the food is on.  If that sign is at chance, no wiring of this sensor pair
could ever steer and the spike's null is a property of the sensor, not of the circuit.

WHAT IS MEASURED, on real unmodified bouts (no injected weights, no lesions):
  at every control step, before the step so the state is exactly the one the sensors
  read that tick,
    diff      = n1 - n2, the two wheel noses, recomputed with Simulation._intensity
                (verified in stage 0 to equal sim.sensor_values() to 1e-15)
    lat_near  = sin(bearing) to the NEAREST LIVE item in the robot's own frame,
                + = the item is on wheel 1's side
    lat_grad  = the same lateral component of the ANALYTIC gradient of the smell field
                (sum_i exp(-d_i/decay) (x_i - p) / (d_i decay)) -- the direction the
                sensor pair is actually differencing, which is the pile's pull, not
                the nearest item's
    dist      = range to that nearest live item
Sides are VERIFIED, not assumed: stage 0 reads the chassis geom rotation matrix, the
drive-wheel and castor offsets in the body frame, and the direction the body actually
travels, and asserts which physical side each nose is on.

Standing rules: 7 robots x 64 PAIRED seeds (the spike's own 9000.. block), the ROBOT is
the unit of analysis, intervals bootstrap over robots.  No library changes.

usage: ./v/bin/python runs/sim-audit/probe_alignment.py [--seeds 64] [--stage0-only]
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
SEED0 = 9000          # the compass spike's paired block
BINS = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, np.inf)

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def make(gen, seed):
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sp = spawn_layout(1, c, seed)
    sim = Simulation([g], c, spawns=sp)
    sim.set_food_seed(seed)
    return sim, c, sp[0]


def nose_units(sim):
    """Phenotype unit index of the food sensor on each drive wheel."""
    ph = sim.phenotypes[0]
    return {u.part: i for i, u in enumerate(ph.units)
            if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food"}


def frame(sim):
    """(nose1, nose2, chassis pos, forward_hat, left_hat) in world xy, from the chassis geom."""
    idx = sim.robots[0]
    d = sim.data
    R = d.geom_xmat[idx.geoms[0]].reshape(3, 3)      # body -> world; columns are the body axes
    fwd = R[:2, 0].copy()
    left = R[:2, 1].copy()
    fwd /= max(np.linalg.norm(fwd), 1e-12)
    left /= max(np.linalg.norm(left), 1e-12)
    p1 = d.geom_xpos[idx.geoms[1]][:2].copy()
    p2 = d.geom_xpos[idx.geoms[2]][:2].copy()
    return p1, p2, d.geom_xpos[idx.geoms[0]][:2].copy(), fwd, left


def bout(task):
    """One real bout; per-step alignment record."""
    gen, seed = task
    sim, c, spawn = make(gen, seed)
    idx = sim.robots[0]
    decay = c.food.decay
    steps = int(round(c.duration / c.control_dt))
    out = np.full((steps, 7), np.nan, dtype=np.float32)
    prev = None
    for t in range(steps):
        p1, p2, pc, fwd, left = frame(sim)
        n1 = sim._intensity(sim.data.geom_xpos[idx.geoms[1]], sim.food_pos)
        n2 = sim._intensity(sim.data.geom_xpos[idx.geoms[2]], sim.food_pos)
        p = 0.5 * (p1 + p2)                                   # the sensor pair's own midpoint
        live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
        if len(live):
            v = live - p
            dd = np.linalg.norm(v, axis=1)
            j = int(np.argmin(dd))
            r = float(dd[j])
            vh = v[j] / max(r, 1e-12)
            lat_near, fwd_near = float(vh @ left), float(vh @ fwd)
            w = np.exp(-dd / decay) / (np.maximum(dd, 1e-9) * decay)
            gvec = (w[:, None] * v).sum(axis=0)               # uphill direction of the smell field
            gn = float(np.linalg.norm(gvec))
            lat_grad = float((gvec / gn) @ left) if gn > 1e-12 else np.nan
        else:
            r = lat_near = fwd_near = lat_grad = np.nan
        travel = np.nan if prev is None else float((p - prev) @ fwd)
        prev = p.copy()
        out[t] = (n1 - n2, lat_near, lat_grad, r, fwd_near, travel, float(np.linalg.norm(pc)))
        sim.step()
    return gen, seed, out, bool(sim.exploded[0]), float(sim.food_eaten[0])


def boot(vals, draws=20000, seed=5):
    rng = np.random.default_rng(seed)
    v = np.asarray(vals, float)
    v = v[np.isfinite(v)]
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def stage0():
    print("=" * 88)
    print("STAGE 0 -- body frame, which nose is on which side, and where the robot actually goes")
    print("=" * 88)
    sim, c, spawn = make(590, SEED0)
    idx, d = sim.robots[0], sim.data
    R = d.geom_xmat[idx.geoms[0]].reshape(3, 3)
    pc = d.geom_xpos[idx.geoms[0]]
    print(f"spawn yaw {spawn.yaw:+.4f} rad -> ({np.cos(spawn.yaw):+.4f}, {np.sin(spawn.yaw):+.4f});"
          f"  chassis geom local +x in world ({R[0,0]:+.4f}, {R[1,0]:+.4f})"
          f"  -> local +x IS the spawn heading: {np.allclose(R[:2,0], [np.cos(spawn.yaw), np.sin(spawn.yaw)], atol=1e-3)}")
    print("part offsets in the chassis frame (fwd, left, up), metres:")
    for k, gid in enumerate(idx.geoms):
        o = R.T @ (d.geom_xpos[gid] - pc)
        tag = {0: "chassis (nose 0)", 1: "DRIVE wheel part 1 (nose 1)", 2: "DRIVE wheel part 2 (nose 2)",
               3: "castor", 4: "castor"}[k]
        print(f"   part {k}: ({o[0]:+.3f}, {o[1]:+.3f}, {o[2]:+.3f})   {tag}")
    o1 = R.T @ (d.geom_xpos[idx.geoms[1]] - pc)
    o2 = R.T @ (d.geom_xpos[idx.geoms[2]] - pc)
    print(f"   nose separation {np.linalg.norm(o1 - o2):.4f} m;"
          f"  part 1 is on the {'LEFT' if o1[1] > 0 else 'RIGHT'} (+left offset {o1[1]:+.3f}),"
          f"  part 2 on the {'LEFT' if o2[1] > 0 else 'RIGHT'} ({o2[1]:+.3f})")
    oc = 0.5 * (R.T @ (d.geom_xpos[idx.geoms[3]] - pc) + R.T @ (d.geom_xpos[idx.geoms[4]] - pc))
    print(f"   drive wheels sit {o1[0] - oc[0]:+.3f} m along +x of the castors -> nominal 'front' is +x")

    # my _intensity call vs what the brain is actually handed
    nu = nose_units(sim)
    b = sim.brains[0]
    kk = {s.unit: k for k, s in enumerate(b.sensors)}
    worst = 0.0
    for t in range(40):
        vals = sim.sensor_values(0, sim.contact_bodies())
        mine = (sim._intensity(d.geom_xpos[idx.geoms[1]], sim.food_pos),
                sim._intensity(d.geom_xpos[idx.geoms[2]], sim.food_pos))
        theirs = (vals[kk[nu[1]]], vals[kk[nu[2]]])
        worst = max(worst, abs(mine[0] - theirs[0]), abs(mine[1] - theirs[1]))
        sim.step()
    print(f"   recomputed noses vs sim.sensor_values(): max abs difference over 40 ticks = {worst:.2e}")

    print("\ndirection of travel in the body frame, 8 seeds per robot (net metres):")
    print(f"   {'robot':>8s} {'fwd (+x)':>10s} {'left (+y)':>10s}   travel")
    for gen in GENS:
        f = l = 0.0
        for s in range(8):
            sim2, c2, _ = make(gen, SEED0 + s)
            i2, d2 = sim2.robots[0], sim2.data
            last = d2.geom_xpos[i2.geoms[0]].copy()
            for _ in range(int(round(c2.duration / c2.control_dt))):
                sim2.step()
                RR = d2.geom_xmat[i2.geoms[0]].reshape(3, 3)
                p = d2.geom_xpos[i2.geoms[0]]
                step = RR.T @ (p - last)
                last = p.copy()
                f += step[0]
                l += step[1]
        print(f"   gen {gen:>4d} {f:10.2f} {l:10.2f}   {'NOSES LEAD (drives +x)' if f > 0 else 'NOSES TRAIL (drives -x, castors first)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stage0-only", action="store_true")
    a = ap.parse_args()
    stage0()
    if a.stage0_only:
        return
    seeds = [SEED0 + i for i in range(a.seeds)]
    tasks = [(g, s) for g in GENS for s in seeds]
    print("\n" + "=" * 88)
    print(f"STAGE 1 -- {len(GENS)} robots x {len(seeds)} paired seeds = {len(tasks)} real bouts")
    print("=" * 88, flush=True)
    t0 = time.time()
    with Pool(a.workers) as p:
        res = p.map(bout, tasks, chunksize=4)
    print(f"collected in {time.time() - t0:.0f}s", flush=True)

    per = {g: [] for g in GENS}
    eaten, expl = {g: [] for g in GENS}, 0
    for gen, seed, arr, ex, food in res:
        per[gen].append(arr)
        eaten[gen].append(food)
        expl += int(ex)
    data = {g: np.concatenate(v, axis=0) for g, v in per.items()}
    allrows = np.concatenate(list(data.values()), axis=0)
    print(f"{len(allrows)} control steps recorded; {expl} exploded bouts; "
          f"mean items {np.mean([np.mean(eaten[g]) for g in GENS]):.2f}")

    def stats(arr):
        diff, lat_n, lat_g, dist = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]
        ok = np.isfinite(lat_n) & np.isfinite(diff)
        d, ln, lg, r = diff[ok], lat_n[ok], lat_g[ok], dist[ok]
        acc_n = float(np.mean(np.sign(d) == np.sign(ln)))
        acc_g = float(np.mean(np.sign(d) == np.sign(lg)))
        # balanced accuracy guards against any left/right base-rate imbalance
        L, Rt = ln > 0, ln < 0
        bal = 0.5 * (np.mean(d[L] > 0) + np.mean(d[Rt] < 0))
        return dict(acc_near=acc_n, acc_grad=acc_g, bal_near=float(bal),
                    r_near=float(np.corrcoef(d, ln)[0, 1]), r_grad=float(np.corrcoef(d, lg)[0, 1]),
                    mean_absdiff=float(np.mean(np.abs(d))), frac_left=float(np.mean(L)),
                    n=int(ok.sum()), dist=r, d=d, ln=ln, lg=lg)

    S = {g: stats(data[g]) for g in GENS}
    print("\nper robot (its own bouts pooled):")
    print(f"{'robot':>8s} {'steps':>8s} {'sign acc vs':>12s} {'balanced':>9s} {'sign acc vs':>12s} "
          f"{'corr(diff,':>11s} {'corr(diff,':>11s} {'mean|n1-n2|':>12s}")
    print(f"{'':>8s} {'':>8s} {'nearest':>12s} {'':>9s} {'gradient':>12s} {'sin brg)':>11s} {'grad lat)':>11s} {'':>12s}")
    for g in GENS:
        s = S[g]
        print(f"gen {g:>4d} {s['n']:8d} {100*s['acc_near']:11.1f}% {100*s['bal_near']:8.1f}% "
              f"{100*s['acc_grad']:11.1f}% {s['r_near']:11.3f} {s['r_grad']:11.3f} {s['mean_absdiff']:12.4f}")

    for key, name in (("acc_near", "sign(n1-n2) predicts the side of the NEAREST LIVE ITEM"),
                      ("acc_grad", "sign(n1-n2) predicts the side of the FIELD GRADIENT"),
                      ("r_near", "corr(n1-n2, sin bearing to nearest)"),
                      ("r_grad", "corr(n1-n2, lateral of field gradient)")):
        m, lo, hi = boot([S[g][key] for g in GENS])
        unit = "%" if key.startswith("acc") else ""
        sc = 100 if key.startswith("acc") else 1
        print(f"\n{name}\n   {sc*m:.2f}{unit}   95% CI over the {len(GENS)} robots [{sc*lo:.2f}, {sc*hi:.2f}]{unit}"
              + ("   (chance = 50%)" if key.startswith("acc") else ""))

    print("\nsign accuracy vs range to the nearest live item (pooled steps; CI over robots):")
    print(f"{'range (m)':>12s} {'% of steps':>11s} {'acc vs nearest':>15s} {'95% CI':>16s} {'acc vs grad':>12s} {'mean|n1-n2|':>12s}")
    tot = sum(S[g]["n"] for g in GENS)
    for lo_, hi_ in zip(BINS[:-1], BINS[1:]):
        accs, accg, shares, mags = [], [], [], []
        for g in GENS:
            s = S[g]
            m = (s["dist"] >= lo_) & (s["dist"] < hi_)
            if m.sum() < 30:
                continue
            accs.append(float(np.mean(np.sign(s["d"][m]) == np.sign(s["ln"][m]))))
            accg.append(float(np.mean(np.sign(s["d"][m]) == np.sign(s["lg"][m]))))
            mags.append(float(np.mean(np.abs(s["d"][m]))))
            shares.append(m.sum())
        if not accs:
            continue
        mm, l_, h_ = boot(accs)
        lbl = f"{lo_:.1f}-{hi_:.1f}" if np.isfinite(hi_) else f">{lo_:.1f}"
        print(f"{lbl:>12s} {100*sum(shares)/tot:10.1f}% {100*mm:14.1f}% "
              f"[{100*l_:6.1f},{100*h_:6.1f}] {100*np.mean(accg):11.1f}% {np.mean(mags):12.4f}")

    # ---- stage 2: is the information USABLE -- does the sign hold still, and does gating on
    # magnitude clean it up?  A sign that flips every tick cannot be steered on.
    print("\nstage 2 -- temporal stability of sign(n1-n2), per bout (control tick = "
          f"{cfg().control_dt*1000:.0f} ms):")
    print(f"{'robot':>8s} {'flips/s':>9s} {'mean run':>10s} {'acc |diff| Q1':>14s} {'Q2':>7s} {'Q3':>7s} {'Q4 (largest)':>14s}")
    fl_all, rl_all, q4_all = [], [], []
    for g in GENS:
        flips, runs = [], []
        for arr in per[g]:
            sgn = np.sign(arr[:, 0])
            ch = int(np.count_nonzero(np.diff(sgn) != 0))
            flips.append(ch / (len(sgn) * cfg().control_dt))
            runs.append(len(sgn) * cfg().control_dt / (ch + 1))
        s_ = S[g]
        a = np.abs(s_["d"])
        qs = np.quantile(a, [0.25, 0.5, 0.75])
        accs = []
        for lo_, hi_ in ((0, qs[0]), (qs[0], qs[1]), (qs[1], qs[2]), (qs[2], np.inf)):
            m = (a >= lo_) & (a < hi_)
            accs.append(float(np.mean(np.sign(s_["d"][m]) == np.sign(s_["ln"][m]))))
        fl_all.append(float(np.mean(flips))); rl_all.append(float(np.mean(runs))); q4_all.append(accs[3])
        print(f"gen {g:>4d} {np.mean(flips):9.2f} {np.mean(runs)*1000:8.0f}ms "
              f"{100*accs[0]:13.1f}% {100*accs[1]:6.1f}% {100*accs[2]:6.1f}% {100*accs[3]:13.1f}%")
    m, lo, hi = boot(fl_all); print(f"   sign flips per second: {m:.2f} [{lo:.2f}, {hi:.2f}]")
    m, lo, hi = boot(rl_all); print(f"   mean time the sign holds: {1000*m:.0f} ms [{1000*lo:.0f}, {1000*hi:.0f}] ms")
    m, lo, hi = boot(q4_all); print(f"   accuracy on the largest-|diff| quartile: {100*m:.1f}% [{100*lo:.1f}, {100*hi:.1f}]%")

    out = {"run": RUN, "gens": list(GENS), "seeds": seeds,
           "flips_per_s": fl_all, "mean_run_s": rl_all, "acc_bigdiff_q4": q4_all,
           "per_robot": {str(g): {k: v for k, v in S[g].items() if not isinstance(v, np.ndarray)} for g in GENS}}
    json.dump(out, open("runs/sim-audit/probe_alignment.json", "w"), indent=1)
    print("\nwrote runs/sim-audit/probe_alignment.json")


if __name__ == "__main__":
    main()
