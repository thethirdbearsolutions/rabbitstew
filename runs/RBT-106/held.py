"""RBT-106: is the planted compass HELD above what the operator alone leaves? (PREREGISTRATION.md §5.1)

RBT-104's `peek.py` statistic, generalised by one parameter (the criterion) and imported, not
copied: its `own_links` (persistence.py's rule for which predicate unit is read), its
`binom_q95`, and RBT-91's instruments through it.  Per arm, at one season:

  living   the arm's living designed-body genomes at the end of the season (lineage.jsonl)
  root     the founder reached along parents[0]; depth = the number of steps
  planted  a root that carries the routed structure at founding; its sign is its own-link sign
  hit      a genome meeting the arm's CRITERION with its root's sign (a bare-rooted genome
           counts at either sign: a de novo carrier)
  k        hits among all living genomes;   n  living genomes with a planted root
  mu       mean over those n of the operator-alone fraction at each genome's own depth (depth
           capped at 40), from `baseline/baseline-wW-SEED.txt` (baseline.py; no selection)
  B        the 95th percentile of Binomial(n, mu)
  HELD     k > B

The criterion is fixed per founder set, before any arm:
  w = 32 (arms HU, HP):  pay32 -- own-link |a| >= 12.5236 (the a = 32 rung) with the root's sign.
                          Half the planted gain; a = 32 pays on part-2 bodies in both worlds
                          (RBT-103; prize.txt).  Not the a = 64 rung: the planted unit reads
                          24.1 on its own links at founding, AT that rung, so a >= 24.71 test
                          would count founders as not paying (baseline: 40% at depth 0).
  w = 1 (arms P1, S1):   same -- the planted structure with the root's sign, at any magnitude.
                          The w = 1 compass never reaches a paying rung (RBT-104 adversary
                          persistence.txt: 0-1% at a = 64 at every depth), so for it "held" can
                          only mean the structure.

Every approximation errs toward reading HELD (as RBT-104's gate errs toward continuing): bare-rooted
hits enter k and not n, and the living are clustered by descent, so a no-selection arm exceeds B
more often than 5%.  The verdict therefore also needs the paired contrast between worlds (§6.1).

Refuses a season an arm has not finished; refuses the window seasons (300, 599) before the arm has
finished 600 (no partial reads).  Any other season is a smoke test and says so.

Usage: held.py RUN_DIR SEED W [--season 599]
"""
import argparse
import importlib.util
import json
import os
import platform
import sys

import mujoco
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_peek", os.path.join(_ROOT, "runs", "RBT-104", "peek.py"))
peek = importlib.util.module_from_spec(_spec)
sys.modules["rbt104_peek"] = peek
_spec.loader.exec_module(peek)

from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

RUNG32 = 12.5236
WINDOW = (300, 599)
MAX_DEPTH = 40
CRITERION = {32.0: ("pay32", "pay32_frac"), 1.0: ("same", "same_frac")}


def baseline(seed, w, column):
    path = os.path.join(_HERE, "baseline", f"baseline-w{w:g}-{seed}.txt")
    head, p = None, {}
    for line in open(path):
        if line.startswith("# depth"):
            head = line[2:].strip().split("\t")
            continue
        if line.startswith("#"):
            continue
        r = dict(zip(head, line.strip().split("\t")))
        p[int(r["depth"])] = float(r[column])
    return p


def hit(av, s0, crit):
    if av is None:
        return False
    same = s0 is None or np.sign(av) == s0
    return bool(same and (crit == "same" or abs(av) >= RUNG32))


def read(run, seed, w, season, smoke_ok=True):
    """(k, n, mu, B, k_bare, mean depth, living) for one arm at one season; see the module docstring."""
    crit, column = CRITERION[w]
    cfg_raw = json.load(open(os.path.join(run, "config.json")))
    sim = SimConfig.from_dict(cfg_raw["sim"])
    living, parents = [], {}
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != "conventional":
            continue
        parents.setdefault(r["name"], r["parents"])
        if r["generation"] == season and "death" not in r:
            living.append(r["name"])
    gdir = os.path.join(run, "conventional", "genomes")
    ph_of = lambda nm: synthesize(Genotype.load(os.path.join(gdir, f"{nm}.json")), sim.synthesis)
    root_sign = {}

    def root(nm):
        d = 0
        while parents.get(nm):
            nm, d = parents[nm][0], d + 1
        if nm not in root_sign:
            a0 = peek.own_links(ph_of(nm))
            root_sign[nm] = None if a0 is None else float(np.sign(a0))
        return nm, d

    p = baseline(seed, w, column)
    k = k_bare = 0
    mus, depths = [], []
    for nm in living:
        r, d = root(nm)
        s0 = root_sign[r]
        av = peek.own_links(ph_of(nm), sign=s0)
        h = hit(av, s0, crit)
        if s0 is not None:
            depths.append(d)
            mus.append(p[min(d, MAX_DEPTH)])
            k += h
        else:
            k += h
            k_bare += h
    n = len(mus)
    mu = float(np.mean(mus)) if mus else 0.0
    B = peek.binom_q95(n, mu) if n else 0
    return dict(k=k, n=n, mu=mu, B=B, k_bare=k_bare, depth=float(np.mean(depths)) if depths else float("nan"),
                living=len(living), held=k > B, crit=crit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("seed", type=int)
    ap.add_argument("w", type=float)
    ap.add_argument("--season", type=int, default=WINDOW[1])
    a = ap.parse_args()
    run = a.run.rstrip("/")
    cfg_raw = json.load(open(os.path.join(run, "config.json")))
    state = json.load(open(os.path.join(run, "state.json")))
    print(f"# RBT-106 held: {run}, seed {a.seed}, founders w = {a.w:g}, season {a.season}")
    print(f"platform {platform.machine()}, MuJoCo {mujoco.__version__}; the arm's patches "
          f"{cfg_raw['sim']['food']['patches']}, link_scale {cfg_raw['mutation'].get('link_scale', 1.0)}")
    if a.w not in CRITERION or cfg_raw["seed"] != a.seed or not cfg_raw["ecology"].get("seed_conventional"):
        print("REFUSED: held.py reads a seeded arm (founders loaded) of this seed, founders w = 1 or 32")
        sys.exit(2)
    if int(state["season"]) <= a.season:
        print(f"REFUSED: the arm has not finished season {a.season} (state.json season {state['season']})")
        sys.exit(2)
    if a.season in WINDOW and int(state["season"]) < 600:
        print("REFUSED: window readings are post-run; this arm has not finished (no partial reads)")
        sys.exit(2)
    if a.season not in WINDOW and a.season != 150:
        print(f"SMOKE TEST at season {a.season}: not a pre-registered reading")
    r = read(run, a.seed, a.w, a.season)
    print(f"\ncriterion: {r['crit']}; living designed genomes {r['living']}, with a planted root {r['n']} "
          f"(mean depth {r['depth']:.2f})")
    print(f"hits: {r['k'] - r['k_bare']} planted-rooted + {r['k_bare']} bare-rooted = k = {r['k']}")
    print(f"no-selection expectation at matched depth: mu = {r['mu']:.4f} (n mu = {r['n'] * r['mu']:.2f}); 95th percentile B = {r['B']}")
    print(f"\nHELD seed {a.seed} season {a.season}: k = {r['k']}, n = {r['n']}, mu = {r['mu']:.4f}, B = {r['B']} -> "
          f"{'HELD ABOVE NO-SELECTION' if r['held'] else 'AT OR BELOW NO-SELECTION'}")


if __name__ == "__main__":
    main()
