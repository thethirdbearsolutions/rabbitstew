"""Adversary probe for RBT-84: is the rise in oscillator-linked births selection, or the operators?

The report reads the birth-level linked-oscillator rate rising from 25% of founders to 65.6% of all
births as "this population acquires oscillator drive", and along one champion's DAG finds the
oscillator entered by ten crossover imports and zero mutation acquisitions.  One lineage is one
lineage.  This scans EVERY birth in the run and asks three things the DAG cannot:

1. How each oscillator-linked birth got its link: inherited from every parent, imported from one
   parent of two, or acquired with no parent carrying it.  And the reverse: births that LOST a link
   every parent had.
2. The operators' own bias, read from single-parent (mutation-only) births: how often a mutation-only
   child of a non-carrier gains a link, against how often a child of a carrier loses one.  If gain
   far exceeds loss, the rise is mutation pressure, not selection, and the same pressure acted on
   seed 801 -- which makes the two populations' opposite outcomes a fact about selection after all.
3. Whether carriers out-reproduce non-carriers: children per individual and lifetime, carriers
   against non-carriers, from lineage.jsonl.

Also, for Prediction A's denominator: the number of DISTINCT genotypes among the saved bests, so
"36 distinct carry one" can be read as a fraction of the distinct bests rather than of 59 snapshots.

Same classifier as the base rate and the DAG (`runs/RBT-28/adversary_founders.py::wiring`).
usage: adversary_population.py RUN_DIR [KIND]
"""
import glob
import importlib.util
import json
import os
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

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
first, last = {}, {}
for r in mine:
    first.setdefault(r["name"], r)
    last[r["name"]] = r

genomes = {os.path.basename(p)[:-5]: p for p in glob.glob(os.path.join(run, kind, "genomes", "*.json"))}
osc = {}
for name, p in genomes.items():
    osc[name] = adv.wiring(Genotype.load(p), cfg)["osc_linked"] > 0

founders = [n for n in genomes if not (last.get(n) or first.get(n) or {"parents": []}).get("parents")
            and n.startswith("h0-")]
births = [n for n in genomes if n not in founders]
L = [f"{run} {kind}: {len(genomes)} genomes on disk ({len(founders)} founders, {len(births)} births); "
     f"{sum(osc.values())} carry a linked oscillator ({sum(osc.values()) / len(genomes):.3f})"]
L.append(f"  founders carrying: {sum(osc[n] for n in founders)}/{len(founders)}; "
         f"births carrying: {sum(osc[n] for n in births)}/{len(births)} = {sum(osc[n] for n in births) / max(1, len(births)):.3f}")

# 1. how every birth got (or lost) its link
kinds = Counter()
by_parents = Counter()
gain_mut = loss_mut = keep_mut_c = keep_mut_n = 0
gain_x = loss_x = 0
for n in births:
    rec = last.get(n) or first.get(n)
    if rec is None:
        kinds["no lineage row"] += 1
        continue
    ps = [p for p in rec["parents"] if p in osc]
    if len(ps) != len(rec["parents"]):
        kinds["parent genome missing"] += 1
        continue
    by_parents[len(ps)] += 1
    carried = [osc[p] for p in ps]
    child = osc[n]
    if child:
        if all(carried):
            kinds["carrier: inherited (every parent had it)"] += 1
        elif any(carried):
            kinds["carrier: IMPORT (one parent of two had it)"] += 1
        else:
            kinds["carrier: ACQUISITION (no parent had it)"] += 1
    else:
        if all(carried):
            kinds["non-carrier: LOST (every parent had it)"] += 1
        elif any(carried):
            kinds["non-carrier: not imported (one parent had it)"] += 1
        else:
            kinds["non-carrier: inherited absence"] += 1
    if len(ps) == 1:
        if carried[0] and child:
            keep_mut_c += 1
        elif carried[0] and not child:
            loss_mut += 1
        elif not carried[0] and child:
            gain_mut += 1
        else:
            keep_mut_n += 1
    elif len(ps) == 2 and not any(carried) and child:
        gain_x += 1
    elif len(ps) == 2 and all(carried) and not child:
        loss_x += 1

L.append("\n=== 1. how each birth got its oscillator link (all births with both parents on disk) ===")
L.append(f"  births by parent count: {dict(sorted(by_parents.items()))}")
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
    L.append(f"  {v:5d}  {k}")

