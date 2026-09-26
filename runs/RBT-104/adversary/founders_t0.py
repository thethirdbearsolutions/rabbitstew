"""RBT-104 design adversary, item 3 (the coordinator's condition 2): what does the seed cost, and
does it steer, at t = 0, in each primary arm?

For seed SEED's pre-registered founders (seed_founders.py; the files S1 and S8 load), each of the
30 planted founders i is paired with its own bare twin (the same founder before the install; its
bare draw is `seed_founders.part2_ecology(SEED)`'s founder i).  Four genotypes per i:

  S1 seeded   = the planted founder                 U1 bare = its bare twin          (K = 1)
  S8 seeded   = the planted founder, links x 8      U8 bare = its bare twin, links x 8 (K = 8)

each scored by RBT-103's `income_bout`, unchanged (RBT-90 part 2's world), on SEEDS paired seeds
from 7000, under real smell and under RBT-97's rotated decoy.  Reported, t over the 30 founders:

  cost    seeded - bare, real smell (the seed's t = 0 income cost in that arm)
  F       intact(real) - intact(decoy) for seeded and bare, and the difference (does the planted
          compass make the founder food-dependent at t = 0?)
  and the arm-level contrast of K: U8 bare - U1 bare (what the flag alone costs a founder).

Usage: founders_t0.py SEED [--seeds 16] [--procs 4]
"""
import argparse
import importlib.util
import os
import sys
from multiprocessing import get_context

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


rp = _load("rbt103_routed_populations", os.path.join(_ROOT, "runs", "RBT-103", "routed_populations.py"))
sf = _load("rbt104_seed_founders", os.path.join(_ROOT, "runs", "RBT-104", "seed_founders.py"))

from rabbitstew.evolution import CONVENTIONAL  # noqa: E402
from rabbitstew.genetics import scale_links  # noqa: E402

RUN = os.path.join(_ROOT, "runs", "RBT-90", "forage-801")  # world config only (the same in every part-2 arm)
BODY = {}


def bout(task):
    i, cond, seed, decoy = task
    orig = rp.genotype
    rp.genotype = lambda run_, kind_, gen_: BODY[(gen_, cond)]
    try:
        _, s, v, x = rp.income_bout((RUN, "conventional", i, 0.0, 0.0, seed, decoy))
    finally:
        rp.genotype = orig
    return i, cond, decoy, s, v, x


def t_int(v):
    v = np.asarray(v, float)
    se = v.std(ddof=1) / np.sqrt(len(v))
    t = 2.045 if len(v) == 30 else 2.0
    return v.mean(), v.mean() - t * se, v.mean() + t * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=int)
    ap.add_argument("--seeds", type=int, default=16)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    rp.RUN[RUN] = rp.config(RUN)
    e = sf.part2_ecology(a.seed)
    bare = [g.copy() for g in e.populations[CONVENTIONAL]]
    e.runner.close()
    seeded = sf.seeded(a.seed)
    planted = [i for i in range(len(seeded)) if i % 2 == 0]
    for i in planted:
        BODY[(i, "S1")] = seeded[i]
        BODY[(i, "U1")] = bare[i]
        BODY[(i, "S8")] = scale_links(seeded[i].copy(), 8.0)
        BODY[(i, "U8")] = scale_links(bare[i].copy(), 8.0)
    seeds = [7000 + j for j in range(a.seeds)]
    tasks = [(i, c, s, d) for i in planted for c in ("S1", "U1", "S8", "U8") for s in seeds for d in (False, True)]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=8)
    got = {(i, c, d, s): v for i, c, d, s, v, _ in rows}
    blew = sum(1 for *_, x in rows if x)
    m = lambda i, c, d: float(np.mean([got[(i, c, d, s)] for s in seeds]))
    print(f"# RBT-104 adversary: the seeded founders at t = 0, seed {a.seed}\n")
    print(f"{len(planted)} planted founders, each against its bare twin; {a.seeds} paired seeds from 7000; "
          f"RBT-103's income_bout in part 2's world; exploded bouts {blew}/{len(rows)}\n")
    print("| quantity (items per bout; t over founders) | K = 1 (S1) | K = 8 (S8) |")
    print("|---|---|---|")
    fmt = lambda x: f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"
    for name, f in (
        ("bare founder income (real smell)", lambda i, K: m(i, "U" + K, False)),
        ("seeded founder income (real smell)", lambda i, K: m(i, "S" + K, False)),
        ("**cost: seeded - bare** (real smell)", lambda i, K: m(i, "S" + K, False) - m(i, "U" + K, False)),
        ("F seeded: real - decoy", lambda i, K: m(i, "S" + K, False) - m(i, "S" + K, True)),
        ("F bare: real - decoy", lambda i, K: m(i, "U" + K, False) - m(i, "U" + K, True)),
        ("**F seeded - F bare** (the planted compass's own food dependence)",
         lambda i, K: (m(i, "S" + K, False) - m(i, "S" + K, True)) - (m(i, "U" + K, False) - m(i, "U" + K, True))),
    ):
        print(f"| {name} | {fmt(t_int([f(i, '1') for i in planted]))} | {fmt(t_int([f(i, '8') for i in planted]))} |")
    k = t_int([m(i, "U8", False) - m(i, "U1", False) for i in planted])
    print(f"\nthe flag alone on a bare founder, U8 - U1 (real smell): {fmt(k)}")
    print("per-sign split, cost seeded - bare at K = 8: "
          + ", ".join(f"sign {'+' if sg == 0 else '-'} {fmt(t_int([m(i, 'S8', False) - m(i, 'U8', False) for i in planted if i % 4 == sg]))}"
                      for sg in (0, 2)))


if __name__ == "__main__":
    main()
