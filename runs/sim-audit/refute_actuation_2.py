"""Refutation pass on H5 / probe_actuation.py, under the DOES-IT-MATTER lens.

The claim under audit has two layers and they must be scored separately.

  L1 (the stated hypothesis H5): "the Pioneer body may not steer from a wheel differential,
     so the Braitenberg premise fails at the ACTUATION layer."  probe_actuation's own B1/B3
     kill this; T1 below reproduces the kill independently.

  L2 (what the probe actually found): runs/compass-spike/spike.py adds the SAME-SIGNED weight
     to both nose->effector links in all 30 circuit conditions.  Because the two wheel hinges
     are antiparallel, forward is (e1>0, e2<0), so S = e1+e2 is the STEERING channel and
     D = e1-e2 the THROTTLE.  Same-signed pairs therefore put the noses' COMMON mode into
     steering and their GRADIENT into throttle.  That is a real bug -- in the spike script,
     not in the simulation.  It is confirmed by reading spike.py (verified here in T0).

  THE LENS: does L2 change the spike's headline?  The spike concluded "a hand-installed
  Braitenberg compass earns nothing here".  If the sign-corrected circuit ALSO earns nothing,
  the bug is real but immaterial: the conclusion it supposedly invalidates survives untouched.

T0  Static audit of spike.py's own weight assignments (no simulation).
T1  Open-loop confirmation that the body steers and that S, not D, is the steering channel.
T2  THE LENS TEST.  Sign-corrected, DC-FREE compasses at increasing authority, 7 robots x 32
    PAIRED seeds, robot as the unit of analysis, bootstrap over robots:
      baseline  - the evolved mower untouched
      wire12    - W[e1,n1]=W[e2,n1]=-w/2, W[e1,n2]=W[e2,n2]=+w/2  =>  dS = -w(n1-n2), dD = 0
                  exactly.  Gradient into STEERING, zero throttle contamination.  w=12.
      wire40    - the same at w=40, i.e. 10x the spike's largest magnitude of gradient-steering
                  authority, so "the fix was too weak" cannot explain a null.
      wire-12   - the same wiring with the sign flipped.
      servo30   - the CEILING for a two-nose Braitenberg on this body: the steering channel is
                  taken away from the gait entirely and handed to the nose gradient,
                  S = clip(-K (n1-n2), +-1.2), while the evolved throttle D is left alone.
                  No chatter, no saturation fight, full 1.24 rad/s of authority available.
      servoa30  - the same ceiling with the opposite sign.  BOTH signs are needed because these
                  evolved mowers drive CASTOR-FIRST (mean D = e1-e2 is about -1.0, i.e. they
                  travel along chassis -x), so which sign of "turn toward the stronger nose"
                  actually closes distance is an empirical question, not a convention.
    Mechanism readout as well as food: mean |bearing error to the nearest live item|.  A
    working compass MUST reduce it whatever it does to the food count.

usage: ./v/bin/python runs/sim-audit/refute_actuation_2.py
"""
from __future__ import annotations

import ast
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
HERO = 590
SEED0 = 9000
NSEED = 32
LEFT, RIGHT, CHASSIS = 1, 2, 0
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


def boot(v, n=20000, seed=7):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    r = np.random.default_rng(seed)
    m = r.choice(v, size=(n, len(v)), replace=True).mean(axis=1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


# --------------------------------------------------------------------------- #
# T0 : static audit of spike.py -- do the two installed weights share a sign?
# --------------------------------------------------------------------------- #
def t0():
    src = open("runs/compass-spike/spike.py").read()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "bout")
    pairs = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Subscript):
            tgt = ast.unparse(node.target)
            if tgt.startswith("W["):
                pairs.setdefault("all", []).append((tgt, ast.unparse(node.value)))
    print("=" * 78)
    print("T0.  STATIC AUDIT of runs/compass-spike/spike.py -- every W[dst,src] += ... in bout()")
    print("=" * 78)
    for tgt, val in pairs["all"]:
        print(f"    {tgt:26s} += {val}")
    vals = {v for _, v in pairs["all"]}
    print(f"\n  distinct right-hand sides: {sorted(vals)}")
    same = vals == {"sgn * m"}
    print(f"  every installed weight is the SAME expression 'sgn * m'  ->  {same}")
    print("  => the two links of every circuit always share a sign; the opposite-sign")
    print("     quadrant (the only Braitenberg wiring on antiparallel hinges) is never sampled.")
    print(f"  MAGS swept: {ast.literal_eval(ast.unparse(next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'MAGS')))}")
    return {"assignments": pairs["all"], "all_same_sign_expression": bool(same)}


