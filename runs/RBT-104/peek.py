"""RBT-104 wave 0: the pre-registered season-150 futility peek (PREREGISTRATION.md §6.2).

Reads ONE thing from ONE arm: the S8 arm's living designed-body genomes at the end of season 150,
through RBT-91's instruments (imported unchanged via the design adversary's `persistence.py`).
It reads no income, no seasons.txt, nothing of S1, and no season after 150.

Per living genome (lineage.jsonl rows, population conventional, generation 150, no death):
  * its ROOT is the founder reached along parents[0]; its DEPTH the number of steps;
  * a founder is PLANTED if it carries the routed structure at founding (the 30 even-i files of
    seed_founders.py), and its SIGN is the sign of its planted unit's own-link response;
  * the genome is PAYING if some predicate unit's own-link |a| >= 24.7145 (the a = 64 rung) with
    the root's sign; a genome rooted in a bare founder counts as paying at that |a| with either sign.
    (persistence.py's rule: among the predicate units, the one with the root's sign and the largest
    |a| is read.)

Statistic, per seed:  k = paying genomes (all roots),  n = living genomes with a planted root.
No-selection expectation: mu = mean over the n planted-rooted genomes of p(depth_i), where p(d) is
the operator-alone paying fraction at depth d (`baseline-SEED.txt`, depths capped at 30).
Bound: B = the 95th percentile of Binomial(n, mu), i.e. the smallest c with P(X <= c) >= 0.95.

  FUTILE on the seed if k <= B.   The gate STOPS the ticket if FUTILE on BOTH wave-0 seeds.

Every approximation errs towards CONTINUING, never towards stopping. Bare-rooted payers are counted
in k but not in n. The living population is clustered in ancestry, so its null spread is wider than
the binomial and a no-selection arm exceeds B more often than 5%.

The same statistic at seasons 300 and 599 (the window's ends) is the F-b reading of §6: S8 has
HELD the paying compass above the no-selection bound on a seed if k > B at both.  Those two
readings are taken after season 599, as post-run steps, never while the arm runs.

Usage: peek.py RUN_DIR SEED [--season 150]      (150: the gate; 300 or 599: the F-b window reading;
                                                 any other season: smoke tests only)
"""
import argparse
import glob
import importlib.util
import json
import math
import os
import platform
import sys

import mujoco
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("persistence", os.path.join(_HERE, "adversary", "persistence.py"))
per = importlib.util.module_from_spec(_spec)
sys.modules["persistence"] = per
_spec.loader.exec_module(per)
sr = per.sr

from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

RUNG = 24.7145
PEEK = 150
WINDOW = (300, 599)


def baseline(seed):
    p = {}
    for line in open(os.path.join(_HERE, f"baseline-{seed}.txt")):
        if line.startswith("#"):
            continue
        d, n, k, frac, hi = line.split("\t")
        p[int(d)] = float(frac)
    return p


def binom_q95(n, mu):
    """Smallest c with P(Binomial(n, mu) <= c) >= 0.95."""
    acc = 0.0
    for c in range(n + 1):
        acc += math.comb(n, c) * mu ** c * (1 - mu) ** (n - c)
        if acc >= 0.95:
            return c
    return n


def own_links(ph, sign=None):
    """(|a|, sign) of the predicate unit read by persistence.py's rule, or None if no structure."""
    best = None
    for k in sr.motif_units(ph):
        a = sr.links_alone_a(ph, k)
        if not np.isfinite(a):
            continue
        key = ((sign is not None and np.sign(a) == sign), abs(a))
        if best is None or key > best[0]:
            best = (key, a)
    return None if best is None else best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("seed", type=int)
    ap.add_argument("--season", type=int, default=PEEK)
    a = ap.parse_args()
    run = a.run.rstrip("/")
    cfg_raw = json.load(open(os.path.join(run, "config.json")))
    K = cfg_raw["mutation"].get("link_scale", 1.0)
    print(f"# RBT-104 wave-0 futility peek: {run}, seed {a.seed}, season {a.season}")
    print(f"platform {platform.machine()}, MuJoCo {mujoco.__version__}; the arm's link_scale {K}")
    if K != 8.0 or cfg_raw["seed"] != a.seed or not cfg_raw["ecology"].get("seed_conventional"):
        print("REFUSED: the peek reads only a seeded S8 arm (link_scale 8, founders loaded) of this seed")
        sys.exit(2)
    if a.season == PEEK:
        print("THE GATE READING (pre-registered, futility only)")
    elif a.season in WINDOW:
        print(f"F-b WINDOW READING at season {a.season} (post-run; not the gate)")
        if int(json.load(open(os.path.join(run, "state.json")))["season"]) < 600:
            print("REFUSED: the window reading is post-run; this arm has not finished (no partial reads)")
            sys.exit(2)
    else:
        print(f"SMOKE TEST at season {a.season}: not the pre-registered peek; its verdict is not a gate reading")
    state = json.load(open(os.path.join(run, "state.json")))
    if int(state["season"]) <= a.season:
        print(f"REFUSED: the arm has not finished season {a.season} (state.json season {state['season']})")
        sys.exit(2)
    sim = SimConfig.from_dict(cfg_raw["sim"])

    living, parents = [], {}
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != "conventional":
            continue
        parents.setdefault(r["name"], r["parents"])
        if r["generation"] == a.season and "death" not in r:
            living.append(r["name"])
    gdir = os.path.join(run, "conventional", "genomes")
    ph_of = lambda n: synthesize(Genotype.load(os.path.join(gdir, f"{n}.json")), sim.synthesis)

    root_sign = {}

    def root(n):
        d = 0
        while parents.get(n):
            n, d = parents[n][0], d + 1
        if n not in root_sign:
            a0 = own_links(ph_of(n))
            root_sign[n] = None if a0 is None else float(np.sign(a0))
        return n, d

    p = baseline(a.seed)
    k = n_planted = 0
    k_bare = 0
    mus, depths = [], []
    for name in living:
        r, d = root(name)
        s0 = root_sign[r]
        av = own_links(ph_of(name), sign=s0)
        if s0 is not None:
            n_planted += 1
            depths.append(d)
            mus.append(p[min(d, 30)])
            k += bool(av is not None and np.sign(av) == s0 and abs(av) >= RUNG)
        else:
            hit = bool(av is not None and abs(av) >= RUNG)
            k += hit
            k_bare += hit
    mu = float(np.mean(mus)) if mus else 0.0
    B = binom_q95(n_planted, mu) if n_planted else 0
    futile = k <= B
    print(f"\nliving designed genomes at season {a.season}: {len(living)}; with a planted root: {n_planted} "
          f"(mean depth {np.mean(depths) if depths else float('nan'):.2f})")
    print(f"paying (same sign as root, own links >= {RUNG}): {k - k_bare} planted-rooted + {k_bare} bare-rooted = k = {k}")
    print(f"no-selection expectation at matched depth: mu = {mu:.4f} (n mu = {n_planted * mu:.2f}); "
          f"95th percentile B = {B}")
    if a.season in WINDOW:
        print(f"\nWINDOW seed {a.seed} season {a.season}: k = {k}, n = {n_planted}, B = {B} -> "
              f"{'AT OR BELOW NO-SELECTION' if futile else 'HELD ABOVE NO-SELECTION'}")
    else:
        print(f"\nPEEK seed {a.seed}: k = {k}, n = {n_planted}, B = {B} -> {'FUTILE' if futile else 'CONTINUE'}")
        print("Rule: FUTILE if k <= B; the ticket STOPS only if both wave-0 seeds (801, 4) read FUTILE.")


if __name__ == "__main__":
    main()
