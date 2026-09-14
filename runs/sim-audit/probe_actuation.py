"""H5 -- can this body steer at all from a wheel differential?  (open loop, no sensors)

The whole Braitenberg premise is that driving one wheel harder than the other turns the
robot.  Before blaming smell, verify the actuation.  Everything here is open loop: the
brain's weight matrix is zeroed entirely and the two drive Effectors are held at fixed
commands by their biases, so ``ctrl`` is a constant pair for the whole bout and no sensor
can touch it.

Four parts.

A.  MOTOR MODE.  Read off the compiled MuJoCo actuators for the two drive wheels: mode,
    gear, joint damping, ctrlrange, and the world direction of each hinge axis.

B.  TRANSFER FUNCTION.  ``e1`` and ``e2`` are the commands on part 1 (left drive, +y) and
    part 2 (right drive, -y).  Decompose any command pair into

        S = e1 + e2   (same sign on both effectors)
        D = e1 - e2   (opposite signs)

    and sweep each with the other held at a forward-drive baseline.  For every setting
    measure mean yaw rate (rad/s), path length, net speed, and the two wheels' mean
    tangential speeds, so we get d(yawrate)/dS and d(yawrate)/dD separately, plus the
    physical wheel-speed differential the pair produces.  Run on FLAT ground for clean
    physics and on the run's own RANDOM terrain for the number that actually applies.

C.  GAIT.  Record the unmodified evolved robots' ctrl traces over a real bout: steady or
    oscillating, and at what frequency.

D.  WHAT THE SPIKE'S CIRCUIT ACTUALLY DID.  Install the compass-spike wiring by hand and
    record the resulting (S, D) traces against the noses' common and differential modes.
    No theory: just the correlation between what the circuit adds and what the wheels do.

usage: ./v/bin/python runs/sim-audit/probe_actuation.py
"""

from __future__ import annotations

import json
import os
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
LEFT, RIGHT = 1, 2  # part indices of the two drive wheels

_CFG = None


def cfg() -> SimConfig:
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def units(gen: int):
    """Phenotype indices: the two drive effectors and the two wheel noses."""
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg().synthesis)
    eff, nose = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (LEFT, RIGHT) and u.unit.kind == "effector":
            eff[u.part] = i
        if u.part in (LEFT, RIGHT) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
    return ph, eff, nose


def yaw_of(sim: Simulation) -> float:
    R = sim.data.xmat[sim.robots[0].root_body].reshape(3, 3)
    return float(np.arctan2(R[1, 0], R[0, 0]))


ATANH_CAP = 0.999


def clamp_bias(c: float) -> float:
    return float(np.arctanh(np.clip(c, -ATANH_CAP, ATANH_CAP)))


# --------------------------------------------------------------------------- #
# B: open-loop bout
# --------------------------------------------------------------------------- #
def open_loop(task):
    """One open-loop bout at a fixed command pair.  Returns yaw rate, speeds, wheel speeds."""
    gen, seed, e1, e2, terrain = task
    c = replace(cfg(), random_start=True, world=replace(cfg().world, terrain=terrain))
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    _, eff, _ = units(gen)
    b = sim.brains[0]
    b.W[:, :] = 0.0
    b.bias[:] = 0.0
    b.bias[eff[LEFT]] = clamp_bias(e1)
    b.bias[eff[RIGHT]] = clamp_bias(e2)

    idx = sim.robots[0]
    jL, jR = idx.joints[LEFT], idx.joints[RIGHT]
    aL = sim.model.jnt_dofadr[jL]
    aR = sim.model.jnt_dofadr[jR]
    radius = sim.phenotypes[0].parts[LEFT].dims[0]

    steps = int(round(c.duration / c.control_dt))
    yaw = yaw_of(sim)
    yaw_total = 0.0
    last = sim.center_of_mass(0)[:2].copy()
    start = last.copy()
    path = 0.0
    wl, wr, ctrls = [], [], []
    for _ in range(steps):
        sim.step()
        y = yaw_of(sim)
        d = (y - yaw + np.pi) % (2 * np.pi) - np.pi
        yaw_total += d
        yaw = y
        p = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(p - last))
        last = p.copy()
        # world-frame forward tangential speed of each wheel contact
        wl.append(radius * float(sim.data.qvel[aL]))
        wr.append(-radius * float(sim.data.qvel[aR]))
        ctrls.append((float(sim.data.ctrl[idx.actuators[(LEFT, 0)]]), float(sim.data.ctrl[idx.actuators[(RIGHT, 0)]])))
    T = steps * c.control_dt
    ctrls = np.array(ctrls)
    return {
        "gen": gen, "seed": seed, "e1": e1, "e2": e2, "terrain": terrain,
        "yaw_rate": yaw_total / T,
        "path": path, "speed": path / T,
        "net": float(np.linalg.norm(last - start)),
        "vL": float(np.mean(wl)), "vR": float(np.mean(wr)),
        "ctrl1": float(ctrls[:, 0].mean()), "ctrl2": float(ctrls[:, 1].mean()),
        "exploded": bool(sim.exploded[0]),
    }


