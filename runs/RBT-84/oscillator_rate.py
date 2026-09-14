"""Linked-oscillator carriage, scored three ways (RBT-84, adversary seams 1 and 2).

Prediction A was written as "<= 2 of ~60 saved bests carry a linked oscillator". The adversary
pointed out that saved bests are SNAPSHOTS and autocorrelated -- one genotype that stays best for a
hundred seasons is ten snapshots -- so a snapshot count can say "8" for one long-lived lineage or
"2" for two separate one-season acquisitions. Their own 1-of-295 on RBT-28 has the same shape.

So A is scored on **distinct genotype names** among the saved bests, with the snapshot count beside
it, and the **birth-level rate over every genome saved at birth** is reported as the base rate the
bests should be read against -- which is the thing no run before RBT-27 could produce.

usage: oscillator_rate.py RUN_DIR [KIND]
"""
import glob
import importlib.util
import json
import os
import pathlib
import re
import sys

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

run = sys.argv[1]
kind = sys.argv[2] if len(sys.argv) > 2 else "holistic"
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def osc_linked(path):
    return adv.wiring(Genotype.load(path), cfg)["osc_linked"] > 0


bests = sorted(glob.glob(os.path.join(run, kind, "best_gen*.json")))
snap, names = 0, set()
for p in bests:
    gen = int(re.search(r"best_gen(\d+)", p).group(1))
    if gen == 0:
        continue                                    # season 0 is the founders, not the search
    g = Genotype.load(p)
    if adv.wiring(g, cfg)["osc_linked"] > 0:
        snap += 1
        names.add(g.name)

births = glob.glob(os.path.join(run, kind, "genomes", "*.json"))
b_osc = sum(osc_linked(p) for p in births)

print(f"{run} {kind}")
print(f"  saved bests after season 0: {len(bests) - 1}")
print(f"  ... snapshots carrying a linked oscillator: {snap}")
print(f"  ... DISTINCT GENOTYPES carrying one:        {len(names)}  {sorted(names) if names else ''}")
print(f"  every genome saved at birth: {len(births)}")
print(f"  ... carrying a linked oscillator: {b_osc}  ({b_osc / max(1, len(births)):.3f} of births)")
print(f"\nPrediction A is scored on the DISTINCT-GENOTYPE count: {len(names)}")
print(f"  <= 2 confirms; >= 8 falsifies; 3-7 is NOT CONFIRMED and the arm could not decide it at this n.")
print(json.dumps({"run": run, "kind": kind, "bests": len(bests) - 1, "snapshots": snap,
                  "distinct": len(names), "births": len(births), "births_osc": b_osc,
                  "birth_rate": b_osc / max(1, len(births))}))
