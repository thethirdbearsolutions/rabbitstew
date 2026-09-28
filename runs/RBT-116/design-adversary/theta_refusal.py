"""RBT-116 FIX-CHECK item 6: the decoy's θ re-draw under the world's clearance rule (S-M1 fix) meets W1's reconciled
eating rule (root + surface, addendum 03:10).  How often does draw_theta find NO θ in [30°, 330°] that clears?

LAYOUT GEOMETRY ONLY: a Simulation is built and its food placed (set_food_seed), then draw_theta is asked for θ; no
season is stepped, no call is made.  Seeds are the PR's TEST draws (100+i, 200+i), never W1's registered pool.
Bodies: the Pioneer (fixed.pioneer_genotype) and RBT-113 O1 seed-1 U finals (committed checkpoint), holistic and
designed.  Layouts: (F) the PR's ONE_NOSE_WORLD fixture (8 items in a 2 m disc); (L) W1's layout PARAMETERS (12 items,
2 patches of 0.4 m, 4 m disc, start 1.5-2.5 m), on test seeds.  Rules: root | geoms (centres) | surface (W1-eat).
    python3 theta_refusal.py PR_TREE CKPT_O1_SEED_DIR > theta_refusal.txt
"""
import importlib.util
import os
import sys
from dataclasses import replace

import numpy as np

tree, ck = sys.argv[1], sys.argv[2]
sys.path.insert(0, tree)
spec = importlib.util.spec_from_file_location("tsteer", os.path.join(tree, "tests/test_rbt116_steer.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
steer = T.steer
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import spawn_layout  # noqa: E402

F = T.ONE_NOSE_WORLD
L = replace(F, start_distance_range=(1.5, 2.5), duration=15.0,
            food=replace(F.food, items=12, patches=2, patch_radius=0.4, radius=4.0, regrow_delay=60.0, decay=1.5))
RULES = {"root": dict(eat_from="root", eat_rule="centre", clear_from="root"),
         "geoms": dict(eat_from="root", eat_rule="centre", clear_from="geoms"),
         "surface (W1-eat)": dict(eat_from="root", eat_rule="surface", clear_from="geoms")}


def bodies():
    out = [("Pioneer (fixture)", T.two_nose_steerer())]
    for kind in ("holistic", "conventional"):
        d = os.path.join(ck, "U", kind, "final")
        out += [(f"RBT-113 {kind} {f}", Genotype.load(os.path.join(d, f))) for f in sorted(os.listdir(d))[:8]]
    return out


def refused(g, cfg, draw):
    c = replace(steer.draw_sim(cfg, draw), opponent_proxy=True)
    sim = steer.DecoySimulation([g], c, spawns=[spawn_layout(2, c, draw.start_seed)[0]])
    sim.set_food_seed(draw.start_seed)
    try:
        _, k = steer.draw_theta(draw.start_seed, steer._live_items(sim), steer.world_clearance(sim))
        return False, k
    except RuntimeError:
        return True, None


print("# theta_refusal.py: layout geometry only (no season stepped); PR test seeds; share of draws with NO clear θ")
draws = T.DRAWS[:36]
B = bodies()
for lname, base in (("F: PR one-nose fixture", F), ("L: W1 layout params, test seeds", L)):
    print(f"\n## {lname}")
    print("rule               body group            draws   refused   mean redraws (when found)")
    for rname, kw in RULES.items():
        cfg = replace(base, food=replace(base.food, **kw))
        for grp in ("Pioneer", "RBT-113 holistic", "RBT-113 conventional"):
            rs = [refused(g, cfg, d) for n, g in B if n.startswith(grp) for d in draws]
            ks = [k for r, k in rs if not r]
            print(f"{rname:18s} {grp:21s} {len(rs):5d}   {sum(r for r, _ in rs) / len(rs):7.3f}   {np.mean(ks) if ks else float('nan'):8.1f}", flush=True)
