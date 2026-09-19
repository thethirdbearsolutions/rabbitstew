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
distinct, pass/fail, on the full signature alone; (2) the set's composite rates AND its linked-
oscillator rates each span both quartiles of the generator, pass/fail; (3) seeds outside the
generator's central 90% band are labelled, kept and named, never excluded.  The thresholds come
from the generator's own reference distribution, ``--reference N``: the same statistics over seeds
1..N (``docs/artifacts/RBT-90-reference.txt`` and ``.json``), which is what "a typical draw" means
here.  **The ``.json`` is authoritative**: the quartiles are achievable values (28/60, 33/60, 11/60,
15/60) that many seeds sit on exactly, so the ``.txt``'s three-decimal print cannot re-derive the
rule's own pass rates (the adversary's probe 1).  Rates are printed as ``k/60`` for that reason.
The shape multiset is reported and read by no clause: it is a strict coarsening of the full
signature over a hardcoded three-shape vocabulary (the adversary's probe 2).

The direction-of-travel split (RBT-69's forward against backward) is undefined on a holistic
founding population, shown rather than assumed: the adversary's ``adversary_direction.py`` runs the
probe in each body's own root frame and finds the per-founder mean directions isotropic.  Each
``founders-<seed>.txt`` carries that probe's summary row when its readout
(``docs/artifacts/RBT-90-adversary-direction-<seed>.txt``) exists, and says to run it when not.

``--choose N``: the part-2 set, committed before any run.  The five calibration seeds are kept and
the further seeds are the lexicographically first combination, by seed number from the reference's
candidates, whose union with the five passes clauses 1 and 2 (``docs/artifacts/RBT-90-part2-seeds.txt``).

usage: founder_diversity.py [--reference N] [--choose N] [SEED ...]        (default seeds: 801 804 805 806 807)
"""
import importlib.util
import itertools
import json
import pathlib
import re
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
SPAN = (25, 75)         # clause 2, pass/fail: a set's composite AND linked-oscillator rates must each reach both reference quartiles
SPAN_ON = ("both", "osc")  # the two statistics clause 2 is ruled on; "drive" is reported beside them
BAND = (5, 95)          # clause 3, a label: a seed outside the reference's central 90% is kept and named


def founders(seed):
    raw = json.load(open(ROOT / CONFIGS.get(seed, CONFIGS[801])))
    base = json.load(open(ROOT / CONFIGS[801]))
    evo = EvolutionConfig.from_dict({k: v for k, v in raw.items() if k != "ecology"})
    base_evo = EvolutionConfig.from_dict({k: v for k, v in base.items() if k != "ecology"})
    if raw["mutation"] != base["mutation"] or raw["ecology"]["capacity"] != base["ecology"]["capacity"] or evo.sim.synthesis != base_evo.sim.synthesis:
        raise SystemExit(f"seed {seed}: its config's vocabulary, capacity or synthesis differs from seed 801's; "
                         "the founders, or what wiring() reads of them, would not be one flag away from forage-801")
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


def k60(x, n=60):
    """A rate as ``k/60`` when it is one (the quartiles and every seed's rate are), else three decimals."""
    k = x * n
    return f"{int(round(k))}/{n}" if abs(k - round(k)) < 1e-9 else f"{x:.3f}"


def direction_row(seed):
    """The adversary's direction probe summary for ``seed``, from its committed readout, or None."""
    path = ART / f"RBT-90-adversary-direction-{seed}.txt"
    if not path.exists():
        return None
    text = path.read_text()
    g = lambda pat: re.search(pat, text)
    R, res, still = g(r"per-founder R: (.*)"), g(r"resultant of the per-founder MEAN angles: ([0-9.]+) over (\d+) founders"), g(r"never moved 1 mm in a tick: (\d+)/(\d+)")
    if not (R and res and still):
        return None
    iso = g(r"isotropy at this n: [^=]*= ([0-9.]+)")
    return {"R": R.group(1).strip(), "resultant": float(res.group(1)), "movers": int(res.group(2)), "isotropic": float(iso.group(1)) if iso else None,
            "still": int(still.group(1)), "n": int(still.group(2)), "file": path.name}


def direction_lines(seed):
    d = direction_row(seed)
    if d is None:
        return ["## direction of travel: not yet measured for this seed",
                f"  run: python runs/RBT-90/adversary_direction.py {seed} 60 16   (about five minutes; writes docs/artifacts/RBT-90-adversary-direction-{seed}.txt)",
                "  a candidate seed for part 2 is measured on it too."]
    verdict = "isotropic: no population-level forward axis" if d["isotropic"] is not None and d["resultant"] < d["isotropic"] else "above the isotropic expectation"
    return ["## direction of travel (the adversary's probe, each body in its own root frame; " + d["file"] + ")",
            f"  RBT-69's forward/backward split is undefined on this population: resultant of the per-founder mean directions {d['resultant']:.3f}"
            f" over {d['movers']} movers, isotropic expectation {d['isotropic']:.3f}: {verdict}",
            f"  per-founder R (travel direction fixed in its own frame): {d['R']}",
            f"  founders that never moved 1 mm in a tick: {d['still']}/{d['n']}: for them the statistic is undefined by immobility",
            "  the split stays measurable on the conventional Pioneer population, which has a designed front"]


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
         f"  link-driven effector (>= 1 live effector with a link into it): {m['drive']}/{m['n']}",
         f"  linked oscillator    (>= 1 oscillator sensor with an outgoing link): {m['osc']}/{m['n']}",
         f"  composite 'drive, no oscillator' (both of: link-driven effector, no linked oscillator): {m['both']}/{m['n']}",
         "  (rates are k/60 throughout; docs/artifacts/RBT-90-reference.json is the authority for the thresholds they are read against)",
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
         f"  distinct shape multisets (sorted node shapes only): {len(set(m['shapes']))}/{m['n']}   (reported; read by no clause: a strict coarsening of the full signature)",
         "  the fraction shared with every other seed is in docs/artifacts/RBT-90-calibration.txt",
         "",
         *direction_lines(m["seed"]),
         ""]
    if ref:
        fmt = lambda k, x: k60(x) if k in ("drive", "osc", "both") else f"{x:g}"
        L += ["## against the generator reference (docs/artifacts/RBT-90-reference.json, authoritative), central 90% band",
              *(f"  {k:13s} {fmt(k, r[k]):>8s}   band [{fmt(k, ref[k][0])}, {fmt(k, ref[k][1])}]   {'inside' if ref[k][0] <= r[k] <= ref[k][1] else 'OUTSIDE'}"
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
         "RBT-90-reference.json beside this file is the authority: rates are k/60 and the quartiles fall on values many",
         "seeds hold exactly, so a re-derivation from a rounded print moves seeds across the thresholds (adversary probe 1).",
         "",
         f"{'statistic':13s} {'min':>7s} {'p5':>7s} {'q25':>7s} {'median':>7s} {'q75':>7s} {'p95':>7s} {'max':>7s}"]
    for k in keys:
        xs = [r[k] for r in rows]
        cell = (lambda x: f"{k60(x):>7s}") if k in ("drive", "osc", "both") else (lambda x: f"{x:7.3f}")
        L.append(f"{k:13s} " + " ".join(cell(np.percentile(xs, p)) for p in (0, 5, 25, 50, 75, 95, 100)))
    L += ["", f"per-seed rows ({n}):", f"{'seed':>5s} {'drive':>7s} {'osc':>7s} {'both':>7s} {'parts':>6s} {'units':>6s}"]
    L += [f"{s:5d} {k60(r['drive']):>7s} {k60(r['osc']):>7s} {k60(r['both']):>7s} {r['parts_median']:6g} {r['units_median']:6g}" for s, r in enumerate(rows, 1)]
    (ART / "RBT-90-reference.txt").write_text("\n".join(L) + "\n")
    json.dump({"n": n, "band": band, "span": span}, open(ART / "RBT-90-reference.json", "w"), indent=1)
    return {"n": n, "band": band, "span": span}


def calibrate(seeds, ref):
    M = {s: measure(s) for s in seeds}
    R = {s: write_seed(M[s], ref["band"] if ref else None) for s in seeds}
    L = [f"RBT-90 calibration set: seeds {' '.join(map(str, seeds))}.  Per-seed readouts: docs/artifacts/founders-<seed>.txt.",
         "Rates are k/60; docs/artifacts/RBT-90-reference.json is the authority for the thresholds.",
         "", "## per seed   (shapes: reported, read by no clause)",
         f"{'seed':>5s} {'drive':>7s} {'osc':>7s} {'both':>7s} {'parts':>6s} {'units':>6s} {'distinct':>8s} {'shapes':>6s}"]
    for s in seeds:
        r, m = R[s], M[s]
        L.append(f"{s:5d} {k60(r['drive']):>7s} {k60(r['osc']):>7s} {k60(r['both']):>7s} {r['parts_median']:6g} {r['units_median']:6g} "
                 f"{len(set(m['sigs'])):5d}/{m['n']} {len(set(m['shapes'])):3d}/{m['n']}")
    L += ["", "## pairwise: founders of A whose body occurs among B's, and of B's among A's (full signature, clause 1 | shape multiset, reported only)",
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
        names = {"both": "composite", "osc": "linked oscillator", "drive": "link-driven effector"}
        L.append(f"  2. span: the set's rates reach both reference quartiles (seeds 1..{ref['n']}) on each of {', '.join(names[k] for k in SPAN_ON)}:")
        for k in SPAN_ON + ("drive",):
            lo, hi = ref["span"][k]
            xs = [R[s][k] for s in seeds]
            ok = min(xs) <= lo and max(xs) >= hi
            if k in SPAN_ON:
                verdict["span"] &= ok
            L.append(f"     {names[k]:21s} quartiles [{k60(lo)}, {k60(hi)}]  set min {k60(min(xs))} max {k60(max(xs))}: "
                     f"{('PASS' if ok else 'FAIL') if k in SPAN_ON else ('spans' if ok else 'does not span') + ' (reported, not ruled on)'}")
        L.append(f"     clause 2: {'PASS' if verdict['span'] else 'FAIL'}")
        keys = ("drive", "osc", "both", "parts_median", "units_median")
        verdict["outliers"] = [(s, k, R[s][k]) for s in seeds for k in keys if not ref["band"][k][0] <= R[s][k] <= ref["band"][k][1]]
        L.append(f"  3. label: seeds outside the generator's central 90% band on any statistic, kept and named: "
                 f"{verdict['outliers'] or 'none'}")
        L.append(f"  verdict: {'DIVERSE ENOUGH' if verdict['bodies'] and verdict['span'] else 'NOT DIVERSE ENOUGH'} under clauses 1 and 2 as stated")
    else:
        L.append("  2-3. need the reference: run with --reference N first")
    L += ["", "## direction of travel (the adversary's probe, each body in its own root frame): RBT-69's split is undefined on a holistic founding population",
          f"{'seed':>5s} {'movers':>6s} {'still':>5s} {'resultant':>9s} {'isotropic':>9s}  per-founder R"]
    for s in seeds:
        d = direction_row(s)
        L.append(f"{s:5d} {d['movers']:6d} {d['still']:5d} {d['resultant']:9.3f} {d['isotropic']:9.3f}  {d['R']}" if d else f"{s:5d}  not yet measured: python runs/RBT-90/adversary_direction.py {s} 60 16")
    text = "\n".join(L)
    (ART / "RBT-90-calibration.txt").write_text(text + "\n")
    return text, verdict


def passes(seeds, ref, cache):
    """Clauses 1 and 2 on a set, from cached measurements."""
    M = {s: cache.setdefault(s, measure(s)) for s in seeds}
    for i, a in enumerate(seeds):
        if len(set(M[a]["sigs"])) < MIN_DISTINCT:
            return False
        for b in seeds[i + 1:]:
            sb, sa = set(M[b]["sigs"]), set(M[a]["sigs"])
            if sum(x in sb for x in M[a]["sigs"]) > MAX_SHARED_BODIES or sum(x in sa for x in M[b]["sigs"]) > MAX_SHARED_BODIES:
                return False
    for k in SPAN_ON:
        lo, hi = ref["span"][k]
        xs = [rates(M[s])[k] for s in seeds]
        if not (min(xs) <= lo and max(xs) >= hi):
            return False
    return True


def choose(n, ref, keep=CALIBRATION):
    """The part-2 set: ``keep`` plus the lexicographically first combination of further seeds, by seed
    number from the reference's candidates 1..N, whose union with ``keep`` passes clauses 1 and 2.
    Deterministic, and committed as a readout before any run (the coordinator's rule, RBT-90 16:20)."""
    cache: dict = {}
    candidates = [s for s in range(1, ref["n"] + 1) if s not in keep]
    tried = 0
    for combo in itertools.combinations(candidates, n - len(keep)):
        tried += 1
        chosen = tuple(keep) + combo
        if passes(chosen, ref, cache):
            break
    else:
        raise SystemExit(f"no {n - len(keep)} candidates from 1..{ref['n']} make a passing set with {keep}")
    L = [f"RBT-90 part 2: the {n} founding seeds, chosen by the committed rule before any run.",
         f"Kept: {' '.join(map(str, keep))} (every population the programme has already read).",
         f"Candidates: seeds 1..{ref['n']} (the committed reference), in lexicographic order of {n - len(keep)}-seed combinations;",
         f"the first whose union with the kept five passes clauses 1 and 2 (composite AND linked-oscillator spans): combination {tried}.",
         f"Chosen: {' '.join(map(str, combo))}", "",
         f"{'seed':>5s} {'drive':>7s} {'osc':>7s} {'both':>7s} {'kept':>5s}"]
    for s in chosen:
        r = rates(cache[s])
        L.append(f"{s:5d} {k60(r['drive']):>7s} {k60(r['osc']):>7s} {k60(r['both']):>7s} {'kept' if s in keep else '':>5s}")
    for k in SPAN_ON + ("drive",):
        xs = [rates(cache[s])[k] for s in chosen]
        L.append(f"  {k:6s} set min {k60(min(xs))} max {k60(max(xs))}  quartiles [{k60(ref['span'][k][0])}, {k60(ref['span'][k][1])}]")
    text = "\n".join(L)
    (ART / "RBT-90-part2-seeds.txt").write_text(text + "\n")
    return chosen, text


def main(argv):
    ref, pick = None, None
    seeds = []
    it = iter(argv)
    for a in it:
        if a == "--reference":
            ref = reference(int(next(it)))
        elif a == "--choose":
            pick = int(next(it))
        else:
            seeds.append(int(a))
    if ref is None and (ART / "RBT-90-reference.json").exists():
        ref = json.load(open(ART / "RBT-90-reference.json"))
    text, _ = calibrate(tuple(seeds) or CALIBRATION, ref)
    print(text)
    if pick:
        _, text = choose(pick, ref)
        print("\n" + text)


if __name__ == "__main__":
    main(sys.argv[1:])
