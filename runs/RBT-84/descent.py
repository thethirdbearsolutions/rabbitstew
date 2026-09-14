"""The descent DAG from a champion back to its founders, and where its drive kind entered.

RBT-84's discriminating evidence. RBT-28's adversary established that its five autopsied arms ran
on one founding population, so "an attractor the search finds" could not be separated from
"structure the founders shared and never diverged from". Separating them needs a second founding
population and the descent path, which RBT-27's genome-at-birth saving now provides.

Ancestors are classified with the SAME wiring classifier the adversary used
(`runs/RBT-28/adversary_founders.py::wiring`), so the founder base rate and the path are one
measurement.

**Every path is traced, not the first parent's.** `Ecology._breed` writes
`child.parents = [parent, other]` on crossover and roughly half of reproductions are crossovers, so
following `parents[0]` reaches one of up to 2^k founders and a structure can enter through the
parent the tracer never visits. Following `parents[0]` alone was this script's second defect,
raised by RBT-84's adversary as seam 3 and fixed here before the champion existed.

Verdict, as pre-registered on the ticket and amended twice before the run finished:
  NOT APPLICABLE -- the champion does not carry the structure, so where it came from does not
                    arise (amendment 1, added on partial output)
  NON-DIVERGENCE -- the champion carries it AND every founder the DAG reaches carries it AND no
                    ancestor anywhere in the DAG lacks it
  ATTRACTOR      -- the champion carries it AND at least one ancestor lacks it (so it entered
                    somewhere after season 0, or entered by crossover from a lineage that had it
                    while another did not)
  UNDECIDABLE    -- the DAG cannot be reconstructed

usage: descent.py RUN_DIR [KIND] [NAME]     (NAME defaults to the last season's best)
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
    last[r["name"]] = r                       # the final row per name, as read_lineage does
born = {n: r["generation"] - r["age"] for n, r in last.items()}

if len(sys.argv) > 3:
    start = sys.argv[3]
else:
    final_season = max(r["generation"] for r in mine)
    start = max((r for r in mine if r["generation"] == final_season), key=lambda r: r["fitness"])["name"]


def classify(name):
    p = os.path.join(run, kind, "genomes", f"{name}.json")
    if not os.path.exists(p):
        return None
    w = adv.wiring(Genotype.load(p), cfg)
    return {**w, "carries": w["eff_driven"] > 0 and w["osc_linked"] == 0,
            "drive": "effector" if w["eff_driven"] > 0 else
                     "bias-only effector" if w["eff_bias_only"] > 0 else "other"}


# Breadth-first over EVERY parent, not the first.
seen, order, crossovers, missing = {}, [], 0, []
q = deque([start])
while q:
    name = q.popleft()
    if name in seen:
        continue
    c = classify(name)
    seen[name] = c
    order.append(name)
    if c is None:
        missing.append(name)
    parents = (last.get(name) or {}).get("parents", [])
    if len(parents) > 1:
        crossovers += 1
    for p in parents:
        if p not in seen:
            q.append(p)

founders = [n for n in order if not (last.get(n) or {}).get("parents")]
known = {n: c for n, c in seen.items() if c}
champ = seen.get(start)

print(f"{run} {kind}: descent DAG of {start}")
print(f"  ancestors reached: {len(order)}   founders reached: {len(founders)}   "
      f"crossover steps: {crossovers}   genomes missing: {len(missing)}")
print(f"\n{'name':>10} {'born':>5} {'parents':>7} {'eff_driven':>10} {'osc_linked':>10} "
      f"{'food_linked':>11} {'drive':>18}  carries")
for n in order[:40]:
    c = seen[n]
    ps = len((last.get(n) or {}).get("parents", []))
    if c is None:
        print(f"{n:>10} {str(born.get(n)):>5} {ps:7d}   -- genome not on disk --")
        continue
    print(f"{n:>10} {str(born.get(n)):>5} {ps:7d} {c['eff_driven']:10d} {c['osc_linked']:10d} "
          f"{c['food_linked']:11d} {c['drive']:>18}  {'YES' if c['carries'] else 'no'}")
if len(order) > 40:
    print(f"  ... {len(order) - 40} more ancestors")

f_carry = [seen[n]["carries"] for n in founders if seen.get(n)]
any_lacks = any(not c["carries"] for c in known.values())
if champ is None or not known:
    verdict = "UNDECIDABLE -- the DAG cannot be reconstructed"
elif not champ["carries"]:
    verdict = "NOT APPLICABLE -- the champion does not carry the structure"
elif f_carry and all(f_carry) and not any_lacks:
    verdict = "NON-DIVERGENCE -- every founder reached carried it and no ancestor lacks it"
else:
    verdict = "ATTRACTOR -- at least one ancestor lacks it, so it entered after season 0"

print(f"\nchampion carries: {champ['carries'] if champ else None}   "
      f"founders carrying: {sum(f_carry)}/{len(f_carry)}   "
      f"any ancestor lacking it: {any_lacks}")
print(f"VERDICT (pre-registered rule, amendments 1 and 2): {verdict}")
print(json.dumps({"run": run, "kind": kind, "champion": start, "ancestors": len(order),
                  "founders": len(founders), "founders_carrying": sum(f_carry),
                  "crossover_steps": crossovers, "genomes_missing": len(missing),
                  "champion_carries": bool(champ and champ["carries"]), "any_ancestor_lacks": any_lacks,
                  "verdict": verdict.split(" --")[0]}))