# --------------------------------------------------------------------------- #
# T1 : open-loop corner probe
# --------------------------------------------------------------------------- #
def open_loop(task):
    seed, e1, e2 = task
    c = replace(cfg(), random_start=True, world=replace(cfg().world, terrain="flat", random_obstacles=0))
    g = Genotype.load(f"{RUN}/conventional/best_gen{HERO:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    eff, _ = units(HERO)
    b = sim.brains[0]
    b.W[:, :] = 0.0
    b.bias[:] = 0.0
    b.bias[eff[LEFT]] = float(np.arctanh(np.clip(e1, -0.999, 0.999)))
    b.bias[eff[RIGHT]] = float(np.arctanh(np.clip(e2, -0.999, 0.999)))
    steps = int(round(c.duration / c.control_dt))
    yaw = yaw_of(sim)
    tot = 0.0
    last = sim.center_of_mass(0)[:2].copy()
    start = last.copy()
    path = 0.0
    for _ in range(steps):
        sim.step()
        y = yaw_of(sim)
        tot += (y - yaw + np.pi) % (2 * np.pi) - np.pi
        yaw = y
        p = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(p - last))
        last = p.copy()
    T = steps * c.control_dt
    return {"seed": seed, "e1": e1, "e2": e2, "yaw_rate": tot / T, "speed": path / T,
            "net": float(np.linalg.norm(last - start))}


# --------------------------------------------------------------------------- #
# T2 : closed loop.  the servo shim -- steering handed to the nose gradient
# --------------------------------------------------------------------------- #
class ServoBrain:
    """Keeps the evolved brain's sensors and its THROTTLE, replaces its STEERING channel with
    a proportional Braitenberg law on the two wheel noses.

    ``decoy`` swaps the real food field for a phantom one of identical size, disc and clearance:
    the same law, the same sensor physics, the same amplitude statistics, no true information.
    ``K == 0`` pins the steering channel to straight ahead."""

    def __init__(self, inner, nose, eff, K, sign=-1.0, cap=1.2, sim=None, decoy=None):
        self.inner, self.nose, self.eff, self.K, self.sign, self.cap = inner, nose, eff, K, sign, cap
        self.sensors = inner.sensors
        self.W = inner.W
        self.sim = sim
        self.decoy = None if decoy is None else np.asarray(decoy, float)
        self.decoy_live = None if decoy is None else np.ones(len(decoy), bool)
        self.cmd = {(LEFT, 0): 0.0, (RIGHT, 0): 0.0}

    def _decoy_nose(self, part):
        """Reproduce Simulation._intensity at this wheel geom against the phantom sources."""
        sim = self.sim
        q = sim.data.geom_xpos[sim.robots[0].geoms[part]][:2]
        live = self.decoy[self.decoy_live]
        if len(live) == 0:
            return 0.0
        tot = float(np.exp(-np.linalg.norm(live - q, axis=1) / sim.config.food.decay).sum())
        return tot / (1.0 + tot)      # config smell mode is "sum" for this run

    @property
    def activation(self):
        return self.inner.activation

    def reset(self):
        self.inner.reset()

    def step(self, vals):
        self.inner.step(vals)
        e1 = self.inner.effector_output(LEFT, 0)
        e2 = self.inner.effector_output(RIGHT, 0)
        D = e1 - e2                                  # keep the evolved throttle exactly
        if self.decoy is not None:
            sim = self.sim
            p = sim.center_of_mass(0)[:2]
            self.decoy_live[np.linalg.norm(self.decoy - p, axis=1) < sim.config.food.eat_radius] = False
            n1, n2 = self._decoy_nose(LEFT), self._decoy_nose(RIGHT)
        else:
            n1 = float(self.inner.activation[self.nose[LEFT]])
            n2 = float(self.inner.activation[self.nose[RIGHT]])
        S = float(np.clip(self.sign * self.K * (n1 - n2), -self.cap, self.cap))
        self.cmd = {(LEFT, 0): float(np.clip((S + D) / 2, -1, 1)),
                    (RIGHT, 0): float(np.clip((S - D) / 2, -1, 1))}

    def effector_output(self, part, dof):
        return self.cmd.get((part, dof), 0.0)

    def outputs(self):
        return dict(self.cmd)


