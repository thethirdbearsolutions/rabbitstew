"""RBT-105 readout adversary: how far does the fate classifier's count move WITHIN one replicate run?

The design adversary's probe_distinct.py (adversary/), unchanged in its instrument and windows, pointed at the 16
replicate arms' bulk (restored from ckpt/rbt-105-SEED-bK) instead of the RBT-90 originals. If the count of one run,
re-scored on half-samples, crosses the 3..7 gap, then "flip" partly measures the classifier, not history.

    python runs/RBT-105/readout-adversary/probe_windows.py BULK_RUNS_DIR > runs/RBT-105/readout-adversary/probe_windows.txt
BULK_RUNS_DIR holds forage-SEED-bK/ (restored checkpoints). Measures only.
"""
import glob
import importlib.util
import json
import os
import re
import sys

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
spec = importlib.util.spec_from_file_location("adv", os.path.join(ROOT, "runs", "RBT-28", "adversary_founders.py"))
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)
WINDOWS = {
    "all": lambda g: 10 <= g <= 590,
    "to580": lambda g: 10 <= g <= 580,
    "to500": lambda g: 10 <= g <= 500,
    "early": lambda g: 10 <= g <= 290,
    "late": lambda g: 300 <= g <= 590,
    "even": lambda g: g >= 10 and g % 20 == 0,
    "odd": lambda g: g >= 10 and g % 20 == 10,
}
ORIG = {7: "D", 805: "D", 4: "A", 807: "A", 806: "A", 2: "A", 1: "D", 804: "D"}


def fate(d):
    return "D" if d <= 2 else ("A" if d >= 8 else "u")


print("# distinct osc-linked bests by window (D <= 2, A >= 8, u 3..7), 16 replicate arms; orig = the RBT-90 original's fate")
print("arm        orig committed | " + " ".join(f"{w:>7s}" for w in WINDOWS) + " | D<->A crossing among windows")
cross = 0
for seed in ORIG:
    for k in (1, 2):
        run = os.path.join(sys.argv[1], f"forage-{seed}-b{k}")
        cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
        snaps = []
        for p in sorted(glob.glob(os.path.join(run, "holistic", "best_gen*.json"))):
            gen = int(re.search(r"best_gen(\d+)", p).group(1))
            g = Genotype.load(p)
            snaps.append((gen, g.name, adv.wiring(g, cfg)["osc_linked"] > 0))
        committed = [json.loads(l) for l in open(os.path.join(ROOT, "runs", "RBT-105", f"forage-{seed}-b{k}", "oscillator.txt")) if l.startswith("{")][-1]["distinct"]
        ds = [len({n for g, n, o in snaps if keep(g) and o}) for keep in WINDOWS.values()]
        fs = {fate(d) for d in ds}
        c = "D" in fs and "A" in fs
        cross += c
        print(f"{seed:>4d}-b{k}   {ORIG[seed]:>4s} {committed:>9d} | " + " ".join(f"{d:>5d} {fate(d)}" for d in ds) + f" | {'YES' if c else 'no'}", flush=True)
print(f"\narms whose count crosses D<->A between windows of the same run: {cross} of 16")
