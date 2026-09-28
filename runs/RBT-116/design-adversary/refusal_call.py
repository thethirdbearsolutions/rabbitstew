"""RBT-116 FINAL check, item 4: the fixture that refused the decoy's θ on 14–16% of draws (FIX-CHECK theta_refusal.txt:
ONE_NOSE_WORLD under clear_from=geoms + eat_rule=surface) now gets a call; the refused draws are excluded, counted and
reported, never fatal.  Bodies: the registered G8(f) build (both sides, input −128, w +2) and the PR's two-nose steerer.
Also W1's registered eating block (root + surface + #446's guard) on the same fixture.
    python3 refusal_call.py PR_TREE > refusal_call.txt
"""
import importlib.util
import os
import sys
from dataclasses import replace

tree = sys.argv[1]
sys.path.insert(0, tree)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("tsteer", os.path.join(tree, "tests/test_rbt116_steer.py"))
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
steer = T.steer
import g8f_sides as GS  # noqa: E402

W = T.ONE_NOSE_WORLD
worlds = {"geoms+surface (refused 14-16% before)": replace(W, food=replace(W.food, eat_from="root", eat_rule="surface", clear_from="geoms")),
          "W1 block (root+surface, #446 guard)": replace(W, food=replace(W.food, eat_from="root", eat_rule="surface", clear_from="root"))}
bodies = {"G8(f) build 128/+2": GS.plant_both(128.0, 2.0), "two-nose steerer": T.two_nose_steerer()}
print("# refusal_call.py: full call_genome on the PR's test battery; refused draws per stage as reported by steer.py")
for wn, cfg in worlds.items():
    for bn, g in bodies.items():
        try:
            rec = steer.call_genome(g, cfg, T.BATTERY)
        except Exception as e:  # anything raised here is a FAIL of item 4
            print(f"{wn:40s} {bn:20s} RAISED {type(e).__name__}: {e}")
            continue
        refused = {k: v for k, v in rec.items() if "refus" in k}
        print(f"{wn:40s} {bn:20s} call {rec['call']:9s} stage {rec['stage']} | refusal fields {refused}")
        print("    " + steer.format_call(bn, rec)[:400])
