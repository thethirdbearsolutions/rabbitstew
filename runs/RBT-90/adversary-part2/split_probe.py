"""RBT-90 part 2 adversary, probe O: is the oscillator SPLIT a founding-population property or history?

For each seed, from the restored bulk (no simulation):
  - the founders' linked-oscillator count (RBT-28's wiring(), as oscillator_rate.py counts it);
  - the founders the season-599 living trace back to by first parent (part2_readout.depth's chain),
    and whether each carries a linked oscillator: which founder's line WON is a run outcome;
  - the de novo linked-oscillator births (no parent carries one) and the season of the first;
  - the rate at birth in seasons 1-100 against the fate: if the fate were fixed by the founders it
    should already be legible early; if it is a sweep it appears later.

usage: split_probe.py BULK_ROOT [SEED ...]
"""
import glob
import importlib.util
import json
import pathlib
import sys

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)
spec = importlib.util.spec_from_file_location("ro", HERE.parent / "part2_readout.py")
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)


def main(bulk, seeds):
    print(f"{'seed':>5s} {'fate':>9s} {'osc f':>5s} | {'founders reached by the living (first parent): name osc?':<52s} | "
          f"{'de novo':>7s} {'first':>5s} | {'rate s1-100':>11s} {'s101-300':>8s} {'s301-599':>8s}")
    for seed in seeds:
        run = pathlib.Path(bulk) / f"forage-{seed}"
        cfg = SimConfig.from_dict(json.load(open(run / "config.json"))["sim"])
        G = {}
        for p in glob.glob(str(run / "holistic" / "genomes" / "*.json")):
            d = json.load(open(p))
            G[d["name"]] = (d.get("parents") or [], d["record"].get("born", 0),
                            adv.wiring(Genotype.load(p), cfg)["osc_linked"] > 0)
        # founders reached, by the readout's own first-parent chain over lineage-last.txt
        recs = {}
        for line in (HERE.parent / f"forage-{seed}" / "lineage-last.txt").read_text().splitlines()[1:]:
            pop, name, gen, age, ev, fit, parents = line.split("\t")
            if pop == "holistic":
                recs[name] = (int(gen), parents.split(",") if parents else [])
        last = max(g for g, _ in recs.values())
        reached = {}
        for name, (g, _) in recs.items():
            if g != last:
                continue
            cur, seen = name, set()
            while recs[cur][1] and recs[cur][1][0] in recs and cur not in seen:
                seen.add(cur)
                cur = recs[cur][1][0]
            reached[cur] = reached.get(cur, 0) + 1
        osc_f = sum(v[2] for v in G.values() if not v[0])
        dn = sorted(b for n, (par, b, o) in G.items() if par and o and not any(G.get(p, ([], 0, False))[2] for p in par))

        def rate(lo, hi):
            xs = [o for par, b, o in G.values() if par and lo <= b <= hi]
            return np.mean(xs) if xs else float("nan")
        o = json.loads([l for l in (HERE.parent / f"forage-{seed}" / "oscillator.txt").read_text().splitlines() if l.startswith("{")][-1])
        fate = "discarded" if o["distinct"] <= ro.OSC_DISCARD else "acquired" if o["distinct"] >= ro.OSC_ACQUIRE else "undecided"
        rc = ", ".join(f"{n}{' OSC' if G[n][2] else ''} x{k}" for n, k in sorted(reached.items(), key=lambda x: -x[1]) if n in G)
        print(f"{seed:5d} {fate:>9s} {osc_f:5d} | {rc:<52s} | {len(dn):7d} {dn[0] if dn else '-':>5} | "
              f"{rate(1, 100):11.3f} {rate(101, 300):8.3f} {rate(301, 599):8.3f}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], [int(a) for a in sys.argv[2:]] or ro.SEEDS)
