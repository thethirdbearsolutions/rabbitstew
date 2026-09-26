"""RBT-104 readout (b): is a champion food-dependent?  RBT-97/RBT-103's harness, pointed at the
circuit a champion EVOLVED rather than one installed into it.

RBT-103 scored an installed motif against the bare body, and its mechanism check as how much of
that gain survives the rotated-live-layout decoy (RBT-97 item 3: the food sensors smell the live
layout rotated about the arena centre by one angle per body and seed, so item count, geometry and
depletion are kept and only the correlation with where the food is goes).  An evolved champion
has no bare version to subtract, so the primary quantity drops the base:

  PRIMARY   F = intact(real smell) - intact(rotated decoy), per body the mean over 64 paired
            seeds from 7000, t(df = n - 1) over the bodies.  FOOD-DEPENDENT if the interval
            excludes zero from above and RBT-38's zero-count veto passes (more than half of the
            paired seeds reading exactly equal means smell is not being used: vetoed).  For an
            installed motif, F is exactly RBT-103's "motif - decoy".

  ATTRIBUTION  with base = the champion **compass-lesioned** (every link from a wheel's food
            nose into a global unit removed: the input half of the routed motif, the only compass
            the genotype can hold, paper 8 section 1.3), RBT-103's rule unchanged: gain = intact
            - lesioned, decoy = intact(rotated) - lesioned; the compass is food-dependent if the
            decoy retains under 25% of the gain and gain - decoy excludes zero.  The lesion cuts only
            the compass's input half, so any other use a champion makes of its noses (a tonic
            drive, a pirouette) stays in the base and is not credited to a compass.

The bout is RBT-103's `income_bout` (the Simulation, the RotatedSmell subclass, the per-body angle
seed [seed, gen, 97]), called with w = 0 on a genotype this script hands it, so nothing of the
harness is re-implemented.

POSITIVE CONTROL (`--install W[,S]`): install RBT-97's routed motif at output weight W and input
weight S (default 1; S > 1 is the geometry a raised --link-scale gives it), signed per body by its
direction of travel with RBT-103's two probes.  The champion plus motif is then "the champion" and
must read FOOD-DEPENDENT.  With --harness-check the script also scores RBT-103's own motif - bare
and decoy - bare on the same bodies, which must reproduce RBT-103's committed row to the digit,
and the bare champion's own F, which is the negative control.

Usage:
  function.py --run RUN [--gens 300,350,400,450,500,550,590] [--install 32[,1]] [--harness-check]
"""
import argparse
import importlib.util
import json
import os
import sys
from multiprocessing import get_context

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


rp = _load("rbt103_routed_populations", os.path.join(_ROOT, "runs", "RBT-103", "routed_populations.py"))
routed, mech, g500 = rp.routed, rp.mech, rp.g500

from rabbitstew.genotype import Genotype  # noqa: E402

GENS = (300, 350, 400, 450, 500, 550, 590)  # the second half of a 600-season arm, RBT-102's window
BODY = {}  # (gen, condition) -> Genotype, set before the pool forks


def lesion(g):
    """The same genotype with every link from a wheel's food nose into a global unit removed."""
    r = g.copy()
    nose, _ = routed.unit_indices(r)
    if r.global_brain is not None:
        r.global_brain.links = [l for l in r.global_brain.links
                                if not (l.src.node in routed.WHEELS and l.src.index == nose)]
    return r


def install(g, w, s, sign):
    """RBT-97's routed motif, input links scaled to +-s (s = 1 is the installer unchanged)."""
    r = routed.install(g, w, sign=sign)
    k = len(r.global_brain.units) - 1
    for l in r.global_brain.links:
        if l.dst.node is None and l.dst.index == k and l.src.node in routed.WHEELS:
            l.weight *= s
    return r


