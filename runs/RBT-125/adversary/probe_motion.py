"""RBT-125 adversary probe: does the common temporal term really cancel in L - R (DESIGN §1 parity table)?

The Pioneer's three food noses share one baseline b (the EMA of their mean ln S).  Moving along the gradient, every
nose lags b by the same amount c ~ tau * d(ln S)/dt, so each wheel reads tanh(G (+-dx/2 + c + e)) with e the
chassis's fore-aft offset.  L - R = tanh(G(dx/2 + c')) - tanh(G(-dx/2 + c')) = 2 tanh(G dx/2) only at c' = 0; for
c' != 0 the steering signal is multiplied by about sech^2(G c').  DESIGN says "the common temporal term cancels in
L - R".  This measures it.

Method (kinematic, the real code path): a committed Pioneer (RBT-19 P-801 g590, three food noses) is carried at a
constant speed v on a straight line, heading at angle theta to the direction of a single food item, through
`Simulation._food_contrast` once per control tick (0.02 s) for 4 s (2 tau), from 2.5 m out.  Printed: the wheel
readings' L - R at the end, against the static reading of the same pose (v = 0: fresh baseline held at that pose
for 10 s), and the ratio.

    python runs/RBT-125/adversary/probe_motion.py
"""
import json
import os
import sys

from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation  # noqa: E402
from rabbitstew.world import Spawn  # noqa: E402

BODY = os.path.join(ROOT, "runs/RBT-19/P-801/conventional/best_gen0590.json")


def pose(sim, xy, yaw):
    adr = sim.robots[0].root_qpos_adr
    sim.data.qpos[adr:adr + 2] = xy
    sim.data.qpos[adr + 3:adr + 7] = (np.cos(yaw / 2), 0.0, 0.0, np.sin(yaw / 2))
    sim.data.qvel[:] = 0.0
    mujoco.mj_forward(sim.model, sim.data)


def wheel_lr(sim, reading):
    b = sim.brains[0]
    ks = [k for k, s in enumerate(b.sensors) if s.source == "food"]
    parts = {k: b.sensors[k].part for k in ks}
    wheels = sorted([k for k in ks if parts[k] in (1, 2)], key=lambda k: parts[k])
    return reading[wheels[0]] - reading[wheels[1]], {parts[k]: reading[k] for k in ks}


def run(G, v, theta, T=4.0):
    cfg = SimConfig.from_dict(json.load(open(os.path.join(ROOT, "runs/RBT-125/gate/worlds/PW-G2.5/config.json")))["sim"])
    cfg = replace(cfg, settle_time=0.0, food=replace(cfg.food, smell_contrast=G, items=1, patches=0))
    sim = Simulation([Genotype.load(BODY)], cfg, spawns=[Spawn(position=(0.0, 0.0, 0.3), yaw=0.0)])
    sim.food_pos = np.array([[0.0, 0.0]])
    # heading makes angle theta with the direction to the item; the body ends at 1.2 m from it
    n = int(round(T / cfg.control_dt))
    end = np.array([1.2, 0.0])
    to_item = -end / np.linalg.norm(end)
    yaw_to = np.arctan2(to_item[1], to_item[0])
    yaw = yaw_to + theta
    dirn = np.array([np.cos(yaw), np.sin(yaw)])
    start = end - dirn * v * T
    for i in range(n + 1):
        pose(sim, start + dirn * v * cfg.control_dt * i, yaw)
        r = sim._food_contrast(0)
    return wheel_lr(sim, r)


def main():
    print("# L - R of the Pioneer's wheel noses, moving (v m/s, 4 s) against static at the same end pose; 1 item, decay 1.5")
    print("| G | v | theta (deg from the item) | L - R moving | L - R static | ratio | chassis, L, R readings moving |")
    print("|---|---|---|---|---|---|---|")
    for G in (2.5, 10.0):
        for v in (0.25, 0.5):
            for th in (45, 90, 135):
                mv, parts = run(G, v, np.radians(th))
                st, _ = run(G, 0.0, np.radians(th), T=10.0)
                print(f"| {G:g} | {v:g} | {th} | {mv:+.3f} | {st:+.3f} | {mv / st if abs(st) > 1e-9 else float('nan'):.2f} | "
                      + ", ".join(f"{parts[p]:+.2f}" for p in sorted(parts)) + " |")


if __name__ == "__main__":
    main()
