"""RBT-102 pre-registration inputs. Measured BEFORE any RBT-90 part-2 arm is restored.

Nothing here reads an arm. It draws Pioneer founders from the part-2 configuration with seeds no
arm uses, and asks three things the pre-registration needs to state a prediction and a control:

  1. FOUNDER RATE: how often a freshly drawn part-2 founder already carries the routed motif's
     structure (RBT-91's predicate, imported unmodified). RBT-91's drift rate was measured from
     EVOLVED committed parents (W4b-801 bests, P-801 final 60); part 2 starts from random founders.
  2. MATCHED MUTATION-ONLY CHAIN: the same founders taken through k = 19 `mutate_controller` steps
     with the part-2 operator and no selection -- RBT-91's denominator (19 mutations, one lineage),
     but from part 2's founder distribution. A secondary reference only; not a drift ARM (no
     crossover, no demography).
  3. POSITIVE-CONTROL DRY RUN: `genotype_motif.install` (RBT-87's routed motif) into founders,
     predicate must say yes; bare founder recorded beside it. The pre-registered control runs on
     arm genomes after restore; this checks the install lands on part-2 genomes at all.
  4. BUDGET: wall time of the predicate and of RBT-80's reference probe (16 x 15 s) per genome.

The config is `part2-dryrun/config.json`: `rabbitstew.cli ecology` with part2_run.sh's exact flags,
--seasons 0 and --seed 999 (no arm uses 999), so it is the arms' config in every field but seeds.

Usage: runs/RBT-102/prereg_inputs.py [n_pops=100] [procs=4]
"""
import importlib.util
import json
import os
import sys
import time
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_argv, sys.argv = sys.argv, ["structural_rate.py"]
_s = importlib.util.spec_from_file_location("ra", os.path.join(ROOT, "runs", "RBT-91", "resign_arrivals.py"))
ra = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ra)
sys.argv = _argv
sr = ra.sr  # RBT-91's structural_rate, as resign_arrivals imports it: the predicate, unmodified

from rabbitstew.evolution import CONVENTIONAL, EvolutionConfig, initial_population
from rabbitstew.genetics import mutate_controller
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

CFG = json.load(open(os.path.join(HERE, "part2-dryrun/config.json")))
EVO = EvolutionConfig.from_dict({k: v for k, v in CFG.items() if k != "ecology"})
SIM = SimConfig.from_dict(CFG["sim"])
K = 19
BASE = 1_020_260_926  # founder-draw seeds BASE + i; no arm seed is anywhere near


def one_pop(i):
    rng = np.random.default_rng(BASE + i)
    founders = list(initial_population(CONVENTIONAL, EVO, rng).members)
    f_hit = chain_hit = 0
    for g in founders:
        f_hit += bool(sr.motif_units(synthesize(g, SIM.synthesis)))
        c = g
        for _ in range(K):
            c = mutate_controller(c, rng, EVO.mutation)
        chain_hit += bool(sr.motif_units(synthesize(c, SIM.synthesis)))
    return len(founders), f_hit, chain_hit


def main():
    n_pops = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    print("# RBT-102 pre-registration inputs (no arm read)\n")
    print(f"config: runs/RBT-102/part2-dryrun/config.json; operator add_link_rate="
          f"{EVO.mutation.add_link_rate} remove_link_rate={EVO.mutation.remove_link_rate} "
          f"weight_sigma={EVO.mutation.weight_sigma}; k = {K}\n")
    with get_context("fork").Pool(procs) as pool:
        rows = pool.map(one_pop, range(n_pops))
    n = sum(r[0] for r in rows)
    f = sum(r[1] for r in rows)
    c = sum(r[2] for r in rows)
    fl, fh = sr.wilson(f, n)
    cl, ch = sr.wilson(c, n)
    print(f"1. founder rate      : {f} of {n} = {100 * f / n:.3f}% [{100 * fl:.3f}, {100 * fh:.3f}] (Wilson 95%)")
    print(f"   populations (60 each) with >= 1 founder carrier: {sum(1 for r in rows if r[1])} of {n_pops}")
    print(f"2. matched chain k=19: {c} of {n} = {100 * c / n:.3f}% [{100 * cl:.3f}, {100 * ch:.3f}] (Wilson 95%)")
    dl, dh = sr.wilson(84, 200_000)
    print(f"   RBT-91 drift rate  : 84 of 200000 = 0.042% [{100 * dl:.4f}, {100 * dh:.4f}] (Wilson 95%)\n")

    # 3. positive-control dry run on independent founders
    gm_spec = importlib.util.spec_from_file_location("gm", os.path.join(ROOT, "scripts", "genotype_motif.py"))
    gm = importlib.util.module_from_spec(gm_spec)
    gm_spec.loader.exec_module(gm)
    rng = np.random.default_rng(BASE - 1)
    sample = list(initial_population(CONVENTIONAL, EVO, rng).members)[:20]
    ok = bare = fail = 0
    for g in sample:
        bare += bool(sr.motif_units(synthesize(g, SIM.synthesis)))
        for w, sign in ((1.0, +1.0), (8.0, -1.0)):
            try:
                ok += bool(sr.motif_units(synthesize(gm.install(g, w, sign=sign), SIM.synthesis)))
            except RuntimeError:
                fail += 1
    print(f"3. positive-control dry run: installed motif detected {ok} of {2 * len(sample)} "
          f"(install invalid {fail}); bare founders detected {bare} of {len(sample)}\n")

    # 4. budget
    g = sample[0]
    t = time.time()
    for _ in range(200):
        sr.motif_units(synthesize(g, SIM.synthesis))
    tp = (time.time() - t) / 200

    class _C:
        sim = SIM
    t = time.time()
    h, R = ra.heading(g, _C, seeds=16, dur=15.0)
    tr = time.time() - t
    print(f"4. budget: predicate {1000 * tp:.2f} ms/genome; reference probe 16 x 15 s "
          f"{tr:.1f} s/genome (single core; heading {h}, R {R:.2f})")


if __name__ == "__main__":
    main()
