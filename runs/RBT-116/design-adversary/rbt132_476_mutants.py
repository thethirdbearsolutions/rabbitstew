"""RBT-132 fix-check of #476: further mutants of the code #476 adds (per-point battery sizes, the calibration flag, the
pooled projection, the cost line), beyond the implementer's rbt132_471_mutants.py, with rbt132_new_mutants.py's harness.

    python runs/RBT-116/design-adversary/rbt132_476_mutants.py TREE [WORKERS] > runs/RBT-116/design-adversary/rbt132_476_mutants.txt
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rbt132_new_mutants as NM  # noqa: E402

S, P, Q = NM.S, NM.P, NM.Q
K = "runs/RBT-116/k3_projection.py"
MUTANTS = [
    NM.MUTANTS[0],
    (S, "battery-check-stage2-only", "    if got != (z[\"stage1\"], z[\"stage2\"], z[\"confirm\"]):", "    if got[1] != z[\"stage2\"]:"),
    (S, "extension-floor-not-ceil", '"pool": pool, "extension": -(-pool // 2)}', '"pool": pool, "extension": pool // 2}'),
    (S, "pool-ratio-floor", "    pool = -(-need * 64 // 36)", "    pool = need * 64 // 36"),
    (K, "second-stage-only-when-unreadable", "        if not pooled and c in (64, UNREADABLE):", "        if not pooled and c == UNREADABLE:"),
    (K, "cost-screen-unextended", '    z_ext = z["pool"] + z["extension"]', '    z_ext = z["pool"]'),
    (K, "pooled-differ-stage2-only", '"differ": a["differ"] + b["differ"]}', '"differ": a["differ"]}'),
    (K, "pooled-mean-unweighted", "    m = (n1 * m1 + n2 * m2) / n", "    m = (m1 + m2) / 2"),
    (P, "calibration-cells-wrong", 'CALIBRATION_CELLS = ("c0-p030-PW-G", "c0-p030-HP-G")', 'CALIBRATION_CELLS = ("c0-p030-PW-G", "c1-p030-PW-G")'),
    (K, "cost-members-one-season", 'PROBE = {"points": 4, "seeds": 4, "seasons": 2,', 'PROBE = {"points": 4, "seeds": 4, "seasons": 1,'),
]

if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), MUTANTS))
    print(f"# rbt132_476_mutants.py: {len(MUTANTS) - 1} further mutants of #476's code, against {' + '.join(NM.TESTS)}")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:36s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]}; killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: "
          + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
