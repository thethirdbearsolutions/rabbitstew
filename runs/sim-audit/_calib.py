"""Throwaway: work out the Pioneer's drive convention, speed, and geometry."""
import json, time
from dataclasses import replace
import numpy as np
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "/home/user/rabbitstew/runs/RBT-23/W4b-801"
cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
g = Genotype.load(f"{RUN}/conventional/best_gen0590.json")
ph = synthesize(g, cfg.synthesis)
print("parts:", [(p.index, p.parent, str(p.shape), tuple(round(d,4) for d in p.dims), round(p.mass,4)) for p in ph.parts])
print("units:", [(i, u.part, u.unit.kind, getattr(u.unit,'source',None), getattr(u.unit,'axis',None)) for i,u in enumerate(ph.units)])

# flat world, no obstacles, to calibrate motion cleanly
flat = replace(cfg, world=replace(cfg.world, terrain="flat", random_obstacles=0), random_start=False)

def drive(e1, e2, steps=200, c=flat):
    sim = Simulation([g], c, spawns=spawn_layout(1, c, None))
    idx = sim.robots[0]
    gid = idx.geoms[0]
    a1, a2 = idx.actuators[(1,0)], idx.actuators[(2,0)]
    p0 = sim.data.geom_xpos[gid].copy(); R0 = sim.data.geom_xmat[gid].reshape(3,3).copy()
    for _ in range(steps):
        sim.data.ctrl[:] = 0.0
        sim.data.ctrl[a1] = e1; sim.data.ctrl[a2] = e2
        for _ in range(c.control_substeps):
            import mujoco; mujoco.mj_step(sim.model, sim.data)
    p1 = sim.data.geom_xpos[gid].copy(); R1 = sim.data.geom_xmat[gid].reshape(3,3).copy()
    disp = p1 - p0
    local = R0.T @ disp
    # yaw change
    yaw0 = np.arctan2(R0[1,0], R0[0,0]); yaw1 = np.arctan2(R1[1,0], R1[0,0])
    dyaw = np.arctan2(np.sin(yaw1-yaw0), np.cos(yaw1-yaw0))
    t = steps*c.control_dt
    return dict(disp=disp[:2], local=local, speed=np.linalg.norm(disp[:2])/t, dyaw=dyaw, rate=dyaw/t)

for e1, e2, tag in ((1,-1,"e1=+1 e2=-1"), (-1,1,"e1=-1 e2=+1"), (1,1,"e1=+1 e2=+1"), (-1,-1,"e1=-1 e2=-1"), (0.6,-0.6,"e=+-0.6")):
    r = drive(e1,e2)
    print(f"{tag:14s} local disp {np.round(r['local'],3)}  speed {r['speed']:.3f} m/s  dyaw {np.degrees(r['dyaw']):8.1f} deg  rate {np.degrees(r['rate']):7.1f} deg/s")

# geometry: wheel positions in chassis local frame
sim = Simulation([g], flat, spawns=spawn_layout(1, flat, None))
idx = sim.robots[0]; gid = idx.geoms[0]
R = sim.data.geom_xmat[gid].reshape(3,3); p = sim.data.geom_xpos[gid]
for k in range(len(idx.geoms)):
    print("part", k, "local pos", np.round(R.T @ (sim.data.geom_xpos[idx.geoms[k]] - p), 4), "rbound", round(float(sim.model.geom_rbound[idx.geoms[k]]),4))
