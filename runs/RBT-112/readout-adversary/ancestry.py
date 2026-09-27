"""RBT-112 readout adversary, attack 5: are seed 4's LOST and seed 805's HELD artefacts of the root rule?

POST HOC, PRINT-ONLY.  Reads one restored HZ arm (lineage.jsonl, conventional/genomes; from ckpt/rbt-112-HZ-SEED) and
RBT-106's held.py (imported, unchanged: its own_links reader, its hit rule and its pay32 criterion).  For the living
designed genomes at 300 and 599 it prints:
  * the registered classification: root along parents[0] (planted / bare), and the pay32 hits in each class;
  * whether a planted founder is ANY ancestor (through either parent at every step: crossover can bring the
    planted global brain in through the second parent), and the hits by that wider rule;
  * the planted roots of the planted-rooted living, and how many living each holds (clade collapse).
Usage: ancestry.py RUN_DIR SEED
"""
import collections
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(D))
_spec = importlib.util.spec_from_file_location("rbt106_held_anc", os.path.join(ROOT, "runs", "RBT-106", "held.py"))
held = importlib.util.module_from_spec(_spec)
sys.modules["rbt106_held_anc"] = held
_spec.loader.exec_module(held)
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402


def main():
    run, seed = sys.argv[1].rstrip("/"), int(sys.argv[2])
    cfg = json.load(open(os.path.join(run, "config.json")))
    sim = SimConfig.from_dict(cfg["sim"])
    gdir = os.path.join(run, "conventional", "genomes")
    ph = lambda nm: synthesize(Genotype.load(os.path.join(gdir, f"{nm}.json")), sim.synthesis)
    parents, living = {}, collections.defaultdict(list)
    for line in open(os.path.join(run, "lineage.jsonl")):
        r = json.loads(line)
        if r["population"] != "conventional":
            continue
        parents.setdefault(r["name"], r["parents"])
        if r["generation"] in (300, 599) and "death" not in r:
            living[r["generation"]].append(r["name"])
    sign = {}

    def fsign(nm):
        if nm not in sign:
            a = held.peek.own_links(ph(nm))
            sign[nm] = None if a is None else float(__import__("numpy").sign(a))
        return sign[nm]

    def root0(nm):
        while parents.get(nm):
            nm = parents[nm][0]
        return nm

    memo = {}

    def planted_anc(nm):
        """The set of planted founders among all ancestors (either parent)."""
        stack, seen, out = [nm], set(), set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            ps = parents.get(x) or []
            if not ps:
                if fsign(x) is not None:
                    out.add(x)
            stack.extend(ps)
        return out

    print(f"# RBT-112 readout adversary: ancestry of HZ-{seed}'s living at 300 and 599 (POST HOC, print-only)")
    for season in (300, 599):
        L = living[season]
        rows = []
        for nm in L:
            r = root0(nm)
            s0 = fsign(r)
            pa = planted_anc(nm)
            av = held.peek.own_links(ph(nm), sign=s0)
            h = held.hit(av, s0, "pay32")
            rows.append((nm, r, s0 is not None, bool(pa), h, pa))
        n_pr = sum(r[2] for r in rows)
        n_any = sum(r[3] for r in rows)
        k_pr = sum(r[4] for r in rows if r[2])
        k_bare = sum(r[4] for r in rows if not r[2])
        k_bare_pa = sum(r[4] for r in rows if not r[2] and r[3])
        clades = collections.Counter(r[1] for r in rows if r[2])
        print(f"\nseason {season}: living {len(L)}")
        print(f"  registered (parents[0] root): planted-rooted n = {n_pr}, k_planted = {k_pr}; bare-rooted {len(L) - n_pr}, k_bare = {k_bare}")
        print(f"  a planted founder anywhere in the ancestry (either parent): {n_any} of {len(L)}; "
              f"bare-rooted hits with a planted ancestor {k_bare_pa} of {k_bare}")
        print(f"  planted roots of the planted-rooted living (root: living): {dict(clades)}")


if __name__ == "__main__":
    main()
