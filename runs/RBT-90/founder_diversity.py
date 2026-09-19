"""Founding-population diversity, defined and measured per seed, from the sixty founders alone (RBT-90 part 1).

No simulation.  A holistic founding population is a pure function of the run's ``seed``, its
mutation vocabulary and the ecology ``capacity`` (``initial_population`` -> ``random_genotype``;
RBT-28's adversary, RBT-84's ``reproducible.py``), so every number here regenerates from a
committed ``config.json``.  The five calibration seeds' configs (801, 804, 805, 806, 807) differ
only in the food economy, the worker count and the seed, none of which the founders read; the
script checks that and refuses a config whose vocabulary or capacity differs from seed 801's.

Per seed, ``docs/artifacts/founders-<seed>.txt`` carries:

* the base rates of a **link-driven effector**, a **linked oscillator** and the **composite**
  ("drive, no oscillator": a link-driven effector and no linked oscillator), on
  ``runs/RBT-28/adversary_founders.py::wiring`` imported rather than reimplemented, as RBT-84 did,
  so the rates are the same measurement as RBT-28's 29/60 and RBT-84's 29/60 (reproduced here);
  RBT-84 section 5's caveat travels with the composite: ``wiring`` asks "is there a link into a
  live effector", which a fan-out from a central driver also satisfies;
* the part-count, unit-count, node-count and link-count distributions;
* the body signatures (``shape_sig``: node shapes in order with each node's unit kinds and
  sources) and, because that signature is never shared between random draws, the coarser
  **shape multiset** (the sorted node shapes, order and brains dropped) that is;
* one row per founder.

Across a set of seeds, ``docs/artifacts/RBT-90-calibration.txt`` carries the pairwise sharing of
both body measures and the verdict of the rule in ``docs/founder-diversity.md``: (1) bodies
distinct, pass/fail; (2) the set's composite rates span both quartiles of the generator, pass/fail;
(3) seeds outside the generator's central 90% band are labelled, kept and named, never excluded.
The thresholds come from the generator's own reference distribution, ``--reference N``: the same
statistics over seeds 1..N (``docs/artifacts/RBT-90-reference.txt`` and ``.json``), which is what
"a typical draw" means here.  The direction-of-travel split is NOT measured: it needs the direction probe
(``scripts/travel_direction.py``, 16 bouts per genome under MuJoCo), and for a random body the
axis "forward" is measured against has to be defined first; RBT-69's is the Pioneer chassis yaw.

usage: founder_diversity.py [--reference N] [SEED ...]        (default seeds: 801 804 805 806 807)
"""
import importlib.util
import json
import pathlib
import sys
from collections import Counter

import numpy as np

from rabbitstew.evolution import HOLISTIC, EvolutionConfig, initial_population

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ART = ROOT / "docs" / "artifacts"
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

CALIBRATION = (801, 804, 805, 806, 807)
CONFIGS = {  # each calibration seed's own committed config; every other seed uses 801's
    801: "runs/RBT-28/data/baseline-801/config.json",
    804: "runs/RBT-71/forage-804/config.json",
    805: "runs/RBT-71/forage-805/config.json",
    806: "runs/RBT-71/forage-806/config.json",
    807: "runs/RBT-84/forage-807/config.json",
}
# The rule (docs/founder-diversity.md).  Bands are percentiles of the generator reference.
MAX_SHARED_BODIES = 1   # clause 1, pass/fail: of 60, per pair (full signature)
MIN_DISTINCT = 58       # clause 1, pass/fail: of 60, within a seed (full signature)
SPAN = (25, 75)         # clause 2, pass/fail: a set's composite rates must reach both reference quartiles
BAND = (5, 95)          # clause 3, a label: a seed outside the reference's central 90% is kept and named


