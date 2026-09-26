"""RBT-105 design adversary, probe 2: how much does RBT-84's `distinct` count move within one run?

The rule's HISTORY verdict fires on one flip, and two wave-1 seeds sit at the discard bar (805 at 1,
7 at 2). This asks whether `distinct` itself is noisy enough to cross the 3..7 gap without any change
of fate, by re-scoring each RBT-90 part 2 arm with the SAME instrument (RBT-84 oscillator_rate.py's
definition: distinct genotype names among saved bests after season 0 carrying a linked oscillator,
wiring from runs/RBT-28/adversary_founders.py) over different windows of the same run:

  all       seasons 10..590 (the committed count; must reproduce oscillator.txt)
  to580     drop the last snapshot            (an adjacent checkpoint)
  to500     seasons 10..500
  late      seasons 300..590 (the second half)
  early     seasons 10..290
  odd/even  alternate snapshots (20,40,..) / (10,30,..): two interleaved half-samples of one run

plus the birth-level rate (share of every genome saved at birth carrying a linked oscillator) per
150-season block, the continuous quantity the count is a thresholded sample of.

Reads the bulk (checkpoints ckpt/rbt-90-SEED restored with scripts/durable.sh restore); measures only.

    python runs/RBT-105/adversary/probe_distinct.py BULK_ROOT [SEED ...] > runs/RBT-105/adversary/probe_distinct.txt
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

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

SEEDS = [int(s) for s in sys.argv[2:]] or [801, 804, 805, 1, 7, 4, 807, 806, 2, 3]
WINDOWS = {
    "all": lambda g: 10 <= g <= 590,
    "to580": lambda g: 10 <= g <= 580,
    "to500": lambda g: 10 <= g <= 500,
    "early": lambda g: 10 <= g <= 290,
    "late": lambda g: 300 <= g <= 590,
    "even": lambda g: g >= 10 and g % 20 == 0,
    "odd": lambda g: g >= 10 and g % 20 == 10,
}


def fate(d):
    return "D" if d <= 2 else ("A" if d >= 8 else "u")


print("# distinct osc-linked bests by window (fate: D <= 2, A >= 8, u 3..7) | birth rate per 150-season block")
print("seed  committed | " + " ".join(f"{w:>7s}" for w in WINDOWS) + " | births 0-149 150-299 300-449 450-599")
for seed in SEEDS:
    run = os.path.join(sys.argv[1], f"forage-{seed}")
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    osc = lambda g: adv.wiring(g, cfg)["osc_linked"] > 0
    snaps = []
    for p in sorted(glob.glob(os.path.join(run, "holistic", "best_gen*.json"))):
        gen = int(re.search(r"best_gen(\d+)", p).group(1))
        g = Genotype.load(p)
        snaps.append((gen, g.name, osc(g)))
    born = {}
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r.get("population") == "holistic" and r["name"] not in born:
                born[r["name"]] = r["generation"] - r.get("age", 0)
    blocks = [[0, 0] for _ in range(4)]
    for p in glob.glob(os.path.join(run, "holistic", "genomes", "*.json")):
        name = pathlib.Path(p).stem
        if name.startswith("h0-"):
            continue  # founders are not births
        b = min(3, max(0, born.get(name, 0)) // 150)
        blocks[b][0] += 1
        blocks[b][1] += osc(Genotype.load(p))
    committed = [json.loads(l) for l in open(ROOT / "runs" / "RBT-90" / f"forage-{seed}" / "oscillator.txt") if l.startswith("{")][-1]["distinct"]
    cells = []
    for w, keep in WINDOWS.items():
        d = len({n for g, n, o in snaps if keep(g) and o})
        cells.append(f"{d:>5d} {fate(d)}")
    print(f"{seed:>4d}  {committed:>9d} | " + " ".join(cells) + " | " + " ".join(f"{b[1] / max(1, b[0]):7.3f}" for b in blocks), flush=True)
    osc_seasons = [g for g, n, o in snaps if o and g >= 10]
    print(f"      snapshot seasons carrying one: {osc_seasons}", flush=True)