L.append("\n=== 2. the operators' own bias, from single-parent (mutation-only) births ===")
nc = gain_mut + keep_mut_n
cc = loss_mut + keep_mut_c
L.append(f"  child of a NON-carrier: {nc} births; gained a link in {gain_mut} ({gain_mut / max(1, nc):.3f})")
L.append(f"  child of a carrier:     {cc} births; lost the link in {loss_mut} ({loss_mut / max(1, cc):.3f})")
if nc and cc:
    g, l = gain_mut / nc, loss_mut / cc
    L.append(f"  mutation-only equilibrium carrier fraction, gain/(gain+loss): {g / (g + l):.3f}"
             f"   (the fraction the operators alone would drift to; compare the founders' and the births' rates above)")
L.append(f"  two-parent births: acquired with neither parent carrying {gain_x}; lost with both carrying {loss_x}")

# 3. do carriers out-reproduce non-carriers?
children = Counter()
for n in births:
    rec = last.get(n) or first.get(n)
    for p in (rec or {}).get("parents", []):
        children[p] += 1
lifetime = {n: last[n]["age"] for n in genomes if n in last}
def stats(names):
    names = [n for n in names if n in last]
    if not names:
        return "n/a"
    ch = np.array([children[n] for n in names], float)
    lt = np.array([lifetime[n] for n in names], float)
    fit = np.array([last[n]["fitness"] for n in names], float)
    return (f"n={len(names)}  children/individual {ch.mean():.3f} +- {ch.std(ddof=1) / np.sqrt(len(ch)):.3f}"
            f"  lifetime {lt.mean():.1f}  final fitness {fit.mean():.3f}")
L.append("\n=== 3. reproduction and lifetime, carriers against non-carriers (individuals with a lineage row) ===")
L.append(f"  carriers:     {stats([n for n in genomes if osc[n]])}")
L.append(f"  non-carriers: {stats([n for n in genomes if not osc[n]])}")
# The era confound runs AGAINST carriers (they are born later, so have had less time to reproduce);
# read the difference restricted to births before season 500, which all had > max_age seasons to
# reproduce, and within each century of birth.
born = {n: max(0, first[n]["generation"] - first[n]["age"]) for n in last}
c = np.array([children[n] for n in last if osc.get(n) and born[n] < 500], float)
nc = np.array([children[n] for n in last if not osc.get(n) and born[n] < 500], float)
d = c.mean() - nc.mean()
se = np.sqrt(c.var(ddof=1) / len(c) + nc.var(ddof=1) / len(nc))
L.append(f"  born before season 500 (all had > max_age seasons to reproduce): carriers n={len(c)} children {c.mean():.3f}; "
         f"non-carriers n={len(nc)} children {nc.mean():.3f}; difference {d:+.3f} +- {se:.3f}, t {d / se:+.2f}")
for b in range(6):
    cc = [children[n] for n in last if osc.get(n) and born[n] // 100 == b]
    nn = [children[n] for n in last if not osc.get(n) and born[n] // 100 == b]
    if cc and nn:
        L.append(f"    born {100 * b}-{100 * b + 99}: carriers n={len(cc)} children {np.mean(cc):.2f} | non-carriers n={len(nn)} children {np.mean(nn):.2f}")
# by generation band, so a late-run dominance does not masquerade as a per-individual advantage
bands = defaultdict(lambda: [0, 0])
for n in births:
    if n in first:
        b = max(0, first[n]["generation"] - first[n]["age"]) // 100
        bands[b][0] += 1
        bands[b][1] += osc[n]
L.append(f"  carrier fraction of births by century of birth (founders excluded; founders {sum(osc[n] for n in founders)}/{len(founders)}): " +
         ", ".join(f"{100 * b}-{100 * b + 99}: {c[1]}/{c[0]}={c[1] / c[0]:.2f}" for b, c in sorted(bands.items())))

# 4. Prediction A's denominator
bests = sorted(glob.glob(os.path.join(run, kind, "best_gen*.json")))
names_all, names_osc = set(), set()
for p in bests:
    if int(re.search(r"best_gen(\d+)", p).group(1)) == 0:
        continue
    g = Genotype.load(p)
    names_all.add(g.name)
    if adv.wiring(g, cfg)["osc_linked"] > 0:
        names_osc.add(g.name)
L.append(f"\n=== 4. Prediction A's denominator ===")
L.append(f"  saved bests after season 0: {len(bests) - 1} snapshots, {len(names_all)} DISTINCT genotypes, "
         f"of which {len(names_osc)} carry a linked oscillator ({len(names_osc) / max(1, len(names_all)):.2f} of the distinct bests)")

text = "\n".join(L)
print(text)
os.makedirs("docs/runs", exist_ok=True)
with open("docs/runs/RBT-84-adversary-population.txt", "w") as f:
    f.write(text + "\n")
