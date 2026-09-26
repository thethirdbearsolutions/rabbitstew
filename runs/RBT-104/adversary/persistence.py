"""RBT-104 design adversary, item 3: can the planted seed be purged before selection acts?

No selection, no simulation: the operator alone.  From seed SEED's pre-registered seeded founders
(`seed_founders.py`, the same files S1 and S8 load), each of the 30 planted founders is carried
down REPS independent lineages of `mutate_controller` under part 2's own MutationConfig (read from
the committed runs/RBT-90/forage-SEED/config.json), at link_scale 1 (S1) and 8 (S8; the founder's
links x8 first, as `Ecology.__init__` does).  Crossover is left out (it can only mix in bare
genomes).  At each depth the lineage is read with RBT-91's instruments, imported unchanged:

  structure   the planted global unit still satisfies the predicate (`motif_units`)
  same sign   ... and its own-link response has the founder's sign
  paying      ... and |own links| >= 24.7145, the a = 64 rung (probe_rung.txt)
  whole brain the small-signal response of the whole brain, |a|

Depths are generations of descent; part 2's window depth is 14.0-17.5 (RBT-102).
This is the mutational half of "purged before selection can act": how many generations the
operator gives selection before the planted structure, or its paying magnitude, is gone.

Usage: persistence.py FOUNDERS_DIR SEED [--reps 20] [--procs 4]
"""
import argparse
import glob
import importlib.util
import json
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_spec = importlib.util.spec_from_file_location("sr91", os.path.join(_ROOT, "runs", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

from rabbitstew.evolution import EvolutionConfig  # noqa: E402
from rabbitstew.genetics import mutate_controller, scale_links  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

RUNG = 24.7145
DEPTHS = (0, 1, 2, 4, 8, 12, 16, 20)


def _cfg(seed):
    raw = json.load(open(os.path.join(_ROOT, "runs", "RBT-90", f"forage-{seed}", "config.json")))
    raw.pop("ecology")
    return EvolutionConfig.from_dict(raw)


def planted_unit(ph):
    """The planted unit: the last global unit at founding (the installer appends it)."""
    us = sr.motif_units(ph)
    return us


def lineage(task):
    seed, path, K, rep = task
    cfg = _cfg(seed)
    mcfg = replace(cfg.mutation, link_scale=K)
    g = scale_links(Genotype.load(path), K)
    ph0 = synthesize(g, cfg.sim.synthesis)
    u0 = sr.motif_units(ph0)
    k0 = u0[-1]
    a0 = sr.links_alone_a(ph0, k0)
    rng = np.random.default_rng(np.random.SeedSequence([104, seed, int(K), rep, int(os.path.basename(path)[:3])]))
    out = []
    d = 0
    for depth in DEPTHS:
        while d < depth:
            g = mutate_controller(g, rng, mcfg)
            d += 1
        ph = synthesize(g, cfg.sim.synthesis)
        us = sr.motif_units(ph)
        best = None
        for k in us:
            a = sr.links_alone_a(ph, k)
            if np.isfinite(a) and (best is None or (np.sign(a) == np.sign(a0), abs(a)) > (np.sign(best) == np.sign(a0), abs(best))):
                best = a
        wb = sr.small_signal_a(ph)
        out.append(dict(depth=depth, structure=bool(us), same=bool(best is not None and np.sign(best) == np.sign(a0)),
                        paying=bool(best is not None and np.sign(best) == np.sign(a0) and abs(best) >= RUNG),
                        alone=abs(best) if best is not None else 0.0, whole=abs(wb) if np.isfinite(wb) else float("nan")))
    return K, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("founders")
    ap.add_argument("seed", type=int)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    paths = sorted(glob.glob(os.path.join(a.founders, "conventional", "*.json")))
    planted = [p for p in paths if int(os.path.basename(p)[:3]) % 2 == 0]
    tasks = [(a.seed, p, K, r) for K in (1.0, 8.0) for p in planted for r in range(a.reps)]
    res = {1.0: [], 8.0: []}
    with ProcessPoolExecutor(a.procs) as ex:
        for K, out in ex.map(lineage, tasks, chunksize=4):
            res[K].append(out)
    print(f"# RBT-104 adversary: the planted seed under the operator alone (no selection), seed {a.seed}\n")
    print(f"{len(planted)} planted founders x {a.reps} lineages per K; part 2's MutationConfig; crossover off.\n")
    for K in (1.0, 8.0):
        L = res[K]
        print(f"## K = {K:g}  ({len(L)} lineages)\n")
        print("| depth | structure | same sign | paying (>= a=64 rung, same sign) | own links median | whole brain median |")
        print("|---|---|---|---|---|---|")
        for j, depth in enumerate(DEPTHS):
            rows = [l[j] for l in L]
            n = len(rows)
            f = lambda key: sum(r[key] for r in rows)
            al = np.median([r["alone"] for r in rows])
            wb = np.nanmedian([r["whole"] for r in rows])
            print(f"| {depth} | {f('structure')}/{n} ({100*f('structure')/n:.0f}%) | {100*f('same')/n:.0f}% | "
                  f"{100*f('paying')/n:.0f}% | {al:.3f} | {wb:.4f} |")
        print()


if __name__ == "__main__":
    main()
