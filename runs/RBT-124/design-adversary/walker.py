"""RBT-124 design adversary: does an honest ball-jointed gait survive the cone?

    walker.py > walker.txt

A planted walker: a 1 x 0.6 x 0.25 box torso with four legs (boxes) on driven BALL joints under its corners, run by
a scripted gait instead of a brain, so the body and the gait are fixed and only the joint limit changes.  Two gaits:
  open    every Effector output A sin(2 pi f t + phase), dof 1 and 2 a quarter period apart.  With the motors'
          gear (4 x the torso's mass) this whirls the legs round (max angle pi at every A tried): it is itself a
          ball-joint rotor, the loophole, so it is shown for contrast only;
  servo   an honest stride: each leg tracks a target rotation (0.6 sin, 0.35 cos about its two bending axes; the
          rotation vector read from the joint's quaternion) with a PD law clipped to [-1, 1], so it never asks for more
          than +-0.6 rad.  A legged gait a real ball joint allows.
Diagonal pairs in phase (a trot).  Twist (dof 0) undriven.
Scored under RBT-113's generation sim (mass budget 15.34, 15 s, food world) on flat ground and on terrain 1131
(start 2131), for ball_cone off, pi/4, pi/2, 3pi/4.  Reported: COM travel (m), work (J), the largest ball-joint
rotation angle reached (rad), and whether the explosion guard fired.  Also a torque sweep (A) at pi/2.
Nothing is written into any run.
"""
import math
import os
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import world  # noqa: E402

import mujoco  # noqa: E402

from rabbitstew.evolution import generation_sim  # noqa: E402
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

TERR = generation_sim(world.evolution_config("U", "", seed=1), 1131)
FLAT = replace(TERR, world=replace(TERR.world, terrain="flat"))
CORNERS = [(1, 1), (-1, -1), (1, -1), (-1, 1)]  # diagonal pairs first
PHASE = [0.0, 0.0, math.pi, math.pi]


def walker(leg_len=0.9):
    conns = [Connection(child=1 + i, position=(0.8 * sx, 0.8 * sy, -1.0), scale=0.45, joint_type=JointType.BALL, joint_limit=None)
             for i, (sx, sy) in enumerate(CORNERS)]
    leg = lambda: Node(Segment(Shape.BOX, (leg_len, 0.18, 0.18), Brain(units=[Effector(dof=1), Effector(dof=2)])))
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 0.6, 0.25)), conns)] + [leg() for _ in range(4)], name="walker")


def rotvec(q):
    w = max(-1.0, min(1.0, q[0]))
    ang = 2 * math.acos(abs(w))
    v = np.asarray(q[1:]) * (1 if w >= 0 else -1)
    n = np.linalg.norm(v)
    return v / n * ang if n > 1e-12 else np.zeros(3)


def run(g, sc, cone, amp=1.0, freq=1.0, start=2131, servo=False, kp=4.0, kd=0.4):
    cfg = replace(sc, random_start=True, world=replace(sc.world, ball_cone=cone, hinge_range=cone))
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, start))
    if cfg.food is not None:
        sim.set_food_seed(start)
    part_phase = {p.index: PHASE[p.index - 1] for p in sim.phenotypes[0].parts if p.parent is not None}

    m0 = sim.model
    jid = {p: mujoco.mj_name2id(m0, mujoco.mjtObj.mjOBJ_JOINT, f"r0_j{p}") for p in part_phase}

    def out(part, dof):
        ph = 2 * math.pi * freq * sim.time + part_phase[part]
        if not servo:
            return amp * math.sin(ph + (0.0 if dof == 1 else math.pi / 2))
        j = jid[part]
        rv = rotvec(sim.data.qpos[m0.jnt_qposadr[j]:m0.jnt_qposadr[j] + 4])
        tgt = amp * (0.6 * math.sin(ph) if dof == 1 else 0.35 * math.cos(ph))
        u = kp * (tgt - rv[dof]) - kd * float(sim.data.qvel[m0.jnt_dofadr[j] + dof])
        return max(-1.0, min(1.0, u))

    sim.brains[0].effector_output = out
    m, d = sim.model, sim.data
    balls = [m.jnt_qposadr[j] for j in range(m.njnt) if m.jnt_type[j] == mujoco.mjtJoint.mjJNT_BALL]
    com0 = sim.center_of_mass(0)[:2].copy()
    amax = 0.0
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        for a in balls:
            amax = max(amax, 2 * math.acos(min(1.0, abs(float(d.qpos[a])))))
    return float(np.linalg.norm(sim.center_of_mass(0)[:2] - com0)), float(sim.work[0]), amax, bool(sim.exploded[0])


def main():
    g = walker()
    print("# servo gait (honest: targets within +-0.6 rad)")
    print(f"{'world':8s} {'cone':>6s} {'A':>4s} {'travel m':>9s} {'work J':>8s} {'max angle':>9s} exploded")
    for wname, sc in (("flat", FLAT), ("t1131", TERR)):
        for cone, lab in ((0.0, "off"), (math.pi / 4, "pi/4"), (math.pi / 2, "pi/2"), (3 * math.pi / 4, "3pi/4")):
            for amp in (1.0, 1.5):
                t, w, a, x = run(g, sc, cone, amp=amp, servo=True)
                print(f"{wname:8s} {lab:>6s} {amp:4.1f} {t:9.3f} {w:8.0f} {a:9.3f} {x}")
    print("# open gait (whirls: the loophole, for contrast)")
    print("# walker.py: planted ball-jointed trotter, scripted gait (A sin, f 1 Hz); RBT-113 generation sim, start 2131")
    print(f"{'world':8s} {'cone':>6s} {'A':>4s} {'travel m':>9s} {'work J':>8s} {'max angle':>9s} exploded")
    for wname, sc in (("flat", FLAT), ("t1131", TERR)):
        for cone, lab in ((0.0, "off"), (math.pi / 4, "pi/4"), (math.pi / 2, "pi/2"), (3 * math.pi / 4, "3pi/4")):
            t, w, a, x = run(g, sc, cone)
            print(f"{wname:8s} {lab:>6s} {1.0:4.1f} {t:9.3f} {w:8.0f} {a:9.3f} {x}")
    for amp in (0.25, 0.5):
        for cone, lab in ((0.0, "off"), (math.pi / 2, "pi/2")):
            t, w, a, x = run(g, FLAT, cone, amp=amp)
            print(f"{'flat':8s} {lab:>6s} {amp:4.2f} {t:9.3f} {w:8.0f} {a:9.3f} {x}")


if __name__ == "__main__":
    main()
