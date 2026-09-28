"""RBT-132 item 4: mutants of holistic_steps.py, with the design adversary's harness unchanged (``rbt132_new_mutants.run``:
a hard-linked private copy per mutant, ``pytest -x`` on tests/test_rbt132.py and tests/test_rbt116_steer.py).

    python runs/RBT-116/rbt132_steps_mutants.py TREE [WORKERS] > runs/RBT-116/rbt132_steps_mutants.txt

Each is a plausible one-line fault against RBT132.md §4 as ruled.  Fixture tests only.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "design-adversary"))
import rbt132_new_mutants as NM  # noqa: E402

H = "runs/RBT-116/holistic_steps.py"
MUTANTS = [
    (NM.S, "CONTROL (no fault: must SURVIVE)", "N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM", "N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM"),
    # the arms
    (H, "step-per-link-not-total", "A_STEP = 0.8", "A_STEP = 0.4"),
    (H, "step-flips-the-sign", "planters.plant_c(host, layout, sign, a)", "planters.plant_c(host, layout, sign if a <= 6 else -sign, a)"),
    (H, "speed-arm-slows", "joint_damping / steps.SPEED))", "joint_damping * steps.SPEED))"),
    (H, "speed-arm-at-c0-only", '("speed@c6", planters.A_RUNG, True))', '("speed@c6", 0.0, True))'),
    (H, "sign-inverted", "sign = +1.0 if table[0][1] >= table[1][1] else -1.0", "sign = -1.0 if table[0][1] >= table[1][1] else +1.0"),
    # the seasons
    (H, "food-seed-unpaired", "    sim.set_food_seed(seed)\n", "    sim.set_food_seed(seed + 1)\n"),
    # the reading
    (H, "no-per-unit-rescale", "speed[h] * 0.25 / (r[h] - 1.0)", "speed[h]"),
    (H, "r-min-ignored", "if r[h] >= steps.R_MIN]", "if True]"),
    (H, "readable-at-any-count", "readable = 2 * len(unit_hosts) >= len(hosts) and len(pu) > 1", "readable = len(pu) > 1"),
    (H, "raw-governs", "per_unit = steps.reading(pu) if readable", "per_unit = steps.reading(raw) if readable"),
    (H, "comparable-not-met", '"COMPARABLE (equivalent within +-0.10)": "MET"', '"COMPARABLE (equivalent within +-0.10)": "NOT MET"'),
    (H, "speed-step-against-c0", "speed = {h: M[h][SPEED_STEP][0] - M[h][BASE][0] for h in hosts}", "speed = {h: M[h][SPEED_STEP][0] - M[h][\"c0\"][0] for h in hosts}"),
    # the checks
    (H, "sim-hash-dropped", "    steer.assert_point_world(raw, point)\n    season = steer.point_season(point)\n    tune_draws",
     "    season = steer.point_season(point)\n    tune_draws"),
    (H, "refusal-when-short-off", "    if len(hosts) < planters.N_HOSTS:\n        say(f\"REFUSED", "    if False:\n        say(f\"REFUSED"),
]

if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), MUTANTS))
    print(f"# rbt132_steps_mutants.py: {len(MUTANTS) - 1} mutants of holistic_steps.py, against {' + '.join(NM.TESTS)}")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:28s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]} (the unmutated copy {'passes: the harness is sound' if ctrl[2] == 'SURVIVED' else 'FAILS: the harness is broken'})")
    print(f"# killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: " + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
