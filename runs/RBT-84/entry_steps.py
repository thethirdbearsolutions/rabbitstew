"""Where a structure entered the champion's descent DAG: import by crossover, or acquisition by mutation.

RBT-84's adversary, in the 08:50 reading note on the amended Prediction B, asked for two things that
the DAG tracer had no way to print:

  1. Beside the B verdict, the number of founders reached, how many carry the structure, and
     `base_rate ** f` as the random-assembly expectation -- so that under the whole-DAG rule (which
     needs EVERY founder to carry it) an ATTRACTOR verdict reads as "acquired or imported" against
     that expectation rather than as a finding on its own.
  2. The crossover-import case kept distinct from the mutation-acquisition case: a step where the
     child carries it, one parent does not and another does is IMPORT, not acquisition.

Both are reported here for each property separately, because RBT-84's composite came apart at the
champion (twelve link-driven effectors AND two linked oscillators) and its two halves go opposite
ways along the same DAG.

A STEP is one child with its parents, both classified by the same `runs/RBT-28/adversary_founders.py::wiring`
the base rate and the path use.  A step counts only when the child carries the property and not every
parent does:
    IMPORT      -- at least one parent carries it (it came across from a lineage that had it)
    ACQUISITION -- no parent carries it (it appeared here, by mutation)
Founders have no parents and so are neither; they are counted separately as the DAG's boundary.

usage: entry_steps.py RUN_DIR [KIND] [NAME]
"""
import importlib.util
import json
import os
import pathlib
import sys
from collections import deque

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
spec = importlib.util.spec_from_file_location("adv", ROOT / "runs" / "RBT-28" / "adversary_founders.py")
adv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adv)

run = sys.argv[1]
kind = sys.argv[2] if len(sys.argv) > 2 else "holistic"
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])

rows = [json.loads(l) for l in open(os.path.join(run, "lineage.jsonl")) if l.strip()]
mine = [r for r in rows if r["population"] == kind]
last = {}
for r in mine:
    last[r["name"]] = r

if len(sys.argv) > 3:
    start = sys.argv[3]
else:
    final_season = max(r["generation"] for r in mine)
    start = max((r for r in mine if r["generation"] == final_season), key=lambda r: r["fitness"])["name"]


def wiring_of(name):
    p = os.path.join(run, kind, "genomes", f"{name}.json")
    if not os.path.exists(p):
        return None
    return adv.wiring(Genotype.load(p), cfg)


seen, order = {}, []
q = deque([start])
while q:
    name = q.popleft()
    if name in seen:
        continue
    seen[name] = wiring_of(name)
    order.append(name)
    for p in (last.get(name) or {}).get("parents", []):
        if p not in seen:
            q.append(p)

founders = [n for n in order if not (last.get(n) or {}).get("parents")]

# The founder base rate for the random-assembly expectation is this seed's own SIXTY founders,
# REGENERATED from the seed exactly as runs/RBT-84/founder_base_rate.py does, not the founders that
# happen to have a lineage row.  They differ by one: `h0-43` died before its first logged season, so
# lineage.jsonl carries 59 of the 60.  Using the regenerated population keeps this expectation and
# the pre-registered base rate (29/60 = 0.483) one measurement; the 59 are printed beside it.
import numpy as np
from rabbitstew.evolution import HOLISTIC, EvolutionConfig, initial_population

_raw = json.load(open(f"{run}/config.json"))
_evo = EvolutionConfig.from_dict({k: v for k, v in _raw.items() if k != "ecology"})
_evo.population_size = _raw["ecology"]["capacity"]
_evo.seed = _raw.get("seed", 807)
base_pool = [adv.wiring(g, _evo.sim)
             for g in initial_population(HOLISTIC, _evo, np.random.default_rng(_evo.seed)).members]
logged_pool = [w for w in (wiring_of(n) for n in sorted(
    n for n in last if not (last[n] or {}).get("parents"))) if w]

PROPS = {
    "composite (link-driven effector AND no linked oscillator)":
        lambda w: w["eff_driven"] > 0 and w["osc_linked"] == 0,
    "half A: a link into a live effector":
        lambda w: w["eff_driven"] > 0,
    "half B: no outgoing oscillator link":
        lambda w: w["osc_linked"] == 0,
    "the oscillator itself: at least one outgoing oscillator link":
        lambda w: w["osc_linked"] > 0,
}

print(f"{run} {kind}: entry steps for {start}")
print(f"  DAG: {len(order)} ancestors, {len(founders)} founders reached")
print(f"  base rates over the {len(base_pool)} founders regenerated from seed {_evo.seed} "
      f"({len(logged_pool)} of them have a lineage row; h0-43 died before its first logged season)\n")

out = {}
for label, f in PROPS.items():
    base = sum(1 for w in base_pool if f(w)) / len(base_pool)
    base_logged = sum(1 for w in logged_pool if f(w)) / len(logged_pool)
    fc = sum(1 for n in founders if seen.get(n) and f(seen[n]))
    nf = sum(1 for n in founders if seen.get(n))
    imports, acquisitions, lacking = [], [], 0
    for n in order:
        w = seen.get(n)
        if w is None:
            continue
        if not f(w):
            lacking += 1
            continue
        ps = [p for p in (last.get(n) or {}).get("parents", []) if seen.get(p)]
        if not ps:
            continue                                  # founder: the DAG's boundary, not a step
        carried = [f(seen[p]) for p in ps]
        if all(carried):
            continue                                  # inherited unchanged, not an entry
        (imports if any(carried) else acquisitions).append(
            (n, [(p, f(seen[p])) for p in ps]))
    champ = seen.get(start)
    print(f"{label}")
    print(f"  champion carries it:            {bool(champ and f(champ))}")
    print(f"  founders reached carrying it:   {fc}/{nf}")
    print(f"  this run's founder base rate:   {base:.3f} over 60 "
          f"({base_logged:.3f} over the 59 logged)"
          f"  -> random assembly of {nf} founders all carrying it: {base ** nf:.3f}")
    print(f"  ancestors lacking it:           {lacking} of {len(order)}")
    print(f"  IMPORT steps (a parent had it):      {len(imports)}"
          + (f"   {[n for n, _ in imports][:8]}" if imports else ""))
    print(f"  ACQUISITION steps (no parent had it):{len(acquisitions):4d}"
          + (f"   {[n for n, _ in acquisitions][:8]}" if acquisitions else ""))
    print()
    out[label] = {"champion": bool(champ and f(champ)), "founders_carrying": fc, "founders": nf,
                  "base_rate": base, "base_rate_logged": base_logged, "random_assembly": base ** nf, "lacking": lacking,
                  "imports": len(imports), "acquisitions": len(acquisitions),
                  "import_names": [n for n, _ in imports],
                  "acquisition_names": [n for n, _ in acquisitions]}
print(json.dumps({"run": run, "kind": kind, "champion": start,
                  "ancestors": len(order), "founders": len(founders), "props": out}))