def founders(seed):
    raw = json.load(open(ROOT / CONFIGS.get(seed, CONFIGS[801])))
    base = json.load(open(ROOT / CONFIGS[801]))
    if raw["mutation"] != base["mutation"] or raw["ecology"]["capacity"] != base["ecology"]["capacity"]:
        raise SystemExit(f"seed {seed}: its config's vocabulary or capacity differs from seed 801's; "
                         "the founders would not be one flag away from forage-801")
    evo = EvolutionConfig.from_dict({k: v for k, v in raw.items() if k != "ecology"})
    evo.population_size = raw["ecology"]["capacity"]
    evo.seed = seed
    return evo, list(initial_population(HOLISTIC, evo, np.random.default_rng(seed)).members)


def shape_multiset(g):
    return tuple(sorted(int(n.segment.shape) for n in g.nodes))


def measure(seed):
    evo, F = founders(seed)
    W = [adv.wiring(g, evo.sim) for g in F]
    n = len(F)
    return {
        "seed": seed, "n": n, "config": CONFIGS.get(seed, CONFIGS[801]),
        "drive": sum(w["eff_driven"] > 0 for w in W),
        "osc": sum(w["osc_linked"] > 0 for w in W),
        "both": sum(w["eff_driven"] > 0 and w["osc_linked"] == 0 for w in W),
        "parts": [w["parts"] for w in W], "units": [w["units"] for w in W],
        "links": [w["links"] for w in W], "nodes": [len(g.nodes) for g in F],
        "sigs": [adv.shape_sig(g) for g in F], "shapes": [shape_multiset(g) for g in F],
        "W": W, "F": F,
    }


def rates(m):
    return {"drive": m["drive"] / m["n"], "osc": m["osc"] / m["n"], "both": m["both"] / m["n"],
            "parts_median": float(np.median(m["parts"])), "units_median": float(np.median(m["units"]))}


def q(xs, ps=(0, 25, 50, 75, 100)):
    return " ".join(f"{np.percentile(xs, p):g}" for p in ps)


def hist(xs):
    c = Counter(xs)
    return "  ".join(f"{k}:{c[k]}" for k in sorted(c))


def write_seed(m, ref):
    r = rates(m)
    L = [f"RBT-90 founding population, seed {m['seed']}: the {m['n']} holistic founders regenerated from {m['config']}",
         "(seed, mutation vocabulary and ecology capacity; nothing else in the config reaches them).  No simulation.",
         "",
         "## base rates (runs/RBT-28/adversary_founders.py::wiring, imported; RBT-28 and RBT-84's classifier)",
         f"  link-driven effector (>= 1 live effector with a link into it): {m['drive']}/{m['n']} = {r['drive']:.3f}",
         f"  linked oscillator    (>= 1 oscillator sensor with an outgoing link): {m['osc']}/{m['n']} = {r['osc']:.3f}",
         f"  composite 'drive, no oscillator' (both of: link-driven effector, no linked oscillator): {m['both']}/{m['n']} = {r['both']:.3f}",
         "  caveat (RBT-84 section 5): 'link into a live effector' is also satisfied by a fan-out from a central",
         "  driver, so the composite reads as more than it measures; it is reported as the wiring number it is.",
         "",
         "## size distributions (min q25 median q75 max)",
         f"  parts: {q(m['parts'])}     histogram {hist(m['parts'])}",
         f"  units: {q(m['units'])}     histogram {hist(m['units'])}",
         f"  nodes: {q(m['nodes'])}     histogram {hist(m['nodes'])}",
         f"  links: {q(m['links'])}",
         "",
         "## bodies",
         f"  distinct full body signatures (shape_sig: node shapes in order + each node's unit kinds/sources): {len(set(m['sigs']))}/{m['n']}",
         f"  distinct shape multisets (sorted node shapes only): {len(set(m['shapes']))}/{m['n']}",
         "  the fraction shared with every other seed is in docs/artifacts/RBT-90-calibration.txt",
         "",
         "## direction of travel: NOT MEASURED",
         "  needs the direction probe (scripts/travel_direction.py: 16 MuJoCo bouts per genome), and for a random",
         "  body the axis 'forward' is read against must be defined first (RBT-69's is the Pioneer chassis yaw).",
         "  This is the named missing measurement of RBT-90 part 1.",
         ""]
    if ref:
        L += ["## against the generator reference (docs/artifacts/RBT-90-reference.txt), central 90% band",
              *(f"  {k:13s} {r[k]:8.3f}   band [{ref[k][0]:.3f}, {ref[k][1]:.3f}]   {'inside' if ref[k][0] <= r[k] <= ref[k][1] else 'OUTSIDE'}"
                for k in ("drive", "osc", "both", "parts_median", "units_median")),
              ""]
    L += ["## one row per founder",
          f"  {'name':7s} {'nodes':>5s} {'parts':>5s} {'units':>5s} {'links':>5s} {'eff':>4s} {'driven':>6s} {'osc':>4s} {'linked':>6s} {'smell':>5s} {'linked':>6s}  shapes"]
    for g, w, s in zip(m["F"], m["W"], m["shapes"]):
        L.append(f"  {g.name:7s} {len(g.nodes):5d} {w['parts']:5d} {w['units']:5d} {w['links']:5d} {w['eff']:4d} {w['eff_driven']:6d} "
                 f"{w['osc']:4d} {w['osc_linked']:6d} {w['food']:5d} {w['food_linked']:6d}  {list(s)}")
    (ART / f"founders-{m['seed']}.txt").write_text("\n".join(L) + "\n")
    return r