# --------------------------------------------------------------------------- #
# C / D: closed-loop trace of an evolved robot, optionally with a circuit installed
# --------------------------------------------------------------------------- #
def traced(task):
    gen, seed, fam, m = task
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    _, eff, nose = units(gen)
    W = sim.brains[0].W
    if fam == "crossed":      # exactly as runs/compass-spike/spike.py wires it
        W[eff[RIGHT], nose[LEFT]] += m
        W[eff[LEFT], nose[RIGHT]] += m
    elif fam == "uncrossed":
        W[eff[LEFT], nose[LEFT]] += m
        W[eff[RIGHT], nose[RIGHT]] += m
    elif fam == "mirror+":   # opposite signs: puts (n1 - n2) into the S channel
        W[eff[LEFT], nose[LEFT]] += m
        W[eff[RIGHT], nose[RIGHT]] -= m
    elif fam == "mirror-":   # opposite signs, other way round: puts (n2 - n1) into S
        W[eff[LEFT], nose[LEFT]] -= m
        W[eff[RIGHT], nose[RIGHT]] += m

    idx = sim.robots[0]
    aidL, aidR = idx.actuators[(LEFT, 0)], idx.actuators[(RIGHT, 0)]
    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    e1s, e2s, n1s, n2s, yaws, dyaws = [], [], [], [], [], []
    near, in_path = [], 0.0
    yaw = yaw_of(sim)
    yaw_total = 0.0
    last = sim.center_of_mass(0)[:2].copy()
    for _ in range(steps):
        sim.step()
        e1s.append(float(sim.data.ctrl[aidL]))
        e2s.append(float(sim.data.ctrl[aidR]))
        n1s.append(float(sim.brains[0].activation[nose[LEFT]]))
        n2s.append(float(sim.brains[0].activation[nose[RIGHT]]))
        y = yaw_of(sim)
        dy = (y - yaw + np.pi) % (2 * np.pi) - np.pi
        yaw_total += dy
        yaw = y
        yaws.append(yaw_total)
        dyaws.append(dy / c.control_dt)
        p = sim.center_of_mass(0)[:2]
        if float(np.linalg.norm(p)) <= disc:
            in_path += float(np.linalg.norm(p - last))
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
        last = p.copy()
    e1, e2 = np.array(e1s), np.array(e2s)
    n1, n2 = np.array(n1s), np.array(n2s)
    S, D = e1 + e2, e1 - e2
    dt = c.control_dt
    # dominant oscillation frequency of the antisymmetric (drive) and same-sign (turn) channels
    def dom_freq(x):
        x = x - x.mean()
        if np.allclose(x, 0):
            return 0.0, 0.0
        F = np.abs(np.fft.rfft(x * np.hanning(len(x))))
        f = np.fft.rfftfreq(len(x), dt)
        F[0] = 0.0
        k = int(np.argmax(F))
        return float(f[k]), float(x.std())

    fS, sS = dom_freq(S)
    fD, sD = dom_freq(D)
    return {
        "gen": gen, "seed": seed, "fam": fam, "m": m,
        "e1_mean": float(e1.mean()), "e2_mean": float(e2.mean()),
        "e1_std": float(e1.std()), "e2_std": float(e2.std()),
        "S_mean": float(S.mean()), "S_std": sS, "S_freq": fS,
        "D_mean": float(D.mean()), "D_std": sD, "D_freq": fD,
        "sat1": float(np.mean(np.abs(e1) > 0.99)), "sat2": float(np.mean(np.abs(e2) > 0.99)),
        "n_common": float((n1 + n2).mean()), "n_diff_abs": float(np.abs(n1 - n2).mean()),
        "corr_S_ncommon": float(np.corrcoef(S, n1 + n2)[0, 1]) if S.std() > 1e-9 else float("nan"),
        "corr_S_ndiff": float(np.corrcoef(S, n1 - n2)[0, 1]) if S.std() > 1e-9 else float("nan"),
        "corr_D_ncommon": float(np.corrcoef(D, n1 + n2)[0, 1]) if D.std() > 1e-9 else float("nan"),
        "corr_D_ndiff": float(np.corrcoef(D, n1 - n2)[0, 1]) if D.std() > 1e-9 else float("nan"),
        "yaw_rate": float(yaws[-1] / (steps * dt)),
        # does the robot turn toward the stronger nose?  n1 is the LEFT (+y) nose, so a
        # working compass has yaw rate (counter-clockwise positive) rising with n1 - n2.
        "corr_turn_gradient": float(np.corrcoef(np.array(dyaws), n1 - n2)[0, 1])
        if np.std(dyaws) > 1e-9 and np.std(n1 - n2) > 1e-9 else float("nan"),
        "in_disc_path": in_path,
        "near_dist": float(np.mean(near)) if near else float("nan"),
        "food": float(sim.food_eaten[0]),
    }


