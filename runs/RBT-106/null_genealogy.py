"""RBT-106 §6.3, layer 3: how often does `held.py` call HELD when nothing selects the compass?

held.py compares k (living genomes still carrying the planted compass) against B, the binomial 95th
percentile of the operator-alone expectation.  The living are related, so a no-selection arm exceeds B
more often than 5% (RBT-104 §6.2 stated this and left it unmeasured).  This measures it, per seed:

  the genealogy  RBT-90 part 2's own (lineage.jsonl, restored from ckpt/rbt-90-SEED), a real
                 600-season genealogy under selection on gait and income, with no compass anywhere
  the plant      RBT-106's founders (founders.py, w = 32 or 1) put at part 2's founders: founder
                 c0-i gets founder file i (checked: the bare odd-i files equal part 2's saved c0-i)
  the operator   RBT-104's adversary persistence.py's operator, down that genealogy: every genome is
                 its first parent's genotype passed once through `mutate_controller` under part 2's
                 MutationConfig (crossover left out, as in the baseline); one draw per birth, shared by
                 all its descendants; REPS independent replicates
  the call       held.py's own rule (`held.read`'s arithmetic, imported: criterion, baseline table at
                 each genome's depth, binomial B) at the two window seasons

Printed: per seed and season, the replicates' k, n, B and the fraction called HELD; and the fraction
HELD at both 300 and 599 (the arm-level call the verdict uses): the false-positive rate of HELD under
real clustering, which power.py's layer 2 takes as q under "no effect".

At K = 8 the founders' links are scaled and every draw is x8, as --link-scale 8 does (the genealogy
stays part 2's, which is the K = 1 one: the null is "this operator on a real clustered genealogy").

Usage: null_genealogy.py PART2_RUN SEED W FOUNDERS_DIR [--k 8] [--reps 20] [--procs 4]
"""
import argparse
import importlib.util
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt106_held", os.path.join(_HERE, "held.py"))
held = importlib.util.module_from_spec(_spec)
sys.modules["rbt106_held"] = held
_spec.loader.exec_module(held)
peek, per = held.peek, held.peek.per

from rabbitstew.genetics import mutate_controller, scale_links  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

G = {}


def genealogy(run):
    parents, living = {}, {}
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != "conventional":
            continue
        parents.setdefault(r["name"], r["parents"])
        if "death" not in r:
            living.setdefault(r["generation"], []).append(r["name"])
    return parents, living


def replicate(task):
    rep, seasons = task
    run, seed, w, fdir, K = G["run"], G["seed"], G["w"], G["fdir"], G["k"]
    parents, living = G["parents"], G["living"]
    cfg = per._cfg(seed)
    mcfg = replace(cfg.mutation, link_scale=K)
    cache = {}

    def geno(nm):
        chain = []
        while nm not in cache and parents.get(nm):
            chain.append(nm)
            nm = parents[nm][0]
        if nm not in cache:
            i = int(nm.split("-")[1])
            cache[nm] = (scale_links(Genotype.load(os.path.join(fdir, "conventional", f"{i:03d}.json")), K), 0, nm)
        g, d, root = cache[nm]
        for c in reversed(chain):
            rng = np.random.default_rng(np.random.SeedSequence([106, seed, int(w), int(K), rep] + [ord(ch) for ch in c]))
            g, d = mutate_controller(g, rng, mcfg), d + 1
            cache[c] = (g, d, root)
        return cache[chain[0]] if chain else cache[nm]

    crit, column = held.CRITERION[(w, K)]
    p = held.baseline(seed, w, column, K)
    out = []
    root_sign = {}
    for s in seasons:
        k = kb = 0
        mus = []
        for nm in living.get(s, []):
            g, d, root = geno(nm)
            if root not in root_sign:
                a0 = peek.own_links(synthesize(cache[root][0], cfg.sim.synthesis))
                root_sign[root] = None if a0 is None else float(np.sign(a0))
            s0 = root_sign[root]
            av = peek.own_links(synthesize(g, cfg.sim.synthesis), sign=s0)
            h = held.hit(av, s0, crit)
            if s0 is not None:
                mus.append(p[min(d, held.MAX_DEPTH)])
                k += h
            else:
                k += h
                kb += h
        n = len(mus)
        mu = float(np.mean(mus)) if mus else 0.0
        B = peek.binom_q95(n, mu) if n else 0
        out.append(dict(season=s, k=k, kb=kb, n=n, mu=mu, B=B, held=k > B, depth=None))
    return rep, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("seed", type=int)
    ap.add_argument("w", type=float)
    ap.add_argument("founders")
    ap.add_argument("--k", type=float, default=1.0)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--seasons", default="300,599")
    a = ap.parse_args()
    seasons = [int(x) for x in a.seasons.split(",")]
    parents, living = genealogy(a.run)
    # founder mapping check: part 2's saved bare founders are the odd-i founder files
    bad = 0
    for i in range(1, 60, 2):
        mine = Genotype.load(os.path.join(a.founders, "conventional", f"{i:03d}.json")).to_dict()
        theirs = Genotype.load(os.path.join(a.run, "conventional", "genomes", f"c0-{i}.json")).to_dict()
        mine.pop("record", None), theirs.pop("record", None)
        bad += mine != theirs
    G.update(run=a.run, seed=a.seed, w=a.w, k=a.k, fdir=a.founders, parents=parents, living=living)
    with ProcessPoolExecutor(a.procs, mp_context=get_context("fork")) as ex:  # G is inherited by fork
        res = sorted(ex.map(replicate, [(r, seasons) for r in range(a.reps)]))
    print(f"# RBT-106 null genealogy: seed {a.seed}, founders w = {a.w:g}, K = {a.k:g}, part 2's genealogy {a.run}, {a.reps} replicates")
    print(f"founder mapping: part 2's saved c0-i equals founder file i for {30 - bad} of 30 bare (odd) i")
    print("| rep | " + " | ".join(f"s{s} k/n/B" for s in seasons) + " | HELD at all |")
    print("|---|" + "---|" * (len(seasons) + 1))
    allh = 0
    per_season = {s: 0 for s in seasons}
    for rep, out in res:
        h = all(o["held"] for o in out)
        allh += h
        for o in out:
            per_season[o["season"]] += o["held"]
        print(f"| {rep} | " + " | ".join(f"{o['k']}/{o['n']}/{o['B']}{' H' if o['held'] else ''}" for o in out) + f" | {h} |")
    print("\n" + ", ".join(f"HELD at season {s}: {per_season[s]}/{len(res)}" for s in seasons))
    print(f"NULL seed {a.seed} w {a.w:g} K {a.k:g}: HELD at every window season in {allh} of {len(res)} replicates")


if __name__ == "__main__":
    main()
