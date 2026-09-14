"""Adversary probe for RBT-84, Prediction C: can the per-unit ranking separate its top two units?

The ticket scores drive kind "per RBT-28's classification", which was the KIND of the single most
costly unit lesion (effector / global neuron / oscillator / local neuron).  On the champion's 64-draw
table the most costly unit is effector unit 20 (+1.52 items) and the second is global neuron 34
(+1.38); the report scored C on the whole-subsystem modes instead (no_global resolvable, so
FALSIFIED).  Under the ticket's own rule the top unit is an effector and C holds -- if the ranking
is real.  This reads the two lesions on the same 64 paired seeds and asks whether their difference
clears anything.

Same bouts as forage_lab.py (its `trial`, unchanged), seeds 8000+, 120 null layouts.
usage: adversary_topunit.py RUN_DIR KIND GEN UNIT_A UNIT_B [N]
"""
import importlib.util
import json
import os
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("flab", ROOT / "scripts" / "forage_lab.py")
flab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flab)

run, kind, gen, ua, ub = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
n = int(sys.argv[6]) if len(sys.argv) > 6 else 64
g, cfg = flab.load(run, kind, gen)
ph = flab.synthesize(g, cfg.synthesis)
gs = flab.groups(ph)
seeds = list(range(8000, 8000 + n))
modes = ["intact", f"lesion:{ua}", f"lesion:{ub}"]
food = {m: np.array([flab.trial(g, cfg, ph, gs, s, m, draws=120)["food"] for s in seeds], float) for m in modes}


def paired(a, b):
    d = a - b
    se = d.std(ddof=1) / np.sqrt(len(d))
    return d.mean(), se, (d.mean() / se if se > 0 else float("nan")), int((d == 0).sum())


def desc(u):
    x = ph.units[u]
    return f"unit {u} part {x.part} {x.unit.kind} {getattr(x.unit, 'name', '')}".strip()


L = [f"{run} {kind} gen {gen} ({g.name}): the top two unit lesions on {n} paired seeds {seeds[0]}..{seeds[-1]}"]
L.append(f"  intact {food['intact'].mean():.3f} +- {food['intact'].std(ddof=1) / np.sqrt(n):.3f} items")
for m in modes[1:]:
    mean, se, t, z = paired(food["intact"], food[m])
    L.append(f"  intact minus {m:10s} {mean:+.3f} +- {se:.3f}  t {t:+.2f}  zeros {z}/{n}   [{desc(int(m[7:]))}]")
mean, se, t, z = paired(food[modes[2]], food[modes[1]])
L.append(f"  cost of {modes[1]} minus cost of {modes[2]}: {mean:+.3f} +- {se:.3f}  t {t:+.2f}  zeros {z}/{n}")
L.append(f"  per-seed (cost A - cost B): " + " ".join(f"{int(x):+d}" for x in (food[modes[2]] - food[modes[1]])))
verdict = ("the ranking is REAL at |t| >= 2.5" if abs(t) >= 2.5 else
           "the ranking CANNOT be resolved at this n: the top-unit kind is undecided")
L.append(f"  -> {verdict}")
L.append(json.dumps({"gen": gen, "name": g.name, "A": ua, "B": ub, "n": n, "diff": mean, "se": se, "t": t, "zeros": z}))
text = "\n".join(L)
print(text)
os.makedirs("docs/runs", exist_ok=True)
with open("docs/runs/RBT-84-adversary-topunit.txt", "w") as f:
    f.write(text + "\n")
