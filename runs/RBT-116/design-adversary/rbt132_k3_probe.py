"""RBT-132 design adversary: K3 as planters.k3_k4 reads it, against RBT-129 §5.5's K3 ("F >= F_MIN is NOT required
here: at a point that does not pay, a planted steerer that reads SMELL-USE shows the instrument can see steering").

    python runs/RBT-116/design-adversary/rbt132_k3_probe.py > runs/RBT-116/design-adversary/rbt132_k3_probe.txt

1. Logic (steer.battery_stats / call_genome): SMELL-USE = c1 and c3 and not c2, with c2 = (lbdT > 0).  k3_k4's ``seen``
   needs lbdT > 0, so a SMELL-USE record can never be seen; ``seen`` is STEERS, which needs c1 = (F >= F_MIN, lbF > 0).
2. Fixture: RBT-116's own fixture two-nose steerer (tests/test_rbt116_steer.py) on its fixture world with the season
   shortened, so the steering is there and the food gain is small.  Fixture world and plant only; no RBT-129 point.
"""
import importlib.util
import os
import sys
from dataclasses import replace

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

print("# 1. synthetic records through planters.k3_k4 (8 (a) + 8 (c) plants each)")
cases = {
    "SMELL-USE, veto passed, lbdT > 0 (impossible by construction)": {"call": steer.SMELL_USE, "stage2": {"c1": True, "c2": True, "c3": True, "lbdT": 0.2, "F": 0.4}},
    "SMELL-USE as steer.py can emit it (c2 False: lbdT <= 0)": {"call": steer.SMELL_USE, "stage2": {"c1": True, "c2": False, "c3": True, "lbdT": -0.01, "F": 0.4}},
    "steers behaviourally, F < F_MIN (a non-paying point): call NONE": {"call": steer.NONE, "stage2": {"c1": False, "c2": True, "c3": True, "lbdT": 0.3, "F": 0.1}},
    "STEERS": {"call": steer.STEERS, "stage2": {"c1": True, "c2": True, "c3": True, "lbdT": 0.3, "F": 0.6}},
}
for label, rec in cases.items():
    k = planters.k3_k4({"a": [rec] * 8, "c": [rec] * 8})
    print(f"  {label:66s} -> K3 {'PASS' if k['K3'] else 'FAIL (VOID)'} seen {k['K3_seen']}")

print("\n# 2. fixture: RBT-116's two-nose steerer, fixture world (tau 1 s), season shortened; 16 stage-2 draws")
g = T.two_nose_steerer()
bat = steer.Battery(T.DRAWS[:4], T.DRAWS[4:20], T.DRAWS[20:36])
for dur, value in ((10.0, 1.0), (3.0, 1.0), (2.0, 1.0), (1.5, 1.0), (1.0, 1.0)):
    cfg = replace(T.FIXTURE, duration=dur, food=replace(T.FIXTURE.food, value=value))
    rec = steer.call_genome(g, cfg, bat)
    s2 = rec.get("stage2", {})
    print(f"  duration {dur:4.1f} s, item value {value:4.2f}: call {rec['call']:9s} F {s2.get('F', float('nan')):+.3f} (c1 {s2.get('c1')}) lbdT {s2.get('lbdT', float('nan')):+.3f} "
          f"(c2 {s2.get('c2')}) veto c3 {s2.get('c3')} unconfirmed {rec['pass_unconfirmed']} -> k3_k4 seen: {planters.k3_k4({'a': [rec], 'c': []})['K3_seen'][0] == 1}")