def reference(n):
    rows = [rates(measure(s)) for s in range(1, n + 1)]
    keys = ("drive", "osc", "both", "parts_median", "units_median")
    band = {k: (float(np.percentile([r[k] for r in rows], BAND[0])), float(np.percentile([r[k] for r in rows], BAND[1]))) for k in keys}
    span = {k: (float(np.percentile([r[k] for r in rows], SPAN[0])), float(np.percentile([r[k] for r in rows], SPAN[1]))) for k in keys}
    L = [f"RBT-90 generator reference: the same statistics over seeds 1..{n}, sixty founders each, seed 801's config.",
         "What 'a typical draw' means for the rule in docs/founder-diversity.md.  No simulation.",
         "",
         f"{'statistic':13s} {'min':>7s} {'p5':>7s} {'q25':>7s} {'median':>7s} {'q75':>7s} {'p95':>7s} {'max':>7s}"]
    for k in keys:
        xs = [r[k] for r in rows]
        L.append(f"{k:13s} " + " ".join(f"{np.percentile(xs, p):7.3f}" for p in (0, 5, 25, 50, 75, 95, 100)))
    L += ["", f"per-seed rows ({n}):", f"{'seed':>5s} {'drive':>7s} {'osc':>7s} {'both':>7s} {'parts':>6s} {'units':>6s}"]
    L += [f"{s:5d} {r['drive']:7.3f} {r['osc']:7.3f} {r['both']:7.3f} {r['parts_median']:6g} {r['units_median']:6g}" for s, r in enumerate(rows, 1)]
    (ART / "RBT-90-reference.txt").write_text("\n".join(L) + "\n")
    json.dump({"n": n, "band": band, "span": span}, open(ART / "RBT-90-reference.json", "w"), indent=1)
    return {"n": n, "band": band, "span": span}


