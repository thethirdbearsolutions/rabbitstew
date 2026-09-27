"""RBT-112: the matched "held" null for the arm, with the operator's crossover, at --global-bias-sigma S.

RBT-106's design adversary's `adversary/null_xover.py`, imported and run through its own `main()`: part 2's
real 600-season genealogy (lineage.jsonl, both parents), RBT-106's w = 32 founders planted at part 2's
founders, the ecology's own designed-body operator (crossover_controller at the recorded mates, then
mutate_controller), 20 replicates per seed, held.py's arithmetic.  Two things change when --global-bias-sigma
is given, and nothing else:
  * the operator's MutationConfig gets global_bias_sigma = S (the arm's operator);
  * mu is read from the arm's own no-selection table, runs/RBT-112/baseline/baseline-w32-S0-SEED.txt
    (baseline.py at S = 0), in place of RBT-106's baseline-w32-SEED.txt.
Every replicate's random stream is the adversary's (SeedSequence([106, seed, 32, 1, rep] + name)), so each
S = 0 replicate is its default twin with the global biases frozen.  Without the flag the run is the
adversary's, and must reproduce its committed xnull-w32-SEED.txt.

Usage: null_xover_s0.py PART2_RUN SEED FOUNDERS_DIR [--global-bias-sigma 0] [--reps 20] [--procs 4]
         > null/xnull-w32[-S0]-SEED.txt      (seasons 150, 300, 599, as the adversary's)
"""
import dataclasses
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt106_null_xover", os.path.join(_ROOT, "runs", "RBT-106", "adversary", "null_xover.py"))
nx = importlib.util.module_from_spec(_spec)
sys.modules["rbt106_null_xover"] = nx
_spec.loader.exec_module(nx)


def s0_baseline_path(seed, w, k=1.0):
    assert (w, k) == (32.0, 1.0), "RBT-112's S = 0 table is w = 32, K = 1 only"
    return os.path.join(_HERE, "baseline", f"baseline-w32-S0-{seed}.txt")


def main():
    argv = list(sys.argv[1:])
    S = None
    if "--global-bias-sigma" in argv:
        i = argv.index("--global-bias-sigma")
        S = float(argv[i + 1])
        del argv[i:i + 2]
        if S != 0.0:
            sys.exit("only S = 0 has a no-selection table (baseline.py)")
        nx.replace = lambda m, **kw: dataclasses.replace(m, global_bias_sigma=S, **kw)
        nx.held.baseline_path = s0_baseline_path
        print(f"# RBT-112: the operator at global_bias_sigma = {S:g}; mu from runs/RBT-112/baseline/baseline-w32-S0-SEED.txt")
    run, seed, fdir = argv[0], argv[1], argv[2]
    sys.argv = [sys.argv[0], run, seed, "32", fdir, "--seasons", "150,300,599"] + argv[3:]
    nx.main()


if __name__ == "__main__":
    main()
