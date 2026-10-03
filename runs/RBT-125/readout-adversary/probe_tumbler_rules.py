"""RBT-125 §C adversary: how much of the tumbler's `surface` income is sweep, and how much is the placement leak?

side_effects.py's tumbler (the same rod(), the same RBT-113 generation-1131 world, the same draws 2131..2150, the
cell's food block) under eating-rule x clearance combinations, plus a MOTORS-OFF rod (effector bias 0) that cannot
move, so everything it eats is static reach.  The U-G0 'surface' row ran with the default root clearance, which C1
(runs/RBT-125/adversary/probe_static_reach.txt) showed leaks under `surface`; `clear_from = geoms` under `surface`
is the fixed, surface-distance clearance (c591a75).  Also `root` + `surface`: the root Part's surface is the mouth.

    python probe_tumbler_rules.py GATE_DIR     (GATE_DIR = runs/RBT-125/gate of the tree to use)
"""
import os, sys
from dataclasses import replace
from multiprocessing import get_context
import numpy as np
G = os.path.abspath(sys.argv[1]); sys.path.insert(0, G)
import side_effects as se  # noqa: E402  (the gate's own rod, season and cond_cfg)
from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402

RULES = {"any/centre/root (committed)": {}, "root/centre/root": {"eat_from": "root"},
         "any/surface/root (the side-effects row)": {"eat_rule": "surface"},
         "any/surface/geoms (fixed clearance)": {"eat_rule": "surface", "clear_from": "geoms"},
         "root/surface/root": {"eat_from": "root", "eat_rule": "surface"}}


def rod_off(a):
    arm = Segment(Shape.BOX, (float(a), 1.0, 1.0), Brain(units=[Effector(dof=0, bias=0.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[])), [conn]), Node(arm)], name="rod-off")


def main():
    base = generation_sim(se.rbt113.evolution_config("U", "", seed=1), 1131)
    seeds = list(range(2131, 2151))
    tasks = []
    for cell in ("U-G0", "PW-G0"):
        c0 = se.cond_cfg(cell, base)
        for name, kw in RULES.items():
            cfg = replace(c0, food=replace(c0.food, **kw))
            for L in (0.45, 6.46):
                aa = (L / 0.3) ** 1.5
                for moving in (True, False):
                    g = (se.rod(aa) if moving else rod_off(aa)).to_dict()
                    tasks += [((cell, name, L, moving), g, cfg, s) for s in seeds]
    R = se.run(tasks, 4)
    print("| world | rule (eat_from/eat_rule/clear_from) | arm (m) | moving: items, net (SE net) | motors off: items, net |")
    print("|---|---|---|---|---|")
    for cell in ("U-G0", "PW-G0"):
        for name in RULES:
            for L in (0.45, 6.46):
                m, o = R[(cell, name, L, True)], R[(cell, name, L, False)]
                print(f"| {cell} | {name} | {L} | {m[:, 0].mean():.2f}, {m[:, 1].mean():+.2f} ({m[:, 1].std(ddof=1) / np.sqrt(len(m)):.2f}) | "
                      f"{o[:, 0].mean():.2f}, {o[:, 1].mean():+.2f} |", flush=True)


if __name__ == "__main__":
    main()
