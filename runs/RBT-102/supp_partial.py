"""RBT-102 SUPPLEMENTARY, POST HOC, NOT VERDICT-BEARING: why is the structural carriage zero?

Written after seven arms read zero carriers, so it is labelled post hoc and nothing in PREREG.md's
rule depends on it. It asks two descriptive questions of every genome an arm saved at birth:

  APPLICABLE  -- does the genome still have what RBT-91's predicate needs (both wheel `food` noses
                 and both drive Effectors)? A zero over genomes that lost their noses would mean
                 something different from a zero over genomes that kept them.
  ONE NOSE    -- how often some global non-sensor unit takes a link from at least one wheel nose.
  HALVES      -- how often each HALF of the routed structure is present on some global non-sensor
                 unit, using the predicate's own sign convention (summed weight per pair):
                   in-half   : links in from BOTH noses, OPPOSITE sign
                   out-half  : links out to BOTH drive Effectors, SAME sign
                 and how often both halves sit on the same unit (= the predicate).

The helpers are RBT-91's (`_wheel_noses`, `drive_effector_units`), imported unmodified.

    python runs/RBT-102/supp_partial.py runs/RBT-90/forage-SEED [...]
"""
import glob
import importlib.util
import json
import os
import sys
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
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
    if noses is None or not le or not re_:
        return (False, False, False, False, False, False)
    n_L, n_R = noses
    e_L, e_R = le[0], re_[0]
    w = {}
    for s, d, x in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + x
    any_in = any_out = both = False
    any_in_any_sign = False
    one_nose = False
    for k, ui in enumerate(ph.units):
        if ui.part is not None or ui.unit.kind == "sensor":
            continue
        a, b = w.get((n_L, k), 0.0), w.get((n_R, k), 0.0)
        c, d = w.get((k, e_L), 0.0), w.get((k, e_R), 0.0)
        in_any = a != 0.0 and b != 0.0
        one_nose |= a != 0.0 or b != 0.0
        in_ok = in_any and np.sign(a) != np.sign(b)
        out_ok = c != 0.0 and d != 0.0 and np.sign(c) == np.sign(d)
        any_in_any_sign |= in_any
        any_in |= in_ok
        any_out |= out_ok
        both |= in_ok and out_ok
    return (True, one_nose, any_in_any_sign, any_in, any_out, both)


def main():
    print("# RBT-102 SUPPLEMENTARY (post hoc, not verdict-bearing): applicability and half-structures\n")
    print("| seed | genomes | applicable | a unit fed by >= 1 nose | a unit fed by both noses (any sign) | in-half (opposite) | out-half (same) | both on one unit |")
    print("|---|---|---|---|---|---|---|---|")
    tot = np.zeros(7, dtype=int)
    for arm in sys.argv[1:]:
        cfg = json.load(open(os.path.join(arm, "config.json")))
        paths = sorted(glob.glob(os.path.join(arm, "conventional", "genomes", "*.json")))
        with get_context("fork").Pool(4, initializer=_init, initargs=(cfg["sim"],)) as pool:
            rows = pool.map(one, paths, chunksize=16)
        c = np.array([len(rows)] + [sum(r[i] for r in rows) for i in range(6)])
        tot += c
        print(f"| {cfg['seed']} | " + " | ".join(str(x) for x in c) + " |")
    print(f"| **all** | " + " | ".join(f"**{x}**" for x in tot) + " |")


if __name__ == "__main__":
    main()
