"""RBT-45 companion: what the *evolved* population actually carries.

The ticket's premise is that the two wheel noses read influence 0.0 "in every
sampled best".  The grid in reach.py measures what the operator proposes; this
reads the same quantity off RBT-23's own saved genotypes -- the 60 bests, one
every ten seasons, and the 60-member final population -- so the drift numbers
have something evolved to be compared against.  Still no world and no selection.
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # so `import reach` works from the repo root

from rabbitstew.analysis import _parent_pool, _run_config
from rabbitstew.genotype import Genotype
from rabbitstew.synthesis import synthesize

import reach  # the readout, so both files score wiring identically

RUN_DIR = reach.RUN_DIR


def rows(genotypes, cfg):
    return [reach.measure_conventional(synthesize(g, cfg.sim.synthesis)) for g in genotypes]


def main():
    cfg = _run_config(RUN_DIR)
    bests = sorted(glob.glob(os.path.join(RUN_DIR, "conventional", "best_gen*.json")))
    out = {"bests": [], "final_population": []}
    for path in bests:
        gen = int(re.search(r"best_gen(\d+)", path).group(1))
        r = reach.measure_conventional(synthesize(Genotype.load(path), cfg.sim.synthesis))
        r["generation"] = gen
        out["bests"].append(r)
    for i, r in enumerate(rows(_parent_pool(RUN_DIR, "conventional"), cfg)):
        r["member"] = i
        out["final_population"].append(r)

    for key in ("bests", "final_population"):
        rs = out[key]
        n = len(rs)
        out[key + "_summary"] = {
            "n": n,
            "pair": sum(r["pair"] for r in rs) / n,
            "half": sum(r["half"] for r in rs) / n,
            "chassis": sum(r["chassis"] for r in rs) / n,
            "uncrossed": sum(r["uncrossed"] for r in rs) / n,
            "crossed": sum(r["crossed"] for r in rs) / n,
            "half_members": [r.get("generation", r.get("member")) for r in rs if r["half"]],
        }
        print(key, json.dumps(out[key + "_summary"]), flush=True)
    with open(os.path.join("runs/RBT-45", "evolved_wiring.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
