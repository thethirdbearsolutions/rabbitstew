"""RBT-116 (FC-M1): why do rectified one-nose plants driving BOTH wheels at w >= 4 earn F ~ +3 on the fixture yet read
NONE?  The full call record (format_call) of four plants from design-adversary/g8f_sides.py on ONE_NOSE_WORLD at
tau = 1 s, test battery 4 + 16 + 16.  Fixture only.

    python runs/RBT-116/g8f_diag.py > runs/RBT-116/g8f_diag.txt
"""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tests")); sys.path.insert(0, ROOT)
import test_rbt116_steer as T
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE
from rabbitstew.genotype import Link, UnitRef
from concurrent.futures import ProcessPoolExecutor
steer = T.steer
def plant(a, w):
    g = T._pioneer(noses=(LEFT_DRIVE,), throttle=0.8); k = T._unit(g, "relu")
    g.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), a))
    for nd in (LEFT_DRIVE, RIGHT_DRIVE):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    return g
def job(v):
    a, w = v
    rec = steer.call_genome(plant(a, w), T.ONE_NOSE_WORLD, T.BATTERY)
    return v, steer.format_call(f"in {a} w {w}", rec)
if __name__ == "__main__":
    print("# g8f_diag.py: rectified one-nose plant (Pioneer, left-wheel nose) to BOTH drive Effectors; ONE_NOSE_WORLD, tau 1 s; full call records")
    with ProcessPoolExecutor(4) as ex:
        for v, line in ex.map(job, [(-128.0, 2.0), (-128.0, 4.0), (-128.0, 16.0), (-32.0, 4.0)]):
            print(line)
