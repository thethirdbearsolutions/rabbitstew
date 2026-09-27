"""RBT-117 design adversary: compare.py end to end on SYNTHETIC tiny seed directories (real `evolve` runs at toy size,
built in a temp dir exactly as tests/test_rbt117.py builds them; no RBT-113 arm output is read).

  1. a PLANTED positive through the scored path: +DELTA raw added to the holistic U line's final-generation fitness
     in every seed directory (generation G-1 is never a parent generation, so RBT-113's controls still pass)
     -> expect HOLISTIC RESPONDS MORE; the same planted in the designed body -> DESIGNED RESPONDS MORE
  2. fail-loud checks: a seed directory passed twice; a missing seed; an extra seed outside 1..12; a directory
     under a non-O arm name

    python runs/RBT-117/design-adversary/probe_pipeline.py > runs/RBT-117/design-adversary/probe_pipeline.txt
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import test_rbt117 as t117  # noqa: E402

SCRIPT = os.path.join(ROOT, "runs", "RBT-117", "compare.py")
DELTA = 5.0


def run(*dirs):
    r = subprocess.run([sys.executable, SCRIPT, *dirs], capture_output=True, text=True)
    v = [l for l in r.stdout.splitlines() if l.startswith("## VERDICT") or l.startswith("## primary")]
    err = (r.stderr.strip().splitlines() or [""])[-1]
    return r.returncode, v, err


def plant(sd, fauna, delta):
    p = os.path.join(sd, "U", "lineage.jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()]
    G = max(r["generation"] for r in rows) + 1
    for r in rows:
        if r["population"] == fauna and r["generation"] == G - 1:
            r["fitness"] += delta
    with open(p, "w") as fh:
        fh.writelines(json.dumps(r) + "\n" for r in rows)


with tempfile.TemporaryDirectory() as tmp:
    from pathlib import Path
    base = Path(tmp)
    dirs = t117._tiny_default_dirs(base / "hol", seeds=(1, 2, 3, 4, 5, 6))
    print("# 0. unplanted, 6 seeds:", run(*dirs))
    for d in dirs:
        plant(d, "holistic", DELTA)
    print(f"# 1a. +{DELTA} planted in the holistic U line, 6 seeds (min exact p 2/64):", run(*dirs))
    ddirs = t117._tiny_default_dirs(base / "des", seeds=(1, 2, 3, 4, 5, 6))
    for d in ddirs:
        plant(d, "conventional", DELTA)
    print(f"# 1b. +{DELTA} planted in the designed U line:", run(*ddirs))
    print("# 2a. the same seed directory passed twice:", run(*dirs, dirs[0]))
    print("# 2b. 5 of the 6 (a lost seed; compare.py does not know 12 are expected):", run(*dirs[:5]))
    x = t117._tiny_default_dirs(base / "O9", seeds=(13,))
    print("# 2c. an extra seed 13 from an arm named O9 (neither in 1..12 nor under O1-O4):", run(*dirs, *x))