def closed(task):
    gen, seed, fam = task
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    eff, nose = units(gen)
    W = sim.brains[0].W
    if fam.startswith("wire"):
        w = float(fam[4:])
        # de1 = de2 = -(w/2)(n1-n2)  ->  dS = -w(n1-n2)  (turn toward the stronger nose), dD = 0
        W[eff[LEFT], nose[LEFT]] += -w / 2
        W[eff[RIGHT], nose[LEFT]] += -w / 2
        W[eff[LEFT], nose[RIGHT]] += +w / 2
        W[eff[RIGHT], nose[RIGHT]] += +w / 2
    elif fam.startswith("servo"):
        tail = fam[5:]
        sign = +1.0 if tail.startswith("a") else -1.0
        tail = tail.lstrip("a")
        decoy = None
        if tail.endswith("decoy"):
            tail = tail[:-5]
            rng = np.random.default_rng(seed + 500000)
            q0 = sim.data.geom_xpos[sim.robots[0].geoms[CHASSIS]][:2]
            pts = []
            while len(pts) < c.food.items:
                rr = c.food.radius * np.sqrt(rng.random())
                aa = rng.uniform(0, 2 * np.pi)
                z = np.array([rr * np.cos(aa), rr * np.sin(aa)])
                if np.linalg.norm(z - q0) >= c.food.clearance:
                    pts.append(z)
            decoy = np.array(pts)
        K = float(tail) if tail else 30.0
        sim.brains[0] = ServoBrain(sim.brains[0], nose, eff, K, sign=sign, sim=sim, decoy=decoy)
    idx = sim.robots[0]
    aidL, aidR = idx.actuators[(LEFT, 0)], idx.actuators[(RIGHT, 0)]
    gid = idx.geoms[CHASSIS]
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    e1s, e2s, n1s, n2s, dy, errs, verrs = [], [], [], [], [], [], []
    near, in_path = [], 0.0
    yaw = yaw_of(sim)
    last = sim.center_of_mass(0)[:2].copy()
    for _ in range(steps):
        sim.step()
        e1s.append(float(sim.data.ctrl[aidL]))
        e2s.append(float(sim.data.ctrl[aidR]))
        act = sim.brains[0].activation
        n1s.append(float(act[nose[LEFT]]))
        n2s.append(float(act[nose[RIGHT]]))
        y = yaw_of(sim)
        dy.append(((y - yaw + np.pi) % (2 * np.pi) - np.pi) / c.control_dt)
        yaw = y
        # bearing error of the chassis forward axis to the nearest LIVE item
        R = sim.data.geom_xmat[gid].reshape(3, 3)
        q = sim.data.geom_xpos[gid][:2]
        fwd = R[:2, 0]
        nf = float(np.linalg.norm(fwd))
        live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
        if len(live) and nf > 1e-9:
            fwd = fwd / nf
            v = live[int(np.argmin(np.linalg.norm(live - q, axis=1)))] - q
            errs.append(abs(float(np.arctan2(fwd[0] * v[1] - fwd[1] * v[0], fwd[0] * v[0] + fwd[1] * v[1]))))
            u = sim.center_of_mass(0)[:2] - last          # actual travel direction this tick
            nu = float(np.linalg.norm(u))
            if nu > 1e-4:
                u = u / nu
                verrs.append(abs(float(np.arctan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))))
        p = sim.center_of_mass(0)[:2]
        if float(np.linalg.norm(p)) <= disc:
            in_path += float(np.linalg.norm(p - last))
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
        last = p.copy()
    e1, e2 = np.array(e1s), np.array(e2s)
    n1, n2 = np.array(n1s), np.array(n2s)
    S, D, nd = e1 + e2, e1 - e2, n1 - n2
    dy = np.array(dy)
    cc = lambda a, b: float(np.corrcoef(a, b)[0, 1]) if a.std() > 1e-9 and b.std() > 1e-9 else float("nan")
    return {"gen": gen, "seed": seed, "fam": fam,
            "food": float(sim.food_eaten[0]),
            "abs_err": float(np.mean(errs)) if errs else float("nan"),
            "vel_err": float(np.mean(verrs)) if verrs else float("nan"),
            "corr_yaw_grad": cc(dy, nd), "corr_S_grad": cc(S, nd),
            "S_mean": float(S.mean()), "S_std": float(S.std()),
            "D_mean": float(D.mean()), "yaw_abs": float(np.abs(dy).mean()),
            "n_grad_abs": float(np.abs(nd).mean()), "n_common": float((n1 + n2).mean()),
            "sat1": float(np.mean(np.abs(e1) > 0.99)), "sat2": float(np.mean(np.abs(e2) > 0.99)),
            "near": float(np.mean(near)) if near else float("nan"),
            "in_path": in_path, "exploded": bool(sim.exploded[0])}


