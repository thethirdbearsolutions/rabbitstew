"""RBT-132 projection check: the implementer's 12 mutants on the K3 projection (rbt132_fix_mutants.PROJ), re-run
independently, plus further faults in k3_projection.py and planters.dT_sd, against tests/test_rbt132.py +
tests/test_rbt116_steer.py with rbt132_new_mutants.py's harness (control included).

    python runs/RBT-116/design-adversary/rbt132_projection_mutants.py TREE [WORKERS] > runs/RBT-116/design-adversary/rbt132_projection_mutants.txt
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import rbt132_new_mutants as NM  # noqa: E402
import rbt132_fix_mutants as FM  # noqa: E402

K, P = FM.K, NM.P
MORE = [
    (K, "target-0.5", "TARGET = 0.6", "TARGET = 0.5"),
    (K, "cap-128", "COUNTS = (16, 32, 64)", "COUNTS = (16, 32, 64, 128)"),
    (K, "veto-from-record-ignored", "kinds[k].append((s2[\"dT\"], sd_from_stats(s2), bool(s2[\"c3\"])))", "kinds[k].append((s2[\"dT\"], sd_from_stats(s2), True))"),
    (K, "rule-takes-first-cell", "    return max(picks)", "    return picks[0]"),
    (K, "quadrature-grid-21", "def p_c2(mu: float, sd: float, n: int, grid: int = 4001)", "def p_c2(mu: float, sd: float, n: int, grid: int = 21)"),
    (K, "chi2-range-truncated", "    hi = df + 40.0 * math.sqrt(2.0 * df) + 40.0", "    hi = float(df)"),
    (K, "report-projects-pooled-cells", "    per_cell = {p: from_planted([p]) for p in paths}", "    per_cell = {p: from_planted(paths) for p in paths}"),
    (P, "dT_sd-sqrt-n-minus-1", "return (s2[\"dT\"] - s2[\"lbdT\"]) * math.sqrt(n) / steer.t_quantile(0.95, n - 1)",
     "return (s2[\"dT\"] - s2[\"lbdT\"]) * math.sqrt(n - 1) / steer.t_quantile(0.95, n - 1)"),
    (K, "stage1-stop-projected-at-null", "                    kinds[k].append((0.0, 1.0, False))", "                    kinds[k].append((0.0, 1.0, True))"),
]

if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    muts = [NM.MUTANTS[0]] + FM.PROJ + MORE
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), muts))
    print(f"# rbt132_projection_mutants.py: the implementer's {len(FM.PROJ)} projection mutants + {len(MORE)} further")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:42s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]}; killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: "
          + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
