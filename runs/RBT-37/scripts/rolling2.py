import json, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
cfg = SimConfig.from_dict(json.load(open("runs/RBT-12/cap-403/config.json"))["sim"])
cfg = replace(cfg, opponent_proxy=True)
g = Genotype.load("runs/RBT-12/cap-403/holistic/best_gen0199.json")
ph = synthesize(g, cfg.synthesis)
p1 = ph.parts[1]
print(f"sphere: radius {p1.dims[0]:.3f} m, geom_offset from ball anchor {p1.geom_offset:.3f} m, attach_pos in box frame {np.round(p1.attach_pos,3)}, mass {p1.mass:.2f}; box half-extents? dims {np.round(ph.parts[0].dims,3)} mass {ph.parts[0].mass:.2f}")
r = p1.dims[0]
def up_z(q): w,x,y,z = q; return 1 - 2*(x*x + y*y)
out = []
for terrain in ("flat", "random"):
    c = replace(cfg, world=replace(cfg.world, terrain=terrain))
    for seed in (6000, 6001):
        spawn = spawn_layout(2, c, seed)[0]
        sim = Simulation([g], c, spawns=[spawn]); sim.start_recording(every=5); sim.run()
        A = sim.trajectory.as_array(); box, sph = A[:, 0, :], A[:, 1, :]
        bpath = float(np.linalg.norm(np.diff(box[:, :2], axis=0), axis=1).sum()); bdisp = float(np.linalg.norm(box[-1, :2] - box[0, :2]))
        boxup = np.array([up_z(q) for q in box[:, 3:7]])
        # sphere centre relative to box centre: how far it orbits
        relv = sph[:, :3] - box[:, :3]; orbit = float(np.linalg.norm(np.diff(relv, axis=0), axis=1).sum())
        row = {"terrain": terrain, "seed": seed, "tat": round(float(sim.time_at_target(0)), 2), "progress": round(float(sim.progress(0)), 2),
               "box_path_m": round(bpath, 2), "box_displacement_m": round(bdisp, 2), "box_speed_m_s": round(bpath / 15, 2),
               "sphere_orbit_about_box_m": round(orbit, 1),
               "sphere_height_min_mean_max": [round(float(sph[:, 2].min()), 3), round(float(sph[:, 2].mean()), 3), round(float(sph[:, 2].max()), 3)],
               "sphere_touching_ground_fraction(z<r+0.01)": round(float((sph[:, 2] < r + 0.01).mean()), 2),
               "box_height_min_mean": [round(float(box[:, 2].min()), 3), round(float(box[:, 2].mean()), 3)],
               "box_up_z_mean": round(float(boxup.mean()), 2), "exploded": bool(sim.exploded[0])}
        print(row); out.append(row)
json.dump({"radius": r, "geom_offset": p1.geom_offset, "rows": out}, open("runs/RBT-37/rolling2.json", "w"), indent=1)
