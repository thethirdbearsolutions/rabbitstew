"""Adversary probe for RBT-28, attack 1: is "effector drive, no oscillator, in four of five" a
finding about the search or a property of the founders?

The autopsy's author pre-registered the caveat and honoured it: at 13-20 reproduction events,
"an attractor the search found" and "structure the founders already shared and never diverged
from" are both live, and "this autopsy cannot separate them.  Separating them needs the
founders."  This probe asks whether the founders are on disk, and, since they are not, whether
they can be had anyway -- and then looks.

Three facts, all checkable from committed files with no simulation:

1. **All five champion runs share `seed = 801`**, and the ecology draws its founders from
   `numpy.random.default_rng(seed)` before anything else (`Ecology.__init__`,
   `initial_population`).  Every run's `holistic/best_gen0000.json` is the same genotype,
   `h0-49`, to the last digit.  The five arms are five worlds run on ONE founding population.
2. **The founders regenerate from the seed.**  `initial_population(HOLISTIC, config, rng)` with
   the run's config and `default_rng(801)` returns sixty genotypes whose 49th is byte-identical
   to the saved `h0-49`.  So "the founders are not on disk" is true and does not matter.
3. With the sixty in hand: which of them carry an oscillator with any outgoing link at all, and
   which carry an effector driven by anything (a link into it) rather than by its bias alone --
   the two structural facts the "effector drive, no oscillator" reading rests on.  Then the
   same survey over every saved best of each run (gens 0..590) to see whether an oscillator link
   is ever acquired, and the nearest founder to each champion by body shape, to see whether the
   four "effector drive" champions descend from the same founder body.

Usage: python runs/RBT-28/adversary_founders.py  (after runs/RBT-28/extract.sh; needs the five
run branches fetched, as extract.sh does)
"""
import json, os, subprocess, sys

import numpy as np

from rabbitstew.evolution import EvolutionConfig, HOLISTIC, initial_population
from rabbitstew.genotype import Genotype
from rabbitstew.synthesis import synthesize

RUNS = {  # label: (branch, run path, champion gen)
    "RBT-13": ("origin/results/RBT-13", "runs/RBT-13/W1-801", 390),
    "RBT-16": ("origin/results/RBT-16", "runs/RBT-16/W4-801", 590),
    "RBT-17": ("origin/claude/wizardly-johnson-4c9hvn", "runs/RBT-17/W5-801", 590),
    "RBT-22": ("origin/results/RBT-22", "runs/RBT-22/W1b-801", 590),
    "baseline-801": ("origin/results/baseline-801", "runs/baseline-801/forage-801", 300),
}
OUT = "docs/runs/RBT-28-adversary-founders.txt"


def show(branch, path):
    return json.loads(subprocess.check_output(["git", "show", f"{branch}:{path}"]))


def strip(d):
    return {k: v for k, v in d.items() if k not in ("name", "parents", "record")}


def wiring(g, cfg):
    """Static wiring facts of one genotype: what is expressed and what is linked."""
    ph = synthesize(g, cfg.synthesis)
    src = {s for s, _, _ in ph.links}
    dst = {d for _, d, _ in ph.links}
    units = ph.units
    osc = [i for i, u in enumerate(units) if u.unit.kind == "sensor" and u.unit.source == "oscillator"]
    food = [i for i, u in enumerate(units) if u.unit.kind == "sensor" and u.unit.source in ("food", "agent")]
    eff = [i for i, u in enumerate(units) if u.unit.kind == "effector" and u.part is not None
           and ph.parts[u.part].parent is not None and ph.parts[u.part].joint_type.name != "FIXED"]
    return {
        "parts": len(ph.parts), "units": len(units), "links": len(ph.links),
        "osc": len(osc), "osc_linked": sum(i in src for i in osc),
        "food": len(food), "food_linked": sum(i in src for i in food),
        "eff": len(eff), "eff_driven": sum(i in dst for i in eff),
        "eff_bias_only": sum(i not in dst and abs(getattr(units[i].unit, "bias", 0.0)) > 1e-9 for i in eff),
        "eff_self_loop": sum(any(s == d == i for s, d, _ in ph.links) for i in eff),
    }


def shape_sig(g):
    """Body signature that survives weight and dims mutations: node shapes in order, and each
    node's unit kinds/sources."""
    return tuple((int(n.segment.shape), tuple((u.kind, getattr(u, "source", None)) for u in n.segment.brain.units)) for n in g.nodes)


def dims_distance(a, b):
    if len(a.nodes) != len(b.nodes):
        return float("inf")
    d = 0.0
    for x, y in zip(a.nodes, b.nodes):
        if int(x.segment.shape) != int(y.segment.shape):
            return float("inf")
        d += float(np.abs(np.asarray(x.segment.dims) - np.asarray(y.segment.dims)).sum())
    return d


