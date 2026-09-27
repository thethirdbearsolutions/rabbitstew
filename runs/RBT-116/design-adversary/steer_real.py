"""RBT-116 design adversary: the registered STEERS call (PREREGISTRATION §1.2-1.3, stage 2 only) on REAL bodies.

    steer_real.py [--per-dir K] [--world pw|committed] [--workers W] SEED_DIR [SEED_DIR ...] > steer_real_<world>.txt

For K members (fixed rng) of each seed directory's RBT-113 U finals, both faunas: 16 paired solo seasons, intact
against RBT-97's RotatedSmell decoy (the LIVE layout rotated about the origin by theta ~ U[30, 330] deg, one theta
per draw from a fixed stream), on RBT-113's arm config for generation 0, with --random-start.
  --world committed : RBT-113's own world (3 m disc, uniform, instant regrowth, sum, decay 1).
  --world pw        : PW's layout WITHOUT the two unbuilt flags (smell_gain, eat_from): 2 patches of 0.4 m in a
                      4 m disc, regrow 60 s, log, decay 1.5.  So this is "PW at gain 1, committed eating".
T = sum |v| cos(v, g) / sum |v| over control ticks with |v| > 0.05 m/s, v the whole-robot centre-of-mass velocity
(subtree_com of the root), g the analytic gradient of the REAL live field.  Call: STEERS / SMELL-USE / NONE as
registered (F >= 0.25 with t lower bound > 0; dT lower bound > 0; <= 8 of 16 draws with food_i == food_d).
Read-only on rabbitstew/: the decoy is a per-instance method patch, as in RBT-97 and RBT-113's probe_food.py.
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

_orig = S.Simulation._intensity
T95_15 = 1.753
NDRAW = 16


def pw(cfg):
    f = replace(cfg.food, patches=2, patch_radius=0.4, radius=4.0, regrow_delay=60.0, smell="log", decay=1.5)
    return replace(cfg, food=f)


def grad_dir(pt, food, decay):
    diff = food - pt
    d = np.linalg.norm(diff, axis=1) + 1e-12
    w = np.exp(-d / decay) / decay
    g = (w[:, None] * diff / d[:, None]).sum(0)
    n = np.linalg.norm(g)
    return g / n if n > 1e-15 else np.zeros(2)


def season(gd, sim_cfg, start, theta):
    g = Genotype.from_dict(gd)
    cfg = replace(sim_cfg, random_start=True)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, start))
    sim.set_food_seed(start)
    if theta is not None:
        c, s = float(np.cos(theta)), float(np.sin(theta))
        Rm = np.array([[c, s], [-s, c]])

        def fake(self, pos, pts, _s=sim):
            if pts is _s.food_pos:
                return _orig(self, pos, pts @ Rm)
            return _orig(self, pos, pts)
        sim._intensity = fake.__get__(sim)
    n = int(round(cfg.duration / cfg.control_dt))
    root = sim.robots[0].root_body
    prev = np.array(sim.data.subtree_com[root][:2])
    num = den = 0.0
    slow = 0
    for _ in range(n):
        sim.step()
        com = np.array(sim.data.subtree_com[root][:2])
        v = (com - prev) / cfg.control_dt
        sp = float(np.linalg.norm(v))
        if sp > 0.05:
            live = sim.food_pos[np.abs(sim.food_pos[:, 0]) < 1e5]
            if len(live):
                gdir = grad_dir(prev, live, cfg.food.decay)
                num += float(np.dot(v, gdir)); den += sp
        else:
            slow += 1
        prev = com
    food = 0.0 if sim.exploded[0] else float(sim.food_eaten[0])
    return food, (num / den if den > 0 else 0.0), slow / n


def job(args):
    gd, sim_cfg, starts, thetas = args
    I = [season(gd, sim_cfg, s, None) for s in starts]
    D = [season(gd, sim_cfg, s, th) for s, th in zip(starts, thetas)]
    g = Genotype.from_dict(gd)
    return I, D


def lb(x):
    s = x.std(ddof=1)
    return x.mean() - T95_15 * s / np.sqrt(len(x)) if s > 0 else x.mean()


def call(I, D):
    fi, fd = np.array([x[0] for x in I]), np.array([x[0] for x in D])
    ti, td = np.array([x[1] for x in I]), np.array([x[1] for x in D])
    dF, dT = fi - fd, ti - td
    c1 = dF.mean() >= 0.25 and lb(dF) > 0
    c3 = int((dF == 0).sum()) <= NDRAW // 2
    lab = "STEERS" if c1 and c3 and lb(dT) > 0 else "SMELL-USE" if c1 and c3 else "NONE"
    return lab, dF.mean(), lb(dF), dT.mean(), lb(dT), int((dF == 0).sum()), fi.mean(), ti.mean(), td.mean(), np.mean([x[2] for x in I])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-dir", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--world", choices=["pw", "committed"], default="pw")
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    rng = np.random.default_rng(116121)
    trng = np.random.default_rng(116330)
    starts = [116_000 + k for k in range(NDRAW)]
    thetas = [float(np.radians(trng.uniform(30, 330))) for _ in range(NDRAW)]
    tasks, keys = [], []
    for d in a.seed_dirs:
        op, seed = decompose.parse_seed_dir(d)
        cfg = world.evolution_config("U", op, seed=seed)
        sim_cfg = generation_sim(cfg, 0)
        if a.world == "pw":
            sim_cfg = pw(sim_cfg)
        for kind in (HOLISTIC, CONVENTIONAL):
            fs = sorted(os.listdir(os.path.join(d, "U", kind, "final")))
            ms = [Genotype.load(os.path.join(d, "U", kind, "final", f)) for f in fs]
            for i in rng.choice(len(ms), a.per_dir, replace=False):
                nf = sum(1 for n_ in ms[i].to_dict().get("nodes", []) for s_ in n_.get("sensors", []) if "food" in str(s_))
                tasks.append((ms[i].to_dict(), sim_cfg, starts, thetas))
                keys.append((os.path.basename(d.rstrip("/")), kind, fs[i]))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    print(f"# steer_real.py --world {a.world}: {len(res)} RBT-113 U finals x {NDRAW} paired draws (intact vs rotated decoy)")
    print("# seed kind member | call | F  lbF | dT  lbdT | zero-draws | food_i  T_i  T_d | share of ticks |v|<=0.05")
    for k, (I, D) in zip(keys, res):
        c = call(I, D)
        print(f"{k[0]:>3s} {k[1]:12s} {k[2]:>12s} | {c[0]:9s} | {c[1]:+.3f} {c[2]:+.3f} | {c[3]:+.3f} {c[4]:+.3f} | {c[5]:2d} | {c[6]:.2f} {c[7]:+.3f} {c[8]:+.3f} | {c[9]:.2f}", flush=True)
    for kind in (HOLISTIC, CONVENTIONAL):
        cs = [call(I, D) for k, (I, D) in zip(keys, res) if k[1] == kind]
        print(f"## {kind}: n {len(cs)}  STEERS {sum(c[0] == 'STEERS' for c in cs)}  SMELL-USE {sum(c[0] == 'SMELL-USE' for c in cs)}  "
              f"mean F {np.mean([c[1] for c in cs]):+.3f}  mean dT {np.mean([c[3] for c in cs]):+.3f}  mean T_intact {np.mean([c[7] for c in cs]):+.3f}  "
              f"mean zero-draws {np.mean([c[5] for c in cs]):.1f}  mean slow-tick share {np.mean([c[9] for c in cs]):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
