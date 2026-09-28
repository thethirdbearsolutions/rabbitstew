"""RBT-116 steer.py FIX-CHECK: steer_mutants.py's 16 mutants (anchors updated to the fixed tree) plus 8 aimed at the
fixes themselves, run against the fixed test file on the TRIAL-MERGED tree (PR #434 @ d276ef6 into integration 42261bd).

    python3 steer_mutants2.py TREE [WORKERS] > steer_mutants2.txt
"""
import sys
from concurrent.futures import ThreadPoolExecutor

import steer_mutants as SM

OLD = {m[0]: m for m in SM.MUTANTS}
OLD["no-clearance-redraw"] = ("no-clearance-redraw", "        if not len(live) or clear(rotate(live, th)):", "        if True:")
NEW = [
    ("clearance-root-only (S-M1 undone)", "    pts = sim._clearance_points()\n", "    pts = sim._robot_positions()\n"),
    ("surface-rule-ignored", "    if pts is _SURFACE_CLEAR:", "    if False:"),
    ("tau-guard-off (item 5)", "    if f is not None and f.smell_contrast > 0 and f.smell_tau != SMELL_TAU:", "    if False:"),
    ("tau-guard-not-called-in-season", "    cfg = replace(draw_sim(cfg, draw), opponent_proxy=True)  # run_solo's season\n    if cfg.food is None:\n        raise ValueError(\"the battery needs a food world\")\n    assert_registered_channel(cfg)\n",
     "    cfg = replace(draw_sim(cfg, draw), opponent_proxy=True)  # run_solo's season\n    if cfg.food is None:\n        raise ValueError(\"the battery needs a food world\")\n"),
    ("fingerprint-back-to-identity (S-S3 undone)", "        if fp != _COMMITTED_LAYOUT[m] or fp[:2] != (\"rabbitstew.simulation\", f\"Simulation.{m}\"):",
     "        if getattr(cls, m) is not getattr(Simulation, m):"),
    ("fingerprint-module-check-dropped", "        if fp != _COMMITTED_LAYOUT[m] or fp[:2] != (\"rabbitstew.simulation\", f\"Simulation.{m}\"):",
     "        if fp != _COMMITTED_LAYOUT[m]:"),
    ("clear_from/eat_rule-check-dropped", "    if cfg.food.clear_from not in CLEAR_FROM or cfg.food.eat_rule not in EAT_RULES:", "    if False:"),
    ("lesion-recorder-off", "            food_abs = max(food_abs, float(np.abs(brain.activation[food_units]).max()))", "            pass"),
]

if __name__ == "__main__":
    tree = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    muts = list(OLD.values()) + NEW
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: SM.run(tree, *m), muts))
    print(f"# steer_mutants2.py: {len(muts)} mutants (16 from steer_mutants.py + {len(NEW)} new) of runs/RBT-116/steer.py on the")
    print("# trial merge of #434 @ d276ef6 into 42261bd; the fixed tests/test_rbt116_steer.py")
    for name, verdict, why in res:
        print(f"{verdict:9s} {name:44s} {why}")
    print(f"# killed {sum(r[1] == 'KILLED' for r in res)} / {len(res)}")
