"""The founding population's base rate for "link-driven effector, no linked oscillator" (RBT-84).

RBT-28's adversary showed all five autopsied arms ran on ONE founding population (seed 801) where
29 of 60 founders already carry that structure, so P(>= 4 of 5 champions sharing it) = 0.17 and the
convergence is suggestive rather than established. This arm runs a second founding population.

The classifier is `runs/RBT-28/adversary_founders.py::wiring`, imported rather than reimplemented,
so the two base rates are the same measurement. Reproducing their 29/60 at seed 801 is the check
that it is.

**The seed is chosen by a stated rule and its base rate is reported as found.** Shopping seeds for a
convenient base rate would be tuning, and the rule the ticket gives is only that the founders differ.

usage: founder_base_rate.py [SEED ...]
"""
import importlib.util
import json
import pathlib
import sys

import numpy as np

from rabbitstew.evolution import HOLISTIC, EvolutionConfig, initial_population

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

cfg0 = json.load(open(ROOT / "runs" / "RBT-28" / "data" / "baseline-801" / "config.json"))
seeds = [int(x) for x in sys.argv[1:]] or [801, 807]

print(f"{'seed':>6} {'founders':>9} {'eff-driven':>11} {'osc-linked':>11} "
      f"{'BOTH (drive, no osc)':>21} {'base rate':>10}")
sigs = {}
for seed in seeds:
    evo = EvolutionConfig.from_dict({k: v for k, v in cfg0.items() if k != "ecology"})
    evo.population_size = cfg0["ecology"]["capacity"]
    evo.seed = seed
    founders = list(initial_population(HOLISTIC, evo, np.random.default_rng(seed)).members)
    w = [adv.wiring(g, evo.sim) for g in founders]   # wiring() wants the object carrying .synthesis
    drive = sum(x["eff_driven"] > 0 for x in w)
    osc = sum(x["osc_linked"] > 0 for x in w)
    both = sum(x["eff_driven"] > 0 and x["osc_linked"] == 0 for x in w)
    sigs[seed] = {adv.shape_sig(g) for g in founders}
    print(f"{seed:6d} {len(founders):9d} {drive:11d} {osc:11d} {both:21d} {both / len(founders):10.3f}")

if len(seeds) == 2:
    a, b = seeds
    shared = sigs[a] & sigs[b]
    print(f"\nbody signatures shared between seed {a} and seed {b}: {len(shared)} "
          f"of {len(sigs[a])} and {len(sigs[b])} distinct")
    print(f"-> the founding populations {'DIFFER' if len(shared) < min(len(sigs[a]), len(sigs[b])) else 'OVERLAP'}"
          f", which is the one thing RBT-84 requires of the seed.")
