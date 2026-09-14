"""Does RBT-84's package reproduce from what is committed?

The delegation protocol says "if a claim rests on it, commit it". `.gitignore` keeps run artifacts
out of the tree (`runs/**` with .md/.py/.txt/config.json allowed), on the repo's standing argument
that a seeded run is re-derivable. RBT-71's adversary has just held a package defective for being
unreproducible, so that argument is checked here rather than asserted.

Two checks, and they establish different amounts:

1. FOUNDERS. Regenerate the sixty founders from the committed `config.json` alone and compare them
   to `genomes/h0-*.json` on disk. Compared on every field EXCEPT the mutable ecology `record`
   (energy, age, born, evals, kind) -- runtime bookkeeping written by the ecology, not genotype, and
   not read by any classifier in this arm.

2. THE RUN ITSELF, over the seasons two attempts share. The first launch was killed at season 66
   (see the report, section 7.1) and was kept. Every genome name the killed attempt saved is compared
   against the completed run's genome of the same name. This is the check that the 600-season run is
   a function of the seed, not of the wall clock -- but it covers 66 seasons of 600, not all of them.

usage: reproducible.py [KILLED_RUN_DIR]
"""
import hashlib
import json
import os
import sys
import tempfile

import numpy as np

from rabbitstew.evolution import HOLISTIC, EvolutionConfig, initial_population
from rabbitstew.genotype import Genotype

RUN, KIND = "runs/RBT-84/forage-807", "holistic"
MUTABLE = "record"        # energy/age/born/evals/kind: ecology bookkeeping, not genotype


def canon(d):
    return hashlib.sha256(
        json.dumps({k: v for k, v in d.items() if k != MUTABLE}, sort_keys=True).encode()).hexdigest()


def dump(g):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as t:
        p = t.name
    g.save(p)
    d = json.load(open(p))
    os.unlink(p)
    return d


raw = json.load(open(f"{RUN}/config.json"))
evo = EvolutionConfig.from_dict({k: v for k, v in raw.items() if k != "ecology"})
evo.population_size = raw["ecology"]["capacity"]
evo.seed = raw.get("seed", 807)

print(f"check 1 -- the founding population, from the committed config.json alone (seed {evo.seed})")
founders = list(initial_population(HOLISTIC, evo, np.random.default_rng(evo.seed)).members)
same = sum(canon(dump(g)) == canon(json.load(open(f"{RUN}/{KIND}/genomes/{g.name}.json")))
           for g in founders)
print(f"  {same} of {len(founders)} identical on every field but `{MUTABLE}`"
      f"   -> {'REPRODUCES' if same == len(founders) else 'DOES NOT REPRODUCE'}")
print(f"  (all 60 differ if `{MUTABLE}` is included; it carries the ecology's live energy and age,")
print("   is absent from a freshly synthesised genome, and is read by nothing in this arm.)")

killed = sys.argv[1] if len(sys.argv) > 1 else None
print("\ncheck 2 -- the run itself, over the seasons the killed first attempt and the completed run share")
if not killed or not os.path.isdir(f"{killed}/{KIND}/genomes"):
    print(f"  SKIPPED: no killed-attempt directory given or found ({killed!r})")
    raise SystemExit
shared = sorted(set(os.listdir(f"{killed}/{KIND}/genomes")) & set(os.listdir(f"{RUN}/{KIND}/genomes")))
agree = [n for n in shared
         if canon(json.load(open(f"{killed}/{KIND}/genomes/{n}")))
         == canon(json.load(open(f"{RUN}/{KIND}/genomes/{n}")))]
kept = len(os.listdir(f"{killed}/{KIND}/genomes"))
print(f"  killed attempt saved {kept} genomes; {len(shared)} of those names also exist in the completed run")
print(f"  identical: {len(agree)} of {len(shared)}"
      f"   -> {'THE RUN IS A FUNCTION OF THE SEED' if len(agree) == len(shared) else 'DIVERGENCE'}"
      f" over its first 66 seasons of 600")
if len(agree) != len(shared):
    print(f"  first differing: {[n for n in shared if n not in set(agree)][:10]}")
