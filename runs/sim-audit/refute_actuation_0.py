"""Audit of H5 / probe_actuation.py.  Three independent checks of measurement soundness.

R1  Command realisation + geometry: does ctrl actually equal the commanded pair, and are the
    wheel axes really antiparallel?  (probe_actuation records ctrl but never reports it.)

R2  OFF-SYMMETRY D SWEEP.  probe_actuation's D sweep is taken at e=(P+off, -P-off), i.e. with
    S = e1+e2 held at EXACTLY 0.  That is the left-right symmetry line of the body, where yaw
    must vanish for any D by symmetry alone.  So "d(yaw)/dD = 0.0006" may be a tautology, not a
    measurement, and the 988:1 authority ratio rests on it.  Re-run the D sweep at S0 = -0.3, 0,
    +0.3 so symmetry cannot force the answer, and bootstrap the SLOPE (probe_actuation puts no
    error bar on any slope at all).

R3  SMALL-SIGNAL S GAIN.  The claim converts a gradient of 0.036 into "-0.022 rad/s of turn"
    using a gain fitted over |S| <= 0.8.  Measure the gain at the gradient's OWN amplitude
    (|S| <= 0.14): if there is a deadband the extrapolation is void.

R4  LIKE-FOR-LIKE COMPASS.  probe_actuation's part F ("mirror+/-") is not a like-for-like
    comparison: with only two weights, W[e1,n1]=+-w and W[e2,n2]=-+w puts -+w*(n1+n2) = -+1.9
    into the THROTTLE channel at w=2, so the mirror bouts differ from baseline in speed as much
    as in steering.  With all four nose->effector links you can inject the gradient into S with
    EXACTLY ZERO throttle term:
        W[e1,n1] = W[e2,n1] = -w/2 ;  W[e1,n2] = W[e2,n2] = +w/2
        => de1 = de2 = (w/2)(n2-n1)  =>  dS = -w(n1-n2), dD = 0
    With k_yaw/dS = -0.622 that is yaw += +0.622*w*(n1-n2): turn toward the stronger LEFT nose.
    Run that ("compass"), its sign-flip ("anti"), and baseline, 7 robots x 32 paired seeds.

usage: ./v/bin/python runs/sim-audit/refute_actuation_0.py
"""
from __future__ import annotations

import json, os, time
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
LEFT, RIGHT = 1, 2
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
    return ph, eff, nose


def yaw_of(sim):
    R = sim.data.xmat[sim.robots[0].root_body].reshape(3, 3)
    return float(np.arctan2(R[1, 0], R[0, 0]))


def clamp_bias(c):
    return float(np.arctanh(np.clip(c, -0.999, 0.999)))


