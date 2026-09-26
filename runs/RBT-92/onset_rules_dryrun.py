"""RBT-92: the three onset rules compared on RBT-71's committed selected arms (design only; part 1's
founders, not RBT-92's seeds; no run).  For each rule: the T it returns and the natural deaths in the
baseline around T, in ten-season windows from T - 30.  A rule that puts [T, T + 10) on the wave's rising
edge places the event on the transient RBT-89 section 8 forbids.

    python runs/RBT-92/onset_rules_dryrun.py > runs/RBT-92/onset_rules_dryrun.txt
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["RBT92_BASELINE_DIR"] = os.path.join(HERE, "..", "RBT-71")
spec = importlib.util.spec_from_file_location("onset", os.path.join(HERE, "onset.py"))
onset = importlib.util.module_from_spec(spec)
spec.loader.exec_module(onset)
KINDS = ("holistic", "conventional")


def rules(d):
    tot = lambda s0, s1: sum(d.get((t, k), 0) for t in range(s0, s1) for k in KINDS)
    sym = min(range(340, 401), key=lambda T: (tot(T - 10, T + 10), -T))
    pre = min(range(340, 401), key=lambda T: (tot(T - 20, T), -T))
    return {"12:42 posted: min deaths [T-10,T+10)": sym, "13:10 ruling: min deaths [T-20,T)": pre}


print(__doc__.split("\n\n")[0])
print()
for seed in (804, 805, 806):
    path = os.path.join(os.environ["RBT92_BASELINE_DIR"], f"forage-{seed}", "seasons.txt")
    d, _ = onset.deaths_alive(path)
    rs = rules(d)
    rs["amendment 2: half a period after the last wave in [280,340)"] = onset.onset(seed)[0]
    for name, T in rs.items():
        cells = []
        for k in KINDS:
            w = [sum(d.get((t, k), 0) for t in range(u, u + 10)) for u in range(T - 30, T + 40, 10)]
            cells.append(f"{k} {w}")
        print(f"forage-{seed}  {name:58s} T={T}  deaths/10 seasons from T-30: " + "  ".join(cells))
        print(f"{'':14s}{'':58s}        [T,T+10): holistic {sum(d.get((t, 'holistic'), 0) for t in range(T, T + 10))}, "
              f"conventional {sum(d.get((t, 'conventional'), 0) for t in range(T, T + 10))}")
    print()
