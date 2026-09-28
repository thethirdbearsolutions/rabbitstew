"""RBT-132: RBT-116's mutant kill-sets, re-run on the RBT-132 tree against the UNCHANGED tests/test_rbt116_steer.py.

    python runs/RBT-116/rbt132_mutants.py TREE [WORKERS] > runs/RBT-116/rbt132_mutants.txt

Two sets, as the design adversary wrote them (design-adversary/steer_mutants.py, 16; steer_mutants2.py, 24), each
mutant one textual fault in runs/RBT-116/steer.py, run in a private copy of the tree.  Anchors that moved are re-pointed
at the same fault on the current line, and each re-pointing is printed:
- steer_mutants.py's no-clearance-redraw: the draw_theta line as the FIX-CHECK re-pointed it (S-M1);
- steer_mutants2.py's surface-rule-ignored: #446's tuple branch in world_clearance (it moved before RBT-132, at 3b23095);
- steer_mutants2.py's tau-guard-off and tau-guard-not-called-in-season: RBT-132's per-point guard, which compares the
  point's registered τ (W1's 1 s by default) and is called with the point.
"""
import importlib.util
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "design-adversary"))
_argv, sys.argv = sys.argv, sys.argv[:1]
import steer_mutants as SM  # noqa: E402
spec = importlib.util.spec_from_file_location("sm2", os.path.join(HERE, "design-adversary", "steer_mutants2.py"))
SM2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SM2)
sys.argv = _argv

REPOINT = {
    "no-clearance-redraw": ("        if not len(live) or clear(rotate(live, th)):", "        if True:"),
    "surface-rule-ignored": ("    if isinstance(pts, tuple) and pts and pts[0] is _SURFACE_CLEAR:", "    if False:"),
    "tau-guard-off (item 5)": ("    if f is not None and f.smell_contrast > 0 and (f.smell_tau != tau or REGISTERED_POINTS[point][\"smell_contrast\"] <= 0):", "    if False:"),
    "tau-guard-not-called-in-season": ("    assert_registered_channel(cfg, point)\n    if condition == \"lesion\":", "    if condition == \"lesion\":"),
}


def repoint(m):
    name = m[0]
    if name in REPOINT:
        return (name,) + REPOINT[name]
    return m


if __name__ == "__main__":
    tree = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    sets = {"steer_mutants.py": [repoint(m) for m in SM.MUTANTS], "steer_mutants2.py": [repoint(m) for m in list(SM2.OLD.values()) + SM2.NEW]}
    print("# rbt132_mutants.py: RBT-116's mutant sets on the RBT-132 tree, tests/test_rbt116_steer.py unchanged")
    print("# re-pointed anchors: " + "; ".join(f"{k} -> {v[0].strip()!r}" for k, v in REPOINT.items()))
    for label, muts in sets.items():
        with ThreadPoolExecutor(w) as ex:
            res = list(ex.map(lambda m: SM.run(tree, *m), muts))
        print(f"## {label}: {len(muts)} mutants")
        for name, verdict, why in res:
            print(f"{verdict:9s} {name:44s} {why}")
        print(f"# {label}: killed {sum(r[1] == 'KILLED' for r in res)} / {len(res)}", flush=True)
