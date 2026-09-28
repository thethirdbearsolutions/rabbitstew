"""RBT-132 design adversary, item 3 / R3: can RBT-113 O1's committed U-line finals carry their plants?

    python runs/RBT-116/design-adversary/rbt132_host_carry.py HOSTS_ROOT > runs/RBT-116/design-adversary/rbt132_host_carry.txt

HOSTS_ROOT is ckpt/rbt-113-O1 restored (O1/<seed>/U/<kind>/final).  Every final is examined in sorted order, NOT in
planters.py's registered permutation (so nothing here says which hosts the planted command will take).  The world is
tests/test_rbt132.py's fixture (G 2.5, tau 2 s, root + surface eating, flat, not --fair) on fixture draws; no RBT-129
point, pool, battery or config is used.  Designed: is_designed and routed.unit_indices (no simulation).  Holistic:
planters.body_geometry on a fixture draw, then planters.c_layout, with the reason for each refusal.
"""
import collections
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


T = load("t132", os.path.join(ROOT, "tests", "test_rbt132.py"))
planters, steer = T.planters, T.steer
from rabbitstew.fair import is_designed  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

root = sys.argv[1]
print(f"# rbt132_host_carry.py: RBT-113 O1 U finals under {os.path.basename(os.path.normpath(root))}; fixture world tests/test_rbt132.FIX_G, fixture draws")
for kind in ("conventional", "holistic"):
    files = [os.path.join(root, "O1", str(s), "U", kind, "final", f) for s in planters.HOST_SEEDS
             for f in sorted(os.listdir(os.path.join(root, "O1", str(s), "U", kind, "final"))) if f[:-5].isdigit()]
    why = collections.Counter()
    for f in files:
        g = Genotype.load(f)
        if kind == "conventional":
            if not is_designed(g):
                why["not designed"] += 1
                continue
            try:
                planters.routed.unit_indices(g)
                why["can carry (a)/(b) (before the direction probe)"] += 1
            except (AssertionError, StopIteration):
                why["no routed motif"] += 1
            continue
        reasons = []
        for d in T.DRAWS[:3]:
            geom = planters.body_geometry(g, T.FIX_G, d)
            if geom is None:
                reasons.append("no heading (< 5 cm)")
                continue
            ph, lat = geom["phenotype"], geom["lat"]
            single = [(nd, p[0]) for nd, p in ph.node_instances.items() if len(p) == 1]
            lay = planters.c_layout(g, geom)
            if lay is not None:
                reasons.append("carries")
            elif len(single) < 2:
                reasons.append("< 2 single-instance Nodes")
            elif not (max(lat[p] for _, p in single) > 0 > min(lat[p] for _, p in single)):
                reasons.append("single-instance Nodes all one side")
            else:
                reasons.append("no one-sided Effector Node on each side")
        why[f"draw 1: {reasons[0]}"] += 1
        why["carries on all 3 fixture draws" if all(r == "carries" for r in reasons) else
            ("carries on some fixture draws, not all" if "carries" in reasons else "carries on none of 3")] += 1
    print(f"\n## {kind}: {len(files)} finals")
    for k, v in sorted(why.items()):
        print(f"  {v:4d}  {k}")
