"""RBT-106 design adversary: the "held" null with the operator's crossover put back.

The designer's null (`runs/RBT-106/null_genealogy.py`, imported here, not edited) carries each
genome down its FIRST parent only, one `mutate_controller` draw per birth, "crossover left out, as in
the baseline".  But the ecology's designed-body operator is `crossover_controller` THEN
`mutate_controller` (rabbitstew/ecology.py `_breed`): with probability crossover_rate (0.3) a breeder
takes a mate, and `crossover_controller` then hands the child the MATE's whole global brain with
probability 0.5.  RBT-97's routed motif is a global unit, so in ~15% of births the compass a child
carries comes from parents[1], not along the parents[0] chain that held.py uses for root, sign and
depth.  Two consequences the designer's null cannot see:

  * bare-rooted genomes (parents[0] root bare) can carry a planted compass got by crossover, and
    held.py counts them as hits "at either sign" in k while they enter neither n nor mu;
  * planted-rooted genomes can lose it to a bare mate's global brain (erasure) or carry a copy with a
    different depth than their parents[0] depth.

This probe re-runs the designer's null on the same real part-2 genealogies (lineage.jsonl, both
parents recorded), the same founders and plant, the same held.py arithmetic (criterion, baseline
table at each genome's parents[0] depth, binomial B), with the operator as the ecology applies it:
for a child with parents [p0, p1], child = mutate_controller(crossover_controller(g(p0), g(p1)), ...),
and with parents [p0] alone, mutate_controller(g(p0)).  One rng per birth (keyed like the designer's).

Printed per replicate: k (planted-rooted hits + bare-rooted hits), n, B, HELD at each season; the
arm-level rate (HELD at every listed season) under the full operator; and, in the same replicate
stream, the designer's mutation-only operator for reference.

Usage: null_xover.py PART2_RUN SEED W FOUNDERS_DIR [--k 8] [--reps 20] [--procs 4] [--seasons 300,599]
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
_D = os.path.dirname(_HERE)
_spec = importlib.util.spec_from_file_location("rbt106_null_genealogy", os.path.join(_D, "null_genealogy.py"))
ng = importlib.util.module_from_spec(_spec)
sys.modules["rbt106_null_genealogy"] = ng
_spec.loader.exec_module(ng)
held, peek, per = ng.held, ng.peek, ng.per

from rabbitstew.genetics import crossover_controller, mutate_controller, scale_links  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

G = {}


def lineage(run):
    """parents (both, as recorded), birth order, and the living per season."""
    parents, order, living = {}, [], {}
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != "conventional":
            continue
        if r["name"] not in parents:
            parents[r["name"]] = r["parents"]
            order.append(r["name"])
        if "death" not in r:
            living.setdefault(r["generation"], []).append(r["name"])
    return parents, order, living


def replicate(task):
    rep, seasons, xover = task
    seed, w, fdir, K = G["seed"], G["w"], G["fdir"], G["k"]
    parents, order, living = G["parents"], G["order"], G["living"]
    cfg = per._cfg(seed)
    mcfg = replace(cfg.mutation, link_scale=K)
    geno, depth, root = {}, {}, {}
    need = set()
    for s in seasons:
        need.update(living.get(s, []))
    # every genome in birth order (parents are born before children); founders from the files
    for nm in order:
        ps = parents[nm]
        if not ps:
            i = int(nm.split("-")[1])
            geno[nm] = scale_links(Genotype.load(os.path.join(fdir, "conventional", f"{i:03d}.json")), K)
            depth[nm], root[nm] = 0, nm
            continue
        rng = np.random.default_rng(np.random.SeedSequence([106, seed, int(w), int(K), rep] + [ord(ch) for ch in nm]))
        g = geno[ps[0]]
        if xover and len(ps) > 1:
            g = crossover_controller(g, geno[ps[1]], rng)
        geno[nm] = mutate_controller(g, rng, mcfg)
        depth[nm], root[nm] = depth[ps[0]] + 1, root[ps[0]]
    crit, column = held.CRITERION[(w, K)]
    p = held.baseline(seed, w, column, K)
    root_sign = {}
    out = []
    for s in seasons:
        k = kb = 0
        mus = []
        for nm in living.get(s, []):
            r = root[nm]
            if r not in root_sign:
                a0 = peek.own_links(synthesize(geno[r], cfg.sim.synthesis))
                root_sign[r] = None if a0 is None else float(np.sign(a0))
            s0 = root_sign[r]
            av = peek.own_links(synthesize(geno[nm], cfg.sim.synthesis), sign=s0)
            h = held.hit(av, s0, crit)
            if s0 is not None:
                mus.append(p[min(depth[nm], held.MAX_DEPTH)])
                k += h
            else:
                k += h
                kb += h
        n = len(mus)
        mu = float(np.mean(mus)) if mus else 0.0
        B = peek.binom_q95(n, mu) if n else 0
        out.append(dict(season=s, k=k, kb=kb, n=n, mu=mu, B=B, held=k > B))
    return rep, xover, out


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
    parents, order, living = lineage(a.run)
    nx = sum(len(parents[n]) > 1 for n in order)
    nb = sum(len(parents[n]) > 0 for n in order)
    G.update(seed=a.seed, w=a.w, k=a.k, fdir=a.founders, parents=parents, order=order, living=living)
    tasks = [(r, seasons, x) for x in (True, False) for r in range(a.reps)]
    with ProcessPoolExecutor(a.procs, mp_context=get_context("fork")) as ex:
        res = list(ex.map(replicate, tasks))
    print(f"# RBT-106 adversary null with crossover: seed {a.seed}, founders w = {a.w:g}, K = {a.k:g}, {a.reps} replicates")
    print(f"designed-body births in the genealogy: {nb}; with a mate recorded: {nx} ({nx / nb:.3f}); "
          f"the mate's global brain is taken with probability 0.5 (crossover_controller)")
    for x in (True, False):
        label = "FULL OPERATOR (crossover_controller then mutate_controller)" if x else "designer's operator (mutate_controller down parents[0] only)"
        print(f"\n## {label}")
        print("| rep | " + " | ".join(f"s{s} k(bare)/n/B" for s in seasons) + " | HELD at all |")
        print("|---|" + "---|" * (len(seasons) + 1))
        allh, per_s, kb_tot, k_tot = 0, {s: 0 for s in seasons}, 0, 0
        for rep, xx, out in sorted(r for r in res if r[1] == x):
            h = all(o["held"] for o in out)
            allh += h
            for o in out:
                per_s[o["season"]] += o["held"]
                kb_tot += o["kb"]
                k_tot += o["k"]
            print(f"| {rep} | " + " | ".join(f"{o['k']}({o['kb']})/{o['n']}/{o['B']}{' H' if o['held'] else ''}" for o in out) + f" | {h} |")
        print(", ".join(f"HELD at season {s}: {per_s[s]}/{a.reps}" for s in seasons)
              + f"; bare-rooted share of k: {kb_tot}/{k_tot}")
        print(f"NULL{'-XOVER' if x else '-MUTONLY'} seed {a.seed} w {a.w:g} K {a.k:g}: HELD at every listed season in {allh} of {a.reps}")


if __name__ == "__main__":
    main()
