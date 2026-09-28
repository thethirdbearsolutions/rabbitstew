"""RBT-132 gate check of #478: mutants of the proposed screen rule (``admissible``, ``SCREEN_ANY``,
``screen_dispersion``, ``planters.screen_line``) with rbt132_new_mutants.py's harness, against tests/test_rbt132.py +
tests/test_rbt116_steer.py.

    python runs/RBT-116/design-adversary/rbt132_478_mutants.py TREE [WORKERS] > runs/RBT-116/design-adversary/rbt132_478_mutants.txt
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rbt132_new_mutants as NM  # noqa: E402

S, P = NM.S, NM.P
MUTANTS = [
    NM.MUTANTS[0],
    (S, "W1-in-SCREEN_ANY", "SCREEN_ANY = frozenset(RBT129_POINTS)", 'SCREEN_ANY = frozenset(RBT129_POINTS) | {"W1"}'),
    (S, "SCREEN_ANY-empty", "SCREEN_ANY = frozenset(RBT129_POINTS)", "SCREEN_ANY = frozenset()"),
    (S, "any-needs-two", "return ate >= 1 if world in SCREEN_ANY else 2 * ate >= hosts", "return ate >= 2 if world in SCREEN_ANY else 2 * ate >= hosts"),
    (S, "half-strict", "return ate >= 1 if world in SCREEN_ANY else 2 * ate >= hosts", "return ate >= 1 if world in SCREEN_ANY else 2 * ate > hosts"),
    (S, "screen-rule-ignores-world", '"admissible": admissible(int(ate), len(hosts), world)})', '"admissible": admissible(int(ate), len(hosts))})'),
    (S, "dispersion-ddof0", "ate.var(ddof=1) / vb", "ate.var() / vb"),
    (S, "dispersion-half-strict", '"half": int((2 * ate >= n).sum())', '"half": int((2 * ate > n).sum())'),
    (S, "dispersion-any-counts-zero", '"any": int((ate >= 1).sum())', '"any": int((ate >= 0).sum())'),
    (P, "screen-line-wrong-rule-label", 'rule = ">= 1 control eats" if point in steer.SCREEN_ANY else ">= half the controls eat"',
     'rule = ">= half the controls eat"'),
    (P, "pays-screen-line-dropped", "    screen = steer.screen_draws(plants, cfg, point, season)\n    say(screen_line(screen, point))\n",
     "    screen = steer.screen_draws(plants, cfg, point, season)\n"),
]

if __name__ == "__main__":
    tree = os.path.abspath(sys.argv[1])
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    with ThreadPoolExecutor(w) as ex:
        res = list(ex.map(lambda m: (m[0],) + NM.run(tree, *m), MUTANTS))
    print(f"# rbt132_478_mutants.py: {len(MUTANTS) - 1} mutants of #478's screen rule, against {' + '.join(NM.TESTS)}")
    for path, name, verdict, why in res:
        print(f"{verdict:9s} {os.path.basename(path):17s} {name:32s} {why}")
    ctrl, rest = res[0], res[1:]
    print(f"# control: {ctrl[2]}; killed {sum(r[2] == 'KILLED' for r in rest)} / {len(rest)}; survivors: "
          + (", ".join(r[1] for r in rest if r[2] != "KILLED") or "none"))