def main():
    L = []
    cfg0 = json.load(open("runs/RBT-28/data/RBT-13/config.json"))
    evo = EvolutionConfig.from_dict({k: v for k, v in cfg0.items() if k != "ecology"})
    evo.population_size = cfg0["ecology"]["capacity"]
    founders = initial_population(HOLISTIC, evo, np.random.default_rng(evo.seed)).members
    L.append(f"founders regenerated from seed {evo.seed}: {len(founders)} holistic genotypes")

    # 1-2. every run's season-0 best is the same founder, and it is founder 49 regenerated
    f49 = strip(founders[49].to_dict())
    for label, (br, path, gen) in RUNS.items():
        b0 = show(br, f"{path}/holistic/best_gen0000.json")
        L.append(f"  {label:12s} seed {json.load(open(f'runs/RBT-28/data/{label}/config.json'))['seed']}  "
                 f"season-0 best {b0['name']}  identical to regenerated founder 49: {strip(b0) == f49}")
    L.append("  -> the five arms were started from ONE founding population; 'four of five arms converged' is not four independent searches")

    # 3. what the founders carry
    L.append("\n=== the sixty founders, statically ===")
    W = [wiring(g, evo.sim) for g in founders]
    def frac(key, pred):
        return sum(pred(w) for w in W)
    L.append(f"  carry >= 1 oscillator sensor: {frac('osc', lambda w: w['osc'] > 0)}/60;  with any outgoing link: {frac('osc', lambda w: w['osc_linked'] > 0)}/60")
    L.append(f"  carry >= 1 smell sensor:      {frac('food', lambda w: w['food'] > 0)}/60;  with any outgoing link: {frac('food', lambda w: w['food_linked'] > 0)}/60")
    L.append(f"  live effectors per founder: median {np.median([w['eff'] for w in W]):.0f};  founders with >= 1 effector driven by a link: "
             f"{frac('eff', lambda w: w['eff_driven'] > 0)}/60;  with an effector on bias alone: {frac('eff', lambda w: w['eff_bias_only'] > 0)}/60;  "
             f"with an effector self-loop: {frac('eff', lambda w: w['eff_self_loop'] > 0)}/60")
    L.append(f"  parts median {np.median([w['parts'] for w in W]):.0f}, units median {np.median([w['units'] for w in W]):.0f}, links median {np.median([w['links'] for w in W]):.0f}")
    joint = frac("", lambda w: w["eff_driven"] > 0 and w["osc_linked"] == 0)
    p = joint / 60.0
    from math import comb
    tail = sum(comb(5, k) * p ** k * (1 - p) ** (5 - k) for k in (4, 5))
    L.append(f"  founders with BOTH a link-driven effector AND no linked oscillator (the 'effector drive, no oscillator' structure, read statically): "
             f"{joint}/60 = {p:.2f}.  If five champions were five draws from that base rate, P(>= 4 of 5 share it) = {tail:.2f}.")
    L.append("  (static proxy: the autopsy's 'effector drive' is a lesion result, this is wiring; the base rate is what it has to beat, not the whole story)")

    # 4. do the runs ever acquire an oscillator link?  every saved best, every run
    L.append("\n=== every saved holistic best, per run: oscillator links over evolutionary time ===")
    for label, (br, path, gen) in RUNS.items():
        cfg = EvolutionConfig.from_dict({k: v for k, v in json.load(open(f"runs/RBT-28/data/{label}/config.json")).items() if k != "ecology"}).sim
        files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", br, f"{path}/holistic/"]).decode().split()
        bests = sorted(f for f in files if os.path.basename(f).startswith("best_gen"))
        rows = []
        for f in bests:
            g = Genotype.from_dict(show(br, f))
            rows.append((int(os.path.basename(f)[8:12]), wiring(g, cfg)))
        osc_linked = [gn for gn, w in rows if w["osc_linked"] > 0]
        food_linked = [gn for gn, w in rows if w["food_linked"] > 0]
        L.append(f"  {label:12s} {len(rows)} bests: oscillator linked at gens {osc_linked or 'NONE'};  smell linked at gens {food_linked or 'NONE'};  "
                 f"effector driven by a link in {sum(w['eff_driven'] > 0 for _, w in rows)}/{len(rows)}")

    # 5. nearest founder to each champion, by body
    L.append("\n=== each champion's nearest founder by body (same node count and shapes; L1 over dims) ===")
    sigs = [shape_sig(g) for g in founders]
    for label, (br, path, gen) in RUNS.items():
        ch = Genotype.load(f"runs/RBT-28/data/{label}/holistic/best_gen{gen:04d}.json")
        cfg = EvolutionConfig.from_dict({k: v for k, v in json.load(open(f"runs/RBT-28/data/{label}/config.json")).items() if k != "ecology"}).sim
        dists = [dims_distance(ch, f) for f in founders]
        j = int(np.argmin(dists))
        same_sig = [i for i, s in enumerate(sigs) if s == shape_sig(ch)]
        w = wiring(ch, cfg)
        wf = wiring(founders[j], cfg)
        L.append(f"  {label:12s} {ch.name} (born {ch.record.get('born')}, parents {ch.parents}): {len(ch.nodes)} nodes; nearest founder h0-{j} at dims-L1 {dists[j]:.3f}"
                 f"{' (inf: no founder has this node count/shapes)' if not np.isfinite(dists[j]) else ''}; founders with the identical node/unit signature: {same_sig or 'none'}")
        L.append(f"               champion: osc {w['osc']} linked {w['osc_linked']}, smell {w['food']} linked {w['food_linked']}, effectors {w['eff']} driven {w['eff_driven']} bias-only {w['eff_bias_only']} self-loop {w['eff_self_loop']}, links {w['links']}")
        L.append(f"               founder : osc {wf['osc']} linked {wf['osc_linked']}, smell {wf['food']} linked {wf['food_linked']}, effectors {wf['eff']} driven {wf['eff_driven']} bias-only {wf['eff_bias_only']} self-loop {wf['eff_self_loop']}, links {wf['links']}")

    text = "\n".join(L)
    print(text)
    os.makedirs("docs/runs", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
