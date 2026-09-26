"""RBT-106 §4: the patchy world's side effects, from 20-season smoke runs of the 2 x 2 (coordinator 20:28:
"base income at 12 items in 3 patches, and survival, at K = 1 and K = 8, first").

Each cell is RBT-90 part 2's command (RBT-104's `short_run.sh`) for 20 seasons on RBT-104's seeded founders
(w = 1), seeds 801 and 4:  S1U (uniform, K = 1)  S1P (patchy, K = 1)  S8U (uniform, K = 8)  S8P (patchy, K = 8).
Throwaway runs, not arms.  Their per-season tables (`seasons.txt`, RBT-71's summary) and configs are copied
into runs/RBT-106/side/CELL-SEED/ and read from there.  Printed per cell: the designed (conventional) fauna's
minimum and last alive, births, and mean lifetime score over seasons 0-19; the holistic fauna's the same.
These are feasibility and side-effect readings over 20 seasons; they are not results about evolution.

Usage: side.py [--collect SCRATCH_SIDE_DIR]
"""
import argparse
import importlib.util
import json
import os
import shutil

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CELLS = ("S1U", "S1P", "S8U", "S8P")
SEEDS = (801, 4)


def collect(src):
    spec = importlib.util.spec_from_file_location("measure", os.path.join(ROOT, "runs", "RBT-71", "measure.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for c in CELLS:
        for s in SEEDS:
            d = os.path.join(src, f"{c}-{s}")
            st = os.path.join(d, "state.json")
            if not os.path.exists(st) or int(json.load(open(st))["season"]) < 20:
                continue  # unfinished: never read a running smoke run
            m.summarise(d)
            out = os.path.join(HERE, "side", f"{c}-{s}")
            os.makedirs(out, exist_ok=True)
            for f in ("seasons.txt", "config.json"):
                shutil.copy(os.path.join(d, f), os.path.join(out, f))


def read(c, s):
    p = os.path.join(HERE, "side", f"{c}-{s}", "seasons.txt")
    if not os.path.exists(p):
        return None
    rows = [l.split("\t") for l in open(p).read().splitlines()]
    k = rows[0]
    rows = [dict(zip(k, r)) for r in rows[1:]]
    cfg = json.load(open(os.path.join(HERE, "side", f"{c}-{s}", "config.json")))
    out = dict(patches=cfg["sim"]["food"]["patches"], K=cfg["mutation"].get("link_scale", 1.0))
    for pop in ("conventional", "holistic"):
        r = [x for x in rows if x["population"] == pop]
        assert len(r) == 20, f"{c}-{s}: {len(r)} seasons, not 20"
        out[pop] = dict(min=min(int(x["alive"]) for x in r), last=int(r[-1]["alive"]), births=sum(int(x["births"]) for x in r),
                        score=float(np.mean([float(x["mean_lifetime_score"]) for x in r])), seasons=len(r))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", default=None)
    a = ap.parse_args()
    if a.collect:
        collect(a.collect)
    print("# RBT-106 side effects: 20-season smoke runs of the 2 x 2, RBT-104's seeded founders (w = 1)\n")
    print("| cell | seed | patches | K | designed alive min / last | designed births | designed mean lifetime score | holistic alive min / last | holistic births |")
    print("|---|---|---|---|---|---|---|---|---|")
    got = {}
    for c in CELLS:
        for s in SEEDS:
            r = read(c, s)
            if r is None:
                print(f"| {c} | {s} | (missing) |")
                continue
            got[(c, s)] = r
            d, h = r["conventional"], r["holistic"]
            print(f"| {c} | {s} | {r['patches']} | {r['K']:g} | {d['min']} / {d['last']} | {d['births']} | {d['score']:.3f} | "
                  f"{h['min']} / {h['last']} | {h['births']} |")
    print()
    for a_, b_, what in (("S1P", "S1U", "the prize at K = 1"), ("S8P", "S8U", "the prize at K = 8"),
                         ("S8U", "S1U", "the reach, uniform"), ("S8P", "S1P", "the reach, patchy")):
        pairs = [(got[(a_, s)], got[(b_, s)]) for s in SEEDS if (a_, s) in got and (b_, s) in got]
        if pairs:
            ratio = [x["conventional"]["score"] / y["conventional"]["score"] for x, y in pairs]
            br = [x["conventional"]["births"] / y["conventional"]["births"] for x, y in pairs]
            print(f"{what} ({a_} / {b_}): designed mean lifetime score x{', x'.join(f'{v:.2f}' for v in ratio)}; "
                  f"births x{', x'.join(f'{v:.2f}' for v in br)} (seeds {', '.join(str(s) for s in SEEDS if (a_, s) in got)})")
    for s in SEEDS:
        if ("S1U", s) in got and ("S8U", s) in got:
            same = [l for l in open(os.path.join(HERE, "side", f"S1U-{s}", "seasons.txt")) if "\tholistic\t" in l] == \
                   [l for l in open(os.path.join(HERE, "side", f"S8U-{s}", "seasons.txt")) if "\tholistic\t" in l]
            print(f"seed {s}: holistic rows of S8U byte-identical to S1U's (the flag is the designed body's only): {same}")
    ext = [f"{c}-{s}" for (c, s), r in got.items() if r["conventional"]["min"] == 0 or r["holistic"]["min"] == 0]
    print(f"\nextinction of either fauna within 20 seasons: {', '.join(ext) if ext else 'none'}")


if __name__ == "__main__":
    main()
