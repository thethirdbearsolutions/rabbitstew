"""RBT-125 adversary: can a body game the running baseline with a nose on a fast-moving Part?

A 0.3 m root cube with one box arm on an unlimited hinge at full throttle (side_effects.py's rod, arm 0.45 m and
1.5 m), a food nose on the ARM's tip Part, in U-G2.5 and PW-G2.5 (committed gate worlds, flat terrain for clarity),
against the same rod with the nose on the ROOT.  Printed: the distribution of the nose's reading over a 15 s season
(median |c|, p90 |c|, the share of ticks with |c| > 0.9) and its correlation with the TRUE bearing-free food signal
d(ln S)/dt at the nose (the part of the reading that is information), 5 seeds each.
A spinning nose reads a large, food-shaped carrier: that is klinotaxis's input, not a free lunch -- unless it is large
with food absent.  The last column is the same season with the food removed (all items parked): the reading must be 0.
"""
import json, os, sys
from dataclasses import replace
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Sensor, Shape
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout


def rod(a, nose_on_arm):
    arm = Segment(Shape.BOX, (float(a), 1.0, 1.0), Brain(units=[Effector(dof=0, bias=3.0)] + ([Sensor("food")] if nose_on_arm else [])))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    root = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[] if nose_on_arm else [Sensor("food")]))
    return Genotype(nodes=[Node(root, [conn]), Node(arm)], name="rod")


def season(cfg, g, seed, empty=False):
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    if empty:
        sim.food_pos[:] = 1e6
    k = [i for i, s in enumerate(sim.brains[0].sensors) if s.source == "food"][0]
    part = sim.brains[0].sensors[k].part
    c, dx, last = [], [], None
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        v = sim.brains[0].sensors  # noqa
        x = sim._log_smell(sim.data.geom_xpos[sim.robots[0].geoms[part]], sim.food_pos)
        c.append(float(np.tanh(cfg.food.smell_contrast * (x - sim._smell_base[0]))))
        dx.append(0.0 if last is None else (x - last) / cfg.control_dt)
        last = x
    return np.array(c), np.array(dx)


print("| world | arm (m) | nose on | median abs c | p90 abs c | share abs c > 0.9 | corr(c, d ln S/dt) | food removed: max abs c |")
print("|---|---|---|---|---|---|---|---|")
for cell in ("U-G2.5", "PW-G2.5"):
    cfg = SimConfig.from_dict(json.load(open(os.path.join(ROOT, "runs/RBT-125/gate/worlds", cell, "config.json")))["sim"])
    cfg = replace(cfg, world=replace(cfg.world, terrain="flat"))
    for L in (0.45, 1.5):
        a = (L / 0.3) ** 1.5
        for on_arm in (True, False):
            C, D, E = [], [], []
            for seed in range(5):
                c, d = season(cfg, rod(a, on_arm), 2131 + seed)
                C.append(c); D.append(d)
                E.append(np.abs(season(cfg, rod(a, on_arm), 2131 + seed, empty=True)[0]).max())
            c, d = np.concatenate(C), np.concatenate(D)
            print(f"| {cell} | {L} | {'arm' if on_arm else 'root'} | {np.median(abs(c)):.2f} | {np.quantile(abs(c), 0.9):.2f} | "
                  f"{np.mean(abs(c) > 0.9):.2f} | {np.corrcoef(c, d)[0, 1]:+.2f} | {max(E):.3f} |", flush=True)