def calibrate(seeds, ref):
    M = {s: measure(s) for s in seeds}
    R = {s: write_seed(M[s], ref["band"] if ref else None) for s in seeds}
    L = [f"RBT-90 calibration set: seeds {' '.join(map(str, seeds))}.  Per-seed readouts: docs/artifacts/founders-<seed>.txt.",
         "", "## per seed",
         f"{'seed':>5s} {'drive':>7s} {'osc':>7s} {'both':>7s} {'parts':>6s} {'units':>6s} {'distinct':>8s} {'shapes':>6s}"]
    for s in seeds:
        r, m = R[s], M[s]
        L.append(f"{s:5d} {r['drive']:7.3f} {r['osc']:7.3f} {r['both']:7.3f} {r['parts_median']:6g} {r['units_median']:6g} "
                 f"{len(set(m['sigs'])):5d}/{m['n']} {len(set(m['shapes'])):3d}/{m['n']}")
    L += ["", "## pairwise: founders of A whose body occurs among B's, and of B's among A's (full signature | shape multiset)",
          f"{'A':>5s} {'B':>5s} {'full A>B':>9s} {'B>A':>6s} {'shapes A>B':>11s} {'B>A':>6s}"]
    verdict = {"bodies": True, "span": True, "outliers": []}

    def shared(a, b, key):
        return sum(x in set(M[b][key]) for x in M[a][key])

    for i, a in enumerate(seeds):
        for b in seeds[i + 1:]:
            fab, fba, sab, sba = shared(a, b, "sigs"), shared(b, a, "sigs"), shared(a, b, "shapes"), shared(b, a, "shapes")
            L.append(f"{a:5d} {b:5d} {fab:6d}/{M[a]['n']} {fba:3d}/{M[b]['n']} {sab:8d}/{M[a]['n']} {sba:3d}/{M[b]['n']}")
            verdict["bodies"] &= max(fab, fba) <= MAX_SHARED_BODIES
    for s in seeds:
        verdict["bodies"] &= len(set(M[s]["sigs"])) >= MIN_DISTINCT
    L += ["", "## the rule (docs/founder-diversity.md)"]
    L.append(f"  1. bodies: every pair shares <= {MAX_SHARED_BODIES}/60 full signatures and every seed has >= {MIN_DISTINCT}/60 distinct: "
             f"{'PASS' if verdict['bodies'] else 'FAIL'}")
    if ref:
        lo, hi = ref["span"]["both"]
        both = [R[s]["both"] for s in seeds]
        verdict["span"] = min(both) <= lo and max(both) >= hi
        L.append(f"  2. span: the set's composite rates reach both reference quartiles [{lo:.3f}, {hi:.3f}] (seeds 1..{ref['n']}): "
                 f"min {min(both):.3f} max {max(both):.3f}: {'PASS' if verdict['span'] else 'FAIL'}")
        for k in ("drive", "osc"):
            xs = [R[s][k] for s in seeds]
            L.append(f"     ({k}: min {min(xs):.3f} max {max(xs):.3f}, reference quartiles [{ref['span'][k][0]:.3f}, {ref['span'][k][1]:.3f}]; reported, not ruled on)")
        keys = ("drive", "osc", "both", "parts_median", "units_median")
        verdict["outliers"] = [(s, k, R[s][k]) for s in seeds for k in keys if not ref["band"][k][0] <= R[s][k] <= ref["band"][k][1]]
        L.append(f"  3. label: seeds outside the generator's central 90% band on any statistic, kept and named: "
                 f"{verdict['outliers'] or 'none'}")
        L.append(f"  verdict: {'DIVERSE ENOUGH' if verdict['bodies'] and verdict['span'] else 'NOT DIVERSE ENOUGH'} under clauses 1 and 2 as stated")
    else:
        L.append("  2-3. need the reference: run with --reference N first")
    L += ["", "## direction of travel: NOT MEASURED (needs the direction probe; see any founders-<seed>.txt)"]
    text = "\n".join(L)
    (ART / "RBT-90-calibration.txt").write_text(text + "\n")
    return text, verdict


def main(argv):
    ref = None
    seeds = []
    it = iter(argv)
    for a in it:
        if a == "--reference":
            ref = reference(int(next(it)))
        else:
            seeds.append(int(a))
    if ref is None and (ART / "RBT-90-reference.json").exists():
        ref = json.load(open(ART / "RBT-90-reference.json"))
    text, _ = calibrate(tuple(seeds) or CALIBRATION, ref)
    print(text)


if __name__ == "__main__":
    main(sys.argv[1:])
