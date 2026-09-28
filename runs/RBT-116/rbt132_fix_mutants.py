"""RBT-132 fix-check support: the design adversary's mutants of RBT-132's code (design-adversary/rbt132_new_mutants.py),
re-run on the fixed tree, plus mutants aimed at the code the 07:10 ruling added.

    python runs/RBT-116/rbt132_fix_mutants.py TREE [WORKERS] > runs/RBT-116/rbt132_fix_mutants.txt

The adversary's harness (``run``: a hard-linked private copy per mutant, ``pytest -x`` on tests/test_rbt132.py and
tests/test_rbt116_steer.py) is used unchanged.  An anchor that the fixes moved is re-pointed at the same fault on its
new line, and every re-pointing is printed.  Fixture tests only.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "design-adversary"))
import rbt132_new_mutants as NM  # noqa: E402
import rbt132_fixcheck_mutants as FC  # noqa: E402  (the fix-check's 17 further mutants, run unchanged)

S, P, Q = NM.S, NM.P, NM.Q
K = "runs/RBT-116/k3_projection.py"
REPOINT = {
    "k3-lbdT-ignored": (P, 'return bool(s2.get("c3") and s2.get("c2") and conf.get("c3") and conf.get("c2"))',
                        'return bool(s2.get("c3") and conf.get("c3") and conf.get("c2"))'),
    "k3-veto-ignored": (P, 'return bool(s2.get("c3") and s2.get("c2") and conf.get("c3") and conf.get("c2"))',
                        'return bool(s2.get("c2") and conf.get("c3") and conf.get("c2"))'),
    "planted-calls-at-W1": (P, "rec = steer.call_genome(gd, cfg, bat, steer.point_season(point))", "rec = steer.call_genome(gd, cfg, bat)"),
    "planted-fair-check-dropped": (P, "    steer.assert_fair_config(raw, point)\n    steer.assert_point_world(raw, point)\n    season = steer.point_season(point)\n    pool =",
                                   "    steer.assert_point_world(raw, point)\n    season = steer.point_season(point)\n    pool ="),
    "compass-probes-need-not-agree": (P, "else backs\n    if backs[0] is None or backs[0] != backs[1]:", "else backs\n    if backs[0] is None:"),
    "power-line-legacy-everywhere": (P, '    if steer.REGISTERED_POINTS[point]["smell_contrast"] > 0:\n        return "# power at this point: " + probe_power.line',
                                     '    if False:\n        return "# power at this point: " + probe_power.line'),
    "missing-below-1": (Q, "if len(alive) < N_MIN:", "if len(alive) < 1:"),
    "probe-at-W1": (Q, "    season = cached(steer.point_season(point))\n    f = [", "    season = cached(steer.run_season)\n    f = ["),
    "probe-fair-check-dropped": (Q, "    steer.assert_fair_config(raw, point)\n    steer.assert_point_world(raw, point)\n    bat =",
                                 "    steer.assert_point_world(raw, point)\n    bat ="),
}
NEW = [
    (S, "sim-hash-check-off (S1)", "        if got != POINT_SIM_HASH[point]:", "        if False:"),
    (S, "cli-sim-hash-check-dropped (S1)", "    assert_point_world(raw, a.world)\n", ""),
    (P, "planted-sim-hash-check-dropped (S1)", "    steer.assert_fair_config(raw, point)\n    steer.assert_point_world(raw, point)\n    season = steer.point_season(point)\n    pool =",
     "    steer.assert_fair_config(raw, point)\n    season = steer.point_season(point)\n    pool ="),
    (Q, "probe-sim-hash-check-dropped (S1)", "    steer.assert_fair_config(raw, point)\n    steer.assert_point_world(raw, point)\n    bat =",
     "    steer.assert_fair_config(raw, point)\n    bat ="),
    (P, "k3-confirmation-ignored (item 1)", 'return bool(s2.get("c3") and s2.get("c2") and conf.get("c3") and conf.get("c2"))',
     'return bool(s2.get("c3") and s2.get("c2"))'),
    (P, "k3-confirmation-not-run (item 1)", 'if k3 and "confirm" not in rec and s2.get("c2") and s2.get("c3"):', "if False:"),
    (P, "b-brake-speeds-up (item 5)", "return +1.0 if backward else -1.0", "return -1.0 if backward else +1.0"),
    (P, "c-gain-not-split (item 4)", "    w = a / len(links)", "    w = a"),
    (Q, "season-check-dropped (S2)", "    check_season(run, season)\n", ""),
    (Q, "extinct-ignored (S2)", "    if extinct(run):", "    if False:"),
    (P, "pays-bound-is-the-mean (S7c)", "(float(np.mean(Fs)), steer.lower_bound(Fs)) if Fs", "(float(np.mean(Fs)), float(np.mean(Fs))) if Fs"),
    (P, "pays-at-W1 (S7c)", "    runs, refused = steer._pairs(gd, cfg, bat.stage2, steer.point_season(point))", "    runs, refused = steer._pairs(gd, cfg, bat.stage2, steer.run_season)"),
    (Q, "f-not-shared (NIT)", "    season = cached(steer.point_season(point))\n    f = [", "    season = steer.point_season(point)\n    f = ["),
]
#: the fix-check ruling's item 2: the K3 projection
PROJ = [
    (K, "proj-seen-not-squared (item 2)", "return p_c2(mu, sd, n) ** 2 if veto else 0.0", "return p_c2(mu, sd, n) if veto else 0.0"),
    (K, "proj-z-bound-not-t (item 2)", "    t = steer.t_quantile(0.95, df)", "    t = 1.6449"),
    (K, "proj-veto-ignored (item 2)", "return p_c2(mu, sd, n) ** 2 if veto else 0.0", "return p_c2(mu, sd, n) ** 2"),
    (K, "proj-one-kind-enough (item 2)", "if all(s >= target for s in shares[n].values())", "if any(s >= target for s in shares[n].values())"),
    (P, "proj-sd-no-sqrt-n (item 2)", "return (s2[\"dT\"] - s2[\"lbdT\"]) * math.sqrt(n) / steer.t_quantile(0.95, n - 1)",
     "return (s2[\"dT\"] - s2[\"lbdT\"]) / steer.t_quantile(0.95, n - 1)"),
    (K, "proj-stage1-stop-dropped (item 2)", "                    kinds[k].append((0.0, 1.0, False))", "                    pass"),
    (K, "proj-measured-bar-one-kind (item 2)", "all(n and s / n >= MEASURED_BAR for kinds in cells.values() for s, n in kinds.values())",
     "all(any(n and s / n >= MEASURED_BAR for s, n in kinds.values()) for kinds in cells.values())"),
    (K, "proj-measured-bar-one-cell (item 2)", "all(n and s / n >= MEASURED_BAR for kinds in cells.values() for s, n in kinds.values())",
     "any(all(n and s / n >= MEASURED_BAR for s, n in kinds.values()) for kinds in cells.values())"),
    (K, "proj-measured-not-seen (item 2)", "(sum(int(planters.seen(r)) for r in", "(sum(int(r.get(\"call\") == steer.STEERS) for r in"),
    (K, "proj-rule-smallest-cell (item 2)", "    return max(picks)", "    return min(picks)"),
    (K, "proj-rule-unreadable-cell-ignored (item 2)", "    if not picks or UNREADABLE in picks:", "    if not picks:"),
    (P, "k3-line-no-sd (item 2)", "sd {dT_sd(s2):.4f} over", "sd {0.0:.4f} over"),
]


def repoint(m):
    path, name, old, new = m
    if name in REPOINT:
        return REPOINT[name][0], name, REPOINT[name][1], REPOINT[name][2]
    return m


if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    muts = [repoint(m) for m in NM.MUTANTS] + NEW + FC.MUTANTS[1:] + PROJ
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), muts))
    print(f"# rbt132_fix_mutants.py: {len(NM.MUTANTS)} adversary mutants (re-pointed where the fixes moved them) + {len(NEW)} new "
          f"+ the fix-check's {len(FC.MUTANTS) - 1} (rbt132_fixcheck_mutants.py, unchanged) + {len(PROJ)} on k3_projection.py, "
          f"against {' + '.join(NM.TESTS)}")
    print("# re-pointed: " + "; ".join(REPOINT))
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:40s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]} (the unmutated copy {'passes: the harness is sound' if ctrl[2] == 'SURVIVED' else 'FAILS: the harness is broken'})")
    print(f"# killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: " + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
