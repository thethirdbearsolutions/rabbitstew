"""Which saved bests carry a smell sensor, and how many of the final population do.

Prints, per population, the generations whose saved best has a food or agent sensor (the
candidates the issue asks to probe) and the share of the final members carrying one.
Usage: nosed_bests.py <run>
"""
import glob, json, os, re, sys
from rabbitstew.genotype import Genotype

run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-22/W1b-801"


def smells(g):
    return sorted({u.source for _, b in g.brains() for u in b.units if u.kind == "sensor" and u.source in ("food", "agent")})


def sources(g):
    return sorted({u.source for _, b in g.brains() for u in b.units if u.kind == "sensor"})


for kind in ("holistic", "conventional"):
    paths = sorted(glob.glob(f"{run}/{kind}/best_gen*.json"))
    nosed = []
    for p in paths:
        gen = int(re.search(r"best_gen(\d+)", p).group(1))
        g = Genotype.load(p)
        s = smells(g)
        print(f"{kind} g{gen:4d} smell {s if s else '-':<20} all sensors {sources(g)}")
        if s:
            nosed.append(gen)
    print(f"{kind}: {len(nosed)} of {len(paths)} saved bests carry a smell sensor: {nosed}")
    final = f"{run}/{kind}/final"
    members = sorted(glob.glob(f"{final}/*.json"))
    if not members and os.path.isdir(final):
        members = sorted(glob.glob(f"{final}/**/*.json", recursive=True))
    have = [os.path.basename(m) for m in members if smells(Genotype.load(m))]
    print(f"{kind}: {len(have)} of {len(members)} final members carry a smell sensor")
    print()
