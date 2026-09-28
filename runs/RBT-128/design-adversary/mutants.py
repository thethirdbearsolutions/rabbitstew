"""RBT-128 design adversary: do the new tests fail on a broken implementation?

    python runs/RBT-128/design-adversary/mutants.py <a checkout of the PR> > runs/RBT-128/design-adversary/mutants.txt

Each mutant is one textual replacement in rabbitstew/fair.py, cli.py or evolution.py of the checkout given.  For each,
tests/test_rbt128.py and the four edited CLI tests are run (PYTHONPATH = the checkout); a mutant is KILLED when at
least one test fails.  The file is restored after each.
"""
import os
import subprocess
import sys

TESTS = ["tests/test_rbt128.py", "tests/test_cli.py", "tests/test_morph_protection.py::test_config_round_trip_and_cli_flag",
         "tests/test_rbt126.py", "tests/test_rbt130.py"]
MUTANTS = [
    ("fair.py", 'ball_cone", math.pi / 2, f"--ball-cone', 'ball_cone", math.pi / 3, f"--ball-cone', "cone pi/2 -> pi/3"),
    ("fair.py", '("settle_max", 10.0, "--settle-max 10"),\n', '', "settle_max dropped from the preset"),
    ("fair.py", '    if fair and unfair:\n        raise', '    if False:\n        raise', "--fair with --unfair-i-know accepted"),
    ("fair.py", 'if got != _UNSET[dest] and got != value:', 'if False:', "a conflicting explicit value silently overridden"),
    ("fair.py", 'if got != _UNSET[dest] and got != value:', 'if got != _UNSET[dest]:', "a matching explicit value refused"),
    ("fair.py", '        setattr(args, dest, value)\n', '', "--fair marks the run but sets no value"),
    ("fair.py", '    if not mixed or marker:\n', '    if True:\n', "guard never fires"),
    ("fair.py", '    if not mixed or marker:\n', '    if not mixed or marker == "fair":\n', "guard refuses --unfair-i-know"),
    ("fair.py", '    return body_plan(genotype) in _DESIGNED_PLANS', '    return False', "is_designed always False (simulate never guarded)"),
    ("fair.py", '    return body_plan(genotype) in _DESIGNED_PLANS', '    return True', "is_designed always True"),
    ("fair.py", 'print(f"warning: {command}', 'pass  # print(f"warning: {command}', "bypass warning dropped"),
    ("fair.py", '    print(f"--fair expands to:', '    return\n    print(f"--fair expands to:', "expansion not printed"),
    ("fair.py", '    args._fair_expanded = True\n', '', "expand not idempotent (double expansion)"),
    ("cli.py", 'fairness="fair" if marker == "fair" else "",\n        population_size=args.capacity', 'fairness="",\n        population_size=args.capacity', "ecology writes no fairness marker"),
    ("cli.py", 'fairness="fair" if marker == "fair" else "",\n        population_size=args.population', 'fairness=marker,\n        population_size=args.population', "evolve writes fairness=\"unfair\" under the bypass"),
    ("cli.py", 'mixed=getattr(args, "only_fauna", None) is None)', 'mixed=True)', "ecology --only-fauna guarded"),
    ("cli.py", 'fair_mod.guard("ecology", marker,', 'fair_mod.guard("ecology", "fair",', "ecology never guarded"),
    ("cli.py", 'mixed=len(kinds) > 1)', 'mixed=len(genotypes) > 1)', "simulate: every two-robot bout guarded"),
    ("cli.py", '    marker = fair_mod.expand(args)\n    fair_mod.guard("evolve"', '    marker = fair_mod.expand(args)\n    if marker == "fair":\n        args.ball_cone = 0.0\n    fair_mod.guard("evolve"', "evolve --fair drops the cone after expansion"),
    ("evolution.py", '        if not d["fairness"]:\n            del d["fairness"]', '        if False:\n            del d["fairness"]', "empty fairness written to config.json"),
]


def main():
    root = sys.argv[1]
    env = dict(os.environ, PYTHONPATH=root)
    killed = 0
    for fname, old, new, label in MUTANTS:
        path = os.path.join(root, "rabbitstew", fname)
        src = open(path).read()
        assert src.count(old) == 1, (label, src.count(old))
        open(path, "w").write(src.replace(old, new))
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *TESTS], cwd=root, env=env,
                               capture_output=True, text=True)
        finally:
            open(path, "w").write(src)
        failed = [l.split(" ")[1] for l in r.stdout.splitlines() if l.startswith("FAILED")]
        k = r.returncode != 0
        killed += k
        print(f"{'KILLED ' if k else 'SURVIVED'} {label:55s} {failed[0] if failed else ''}", flush=True)
    print(f"# {killed} of {len(MUTANTS)} mutants killed")


if __name__ == "__main__":
    main()
