"""Throwaway 2: how well can this body actually turn?"""
import json
from dataclasses import replace
import numpy as np, mujoco
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

RUN = "/home/user/rabbitstew/runs/RBT-23/W4b-801"
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
g = Genotype.load(f"{RUN}/conventional/best_gen0590.json")
flat = replace(cfg, world=replace(cfg.world, terrain="flat", random_obstacles=0), random_start=False)
real = replace(cfg, random_start=True)

def drive(e1, e2, steps, c, seed=None):
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    if c.food is not None: sim.set_food_seed(seed if seed is not None else 0)
    idx = sim.robots[0]; gid = idx.geoms[0]
    a1, a2 = idx.actuators[(1,0)], idx.actuators[(2,0)]
    yaws, pos = [], []
    for _ in range(steps):
        sim.data.ctrl[:] = 0.0
        sim.data.ctrl[a1] = e1; sim.data.ctrl[a2] = e2
        for _ in range(c.control_substeps): mujoco.mj_step(sim.model, sim.data)
        R = sim.data.geom_xmat[gid].reshape(3,3)
        yaws.append(np.arctan2(R[1,0], R[0,0])); pos.append(sim.data.geom_xpos[gid][:2].copy())
    yaws = np.unwrap(np.array(yaws)); pos = np.array(pos)
    t = steps*c.control_dt
    path = float(np.abs(np.diff(pos,axis=0)).sum()) if False else float(np.linalg.norm(np.diff(pos,axis=0),axis=1).sum())
    return np.degrees(yaws[-1]-yaws[0])/t, path/t, yaws

print("FLAT, no obstacles, 4 s each")
print(f"{'e1':>6s} {'e2':>6s} {'yawrate deg/s':>14s} {'speed m/s':>10s}")
for e1, e2 in ((1,-1),(1,-0.5),(1,0.0),(1,0.5),(1,1),(0.6,0.2),(0.5,-0.5),(1,-0.2)):
    r, s, _ = drive(e1,e2,200,flat)
    print(f"{e1:6.2f} {e2:6.2f} {r:14.1f} {s:10.3f}")

# spin-up profile
_,_,y = drive(1,1,300,flat)
y = np.degrees(y - y[0])
print("\nspin (e1=e2=1) yaw deg at t=", [f"{i*0.02:.1f}s:{y[i-1]:.0f}" for i in (25,50,100,150,200,250,300)])

print("\nREAL world (random terrain + 14 obstacles), 4 s, seed 9000")
for e1, e2 in ((1,-1),(1,1),(1,0.0)):
    r, s, _ = drive(e1,e2,200,real,9000)
    print(f"{e1:6.2f} {e2:6.2f} {r:14.1f} {s:10.3f}")
