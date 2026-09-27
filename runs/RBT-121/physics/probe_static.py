"""RBT-121 audit A, probe 1: what the body model grants at build time (no stepping).

    probe_static.py SEED_DIR [...] > probe_static.txt

For every member of generation 23 of every line (U, D, C) and of the regenerated founders, both faunas, in RBT-113
seed directories (restored bulk; RUNNER §6), under the arm's own SimConfig (mass budget 15.34), this reports:

  motor capacity  sum of driven-DOF gear / (4 x mass) (the Pioneer reads 1.76), and the same ratio under each
                  candidate RBT-120 budget rule:
                    child   gear keyed to the CHILD part's mass (not the heavier of the two)
                    share   a ball joint's gear split across its driven DOFs (one joint, one motor budget)
                    both    child and share together
                    cap     sum gear <= 1.77 x 4 x mass (rescaled uniformly when over); the Pioneer reads 1.7605
                    sh+cap  share, then cap
  body plan       parts, the part cap ceil(2 x nodes), reachable nodes, how many nodes are unreachable (recessive:
                  they raise the part cap for free), the mass-budget scale, the longest part extent and the body's
                  horizontal span
  eating reach    the area (m^2) of the union of 0.35 m discs around every geom centre (the set of points where an
                  item is eaten at this instant), and the part of it more than 0.8 m (the food clearance) from the
                  root body, where a regrown item can land and be eaten on the next tick
  self-overlap    geom pairs of the same robot already in contact at build, and the deepest of them (m)

Nothing is written into any run.
"""
import os
import sys
from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RBT113 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113")
sys.path.insert(0, RBT113)
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype, JointType  # noqa: E402
from rabbitstew.world import driven_dofs  # noqa: E402

PIONEER = 1.77  # the cap c: the designed body reads 1.7605 (2 x 13.5 kg chassis / 15.337 kg), so c = 1.77 leaves it untouched
EAT, CLEAR = 0.35, 0.8
MAXED = ("cur", "ext", "span", "far", "pen")


def footprint(xy, root_xy, h=0.02):
    lo, hi = xy.min(0) - EAT, xy.max(0) + EAT
    gx, gy = np.meshgrid(np.arange(lo[0], hi[0], h), np.arange(lo[1], hi[1], h))
    pts = np.c_[gx.ravel(), gy.ravel()]
    inside = (np.linalg.norm(pts[:, None, :] - xy[None, :, :], axis=2) < EAT).any(1)
    far = np.linalg.norm(pts - root_xy, axis=1) > CLEAR
    return inside.sum() * h * h, (inside & far).sum() * h * h


def measure(g, sc):
    sc0 = replace(sc, settle_time=0.0)
    sim = S.Simulation([g], sc0, spawns=[S.Spawn((0.0, 0.0, 0.0))])
    ph, m, d, idx = sim.phenotypes[0], sim.model, sim.data, sim.robots[0]
    M = ph.total_mass()
    driven = driven_dofs(ph)
    k = sc.world.motor_strength
    cur = child = share = both = 0.0
    for p in ph.parts:
        if p.parent is None:
            continue
        nd = sum((p.index, j) in driven for j in range(p.joint_type.ndof))
        if nd == 0:
            continue
        heavy, own = k * max(p.mass, ph.parts[p.parent].mass), k * p.mass
        per = 1.0 / nd if p.joint_type == JointType.BALL else 1.0
        cur += nd * heavy
        child += nd * own
        share += nd * heavy * per
        both += nd * own * per
    cap = min(cur, PIONEER * k * M)
    shcap = min(share, PIONEER * k * M)
    xy = d.geom_xpos[idx.geoms][:, :2]
    area, far = footprint(xy, d.xpos[idx.root_body][:2])
    ext = max(max(p.dims) * (2 if p.shape.name == "SPHERE" else 1) for p in ph.parts)
    rb = m.geom_rbound[idx.geoms]
    span = max(np.linalg.norm(xy[i] - xy[j]) + rb[i] + rb[j] for i in range(len(xy)) for j in range(len(xy)))
    own = set(idx.geoms)
    pen = [-c.dist for c in d.contact[: d.ncon] if c.geom1 in own and c.geom2 in own]
    reach = len(g.reachable_nodes())
    return dict(M=M, cur=cur / (k * M), child=child / (k * M), share=share / (k * M), both=both / (k * M), cap=cap / (k * M), shcap=shcap / (k * M),
                capped=float(cur > cap * (1 + 1e-6)), parts=len(ph.parts), partcap=sc.synthesis.max_parts(len(g.nodes)),
                recessive=len(g.nodes) - reach, scaled=ph.mass_scaled, ext=ext, span=span, area=area, far=far,
                overlaps=len(pen), pen=max(pen) if pen else 0.0)


def main(argv):
    rows = {}
    for dd in argv:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = generation_sim(cfg, 1131)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                p = os.path.join(dd, L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for gname, ms in groups.items():
                rows.setdefault((kind, gname), []).extend(measure(g, sc) for g in ms)
    keys = ["M", "cur", "child", "share", "both", "cap", "shcap", "capped", "parts", "partcap", "recessive", "scaled", "ext", "span", "area", "far", "overlaps", "pen"]
    print(f"# probe_static.py over {len(argv)} seed directories: {', '.join(os.path.basename(a.rstrip('/')) for a in argv)}")
    print("# means over members (mean/max for cur, ext, span, far, pen); ratios are sum gear / (4 x mass)")
    print(f"{'fauna':12s} {'group':8s} {'n':>4s} " + " ".join(f"{k:>11s}" if k in MAXED else f"{k:>9s}" for k in keys))
    for (kind, gname), R in rows.items():
        cells = []
        for k in keys:
            v = np.array([r[k] for r in R])
            cells.append(f"{v.mean():9.3f}" if k not in MAXED else f"{v.mean():.2f}/{v.max():.2f}".rjust(11))
        print(f"{kind:12s} {gname:8s} {len(R):4d} " + " ".join(cells))


if __name__ == "__main__":
    main(sys.argv[1:])
