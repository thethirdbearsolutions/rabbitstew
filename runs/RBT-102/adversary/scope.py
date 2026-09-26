"""RBT-102 adversary, probe 4: scope -- what was read, and could anything outside it carry the motif?

1. COUNTS. Genomes saved at birth per arm (conventional fauna) against RBT-102's 12,276, and the
   seasons each arm's lineage covers.
2. THE GLOBAL-ONLY CLAUSE. RBT-91's predicate looks only at GLOBAL non-sensor units. A local neuron
   in a node that neighbours both wheels (the Pioneer root) could route the same computation, since
   a wheel brain may take a link from a neighbouring node's unit (genotype.py validate). This counts
   local non-sensor, non-effector units in the part-2 genomes, and applies the predicate's own rule
   (opposite-sign in from both wheel noses, same-sign out to both drive Effectors, summed weights,
   no magnitude) to EVERY non-sensor unit, local or global, so a route the predicate cannot see
   would show here.

    python runs/RBT-102/adversary/scope.py runs/RBT-90/forage-{1,2,...}
"""
import glob
import importlib.util
import json
import os
import sys
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_argv, sys.argv = sys.argv, ["structural_rate.py"]
_s = importlib.util.spec_from_file_location("sr", os.path.join(ROOT, "runs", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(_s)
_s.loader.exec_module(sr)
sys.argv = _argv

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

SIM = None


def _init(d):
    global SIM
    SIM = SimConfig.from_dict(d)


def one(path):
    ph = synthesize(Genotype.load(path), SIM.synthesis)
    noses = sr._wheel_noses(ph)
    le, re_ = sr.drive_effector_units(ph)
    local_neurons = sum(1 for ui in ph.units if ui.part is not None and ui.unit.kind == "neuron")
    if noses is None or not le or not re_:
        return local_neurons, False, False
    n_L, n_R = noses
    e_L, e_R = le[0], re_[0]
    w = {}
    for s, d, x in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + x
    any_unit = local = False
    for k, ui in enumerate(ph.units):
        if ui.unit.kind == "sensor":
            continue
        a, b = w.get((n_L, k), 0.0), w.get((n_R, k), 0.0)
        c, d = w.get((k, e_L), 0.0), w.get((k, e_R), 0.0)
        ok = (a != 0.0 and b != 0.0 and np.sign(a) != np.sign(b)
              and c != 0.0 and d != 0.0 and np.sign(c) == np.sign(d))
        any_unit |= ok
        local |= ok and ui.part is not None
    return local_neurons, any_unit, local


def main():
    print("# RBT-102 adversary probe 4: scope\n")
    print("| seed | genomes saved | lineage seasons | genomes with a local neuron | local neurons max "
          "| predicate rule on ANY non-sensor unit | of which on a local unit |")
    print("|---|---|---|---|---|---|---|")
    tot = np.zeros(4, dtype=int)
    for arm in sys.argv[1:]:
        cfg = json.load(open(os.path.join(arm, "config.json")))
        paths = sorted(glob.glob(os.path.join(arm, "conventional", "genomes", "*.json")))
        seasons = set()
        for line in open(os.path.join(arm, "lineage.jsonl")):
            r = json.loads(line)
            if r["population"] == "conventional":
                seasons.add(r["generation"])
        with get_context("fork").Pool(4, initializer=_init, initargs=(cfg["sim"],)) as pool:
            rows = pool.map(one, paths, chunksize=16)
        c = [len(paths), sum(r[0] > 0 for r in rows), sum(r[1] for r in rows), sum(r[2] for r in rows)]
        tot += c
        print(f"| {cfg['seed']} | {c[0]} | {min(seasons)}-{max(seasons)} ({len(seasons)}) | {c[1]} | "
              f"{max(r[0] for r in rows)} | {c[2]} | {c[3]} |")
    print(f"| **all** | **{tot[0]}** | | **{tot[1]}** | | **{tot[2]}** | **{tot[3]}** |")


if __name__ == "__main__":
    main()
