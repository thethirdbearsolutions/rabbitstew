"""H7 -- TIMESCALE MISMATCH.  Does the wheel-nose differential alternate faster than the drive
can answer, so that a steady crossed weight integrates to nothing?

Three measurements, all on evolved Pioneers from runs/RBT-23/W4b-801 in their own world:

  PART A  signal timescale.  Per control tick over real bouts, record the wheel-nose
          differential D(t) = n1 - n2, the chassis heading, the position and the drive
          commands.  From D: power spectrum, autocorrelation zero-crossing and 1/e times,
          sign-run lengths, and the windowed rectification ratio |int D| / int|D| -- the
          fraction of a crossed weight's steering push that survives averaging over a
          window.

  PART B  where D's variation comes from.  With the nose offsets held in the body frame,
          split each tick's change in D into the part caused by the body rotating and the
          part caused by the body translating:
             dD_rot = Dm(p_{t-1}, psi_t)   - Dm(p_{t-1}, psi_{t-1})
             dD_tr  = Dm(p_t,     psi_{t-1}) - Dm(p_{t-1}, psi_{t-1})
          and report the share of the summed squares.

  PART C  the drive's mechanical bandwidth.  Bypassing the brain, hold both wheels at a
          forward command, then (i) step the differential and fit the yaw-rate rise time,
          (ii) drive a sinusoidal differential at 0.25-8 Hz and lock-in detect the yaw-rate
          and heading amplitude.  This is the frequency response D(t) has to live inside.

Standing rules: 64 paired seeds (same spawn_layout and set_food_seed per seed across every
robot), the robot is the unit of analysis, intervals bootstrap over robots.  No library
changes; nothing here writes to rabbitstew/.

usage: ./v/bin/python runs/sim-audit/probe_timescale.py [--seeds 64]
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from multiprocessing import Pool

import mujoco
import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

RUN = "runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
SEED0 = 9000
OUT = "runs/sim-audit/probe_timescale.json"

_CFG = None


def cfg() -> SimConfig:
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def heading(sim: Simulation, body: int) -> float:
    R = sim.data.xmat[body].reshape(3, 3)
    return float(np.arctan2(R[1, 0], R[0, 0]))


# ---------------------------------------------------------------- parts A + B


def _lp(x: np.ndarray, k: int) -> np.ndarray:
    """1 s boxcar, edges dropped: what survives to the heading integrator."""
    return np.convolve(x, np.ones(k) / k, "valid")


def _lp_corr(a: np.ndarray, b: np.ndarray, k: int) -> float:
    x, y = _lp(a, k), _lp(b, k)
    if x.std() < 1e-12 or y.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _lp_slope(a: np.ndarray, b: np.ndarray, k: int) -> float:
    """d(injected turn command) / dD at low frequency.  A working compass of weight w gives -w."""
    x, y = _lp(a, k), _lp(b, k)
    v = float(y.var())
    return float(np.cov(x, y)[0, 1] / v) if v > 1e-16 else float("nan")


def bout(args) -> dict:
    gen, seed = args
    c = cfg()
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    idx = sim.robots[0]
    gw1, gw2, gc = idx.geoms[1], idx.geoms[2], idx.geoms[0]
    aL, aR = idx.actuators[(1, 0)], idx.actuators[(2, 0)]
    br = sim.brains[0]
    e1 = br.effectors[(1, 0)][0]
    e2 = br.effectors[(2, 0)][0]
    WS = (1.0, 2.0, 4.0, 8.0)  # candidate crossed-compass weights
    decay = c.food.decay
    steps = int(round(c.duration / c.control_dt))
    dt = c.control_dt

    def field(pt2: np.ndarray, food: np.ndarray) -> float:
        """The sim's own smell model, planar, "sum" mode: total/(1+total)."""
        tot = float(np.exp(-np.linalg.norm(food - pt2, axis=1) / decay).sum())
        return tot / (1.0 + tot)

    D, N0, PSI, XY, S, FD, NEAR = [], [], [], [], [], [], []
    G1, G2, C1, C2, DPSI = [], [], [], [], []  # tanh gain/output at each effector; dD/dpsi
    inj = {w: [0.0, 0.0, []] for w in WS}  # signed sum, absolute sum, series
    rot2 = tr2 = tot2 = 0.0
    cross = 0.0
    prev = None
    off = None
    for _ in range(steps):
        sim.step()
        d = sim.data
        com = np.array(d.subtree_com[idx.root_body][:2])
        psi = heading(sim, idx.root_body)
        p1, p2 = d.geom_xpos[gw1], d.geom_xpos[gw2]
        n1 = sim._intensity(p1, sim.food_pos)
        n2 = sim._intensity(p2, sim.food_pos)
        n0 = sim._intensity(d.geom_xpos[gc], sim.food_pos)
        D.append(n1 - n2)
        N0.append(n0)
        PSI.append(psi)
        XY.append(com.copy())
        S.append(float(d.ctrl[aL] + d.ctrl[aR]))   # TURN command (anti-parallel wheel axes)
        FD.append(float(d.ctrl[aL] - d.ctrl[aR]))  # DRIVE command
        # what a SIGN-CORRECT crossed compass of weight w would actually add to the turn command,
        # through the effectors' own tanh (so saturation is counted, not assumed away)
        x1 = float(br._prev_input[e1])
        x2 = float(br._prev_input[e2])
        o1c, o2c = float(np.tanh(x1)), float(np.tanh(x2))
        G1.append(1.0 - o1c * o1c)
        G2.append(1.0 - o2c * o2c)
        C1.append(o1c)
        C2.append(o2c)
        for w in WS:
            dS = (np.tanh(x1 + w * n2) - o1c) + (np.tanh(x2 - w * n1) - o2c)
            inj[w][0] += float(dS)
            inj[w][1] += abs(float(dS))
            inj[w][2].append(float(dS))
        live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
        NEAR.append(float(np.linalg.norm(live - com, axis=1).min()) if len(live) else np.nan)
        # body-frame nose offsets, from the geometry as it actually stands this tick
        R = np.array([[np.cos(psi), -np.sin(psi)], [np.sin(psi), np.cos(psi)]])
        o1 = R.T @ (p1[:2] - com)
        o2 = R.T @ (p2[:2] - com)
        food = sim.food_pos.copy()

        def Dm(p: np.ndarray, a: float, u1=o1, u2=o2, f=food) -> float:
            Ra = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
            return field(p + Ra @ u1, f) - field(p + Ra @ u2, f)

        DPSI.append((Dm(com, psi + 0.05) - Dm(com, psi - 0.05)) / 0.10)  # dD/dpsi, the closed loop's gain
        if prev is not None:
            p0, a0 = prev
            base = Dm(p0, a0)
            dr = Dm(p0, psi) - base
            dtr = Dm(com, a0) - base
            dtt = Dm(com, psi) - base
            rot2 += dr * dr
            tr2 += dtr * dtr
            tot2 += dtt * dtt
            cross += dr * dtr
        prev = (com.copy(), psi)
        off = (o1, o2)

    D = np.asarray(D)
    PSI = np.unwrap(np.asarray(PSI))
    XY = np.asarray(XY)
    S = np.asarray(S)
    FD = np.asarray(FD)
    step_len = np.linalg.norm(np.diff(XY, axis=0), axis=1)
    path = float(step_len.sum())
    speed = step_len / dt
    omega = np.diff(PSI) / dt

    # --- spectrum of D (Hann window, one-sided power)
    x = D - D.mean()
    w = np.hanning(len(x))
    P = np.abs(np.fft.rfft(x * w)) ** 2
    f = np.fft.rfftfreq(len(x), dt)
    P[0] = 0.0
    cum = np.cumsum(P)
    tot = cum[-1] if cum[-1] > 0 else 1.0
    f50 = float(np.interp(0.5 * tot, cum, f))
    f90 = float(np.interp(0.9 * tot, cum, f))
    fpk = float(f[int(np.argmax(P))])
    fmean = float((f * P).sum() / tot)
    # yaw-rate spectrum, same treatment
    xw = omega - omega.mean()
    Pw = np.abs(np.fft.rfft(xw * np.hanning(len(xw)))) ** 2
    fw = np.fft.rfftfreq(len(xw), dt)
    Pw[0] = 0.0
    cw = np.cumsum(Pw)
    tw = cw[-1] if cw[-1] > 0 else 1.0
    w50 = float(np.interp(0.5 * tw, cw, fw))
    w90 = float(np.interp(0.9 * tw, cw, fw))
    xs = S - S.mean()
    Ps = np.abs(np.fft.rfft(xs * np.hanning(len(xs)))) ** 2
    Ps[0] = 0.0
    cs_ = np.cumsum(Ps)
    ts_ = cs_[-1] if cs_[-1] > 0 else 1.0
    s50 = float(np.interp(0.5 * ts_, cs_, f))
    s90 = float(np.interp(0.9 * ts_, cs_, f))

    # --- autocorrelation of D
    ac = np.correlate(x, x, "full")[len(x) - 1:]
    ac = ac / (ac[0] if ac[0] != 0 else 1.0)
    zc = np.nonzero(ac <= 0)[0]
    tau_zero = float(zc[0] * dt) if len(zc) else float(len(ac) * dt)
    ec = np.nonzero(ac <= np.exp(-1.0))[0]
    tau_e = float(ec[0] * dt) if len(ec) else float(len(ac) * dt)

    # --- sign runs of D
    sg = np.sign(D)
    sg[sg == 0] = 1
    flips = np.nonzero(np.diff(sg))[0]
    runs = np.diff(np.concatenate(([-1], flips, [len(sg) - 1]))) * dt
    # --- windowed rectification: how much of int|D| survives as int D
    rect = {}
    for T in (0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 15.0):
        k = max(1, int(round(T / dt)))
        nseg = len(D) // k
        if nseg == 0:
            continue
        seg = D[: nseg * k].reshape(nseg, k)
        num = np.abs(seg.sum(axis=1))
        den = np.abs(seg).sum(axis=1)
        rect[str(T)] = float(np.mean(num / np.where(den > 0, den, 1.0)))

    return {
        "gen": gen, "seed": seed, "eaten": float(sim.food_eaten[0]),
        "path": path, "net": float(np.linalg.norm(XY[-1] - XY[0])),
        "mean_speed": float(speed.mean()),
        "near_mean": float(np.nanmean(NEAR)), "near_med": float(np.nanmedian(NEAR)),
        "D_mean": float(D.mean()), "D_absmean": float(np.abs(D).mean()),
        "D_rms": float(np.sqrt((D ** 2).mean())), "D_max": float(np.abs(D).max()),
        "n0_mean": float(np.mean(N0)),
        "S_absmean": float(np.abs(S).mean()), "S_rms": float(np.sqrt((S ** 2).mean())),
        "F_absmean": float(np.abs(FD).mean()), "s50": s50, "s90": s90,
        "f50": f50, "f90": f90, "fpk": fpk, "fmean": fmean,
        "tau_zero": tau_zero, "tau_e": tau_e,
        "run_mean": float(runs.mean()), "run_med": float(np.median(runs)),
        "flips_per_s": float(len(flips) / c.duration),
        "omega_absmean": float(np.abs(omega).mean()), "omega_rms": float(np.sqrt((omega ** 2).mean())),
        "turns": float(np.abs(np.diff(PSI)).sum() / (2 * np.pi)),
        "net_yaw": float(PSI[-1] - PSI[0]),
        "w50": w50, "w90": w90,
        "rot_share": float(rot2 / (rot2 + tr2)) if (rot2 + tr2) > 0 else float("nan"),
        "rot_rms": float(np.sqrt(rot2 / max(1, steps - 1))),
        "tr_rms": float(np.sqrt(tr2 / max(1, steps - 1))),
        "model_check": float(tot2 / (rot2 + tr2 + 2 * cross)) if (rot2 + tr2 + 2 * cross) > 0 else float("nan"),
        "rect": rect,
        "gate1": float(np.mean(G1)), "gate2": float(np.mean(G2)),
        "dDdpsi": float(np.mean(DPSI)), "dDdpsi_abs": float(np.mean(np.abs(DPSI))),
        "sat_frac": float(np.mean((np.abs(C1) > 0.95) | (np.abs(C2) > 0.95))),
        "sat_both": float(np.mean((np.abs(C1) > 0.95) & (np.abs(C2) > 0.95))),
        "inj": {str(w): {"mean_abs": inj[w][1] / steps,
                         "corr_lp": _lp_corr(np.asarray(inj[w][2]), D, int(round(1.0 / dt))),
                         "slope_lp": _lp_slope(np.asarray(inj[w][2]), D, int(round(1.0 / dt))),
                         "net_over_bout": inj[w][0] * dt,
                         "abs_over_bout": inj[w][1] * dt,
                         "rect": (abs(inj[w][0]) / inj[w][1]) if inj[w][1] > 0 else float("nan"),
                         "corr_with_D": float(np.corrcoef(np.asarray(inj[w][2]), D)[0, 1])}
                for w in WS},
    }


