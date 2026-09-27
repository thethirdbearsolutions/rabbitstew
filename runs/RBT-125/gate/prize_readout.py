"""RBT-125 world gate, part A readout: the routed compass's prize at a = 6 per cell, across RBT-90 part 2's ten
populations (REGISTRATION.md §A).  Reads runs/RBT-125/gate/prize/<cell>-<seed>.txt (prize_gate.py's output).

Per population: the mean over its signed bodies of (motif at w = 3) - (the body's own base), 64 paired seeds; and,
where the cell ran the decoy, the same for the rotated-live-layout decoy.  Across populations: mean and Student
t(n - 1) 95% interval (RBT-106's prize statistic).  The gate line is printed last.
"""
import os
import re

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
CELLS = ("PW-G2.5", "PW-G10", "PW-G0", "HP-G2.5", "HP-G10", "U-G2.5", "U-G10", "HP-G0", "U-G0")
PRIMARY, ALTERNATIVE, CONTROL = "PW-G2.5", "PW-G10", "PW-G0"


def t_int(x):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - h, x.mean() + h


def fmt(t):
    return f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"


def read(path):
    """(per-body {gen: (base, delta)}, motif mean or None, decoy mean or None, zero count, n, ROW)"""
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    if "ROW" not in txt:
        return None
    body = {int(g): (float(b), float(d)) for g, b, d in re.findall(r"^g(\d+)\s+[+-]1\s+(\d+\.\d+) \|\s+([+-]\d+\.\d+)\s*$", txt, re.M)}
    mot = re.search(r"^\s+motif\s+([+-]\d+\.\d+)", txt, re.M)
    dec = re.search(r"^\s+rotated decoy\s+([+-]\d+\.\d+)", txt, re.M)
    z = re.search(r"\]\s+\d+/\d+\s+(\d+)/(\d+) \|", txt)
    row = re.search(r"^ROW .*$", txt, re.M).group(0)
    return body, float(mot.group(1)) if mot else None, float(dec.group(1)) if dec else None, int(z.group(1)) if z else None, int(z.group(2)) if z else None, row


def main():
    print("# RBT-125 world gate A: the routed compass's prize at a = 6 (w = 3), RBT-90 part 2's ten populations\n")
    h = os.path.join(HERE, "prize", "harness-801-uniform.txt")
    c = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "docs", "artifacts", "RBT-103-seed-801.txt")
    if os.path.exists(h) and read(h):
        a, b = read(h)[5], re.search(r"^ROW .*$", open(c).read(), re.M).group(0)
        print(f"harness check (this tree, restored bodies, own world, seed 801, a = 32/64): {a}")
        print(f"                                                    committed RBT-103: {b}  -> {'IDENTICAL' if a == b else 'DIFFERENT'}\n")
    per = {}
    print("| cell | populations | prize a=6 (t 95%) | base income | motif - decoy (t 95%) | decoy retains | zero pairs |")
    print("|---|---|---|---|---|---|---|")
    for cell in CELLS:
        rows = {s: read(os.path.join(HERE, "prize", f"{cell}-{s}.txt")) for s in SEEDS}
        rows = {s: r for s, r in rows.items() if r and r[0]}
        if len(rows) < 2:
            continue
        d = {s: np.mean([v[1] for v in r[0].values()]) for s, r in rows.items()}
        base = [np.mean([v[0] for v in r[0].values()]) for r in rows.values()]
        per[cell] = d
        dec = [r[1] - r[2] for r in rows.values() if r[2] is not None]
        ret = np.mean([r[2] for r in rows.values() if r[2] is not None]) / np.mean([r[1] for r in rows.values() if r[2] is not None]) if dec else None
        zs = sum(r[3] for r in rows.values() if r[3] is not None), sum(r[4] for r in rows.values() if r[4] is not None)
        print(f"| {cell} | {len(rows)} | {fmt(t_int(list(d.values())))} | {np.mean(base):.3f} | {fmt(t_int(dec)) if len(dec) > 1 else '--'} | "
              f"{f'{100 * ret:.0f}%' if ret is not None else '--'} | {zs[0]}/{zs[1]} |")
    print("\n## the channel's own contribution, paired by population (cell - its G = 0 control)")
    for cell in CELLS:
        ctl = cell.split("-")[0] + "-G0"
        if cell == ctl or cell not in per or ctl not in per:
            continue
        common = sorted(set(per[cell]) & set(per[ctl]))
        print(f"  {cell} - {ctl}: {fmt(t_int([per[cell][s] - per[ctl][s] for s in common]))}  (n {len(common)})")
    print("\n## the gate (REGISTRATION.md §A): PASS at a cell if the prize's t lower bound > 0 AND motif - decoy's lower bound > 0")
    for cell in (PRIMARY, ALTERNATIVE, CONTROL):
        if cell not in per:
            print(f"GATE {cell}: not run")
            continue
        rows = {s: read(os.path.join(HERE, "prize", f"{cell}-{s}.txt")) for s in SEEDS}
        rows = {s: r for s, r in rows.items() if r and r[0]}
        p = t_int(list(per[cell].values()))
        dec = [r[1] - r[2] for r in rows.values() if r[2] is not None]
        dd = t_int(dec) if len(dec) > 1 else (np.nan, np.nan, np.nan)
        ok = p[1] > 0 and dd[1] > 0
        print(f"GATE {cell}: prize {fmt(p)}, motif - decoy {fmt(dd)} -> {'PASS' if ok else 'FAIL'}")


if __name__ == "__main__":
    main()
