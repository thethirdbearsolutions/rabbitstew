"""RBT-121 adversary (physics): re-derive audit A's A2 "ghost limbs" numbers with an independent inside-ness measure.

    phys_ghost.py [--per-group K] [--workers W] SEED_DIR [...] > phys_ghost.txt

Same members as audit A's probe_ghost.py (rng 121, K per group per directory, holistic fauna, decompose.py draw 0).
Per parent-child pair (a part and its parent part, one geom each) it reports, at the season's first tick and at every
control tick:
  sd     signed geom distance from mj_geomDistance (audit A's metric; < -2 cm counts as "embedded")
  cin    the child's geom CENTRE lies inside the parent's geom (exact point-in-box/sphere/cylinder test)
  vfrac  fraction of the child's geom VOLUME inside the parent's geom (Monte Carlo, 256 fixed points per child)
Work is attributed EXACTLY: per-actuator |force x velocity| x timestep accumulated at every physics substep (the same
formula as Simulation.step), and a tick's actuator work is booked "embedded" under each criterion if that actuator's
joint's child is embedded at the end of the tick.  Also reports the model's collision flags (filterparent,
contype/conaffinity, excludes) and the joint-type / motor-mode mix of embedded pairs.  Nothing is written into any run.
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

TERRAIN, START = decompose.DRAWS[0]
NPTS = 256


def local_samples(m, gid, rng):
    t, s = m.geom_type[gid], m.geom_size[gid]
    u = rng.uniform(-1, 1, (NPTS * 4, 3))
    if t == mujoco.mjtGeom.mjGEOM_BOX:
        return u[:NPTS] * s
    if t == mujoco.mjtGeom.mjGEOM_SPHERE:
        u = u[np.linalg.norm(u, axis=1) <= 1][:NPTS]
        return u * s[0]
    if t == mujoco.mjtGeom.mjGEOM_CYLINDER:
        u = u[np.linalg.norm(u[:, :2], axis=1) <= 1][:NPTS]
        return u * np.array([s[0], s[0], s[1]])
    raise ValueError(t)


def inside(m, d, gid, pts_world):
    t, s = m.geom_type[gid], m.geom_size[gid]
    loc = (pts_world - d.geom_xpos[gid]) @ d.geom_xmat[gid].reshape(3, 3)
    if t == mujoco.mjtGeom.mjGEOM_BOX:
        return np.all(np.abs(loc) <= s, axis=1)
    if t == mujoco.mjtGeom.mjGEOM_SPHERE:
        return np.linalg.norm(loc, axis=1) <= s[0]
    return (np.linalg.norm(loc[:, :2], axis=1) <= s[0]) & (np.abs(loc[:, 2]) <= s[1])


def job(args):
    gd, sc = args
    g = Genotype.from_dict(gd)
    cfg = replace(sc, random_start=True)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, START))
    sim.set_food_seed(START)
    m, d, idx, ph = sim.model, sim.data, sim.robots[0], sim.phenotypes[0]
    flags = dict(filterparent_disabled=bool(m.opt.disableflags & mujoco.mjtDisableBit.mjDSBL_FILTERPARENT),
                 contact_disabled=bool(m.opt.disableflags & mujoco.mjtDisableBit.mjDSBL_CONTACT),
                 nexclude=int(m.nexclude), npair=int(m.npair),
                 contype=sorted(set(int(x) for x in m.geom_contype[list(idx.geoms)])),
                 conaff=sorted(set(int(x) for x in m.geom_conaffinity[list(idx.geoms)])))
    rng = np.random.default_rng(0)
    pairs = []
    for p in ph.parts:
        if p.parent is None:
            continue
        gc, gp = idx.geoms[p.index], idx.geoms[p.parent]
        pairs.append(dict(pi=p.index, gc=gc, gp=gp, jt=p.joint_type.name, motor=p.motor, loc=local_samples(m, gc, rng)))
    act_of = {}
    for (pi, dof), aid in idx.actuators.items():
        act_of.setdefault(pi, []).append(aid)

    def measure(pr):
        sd = mujoco.mj_geomDistance(m, d, pr["gc"], pr["gp"], 0.5, None)
        pts = d.geom_xpos[pr["gc"]] + pr["loc"] @ d.geom_xmat[pr["gc"]].reshape(3, 3).T
        vf = float(inside(m, d, pr["gp"], pts).mean())
        cin = bool(inside(m, d, pr["gp"], d.geom_xpos[pr["gc"]][None])[0])
        return sd, cin, vf

    start = [measure(pr) for pr in pairs]
    # non-parent same-robot geom pairs that overlap at start but produce no contact (filtered some other way)
    gl = list(idx.geoms)
    par = {(pr["gc"], pr["gp"]) for pr in pairs} | {(pr["gp"], pr["gc"]) for pr in pairs}
    con = {(int(c.geom1), int(c.geom2)) for c in d.contact[: d.ncon]}
    con |= {(b, a) for a, b in con}
    hidden = 0
    for i_, a_ in enumerate(gl):
        for b_ in gl[i_ + 1:]:
            if (a_, b_) in par:
                continue
            if mujoco.mj_geomDistance(m, d, a_, b_, 0.5, None) < -0.005 and (a_, b_) not in con:
                hidden += 1
    # exact per-actuator work, hooked into every mj_step Simulation.step makes
    real_step = mujoco.mj_step
    acc = np.zeros(m.nu)

    class Hook:
        def __getattr__(self, k):
            return getattr(mujoco, k)

        def mj_step(self, mm, dd):
            real_step(mm, dd)
            if mm.nu:
                acc[:] += np.abs(dd.actuator_force * dd.actuator_velocity) * cfg.world.timestep

    S.mujoco = Hook()
    n = int(round(cfg.duration / cfg.control_dt))
    crit = ["sd", "cin", "v50", "v10", "free", "freeout"]
    wemb = dict.fromkeys(crit, 0.0)
    wtot = 0.0
    tick_emb = dict.fromkeys(crit, 0)
    wj = {}
    for _ in range(n):
        acc[:] = 0
        sim.step()
        wtot += acc.sum()
        anyc = dict.fromkeys(crit, False)
        touched = set()
        for c_ in d.contact[: d.ncon]:
            touched.add(int(c_.geom1)); touched.add(int(c_.geom2))
        for pr in pairs:
            sd, cin, vf = measure(pr)
            e = dict(sd=sd < -0.02, cin=cin, v50=vf >= 0.5, v10=vf >= 0.1)
            e["free"] = pr["gc"] not in touched
            e["freeout"] = e["free"] and vf < 0.1
            w = acc[act_of[pr["pi"]]].sum() if pr["pi"] in act_of else 0.0
            wj[pr["jt"]] = wj.get(pr["jt"], 0.0) + w
            for c in crit:
                if e[c]:
                    wemb[c] += w
                    anyc[c] = True
        for c in crit:
            tick_emb[c] += anyc[c]
    S.mujoco = mujoco
    np_ = max(len(pairs), 1)
    out = dict(
        flags=flags, npairs=len(pairs), hidden=hidden,
        start_sd=sum(s[0] < -0.02 for s in start) / np_, start_cin=sum(s[1] for s in start) / np_,
        start_v50=sum(s[2] >= 0.5 for s in start) / np_, start_v10=sum(s[2] >= 0.1 for s in start) / np_,
        start_vmean=float(np.mean([s[2] for s in start])) if start else 0.0,
        pair_jt=[pr["jt"] for pr in pairs], pair_motor=[pr["motor"] for pr in pairs],
        pair_sd=[s[0] for s in start], pair_vf=[s[2] for s in start], pair_driven=[pr["pi"] in act_of for pr in pairs],
        wtot=wtot, **{f"w_{c}": wemb[c] / wtot if wtot > 0 else 0.0 for c in crit},
        **{f"t_{c}": tick_emb[c] / n for c in crit}, wj={k: v / wtot if wtot > 0 else 0 for k, v in wj.items()},
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    tasks, keys = [], []
    for dd in a.dirs:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = generation_sim(cfg, TERRAIN)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        rng = np.random.default_rng(121)
        kind = HOLISTIC  # same picks as probe_ghost.py: holistic is drawn first in each directory
        groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
        for L in "UDC":
            p = os.path.join(dd, L, kind, "final")
            groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        for gname, ms in groups.items():
            for i in rng.choice(len(ms), a.per_group, replace=False):
                tasks.append((ms[i].to_dict(), sc))
                keys.append(gname)
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    print(f"# phys_ghost.py, {a.per_group} holistic members per group per directory over {len(a.dirs)} dirs; draw ({TERRAIN}, {START})")
    fl = {str(r["flags"]) for r in res}
    print("# collision flags seen:", "; ".join(fl))
    print("# PAIRS at season start (after settle): share with sd<-2cm (audit's) | child centre inside parent | >=50% child volume inside | >=10% inside | mean volume fraction")
    print("# WORK share on joints whose child is embedded at the tick, by criterion (exact per-actuator work), pooled = sum over members of embedded work / sum of work; mean = mean of per-member shares (audit reports the mean)")
    print("# TICKS share with any pair embedded, by criterion")
    for gname in dict.fromkeys(keys):
        R = [r for r, k in zip(res, keys) if k == gname]
        W = sum(r["wtot"] for r in R)
        line = f"{gname:9s} n={len(R):2d} pairs " + " ".join(f"{np.mean([r[k] for r in R]):.2f}" for k in ["start_sd", "start_cin", "start_v50", "start_v10", "start_vmean"])
        line += " | work mean " + " ".join(f"{c}={np.mean([r['w_' + c] for r in R]):.2f}" for c in ["sd", "cin", "v50", "v10", "free", "freeout"])
        line += " pooled " + " ".join(f"{c}={sum(r['w_' + c] * r['wtot'] for r in R) / W:.2f}" for c in ["sd", "cin", "v50", "v10", "free", "freeout"])
        line += " | ticks " + " ".join(f"{c}={np.mean([r['t_' + c] for r in R]):.2f}" for c in ["sd", "cin", "v50"])
        print(line)
        print(f"    overlapping (>5 mm) non-parent same-robot geom pairs with NO contact at start (filtered beyond parent-child): {sum(r['hidden'] for r in R)}")
        jt, sd, vf, dr = sum((r["pair_jt"] for r in R), []), sum((r["pair_sd"] for r in R), []), sum((r["pair_vf"] for r in R), []), sum((r["pair_driven"] for r in R), [])
        mo = sum((r["pair_motor"] for r in R), [])
        for t in sorted(set(jt)):
            sel = [i for i, x in enumerate(jt) if x == t]
            print(f"    {t:7s} pairs {len(sel):3d}  driven {sum(dr[i] for i in sel):3d}  sd<-2cm {sum(sd[i] < -0.02 for i in sel):3d}  centre-in/v50 {sum(vf[i] >= 0.5 for i in sel):3d}  v10 {sum(vf[i] >= 0.1 for i in sel):3d}  "
                  f"motors {dict((mm, sum(mo[i] == mm for i in sel)) for mm in sorted(set(mo[i] for i in sel)))}  work share {np.mean([r['wj'].get(t, 0) for r in R]):.2f}")
    # per-member detail for the D line
    print("# holistic D per member: wtot(J) w_sd w_cin w_v50 | start_sd start_v50")
    for r, k in zip(res, keys):
        if k == "D":
            print(f"    {r['wtot']:9.0f} {r['w_sd']:.2f} {r['w_cin']:.2f} {r['w_v50']:.2f} | {r['start_sd']:.2f} {r['start_v50']:.2f}")


if __name__ == "__main__":
    main()
