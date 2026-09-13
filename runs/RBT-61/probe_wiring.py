"""At depth 78, is the crossed pairing proposed and removed, or never proposed? (RBT-61)

RBT-45 measured, with no world and no selection, that drift carries a two-nose
pairing in ~9% of lineages at depth 19, rising to ~36% by depth 100 and ~49% by
200 (uncrossed), with the crossed circuit at 1.3%, 8.6% and 14.7% at the same
depths.  RBT-60's max_age 15 arm reached depth 78 with real selection running.
Its final populations are therefore a direct test of drift against selection:
match the drift curve and the circuit is proposed and simply never useful; fall
far below it and selection is removing it.

File analysis only.  No simulation.  usage: probe_wiring.py RUN LABEL
"""
import glob, os, sys

from rabbitstew.analysis import sensor_influence
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize
import json


def survey(run, kind):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    files = sorted(glob.glob(f"{run}/{kind}/final/*.json"))
    n = any_ = pair = half = chassis = 0
    for f in files:
        ph = synthesize(Genotype.load(f), cfg.synthesis)
        rows = [r for r in sensor_influence(ph) if r["label"].startswith("food")]
        wheel = [r for r in rows if r["part"] != 0 and r["influence"] > 0]
        ch = [r for r in rows if r["part"] == 0 and r["influence"] > 0]
        n += 1
        any_ += 1 if (wheel or ch) else 0
        pair += 1 if len(wheel) >= 2 else 0
        half += 1 if len(wheel) == 1 else 0
        chassis += 1 if ch else 0
    return n, any_, pair, half, chassis


run, label = sys.argv[1], sys.argv[2]
print(f"{label}  ({run})")
for kind in ("conventional", "holistic"):
    if not os.path.isdir(f"{run}/{kind}/final"):
        continue
    n, any_, pair, half, ch = survey(run, kind)
    if n:
        print(f"  {kind:12} n={n:3d}  any food nose wired {any_:3d} ({any_/n:4.0%})  "
              f"BOTH wheel noses {pair:3d} ({pair/n:4.0%})  one wheel nose {half:3d} ({half/n:4.0%})  "
              f"chassis nose {ch:3d} ({ch/n:4.0%})")
