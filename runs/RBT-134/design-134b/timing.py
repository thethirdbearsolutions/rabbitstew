"""RBT-134b: per-lineage CPU cost of each 134b step, for the cost table (DESIGN-134b.md 8).

Throwaway seed 1 only (not MASTER_SEED, not a held-out seed), the default operator (no registered condition's fields),
N lineages per pool.  Nothing it computes is printed but CPU time: no arrival, background or swap result.

    python runs/RBT-134/design-134b/timing.py > runs/RBT-134/design-134b/timing.txt
"""
import importlib.util
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
N = 150
SEED = 1  # throwaway


def _assay():
    spec = importlib.util.spec_from_file_location("assay134t", os.path.join(HERE, "..", "assay.py"))
    mod = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ["assay.py"]
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod


def main():
    os.chdir(ROOT)
    A = _assay()
    for label in A.rbt78.POOLS:  # warm the pool cache outside the clock
        A.rbt78._load(label)
    t = {"lineage": 0.0, "tracked": 0.0, "bg probe": 0.0, "swap": 0.0}
    n = 0
    for label in A.rbt78.POOLS:
        for i in range(N):
            c0 = time.process_time()
            ph = A.lineage_134b(label, i, {}, SEED)[0]
            A.predicate(ph, "food"), A.predicate(ph, "agent"), A.sr.motif_units(ph)
            c1 = time.process_time()
            A.lineage_134b(label, i, {}, SEED, track=True)
            c2 = time.process_time()
            A.sr.small_signal_a(ph), A.dec.sign_flip(ph, None)
            c3 = time.process_time()
            phs = A.lineage_134b(label, i, {}, SEED, swap=True)[0]
            A.predicate(phs, "food"), A.predicate(phs, "agent")
            c4 = time.process_time()
            t["lineage"] += c1 - c0
            t["tracked"] += c2 - c1  # a tracked lineage (its final predicates are not repeated)
            t["bg probe"] += c3 - c2
            t["swap"] += c4 - c3
            n += 1
    ms = {k: 1000 * v / n for k, v in t.items()}
    print("RBT-134b: CPU per lineage of each 134b step (throwaway seed 1, default operator; CPU time, one core)\n")
    print(f"host: {platform.machine()}, Python {platform.python_version()}; lineages {n} ({N} per pool)\n")
    print("| step | ms per lineage |\n|---|---|")
    print(f"| lineage, 19 steps + final synthesis + food, agent and motif predicates | {ms['lineage']:.1f} |")
    print(f"| the same lineage tracked (synthesis + predicate after every step) | {ms['tracked']:.1f} |")
    print(f"| background probe (whole-brain small-signal a + sign-flip) | {ms['bg probe']:.1f} |")
    print(f"| swap regeneration (lineage from relabelled parent + two predicates) | {ms['swap']:.1f} |")


if __name__ == "__main__":
    main()
