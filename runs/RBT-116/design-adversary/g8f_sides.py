"""RBT-116 FIX-CHECK item 4: g8f_grid.py found Amendment 2's ONE-SIDE grid steers on 0 of 12 at τ = 1 s.  Is it the side
rule?  The same rectified unit (input −g), linked ±w to BOTH drive Effectors, at τ = 1 s, on the same fixture/battery.
    python3 g8f_sides.py PR_TREE [workers] > g8f_sides.txt
"""
import sys
from concurrent.futures import ProcessPoolExecutor

import g8f_grid as G
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE
from rabbitstew.genotype import Link, UnitRef


def plant_both(g_in, w):
    g = G.T._pioneer(noses=(LEFT_DRIVE,), throttle=0.8)
    k = G.T._unit(g, "relu")
    g.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), -g_in))
    for nd in (LEFT_DRIVE, RIGHT_DRIVE):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    return g


def job(v):
    g_in, w = v
    rec = G.steer.call_genome(plant_both(g_in, w), G.WORLDS["default"], G.T.BATTERY)
    s2 = rec.get("stage2") or {}
    return g_in, w, rec["call"], s2.get("F", float("nan"))


if __name__ == "__main__":
    grid = [(g, w) for g in (128.0,) for w in (2.0, 4.0, -4.0, 16.0, -16.0, 64.0)] + [(32.0, 4.0), (32.0, 16.0)]
    with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
        res = list(ex.map(job, grid))
    print(f"# g8f_sides.py: rectified one-nose unit to BOTH drive Effectors, fixture ONE_NOSE_WORLD at τ = {G.T.ONE_NOSE_WORLD.food.smell_tau}")
    for g_in, w, call, F in res:
        print(f"in {-g_in:6.0f}  w {w:5.0f}  both wheels   {call:10s} F {F:+.3f}")
    print(f"# STEERS on {sum(r[2] == 'STEERS' for r in res)} of {len(res)}")
