"""H2 -- does the TASK reward steering at all?  A cheating oracle sets the ceiling.

The compass spike (runs/compass-spike/) found that a hand-installed Braitenberg circuit earns
nothing.  Before blaming the nose, establish the headroom: replace the sensor-and-brain chain
with an ORACLE that is handed the true bearing to the nearest live item every control tick and
drives the wheels straight at it.  If a perfect compass cannot beat the blind mower, the sensor
was never the binding constraint -- the task was.

Method
------
The oracle bypasses the evolved brain entirely for the drive signal: sim.brains[0] is wrapped in
a shim that keeps the real brain's sensors (so nothing else in Simulation.step changes) but whose
effector_output() returns the oracle's wheel commands.  No library code is touched.

Drive convention, measured (runs/sim-audit/_calib.py, flat world, no obstacles):
    forward is the chassis geom's local +x;  e1=+1, e2=-1  ->  1.50 m/s straight, 0 deg/s yaw
    e1=+1, e2=+1  ->  -71 deg/s yaw, 0.08 m/s   (spin in place)
so  e1 = f - w,  e2 = -(f + w)  with f forward throttle and w a CCW-positive turn command.

Standing rules: 64 PAIRED seeds (same spawn_layout and same set_food_seed for every condition),
the ROBOT is the unit of analysis, intervals bootstrap over robots.  The oracle's gains are tuned
on a DISJOINT seed block (7000-7015) so the headline seeds are never used to pick a policy.

usage:  ./v/bin/python runs/sim-audit/probe_oracle.py [--seeds 64] [--tune]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)   # the same seven Pioneers the compass spike used
SEED0 = 9000                                 # headline seeds, as in the spike
TUNE0 = 7000                                 # disjoint block for choosing the gains
CHASSIS, WL, WR = 0, 1, 2

_CFG = None


def cfg() -> SimConfig:
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


# --------------------------------------------------------------------------- #
# the cheating controller
# --------------------------------------------------------------------------- #
class OracleBrain:
    """Wraps a RuntimeBrain, keeps its sensors, replaces its wheel commands with pure pursuit
    of the nearest LIVE food item using the true world state."""

    def __init__(self, inner, sim, kw: float, kf: float, power: float, fake=None):
        self.inner, self.sim = inner, sim
        self.kw, self.kf, self.power = kw, kf, power
        self.fake = None if fake is None else np.asarray(fake, dtype=float)
        self.fake_live = None if fake is None else np.ones(len(fake), dtype=bool)
        self.sensors = inner.sensors
        self.W = inner.W
        self.cmd = {(WL, 0): 0.0, (WR, 0): 0.0}
        self.err_sum, self.n_err = 0.0, 0

    def reset(self):
        self.inner.reset()

    def step(self, vals):
        self.inner.step(vals)                      # harmless; its outputs are discarded
        sim, d = self.sim, self.sim.data
        gid = sim.robots[0].geoms[CHASSIS]
        p = d.geom_xpos[gid][:2]
        R = d.geom_xmat[gid].reshape(3, 3)
        fwd = R[:2, 0]
        n = float(np.linalg.norm(fwd))
        if self.fake is None:
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else np.zeros((0, 2))
        else:   # the decoy control: same law, same motion statistics, wrong target information
            if self.fake_live.any():
                self.fake_live[np.linalg.norm(self.fake - p, axis=1) < sim.config.food.eat_radius] = False
            live = self.fake[self.fake_live]
        if len(live) == 0 or n < 1e-9:
            f, w = self.kf, 0.0
        else:
            fwd = fwd / n
            v = live[int(np.argmin(np.linalg.norm(live - p, axis=1)))] - p
            err = float(np.arctan2(fwd[0] * v[1] - fwd[1] * v[0], fwd[0] * v[0] + fwd[1] * v[1]))
            self.err_sum += abs(err); self.n_err += 1
            w = float(np.clip(self.kw * err, -1.0, 1.0))
            f = self.kf * max(0.0, np.cos(err)) ** self.power
        self.cmd = {(WL, 0): float(np.clip(f - w, -1, 1)), (WR, 0): float(np.clip(-f - w, -1, 1))}

    def effector_output(self, part, dof):
        return self.cmd.get((part, dof), 0.0)

    def outputs(self):
        return dict(self.cmd)


# --------------------------------------------------------------------------- #
# one bout
# --------------------------------------------------------------------------- #
def bout(task) -> dict:
    gen, seed, mode, gains = task
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    if mode == "wire" and gains is not None:
        fam, m = gains
        ph = synthesize(g, c.synthesis)
        nose = {u.part: i for i, u in enumerate(ph.units)
                if u.part in (WL, WR) and u.unit.kind == "sensor" and u.unit.source == "food"}
        eff = {u.part: i for i, u in enumerate(ph.units) if u.part in (WL, WR) and u.unit.kind == "effector"}
        W = sim.brains[0].W
        if fam == "spike":       # exactly what runs/compass-spike/spike.py installs
            W[eff[WR], nose[WL]] += m; W[eff[WL], nose[WR]] += m
        else:                    # sign-corrected: crossed EXCITATION in physical wheel terms
            W[eff[WL], nose[WR]] += m; W[eff[WR], nose[WL]] += -m
    oracle = None
    if mode in ("oracle", "decoy"):
        fake = None
        if mode == "decoy":     # 12 phantom items, same disc, same clearance, independent draw
            rng = np.random.default_rng(seed + 500000)
            q0 = sim.data.geom_xpos[sim.robots[0].geoms[CHASSIS]][:2]
            pts = []
            while len(pts) < c.food.items:
                r = c.food.radius * np.sqrt(rng.random()); a = rng.uniform(0, 2 * np.pi)
                z = np.array([r * np.cos(a), r * np.sin(a)])
                if np.linalg.norm(z - q0) >= c.food.clearance:
                    pts.append(z)
            fake = np.array(pts)
        oracle = OracleBrain(sim.brains[0], sim, *gains, fake=fake)
        sim.brains[0] = oracle

    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    gid0 = sim.robots[0].geoms[CHASSIS]
    spots0 = sim.food_pos.copy()                      # the exact layout this bout starts from
    p0 = sim.data.geom_xpos[gid0][:2].copy()
    R0 = sim.data.geom_xmat[gid0].reshape(3, 3)
    h0 = float(np.arctan2(R0[1, 0], R0[0, 0]))
    last = sim.center_of_mass(0)[:2].copy()
    path = in_path = in_ticks = 0.0
    near_all, near_in = [], []
    yaws, fwds = [], []
    for _ in range(steps):
        sim.step()
        Rk = sim.data.geom_xmat[gid0].reshape(3, 3)
        yaws.append(float(np.arctan2(Rk[1, 0], Rk[0, 0])))
        vk = sim.data.geom_xpos[gid0][:2] - last
        fwds.append(float(np.dot(vk, Rk[:2, 0]) / c.control_dt))
        p = sim.center_of_mass(0)[:2]
        step_len = float(np.linalg.norm(p - last)); last = p.copy()
        path += step_len
        r = float(np.linalg.norm(p))
        live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else np.zeros((0, 2))
        nd = float(np.linalg.norm(live - p, axis=1).min()) if len(live) else np.nan
        near_all.append(nd)
        if r <= disc:
            in_ticks += 1; in_path += step_len
            near_in.append(nd)
    return {"gen": gen, "seed": seed, "mode": mode,
            "spots": spots0, "p0": p0, "h0": h0,
            "items": float(sim.food_eaten[0]),
            "score": float(sim.food_score(0)),
            "near_all": float(np.nanmean(near_all)),
            "near_in": float(np.nanmean(near_in)) if near_in else np.nan,
            "path": path, "in_path": in_path, "in_disc": in_ticks / steps,
            "items_per_m": float(sim.food_eaten[0]) / path if path > 0.05 else 0.0,
            "exploded": float(bool(sim.exploded[0])),
            "wire": repr(gains) if mode == "wire" else mode,
            "yawrate": float(np.degrees(np.abs(np.diff(np.unwrap(yaws)))).mean() / c.control_dt),
            "fwd": float(np.mean(fwds)),
            "abs_err": (oracle.err_sum / max(1, oracle.n_err)) if oracle else np.nan}


# --------------------------------------------------------------------------- #
# crude upper bound: a point robot that always drives flat out along a greedy tour
# --------------------------------------------------------------------------- #
def teleport_bound(spots, p0, h0, duration, eat_radius, vmax, yawrate):
    """How many of the 12 items a robot could reach in the bout if it followed a greedy
    nearest-first tour at top speed, from the bout's real start pose and real layout.
    Returns (no turn cost, charged for turning in place at ``yawrate`` deg/s)."""
    spots = np.asarray(spots, dtype=float)
    out = []
    for charge in (False, True):
        live = np.ones(len(spots), dtype=bool)
        p, hd, t, n = np.asarray(p0, float).copy(), float(h0), 0.0, 0
        while live.any():
            idx = np.nonzero(live)[0]
            j = idx[int(np.argmin(np.linalg.norm(spots[idx] - p, axis=1)))]
            v = spots[j] - p
            t += max(0.0, float(np.linalg.norm(v)) - eat_radius) / vmax
            if charge:
                want = float(np.arctan2(v[1], v[0]))
                t += abs(float(np.arctan2(np.sin(want - hd), np.cos(want - hd)))) / np.radians(yawrate)
                hd = want
            if t > duration:
                break
            n += 1; p = spots[j]; live[j] = False
        out.append(n)
    return out[0], out[1]



# --------------------------------------------------------------------------- #
# side check: is the compass spike's "crossed" wiring physically a compass?
# --------------------------------------------------------------------------- #
# Measured convention: forward = e1 - e2, turn (CCW) = -(e1 + e2).  A weight k added to BOTH
# effector units (what the spike does: W[eff2,nose1] += s*m and W[eff1,nose2] += s*m, same sign)
# therefore contributes  dforward = k(n2-n1)/2  and  dturn = -k(n1+n2)/2.  That routes the big DC
# common mode (0.33) into SPIN and the tiny gradient (0.04) into forward speed -- the inverse of a
# Braitenberg compass, and it is identical for crossed and uncrossed.  The sign-corrected compass
# respects the wheel convention: W[eff1,nose2] += +m, W[eff2,nose1] += -m.
def signcheck(pool):
    gens, seeds = (390, 590), [SEED0 + s for s in range(32)]
    conds = [("baseline", None), ("spike-crossed +4", ("spike", +4.0)), ("corrected +2", ("corr", +2.0)),
             ("corrected -2", ("corr", -2.0)), ("corrected +4", ("corr", +4.0))]
    tasks = [(g, s, "wire", c[1]) for c in conds for g in gens for s in seeds]
    out = pool.map(bout, tasks)
    by = {}
    for r in out:
        by.setdefault(r["wire"], []).append(r)
    print(f"SIGN CHECK -- {len(gens)} Pioneers x {len(seeds)} paired seeds")
    print(f"  {'wiring':>18s} {'items':>7s} {'path m':>8s} {'|yaw| deg/s':>12s} {'fwd speed':>10s} {'nearest m':>10s}")
    for name, w in conds:
        t = table(by[repr(w)], keys=("items", "path", "yawrate", "fwd", "near_all"))
        print(f"  {name:>18s} {t['items']:7.2f} {t['path']:8.2f} {t['yawrate']:12.1f} {t['fwd']:10.3f} {t['near_all']:10.2f}")


# --------------------------------------------------------------------------- #
def boot_ci(per_robot: np.ndarray, n: int = 20000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    k = len(per_robot)
    draws = per_robot[rng.integers(0, k, size=(n, k))].mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def table(rows, keys=("items", "near_all", "near_in", "in_path", "path", "in_disc", "score", "items_per_m", "exploded")):
    return {k: float(np.nanmean([r[k] for r in rows])) for k in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--tune", action="store_true")
    ap.add_argument("--signcheck", action="store_true")
    ap.add_argument("--procs", type=int, default=8)
    args = ap.parse_args()

    # the body is fixed, so the oracle's bout depends only on the seed, not on the robot
    ph = [synthesize(Genotype.load(f"{RUN}/conventional/best_gen{g:04d}.json"), cfg().synthesis) for g in GENS]
    sig = {tuple(tuple(np.round(p.dims, 9)) for p in x.parts) for x in ph}
    assert len(sig) == 1, "the seven Pioneers are not the same body -- the oracle must be re-run per robot"

    pool = Pool(args.procs)

    if args.tune:
        grid = [(2.0, 1.0, 1.0), (2.0, 1.0, 0.0), (4.0, 1.0, 1.0), (1.0, 1.0, 1.0),
                (4.0, 1.0, 2.0), (8.0, 1.0, 2.0), (4.0, 0.6, 1.0), (2.0, 1.0, 2.0)]
        seeds = [TUNE0 + s for s in range(16)]
        base = pool.map(bout, [(590, s, "base", None) for s in seeds])
        print(f"TUNING on {len(seeds)} disjoint seeds ({TUNE0}..{TUNE0+15}), gen 590 only")
        b = table(base)
        print(f"  {'policy':>22s} {'items':>7s} {'nearest m':>10s} {'|err| deg':>10s} {'path m':>8s}")
        print(f"  {'baseline (evolved)':>22s} {b['items']:7.2f} {b['near_all']:10.2f} {'-':>10s} {b['path']:8.1f}")
        for gains in grid:
            rs = pool.map(bout, [(590, s, "oracle", gains) for s in seeds])
            t = table(rs)
            e = float(np.nanmean([r["abs_err"] for r in rs]))
            print(f"  kw={gains[0]:<4g} kf={gains[1]:<4g} p={gains[2]:<3g} {t['items']:7.2f} {t['near_all']:10.2f}"
                  f" {np.degrees(e):10.1f} {t['path']:8.1f}")
        return

    if args.signcheck:
        signcheck(pool); return

    GAINS = (4.0, 1.0, 2.0)     # best on the disjoint tuning block (4.62 items); see --tune
    seeds = [SEED0 + s for s in range(args.seeds)]
    tasks = [(g, s, "base", None) for g in GENS for s in seeds]
    tasks += [(GENS[0], s, "oracle", GAINS) for s in seeds]   # body-independent: one run per seed
    tasks += [(GENS[0], s, "decoy", GAINS) for s in seeds]
    out = pool.map(bout, tasks)
    base = {(r["gen"], r["seed"]): r for r in out if r["mode"] == "base"}
    orac = {r["seed"]: r for r in out if r["mode"] == "oracle"}
    dec = {r["seed"]: r for r in out if r["mode"] == "decoy"}

    print(f"H2 ORACLE PROBE -- {RUN}, {len(GENS)} Pioneers x {len(seeds)} paired seeds "
          f"(same layout + start per pair), oracle gains kw={GAINS[0]} kf={GAINS[1]} power={GAINS[2]}")
    print(f"world: {cfg().duration:g} s, {cfg().food.items} items in a {cfg().food.radius:g} m disc, "
          f"eat radius {cfg().food.eat_radius:g} m, decay {cfg().food.decay:g} m\n")

    bb = table([base[(g, s)] for g in GENS for s in seeds])
    oo = table([orac[s] for s in seeds])
    dd = table([dec[s] for s in seeds])
    hdr = (f"{'':>22s} {'items':>7s} {'score':>7s} {'nearest m':>10s} {'near in-disc':>13s} {'in-disc m':>10s}"
           f" {'path m':>8s} {'items/m':>8s} {'in disc':>8s} {'blown':>6s}")
    print(hdr)
    for name, t in (("baseline (evolved)", bb), ("ORACLE (cheating)", oo), ("decoy (wrong info)", dd)):
        print(f"{name:>22s} {t['items']:7.2f} {t['score']:7.2f} {t['near_all']:10.2f} {t['near_in']:13.2f}"
              f" {t['in_path']:10.2f} {t['path']:8.2f} {t['items_per_m']:8.3f} {100*t['in_disc']:7.0f}%"
              f" {100*t['exploded']:5.0f}%")
    print(f"{'oracle |bearing err|':>22s} {np.degrees(np.nanmean([orac[s]['abs_err'] for s in seeds])):6.1f} deg")

    print("\nper robot (mean over the 64 paired seeds):")
    print(f"  {'gen':>5s} {'base items':>11s} {'oracle items':>13s} {'delta':>7s} {'base nearest':>13s} {'oracle nearest':>15s}")
    d_items, d_near = [], []
    for g in GENS:
        bi = np.mean([base[(g, s)]["items"] for s in seeds])
        oi = np.mean([orac[s]["items"] for s in seeds])
        bn = np.nanmean([base[(g, s)]["near_all"] for s in seeds])
        on = np.nanmean([orac[s]["near_all"] for s in seeds])
        d_items.append(oi - bi); d_near.append(on - bn)
        print(f"  {g:5d} {bi:11.2f} {oi:13.2f} {oi-bi:+7.2f} {bn:13.2f} {on:15.2f}")
    d_items, d_near = np.array(d_items), np.array(d_near)
    lo, hi = boot_ci(d_items)
    print(f"\ndelta items (oracle - baseline), bootstrap over {len(GENS)} robots: "
          f"{d_items.mean():+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]")
    lo2, hi2 = boot_ci(d_near)
    print(f"delta mean distance to nearest live item: {d_near.mean():+.3f} m  95% CI [{lo2:+.3f}, {hi2:+.3f}]  "
          f"(negative = the oracle homes)")

    # per-seed paired sign test against the pooled baseline, as a sanity cross-check
    wins = sum(1 for s in seeds if orac[s]["items"] > np.mean([base[(g, s)]["items"] for g in GENS]))
    print(f"seeds where the oracle beats the mean baseline: {wins}/{len(seeds)}")
    dwin = sum(1 for s in seeds if dec[s]["items"] > np.mean([base[(g, s)]["items"] for g in GENS]))
    print(f"seeds where the DECOY beats the mean baseline:  {dwin}/{len(seeds)}   "
          f"(decoy - baseline = {dd['items'] - bb['items']:+.3f} items, oracle - decoy = {oo['items'] - dd['items']:+.3f})")

    vmax, yawrate = 1.45, 70.0   # measured: 1.45 m/s flat out on the real terrain, 70 deg/s spin
    fc = cfg().food
    nb = np.array([teleport_bound(orac[s]["spots"], orac[s]["p0"], orac[s]["h0"],
                                  cfg().duration, fc.eat_radius, vmax, yawrate) for s in seeds])
    print(f"\ncrude upper bounds over the same {len(seeds)} layouts "
          f"(greedy nearest-first tour, {vmax} m/s, eat radius credited):")
    print(f"  items reachable in {cfg().duration:g} s, no turn cost   : {nb[:,0].mean():.2f}  (max {nb[:,0].max():.0f})")
    print(f"  items reachable in {cfg().duration:g} s, turning at {yawrate:g} deg/s: {nb[:,1].mean():.2f}  (max {nb[:,1].max():.0f})")
    print(f"  distance budget = {vmax*cfg().duration:.1f} m of path in a {cfg().food.radius:g} m disc")

    print(f"\nHEADROOM: baseline {bb['items']:.2f} -> oracle {oo['items']:.2f} -> path-limited bound "
          f"{nb[:,1].mean():.2f} (with turn cost) / {nb[:,0].mean():.2f} (without)")


if __name__ == "__main__":
    main()
