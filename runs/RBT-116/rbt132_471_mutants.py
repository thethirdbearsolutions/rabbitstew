"""RBT-132, #471's ruling: mutants of M1 (per-point counts, the pool rule, the cost line), S1 (report per cell), S2 (the
calibration's second stage), N1 (the veto projected) and N2 (refusals), plus the projection check's 21 mutants
(``design-adversary/rbt132_projection_mutants.py``: the implementer's 12 and the adversary's 9), re-pointed where #471's
changes moved their anchors.  The design adversary's harness is used unchanged (``rbt132_new_mutants.run``: a
hard-linked private copy per mutant, ``pytest -x`` on tests/test_rbt132.py and tests/test_rbt116_steer.py).

    python runs/RBT-116/rbt132_471_mutants.py TREE [WORKERS] > runs/RBT-116/rbt132_471_mutants.txt
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "design-adversary"))
sys.path.insert(0, HERE)
import rbt132_new_mutants as NM  # noqa: E402
import rbt132_projection_mutants as PM  # noqa: E402  (imports rbt132_fix_mutants for PROJ)

S, P, Q, K = NM.S, NM.P, NM.Q, PM.K
#: the projection check's mutants whose anchors #471's changes moved: the same fault on its new line
REPOINT = {
    "proj-seen-not-squared (item 2)": (K, "    return (p_c2(mu, sd, n) * p_c3(q, n)) ** 2", "    return p_c2(mu, sd, n) * p_c3(q, n)"),
    "proj-veto-ignored (item 2)": (K, "    return (p_c2(mu, sd, n) * p_c3(q, n)) ** 2", "    return p_c2(mu, sd, n) ** 2"),
    "proj-stage1-stop-dropped (item 2)": (K, "kinds[k] += [_plant(rec, pooled) for rec in calls.get(k, [])]",
                                          "kinds[k] += [_plant(rec, pooled) for rec in calls.get(k, []) if rec.get(\"stage2\")]"),
    "veto-from-record-ignored": (K, "    return (s2[\"dT\"], sd_from_stats(s2), s2[\"differ\"] / s2[\"n\"], refused)",
                                 "    return (s2[\"dT\"], sd_from_stats(s2), 1.0, refused)"),
    "report-projects-pooled-cells": (K, "    per_cell = {p: from_planted([p], pooled) for p in paths}",
                                     "    per_cell = {p: from_planted(paths, pooled) for p in paths}"),
    "stage1-stop-projected-at-null": (K, "        return (0.0, 1.0, 0.0, refused)\n    return (s2[\"dT\"]",
                                      "        return (0.0, 1.0, 1.0, refused)\n    return (s2[\"dT\"]"),
}
NEW = [
    # M1(a), (c): per-point sizes and the pool rule
    (S, "raised-pool-not-ruled (M1c)", "    pool = -(-need * 64 // 36)", "    pool = 2 * need"),
    (S, "raised-extension-registered (M1c)", '"pool": pool, "extension": -(-pool // 2)}', '"pool": pool, "extension": 32}'),
    (S, "W1-raisable (M1a)", 'return sizes_at(N_STAGE2 if world == "W1" else RAISED_N.get(world, N_STAGE2))',
     "return sizes_at(RAISED_N.get(world, N_STAGE2))"),
    (S, "pool-registered-size (M1a)", '    n = size["pool"] + (size["extension"] if extended else 0)',
     "    n = POOL_SIZE + (POOL_EXTENSION if extended else 0)"),
    (S, "assign-at-W1 (M1a)", "    z = battery_size(world)\n    if len(a) < z[\"battery\"]:", "    z = battery_size(\"W1\")\n    if len(a) < z[\"battery\"]:"),
    (S, "screen-assigns-at-W1 (M1a)", "    battery = assign_battery(adm, world)", "    battery = assign_battery(adm)"),
    (S, "screen-threshold-registered (M1a)", '    if sum(r["admissible"] for r in table) < size["battery"]:',
     "    if sum(r[\"admissible\"] for r in table) < N_BATTERY:"),
    (S, "screen-extension-registered (M1a)", '        table += run(draw_pool(world, extended=True)[size["pool"]:])',
     "        table += run(draw_pool(world, extended=True)[POOL_SIZE:])"),
    # M1(b): plants and members at the same counts
    (Q, "probe-battery-unchecked (M1b)", "    steer.assert_battery_size(bat, point)  # #471 M1(b)", "    pass  # #471 M1(b)"),
    (P, "planted-battery-unchecked (M1b)", '    steer.assert_battery_size(screen["battery"], point)\n', ""),
    (P, "pays-battery-unchecked (M1b)", '    bat = screen["battery"]\n    steer.assert_battery_size(bat, point)\n', '    bat = screen["battery"]\n'),
    # M1(d): the cost line
    (K, "cost-without-confirmation (M1d)", "    per_call = 2 * steer.N_STAGE1 + 4 * n + 2 * n", "    per_call = 2 * steer.N_STAGE1 + 4 * n"),
    (K, "cost-not-printed (M1d)", "        lines.append(f\"COST at n {n}:", "        (f\"COST at n {n}:"),
    # S2: the calibration's second stage
    (P, "calibration-flag-ignored (S2)", '(calibration or (s2.get("c2") and s2.get("c3")))', '(s2.get("c2") and s2.get("c3"))'),
    (P, "calibration-anywhere (S2)", "    if calibration and point not in CALIBRATION_CELLS:", "    if False:"),
    (P, "calibration-flag-not-passed (S2)", "return planted(a.point, a.config, a.out, a.hosts, a.workers, a.calibration)",
     "return planted(a.point, a.config, a.out, a.hosts, a.workers)"),
    (K, "pooled-sd-within-only (S2)", " + n1 * (m1 - m) ** 2 + n2 * (m2 - m) ** 2", ""),
    (K, "pooled-stage2-only (S2)", "        parts = [x for x in (s2, conf) if", "        parts = [x for x in (s2,) if"),
    (K, "pooled-missing-confirmation-allowed (S2)", "        if conf is None:\n            raise", "        if False:\n            raise"),
    # N1: the veto projected from differ
    (K, "c3-at-half (N1)", "for k in range(n // 2 + 1, n + 1)", "for k in range(n // 2, n + 1)"),
    (K, "veto-inside-once (N1)", "    return (p_c2(mu, sd, n) * p_c3(q, n)) ** 2", "    return p_c2(mu, sd, n) ** 2 * p_c3(q, n)"),
    (K, "q-from-the-c3-bool (N1)", "    return (s2[\"dT\"], sd_from_stats(s2), s2[\"differ\"] / s2[\"n\"], refused)",
     "    return (s2[\"dT\"], sd_from_stats(s2), float(s2.get(\"c3\", True)), refused)"),
    # N2: refusals
    (K, "refusals-not-read (N2)", '    refused = int(rec.get("theta_refused", 0))', "    refused = 0"),
    (K, "refusals-not-printed (N2)", ' veto {pl[2]:.2f} refused {pl[3]}"', ' veto {pl[2]:.2f}"'),
]


def repoint(m):
    path, name, old, new = m
    return (REPOINT[name][0], name, REPOINT[name][1], REPOINT[name][2]) if name in REPOINT else m


if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    muts = [NM.MUTANTS[0]] + [repoint(m) for m in PM.FM.PROJ + PM.MORE] + NEW
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), muts))
    print(f"# rbt132_471_mutants.py: the projection check's {len(PM.FM.PROJ) + len(PM.MORE)} (re-pointed where #471 moved "
          f"them) + {len(NEW)} new, against {' + '.join(NM.TESTS)}")
    print("# re-pointed: " + "; ".join(REPOINT))
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:44s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]} (the unmutated copy {'passes: the harness is sound' if ctrl[2] == 'SURVIVED' else 'FAILS: the harness is broken'})")
    print(f"# killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: " + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
