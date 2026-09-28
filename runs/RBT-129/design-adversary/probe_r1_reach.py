"""R1 check probe: is prints.txt's "reach-limited share 0 by geometry" under root + surface credible?

prints.py argues per obstacle: a footprint is at most 0.7 m across, so no item lies deeper than 0.35 m (the surface eat
radius) inside one.  But obstacles overlap, and an item inside the UNION of tall footprints can be farther than 0.35 m
from free ground.  Here, on prints.py's own arenas (terrain and start seeds 0..99), an item inside a footprint taller
than 0.1 m counts as out of reach when no point within 0.35 m of it (16 directions x 7 radii) lies outside every tall
footprint, i.e. a root touching free ground cannot come within 0.35 m (it also assumes the root's surface reaches the
ground, which bounds the share from below).  python3 probe_r1_reach.py <tree> [draws]
"""
import os
import sys
from dataclasses import replace

import numpy as np

T = sys.argv[1]
DRAWS = int(sys.argv[2]) if len(sys.argv) > 2 else 100
sys.path[:0] = [T, os.path.join(T, "runs/RBT-129/launch")]
import blocks  # noqa: E402
import prints  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402
from rabbitstew.world import scenery  # noqa: E402

ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
rad = np.linspace(0.05, 0.35, 7)
ring = np.array([(r * np.cos(a), r * np.sin(a)) for r in rad for a in ang])
print(f"# probe_r1_reach: {DRAWS} arenas a row; union-of-tall-footprints depth > 0.35 m")
print("# layout c   tall(any)  deeper than 0.35 m from free ground (union)   items  fallbacks")
for L in blocks.LAYOUTS:
    for c in (1.0, 2.0):
        pid = blocks.point_id(c, 0.03, L, "G")
        base = prints.sim_config(pid)
        fx = [prints.drive_straight_genotype(0.6)] * 4
        tall = deep = tot = fb = 0
        for k in range(DRAWS):
            cfg = replace(base, random_start=True, world=replace(base.world, terrain_seed=k))
            sim = Simulation(fx, cfg, spawns=spawn_layout(4, cfg, k))
            sim.set_food_seed(k)
            fb += int(getattr(sim, "food_fallbacks", 0))
            items = np.asarray(sim.food_spots, dtype=float).reshape(-1, 2)
            obs = scenery(sim.config.world)
            inside = prints.footprint_mask(items, obs, tall=prints.TALL)
            tall += inside.sum()
            tot += len(items)
            for p in items[inside]:
                pts = p[None, :] + ring
                if prints.footprint_mask(pts, obs, tall=prints.TALL).all():
                    deep += 1
        print(f"  {L:5s} {c:3.1f}  {tall / tot:.3f}      {deep / tot:.4f} ({deep} of {tot})                          {tot}   {fb}", flush=True)
