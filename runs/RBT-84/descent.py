"""The descent path from a champion back to its founder, and where its drive kind was fixed.

RBT-84's discriminating evidence. RBT-28's adversary established that the five autopsied arms ran
on one founding population and that P(>= 4 of 5 sharing the drive structure) = 0.17 against its base
rate -- so "an attractor the search finds" and "structure the founders shared and never diverged
from" could not be separated. Separating them needs the descent path, which no run before RBT-27's
genome-at-birth saving had.

This walks a champion back through `lineage.jsonl`'s `parents` to a founder, loads every ancestor's
genotype from `<kind>/genomes/<name>.json`, and classifies each with the SAME wiring classifier the
adversary used, so the base rate and the path are one measurement.

Verdict, as pre-registered on the ticket before the run launched:
  non-divergence -- the lineage's founder already carried link-driven-effector-and-no-linked-
                    oscillator AND the drive kind never changes along the path
  attractor      -- the founder did not carry it and the lineage acquired it after season 0,
                    OR the drive kind changes at least once and settles on it
  undecidable    -- the path cannot be reconstructed

  NOT APPLICABLE -- a fourth outcome the pre-registered rule did not cover, added on partial
                    output before the run finished and declared on the ticket at the time.  The
                    rule assumed the champion carries the structure and only asked where it came
                    from; run on a season-10 champion that does NOT carry it, the rule returned
                    "attractor" for a lineage in which the structure is absent throughout.  That
                    is a hole, not a re-tuning: it adds a case the rule could not express and
                    changes no outcome the rule already had.

usage: descent.py RUN_DIR [KIND] [NAME]     (NAME defaults to the last season's best)
"""
import importlib.util
import json
import os
import pathlib
import sys

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
    last[r["name"]] = r                      # keep the final row per name, as read_lineage does
born = {r["name"]: r["generation"] - r["age"] for r in last.values()}

if len(sys.argv) > 3:
    start = sys.argv[3]
else:
    final_season = max(r["generation"] for r in mine)
    alive = [r for r in mine if r["generation"] == final_season]
    start = max(alive, key=lambda r: r["fitness"])["name"]

def genome(name):
    p = os.path.join(run, kind, "genomes", f"{name}.json")
    return Genotype.load(p) if os.path.exists(p) else None

def drive(name):
    g = genome(name)
    if g is None:
        return None
    w = adv.wiring(g, cfg)
    kindname = ("effector" if w["eff_driven"] > 0 else
                "bias-only effector" if w["eff_bias_only"] > 0 else "other")
    return {**w, "drive": kindname, "carries": w["eff_driven"] > 0 and w["osc_linked"] == 0}

path, cur, seen = [], start, set()
while cur and cur not in seen:
    seen.add(cur)
    rec = last.get(cur)
    d = drive(cur)
    path.append((cur, born.get(cur), rec, d))
    parents = rec["parents"] if rec else []
    cur = parents[0] if parents else None

print(f"{run} {kind}: descent of {start}, {len(path)} ancestors back to "
      f"{'a founder' if path and not (path[-1][2] or {}).get('parents') else 'a break in the chain'}")
print(f"{'name':>10} {'born':>5} {'parts':>5} {'links':>5} {'eff_driven':>10} {'osc_linked':>10} "
      f"{'food_linked':>11} {'drive':>18}  carries")
for name, b, rec, d in path:
    if d is None:
        print(f"{name:>10} {str(b):>5}   -- genome not saved (a founder of a run without archiving) --")
        continue
    print(f"{name:>10} {str(b):>5} {d['parts']:5d} {d['links']:5d} {d['eff_driven']:10d} "
          f"{d['osc_linked']:10d} {d['food_linked']:11d} {d['drive']:>18}  {'YES' if d['carries'] else 'no'}")

kinds = [d["drive"] for _, _, _, d in path if d]
carries = [d["carries"] for _, _, _, d in path if d]
founder_ok = carries[-1] if carries else None
changed = len(set(kinds)) > 1
champion_ok = carries[0] if carries else None
if not carries:
    verdict = "UNDECIDABLE -- no ancestor genome on disk"
elif not champion_ok:
    verdict = ("NOT APPLICABLE -- the champion does not carry the structure, so where it came from "
               "does not arise")
elif founder_ok and not changed:
    verdict = "NON-DIVERGENCE -- the founder already carried it and the drive kind never changed"
elif not founder_ok or changed:
    verdict = "ATTRACTOR -- acquired after season 0, or the drive kind changed and settled"
print(f"\nchampion {start} carries the structure: {champion_ok}; founder {path[-1][0]} carries it: "
      f"{founder_ok}; drive kind changed along the path: {changed}")
print(f"VERDICT (pre-registered rule): {verdict}")
print(json.dumps({"run": run, "kind": kind, "champion": start, "ancestors": len(path),
                  "champion_carries": champion_ok, "founder_carries": founder_ok, "changed": changed, "verdict": verdict.split(" --")[0]}))
