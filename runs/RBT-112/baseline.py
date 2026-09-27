"""RBT-112 step 3: the operator-alone baseline with the global biases frozen (DECISION.md).

RBT-106's `baseline.py` (w = 32, K = 1), run here through its own `main()` with one change: the
MutationConfig that RBT-104's adversary's `persistence.lineage()` builds (`replace(cfg.mutation,
link_scale=K)`) also gets `global_bias_sigma = S` when --global-bias-sigma is given.  Nothing else is
touched: the same planted founders, the same lineage seeds (SeedSequence([104, seed, K, rep, founder])),
the same instruments, the same table.  Since the flag keeps the random stream, each S = 0 lineage is
its default twin draw for draw, with the global units' biases never stepping.  Without the flag the
run is RBT-106's, and must reproduce its committed `baseline-w32-SEED.txt` below the header.

The pool is forked, so that the workers inherit the patched `persistence.replace`.

Usage: baseline.py SEED FOUNDERS_DIR [--global-bias-sigma S] [--reps 20] [--procs 4]
         > baseline/baseline-w32[-S0]-SEED.txt
"""
import dataclasses
import importlib.util
import multiprocessing
import os
import sys
from concurrent.futures import ProcessPoolExecutor

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt106_baseline", os.path.join(_ROOT, "runs", "RBT-106", "baseline.py"))
b106 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b106)
per = b106.per  # RBT-104's adversary persistence.py, as sys.modules["persistence"]


def main():
    argv = list(sys.argv[1:])
    S = None
    if "--global-bias-sigma" in argv:
        i = argv.index("--global-bias-sigma")
        S = float(argv[i + 1])
        del argv[i:i + 2]
    if S is not None:
        per.replace = lambda m, **kw: dataclasses.replace(m, global_bias_sigma=S, **kw)
        # the header line names the change; the table below it is RBT-106's format
        _print = print

        def print_(*a, **k):
            if a and isinstance(a[0], str) and a[0].startswith("# RBT-106 no-selection baseline"):
                a = (a[0].replace("# RBT-106 no-selection baseline", f"# RBT-112 no-selection baseline, global_bias_sigma = {S:g}"),) + a[1:]
            _print(*a, **k)
        b106.print = print_
    ctx = multiprocessing.get_context("fork")
    b106.ProcessPoolExecutor = lambda n: ProcessPoolExecutor(n, mp_context=ctx)
    sys.argv = [sys.argv[0], argv[0], "32", argv[1]] + argv[2:]
    b106.main()


if __name__ == "__main__":
    main()
