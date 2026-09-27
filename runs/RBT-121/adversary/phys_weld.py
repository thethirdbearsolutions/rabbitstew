"""RBT-121 adversary (physics): which same-robot geom pairs does MuJoCo's parent filter actually drop?

    phys_weld.py SEED_DIR [...] > phys_weld.txt

MuJoCo's filterparent works on WELD groups (bodies joined with no joint collapse into one weld body, body_weldid),
not on bodies: two geoms never collide if they are in the same weld group, or if one weld group is the parent weld
group of the other (unless that parent is the world).  So with FIXED connections (no joint in world.py) a limb also
passes through its grandparent, its fixed siblings, etc.  For every holistic member (gen 23 of U, D, C and founders)
this counts same-robot geom pairs (a) that are body parent-child, (b) that MuJoCo filters, by the weld rule, and
(c) = (b) minus (a): extra filtered pairs audit A's "a child never collides with its parent" does not mention.
It verifies the rule empirically on overlapping pairs (mj_geomDistance < -5 mm) against d.contact.  No stepping.
"""
import os
import sys
from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

TERRAIN, START = decompose.DRAWS[0]


def one(g, sc):
    cfg = replace(sc, random_start=True, settle_time=0.0)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, START))
    m, d, idx = sim.model, sim.data, sim.robots[0]
    mujoco.mj_forward(m, d)
    gl = list(idx.geoms)
    con = {(int(c.geom1), int(c.geom2)) for c in d.contact[: d.ncon]}
    con |= {(b, a) for a, b in con}
    n = pc = filt = extra = ov_pred = ov_ok = 0
    for i, a in enumerate(gl):
        for b in gl[i + 1:]:
            ba, bb = m.geom_bodyid[a], m.geom_bodyid[b]
            wa, wb = m.body_weldid[ba], m.body_weldid[bb]
            is_pc = m.body_parentid[ba] == bb or m.body_parentid[bb] == ba
            f = wa == wb or (m.body_weldid[m.body_parentid[wa]] == wb and wb != 0) or (m.body_weldid[m.body_parentid[wb]] == wa and wa != 0)
            n += 1
            pc += is_pc
            filt += f
            extra += f and not is_pc
            if mujoco.mj_geomDistance(m, d, a, b, 0.5, None) < -0.005:
                ov_pred += 1
                ov_ok += (f == ((a, b) not in con))
    return n, pc, filt, extra, ov_pred, ov_ok


def main():
    rows = {}
    for dd in sys.argv[1:]:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = generation_sim(cfg, TERRAIN)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        groups = {"founders": initial_population(HOLISTIC, cfg, streams[HOLISTIC]).members}
        for L in "UDC":
            p = os.path.join(dd, L, HOLISTIC, "final")
            groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        for k, ms in groups.items():
            rows.setdefault(k, []).extend(one(g, sc) for g in ms)
    print("# phys_weld.py over", len(sys.argv) - 1, "dirs; same-robot geom pairs, summed over all holistic members")
    print("# group  members  pairs  parent-child  filtered(weld rule)  filtered-but-not-parent-child  overlapping(<-5mm)  rule-agrees-with-d.contact")
    for k, R in rows.items():
        R = np.array(R).sum(axis=0)
        print(f"{k:9s} {len(rows[k]):4d} " + " ".join(f"{int(x):7d}" for x in R))


if __name__ == "__main__":
    main()