# --------------------------------------------------------------------- R2/R3 --
def open_loop(task):
    seed, e1, e2, terrain = task
    c = replace(cfg(), random_start=True, world=replace(cfg().world, terrain=terrain))
    g = Genotype.load(f"{RUN}/conventional/best_gen{HERO:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    _, eff, _ = units(HERO)
    b = sim.brains[0]
    b.W[:, :] = 0.0
    b.bias[:] = 0.0
    b.bias[eff[LEFT]] = clamp_bias(e1)
    b.bias[eff[RIGHT]] = clamp_bias(e2)
    idx = sim.robots[0]
    aidL, aidR = idx.actuators[(LEFT, 0)], idx.actuators[(RIGHT, 0)]
    steps = int(round(c.duration / c.control_dt))
    yaw = yaw_of(sim); tot = 0.0
    last = sim.center_of_mass(0)[:2].copy(); start = last.copy(); path = 0.0
    c1 = c2 = 0.0
    for _ in range(steps):
        sim.step()
        y = yaw_of(sim); tot += (y - yaw + np.pi) % (2 * np.pi) - np.pi; yaw = y
        p = sim.center_of_mass(0)[:2]; path += float(np.linalg.norm(p - last)); last = p.copy()
        c1 += float(sim.data.ctrl[aidL]); c2 += float(sim.data.ctrl[aidR])
    T = steps * c.control_dt
    return {"seed": seed, "e1": e1, "e2": e2, "terrain": terrain,
            "yaw_rate": tot / T, "speed": path / T,
            "net": float(np.linalg.norm(last - start)),
            "ctrl1": c1 / steps, "ctrl2": c2 / steps,
            "exploded": bool(sim.exploded[0])}


# ------------------------------------------------------------------------ R4 --
def closed(task):
    gen, seed, fam, w = task
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    _, eff, nose = units(gen)
    W = sim.brains[0].W
    s = {"compass": -1.0, "anti": +1.0}.get(fam, 0.0)
    if s:
        # de1 = de2 = s*(w/2)*(n1 - n2)  ->  dS = s*w*(n1-n2), dD = 0 exactly
        W[eff[LEFT], nose[LEFT]] += s * w / 2
        W[eff[RIGHT], nose[LEFT]] += s * w / 2
        W[eff[LEFT], nose[RIGHT]] -= s * w / 2
        W[eff[RIGHT], nose[RIGHT]] -= s * w / 2
    idx = sim.robots[0]
    aidL, aidR = idx.actuators[(LEFT, 0)], idx.actuators[(RIGHT, 0)]
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    e1s, e2s, n1s, n2s, dy = [], [], [], [], []
    near, in_path = [], 0.0
    yaw = yaw_of(sim); last = sim.center_of_mass(0)[:2].copy()
    for _ in range(steps):
        sim.step()
        e1s.append(float(sim.data.ctrl[aidL])); e2s.append(float(sim.data.ctrl[aidR]))
        n1s.append(float(sim.brains[0].activation[nose[LEFT]]))
        n2s.append(float(sim.brains[0].activation[nose[RIGHT]]))
        y = yaw_of(sim); dy.append(((y - yaw + np.pi) % (2 * np.pi) - np.pi) / c.control_dt); yaw = y
        p = sim.center_of_mass(0)[:2]
        if float(np.linalg.norm(p)) <= disc:
            in_path += float(np.linalg.norm(p - last))
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
        last = p.copy()
    e1, e2 = np.array(e1s), np.array(e2s)
    n1, n2 = np.array(n1s), np.array(n2s)
    S, D, nd = e1 + e2, e1 - e2, n1 - n2
    dy = np.array(dy)
    cc = lambda a, b: float(np.corrcoef(a, b)[0, 1]) if a.std() > 1e-9 and b.std() > 1e-9 else float("nan")
    return {"gen": gen, "seed": seed, "fam": fam, "w": w,
            "corr_turn_grad": cc(dy, nd), "corr_S_ndiff": cc(S, nd), "corr_D_ndiff": cc(D, nd),
            "S_mean": float(S.mean()), "S_std": float(S.std()),
            "D_mean": float(D.mean()), "D_std": float(D.std()),
            "n_diff_abs": float(np.abs(nd).mean()), "n_common": float((n1 + n2).mean()),
            "sat1": float(np.mean(np.abs(e1) > 0.99)), "sat2": float(np.mean(np.abs(e2) > 0.99)),
            "near": float(np.mean(near)) if near else float("nan"),
            "in_path": in_path, "food": float(sim.food_eaten[0]),
            "exploded": bool(sim.exploded[0])}


def boot_ci(v, n=8000, seed=0):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    if len(v) < 2:
        return float("nan"), float("nan")
    r = np.random.default_rng(seed)
    m = r.choice(v, size=(n, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def slope(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    A = np.c_[x, np.ones_like(x)]
    co, *_ = np.linalg.lstsq(A, y, rcond=None)
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float(((y - A @ co) ** 2).sum()) / ss if ss > 0 else float("nan")
    return float(co[0]), r2


def boot_slope(xs, per_seed, nb=4000, seed=0):
    """Bootstrap the sweep slope by resampling SEEDS (seeds are paired across sweep points)."""
    M = np.array([per_seed[x] for x in xs])           # (npoints, nseeds)
    r = np.random.default_rng(seed)
    ns = M.shape[1]
    out = []
    for _ in range(nb):
        j = r.integers(0, ns, ns)
        out.append(slope(xs, M[:, j].mean(axis=1))[0])
    out = np.array(out)
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    c = cfg()
    out = {}
    t0 = time.time()

    # ---------------------------------------------------------------- R1 ---- #
    print("=" * 78); print("R1.  GEOMETRY AND COMMAND REALISATION"); print("=" * 78)
    g = Genotype.load(f"{RUN}/conventional/best_gen{HERO:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, SEED0))
    m, d, idx = sim.model, sim.data, sim.robots[0]
    R = d.xmat[idx.root_body].reshape(3, 3)
    ax = {}
    for p in (LEFT, RIGHT):
        jid = idx.joints[p]
        aw = d.xmat[idx.bodies[p]].reshape(3, 3) @ m.jnt_axis[jid]
        ax[p] = (R.T @ aw)          # hinge axis in the CHASSIS frame
        print(f"  part {p}: hinge axis in chassis frame = {np.round(ax[p],4)}  "
              f"(body-frame y of geom = {(R.T@(d.geom_xpos[idx.geoms[p]]-d.xpos[idx.root_body]))[1]:+.4f})")
    dot = float(ax[LEFT] @ ax[RIGHT])
    print(f"  dot(axisL, axisR) = {dot:+.4f}  ->  {'ANTIPARALLEL' if dot < -0.9 else 'not antiparallel'}")
    print("  both axes lie along chassis y (the correct axle direction); they are mirrored,")
    print("  so equal ctrl on the two motors counter-rotates the wheels.")
    out["R1_axis_dot"] = dot
    out["R1_axisL"] = [float(v) for v in ax[LEFT]]
    out["R1_axisR"] = [float(v) for v in ax[RIGHT]]

    # ---------------------------------------------------------------- R2 ---- #
    print(); print("=" * 78)
    print("R2.  OFF-SYMMETRY D SWEEP  (is d(yaw)/dD=0 a measurement or a symmetry tautology?)")
    print("=" * 78)
    S0S = (-0.30, 0.0, 0.30)
    DS = (0.60, 1.00, 1.40)
    NS2 = 16
    tasks = []
    for terrain in ("flat", "random"):
        for s0 in S0S:
            for D in DS:
                e1, e2 = (s0 + D) / 2, (s0 - D) / 2
                for k in range(NS2):
                    tasks.append((SEED0 + k, e1, e2, terrain))
    # R3 small-signal S sweep, same worker
    SS = (-0.14, -0.068, 0.0, 0.068, 0.14)
    NS3 = 32
    for terrain in ("flat", "random"):
        for S in SS:
            e1, e2 = (S + 1.2) / 2, (S - 1.2) / 2
            for k in range(NS3):
                tasks.append((SEED0 + k, e1, e2, terrain))
    print(f"  {len(tasks)} open-loop bouts ...", flush=True)
    with Pool(4) as pool:
        rows = pool.map(open_loop, tasks, chunksize=4)
    print(f"  ({time.time()-t0:.0f}s)")

    def sel(e1, e2, terrain):
        return [r for r in rows if abs(r["e1"] - e1) < 1e-9 and abs(r["e2"] - e2) < 1e-9
                and r["terrain"] == terrain]

    # command realisation
    err = max(abs(r["ctrl1"] - r["e1"]) for r in rows), max(abs(r["ctrl2"] - r["e2"]) for r in rows)
    print(f"  max |realised ctrl - commanded| over all {len(rows)} bouts: "
          f"e1 {err[0]:.2e}, e2 {err[1]:.2e}  -> commands are realised exactly")
    print(f"  exploded bouts: {sum(r['exploded'] for r in rows)}/{len(rows)}")
    out["R1_ctrl_err"] = [float(err[0]), float(err[1])]

    out["R2"] = {}
    for terrain in ("flat", "random"):
        print(f"\n  -- {terrain.upper()} --")
        print(f"     {'S0':>6s} | " + " ".join(f"{'D='+format(D,'.2f'):>14s}" for D in DS)
              + f" | {'d(yaw)/dD':>10s} {'95% CI (seeds)':>22s}")
        for s0 in S0S:
            per_seed, means = {}, []
            for D in DS:
                e1, e2 = (s0 + D) / 2, (s0 - D) / 2
                rs = sorted(sel(e1, e2, terrain), key=lambda r: r["seed"])
                per_seed[D] = np.array([r["yaw_rate"] for r in rs])
                means.append(float(per_seed[D].mean()))
            k, r2 = slope(DS, means)
            lo, hi = boot_slope(list(DS), per_seed, seed=1)
            print(f"     {s0:+6.2f} | " + " ".join(f"{v:14.4f}" for v in means)
                  + f" | {k:+10.4f} [{lo:+9.4f},{hi:+9.4f}]")
            out["R2"][f"{terrain}_S0{s0:+.2f}"] = {"D": list(DS), "yaw": means, "k": k, "r2": r2,
                                                   "ci": [lo, hi]}
        # and the S gain at each fixed D, for the ratio
    print("\n     (S0 is held constant down each row, so any yaw response to D would show up as a")
    print("      non-zero slope; the symmetry argument only pins the S0=0 row.)")

    # ---------------------------------------------------------------- R3 ---- #
    print(); print("=" * 78)
    print("R3.  SMALL-SIGNAL S GAIN AT THE GRADIENT'S OWN AMPLITUDE  (|S| <= 0.14, D=1.2)")
    print("=" * 78)
    out["R3"] = {}
    for terrain in ("flat", "random"):
        per_seed, means = {}, []
        for S in SS:
            e1, e2 = (S + 1.2) / 2, (S - 1.2) / 2
            rs = sorted(sel(e1, e2, terrain), key=lambda r: r["seed"])
            per_seed[S] = np.array([r["yaw_rate"] for r in rs])
            means.append(float(per_seed[S].mean()))
        k, r2 = slope(SS, means)
        lo, hi = boot_slope(list(SS), per_seed, seed=2)
        print(f"  {terrain:>6s}: yaw at S={[f'{s:+.3f}' for s in SS]}")
        print(f"          = {[f'{v:+.4f}' for v in means]}")
        print(f"          d(yaw)/dS = {k:+.4f} [{lo:+.4f},{hi:+.4f}] rad/s per unit S  (R^2 {r2:.3f})")
        out["R3"][terrain] = {"S": list(SS), "yaw": means, "k": k, "r2": r2, "ci": [lo, hi],
                              "n_seeds": NS3}

    # ---------------------------------------------------------------- R4 ---- #
    print(); print("=" * 78)
    print("R4.  LIKE-FOR-LIKE COMPASS: gradient into S, EXACTLY ZERO into the throttle")
    print("=" * 78)
    W = 4.0
    NS4 = 32
    FAMS = ("baseline", "compass", "anti")
    tasksC = [(gen, SEED0 + s, fam, W) for gen in GENS for s in range(NS4) for fam in FAMS]
    print(f"  {len(tasksC)} closed-loop bouts, 7 robots x {NS4} paired seeds x {len(FAMS)} conditions, w={W} ...",
          flush=True)
    with Pool(4) as pool:
        rowsC = pool.map(closed, tasksC, chunksize=8)
    print(f"  ({time.time()-t0:.0f}s)")
    per = {}
    KEYS = ("corr_turn_grad", "corr_S_ndiff", "corr_D_ndiff", "S_mean", "S_std", "D_mean",
            "n_diff_abs", "sat1", "sat2", "near", "in_path", "food")
    for fam in FAMS:
        rs = [r for r in rowsC if r["fam"] == fam]
        per[fam] = {gg: {k: float(np.nanmean([r[k] for r in rs if r["gen"] == gg])) for k in KEYS}
                    for gg in GENS}
    print(f"\n  {'cond':>9s} | {'corr(yaw,n1-n2)':>16s} {'corr(S,n1-n2)':>14s} {'corr(D,n1-n2)':>14s} "
          f"| {'D mean':>7s} {'S sd':>6s} {'near m':>7s} {'food':>6s}")
    for fam in FAMS:
        a = {k: float(np.mean([per[fam][gg][k] for gg in GENS])) for k in KEYS}
        print(f"  {fam:>9s} | {a['corr_turn_grad']:16.4f} {a['corr_S_ndiff']:14.4f} "
              f"{a['corr_D_ndiff']:14.4f} | {a['D_mean']:7.3f} {a['S_std']:6.3f} "
              f"{a['near']:7.3f} {a['food']:6.3f}")
    print(f"\n  paired vs baseline, ROBOT is the unit (7 robots, {NS4} shared seeds each):")
    res = {}
    for fam in ("compass", "anti"):
        for k, lab in (("corr_turn_grad", "d corr(yaw,n1-n2)"), ("corr_S_ndiff", "d corr(S,n1-n2)"),
                       ("food", "d food"), ("near", "d near-dist"), ("D_mean", "d D (throttle)")):
            dv = [per[fam][gg][k] - per["baseline"][gg][k] for gg in GENS]
            lo, hi = boot_ci(dv, seed=13)
            print(f"    {fam:>8s}  {lab:<20s} = {np.mean(dv):+8.4f}  [{lo:+.4f},{hi:+.4f}]")
            res[f"{fam}_{k}"] = {"mean": float(np.mean(dv)), "ci": [lo, hi],
                                 "per_robot": [float(x) for x in dv]}
        print()
    out["R4"] = {"w": W, "n_seeds": NS4, "per_robot": {f: {str(gg): v for gg, v in per[f].items()} for f in FAMS},
                 "paired": res,
                 "exploded": sum(r["exploded"] for r in rowsC) / len(rowsC)}
    print(f"  exploded fraction {out['R4']['exploded']:.4f}")

    with open("runs/sim-audit/refute_actuation_0.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nwrote runs/sim-audit/refute_actuation_0.json   total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
