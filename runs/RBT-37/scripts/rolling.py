"""Does cap-403's h199-15 roll?  Sphere rotation x radius against sphere-centre path length, box up-vector."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
cfg = SimConfig.from_dict(json.load(open("runs/RBT-12/cap-403/config.json"))["sim"])
cfg = replace(cfg, opponent_proxy=True)
g = Genotype.load("runs/RBT-12/cap-403/holistic/best_gen0199.json")
ph = synthesize(g, cfg.synthesis)
for i, p in enumerate(ph.parts): print(f"part {i}: {p.shape.name} dims {tuple(round(d,3) for d in p.dims)} joint {p.joint_type.name} mass {p.mass:.2f}")
r = ph.parts[1].dims[0]
def qmul(a, b):
    w1,x1,y1,z1 = a; w2,x2,y2,z2 = b
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2, w1*x2+x1*w2+y1*z2-z1*y2, w1*y2-x1*z2+y1*w2+z1*x2, w1*z2+x1*y2-y1*x2+z1*w2])
def qconj(q): return q * np.array([1,-1,-1,-1])
def up_z(q):  # third column of the rotation matrix's z row: world z component of the body's local +z
    w,x,y,z = q; return 1 - 2*(x*x + y*y)
out = []
for seed in (6000, 6001, 6002):
    spawn = spawn_layout(2, cfg, seed)[0]
    sim = Simulation([g], cfg, spawns=[spawn])
    sim.start_recording(every=5)
    sim.run()
    A = sim.trajectory.as_array()  # (frames, units, 7)
    box, sph = A[:, 0, :], A[:, 1, :]
    path = float(np.linalg.norm(np.diff(sph[:, :2], axis=0), axis=1).sum())
    ang = 0.0; angs = []
    for k in range(1, len(sph)):
        dq = qmul(sph[k, 3:7], qconj(sph[k-1, 3:7]))
        a = 2 * np.arccos(np.clip(abs(dq[0]), -1, 1)); ang += a; angs.append(a)
    rel = 0.0
    for k in range(1, len(sph)):
        q1 = qmul(qconj(box[k, 3:7]), sph[k, 3:7]); q0 = qmul(qconj(box[k-1, 3:7]), sph[k-1, 3:7])
        dq = qmul(q1, qconj(q0)); rel += 2 * np.arccos(np.clip(abs(dq[0]), -1, 1))
    boxup = np.array([up_z(q) for q in box[:, 3:7]]); sphz = sph[:, 2]
    row = {"seed": seed, "tat": round(float(sim.time_at_target(0)), 2), "progress": round(float(sim.progress(0)), 2),
           "sphere_path_m": round(path, 2), "sphere_rotation_x_radius_m": round(float(ang * r), 2), "rolling_ratio": round(float(ang * r / max(path, 1e-6)), 2),
           "sphere_turns": round(float(ang / (2*np.pi)), 1), "sphere_vs_box_turns": round(float(rel / (2*np.pi)), 1),
           "box_up_z_mean": round(float(boxup.mean()), 2), "box_up_z_min": round(float(boxup.min()), 2), "box_upright_fraction": round(float((boxup > 0.5).mean()), 2),
           "sphere_height_mean": round(float(sphz.mean()), 3), "sphere_height_std": round(float(sphz.std()), 3), "box_height_mean": round(float(box[:, 2].mean()), 3)}
    print(row); out.append(row)
json.dump({"radius": r, "rows": out}, open("runs/RBT-37/rolling.json", "w"), indent=1)
