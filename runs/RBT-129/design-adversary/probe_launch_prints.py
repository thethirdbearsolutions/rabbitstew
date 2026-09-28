"""Launch-adversary probe L4: how much of prints.py's "unreachable" share is out of reach under the eating rule?

prints.py counts an item unreachable when it lies inside an obstacle's ground footprint.  But the eating rule is
xy-only (`eat_rule centre`: an item within eat_radius 0.35 m, in xy, of an eating geom's centre), and under the
candidate `eat_from root` the root's centre can stand at the obstacle's edge.  So an item inside a footprint but
within about 0.35 - 0.15 = 0.20 m of its edge (0.15 m: half a 0.3 m root) can be eaten from beside it, and a bump
<= 0.1 m can be driven over.  Printed here for the same arenas (prints.py's own draws, terrain and start seeds 0..99):
  any       prints.py's share (inside any footprint)
  tall      prints.py's second column (inside a footprint taller than 0.1 m)
  deep      inside a footprint taller than 0.1 m AND deeper than 0.20 m from its edge (the edge-reach bound)
Also the mechanical income shift a common food tax makes in x = H - D: f_deep x (food_D - food_H), with RBT-118's
restored foods (random terrain, season 599: designed 1.49, holistic 1.25; RBT-118 prior section 4a).

python3 probe_launch_prints.py <PR-435 worktree> [draws]
"""
import os
import sys
from dataclasses import replace

import numpy as np

WT = sys.argv[1]
DRAWS = int(sys.argv[2]) if len(sys.argv) > 2 else 100
sys.path[:0] = [WT, os.path.join(WT, "runs/RBT-129/launch")]
import blocks  # noqa: E402
import prints  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402
from rabbitstew.world import Shape as WShape, scenery  # noqa: E402

REACH = 0.20


def depth(items, sc):
    x, y = items[:, 0] - sc.pos[0], items[:, 1] - sc.pos[1]
    if sc.shape == WShape.BOX:
        w, h, (qw, qx, qy, qz) = sc.dims[0], sc.dims[1], sc.quat
        yaw = np.arctan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
        u = np.cos(yaw) * x + np.sin(yaw) * y
        v = -np.sin(yaw) * x + np.cos(yaw) * y
        return np.minimum(w / 2 - np.abs(u), h / 2 - np.abs(v)), sc.dims[2]
    if sc.shape == WShape.CYLINDER:
        return sc.dims[0] - np.hypot(x, y), sc.dims[1]
    r, zc = sc.dims[0], sc.pos[2]
    rf = np.sqrt(max(r * r - zc * zc, 0.0))
    return rf - np.hypot(x, y), zc + r


print(f"# probe_launch_prints: {DRAWS} arenas per row; REACH {REACH} m; eat radius 0.35 xy, root centre at the edge")
print("# layout c   any    tall   deep   | shift in H - D from a common tax at f_deep (and at f_any), items a season")
for L in blocks.LAYOUTS:
    for c in (1.0, 2.0):
        pid = blocks.point_id(c, 0.03, L, "L")
        base = prints.sim_config(pid)
        fx = [prints.drive_straight_genotype(0.6)] * 4
        n_any = n_tall = n_deep = tot = 0
        for k in range(DRAWS):
            cfg = replace(base, random_start=True, world=replace(base.world, terrain_seed=k))
            sim = Simulation(fx, cfg, spawns=spawn_layout(4, cfg, k))
            sim.set_food_seed(k)
            items = np.asarray(sim.food_spots, dtype=float).reshape(-1, 2)
            obs = scenery(sim.config.world)
            best = np.full(len(items), -np.inf)
            anyin = np.zeros(len(items), bool)
            for sc in obs:
                d, hgt = depth(items, sc)
                anyin |= d >= 0
                if hgt > prints.TALL:
                    best = np.maximum(best, d)
            n_any += anyin.sum(); n_tall += (best >= 0).sum(); n_deep += (best > REACH).sum(); tot += len(items)
        fa, ft, fd = n_any / tot, n_tall / tot, n_deep / tot
        print(f"  {L:5s} {c:3.1f} {fa:.3f}  {ft:.3f}  {fd:.3f}  | {fd * (1.49 - 1.25):+.3f} ({fa * (1.49 - 1.25):+.3f})", flush=True)
