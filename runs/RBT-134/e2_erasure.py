"""RBT-134 E2 (DESIGN.md 8): RBT-112's functional erosion u(8) under a registered condition.

RBT-112's `baseline.py` route, unchanged except for the operator: RBT-106's `baseline.py` (w = 32, K = 1) through its
own `main()`, with RBT-104's adversary `persistence.lineage()` building its MutationConfig by `replace(...)`.  Here
that `replace` also gets the condition's fields (assay.CONDITIONS), and `mutate_controller` gets the registered
auxiliary stream: per lineage, SeedSequence(<the lineage's own seed entropy> + [134]).  Without fields (B0) the
output must equal RBT-112's committed `baseline/baseline-w32-SEED.txt` below the header.

    e2_erasure.py run COND SEED FOUNDERS_DIR [--reps 20] [--procs 4] [--go] > out/e2-COND-SEED.txt
    e2_erasure.py summary COND                                         (reads out/e2-COND-*.txt)

FOUNDERS_DIR is built by `runs/RBT-106/founders.py SEED 32 DIR` (digest-checked).  Every condition but B0 refuses
without --go (B0's output must equal RBT-112's committed table; F1).
"""
import dataclasses
import importlib.util
import multiprocessing
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)  #: RBT-112's ten (runs/RBT-112/erasure.py)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _conditions():
    argv, sys.argv = sys.argv, ["assay.py"]
    try:
        return _load("assay134", os.path.join(_HERE, "assay.py")).CONDITIONS
    finally:
        sys.argv = argv


def run(cond, argv):
    go = "--go" in argv
    argv = [a for a in argv if a != "--go"]
    if cond != "B0" and not go:
        sys.exit("refused: registered conditions run only after the merge and the coordinator's GO (pass --go; "
                 "B0 alone needs none)")
    fields = _conditions()[cond]
    b106 = _load("rbt106_baseline", os.path.join(_ROOT, "runs", "RBT-106", "baseline.py"))
    per = b106.per
    if fields:
        per.replace = lambda m, **kw: dataclasses.replace(m, **fields, **kw)
        inner = per.mutate_controller
        aux = {}

        def mutate_controller(g, rng, mcfg):
            if rng not in aux:
                if len(aux) > 64:
                    aux.clear()
                ss = rng.bit_generator.seed_seq
                aux[rng] = np.random.default_rng(np.random.SeedSequence(list(np.atleast_1d(ss.entropy)) + [134]))
            return inner(g, rng, mcfg, aux_rng=aux[rng])
        per.mutate_controller = mutate_controller
        _print = print

        def print_(*a, **k):
            if a and isinstance(a[0], str) and a[0].startswith("# RBT-106 no-selection baseline"):
                a = (a[0].replace("# RBT-106 no-selection baseline", f"# RBT-134 E2 no-selection baseline, {cond} {fields}"),) + a[1:]
            _print(*a, **k)
        b106.print = print_
    ctx = multiprocessing.get_context("fork")
    b106.ProcessPoolExecutor = lambda n: ProcessPoolExecutor(n, mp_context=ctx)
    sys.argv = [sys.argv[0], argv[0], "32", argv[1]] + argv[2:]
    b106.main()


def summary(cond):
    er = _load("rbt112_erasure", os.path.join(_ROOT, "runs", "RBT-112", "erasure.py"))
    T = {s: er.table(os.path.join(_HERE, "out", f"e2-{cond}-{s}.txt")) for s in SEEDS}
    f8 = er.f(T, "pay32", 8)
    per_seed = np.array([er.u(er.f(T, "pay32", 8, seeds=(s,)), 8) for s in SEEDS])
    m, se = per_seed.mean(), per_seed.std(ddof=1) / np.sqrt(len(SEEDS))
    u8 = er.u(f8, 8)
    print(f"# RBT-134 E2 {cond}: pooled u(8) on pay32 = {u8:.3f} (default 0.282, global_bias_sigma 0: 0.089; "
          f"runs/RBT-112/erasure.txt:25)")
    print(f"  per seed mean {m:+.3f} [{m - er.T975_9 * se:+.3f}, {m + er.T975_9 * se:+.3f}] (t(9))")
    print(f"  reading (registered): {'PROPOSES BUT CANNOT KEEP (u(8) > 0.5)' if u8 > 0.5 else 'u(8) <= 0.5'}; "
          f"a cost, never a veto (DESIGN.md 8, E2)")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "summary":
        summary(sys.argv[2])
    elif len(sys.argv) >= 5 and sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
