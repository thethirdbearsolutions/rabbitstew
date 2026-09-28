"""RBT-128 FIX-CHECK: do the tests at f8f903e fail on a broken implementation of the fixes?

    python runs/RBT-128/design-adversary/fc_mutants.py <a checkout of the PR> > runs/RBT-128/design-adversary/fc_mutants.txt

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
    ("fair.py", '    ("effector_bias_sigma", 0.0, "--effector-bias-sigma 0"),\n', '', "M2: S = 0 dropped from the preset"),
    ("fair.py", '    ("effector_bias_sigma", 0.0, "--effector-bias-sigma 0"),\n', '    ("effector_bias_sigma", 0.05, "--effector-bias-sigma 0.05"),\n', "M2: S = 0.05 in the preset"),
    ("cli.py", 'fair_mod.guard("ecology", marker, mixed=True)', 'fair_mod.guard("ecology", marker, mixed=getattr(args, "only_fauna", None) is None)', "M3: --only-fauna exempt again"),
    ("cli.py", '        fair_mod.note_resume(args)\n        ex = Experiment.resume', '        fair_mod.guard("evolve", fair_mod.expand(args), mixed=True)\n        ex = Experiment.resume', "resume meets the guard (evolve)"),
    ("cli.py", '        fair_mod.note_resume(args)\n        Ecology.resume', '        fair_mod.guard("ecology", fair_mod.expand(args), mixed=True)\n        Ecology.resume', "resume meets the guard (ecology)"),
    ("cli.py", '        fair_mod.note_resume(args)\n        Ecology.resume', '        Ecology.resume', "S2/N3: resume note dropped (ecology)"),
    ("cli.py", 'fairness="fair" if marker == "fair" else "",\n        population_size=args.capacity', 'fairness="",\n        population_size=args.capacity', "S2: ecology writes no fairness marker"),
    ("fair.py", '    bad = shift_on_preset(getattr(args, "shift", None))\n', '    bad = ""\n', "S1: shift onto a preset field accepted"),
    ("fair.py", '    targets = {path[len("sim."):] for path in CONFIG_PATH.values() if path.startswith("sim.")}', '    targets = {"synthesis.mass_budget"}', "S1: only the mass-budget shift refused"),
    ("fair.py", '    if config.get("fairness") != "fair":\n', '    if False:\n', "S3: check ignores a missing marker"),
    ("fair.py", '    if shift_on_preset(shift):\n', '    if False:\n', "S3: check ignores a shift onto a preset field"),
    ("fair.py", '            out.append(f"{CONFIG_PATH[dest]} is {node!r}, the preset\'s is {value!r} ({flag})")\n', '            out.append(f"{CONFIG_PATH[dest]} is {node!r}, the preset\'s is {value!r} ({flag})")\n            break\n', "S3: check stops at the first value deviation"),
    ("fair.py", 'abs_tol=1e-12', 'abs_tol=0.05', "S3: check tolerates |dev| <= 0.05 (settle 0.02 passes)"),
    ("fair.py", 'if node is None or (isinstance(value, float)', 'if node is None or (False and isinstance(value, float)', "S3: check reads presence only, not values"),
    ("fair.py", '"effector_bias_sigma": "mutation.effector_bias_sigma"}', '"effector_bias_sigma": "mutation.global_bias_sigma"}', "S3: check reads the wrong mutation key"),
    ("fair.py", '    print(f"--fair expands to: {expanded_flags(args)}', '    print(f"--fair expands to: {expanded_flags(args).replace(\' --effector-bias-sigma 0\', \'\')}', "M2: S not printed"),
    ("fair.py", '"effector_bias_sigma": None}', '"effector_bias_sigma": 0.4}', "M2: --effector-bias-sigma 0.4 read as unset (silently 0)"),
    ("fair.py", 'if got != _UNSET[dest] and got != value:', 'if False:', "a conflicting explicit value silently overridden"),
    ("fair.py", '    if not mixed or marker:\n', '    if True:\n', "guard never fires"),
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
