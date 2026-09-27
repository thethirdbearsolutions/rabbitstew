"""RBT-121 audit A, probe 3: hand-built bodies that reach allowances no committed line has reached yet.

    probe_synthetic.py > probe_synthetic.txt

All under RBT-113's SimConfig (mass budget 15.34, food world, work cost 0.03 / kJ, 15 s solo seasons), on RBT-113's
first generation sim (terrain 1131).  Nothing is written into any run.

S1  STAR HUB + RECESSIVE NODES.  A 13.5 kg sphere root with k light boxes on driven ball joints (all 3 DOFs).  Each
    child's gear is keyed to the ROOT's mass, 3 times.  The part cap is ceil(2 x nodes), so k > 3 needs extra nodes:
    they are added as unreachable (recessive) nodes, which cost nothing and are never built.  Reported: parts, sum
    gear / (4 x mass) (the Pioneer: 1.76), the free-spin work ceiling in yield units (as probe_gear.py), and the
    work actually burnt in one season at full throttle.
S2  ROD SWEEPER.  A 0.3 m cube root with ONE child: a box of relative dims (5, 0.05, 0.05) -- inside the mutation
    operator's clip [0.05, 5] -- normalised to unit volume, so at size 0.3 it is 6.5 m long and 6.5 cm thick.  It is
    hinged about the vertical to the root and driven at full throttle, so its geom centre (3.4 m out) sweeps a circle.
    Reported over 20 start draws: food, work, net yield, and the same with the motor OFF (a free lunch can only come
    from an item placed or regrown within 0.35 m of a geom centre that is more than the 0.8 m clearance from the root).
    Compare: the designed D, U lines eat 0.9-1.3 items per season (probe_food.txt, decompose.txt).
"""
import math
import os
import sys
from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import world  # noqa: E402
sys.path.insert(0, HERE)
from probe_static import measure  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402

SC = generation_sim(world.evolution_config("U", "", seed=1), 1131)


def ceiling(sim):
    m = sim.model
    tot = c = 0.0
    for a in range(m.nu):
        j = m.actuator_trnid[a, 0]
        k = int(np.argmax(np.abs(m.actuator_gear[a, :3])))
        dof = m.jnt_dofadr[j] + (k if m.jnt_type[j] == mujoco.mjtJoint.mjJNT_BALL else 0)
        g = abs(m.actuator_gear[a, k])
        tot += g
        c += g * g / max(m.dof_damping[dof], 1e-9)
    return tot, c * SC.duration * 0.03 / 1000


def season(g, seed, off=False):
    cfg = replace(SC, random_start=True)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    if off:
        sim.brains[0].effector_output = lambda *a: 0.0
    sim.run()
    return sim


def star(k):
    child = Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[Effector(dof=d, bias=3.0) for d in range(3)]))
    conns = []
    for i in range(k):
        a, b = 2 * math.pi * i / max(k, 1), math.pi * (0.25 + 0.5 * ((i * 0.618) % 1.0))
        conns.append(Connection(child=1, position=(math.cos(a) * math.sin(b), math.sin(a) * math.sin(b), math.cos(b)), scale=0.25,
                                joint_type=JointType.BALL, joint_limit=None))
    nodes = [Node(Segment(Shape.SPHERE, (1.0,)), conns), Node(child)]
    need = math.ceil((k + 1) / 2.0)
    nodes += [Node(Segment(Shape.BOX, (1.0, 1.0, 1.0))) for _ in range(max(0, need - 2))]  # recessive: unreachable
    return Genotype(nodes=nodes, name=f"star{k}")


def rod(off=False):
    arm = Segment(Shape.BOX, (5.0, 0.05, 0.05), Brain(units=[Effector(dof=0, bias=3.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0)), [conn]), Node(arm)], name="rod")


def main():
    print("# S1 star hub: k light children on driven ball joints around a heavy root; extra nodes are recessive")
    print(f"{'k':>3s} {'nodes':>5s} {'parts':>5s} {'mass':>6s} {'sum gear':>9s} {'/(4 x mass)':>11s} {'ceiling (yield)':>15s} {'work burnt (yield)':>18s} {'exploded':>8s}  under the RBT-120 rules: child / share / both / cap / share+cap")
    for k in (1, 3, 6, 12, 24, 40):
        g = star(k)
        sim = season(g, 2131)
        tot, ceil = ceiling(sim)
        M = sim.phenotypes[0].total_mass()
        print(f"{k:3d} {len(g.nodes):5d} {len(sim.phenotypes[0].parts):5d} {M:6.2f} {tot:9.1f} {tot / (4 * M):11.2f} {ceil:15.2f} {sim.work[0] * 0.03 / 1000:18.2f} {str(bool(sim.exploded[0])):>8s}  "
              + " / ".join(f"{r[k]:.2f}" for r in [measure(g, SC)] for k in ("child", "share", "both", "cap", "shcap")))
    print("#   the Pioneer: sum gear 108, / (4 x mass) 1.76, ceiling 0.97 yield")
    print()
    print("# S2 rod sweeper: one 6.5 m arm hinged about the vertical, full throttle; 20 start draws (2131..2150)")
    g = rod()
    ph = season(g, 2131).phenotypes[0]
    print(f"#   parts {len(ph.parts)}, arm dims {tuple(round(x, 3) for x in ph.parts[1].dims)} m, mass {ph.total_mass():.2f} kg (scaled x{ph.mass_scaled:.2f})")
    for off in (False, True):
        R = []
        for s in range(2131, 2151):
            sim = season(g, s, off)
            R.append((sim.food_eaten[0], sim.work[0] * 0.03 / 1000, sim.food_score(0), sim.exploded[0]))
        R = np.array(R, float)
        print(f"#   motor {'OFF' if off else 'ON '}: food {R[:, 0].mean():.2f} [{R[:, 0].min():.0f}, {R[:, 0].max():.0f}]  work {R[:, 1].mean():.3f}  net {R[:, 2].mean():+.2f}  exploded {int(R[:, 3].sum())}/20")


if __name__ == "__main__":
    main()
