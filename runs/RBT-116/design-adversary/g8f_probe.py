"""RBT-116 steer.py design adversary: can G8(f) as REGISTERED produce a one-nose steerer the call confirms?

§4.3 G8(f): "one food sensor on the host's most-moving expressed Part, a global unit on its reading, and a turn command
±w to the Effectors on one side of the measured heading, 2 signs × w ∈ {4, 16, 64}, best by F on screening draws."
The PR's passing one-nose fixture plant (tests/test_rbt116_steer.py one_nose_steerer) is different: a RELU unit on
−128 × the reading (turn only while the contrast FALLS) driving BOTH wheels at w = 2.  Here, on the PR's own
ONE_NOSE_WORLD fixture and test battery (Pioneer host, nose on the left wheel, as the fixture): the registered shape
(tanh unit, input weight 1, ±w to ONE wheel's Effector) against the fixture's rectified shape.  Full call_genome.
    python3 g8f_probe.py PR_TREE [workers] > g8f_probe.txt
"""
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor

tree = sys.argv[1]
sys.path.insert(0, tree)
spec = importlib.util.spec_from_file_location("tsteer", os.path.join(tree, "tests/test_rbt116_steer.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
steer = T.steer
from rabbitstew.fixed import LEFT_DRIVE, RIGHT_DRIVE  # noqa: E402
from rabbitstew.genotype import Link, UnitRef  # noqa: E402


def plant(func, a, w, both):
    g = T._pioneer(noses=(LEFT_DRIVE,), throttle=0.8)
    k = T._unit(g, func)
    g.global_brain.links.append(Link(UnitRef(LEFT_DRIVE, 1), UnitRef(None, k), a))
    for nd in ((LEFT_DRIVE, RIGHT_DRIVE) if both else (LEFT_DRIVE,)):
        g.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, 0), w))
    assert g.is_valid(), g.validate()
    return g


VARIANTS = [("registered: tanh, in 1, one wheel", "tanh", 1.0, w, False) for w in (4.0, -4.0, 16.0, -16.0, 64.0, -64.0)]
VARIANTS += [("fixture: relu, in -128, both wheels", "relu", -128.0, 2.0, True),
             ("tanh, in -128, both wheels", "tanh", -128.0, 2.0, True),
             ("relu, in -1, one wheel", "relu", -1.0, 16.0, False)]


def job(v):
    lab, func, a, w, both = v
    rec = steer.call_genome(plant(func, a, w, both), T.ONE_NOSE_WORLD, T.BATTERY)
    s2 = rec.get("stage2") or {}
    return lab, a, w, rec["call"], s2.get("F", float("nan")), s2.get("lbdT", float("nan")), rec["pass_unconfirmed"]


if __name__ == "__main__":
    with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
        res = list(ex.map(job, VARIANTS))
    print("# g8f_probe.py: PR #434's ONE_NOSE_WORLD fixture and test battery (4 + 16 + 16), Pioneer host, one wheel nose")
    print("variant                                 in gain      w   call        F(stage 2)  lb dT   pass-unconfirmed")
    for lab, a, w, call, F, lbt, pu in res:
        print(f"{lab:38s} {a:8.0f} {w:6.0f}   {call:10s} {F:+8.3f}  {lbt:+7.3f}   {pu}")
