"""RBT-116 FINAL check, item 2: is the "F falls on the confirmation battery" an artefact of the call (a defect that
would also hit real steerers) or of the unscreened test battery's draws?

On the PR's ONE_NOSE_WORLD fixture (τ = 1 s) and test BATTERY, for the rectified both-sides plant (input −128, w 4:
PASS-UNCONFIRMED in g8f_diag.txt) and the registered (128, +2) build:
  (a) the call as registered;
  (b) the SAME genome with stage 2 and confirmation SWAPPED (a draw effect follows the draws; a position/state effect
      stays with the stage);
  (c) the confirmation draws' F computed alone, in a fresh call of battery_stats (no preceding seasons): equal to (a)'s
      confirmation F iff no state leaks between seasons;
  (d) draw quality with no smell at all: a sensorless mover's intact food on the stage-2 vs confirmation draws, and the
      plants' LESIONED food there (what the body eats without information);
  (e) seeding: the stage-2 and confirmation draws are disjoint, and each season's θ is a function of its start seed only.
    python3 confirm_probe.py PR_TREE > confirm_probe.txt
"""
import importlib.util
import os
import sys

import numpy as np

tree = sys.argv[1]
sys.path.insert(0, tree)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("tsteer", os.path.join(tree, "tests/test_rbt116_steer.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
steer = T.steer
import g8f_sides as GS  # noqa: E402  (plant_both: rectified unit to both drive Effectors)

W, B = T.ONE_NOSE_WORLD, T.BATTERY
swap = steer.Battery(B.stage1, B.confirm, B.stage2)
print(f"# confirm_probe.py: ONE_NOSE_WORLD (τ = {W.food.smell_tau}), test battery; stage-2 draws {B.stage2[0].start_seed}..{B.stage2[-1].start_seed}, confirmation {B.confirm[0].start_seed}..{B.confirm[-1].start_seed}")
print(f"(e) draws disjoint: {not (set(B.stage2) & set(B.confirm))}")
for g_in, w in ((128.0, 4.0), (128.0, 2.0)):
    g = GS.plant_both(g_in, w)
    a = steer.call_genome(g, W, B)
    b = steer.call_genome(g, W, swap)
    c = steer.battery_stats(steer._pairs(g, W, B.confirm, steer.run_season)[0])
    s2b = b.get("stage2", {})
    print(f"\n## plant in -{g_in:.0f} w {w:.0f}")
    print(f"(a) registered: {a['call']:9s} stage-2 F {a['stage2']['F']:+.3f} lb {a['stage2']['lbF']:+.3f} | confirm F {a['confirm']['F']:+.3f} lb {a['confirm']['lbF']:+.3f}")
    cf = b.get("confirm")
    print(f"(b) swapped:    {b['call']:9s} stage-2 (old confirm draws) F {s2b.get('F', float('nan')):+.3f} lb {s2b.get('lbF', float('nan')):+.3f}"
          + (f" | confirm (old stage-2 draws) F {cf['F']:+.3f} lb {cf['lbF']:+.3f}" if cf else " | (stopped at stage 2)"))
    print(f"(c) confirm draws alone: F {c['F']:+.3f} lb {c['lbF']:+.3f}  == (a)'s confirm: {abs(c['F'] - a['confirm']['F']) < 1e-12 and abs(c['lbF'] - a['confirm']['lbF']) < 1e-12}")
    les = {k: np.mean([steer.run_season(g, W, d, 'lesion').food for d in ds]) for k, ds in (("stage2", B.stage2), ("confirm", B.confirm))}
    inta = {k: np.mean([steer.run_season(g, W, d, 'intact').food for d in ds]) for k, ds in (("stage2", B.stage2), ("confirm", B.confirm))}
    print(f"(d) plant intact food: stage-2 draws {inta['stage2']:.2f}, confirm draws {inta['confirm']:.2f} | lesioned: {les['stage2']:.2f} vs {les['confirm']:.2f}")
m = T.sensorless_mover()
fm = {k: np.mean([steer.run_season(m, W, d, 'intact').food for d in ds]) for k, ds in (("stage2", B.stage2), ("confirm", B.confirm))}
print(f"\n(d) sensorless mover intact food: stage-2 draws {fm['stage2']:.2f}, confirmation draws {fm['confirm']:.2f}")