# ------------------------------------------------------------------- part C
#
# CONVENTION, measured not assumed (H5/H6 found the same thing independently): the two drive
# wheels' hinge axes are ANTI-PARALLEL in the world (probe_actuation records +0.819,+0.574 and
# -0.819,-0.574), so the pair that TURNS this body is the SUM of the two effector commands and
# the pair that DRIVES it is the DIFFERENCE -- the opposite of the textbook differential drive.
# Everything below is therefore parametrised as
#       ctrl_1 = +F/2 + S/2 ,  ctrl_2 = -F/2 + S/2      F = drive, S = turn
# and stage C0 asserts it from the compiled model and the wheels' own rolling speeds.


def drive_probe(args) -> dict:
    """Open-loop drive dynamics on the turn axis S = ctrl_1 + ctrl_2, brain bypassed."""
    seed, flat = args
    c = cfg()
    if flat:
        c = replace(c, world=replace(c.world, terrain="flat"))
    g = Genotype.load(f"{RUN}/conventional/best_gen0590.json")
    ts = c.world.timestep
    out = {"seed": seed, "flat": flat}

    def fresh():
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        idx = sim.robots[0]
        return sim, idx, idx.actuators[(1, 0)], idx.actuators[(2, 0)], idx.root_body, idx.joints

    res = np.zeros(6)

    def run(ctrl_of, n_phys, sim, aL, aR, body):
        om, hd = [], []
        for k in range(n_phys):
            u1, u2 = ctrl_of(k * ts)
            sim.data.ctrl[aL] = u1
            sim.data.ctrl[aR] = u2
            mujoco.mj_step(sim.model, sim.data)
            mujoco.mj_objectVelocity(sim.model, sim.data, mujoco.mjtObj.mjOBJ_BODY, body, res, 0)
            om.append(float(res[2]))
            hd.append(heading(sim, body))
        return np.asarray(om), np.unwrap(np.asarray(hd))

    # --- C0 axis convention: which command pair spins the wheels the same way?
    sim, idx, aL, aR, body, joints = fresh()
    conv = {}
    for name, (u1, u2) in (("F=1.2,S=0", (0.6, -0.6)), ("F=0,S=1.2", (0.6, 0.6))):
        s2, i2, a1, a2, b2, j2 = fresh()
        run(lambda t: (u1, u2), int(1.5 / ts), s2, a1, a2, b2)
        om, hd = run(lambda t: (u1, u2), int(1.5 / ts), s2, a1, a2, b2)
        v1 = float(s2.data.qvel[s2.model.jnt_dofadr[j2[1]]])
        v2 = float(s2.data.qvel[s2.model.jnt_dofadr[j2[2]]])
        conv[name] = {"yaw_rate": float(om.mean()), "wheel_qvel": [v1, v2],
                      "same_sign": bool(v1 * v2 > 0)}
    out["convention"] = conv
    out["axis_world"] = [[round(float(x), 4) for x in sim.data.xaxis[j]] for j in (joints[1], joints[2])]

    # --- C1 step response of yaw rate to a step in the TURN command S
    taus, taus_fit, gains = [], [], []
    for sgn in (+1.0, -1.0):
        sim, idx, aL, aR, body, _ = fresh()
        run(lambda t: (0.6, -0.6), int(1.5 / ts), sim, aL, aR, body)          # straight, S = 0
        om0, _ = run(lambda t: (0.6, -0.6), int(0.3 / ts), sim, aL, aR, body)
        base = float(om0.mean())
        dS = 0.4 * sgn
        om, _ = run(lambda t: (0.6 + dS / 2, -0.6 + dS / 2), int(1.0 / ts), sim, aL, aR, body)
        y = om - base
        plateau = float(y[-int(0.4 / ts):].mean())
        if abs(plateau) < 0.05:
            continue
        gains.append(plateau / dS)
        ysm = np.convolve(y, np.ones(5) / 5, "same")                          # 25 ms smoothing
        hit = np.nonzero(ysm / plateau >= 0.632)[0]
        if len(hit):
            taus.append(float(hit[0] * ts))
        t = np.arange(len(y)) * ts
        grid = np.geomspace(0.002, 1.0, 200)
        err = [float((((plateau * (1 - np.exp(-t / tau))) - y) ** 2).sum()) for tau in grid]
        taus_fit.append(float(grid[int(np.argmin(err))]))
    out["tau_63"] = float(np.median(taus)) if taus else float("nan")
    out["tau_fit"] = float(np.median(taus_fit)) if taus_fit else float("nan")
    out["k_yaw_S"] = float(np.median(gains)) if gains else float("nan")

    # --- C2 swept sine, on the turn axis S and (for contrast) on the drive axis F
    sweep = {"S": {}, "F": {}}
    for axis in ("S", "F"):
        for fq in (0.25, 0.5, 1.0, 2.0, 4.0, 8.0):
            sim, idx, aL, aR, body, _ = fresh()
            run(lambda t: (0.6, -0.6), int(1.0 / ts), sim, aL, aR, body)
            n = min(int(round(max(4, np.ceil(fq * 3)) / fq / ts)), int(4.0 / ts))
            a = 0.2  # amplitude 0.4 on the chosen axis
            if axis == "S":
                fn = lambda t: (0.6 + a * np.sin(2 * np.pi * fq * t), -0.6 + a * np.sin(2 * np.pi * fq * t))
            else:
                fn = lambda t: (0.6 + a * np.sin(2 * np.pi * fq * t), -0.6 - a * np.sin(2 * np.pi * fq * t))
            om, hd = run(fn, n, sim, aL, aR, body)
            t = np.arange(n) * ts
            sn, cs = np.sin(2 * np.pi * fq * t), np.cos(2 * np.pi * fq * t)
            om_amp = float(np.hypot(2 * (om * sn).mean(), 2 * (om * cs).mean()))
            h = hd - hd.mean()
            hd_amp = float(np.hypot(2 * (h * sn).mean(), 2 * (h * cs).mean()))
            sweep[axis][str(fq)] = {"omega_per_amp": om_amp / 0.4, "heading_per_amp": hd_amp / 0.4}
    out["sweep"] = sweep
    return out


