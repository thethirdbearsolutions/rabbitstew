"""RBT-116 steer.py design adversary: can the planted positives and negatives (tests/test_rbt116_steer.py) fail?

Mutation test.  Each mutant is one textual fault in runs/RBT-116/steer.py (PR #434 @ e703f4a); the whole test file is
run against it in a private copy of the tree.  KILLED = some test failed (the suite can see this fault); SURVIVED = all
24 passed (a fault the suite cannot see).  Fixture worlds only (the tests' own); no W1, no RBT-116 host.

    python3 steer_mutants.py TREE [WORKERS] > steer_mutants.txt      (TREE: a checkout of results/RBT-116-steer)
"""
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

MUTANTS = [
    ("decoy-is-intact", "        sim._rot = theta\n", "        sim._rot = None\n"),
    ("decoy-rotates-legacy-only", "    def _log_smell(self, point, sources):\n        return Simulation._log_smell(self, point, self._rotated(sources))\n", ""),
    ("no-clearance-redraw", "        if not len(live) or float(np.linalg.norm(rotate(live, th) - root_xy, axis=1).min()) >= clearance:", "        if True:"),
    ("theta-near-identity-allowed", "THETA_LO_DEG, THETA_HI_DEG = 30.0, 330.0", "THETA_LO_DEG, THETA_HI_DEG = 0.0, 360.0"),
    ("veto-off", '    out["c3"] = bool(2 * differ > len(I))', '    out["c3"] = True'),
    ("veto-at-half", '    out["c3"] = bool(2 * differ > len(I))', '    out["c3"] = bool(2 * differ >= len(I))'),
    ("veto-is-food-count (r3's M1 bug back)", "    differ = sum(trajectories_differ(a, b) for a, b in zip(I, D))", "    differ = sum(a.food != b.food for a, b in zip(I, D))"),
    ("no-confirmation", '    if c["passes"]:\n        rec["call"] = STEERS', '    if True:\n        rec["call"] = STEERS'),
    ("stage1-stops-on-any-identical", "    if all(same):", "    if any(same):"),
    ("smell-use-inverted", 'SMELL_USE if (s2["c1"] and s2["c3"] and not s2["c2"])', 'SMELL_USE if (s2["c1"] and s2["c3"] and s2["c2"])'),
    ("decoy-on-its-own-speed-bar", "        t_b, f_b, e_b = chemotaxis_index(b, vm)", "        t_b, f_b, e_b = chemotaxis_index(b, b.v_min())"),
    ("T-against-decoy-field", "        gdir = _unit_gradient(com, _live_items(sim), cfg.food.decay)",
     "        gdir = _unit_gradient(com, rotate(_live_items(sim), theta) if theta is not None else _live_items(sim), cfg.food.decay)"),
    ("lesion-not-applied", "        cfg = replace(cfg, food=replace(cfg.food, smell_lesion=True))", "        pass"),
    ("motors-off-not-applied", "        sim.brains[0].effector_output = lambda *a: 0.0", "        pass"),
    ("lower-bound-uses-z", "    return float(x.mean() - t_quantile(0.95, len(x) - 1) * sd / math.sqrt(len(x)))", "    return float(x.mean() - 1.645 * sd / math.sqrt(len(x)))"),
    ("F_MIN-halved", "F_MIN = 0.25  #", "F_MIN = 0.125  #"),
]


def run(tree, name, old, new):
    src = open(os.path.join(tree, "runs/RBT-116/steer.py")).read()
    if src.count(old) != 1:
        return name, "BAD-MUTANT (anchor not unique)", ""
    tmp = tempfile.mkdtemp(prefix="mut-")
    for p in ("rabbitstew", "tests", "runs/RBT-116"):
        shutil.copytree(os.path.join(tree, p), os.path.join(tmp, p))
    for f in ("pyproject.toml",):
        shutil.copy(os.path.join(tree, f), tmp)
    open(os.path.join(tmp, "runs/RBT-116/steer.py"), "w").write(src.replace(old, new))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/test_rbt116_steer.py"],
                       cwd=tmp, capture_output=True, text=True, timeout=1800)
    shutil.rmtree(tmp, ignore_errors=True)
    failed = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
    return name, ("KILLED" if r.returncode else "SURVIVED"), (failed[0].split(" - ")[0] if failed else r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    tree = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: run(tree, *m), MUTANTS))
    print(f"# steer_mutants.py: {len(MUTANTS)} mutants of runs/RBT-116/steer.py @ e703f4a, tests/test_rbt116_steer.py (24 tests)")
    for name, verdict, why in res:
        print(f"{verdict:9s} {name:40s} {why}")
    print(f"# killed {sum(r[1] == 'KILLED' for r in res)} / {len(res)}")
