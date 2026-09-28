"""RBT-132 fix-check: further mutants of the code the 07:10 fixes added, beyond rbt132_fix_mutants.py's 13, against the
same tests (tests/test_rbt132.py + tests/test_rbt116_steer.py), with rbt132_new_mutants.py's harness unchanged.

    python runs/RBT-116/design-adversary/rbt132_fixcheck_mutants.py TREE [WORKERS] > runs/RBT-116/design-adversary/rbt132_fixcheck_mutants.txt

Each is a plausible one-line fault in the ruled code that the implementer's set does not aim at.  Fixture tests only.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rbt132_new_mutants as NM  # noqa: E402

S, P, Q = NM.S, NM.P, NM.Q
MUTANTS = [
    (S, "CONTROL (no fault: must SURVIVE)", "N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM", "N_BATTERY = N_STAGE1 + N_STAGE2 + N_CONFIRM"),
    # S2: the season and EXTINCT
    (Q, "last-season-off-by-one", "return max(int(e[\"season\"]) for e in h) + 1 if h else 0", "return max(int(e[\"season\"]) for e in h) if h else 0"),
    (Q, "extinct-only-beside-S (not the unit)", "for d in (run, os.path.dirname(os.path.abspath(run))))", "for d in (run,))"),
    (Q, "extinct-only-in-unit (not beside S)", "for d in (run, os.path.dirname(os.path.abspath(run))))", "for d in (os.path.dirname(os.path.abspath(run)),))"),
    (Q, "season-any-nonzero", "if season != 0 and season != last_season(run):", "if season != 0 and season < 0:"),
    # f sharing: the cache must key on the condition and the draw
    (Q, "cache-ignores-condition", "key = (draw.terrain_seed, draw.start_seed, cond)", "key = (draw.terrain_seed, draw.start_seed)"),
    (Q, "cache-ignores-terrain", "key = (draw.terrain_seed, draw.start_seed, cond)", "key = (draw.start_seed, cond)"),
    # K3 SEEN
    (P, "seen-ignores-calls-own-confirm", 'conf = rec.get("confirm") or rec.get("k3_confirm") or {}', 'conf = rec.get("k3_confirm") or {}'),
    (P, "seen-confirm-c3-only", 'and conf.get("c3") and conf.get("c2"))', 'and conf.get("c3"))'),
    (P, "k3-confirm-for-b-too", 'point, key in ("a", "c")) for key, g in tasks]', 'point, True) for key, g in tasks]'),
    (P, "k3-confirm-min-usable-dropped", "        if len(runs[\"intact\"]) >= steer.MIN_USABLE:\n            rec[\"k3_confirm\"]", "        if True:\n            rec[\"k3_confirm\"]"),
    # G8(b), G8(c)
    (P, "b-sign-from-second-probe", "sB = slowing_sign(backs[0])", "sB = slowing_sign(backs[1] if backs[1] is not None else backs[0])"),
    (P, "c-split-over-effector-nodes-not-links", "    w = a / len(links)", "    w = a / len({nd for nd, _, _ in links})"),
    # holistic PAYS F leg
    (P, "pays-refusal-when-short-off", "    if len(plants) < N_HOSTS:\n        say(f\"REFUSED: {len(plants)} hosts carry G8(c)", "    if False:\n        say(f\"REFUSED: {len(plants)} hosts carry G8(c)"),
    (P, "pays-F-on-confirm-draws", "steer._pairs(gd, cfg, bat.stage2, steer.point_season(point))", "steer._pairs(gd, cfg, bat.confirm, steer.point_season(point))"),
    (P, "pays-gate-failure-ignored", "    if not screen[\"passed\"]:\n        say(f\"GATE FAILED at {point}: {screen['admissible']} admissible draws\")\n        return 8",
     "    if False:\n        say(f\"GATE FAILED at {point}: {screen['admissible']} admissible draws\")\n        return 8"),
    (P, "pays-sim-hash-dropped", "    steer.assert_point_world(raw, point)\n    season = steer.point_season(point)\n    tune_draws",
     "    season = steer.point_season(point)\n    tune_draws"),
    # S1
    (S, "hash-ignores-key-order", 'json.dumps(sim, sort_keys=True, separators=(",", ":"))', 'json.dumps(sim, separators=(",", ":"))'),
]

if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), MUTANTS))
    print(f"# rbt132_fixcheck_mutants.py: {len(MUTANTS) - 1} further mutants of the ruled code, against {' + '.join(NM.TESTS)}")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:42s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]} (the unmutated copy {'passes: the harness is sound' if ctrl[2] == 'SURVIVED' else 'FAILS: the harness is broken'})")
    print(f"# killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: " + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
