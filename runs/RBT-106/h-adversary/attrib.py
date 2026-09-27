"""RBT-106 H readout adversary, attack 2: is the H lines' food dependence the PLANTED unit acting as a compass?

function.py's ATTRIBUTION lesion removes every link from a wheel's food nose into ANY global unit.  That
credits "the compass" but not which unit: another nose-fed global unit could be doing the steering.  And
F12 flagged HP-804/805/806, whose planted unit carries a drifted bias (resting drive 3-7): is what pays a
static turning bias rather than steering by smell?  This probe splits the lesion, on the same bests,
harness and paired seeds as function.py (its `bout`, imported: RBT-103's income_bout, nothing re-implemented).

  planted unit   a global unit fed by a wheel nose whose largest output weight to a drive Effector is
                 >= 16 in magnitude (the planted motif sits at v = 32; F12's planted-type units with |v| ~ 1
                 are not it).  Found per best with f12.planted_units.
  conditions     (real smell unless marked)
    intact           the champion                                       (function.py)
    decoy            the champion, rotated-decoy smell                  (function.py)
    lesion_all       every nose -> global link removed                  (function.py's lesion)
    lesion_planted   nose -> planted-unit links removed only: its input half.  Its bias, and so its resting
                     drive, is kept: a static turning bias would survive this lesion
    lesion_other     nose -> global links removed into every unit EXCEPT the planted unit(s)
    cut_planted      the planted unit's links to the drive Effectors removed: no compass, no resting drive
    bias0            the planted unit's bias set to 0 (resting drive 0), links kept
  read
    gain_planted = intact - lesion_planted    (the planted unit's input carries the gain)
    gain_other   = intact - lesion_other      (other nose-fed units carry it)
    static       = lesion_planted - cut_planted   (what the planted unit's resting drive earns with no smell input)
    drift        = intact - bias0             (what the drifted bias adds or costs)
  Each is a mean over 64 paired seeds per best, then t(6) over the bests.

Usage: attrib.py --run RUN [--seeds 64] [--procs 4]   (from a checkout whose rabbitstew/ is c872e80's)
"""
import argparse
import importlib.util
import math
import os
import sys
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(D))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


f12 = _load("rbt106_f12", os.path.join(D, "f12.py"))
fn = f12.fn   # RBT-104's function.py as f12 (via sat_probe) already loaded it: one module object, picklable
rp, routed, mech = fn.rp, fn.routed, fn.mech
BIG = 16.0


def planted(g):
    return [k for k, fu, b, vs, d in f12.planted_units(g) if max(abs(v) for v in vs) >= BIG]


def lesion_into(g, keep=None, only=None):
    r = g.copy()
    nose, _ = routed.unit_indices(r)
    if r.global_brain is not None:
        def cut(l):
            if not (l.src.node in routed.WHEELS and l.src.index == nose and l.dst.node is None):
                return False
            if only is not None:
                return l.dst.index in only
            return l.dst.index not in (keep or ())
        r.global_brain.links = [l for l in r.global_brain.links if not cut(l)]
    return r


def cut_out(g, ks):
    r = g.copy()
    _, eff = routed.unit_indices(r)
    for nd in routed.WHEELS:
        br = r.nodes[nd].segment.brain
        br.links = [l for l in br.links if not (l.src.node is None and l.src.index in ks and l.dst.node == nd and l.dst.index == eff)]
    return r


