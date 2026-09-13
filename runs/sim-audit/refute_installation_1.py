"""Adversarial re-audit of H6 (runs/sim-audit/probe_installation.py).

H6's claim has two halves:
  (i)  same-signed drive on the two wheel effectors is ROTATION, not forward drive
       (translation lives on ctrl1-ctrl2, rotation on ctrl1+ctrl2);
  (ii) THEREFORE spike.py's crossed/uncrossed wirings inject a turn command that is
       "IDENTICALLY w(n1+n2)" -- a function of total smell only -- so both put ZERO
       gradient information on the steering axis, and the spike's observation that
       crossed and uncrossed behave identically is "a mathematical identity, not a
       null result".

(ii) follows from (i) only if the two effectors have the SAME incremental gain.  They
do not: H6's own section E reports mean x1 = -0.49 and mean x2 = +2.58 with 75% of
ticks past |x| = 2, i.e. tanh gains that differ by 35x.  With g1 != g2 the injected
turn is w(g1*n_a + g2*n_b), which is NOT a function of (n1+n2) alone.

This script measures, rather than assumes:
  R1  the drive convention (1 robot, replicates H6 section C) -- corroboration only.
  R2  the per-tick incremental gains g1,g2 in REAL bouts and the exact injected turn
      command decomposed into common (n1+n2) and gradient (n1-n2) parts, for each
      wiring, both at a common frozen operating point and in each wiring's own loop.
  R3  a mirrored veer test with the REAL evolved brain (H6 only ran it with the brain
      wiped to a symmetric bias, which is not the regime the spike ran in).
  R4  H6's own wiped-brain veer test, broken out PER SIDE and with UNWRAPPED yaw.

usage: ./v/bin/python runs/sim-audit/refute_installation_1.py [--workers 4]
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
from rabbitstew.world import Spawn

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


# The install, expressed as the pair of (dst_effector, src_nose, sign) triples, so the
# same table drives both the live install and the analytic counterfactual.
WIRINGS = {
    "baseline":        [],
    "spike_crossed":   [(1, 2, +1), (2, 1, +1)],   # W[e1,n2]+=w, W[e2,n1]+=w
    "spike_uncrossed": [(1, 1, +1), (2, 2, +1)],
    "oppA":            [(1, 2, +1), (2, 1, -1)],
    "oppB":            [(1, 1, +1), (2, 2, -1)],
}


def install(W, nose, eff, fam, w):
    for dst, src, sgn in WIRINGS[fam]:
        W[eff[dst], nose[src]] += sgn * w


def deltas(fam, w, n1, n2):
    """(d1, d2): what the install adds to x[e1] and x[e2] at a tick with noses n1,n2."""
    n = {1: n1, 2: n2}
    d = {1: 0.0, 2: 0.0}
    for dst, src, sgn in WIRINGS[fam]:
        d[dst] = d[dst] + sgn * w * n[src]
    return d[1], d[2]


# --------------------------------------------------------------------------- #
# R2 -- instrumented bouts: gains and the exact injected turn command
# --------------------------------------------------------------------------- #
def trace(task):
    gen, fam, w, seed = task
    c = replace(cfg(), random_start=True)
    ph, nose, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    br = sim.brains[0]
    install(br.W, nose, eff, fam, w)
    e1, e2, n1i, n2i = eff[1], eff[2], nose[1], nose[2]
    rec = []
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        a = br.activation
        x = br.W @ a + br.bias
        rec.append((a[n1i], a[n2i], x[e1], x[e2]))
    r = np.array(rec)
    return dict(gen=gen, fam=fam, w=w, seed=seed, arr=r, food=float(sim.food_eaten[0]))


def decompose(n1, n2, x1_off, x2_off, fam, w, eps=0.02):
    """How much TURN command does the install put on the gradient, state held fixed?

    x*_off are the pre-activations WITHOUT the install.  At every tick the noses are
    perturbed by a pure gradient (n1+eps, n2-eps) vs (n1-eps, n2+eps) -- 2*eps = 0.04 is
    the measured mean |n1-n2| -- and by a pure common-mode step of the same size, and the
    resulting swing in the turn command R = c1+c2 and drive command T = c1-c2 is recorded.
    No regression, so the (large) tick-to-tick variation of the state cannot leak in.
    """
    def RT(a, b):
        d1, d2 = deltas(fam, w, a, b)
        c1, c2 = np.tanh(x1_off + d1), np.tanh(x2_off + d2)
        return c1 + c2, c1 - c2

    Rg_p, Tg_p = RT(n1 + eps, n2 - eps)
    Rg_m, Tg_m = RT(n1 - eps, n2 + eps)
    Rc_p, Tc_p = RT(n1 + eps, n2 + eps)
    Rc_m, Tc_m = RT(n1 - eps, n2 - eps)
    d1, d2 = deltas(fam, w, n1, n2)
    dR = (np.tanh(x1_off + d1) + np.tanh(x2_off + d2)) - (np.tanh(x1_off) + np.tanh(x2_off))
    return dict(turn_grad=float(np.mean(Rg_p - Rg_m)),          # signed swing of the turn command
                turn_grad_abs=float(np.mean(np.abs(Rg_p - Rg_m))),
                turn_common=float(np.mean(Rc_p - Rc_m)),
                drive_grad=float(np.mean(Tg_p - Tg_m)),
                drive_common=float(np.mean(Tc_p - Tc_m)),
                turn_offset=float(np.mean(dR)))


# --------------------------------------------------------------------------- #
# R3/R4 -- veer tests.  One uneatable item in body frame at (2.5, side*1.2).
# --------------------------------------------------------------------------- #
def veer_cfg(dur=8.0):
    c = cfg()
    return replace(c, world=replace(c.world, terrain="flat"),
                   food=replace(c.food, items=1, eat_radius=0.02, clearance=0.0, regrow=False),
                   random_start=False, duration=dur)


def veer(task):
    gen, fam, w, side, yaw, wipe, base = task
    c = veer_cfg()
    ph, nose, eff = wiring(gen)
    sim = Simulation([geno(gen)], c, spawns=[Spawn(position=(0.0, 0.0, 0.0), yaw=yaw)])
    sim.set_food_seed(1)
    ca, sa = np.cos(yaw), np.sin(yaw)
    loc = np.array([[2.5 * ca - side * 1.2 * sa, 2.5 * sa + side * 1.2 * ca]])
    sim.food_pos = loc.copy()
    sim.food_spots = loc.copy()
    sim.food_alive = np.ones(1, dtype=bool)
    sim.food_timer = np.zeros(1)
    br = sim.brains[0]
    if wipe:
        br.W[:, :] = 0.0
        br.bias[:] = 0.0
        br.bias[eff[1]] = +base
        br.bias[eff[2]] = -base
    install(br.W, nose, eff, fam, w)
    rb = sim.robots[0]
    R0 = sim.data.xmat[rb.root_body].reshape(3, 3).copy()
    p0 = sim.center_of_mass(0)[:2].copy()
    y_prev = np.arctan2(R0[1, 0], R0[0, 0])
    cum = 0.0                                   # UNWRAPPED cumulative yaw
    mind = 1e9
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
        Rk = sim.data.xmat[rb.root_body].reshape(3, 3)
        yk = np.arctan2(Rk[1, 0], Rk[0, 0])
        cum += float(np.arctan2(np.sin(yk - y_prev), np.cos(yk - y_prev)))
        y_prev = yk
        mind = min(mind, float(np.linalg.norm(sim.center_of_mass(0)[:2] - loc[0])))
    d = sim.center_of_mass(0)[:2] - p0
    return dict(gen=gen, fam=fam, w=w, side=side, yaw=round(yaw, 3), wipe=wipe,
                lat=float(R0[:2, 1] @ d), fwd=float(R0[:2, 0] @ d),
                cumyaw=float(np.degrees(cum)), min_dist=mind)


def boot(v, draws=20000, seed=5):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    T0 = time.time()
    out = {}
    FAMS = ["baseline", "spike_crossed", "spike_uncrossed", "oppA", "oppB"]
    W = 2.0

    # ---------- R1 drive convention (corroboration of H6 section C) --------- #
    print("=" * 78)
    print("R1. DRIVE CONVENTION -- is same-signed effector drive really rotation?")
    print("=" * 78)
    ph, nose, eff = wiring(590)
    for p in ph.parts:
        print(f"   part {p.index}: parent={p.parent} attach={np.round(p.attach_pos, 3)} "
              f"units={len(ph.units_of_part(p.index))}")
    c = replace(cfg(), random_start=True)
    pol = {}
    for tag, (b1, b2) in (("(+,+)", (3.0, 3.0)), ("(+,-)", (3.0, -3.0)),
                          ("(-,+)", (-3.0, 3.0)), ("(-,-)", (-3.0, -3.0))):
        sim = Simulation([geno(590)], c, spawns=spawn_layout(1, c, SEED0))
        sim.set_food_seed(SEED0)
        br = sim.brains[0]
        br.W[:, :] = 0.0
        br.bias[:] = 0.0
        br.bias[eff[1]] = b1
        br.bias[eff[2]] = b2
        rb = sim.robots[0]
        R0 = sim.data.xmat[rb.root_body].reshape(3, 3).copy()
        p0 = sim.center_of_mass(0)[:2].copy()
        yp = np.arctan2(R0[1, 0], R0[0, 0])
        cum = 0.0
        for _ in range(200):
            sim.step()
            Rk = sim.data.xmat[rb.root_body].reshape(3, 3)
            yk = np.arctan2(Rk[1, 0], Rk[0, 0])
            cum += float(np.arctan2(np.sin(yk - yp), np.cos(yk - yp)))
            yp = yk
        d = sim.center_of_mass(0)[:2] - p0
        pol[tag] = dict(disp=float(np.linalg.norm(d)), cumyaw=float(np.degrees(cum)))
        print(f"   {tag}: |displacement| {pol[tag]['disp']:6.3f} m   cumulative yaw "
              f"{pol[tag]['cumyaw']:+8.1f} deg")
    print("   fixed.py:143 'Each wheel hinges about its own outward normal, so the right wheel")
    print("   needs the opposite sign' -- drive_straight_genotype() uses (+1,-1).  H6's half (i)")
    print("   is CORRECT and is the library's own documented convention.")
    out["polarity"] = pol

    # ---------- R2 gains and the injected turn command ---------------------- #
    print()
    print("=" * 78)
    print("R2. WHAT THE INSTALL ACTUALLY PUTS ON THE TURN AXIS (7 robots x 4 seeds, real bouts)")
    print("=" * 78)
    tasks = [(g, fam, 0.0 if fam == "baseline" else W, SEED0 + s)
             for g in GENS for s in range(4) for fam in FAMS]
    with Pool(args.workers) as p:
        trows = p.map(trace, tasks, chunksize=4)
    print(f"   {len(tasks)} instrumented bouts in {time.time() - T0:.0f}s")

    def pool_arr(fam):
        return np.concatenate([r["arr"] for r in trows if r["fam"] == fam], axis=0)

    print(f"\n   incremental tanh gain of each effector, sech^2(x), in each wiring's OWN loop:")
    print(f"   {'wiring':17s} {'mean x1':>8s} {'mean x2':>8s} {'g1=E sech^2 x1':>15s} "
          f"{'g2=E sech^2 x2':>15s} {'g2/g1':>7s}")
    gains = {}
    for fam in FAMS:
        a = pool_arr(fam)
        g1 = float(np.mean(1.0 / np.cosh(a[:, 2]) ** 2))
        g2 = float(np.mean(1.0 / np.cosh(a[:, 3]) ** 2))
        gains[fam] = dict(x1=float(a[:, 2].mean()), x2=float(a[:, 3].mean()), g1=g1, g2=g2)
        print(f"   {fam:17s} {a[:, 2].mean():+8.3f} {a[:, 3].mean():+8.3f} {g1:15.4f} "
              f"{g2:15.4f} {g2 / g1:7.3f}")
    out["gains"] = gains
    print("   H6's algebra needs g1 == g2.  If g2/g1 << 1 the two effectors are NOT")
    print("   interchangeable and the 'identically w(n1+n2)' cancellation cannot happen.")

    # (a) frozen common operating point: the baseline bouts' own states
    b = pool_arr("baseline")
    n1b, n2b, x1b, x2b = b[:, 0], b[:, 1], b[:, 2], b[:, 3]
    print(f"\n   (a) FROZEN counterfactual -- every wiring evaluated on the SAME states")
    print(f"       (the {len(b)} ticks of the unmodified robots), w = {W:g}.")
    print(f"       'turn swing on a realistic gradient' = change in R = c1+c2 when the noses")
    print(f"       are swung by (n1-n2) -> +/-0.04, the measured mean gradient, state fixed.")
    print(f"   {'wiring':17s} {'turn swing / grad':>18s} {'vs oppA':>8s} {'turn swing / common':>20s} "
          f"{'drive swing / grad':>19s}")
    froz = {}
    for fam in FAMS[1:]:
        froz[fam] = decompose(n1b, n2b, x1b, x2b, fam, W)
    ref = abs(froz["oppA"]["turn_grad"])
    for fam in FAMS[1:]:
        d = froz[fam]
        print(f"   {fam:17s} {d['turn_grad']:+18.4f} {abs(d['turn_grad']) / ref:8.3f} "
              f"{d['turn_common']:+20.4f} {d['drive_grad']:+19.4f}")
    out["frozen"] = froz
    print("   H6 predicts the 'turn swing / grad' column is EXACTLY 0.0000 for both spike")
    print("   wirings, and equal for them; and that they cannot differ from each other.")

    # (b) each wiring in its own closed loop
    print(f"\n   (b) each wiring evaluated in ITS OWN closed loop (operating point shifts):")
    print(f"   {'wiring':17s} {'turn swing / grad':>18s} {'vs oppA':>8s} {'turn swing / common':>20s}")
    own = {}
    for fam in FAMS[1:]:
        a = pool_arr(fam)
        d1, d2 = deltas(fam, W, a[:, 0], a[:, 1])
        own[fam] = decompose(a[:, 0], a[:, 1], a[:, 2] - d1, a[:, 3] - d2, fam, W)
    ref2 = abs(own["oppA"]["turn_grad"])
    for fam in FAMS[1:]:
        d = own[fam]
        print(f"   {fam:17s} {d['turn_grad']:+18.4f} {abs(d['turn_grad']) / ref2:8.3f} "
              f"{d['turn_common']:+20.4f}")
    out["own_loop"] = own

    # ---------- R3 veer with the REAL brain --------------------------------- #
    print()
    print("=" * 78)
    print("R3. MIRRORED VEER WITH THE REAL EVOLVED BRAIN (7 robots x 3 start yaws x both sides)")
    print("=" * 78)
    yaws = [0.0, 2 * np.pi / 3, 4 * np.pi / 3]
    vt = [(g, fam, 0.0 if fam == "baseline" else W, side, y, False, 0.0)
          for g in GENS for fam in FAMS for side in (+1, -1) for y in yaws]
    with Pool(args.workers) as p:
        vrows = p.map(veer, vt, chunksize=4)
    print(f"   {'wiring':17s} {'yaw toward item':>16s} {'95% CI over robots':>24s} "
          f"{'lat toward':>11s} {'mean closest':>13s}")
    r3 = {}
    for fam in FAMS:
        w_ = 0.0 if fam == "baseline" else W
        per_robot_y, per_robot_l, per_robot_m = [], [], []
        for g in GENS:
            sel = [r for r in vrows if r["fam"] == fam and r["gen"] == g and r["w"] == w_]
            per_robot_y.append(float(np.mean([r["side"] * r["cumyaw"] for r in sel])))
            per_robot_l.append(float(np.mean([r["side"] * r["lat"] for r in sel])))
            per_robot_m.append(float(np.mean([r["min_dist"] for r in sel])))
        m, lo, hi = boot(per_robot_y)
        r3[fam] = dict(yaw=m, ci=[lo, hi], lat=float(np.mean(per_robot_l)),
                       mind=float(np.mean(per_robot_m)), per_robot_yaw=per_robot_y)
        print(f"   {fam:17s} {m:+16.2f} {'[' + format(lo, '+.2f') + ', ' + format(hi, '+.2f') + ']':>24s} "
              f"{np.mean(per_robot_l):+11.3f} {np.mean(per_robot_m):13.3f}")
    print("   positive yaw/lat = turned toward the item's side; averaged over the two mirrored")
    print("   placements so a body or brain asymmetry cannot fake a sign.")
    d = np.array(r3["spike_crossed"]["per_robot_yaw"]) - np.array(r3["spike_uncrossed"]["per_robot_yaw"])
    m, lo, hi = boot(d)
    print(f"\n   spike_crossed - spike_uncrossed, antisymmetric yaw: {m:+.2f} deg "
          f"95% CI [{lo:+.2f}, {hi:+.2f}]")
    print(f"   (H6 says this difference must be exactly zero: both inject w(n1+n2) and nothing else.)")
    r3["crossed_minus_uncrossed_yaw"] = dict(delta=m, ci=[lo, hi])
    d2 = np.array(r3["oppA"]["per_robot_yaw"]) - np.array(r3["oppB"]["per_robot_yaw"])
    m2, lo2, hi2 = boot(d2)
    print(f"   oppA - oppB, antisymmetric yaw:                     {m2:+.2f} deg "
          f"95% CI [{lo2:+.2f}, {hi2:+.2f}]")
    r3["oppA_minus_oppB_yaw"] = dict(delta=m2, ci=[lo2, hi2])
    out["veer_real"] = r3

    # ---------- R4 H6's own wiped-brain veer, per side, unwrapped ----------- #
    print()
    print("=" * 78)
    print("R4. H6's OWN WIPED-BRAIN VEER, BROKEN OUT PER SIDE, WITH UNWRAPPED YAW")
    print("=" * 78)
    wt = [(g, fam, 0.0 if fam == "baseline" else W, side, 0.0, True, 0.7)
          for g in GENS for fam in FAMS for side in (+1, -1)]
    with Pool(args.workers) as p:
        wrows = p.map(veer, wt, chunksize=4)
    print(f"   {'wiring':17s} {'yaw side=+1':>12s} {'yaw side=-1':>12s} {'antisym':>9s} "
          f"{'common':>9s} {'H6 wrapped antisym':>20s}")
    r4 = {}
    for fam in FAMS:
        w_ = 0.0 if fam == "baseline" else W
        yp = float(np.mean([r["cumyaw"] for r in wrows if r["fam"] == fam and r["w"] == w_ and r["side"] == +1]))
        ym = float(np.mean([r["cumyaw"] for r in wrows if r["fam"] == fam and r["w"] == w_ and r["side"] == -1]))
        wrapped = float(np.mean([r["side"] * np.degrees(np.arctan2(np.sin(np.radians(r["cumyaw"])),
                                                                   np.cos(np.radians(r["cumyaw"]))))
                                 for r in wrows if r["fam"] == fam and r["w"] == w_]))
        r4[fam] = dict(yaw_plus=yp, yaw_minus=ym, antisym=(yp - ym) / 2, common=(yp + ym) / 2,
                       wrapped_antisym=wrapped)
        print(f"   {fam:17s} {yp:+12.1f} {ym:+12.1f} {(yp - ym) / 2:+9.1f} {(yp + ym) / 2:+9.1f} "
              f"{wrapped:+20.1f}")
    print("   'antisym' = the genuine steering response (toward the item is positive).")
    print("   'common'  = the side-blind spin.  H6 reported only the WRAPPED antisym column.")
    out["veer_wiped"] = r4

    # ---------- R5 the spike's own crossed-vs-uncrossed contrast ------------ #
    print()
    print("=" * 78)
    print("R5. THE SPIKE'S OWN crossed-vs-uncrossed CONTRAST (its saved rows, 7 robots x 64 seeds)")
    print("=" * 78)
    sp = json.load(open("runs/compass-spike/spike.json"))
    by = {(r["gen"], r["seed"], r["cond"]): r for r in sp["rows"]}
    seeds = sp["seeds"]
    r5 = {}
    for mag in (1.0, 2.0, 4.0):
        per_robot = []
        for g in sp["gens"]:
            v = [by[(g, s, f"crossed+{mag}")]["food"] - by[(g, s, f"uncrossed+{mag}")]["food"]
                 for s in seeds]
            per_robot.append(float(np.mean(v)))
        m, lo, hi = boot(per_robot)
        r5[f"m{mag:g}"] = dict(delta=m, ci=[lo, hi])
        print(f"   crossed+{mag} - uncrossed+{mag}: {m:+.3f} items  95% CI [{lo:+.3f}, {hi:+.3f}]")
    out["spike_contrast"] = r5

    with open("runs/sim-audit/refute_installation_1.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\ntotal {time.time() - T0:.0f}s; wrote runs/sim-audit/refute_installation_1.json")
