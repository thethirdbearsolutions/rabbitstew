"""RBT-116 FINAL check, item 1: independent reproduction of Amendment 3's registered G8(f) builds on its three fixture
variants (τ = 1 s): F1 ONE_NOSE_WORLD, test battery; F2 the same under W1's eating block (root + surface, clear_from
root, #446 guard); F3 F1's world on the second test battery (draws 40–75 of the test stream: Draw(100+i, 200+i)).
Plant: g8f_sides.plant_both (rectified unit on the left-wheel nose at input −g, +w to both drive Effectors).
    python3 g8f_rule_repro.py PR_TREE [workers] > g8f_rule_repro.txt
"""
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import g8f_sides as GS

T, steer = GS.G.T, GS.G.steer
W = T.ONE_NOSE_WORLD
W1EAT = replace(W, food=replace(W.food, eat_from="root", eat_rule="surface", clear_from="root"))
D2 = [steer.Draw(100 + i, 200 + i) for i in range(40, 76)]
B2 = steer.Battery(D2[:4], D2[4:20], D2[20:36])
VAR = {"F1": (W, T.BATTERY), "F2": (W1EAT, T.BATTERY), "F3": (W, B2)}
BUILDS = [(32.0, 16.0), (32.0, 64.0), (128.0, 2.0), (128.0, 16.0)]


def job(a):
    (g, w), v = a
    cfg, bat = VAR[v]
    return (g, w), v, steer.call_genome(GS.plant_both(g, w), cfg, bat)["call"]


if __name__ == "__main__":
    tasks = [(b, v) for b in BUILDS for v in VAR]
    with ProcessPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
        res = list(ex.map(job, tasks))
    print(f"# g8f_rule_repro.py: Amendment 3's 4 registered builds, τ = {W.food.smell_tau}")
    for b in BUILDS:
        calls = {v: c for bb, v, c in res if bb == b}
        n = sum(c == "STEERS" for c in calls.values())
        print(f"g {b[0]:4.0f} w +{b[1]:<3.0f} | F1 {calls['F1']:8s} F2 {calls['F2']:8s} F3 {calls['F3']:8s} | STEERS {n}/3 {'majority' if n >= 2 else 'NO MAJORITY'}")
