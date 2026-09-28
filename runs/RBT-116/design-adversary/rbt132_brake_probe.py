"""RBT-132 fix-check: does planters.slowing_sign actually SLOW a designed host?

    python runs/RBT-116/design-adversary/rbt132_brake_probe.py HOSTS_ROOT > runs/RBT-116/design-adversary/rbt132_brake_probe.txt

The 07:10 ruling (S6) fixes G8(b)'s brake to the slowing sign.  planters.slowing_sign(backward) returns -1 for a host
that travels chassis-forward and +1 for one that travels backward; the test pins those constants but not their physics.
Here each host gets G8(b)'s brake path with the nose removed: a constant unit (relu, bias 1) wired to the two drive
Effectors at +sB*0.5 (LEFT) and -sB*0.5 (RIGHT), exactly plant_b's difference-axis term with s_T = 0 and the unit fully
on.  Mean CoM speed over 6 fixture draws is compared: host alone, sB = slowing_sign(travel), sB = its opposite.
Fixture world (tests/test_rbt116_steer.FIXTURE, W1-shaped, tau 1 s) and fixture draws only; hosts: RBT-19 P-801's
designed body and the first RBT-113 O1 U designed finals in sorted order (not planters.py's permutation).
"""
import copy
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-116"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


planters = load("planters", os.path.join(ROOT, "runs", "RBT-116", "planters.py"))
steer = planters.steer
T = load("t116", os.path.join(ROOT, "tests", "test_rbt116_steer.py"))
from rabbitstew.genotype import Brain, Genotype, Link, Neuron, UnitRef  # noqa: E402

CFG = T.FIXTURE
DRAWS = T.DRAWS[:6]


def brake(g, sB, gain=0.5):
    nose, eff = planters.routed.unit_indices(g)
    out = copy.deepcopy(g)
    gb = out.global_brain if out.global_brain is not None else Brain()
    out.global_brain = gb
    gb.units.append(Neuron(bias=1.0, func="relu"))
    u = len(gb.units) - 1
    for nd, side in ((planters.LEFT, +1.0), (planters.RIGHT, -1.0)):
        out.nodes[nd].segment.brain.links.append(Link(UnitRef(None, u), UnitRef(nd, eff), side * sB * gain))
    assert out.validate() == []
    return out


def speed(g):
    return float(np.mean([np.mean(steer.run_season(g, CFG, d, "intact").speed) for d in DRAWS]))


root = sys.argv[1] if len(sys.argv) > 1 else None
hosts = [os.path.join(ROOT, "runs", "RBT-19", "P-801", "conventional", "best_gen0590.json")]
if root:
    d = os.path.join(root, "O1", "1", "U", "conventional", "final")
    hosts += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f[:-5].isdigit()][:5]
print("# rbt132_brake_probe.py: G8(b)'s brake term alone (constant unit, s_T 0), mean CoM speed (m/s) over 6 fixture draws")
print(f"# {'host':42s} travel    alone   sB=slowing_sign  sB=opposite  | slows (vs alone and vs opposite)?")
ok = rel = 0
for p in hosts:
    g = Genotype.load(p)
    back = planters.travel_backward(g, CFG)
    if back is None:
        print(f"  {os.path.relpath(p, root or ROOT)[-42:]:42s} UNDETERMINED")
        continue
    s0 = speed(g)
    sb = planters.slowing_sign(back)
    s1, s2 = speed(brake(g, sb)), speed(brake(g, -sb))
    good = s1 < s0 and s1 < s2
    ok += good
    rel += s1 < s2
    print(f"  {os.path.relpath(p, root or ROOT)[-42:]:42s} {'backward' if back else 'forward ':8s} {s0:7.3f}  {s1:14.3f}  {s2:11.3f}  | {'YES' if good else 'NO'}"
          f" (slower than the opposite sign: {'yes' if s1 < s2 else 'no'})")
print(f"# slowing_sign slows below the host alone AND below the opposite sign on {ok} hosts; below the opposite sign on {rel}")