def boot_ci(vals, n=4000, seed=0):
    v = np.asarray([x for x in vals if np.isfinite(x)], dtype=float)
    if len(v) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    m = rng.choice(v, size=(n, len(v)), replace=True).mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def slope(xs, ys):
    """Least-squares slope through the sweep, and R^2."""
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    A = np.c_[x, np.ones_like(x)]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    ss = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(((y - pred) ** 2).sum()) / ss if ss > 0 else float("nan")
    return float(coef[0]), r2


def main():
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    c = cfg()
    out = {}

    # ------------------------------------------------------------------ A --- #
    print("=" * 78)
    print("A.  MOTOR MODE AND GEOMETRY OF THE DRIVE WHEELS")
    print("=" * 78)
    import mujoco

    g = Genotype.load(f"{RUN}/conventional/best_gen{HERO:04d}.json")
    sim = Simulation([g], replace(c, random_start=True), spawns=spawn_layout(1, c, SEED0))
    m, d, idx = sim.model, sim.data, sim.robots[0]
    ph = sim.phenotypes[0]
    modes = {}
    for part in (LEFT, RIGHT):
        aid = idx.actuators[(part, 0)]
        jid = idx.joints[part]
        bid = idx.bodies[part]
        axis_local = m.jnt_axis[jid]
        axis_world = d.xmat[bid].reshape(3, 3) @ axis_local
        gt = int(m.actuator_gaintype[aid])
        bt = int(m.actuator_biastype[aid])
        info = {
            "part": part, "motor_field": ph.parts[part].motor,
            "gaintype": gt, "biastype": bt,
            "gear": float(m.actuator_gear[aid][0]),
            "gainprm0": float(m.actuator_gainprm[aid][0]),
            "biasprm": [float(v) for v in m.actuator_biasprm[aid][:3]],
            "ctrlrange": [float(v) for v in m.actuator_ctrlrange[aid]],
            "joint_damping": float(m.dof_damping[m.jnt_dofadr[jid]]),
            "armature": float(m.dof_armature[m.jnt_dofadr[jid]]),
            "axis_world": [round(float(v), 4) for v in axis_world],
            "wheel_radius": float(ph.parts[part].dims[0]),
            "mass": float(ph.parts[part].mass),
        }
        modes[part] = info
        name = "LEFT (+y)" if part == LEFT else "RIGHT (-y)"
        print(f"  {name:11s} motor={info['motor_field']:9s} gaintype={gt} biastype={bt} "
              f"gear={info['gear']:.3f}  ctrlrange={info['ctrlrange']}")
        print(f"              joint damping={info['joint_damping']:.4f}  armature={info['armature']:.4f}  "
              f"wheel r={info['wheel_radius']:.4f} m  mass={info['mass']:.4f} kg")
        print(f"              hinge axis in WORLD at spawn = {info['axis_world']}")
    track = float(np.linalg.norm(d.geom_xpos[idx.geoms[LEFT]] - d.geom_xpos[idx.geoms[RIGHT]]))
    gear = modes[LEFT]["gear"]
    damp = modes[LEFT]["joint_damping"]
    castors = float(np.linalg.norm(d.geom_xpos[idx.geoms[3]] - d.geom_xpos[idx.geoms[4]]))
    wheelbase = float(np.linalg.norm(d.geom_xpos[idx.geoms[LEFT]] - d.geom_xpos[idx.geoms[3]]))
    print(f"  wheel track (drive geom separation) = {track:.4f} m; rear pair {castors:.4f} m; "
          f"wheelbase {wheelbase:.4f} m")
    print(f"  rear wheels: joint_type={ph.parts[3].joint_type}, axis={ph.parts[3].joint_axis} "
          f"-- HINGED FORE-AFT like the drive wheels, not swivelling castors => four-wheel SKID steer")
    print(f"  chassis mass {ph.parts[0].mass:.3f} kg, total {sum(p.mass for p in ph.parts):.3f} kg")
    print(f"  torque motor: tau = gear * ctrl = {gear:.2f} N.m at ctrl=1;  free-spin terminal "
          f"omega = gear/damping = {gear / damp:.2f} rad/s -> {gear / damp * modes[LEFT]['wheel_radius']:.2f} m/s")
    print("  => the wheels are TORQUE motors (MuJoCo <motor>, gaintype=0/biastype=0), speed-limited")
    print("     only by joint damping.  ctrl is a torque, not a velocity or a position.")
    out["A_motor"] = {str(k): v for k, v in modes.items()}
    out["A_track"] = track

    # ------------------------------------------------------------------ B --- #
    print()
    print("=" * 78)
    print("B.  OPEN-LOOP TRANSFER FUNCTION  (W zeroed; ctrl held at a constant pair)")
    print("=" * 78)
    OFF = (-0.40, -0.20, -0.10, 0.0, 0.10, 0.20, 0.40)
    P = 0.60  # forward-drive baseline

    tasks = []
    # corner probes: which command pattern is "forward" and which is "spin"?
    CORNERS = [(1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (1.0, 0.0), (0.0, 1.0)]
    for e1, e2 in CORNERS:
        for s in range(12):
            tasks.append((HERO, SEED0 + s, e1, e2, "flat"))
    # S sweep (same sign added to both) and D sweep (opposite signs), around forward drive
    for terrain, nseeds in (("flat", 12), ("random", 32)):
        for off in OFF:
            for s in range(nseeds):
                tasks.append((HERO, SEED0 + s, P + off, -P + off, terrain))   # S sweep: S = 2*off
                tasks.append((HERO, SEED0 + s, P + off, -P - off, terrain))   # D sweep: D = 2P + 2*off

    with Pool(4) as pool:
        rowsB = pool.map(open_loop, tasks, chunksize=4)

    def sel(rows, e1, e2, terrain):
        return [r for r in rows if abs(r["e1"] - e1) < 1e-9 and abs(r["e2"] - e2) < 1e-9 and r["terrain"] == terrain]

    print("\n  B1. corner probes on flat ground, 12 start poses each (15 s bouts)")
    print(f"    {'e1':>6s} {'e2':>6s} {'S':>6s} {'D':>6s} | {'yaw rate':>10s} {'net disp':>9s} "
          f"{'path':>7s} {'vL':>7s} {'vR':>7s} {'vL-vR':>7s}")
    corner_rows = {}
    for e1, e2 in CORNERS:
        rs = sel(rowsB, e1, e2, "flat")
        yr = np.mean([r["yaw_rate"] for r in rs])
        lo, hi = boot_ci([r["yaw_rate"] for r in rs])
        corner_rows[(e1, e2)] = {"yaw_rate": float(yr), "ci": [lo, hi],
                                 "net": float(np.mean([r["net"] for r in rs])),
                                 "path": float(np.mean([r["path"] for r in rs])),
                                 "vL": float(np.mean([r["vL"] for r in rs])),
                                 "vR": float(np.mean([r["vR"] for r in rs]))}
        r = corner_rows[(e1, e2)]
        print(f"    {e1:6.2f} {e2:6.2f} {e1 + e2:6.2f} {e1 - e2:6.2f} | {yr:8.3f}r/s {r['net']:8.2f}m "
              f"{r['path']:6.2f}m {r['vL']:6.2f} {r['vR']:6.2f} {r['vL'] - r['vR']:7.2f}")
    out["B1_corners"] = {f"{k[0]}|{k[1]}": v for k, v in corner_rows.items()}

    out["B2"] = {}
    for terrain, nseeds in (("flat", 12), ("random", 32)):
        print(f"\n  B2. sweeps on {terrain.upper()} terrain, forward baseline e=({P:+.2f},{-P:+.2f}), "
              f"{nseeds} paired start poses per point")
        for fam in ("S", "D"):
            print(f"\n    -- {'SAME-SIGN offset on both effectors (S sweep)' if fam == 'S' else 'OPPOSITE-SIGN offset (D sweep)'} --")
            print(f"      {'off':>6s} {'S':>6s} {'D':>6s} | {'yaw rate rad/s':>16s} {'95% CI':>18s} "
                  f"{'speed m/s':>10s} {'vL-vR m/s':>10s}")
            xs_S, xs_D, ys, sp, dv = [], [], [], [], []
            for off in OFF:
                e1 = P + off
                e2 = (-P + off) if fam == "S" else (-P - off)
                rs = sel(rowsB, e1, e2, terrain)
                yr = float(np.mean([r["yaw_rate"] for r in rs]))
                lo, hi = boot_ci([r["yaw_rate"] for r in rs])
                s_ = float(np.mean([r["speed"] for r in rs]))
                dvw = float(np.mean([r["vL"] - r["vR"] for r in rs]))
                xs_S.append(e1 + e2); xs_D.append(e1 - e2); ys.append(yr); sp.append(s_); dv.append(dvw)
                print(f"      {off:6.2f} {e1 + e2:6.2f} {e1 - e2:6.2f} | {yr:16.3f} "
                      f"[{lo:7.3f},{hi:7.3f}] {s_:10.3f} {dvw:10.3f}")
            x = xs_S if fam == "S" else xs_D
            k_yaw, r2 = slope(x, ys)
            k_spd, _ = slope(x, sp)
            k_dv, _ = slope(x, dv)
            var = "S" if fam == "S" else "D"
            print(f"      slope d(yawrate)/d{var} = {k_yaw:+.4f} rad/s per unit {var}  (R^2={r2:.3f})")
            print(f"      slope d(speed)/d{var}   = {k_spd:+.4f} m/s per unit {var}")
            print(f"      slope d(vL-vR)/d{var}   = {k_dv:+.4f} m/s per unit {var}")
            out["B2"][f"{terrain}_{fam}"] = {"off": list(OFF), "S": xs_S, "D": xs_D, "yaw": ys,
                                             "speed": sp, "dv": dv, "k_yaw": k_yaw, "r2": r2,
                                             "k_speed": k_spd, "k_dv": k_dv}

    # kinematic check: does yaw rate follow (vR - vL)/track as differential drive says?
    flat = [r for r in rowsB if r["terrain"] == "flat"]
    pred = np.array([(r["vR"] - r["vL"]) / track for r in flat])
    obs = np.array([r["yaw_rate"] for r in flat])
    ok = np.isfinite(pred) & np.isfinite(obs)
    kk, rr = slope(pred[ok], obs[ok])
    print(f"\n  B3. differential-drive kinematics check over all {ok.sum()} flat bouts:")
    print(f"      observed yaw rate vs (vR - vL)/track :  slope {kk:.3f}, R^2 {rr:.3f}, "
          f"corr {np.corrcoef(pred[ok], obs[ok])[0, 1]:.3f}")
    out["B3_kinematics"] = {"slope": kk, "r2": rr, "corr": float(np.corrcoef(pred[ok], obs[ok])[0, 1]), "n": int(ok.sum())}

    # ------------------------------------------------------------------ C --- #
    print()
    print("=" * 78)
    print("C.  IS THE EVOLVED GAIT STEADY OR OSCILLATORY?  (unmodified robots)")
    print("=" * 78)
    tasksC = [(gen, SEED0 + s, "baseline", 0.0) for gen in GENS for s in range(8)]
    with Pool(4) as pool:
        rowsC = pool.map(traced, tasksC, chunksize=4)
    print(f"    {'gen':>5s} {'e1 mean':>8s} {'e1 sd':>7s} {'e2 mean':>8s} {'e2 sd':>7s} "
          f"{'S mean':>7s} {'S sd':>6s} {'S Hz':>6s} {'D mean':>7s} {'D sd':>6s} {'D Hz':>6s} "
          f"{'sat1':>5s} {'sat2':>5s} {'food':>5s}")
    perg = {}
    for gen in GENS:
        rs = [r for r in rowsC if r["gen"] == gen]
        a = {k: float(np.mean([r[k] for r in rs])) for k in
             ("e1_mean", "e1_std", "e2_mean", "e2_std", "S_mean", "S_std", "S_freq",
              "D_mean", "D_std", "D_freq", "sat1", "sat2", "food", "yaw_rate")}
        perg[gen] = a
        print(f"    {gen:5d} {a['e1_mean']:8.3f} {a['e1_std']:7.3f} {a['e2_mean']:8.3f} {a['e2_std']:7.3f} "
              f"{a['S_mean']:7.3f} {a['S_std']:6.3f} {a['S_freq']:6.2f} {a['D_mean']:7.3f} {a['D_std']:6.3f} "
              f"{a['D_freq']:6.2f} {a['sat1']:5.2f} {a['sat2']:5.2f} {a['food']:5.2f}")
    out["C_gait"] = {str(k): v for k, v in perg.items()}
    allS = np.array([perg[g]["S_std"] for g in GENS])
    allD = np.array([perg[g]["D_std"] for g in GENS])
    print(f"\n    across the 7 robots: mean sd of S (turn channel) = {allS.mean():.3f}, "
          f"of D (drive channel) = {allD.mean():.3f}")
    print(f"    mean |S| = {np.mean([abs(perg[g]['S_mean']) for g in GENS]):.3f}, "
          f"mean |D| = {np.mean([abs(perg[g]['D_mean']) for g in GENS]):.3f}")
    print(f"    mean saturation fraction: e1 {np.mean([perg[g]['sat1'] for g in GENS]):.2f}, "
          f"e2 {np.mean([perg[g]['sat2'] for g in GENS]):.2f}")

    # ------------------------------------------------------------------ D --- #
    print()
    print("=" * 78)
    print("D.  WHAT THE COMPASS-SPIKE CIRCUIT ACTUALLY PUTS ON THE WHEELS")
    print("=" * 78)
    tasksD = [(gen, SEED0 + s, fam, 2.0) for gen in GENS for s in range(8)
              for fam in ("crossed", "uncrossed")]
    with Pool(4) as pool:
        rowsD = pool.map(traced, tasksD, chunksize=4)
    print(f"    {'fam':>10s} | {'corr(S, n1+n2)':>15s} {'corr(S, n1-n2)':>15s} "
          f"{'corr(D, n1+n2)':>15s} {'corr(D, n1-n2)':>15s} | {'S mean':>7s} {'D mean':>7s} "
          f"{'yaw r/s':>8s} {'food':>5s}")
    dsum = {}
    for fam in ("crossed", "uncrossed"):
        rs = [r for r in rowsD if r["fam"] == fam]
        # robot is the unit of analysis
        perrobot = {g: {k: float(np.mean([r[k] for r in rs if r["gen"] == g]))
                        for k in ("corr_S_ncommon", "corr_S_ndiff", "corr_D_ncommon", "corr_D_ndiff",
                                  "S_mean", "D_mean", "yaw_rate", "food", "n_common", "n_diff_abs")}
                    for g in GENS}
        a = {k: float(np.mean([perrobot[g][k] for g in GENS])) for k in perrobot[GENS[0]]}
        dsum[fam] = {"mean": a, "per_robot": {str(k): v for k, v in perrobot.items()}}
        print(f"    {fam:>10s} | {a['corr_S_ncommon']:15.3f} {a['corr_S_ndiff']:15.3f} "
              f"{a['corr_D_ncommon']:15.3f} {a['corr_D_ndiff']:15.3f} | {a['S_mean']:7.3f} "
              f"{a['D_mean']:7.3f} {a['yaw_rate']:8.3f} {a['food']:5.2f}")
    base = {g: float(np.mean([r["food"] for r in rowsC if r["gen"] == g])) for g in GENS}
    print(f"\n    baseline food (same robots, same 8 seeds) = {np.mean(list(base.values())):.3f}")
    nc = dsum["crossed"]["mean"]["n_common"]
    nd = dsum["crossed"]["mean"]["n_diff_abs"]
    print(f"    noses over these bouts: mean(n1+n2) = {nc:.4f}, mean|n1-n2| = {nd:.4f} "
          f"(differential is {100 * nd / nc:.1f}% of common)")
    out["D_circuit"] = dsum
    out["D_baseline_food"] = base

    # ------------------------------------------------------------------ E --- #
    print()
    print("=" * 78)
    print("E.  WHAT THAT BUYS IN TURNING, AT THE MEASURED GAINS")
    print("=" * 78)
    kS = out["B2"]["random_S"]["k_yaw"]
    kD = out["B2"]["random_D"]["k_yaw"]
    kSf = out["B2"]["flat_S"]["k_yaw"]
    kDf = out["B2"]["flat_D"]["k_yaw"]
    print(f"    yaw gain per unit S (same-sign offset) : {kSf:+.4f} rad/s flat, {kS:+.4f} rad/s random")
    print(f"    yaw gain per unit D (opposite-sign)    : {kDf:+.4f} rad/s flat, {kD:+.4f} rad/s random")
    for w in (0.5, 1.0, 2.0, 4.0, 8.0):
        # spike's crossed wiring adds +w*n2 to e1 and +w*n1 to e2 (before tanh/clip)
        dS = w * nc          # same-sign channel gets the COMMON mode
        dD = -w * nd         # opposite-sign channel gets the DIFFERENTIAL (sign set by which nose leads)
        print(f"    w={w:4.1f}: circuit adds  S += {dS:+.3f} (common mode) -> {kSf * dS:+.3f} rad/s of turn;"
              f"  D += {dD:+.3f} (gradient) -> {kDf * dD:+.3f} rad/s of turn")
    out["E"] = {"k_yaw_S_flat": kSf, "k_yaw_D_flat": kDf, "k_yaw_S_random": kS, "k_yaw_D_random": kD,
                "n_common": nc, "n_diff_abs": nd}

    # ------------------------------------------------------------------ F --- #
    print()
    print("=" * 78)
    print("F.  WIRING THE GRADIENT INTO THE CHANNEL THAT ACTUALLY STEERS  (32 paired seeds)")
    print("=" * 78)
    print("    mirror+/- put OPPOSITE-sign weights on the two nose->wheel links, so S (the")
    print("    steering channel) carries n1-n2 and D (the throttle) carries n1+n2 -- the")
    print("    transpose of the spike's matched-sign wiring.  Does the robot then turn toward")
    print("    the stronger nose?  n1 is the LEFT nose; a compass has corr(yawrate, n1-n2) > 0.")
    NS = 32
    FAMS = ("baseline", "crossed", "mirror+", "mirror-")
    tasksF = [(gen, SEED0 + s, fam, 2.0) for gen in GENS for s in range(NS) for fam in FAMS]
    with Pool(4) as pool:
        rowsF = pool.map(traced, tasksF, chunksize=8)
    print(f"\n    {'wiring':>9s} | {'corr(yawrate,n1-n2)':>20s} {'95% CI over robots':>22s} | "
          f"{'corr(S,n1-n2)':>13s} {'|yaw| r/s':>9s} {'near m':>7s} {'food':>6s}")
    fsum = {}
    for fam in FAMS:
        rs = [r for r in rowsF if r["fam"] == fam]
        per = {g: {k: float(np.nanmean([r[k] for r in rs if r["gen"] == g]))
                   for k in ("corr_turn_gradient", "corr_S_ndiff", "corr_S_ncommon",
                             "yaw_rate", "near_dist", "food", "in_disc_path", "S_std", "sat1", "sat2")}
               for g in GENS}
        a = {k: float(np.nanmean([per[g][k] for g in GENS])) for k in per[GENS[0]]}
        lo, hi = boot_ci([per[g]["corr_turn_gradient"] for g in GENS], seed=7)
        fsum[fam] = {"mean": a, "ci_corr_turn": [lo, hi], "per_robot": {str(k): v for k, v in per.items()}}
        print(f"    {fam:>9s} | {a['corr_turn_gradient']:20.4f} [{lo:10.4f},{hi:10.4f}] | "
              f"{a['corr_S_ndiff']:13.3f} {abs(a['yaw_rate']):9.3f} {a['near_dist']:7.3f} {a['food']:6.3f}")
    # paired difference against baseline, robot as the unit
    print(f"\n    paired vs baseline (robot is the unit, 7 robots x {NS} shared seeds):")
    b = fsum["baseline"]["per_robot"]
    for fam in ("crossed", "mirror+", "mirror-"):
        p = fsum[fam]["per_robot"]
        dcorr = [p[str(g)]["corr_turn_gradient"] - b[str(g)]["corr_turn_gradient"] for g in GENS]
        dfood = [p[str(g)]["food"] - b[str(g)]["food"] for g in GENS]
        c1 = boot_ci(dcorr, seed=11)
        c2 = boot_ci(dfood, seed=12)
        print(f"      {fam:>9s}: d corr(yawrate,n1-n2) = {np.mean(dcorr):+.4f} [{c1[0]:+.4f},{c1[1]:+.4f}]"
              f"   d food = {np.mean(dfood):+.3f} [{c2[0]:+.3f},{c2[1]:+.3f}]")
    out["F"] = {k: {"mean": v["mean"], "ci_corr_turn": v["ci_corr_turn"],
                    "per_robot": v["per_robot"]} for k, v in fsum.items()}

    with open("runs/sim-audit/probe_actuation.json", "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote runs/sim-audit/probe_actuation.json")


if __name__ == "__main__":
    main()
