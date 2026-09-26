"""RBT-92 adversary probe E: how often does tables.py's body-structure digest survive one birth?

B(s) and S(s) in readout.py count exact equality of body_structure digests with a C0 ancestor's.
That readout has range only if a digest usually passes unchanged from parent to child.  This reads
the throwaway runs of shared_baseline_runs.sh (and probe C's plain arm when present) and, for every
holistic child whose genome and first parent's genome exist, compares (i) tables.py's digest (equal to either parent's counts as inherited: crossover_rate 0.3),
(ii) a coarser, order-free digest (node count, sorted segment shapes, sorted joint types,
connection count), (iii) rabbitstew.genetics.body_signature, and, per component of (i) against the first parent, which one
changed.  Genomes only; no score is read.

    python runs/RBT-92/adversary/probe_digest_inheritance.py > runs/RBT-92/adversary/probe_digest_inheritance.txt
"""
import collections
import importlib.util
import json
import os

from rabbitstew.genetics import body_signature
from rabbitstew.genotype import Genotype

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tables", os.path.join(HERE, "..", "tables.py"))
tables = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tables)
RUNS = ["sbc-plain-801", "sbc-plain-9901", "probe-plain-9902"]


def comp(g):
    return {"root": g.root, "node count": len(g.nodes), "segment shapes": tuple(int(n.segment.shape) for n in g.nodes),
            "connection graph": tuple(tuple(c.child for c in n.connections) for n in g.nodes),
            "joint types": tuple(tuple(int(c.joint_type) for c in n.connections) for n in g.nodes),
            "recursive limits": tuple(tuple(c.recursive_limit for c in n.connections) for n in g.nodes),
            "motor/mirror": tuple(tuple((c.motor, c.mirror) for c in n.connections) for n in g.nodes),
            "non-neuron units": tuple(tuple((u.kind, getattr(u, "source", None), getattr(u, "axis", None), getattr(u, "dof", None))
                                            for u in n.segment.brain.units if u.kind != "neuron") for n in g.nodes)}


def coarse(g):
    return (len(g.nodes), tuple(sorted(int(n.segment.shape) for n in g.nodes)),
            tuple(sorted(int(c.joint_type) for n in g.nodes for c in n.connections)), sum(len(n.connections) for n in g.nodes))


print(__doc__.split("\n\n")[0])
print()
for run in RUNS:
    d = os.path.join(HERE, "..", "data", run)
    if not os.path.exists(os.path.join(d, "lineage.jsonl")):
        print(f"{run}: not present")
        continue
    par = {}
    with open(os.path.join(d, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["population"] == "holistic" and r["name"] not in par:
                p = r["parents"]
                par[r["name"]] = p if isinstance(p, list) else [x for x in p.split(",") if x]
    n = eq = eqc = eqs = 0
    what = collections.Counter()
    for name, ps in par.items():
        if not ps:
            continue
        paths = [os.path.join(d, "holistic", "genomes", f"{x}.json") for x in [name] + ps]
        if not all(os.path.exists(x) for x in paths):
            continue
        ga, *gp = [Genotype.load(x) for x in paths]
        gb = gp[0]
        n += 1
        eq += tables.body_structure(ga) in {tables.body_structure(g) for g in gp}
        eqc += coarse(ga) in {coarse(g) for g in gp}
        eqs += repr(body_signature(ga)) in {repr(body_signature(g)) for g in gp}
        ca, cb = comp(ga), comp(gb)
        for k in ca:
            what[k] += ca[k] != cb[k]
    print(f"{run}: {n} holistic births with both genomes")
    print(f"  tables.py digest equal to the parent's: {eq}/{n};  coarse order-free digest: {eqc}/{n};  full body_signature: {eqs}/{n}")
    print(f"  components of the digest that changed, births out of {n}: " + ", ".join(f"{k} {v}" for k, v in what.items()))
