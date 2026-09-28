"""RBT-124 design adversary: can a holistic body meet world.is_wheel as easily as the Pioneer?

    reach_wheel.py > reach_wheel.txt

1. Built parts in restored RBT-113 O1 (seeds 1-3; regenerated founders and every U/D/C final, both faunas): unlimited
   hinges, how many are wheels by the rule, and how many of those wheels carry children.
2. The genetic route: founding axes are uniform on the sphere (genotype.random_connection), so P(|a_x| >= 0.999) = 0.001
   per founding hinge; a mutated axis is a + N(0, 0.5)^3, renormalised (genetics.py), Monte Carlo from a uniform axis
   and from an axis 5 degrees off x (a near-wheel, which the rule ranges).
3. What a wider tolerance would admit: in the same holistic bodies, unlimited hinges on round (cylinder/sphere) parts
   with |cos(axis, x)| above cos(10/20/30/45 deg), and how many are leaves (no child); and the round LEAF parts on
   ball joints (the "ball-mounted wheels" the cone takes away, runs/RBT-124/wheels.txt).
Nothing is written into any run.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import world  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype, JointType  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402
from rabbitstew.world import WHEEL_ALIGNMENT, is_wheel  # noqa: E402


def count(members, syn):
    bodies = hinges = unlimited = wheels = wheels_kids = bodies_w = 0
    for g in members:
        ph = synthesize(g, syn)
        kids = {p.parent for p in ph.parts if p.parent is not None}
        bodies += 1
        hw = 0
        for p in ph.parts:
            if p.joint_type == JointType.HINGE:
                hinges += 1
                if p.joint_range is None:
                    unlimited += 1
                    if is_wheel(p):
                        wheels += 1
                        hw += 1
                        wheels_kids += p.index in kids
        bodies_w += hw > 0
    return bodies, hinges, unlimited, wheels, wheels_kids, bodies_w


def tolerance(members, syn, out):
    from rabbitstew.genotype import Shape
    for g in members:
        ph = synthesize(g, syn)
        kids = {p.parent for p in ph.parts if p.parent is not None}
        for p in ph.parts:
            if p.shape not in (Shape.CYLINDER, Shape.SPHERE):
                continue
            leaf = p.index not in kids
            if p.joint_type == JointType.BALL:
                out["ball round"] += 1
                out["ball round leaf"] += leaf
            if p.joint_type == JointType.HINGE and p.joint_range is None:
                c = abs(p.joint_axis[0]) / np.linalg.norm(p.joint_axis)
                out["unlim hinge round"] += 1
                for deg in (10, 20, 30, 45):
                    if c >= np.cos(np.radians(deg)):
                        out[f"within {deg} deg"] += 1
                        out[f"within {deg} deg, leaf"] += leaf


def main():
    arm = os.path.join(ROOT, "runs", "RBT-113", "O1")
    print(f"# reach_wheel.py: WHEEL_ALIGNMENT {WHEEL_ALIGNMENT}")
    print(f"{'fauna':10s} {'group':9s} {'bodies':>6s} {'hinges':>6s} {'unlim':>6s} {'wheels':>6s} {'w/kids':>6s} {'bodies w/ wheel':>15s}")
    tot = {}
    for kind in (HOLISTIC, CONVENTIONAL):
        for seed in (1, 2, 3):
            cfg = world.evolution_config("U", "", seed=seed)
            groups = {"founders": initial_population(kind, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[kind]).members}
            for L in "UDC":
                p = os.path.join(arm, str(seed), L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for gname, ms in groups.items():
                r = count(ms, cfg.sim.synthesis)
                t = tot.setdefault((kind, gname), [0] * 6)
                for i, x in enumerate(r):
                    t[i] += x
    tol = {}
    for seed in (1, 2, 3):
        cfg = world.evolution_config("U", "", seed=seed)
        ms = initial_population(HOLISTIC, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[HOLISTIC]).members
        for L in "UDC":
            p = os.path.join(arm, str(seed), L, HOLISTIC, "final")
            ms += [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        tolerance(ms, cfg.sim.synthesis, tol := tol if tol else __import__("collections").Counter())
    for (kind, gname), t in tot.items():
        print(f"{kind:10s} {gname:9s} " + " ".join(f"{x:6d}" for x in t[:5]) + f" {t[5]:15d}")

    print("\nholistic, all 480 bodies (founders + U/D/C finals, O1/1-3): " + ", ".join(f"{k} {v}" for k, v in tol.items()))
    rng = np.random.default_rng(124)
    n = 2_000_000
    a = rng.normal(size=(n, 3))
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    print(f"\nuniform founding axis: P(|a_x| >= {WHEEL_ALIGNMENT}) = {np.mean(np.abs(a[:, 0]) >= WHEEL_ALIGNMENT):.5f} (exact {1 - WHEEL_ALIGNMENT:.5f})")
    for label, start in (("uniform axis", a), ("5 deg off x", np.tile([np.cos(np.radians(5)), np.sin(np.radians(5)), 0.0], (n, 1))),
                         ("2 deg off x (a wheel)", np.tile([np.cos(np.radians(2)), np.sin(np.radians(2)), 0.0], (n, 1)))):
        m = start + rng.normal(0, 0.5, (n, 3))
        m /= np.linalg.norm(m, axis=1, keepdims=True)
        print(f"one axis mutation from {label:22s}: P(wheel after) = {np.mean(np.abs(m[:, 0]) >= WHEEL_ALIGNMENT):.5f}")


if __name__ == "__main__":
    main()