def main():
    t0_res = t0()
    t_start = time.time()
    out = {"T0": t0_res}

    # ------------------------------------------------------------------ T1 -- #
    print()
    print("=" * 78)
    print("T1.  OPEN LOOP, flat, no obstacles, 3 paired starts each: which channel steers?")
    print("=" * 78)
    corners = [(+1, -1), (+1, +1), (-1, -1), (+1, 0), (0, +1)]
    tasks1 = [(SEED0 + s, e1, e2) for e1, e2 in corners for s in range(3)]
    with Pool(4) as pool:
        r1 = pool.map(open_loop, tasks1)
    out["T1"] = {}
    print(f"  {'(e1,e2)':>10s} {'S':>6s} {'D':>6s} | {'yaw rate':>10s} {'speed':>8s} {'net disp':>9s}")
    for e1, e2 in corners:
        rs = [r for r in r1 if r["e1"] == e1 and r["e2"] == e2]
        yr = float(np.mean([r["yaw_rate"] for r in rs]))
        sp = float(np.mean([r["speed"] for r in rs]))
        nt = float(np.mean([r["net"] for r in rs]))
        print(f"  {f'({e1:+g},{e2:+g})':>10s} {e1+e2:+6.1f} {e1-e2:+6.1f} | {yr:+10.4f} {sp:8.3f} {nt:9.2f}")
        out["T1"][f"{e1:+g},{e2:+g}"] = {"yaw_rate": yr, "speed": sp, "net": nt}
    print("  (rad/s, m/s, m).  Yaw follows S = e1+e2; D = e1-e2 is the throttle.")

    # ------------------------------------------------------------------ T2 -- #
    FAMS = ("baseline", "wire12.0", "wire40.0", "wire-12.0", "servo30", "servoa30")
    tasks2 = [(g, SEED0 + s, f) for g in GENS for s in range(NSEED) for f in FAMS]
    print()
    print("=" * 78)
    print(f"T2.  LENS TEST: sign-CORRECTED, DC-free compasses.  {len(tasks2)} bouts "
          f"({len(GENS)} robots x {NSEED} paired seeds x {len(FAMS)} conditions)")
    print("=" * 78, flush=True)
    with Pool(4) as pool:
        rows = pool.map(closed, tasks2, chunksize=8)
    print(f"  ({time.time()-t_start:.0f}s)")

    KEYS = ("food", "abs_err", "vel_err", "corr_yaw_grad", "corr_S_grad", "S_std", "D_mean", "yaw_abs",
            "n_grad_abs", "sat1", "sat2", "near", "in_path")
    per = {}
    for fam in FAMS:
        rs = [r for r in rows if r["fam"] == fam]
        per[fam] = {g: {k: float(np.nanmean([r[k] for r in rs if r["gen"] == g])) for k in KEYS}
                    for g in GENS}
    print(f"\n  {'cond':>9s} | {'food':>6s} {'|chassis err|':>13s} {'|travel err|':>13s} {'corr(yaw,n1-n2)':>16s} "
          f"{'corr(S,n1-n2)':>14s} {'S sd':>6s} {'|yaw|':>6s} {'sat2':>5s} {'near':>6s}")
    for fam in FAMS:
        a = {k: float(np.mean([per[fam][g][k] for g in GENS])) for k in KEYS}
        print(f"  {fam:>9s} | {a['food']:6.3f} {np.degrees(a['abs_err']):11.1f} deg {np.degrees(a['vel_err']):11.1f} deg "
              f"{a['corr_yaw_grad']:16.4f} {a['corr_S_grad']:14.4f} {a['S_std']:6.3f} "
              f"{a['yaw_abs']:6.3f} {a['sat2']:5.2f} {a['near']:6.3f}")

    print(f"\n  paired vs baseline; the ROBOT is the unit ({len(GENS)} robots, {NSEED} shared seeds each),")
    print("  95% CI bootstrapped over robots:\n")
    res = {}
    for fam in FAMS[1:]:
        for k, lab, scale in (("food", "d food (items)", 1.0),
                              ("vel_err", "d |travel-dir err| (deg)", 180 / np.pi),
                              ("abs_err", "d |chassis err| (deg)", 180 / np.pi),
                              ("corr_yaw_grad", "d corr(yaw, n1-n2)", 1.0),
                              ("corr_S_grad", "d corr(S, n1-n2)", 1.0),
                              ("near", "d near-dist (m)", 1.0),
                              ("yaw_abs", "d |yaw rate| (rad/s)", 1.0)):
            dv = [(per[fam][g][k] - per["baseline"][g][k]) * scale for g in GENS]
            m, lo, hi = boot(dv, seed=11)
            print(f"    {fam:>9s}  {lab:<24s} = {m:+9.4f}  [{lo:+.4f}, {hi:+.4f}]")
            res[f"{fam}|{k}"] = {"mean": m, "ci": [lo, hi], "per_robot": [float(x) for x in dv]}
        print()
    out["T2"] = {"n_seeds": NSEED, "gens": list(GENS), "fams": list(FAMS),
                 "per_robot": {f: {str(g): v for g, v in per[f].items()} for f in FAMS},
                 "paired": res,
                 "exploded": sum(r["exploded"] for r in rows) / len(rows)}
    print(f"  exploded fraction {out['T2']['exploded']:.4f}")
    with open("runs/sim-audit/refute_actuation_2.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nwrote runs/sim-audit/refute_actuation_2.json   total {time.time()-t_start:.0f}s")


