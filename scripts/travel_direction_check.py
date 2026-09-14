# Independent of scripts/travel_direction.py (RBT-45 branch): written without reference to it,
# because this thread is about instruments agreeing for the wrong reason.
"""Independent check of the coordinator's resolution: which way does each population drive?

Travel azimuth minus chassis yaw, circular-averaged over baseline bouts. Written without
reference to scripts/travel_direction.py, which is on an unmerged branch.
"""
import json, math, sys, numpy as np
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

def yaw(q):
    w, x, y, z = q
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))

def offsets(run, gens, cfgpath=None, n=16):
    cfg = SimConfig.from_dict(json.load(open(cfgpath or f"{run}/config.json"))["sim"])
    out = {}
    for gen in gens:
        vecs = []
        for s in range(n):
            g = Genotype.load(f"{run}/conventional/best_gen{gen:04d}.json")
            sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, 7000 + s)); sim.set_food_seed(7000 + s)
            prev = sim.center_of_mass(0)[:2].copy()
            for t in range(int(round(cfg.duration / cfg.control_dt))):
                sim.step()
                if t % 10 == 0:
                    p = sim.center_of_mass(0)[:2]; d = p - prev
                    if np.linalg.norm(d) > 1e-3:   # only while actually moving
                        off = math.atan2(d[1], d[0]) - yaw(sim.data.xquat[sim.robots[0].root_body])
                        vecs.append(np.array([math.cos(off), math.sin(off)]))
                    prev = p.copy()
        m = np.mean(vecs, axis=0)
        out[gen] = (math.degrees(math.atan2(m[1], m[0])), float(np.linalg.norm(m)))
    return out

run, gens = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
cfgpath = sys.argv[3] if len(sys.argv) > 3 else None
res = offsets(run, gens, cfgpath)
print(f"{run}")
for g, (deg, R) in res.items():
    print(f"  gen {g:4d}: offset {deg:+8.1f} deg   R={R:.3f}   {'FORWARD' if abs(deg) < 90 else 'BACKWARD'}")
allv = np.mean([[math.cos(math.radians(d)), math.sin(math.radians(d))] for d, _ in res.values()], axis=0)
print(f"  pooled : {math.degrees(math.atan2(allv[1], allv[0])):+8.1f} deg   R={np.linalg.norm(allv):.3f}")
