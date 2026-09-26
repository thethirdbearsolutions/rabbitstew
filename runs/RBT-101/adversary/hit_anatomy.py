"""RBT-101 adversary probe C: what a natural `new` hit is made of.  For every hit in the baseline's C0 (alive at 139)
-> P (alive at 300) window, the committed control window, compare the survivor with its C0 ancestor of largest g1:
did it gain posture SENSORS (ns, a body change) or links on the sensors it already had (n1 with ns unchanged)?
§3 of the protocol: in C4 "re-adapts" could mean "a new use of an existing sensor".

    PYTHONPATH=. python runs/RBT-101/adversary/hit_anatomy.py RUN_DIR... > runs/RBT-101/adversary/hit_anatomy.txt
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import turnover_probe as tp  # noqa: E402
import wiring  # noqa: E402


def dig(run, kind, name, syn, cache):
    from rabbitstew.genotype import Genotype
    from rabbitstew.synthesis import synthesize
    if (kind, name) not in cache:
        cache[(kind, name)] = wiring.digest(synthesize(Genotype.load(os.path.join(run, kind, "genomes", f"{name}.json")), syn))
    return cache[(kind, name)]


print("# RBT-101 adversary probe C: anatomy of natural `new` hits, baseline, C0 alive at 139, P alive at 300")
tot = {k: [0, 0, 0] for k in tp.KINDS}
for run in sys.argv[1:]:
    syn = wiring.sim_config(run).synthesis
    life, parents = tp.lineage(run)
    cache = {}
    for kind in tp.KINDS:
        alive = lambda s: {n for (k, n), (b, l) in life.items() if k == kind and b <= s <= l}
        c0, P = alive(139), alive(300)
        hits = more_sensors = 0
        for n in sorted(P):
            stack, seen, anc = [n], set(), set()
            while stack:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x)
                if x in c0:
                    anc.add(x)
                    continue
                stack.extend(parents.get((kind, x), []))
            if not anc:
                continue
            d = dig(run, kind, n, syn, cache)
            A = [dig(run, kind, a, syn, cache) for a in anc]
            top = max(A, key=lambda r: r["g1"])
            if d["g1"] >= top["g1"] + 0.5:
                hits += 1
                more_sensors += d["ns"] > max(a["ns"] for a in A)
        tot[kind][0] += hits
        tot[kind][1] += more_sensors
        print(f"{os.path.basename(run)}\t{kind}\thits {hits}\twith more posture sensors than every C0 ancestor {more_sensors}")
for kind in tp.KINDS:
    h, m, _ = tot[kind]
    print(f"# {kind}: {m}/{h} hits carry more posture sensors than any C0 ancestor (a body change); {h - m}/{h} are links on a sensor set no larger")
