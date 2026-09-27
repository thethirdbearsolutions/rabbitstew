"""RBT-118 prior ADVERSARY probe: is claim 4's work lead a random-terrain (clutter) lead?  Food and work per fauna over the
last 20 seasons of each flat-terrain fork (RBT-101 shift, RBT-107 fresh shift), from its ckpt lineage.jsonl, set beside
the same history's random-terrain values from PR #399's levers.tsv (same 20-season window at the last season).

    python runs/RBT-118/prior-adversary/probe_flatwork.py PATH/TO/levers.tsv SCRATCH > runs/RBT-118/prior-adversary/probe_flatwork.txt
"""
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WINDOW = 20
PAIRS = ([(f"rbt-101-shift-{s}", f"rbt-90-{s}") for s in (1, 2, 3, 4, 7, 801, 804, 805, 806, 807)]
         + [(f"rbt-107-fresh-shift-{s}", f"rbt-107-fresh-base-{s}") for s in range(11, 31) if s != 29])


def git(*a, **k):
    return subprocess.run(["git", "-C", ROOT, *a], check=True, capture_output=True, **k).stdout


def restore(label, scratch):
    ref = f"ckpt/{label}"
    git("fetch", "-q", "--depth", "1", "origin", f"{ref}:refs/remotes/origin/{ref}")
    names = git("ls-tree", "--name-only", f"origin/{ref}", text=True).split()
    blob = b"".join(git("show", f"origin/{ref}:{n}") for n in sorted(x for x in names if x.startswith("run.tar.gz.part")))
    dest = os.path.join(scratch, label)
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as t:
        members = [m for m in t.getmembers() if m.name.endswith("lineage.jsonl") or m.name.endswith("config.json")]
        t.extractall(dest, members=members, filter="data")
    manifest = git("show", f"origin/{ref}:MANIFEST", text=True).split()
    git("update-ref", "-d", f"refs/remotes/origin/{ref}")
    for dp, _, fs in os.walk(dest):
        if "lineage.jsonl" in fs and "config.json" in fs:
            return dp, manifest
    raise RuntimeError(label)


lev = defaultdict(dict)
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    lev[r["label"]][(int(r["season"]), r["fauna"])] = r
scratch = sys.argv[2]
print("# RBT-118 prior ADVERSARY, probe_flatwork.py: EXPLORATORY, descriptive. food items, work kJ, net = food - 0.03*kJ; last 20 seasons")
print(f"{'flat fork':24s} {'shift':22s} {'H food':>6s} {'H kJ':>6s} {'D food':>6s} {'D kJ':>6s} | {'rand H food':>11s} {'H kJ':>6s} {'D food':>6s} {'D kJ':>6s}")
out = []
for flat, base in PAIRS:
    d, man = restore(flat, scratch)
    cfg = json.load(open(os.path.join(d, "config.json")))
    rows = defaultdict(lambda: defaultdict(list))
    last = 0
    with open(os.path.join(d, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("death"):
                continue
            rows[r["generation"]][r["population"]].append(r)
            last = max(last, r["generation"])
    fl = {}
    for k in ("holistic", "conventional"):
        win = [r for t in range(last - WINDOW + 1, last + 1) for r in rows[t][k]]
        fl[k] = (np.mean([float(r["food"]) for r in win if r.get("food") is not None]), np.mean([float(r["work"]) for r in win if r.get("work") is not None]) / 1000)
    bl = max(s for s, _ in lev[base])
    rb = {k: (float(lev[base][(bl, k)]["food"]), float(lev[base][(bl, k)]["work_j"]) / 1000) for k in ("holistic", "conventional")}
    out.append((fl, rb))
    print(f"{flat:24s} {cfg['ecology']['shift'] + '@' + str(cfg['ecology']['shift_at']):22s} {fl['holistic'][0]:6.2f} {fl['holistic'][1]:6.1f} {fl['conventional'][0]:6.2f} {fl['conventional'][1]:6.1f} | "
          f"{rb['holistic'][0]:11.2f} {rb['holistic'][1]:6.1f} {rb['conventional'][0]:6.2f} {rb['conventional'][1]:6.1f}   MANIFEST {man[1] if len(man) > 1 else '?'} last {last}")
    shutil.rmtree(os.path.join(scratch, flat), ignore_errors=True)

n = len(out)
def med(f):
    return np.median([f(fl, rb) for fl, rb in out])
print(f"\npairs: {n}")
for lab, i in (("food", 0), ("work kJ", 1)):
    for k, K in (("holistic", "H"), ("conventional", "D")):
        print(f"  {K} {lab:8s}: random {med(lambda fl, rb: rb[k][i]):6.2f}  flat {med(lambda fl, rb: fl[k][i]):6.2f}")
print(f"  flat: H works less on {sum(fl['holistic'][1] < fl['conventional'][1] for fl, _ in out)}/{n}; H eats less on {sum(fl['holistic'][0] < fl['conventional'][0] for fl, _ in out)}/{n}")
print(f"  flat: H-D food term median {med(lambda fl, rb: fl['holistic'][0] - fl['conventional'][0]):+.3f}, work term {med(lambda fl, rb: -0.03 * (fl['holistic'][1] - fl['conventional'][1])):+.3f}")
print(f"  random: H-D food term median {med(lambda fl, rb: rb['holistic'][0] - rb['conventional'][0]):+.3f}, work term {med(lambda fl, rb: -0.03 * (rb['holistic'][1] - rb['conventional'][1])):+.3f}")
print(f"  designed flat - random: food {med(lambda fl, rb: fl['conventional'][0] - rb['conventional'][0]):+.3f}, work kJ {med(lambda fl, rb: fl['conventional'][1] - rb['conventional'][1]):+.2f}")