# ------------------------------------------------------------------- driver


def boot(vals: list, n: int = 4000, seed: int = 7) -> tuple:
    v = np.asarray([x for x in vals if np.isfinite(x)])
    if len(v) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    m = v[rng.integers(0, len(v), (n, len(v)))].mean(axis=1)
    return (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    a = ap.parse_args()
    jobs = [(g, SEED0 + s) for g in GENS for s in range(a.seeds)]
    with Pool(min(4, os.cpu_count() or 1)) as pool:
        rows = pool.map(bout, jobs, chunksize=8)
        drive = pool.map(drive_probe, [(SEED0 + s, False) for s in range(10)])
        flat = pool.map(drive_probe, [(SEED0 + s, True) for s in range(6)])

    per_robot = {}
    for r in rows:
        per_robot.setdefault(r["gen"], []).append(r)
    keys = ["eaten", "path", "net", "mean_speed", "near_mean", "D_absmean", "D_rms", "D_max",
            "n0_mean", "S_absmean", "S_rms", "F_absmean", "s50", "s90",
            "f50", "f90", "fpk", "fmean", "tau_zero", "tau_e",
            "run_mean", "run_med", "flips_per_s", "omega_absmean", "omega_rms", "turns",
            "w50", "w90", "rot_share", "rot_rms", "tr_rms", "model_check",
            "gate1", "gate2", "sat_frac", "sat_both", "dDdpsi", "dDdpsi_abs"]
    robot_means = {g: {k: float(np.nanmean([r[k] for r in rs])) for k in keys} for g, rs in per_robot.items()}
    summary = {k: {"mean": float(np.mean([robot_means[g][k] for g in GENS])),
                   "ci": boot([robot_means[g][k] for g in GENS]),
                   "per_robot": {str(g): robot_means[g][k] for g in GENS}} for k in keys}
    Ts = sorted({t for r in rows for t in r["rect"]}, key=float)
    rect = {}
    for T in Ts:
        pr = {g: float(np.mean([r["rect"][T] for r in rs if T in r["rect"]])) for g, rs in per_robot.items()}
        rect[T] = {"mean": float(np.mean(list(pr.values()))), "ci": boot(list(pr.values()))}

    def collect(ds):
        fs = sorted({f for d in ds for f in d["sweep"]["S"]}, key=float)
        sw = {ax: {f: {k: float(np.median([d["sweep"][ax][f][k] for d in ds]))
                       for k in ("omega_per_amp", "heading_per_amp")} for f in fs} for ax in ("S", "F")}
        return {"sweep": sw, "freqs": fs,
                "tau_63": float(np.nanmedian([d["tau_63"] for d in ds])),
                "tau_fit": float(np.nanmedian([d["tau_fit"] for d in ds])),
                "tau_fit_all": [d["tau_fit"] for d in ds],
                "k_yaw_S": float(np.nanmedian([abs(d["k_yaw_S"]) for d in ds]))}

    dr, fl = collect(drive), collect(flat)
    WS = sorted({w for r in rows for w in r["inj"]}, key=float)
    injag = {}
    for w in WS:
        injag[w] = {}
        for k in ("mean_abs", "net_over_bout", "abs_over_bout", "rect", "corr_with_D", "corr_lp", "slope_lp"):
            pr = [float(np.mean([abs(r["inj"][w][k]) if k == "net_over_bout" else r["inj"][w][k]
                                 for r in rs])) for g, rs in per_robot.items()]
            injag[w][k] = {"mean": float(np.mean(pr)), "ci": boot(pr)}
    res = {"seeds": a.seeds, "gens": list(GENS), "summary": summary, "rect": rect, "injection": injag,
           "drive_random_terrain": dr, "drive_flat": fl,
           "convention": drive[0]["convention"], "axis_world": drive[0]["axis_world"]}
    json.dump(res, open(OUT, "w"), indent=1)

    def line(k, unit="", scale=1.0, fmt="7.3f"):
        s = summary[k]
        print(f"  {k:14s} {s['mean']*scale:{fmt}}  [{s['ci'][0]*scale:{fmt}}, {s['ci'][1]*scale:{fmt}}] {unit}")

    c = cfg()
    print(f"\n{RUN}: {len(GENS)} evolved Pioneers x {a.seeds} paired seeds "
          f"({len(rows)} bouts of {int(c.duration/c.control_dt)} ticks at control_dt={c.control_dt}s, "
          f"physics {c.world.timestep}s)")
    print("means over robots, 95% bootstrap CI over the 7 robots\n")
    print("HEADLINE (per 15 s bout)")
    for k, u in (("eaten", "items"), ("path", "m of path"), ("net", "m net displacement"),
                 ("mean_speed", "m/s"), ("near_mean", "m to nearest live item"),
                 ("turns", "full body turns (sum|dpsi|/2pi)")):
        line(k, u)
    print("\nSIGNAL: wheel-nose differential D = n1 - n2  (nose separation = wheel track 0.387 m)")
    for k, u in (("n0_mean", "chassis nose, the DC level"), ("D_absmean", "mean |D|"),
                 ("D_rms", "rms D"), ("D_max", "max |D|")):
        line(k, u)
    print("\nTIMESCALE of D  -- how long the compass signal holds still")
    for k, u in (("tau_zero", "s   autocorrelation first zero crossing"),
                 ("tau_e", "s   autocorrelation 1/e time"),
                 ("run_mean", "s   mean run of constant sign"), ("run_med", "s   median sign run"),
                 ("flips_per_s", "Hz  sign flips"), ("f50", "Hz  median-power frequency"),
                 ("f90", "Hz  90%-power frequency"), ("fpk", "Hz  peak"),
                 ("fmean", "Hz  power-weighted mean")):
        line(k, u)
    print("\nBODY ROTATION and the commands the evolved brain already issues")
    for k, u in (("omega_absmean", "rad/s mean |yaw rate|"), ("omega_rms", "rad/s rms yaw rate"),
                 ("w50", "Hz  median-power frequency of yaw rate"), ("w90", "Hz  90%-power"),
                 ("S_absmean", "mean |turn command ctrl1+ctrl2|"), ("S_rms", "rms turn command"),
                 ("F_absmean", "mean |drive command ctrl1-ctrl2|"),
                 ("s50", "Hz  median-power frequency of the brain's own turn command"),
                 ("s90", "Hz  90%-power of the brain's own turn command")):
        line(k, u)
    print("\nWHAT MOVES D  (each tick's change split into body rotation vs body translation)")
    for k, u in (("rot_share", "share of summed-square dD from rotation"),
                 ("rot_rms", "rms per-tick dD from rotation"),
                 ("tr_rms", "rms per-tick dD from translation"),
                 ("model_check", "1.0 = the planar two-nose model reproduces the real dD")):
        line(k, u, fmt="7.4f")
    print("\nRECTIFICATION  mean |int D dt| / int |D| dt over windows of length T")
    print("  1.0 = D holds one sign across the window, so a steady weight pushes coherently;")
    print("  0.0 = it alternates and the push cancels.")
    for T in Ts:
        r = rect[T]
        print(f"  T = {float(T):5.2f} s   {r['mean']:6.3f}  [{r['ci'][0]:.3f}, {r['ci'][1]:.3f}]")

    print("\nDRIVE MECHANICS, brain bypassed.  CONVENTION CHECK (this body's wheel hinge axes"
          " are anti-parallel, so the TURN axis is S = ctrl1 + ctrl2, not the difference):")
    print(f"  wheel hinge axes in the model: {drive[0]['axis_world']}")
    for name, v in drive[0]["convention"].items():
        print(f"  {name:10s} yaw {v['yaw_rate']:+7.3f} rad/s   wheel qvel {v['wheel_qvel'][0]:+7.2f} "
              f"{v['wheel_qvel'][1]:+7.2f}  same sign: {v['same_sign']}")
    for label, d in (("random terrain (the run's own world)", dr), ("flat ground", fl)):
        print(f"\n  -- {label} --")
        print(f"  yaw-rate step response to a step in S: 63% at {d['tau_63']*1000:.0f} ms, "
              f"exp fit tau = {d['tau_fit']*1000:.0f} ms "
              f"(per seed {sorted(round(t*1000) for t in d['tau_fit_all'] if np.isfinite(t))} ms)")
        print(f"  DC steering gain: {d['k_yaw_S']:.3f} rad/s per unit turn command S")
        print(f"  {'freq Hz':>8s} | {'S axis: yaw/amp':>16s} {'vs DC':>6s} {'heading/amp rad':>16s}"
              f" | {'F axis: yaw/amp':>16s}")
        for f in d["freqs"]:
            sS, sF = d["sweep"]["S"][f], d["sweep"]["F"][f]
            print(f"  {float(f):8.2f} | {sS['omega_per_amp']:16.3f} {sS['omega_per_amp']/max(d['k_yaw_S'],1e-9):6.2f}"
                  f" {sS['heading_per_amp']:16.4f} | {sF['omega_per_amp']:16.3f}")

    # --- what a sign-correct crossed compass would actually inject, through the real tanh
    Dm = summary["D_absmean"]["mean"]
    k = fl["k_yaw_S"]
    print("\nEFFECTOR HEADROOM (a small injected weight only bites where tanh is not saturated)")
    for key, u in (("gate1", "mean tanh gain 1-ctrl^2 at effector 1"),
                   ("gate2", "mean tanh gain 1-ctrl^2 at effector 2"),
                   ("sat_frac", "fraction of ticks with either effector |ctrl| > 0.95"),
                   ("sat_both", "fraction with both saturated")):
        line(key, u, fmt="7.4f")
    print("\nWHAT A SIGN-CORRECT CROSSED COMPASS OF WEIGHT w ACTUALLY INJECTS")
    print("  (nose2 -> effector1 with +w, nose1 -> effector2 with -w, so the TURN command"
          " ctrl1+ctrl2 moves with -D; evaluated tick by tick through the real tanh)")
    print(f"  {'w':>5s} {'mean |dS|':>10s} {'ideal w|D|':>10s} {'rect':>6s} {'corr(dS,D)':>11s}"
          f" {'corr 1s-lp':>11s} {'slope 1s-lp':>12s} {'want':>6s} {'net yaw rad':>12s}")
    for w in WS:
        i = injag[w]
        net = k * i["net_over_bout"]["mean"]
        gross = k * i["abs_over_bout"]["mean"]
        print(f"  {float(w):5.1f} {i['mean_abs']['mean']:10.4f} {float(w)*Dm:10.4f}"
              f" {i['rect']['mean']:6.3f} {i['corr_with_D']['mean']:11.3f}"
              f" {i['corr_lp']['mean']:11.3f} {i['slope_lp']['mean']:12.3f} {-float(w):6.1f}"
              f" {net:12.3f}")
    print(f"\n  for reference the brain's own turn command has rms {summary['S_rms']['mean']:.2f}"
          f" and the ideal (unsaturated) injection at w=2 would be {2*Dm:.3f}")
    tau = fl["tau_fit"]
    per90 = 1.0 / summary["f90"]["mean"]
    print(f"\nTHE TWO TIMESCALES, SIDE BY SIDE")
    print(f"  drive answers a step in the turn command with tau = {tau*1000:.0f} ms"
          f" (63% at {fl['tau_63']*1000:.0f} ms); yaw-rate gain is flat to within"
          f" {100*abs(1-min(fl['sweep']['S'][f]['omega_per_amp']/fl['k_yaw_S'] for f in fl['freqs'])):.0f}%"
          f" from DC to 8 Hz")
    print(f"  the signal it would have to follow has 90% of its power below"
          f" {summary['f90']['mean']:.2f} Hz -- periods longer than {per90:.1f} s")
    gpsi = summary["dDdpsi_abs"]["mean"]
    print(f"\nCLOSED LOOP: a compass is negative feedback on bearing.  Measured |dD/dpsi| ="
          f" {gpsi:.4f} per rad, so the loop time constant is 1/(k_yaw * w * |dD/dpsi|):")
    for w in WS:
        tl = 1.0 / (k * float(w) * gpsi)
        print(f"    w = {float(w):4.1f}:  tau_loop = {tl:6.1f} s   ({c.duration/tl:5.2f} loop time"
              f" constants inside one {c.duration:.0f} s bout)")
    print(f"  phase margin is not the problem: the plant's own lag ({tau*1000:.0f} ms) is"
          f" {1.0/(k*2.0*gpsi)/max(tau,1e-9):.0f}x shorter than the w=2 loop it sits inside.")
    print(f"  ratio of the two: {per90/max(tau,1e-9):.0f}x.  D holds one sign for"
          f" {summary['run_mean']['mean']:.1f} s on average and its autocorrelation does not reach"
          f" zero for {summary['tau_zero']['mean']:.1f} s.")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
