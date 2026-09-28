"""RBT-132 fix-check: re-run, independently, the implementer's 9 re-pointed anchors and 13 new mutants
(runs/RBT-116/rbt132_fix_mutants.py) with this directory's harness (rbt132_new_mutants.run), plus the control.

    python runs/RBT-116/design-adversary/rbt132_fix_mutants_rerun.py TREE [WORKERS] > runs/RBT-116/design-adversary/rbt132_fix_mutants_rerun.txt
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import rbt132_new_mutants as NM  # noqa: E402
import rbt132_fix_mutants as FM  # noqa: E402

if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    muts = [NM.MUTANTS[0]] + [FM.repoint(m) for m in NM.MUTANTS if m[1] in FM.REPOINT] + FM.NEW
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), muts))
    print(f"# rbt132_fix_mutants_rerun.py: the implementer's {len(FM.REPOINT)} re-pointed + {len(FM.NEW)} new mutants, re-run")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:40s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]}; killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: "
          + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