def t3():
    """Controls for T2's servoa30 win: is the +1.0 items really CHEMOTAXIS, or just
    'the steering channel stopped chattering' / 'the robot turned more'?"""
    old = json.load(open("runs/sim-audit/refute_actuation_2.json"))
    base = {g: old["T2"]["per_robot"]["baseline"][str(g)] for g in GENS}
    FAMS = ("servoa0", "servoa30decoy", "wire-40.0")
    tasks = [(g, SEED0 + s, f) for g in GENS for s in range(NSEED) for f in FAMS]
    print("=" * 78)
    print(f"T3.  CONTROLS.  {len(tasks)} bouts, same 7 robots x {NSEED} PAIRED seeds as T2")
    print("     servoa0       steering channel pinned to S=0 (drive straight, evolved throttle)")
    print("     servoa30decoy identical servo law on a PHANTOM food field: same physics, no info")
    print("     wire-40.0     the additive sign-corrected compass at w=40 (dS = +40(n1-n2), dD=0)")
    print("=" * 78, flush=True)
    t = time.time()
    with Pool(4) as pool:
        rows = pool.map(closed, tasks, chunksize=8)
    print(f"  ({time.time()-t:.0f}s)")
    KEYS = ("food", "abs_err", "vel_err", "corr_yaw_grad", "corr_S_grad", "S_std", "D_mean",
            "yaw_abs", "n_grad_abs", "sat1", "sat2", "near", "in_path")
    per = {f: {g: {k: float(np.nanmean([r[k] for r in rows if r["fam"] == f and r["gen"] == g]))
                   for k in KEYS} for g in GENS} for f in FAMS}
    res = {}
    print(f"\n  {'cond':>14s} | {'food':>6s} {'d food (items)':>16s} {'95% CI':>20s} | "
          f"{'|travel err|':>12s} {'S sd':>6s} {'|yaw|':>6s} {'near':>6s}")
    for f in FAMS:
        a = {k: float(np.mean([per[f][g][k] for g in GENS])) for k in KEYS}
        dv = [per[f][g]["food"] - base[g]["food"] for g in GENS]
        m, lo, hi = boot(dv, seed=11)
        print(f"  {f:>14s} | {a['food']:6.3f} {m:+16.4f} [{lo:+8.4f},{hi:+8.4f}] | "
              f"{np.degrees(a['vel_err']):9.1f} deg {a['S_std']:6.3f} {a['yaw_abs']:6.3f} {a['near']:6.3f}")
        res[f] = {"food": a["food"], "d_food": m, "ci": [lo, hi],
                  "per_robot": [float(x) for x in dv],
                  **{k: a[k] for k in KEYS}}
    ab = {k: float(np.mean([base[g][k] for g in GENS])) for k in KEYS}
    print(f"  {'baseline':>14s} | {ab['food']:6.3f} {0.0:+16.4f} {'(reference)':>20s} | "
          f"{np.degrees(ab['vel_err']):9.1f} deg {ab['S_std']:6.3f} {ab['yaw_abs']:6.3f} {ab['near']:6.3f}")
    old["T3"] = {"n_seeds": NSEED, "fams": list(FAMS), "res": res,
                 "per_robot": {f: {str(g): v for g, v in per[f].items()} for f in FAMS},
                 "exploded": sum(r["exploded"] for r in rows) / len(rows)}
    with open("runs/sim-audit/refute_actuation_2.json", "w") as fh:
        json.dump(old, fh, indent=1)
    print("\nwrote T3 into runs/sim-audit/refute_actuation_2.json")


if __name__ == "__main__":
    import sys
    if "--t3" in sys.argv:
        t3()
    else:
        main()