def bout(task):
    """RBT-103's income_bout on a prepared genotype: it loads by (run, kind, gen), so the prepared
    genotype is swapped in for the duration of the call."""
    run, gen, cond, seed, decoy = task
    orig = rp.genotype
    rp.genotype = lambda run_, kind_, gen_: BODY[(gen_, cond)]
    try:
        key, s, v, x = rp.income_bout((run, "conventional", gen, 0.0, 0.0, seed, decoy))
    finally:
        rp.genotype = orig
    return gen, cond, decoy, s, v, x


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--gens", default=None)
    p.add_argument("--install", default=None, help="W[,S]: positive control, the routed motif at output W, input S")
    p.add_argument("--harness-check", action="store_true", dest="harness_check")
    p.add_argument("--seeds", type=int, default=64)
    p.add_argument("--seed0", type=int, default=7000)
    p.add_argument("--procs", type=int, default=4)
    a = p.parse_args()
    run = a.run.rstrip("/")
    gens = GENS if not a.gens else tuple(int(x) for x in a.gens.split(","))
    seeds = [a.seed0 + i for i in range(a.seeds)]
    cfg = rp.config(run)
    rp.RUN[run] = cfg
    inst = None if not a.install else tuple(float(x) for x in (a.install.split(",") + ["1"])[:2])

    print(f"# RBT-104 readout (b): is the champion's use of smell food-dependent?  {run}")
    print(f"bodies: conventional bests {list(gens)}; {a.seeds} paired seeds from {seeds[0]}")
    print(f"world: {cfg.food.items} items, radius {cfg.food.radius:g}, patches {cfg.food.patches}, "
          f"regrow {cfg.food.regrow}, duration {cfg.duration:g}s")
    link_scale = json.load(open(f"{run}/config.json"))["mutation"].get("link_scale", 1.0)
    print(f"run's --link-scale: {link_scale:g}")

    sign = {}
    if inst:
        w, s = inst
        print(f"\nPOSITIVE CONTROL: RBT-97's routed motif installed in every body, output w = {w:g}, "
              f"input +-{s:g} (linear a = {2 * w * s:g}), signed by direction of travel")
        tasks = [(run, "conventional", gen, i, k) for k in g500.PROBES for gen in gens for i in range(16)]
        with get_context("fork").Pool(a.procs) as pool:
            rows = pool.map(rp.direction_bout, tasks, chunksize=4)
        by = {}
        for r in rows:
            by.setdefault((r[1], r[0]), []).append(r[2:])
        for gen in gens:
            backs = []
            for k in g500.PROBES:
                sn = sum(x[0] for x in by[(k, gen)]); cs = sum(x[1] for x in by[(k, gen)]); n = sum(x[2] for x in by[(k, gen)])
                backs.append(abs(float(np.degrees(np.arctan2(sn / n, cs / n)))) > 90 if n else None)
            if backs[0] is not None and backs[0] == backs[1]:
                sign[gen] = +1.0 if backs[0] == mech.rs.PUBLISHED_IS_BACKWARD else -1.0
        print("  signs: " + ", ".join(f"g{g} {sign[g]:+.0f}" if g in sign else f"g{g} UNDETERMINED" for g in gens))
        gens = tuple(g for g in gens if g in sign)

    for gen in gens:
        g = rp.genotype(run, "conventional", gen)
        if inst:
            g = install(g, inst[0], inst[1], sign[gen])
        BODY[(gen, "intact")] = g
        BODY[(gen, "lesioned")] = lesion(g)
        if inst and a.harness_check:
            BODY[(gen, "bare")] = rp.genotype(run, "conventional", gen)
    conds = [("intact", False), ("intact", True), ("lesioned", False)]
    if inst and a.harness_check:
        conds += [("bare", False), ("bare", True)]
    tasks = [(run, gen, c, s_, d) for gen in gens for c, d in conds for s_ in seeds]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=16)
    got = {(gen, c, d, s_): v for gen, c, d, s_, v, _ in rows}
    blew = sum(1 for *_, x in rows if x)
    excl = lambda lo_, hi_: (lo_ > 0) == (hi_ > 0)

    def primary(cond, title):
        per, zeros = [], 0
        for gen in gens:
            dd = [got[(gen, cond, False, s_)] - got[(gen, cond, True, s_)] for s_ in seeds]
            zeros += sum(1 for x in dd if x == 0.0)
            per.append(float(np.mean(dd)))
        m, lo, hi = mech.t_interval(per)
        veto = zeros > len(gens) * len(seeds) / 2
        v = ("FOOD-DEPENDENT" if lo > 0 and not veto else "VETOED by the zero count" if veto
             else "NEGATIVE" if hi < 0 else "not food-dependent")
        print(f"    {title:34s} F {m:+8.3f} [{lo:+8.3f}, {hi:+8.3f}]  {v}  (zeros {zeros}/{len(gens) * len(seeds)})")
        return per, m, lo, hi, v

    print(f"\n## Per body, mean over {a.seeds} paired seeds (items)")
    print(f"{'gen':>6s} {'intact':>7s} {'decoy':>7s} {'lesion':>7s} | {'F':>8s} {'gain':>8s} {'ret. decoy':>10s}")
    gain, dec = [], []
    for gen in gens:
        it = np.mean([got[(gen, 'intact', False, s_)] for s_ in seeds])
        dc = np.mean([got[(gen, 'intact', True, s_)] for s_ in seeds])
        le = np.mean([got[(gen, 'lesioned', False, s_)] for s_ in seeds])
        gain.append(float(it - le))
        dec.append(float(dc - le))
        print(f"g{gen:<5d} {it:7.3f} {dc:7.3f} {le:7.3f} | {it - dc:+8.3f} {it - le:+8.3f} {dc - le:+10.3f}")
    print("\n## PRIMARY: intact(real) - intact(rotated decoy), t over bodies")
    _, fm, flo, fhi, fv = primary("intact", "the champion")
    print("\n## ATTRIBUTION: the compass lesion as base, RBT-103's rule")
    m, mlo, mhi = mech.t_interval(gain)
    d, dlo, dhi = mech.t_interval(dec)
    f, glo, ghi = mech.t_interval([x - y for x, y in zip(gain, dec)])
    frac = float(np.mean(dec)) / float(np.mean(gain)) if abs(np.mean(gain)) > 1e-9 else float("nan")
    att = ("no compass gain" if not mlo > 0 else
           "FOOD-DEPENDENT" if frac < 0.25 and excl(glo, ghi) else
           "GAIT EFFECT" if frac >= 0.75 and excl(dlo, dhi) else "UNRESOLVED at this n")
    print(f"    {'gain (intact - lesioned)':34s} {m:+8.3f} [{mlo:+8.3f}, {mhi:+8.3f}]")
    print(f"    {'decoy (rotated - lesioned)':34s} {d:+8.3f} [{dlo:+8.3f}, {dhi:+8.3f}]")
    print(f"    {'gain - decoy':34s} {f:+8.3f} [{glo:+8.3f}, {ghi:+8.3f}];  the decoy retains {100 * frac:.1f}%")
    print(f"    compass: {att}   (exploded bouts {blew}/{len(rows)})")
    print(f"\nLINE {os.path.basename(run)}: {fv}  F {fm:+.3f} [{flo:+.3f}, {fhi:+.3f}]  compass {att}  bodies {len(gens)}")

    if inst and a.harness_check:
        md = [float(np.mean([got[(g_, 'intact', False, s_)] - got[(g_, 'bare', False, s_)] for s_ in seeds])) for g_ in gens]
        dd = [float(np.mean([got[(g_, 'intact', True, s_)] - got[(g_, 'bare', False, s_)] for s_ in seeds])) for g_ in gens]
        mm, ml, mh = mech.t_interval(md)
        dm, dl, dh = mech.t_interval(dd)
        print(f"\n## Harness check: RBT-103's own scoring on these bodies (motif - bare, rotated decoy - bare)")
        print(f"    motif  {mm:+.3f} [{ml:+.3f}, {mh:+.3f}]")
        print(f"    decoy  {dm:+.3f} [{dl:+.3f}, {dh:+.3f}]   retains {100 * dm / mm:.1f}%")
        print("\n## NEGATIVE CONTROL: the bare champion's own F")
        primary("bare", "bare champion (no install)")


if __name__ == "__main__":
    main()