def bias0(g, ks):
    r = g.copy()
    for k in ks:
        r.global_brain.units[k].bias = 0.0
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--seeds", type=int, default=64)
    p.add_argument("--procs", type=int, default=4)
    a = p.parse_args()
    run = a.run.rstrip("/")
    seeds = [7000 + i for i in range(a.seeds)]
    cfg = rp.config(run)
    rp.RUN[run] = cfg
    print(f"# RBT-106 H adversary attribution probe: {run}")
    print(f"world: {cfg.food.items} items, patches {cfg.food.patches}; bests {list(fn.GENS)}; {a.seeds} paired seeds from 7000")
    gens, units, others = [], {}, {}
    for gen in fn.GENS:
        g = rp.genotype(run, "conventional", gen)
        ks = planted(g)
        units[gen] = [(k, fu, b, vs, d) for k, fu, b, vs, d in f12.planted_units(g) if k in ks]
        nose, _ = routed.unit_indices(g)
        nl = [l.dst.index for l in (g.global_brain.links if g.global_brain else [])
              if l.src.node in routed.WHEELS and l.src.index == nose and l.dst.node is None]
        others[gen] = (sum(1 for x in nl if x not in ks), len(set(x for x in nl if x not in ks)))
        fn.BODY[(gen, "intact")] = g
        fn.BODY[(gen, "lesion_all")] = fn.lesion(g)
        if ks:
            fn.BODY[(gen, "lesion_planted")] = lesion_into(g, only=set(ks))
            fn.BODY[(gen, "lesion_other")] = lesion_into(g, keep=set(ks))
            fn.BODY[(gen, "cut_planted")] = cut_out(g, set(ks))
            fn.BODY[(gen, "bias0")] = bias0(g, ks)
        gens.append(gen)
    conds = [("intact", False), ("intact", True), ("lesion_all", False), ("lesion_planted", False),
             ("lesion_other", False), ("cut_planted", False), ("bias0", False)]
    tasks = [(run, gen, c, s, d) for gen in gens for c, d in conds if (gen, c) in fn.BODY for s in seeds]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(fn.bout, tasks, chunksize=16)
    got = {(gen, c, d, s): v for gen, c, d, s, v, _ in rows}
    M = lambda gen, c, d=False: float(np.mean([got[(gen, c, d, s)] for s in seeds])) if (gen, c, d, seeds[0]) in got else float("nan")

    print("\n| best | planted unit(s): func, b, v, resting drive | intact | decoy | lesion_all | lesion_planted | lesion_other | cut_planted | bias0 |")
    print("|---|---|---|---|---|---|---|---|---|")
    stat = {k: [] for k in ("gain_all", "gain_planted", "gain_other", "static", "drift", "F")}
    for gen in gens:
        desc = "; ".join(f"u{k} {fu} b {b:+.3f} v [{', '.join(f'{v:+.1f}' for v in vs)}] drive {'n/a' if d is None else f'{d:.2f}'}"
                         for k, fu, b, vs, d in units[gen]) or "none"
        desc += f"; other nose->global links {others[gen][0]} into {others[gen][1]} unit(s)"
        it, dc, la = M(gen, "intact"), M(gen, "intact", True), M(gen, "lesion_all")
        lp, lo, cp, b0 = (M(gen, c) for c in ("lesion_planted", "lesion_other", "cut_planted", "bias0"))
        print(f"| g{gen} | {desc} | {it:.3f} | {dc:.3f} | {la:.3f} | {lp:.3f} | {lo:.3f} | {cp:.3f} | {b0:.3f} |")
        stat["F"].append(it - dc)
        stat["gain_all"].append(it - la)
        if units[gen]:
            stat["gain_planted"].append(it - lp)
            stat["gain_other"].append(it - lo)
            stat["static"].append(lp - cp)
            stat["drift"].append(it - b0)
            stat.setdefault("gain_all_pl", []).append(it - la)
    print("\n## t over bests (bests without a planted unit enter F and gain_all only)")
    for k, lab in (("F", "F = intact - decoy (function.py PRIMARY)"), ("gain_all", "gain, every nose->global link cut (function.py)"),
                   ("gain_planted", "gain, the planted unit's input cut only"), ("gain_other", "gain, every OTHER unit's nose input cut"),
                   ("static", "resting drive's own earnings (lesion_planted - cut)"), ("drift", "intact - bias0 (what the drifted bias adds)")):
        v = stat[k]
        if len(v) >= 2:
            m, lo_, hi_ = mech.t_interval(v)
            print(f"    {lab:52s} {m:+8.3f} [{lo_:+8.3f}, {hi_:+8.3f}]  (bests {len(v)})")
        else:
            print(f"    {lab:52s} n/a (bests {len(v)})")
    ga = np.mean(stat["gain_all_pl"]) if stat["gain_planted"] else float("nan")
    gp = np.mean(stat["gain_planted"]) if stat["gain_planted"] else float("nan")
    print(f"\nATTRIB {os.path.basename(run)}: planted-unit share of the compass gain {gp / ga if ga else float('nan'):.2f} "
          f"(mean gain_planted / mean gain_all over bests with a planted unit: {len(stat['gain_planted'])}/{len(gens)})")


if __name__ == "__main__":
    main()
