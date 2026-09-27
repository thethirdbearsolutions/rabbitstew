"""RBT-112: is the planted compass HELD in the arm above what the arm's own operator leaves? (PREREGISTRATION.md §5)

RBT-106's `held.py`, imported and run through its own `main()`, with one change: an arm whose config.json
records mutation.global_bias_sigma = 0 is read against the no-selection table of THAT operator,
runs/RBT-112/baseline/baseline-w32-S0-SEED.txt (baseline.py at S = 0), and not against RBT-106's default
table.  Criterion (pay32), k_planted / k_bare, mu at each genome's own depth, B, and the call (HELD iff
k_planted > B) are RBT-106's, unchanged.  An arm at the default operator is read exactly as RBT-106 reads it.
Any other global_bias_sigma is refused (it has no table).

Usage: held.py RUN_DIR SEED 32 [--season 599]
"""
import importlib.util
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt106_held", os.path.join(_ROOT, "runs", "RBT-106", "held.py"))
held = importlib.util.module_from_spec(_spec)
sys.modules["rbt106_held"] = held
_spec.loader.exec_module(held)
_default_path = held.baseline_path


def table_for(run):
    """The baseline_path function for this arm's operator."""
    gbs = json.load(open(os.path.join(run, "config.json")))["mutation"].get("global_bias_sigma")
    if gbs is None:
        return _default_path
    if gbs != 0.0:
        raise SystemExit(f"REFUSED: global_bias_sigma {gbs} has no no-selection table (only 0 does)")

    def s0(seed, w, k=1.0):
        assert (w, k) == (32.0, 1.0), "the S = 0 table is w = 32, K = 1 only"
        return os.path.join(_HERE, "baseline", f"baseline-w32-S0-{seed}.txt")
    return s0


def main():
    run = sys.argv[1].rstrip("/")
    held.baseline_path = table_for(run)
    gbs = json.load(open(os.path.join(run, "config.json")))["mutation"].get("global_bias_sigma")
    print(f"# RBT-112 held (RBT-106's held.py; operator global_bias_sigma {gbs if gbs is not None else 'default'}; "
          f"table {held.baseline_path(int(sys.argv[2]), float(sys.argv[3]))})")
    held.main()


if __name__ == "__main__":
    main()
