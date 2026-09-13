"""REFUTATION ATTEMPT vs H6 (probe_installation.py).

H6 says: the body's drive convention is anti-symmetric (translation = ctrl1-ctrl2,
rotation = ctrl1+ctrl2), therefore spike.py's same-signed crossed/uncrossed installs
both inject the IDENTICAL turn command w(n1+n2) and put "exactly zero gradient
information on the steering axis ... a mathematical identity, not a null result".

That algebra is done in PRE-ACTIVATION space and treats the two effectors as having
the same gain.  They do not.  H6's own section E measured mean x1 = -0.488 and
mean x2 = +2.579 on the unmodified robot -- sech^2 gains differing by ~35x.  With
g1 != g2 the turn response to the nose gradient is

    dR/d(delta) = g1*A1 + g2*A2,   n1 = nbar+delta, n2 = nbar-delta
    crossed   -> w*(g2-g1)      uncrossed -> w*(g1-g2)      oppA -> -w*(g1+g2)

so crossed and uncrossed differ by 2w|g1-g2| on the steering axis, and if the gains
are as lopsided as H6 measured, |g1-g2| ~ |g1+g2| -- i.e. the spike's crossed wiring
would carry essentially as much gradient steering as H6's "corrected" oppA.

Sections:
  1  structural re-verification of the drive convention + linearity of the ctrl map
  2  realized per-tick gain asymmetry and gradient sensitivity of the turn command,
     on REAL bouts with REAL brains (7 robots x 12 paired seeds), plus a realized
     regression of the turn command on common and differential smell
  3  behavioural falsification: H6's own veer test, re-run in gain-asymmetric
     operating regimes.  If H6 is right, crossed and uncrossed veer identically in
     every regime.  If the gains matter, they veer OPPOSITELY when g1 != g2.

usage: ./v/bin/python runs/sim-audit/refute_installation_0.py
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
_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def geno(gen):
    return Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")


def wiring(gen):
    ph = synthesize(geno(gen), cfg().synthesis)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    return ph, nose, eff


def install(W, nose, eff, fam, w):
    e1, e2, n1, n2 = eff[1], eff[2], nose[1], nose[2]
    if fam == "baseline":
        return
    if fam == "spike_crossed":
        W[e2, n1] += w; W[e1, n2] += w
    elif fam == "spike_uncrossed":
        W[e1, n1] += w; W[e2, n2] += w
    elif fam == "oppA":
        W[e1, n2] += w; W[e2, n1] -= w
    elif fam == "oppB":
        W[e1, n1] += w; W[e2, n2] -= w
    else:
        raise ValueError(fam)


CONDS = [("baseline", 0.0), ("spike_crossed", 2.0), ("spike_uncrossed", 2.0),
         ("oppA", 2.0), ("oppB", 2.0)]


def lab(fam, w):
    return "baseline" if fam == "baseline" else f"{fam}{w:g}"


# --------------------------------------------------------------------------- #
# 2. realized gain asymmetry / gradient sensitivity on real bouts
# --------------------------------------------------------------------------- #
def trace(task):
    gen, fam, w, seed = task
    c = replace(cfg(), random_start=True)
    ph, nose, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    br = sim.brains[0]
    install(br.W, nose, eff, fam, w)
    e1, e2, n1, n2 = eff[1], eff[2], nose[1], nose[2]
    # sensitivity of each effector's pre-activation to the differential / common mode
    A1 = br.W[e1, n1] - br.W[e1, n2]
    A2 = br.W[e2, n1] - br.W[e2, n2]
    S1 = br.W[e1, n1] + br.W[e1, n2]
    S2 = br.W[e2, n1] + br.W[e2, n2]
    rec = []
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        a = br.activation
        x = br.W @ a + br.bias
        rec.append((a[n1], a[n2], x[e1], x[e2], a[e1], a[e2]))
    r = np.array(rec)
    nn1, nn2, x1, x2, c1, c2 = (r[:, i] for i in range(6))
    g1 = 1.0 / np.cosh(x1) ** 2
    g2 = 1.0 / np.cosh(x2) ** 2
    dRd = g1 * A1 + g2 * A2          # turn command response to the gradient
    dTd = g1 * A1 - g2 * A2
    dRs = g1 * S1 + g2 * S2          # turn command response to common-mode smell
    R = c1 + c2
    # realized regression R ~ a + bs*(n1+n2) + bd*(n1-n2)
    X = np.column_stack([np.ones(len(R)), nn1 + nn2, nn1 - nn2])
    coef, *_ = np.linalg.lstsq(X, R, rcond=None)
    return dict(gen=gen, cond=lab(fam, w), seed=seed,
                g1=float(g1.mean()), g2=float(g2.mean()),
                A1=float(A1), A2=float(A2), S1=float(S1), S2=float(S2),
                dRd=float(dRd.mean()), absdRd=float(np.abs(dRd).mean()),
                dTd=float(dTd.mean()), dRs=float(dRs.mean()),
                bd=float(coef[2]), bs=float(coef[1]),
                delta=float(np.mean(np.abs(nn1 - nn2))), nbar=float(np.mean(nn1 + nn2)),
                food=float(sim.food_eaten[0]))


# --------------------------------------------------------------------------- #
# 3. veer test in gain-asymmetric regimes
# --------------------------------------------------------------------------- #
REGIMES = {                     # (bias e1, bias e2) -> ctrl, gains
    "sym":   (+0.70, -0.70),    # H6's regime: g1 == g2
    "asymA": (+2.60, -0.485),   # g2 >> g1
    "asymB": (+0.485, -2.60),   # g1 >> g2   <-- matches the real robots (x1 small, x2 big)
}


def veer_cfg():
    c = cfg()
    return replace(c, world=replace(c.world, terrain="flat"),
                   food=replace(c.food, items=1, eat_radius=0.02, clearance=0.0, regrow=False),
                   random_start=False, duration=8.0)


def veer(task):
    gen, reg, fam, w, side = task
    c = veer_cfg()
    ph, nose, eff = wiring(gen)
    from rabbitstew.world import Spawn
    sim = Simulation([geno(gen)], c, spawns=[Spawn(position=(0.0, 0.0, 0.0), yaw=0.0)])
    sim.set_food_seed(1)
    item = np.array([[2.5, side * 1.2]])
    sim.food_pos = item.copy()
    sim.food_spots = item.copy()
    sim.food_alive = np.ones(1, dtype=bool)
    sim.food_timer = np.zeros(1)
    br = sim.brains[0]
    br.W[:, :] = 0.0
    br.bias[:] = 0.0
    b1, b2 = REGIMES[reg]
    br.bias[eff[1]] = b1
    br.bias[eff[2]] = b2
    install(br.W, nose, eff, fam, w)
    rb = sim.robots[0]
    R0 = sim.data.xmat[rb.root_body].reshape(3, 3).copy()
    p0 = sim.center_of_mass(0)[:2].copy()
    mind = 1e9
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        mind = min(mind, float(np.linalg.norm(sim.center_of_mass(0)[:2] - item[0])))
    d = sim.center_of_mass(0)[:2] - p0
    return dict(gen=gen, reg=reg, cond=lab(fam, w), side=side,
                toward=float(side * (R0[:2, 1] @ d)), fwd=float(R0[:2, 0] @ d), min_dist=mind)


def boot_ci(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


if __name__ == "__main__":
    T0 = time.time()
    out = {}
    W_ = 4

    # ---------------- 1. structural check of the drive convention ---------- #
    print("=" * 78)
    print("1. DRIVE CONVENTION -- structural re-verification")
    print("=" * 78)
    c = replace(cfg(), random_start=True)
    sim = Simulation([geno(590)], c, spawns=spawn_layout(1, c, SEED0))
    m, d = sim.model, sim.data
    acts = dict(sim.robots[0].actuators)
    axes = {}
    for (part, dof), aid in acts.items():
        jid = int(m.actuator_trnid[aid, 0])
        bid = int(m.jnt_bodyid[jid])
        ax_world = d.xmat[bid].reshape(3, 3) @ m.jnt_axis[jid]
        axes[part] = ax_world
        print(f"  actuator {aid} drives part {part} joint {jid} (body {bid}); "
              f"hinge axis in world = {np.round(ax_world, 3)}")
    dot = float(axes[1] @ axes[2])
    print(f"  => dot(axis1, axis2) = {dot:+.3f}  "
          f"({'ANTI-PARALLEL: same-signed ctrl counter-rotates the wheels' if dot < -0.9 else 'NOT anti-parallel'})")
    out["axis_dot"] = dot
    print("  H6's section C conclusion is structurally correct: same-signed ctrl = spin.")

    # ---------------- 2. realized gain asymmetry --------------------------- #
    print()
    print("=" * 78)
    print("2. REALIZED GAIN ASYMMETRY AND GRADIENT SENSITIVITY (real brains, real bouts)")
    print("   7 robots x 12 paired seeds; per-tick g = sech^2(x); dR/ddelta = g1*A1 + g2*A2")
    print("=" * 78)
    seeds = [SEED0 + i for i in range(12)]
    tasks = [(g, fam, w, s) for g in GENS for s in seeds for fam, w in CONDS]
    with Pool(W_) as p:
        trows = p.map(trace, tasks, chunksize=8)
    print(f"  {len(tasks)} bouts in {time.time() - T0:.0f}s\n")
    print(f"  {'condition':18s} {'mean g1':>8s} {'mean g2':>8s} {'|g1-g2|':>8s} {'g1+g2':>7s} "
          f"{'dR/dd':>9s} {'|dR/dd|':>8s} {'dR/dnbar':>9s} {'reg bd':>9s}")
    tsum = {}
    for fam, w in CONDS:
        L = lab(fam, w)
        sel = [r for r in trows if r["cond"] == L]
        per_robot_bd = [float(np.mean([r["bd"] for r in sel if r["gen"] == g])) for g in GENS]
        mbd, lo, hi = boot_ci(per_robot_bd)
        row = dict(g1=float(np.mean([r["g1"] for r in sel])), g2=float(np.mean([r["g2"] for r in sel])),
                   dRd=float(np.mean([r["dRd"] for r in sel])),
                   absdRd=float(np.mean([r["absdRd"] for r in sel])),
                   dRs=float(np.mean([r["dRs"] for r in sel])),
                   bd=mbd, bd_ci=[lo, hi],
                   delta=float(np.mean([r["delta"] for r in sel])),
                   nbar=float(np.mean([r["nbar"] for r in sel])),
                   food=float(np.mean([r["food"] for r in sel])))
        tsum[L] = row
        print(f"  {L:18s} {row['g1']:8.4f} {row['g2']:8.4f} {abs(row['g1']-row['g2']):8.4f} "
              f"{row['g1']+row['g2']:7.4f} {row['dRd']:+9.4f} {row['absdRd']:8.4f} "
              f"{row['dRs']:+9.4f} {mbd:+9.4f} [{lo:+.3f},{hi:+.3f}]")
    out["trace"] = tsum
    b = tsum["baseline"]
    print(f"\n  baseline per-tick gains: g1={b['g1']:.4f} g2={b['g2']:.4f} -> ratio {b['g1']/max(b['g2'],1e-9):.1f}x")
    print(f"  mean|n1-n2| = {b['delta']:.4f}   mean(n1+n2) = {b['nbar']:.4f}")
    ref = abs(tsum["oppA2"]["dRd"])
    for L in ("spike_crossed2", "spike_uncrossed2", "oppB2"):
        print(f"  |dR/ddelta| of {L:18s} = {abs(tsum[L]['dRd']):.4f}  "
              f"= {100*abs(tsum[L]['dRd'])/max(ref,1e-9):5.1f}% of oppA2's, "
              f"sign {'SAME as' if np.sign(tsum[L]['dRd'])==np.sign(tsum['oppA2']['dRd']) else 'OPPOSITE to'} oppA2")

    # ---------------- 3. veer in asymmetric regimes ------------------------ #
    print()
    print("=" * 78)
    print("3. VEER TEST IN GAIN-ASYMMETRIC REGIMES (H6's own test, three operating points)")
    print("   positive = curved toward the item; reported as (cond - same-regime baseline)")
    print("=" * 78)
    vtasks = [(g, reg, fam, w, side) for g in GENS for reg in REGIMES
              for fam, w in CONDS for side in (+1, -1)]
    with Pool(W_) as p:
        vrows = p.map(veer, vtasks, chunksize=4)
    vsum = {}
    for reg in REGIMES:
        base = float(np.mean([r["toward"] for r in vrows if r["reg"] == reg and r["cond"] == "baseline"]))
        bfwd = float(np.mean([r["fwd"] for r in vrows if r["reg"] == reg and r["cond"] == "baseline"]))
        print(f"\n  regime {reg} (bias {REGIMES[reg]}): baseline toward {base:+.3f} m, fwd {bfwd:+.2f} m")
        print(f"    {'wiring':18s} {'d toward (m)':>13s} {'fwd (m)':>9s} {'closest (m)':>12s}")
        for fam, w in CONDS:
            L = lab(fam, w)
            if L == "baseline":
                continue
            sel = [r for r in vrows if r["reg"] == reg and r["cond"] == L]
            tv = float(np.mean([r["toward"] for r in sel])) - base
            fw = float(np.mean([r["fwd"] for r in sel]))
            md = float(np.mean([r["min_dist"] for r in sel]))
            vsum[f"{reg}/{L}"] = dict(d_toward=tv, fwd=fw, min_dist=md)
            print(f"    {L:18s} {tv:+13.3f} {fw:+9.2f} {md:12.3f}")
        cr = vsum[f"{reg}/spike_crossed2"]["d_toward"]
        un = vsum[f"{reg}/spike_uncrossed2"]["d_toward"]
        oa = vsum[f"{reg}/oppA2"]["d_toward"]
        print(f"    crossed - uncrossed = {cr - un:+.3f} m   "
              f"(H6: 'identically w(n1+n2)' predicts 0)   |oppA| = {abs(oa):.3f} m")
    out["veer"] = vsum

    # spread across the 7 (identical-when-wiped) robots, to check H6's n
    sd = float(np.std([r["toward"] for r in vrows
                       if r["reg"] == "sym" and r["cond"] == "oppA2" and r["side"] == 1]))
    print(f"\n  sd of 'toward' across the 7 robots in the wiped-brain veer test (sym/oppA2/side+1): "
          f"{sd:.3e}  -> the 7 'robots' are one system; H6's section C/D n is 1, not 7.")
    out["veer_robot_sd"] = sd

    with open("runs/sim-audit/refute_installation_0.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\ntotal {time.time() - T0:.0f}s")
