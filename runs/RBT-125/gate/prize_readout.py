"""RBT-125 world gate, part A readout: the routed compass's prize at a = 6 per cell, across RBT-90 part 2's ten
populations (REGISTRATION.md §A, as amended per the coordinator's ruling of 22:28).  Reads
runs/RBT-125/gate/prize/<cell>-<seed>.txt (prize_gate.py's output).

Per population: the mean over its signed bodies of (motif at w = 3) - (the body's own base), 64 paired seeds; and,
where the cell ran the decoy, the same for the rotated-live-layout decoy.  A population with no readable ROW (every
body UNDETERMINED, a STOPPING, a crash) counts as prize 0 and decoy difference 0 (M2), and is listed.  Across the ten:
mean and Student t(9) 95% interval (RBT-106's prize statistic).  The gate lines are printed last.
"""
import os
import re

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
CELLS = ("PW-G2.5", "PW-G10", "PW-G0", "PW-G2.5-tau1", "HP-G2.5", "HP-G10", "U-G2.5", "U-G10", "HP-G0", "U-G0")
PRIMARY, ALTERNATIVE, CONTROL = "PW-G2.5", "PW-G10", "PW-G0"
HARNESS = {  # this tree's output -> the committed row it must reproduce to the digit
    "harness-801-uniform.txt": os.path.join(ROOT, "docs", "artifacts", "RBT-103-seed-801.txt"),
    "harness-801-HP.txt": os.path.join(ROOT, "runs", "RBT-106", "prize", "patchy-801.txt"),
}


def t_int(x):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - h, x.mean() + h


def fmt(t):
    return f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"


def row(path):
    m = re.search(r"^ROW .*$", open(path).read(), re.M) if os.path.exists(path) else None
    return m.group(0) if m else None


def read(path):
    """{gen: (sign, base, delta)}, motif mean, decoy mean, zero count, n, ROW -- or None when there is no ROW."""
    if row(path) is None:
        return None
    txt = open(path).read()
    body = {int(g): (int(s), float(b), float(d)) for g, s, b, d in re.findall(r"^g(\d+)\s+([+-]1)\s+(\d+\.\d+) \|\s+([+-]\d+\.\d+)\s*$", txt, re.M)}
    if not body:
        return None
    mot = re.search(r"^\s+motif\s+([+-]\d+\.\d+)", txt, re.M)
    dec = re.search(r"^\s+rotated decoy\s+([+-]\d+\.\d+)", txt, re.M)
    z = re.search(r"\]\s+\d+/\d+\s+(\d+)/(\d+) \|", txt)
    return (body, float(mot.group(1)) if mot else None, float(dec.group(1)) if dec else None,
            int(z.group(1)) if z else 0, int(z.group(2)) if z else 0, row(path))


def cell_rows(cell):
    return {s: read(os.path.join(HERE, "prize", f"{cell}-{s}.txt")) for s in SEEDS}


def prize(rows):
    """per-population prize over all ten, a missing population as 0"""
    return {s: (np.mean([v[2] for v in r[0].values()]) if r else 0.0) for s, r in rows.items()}


def decoy_diff(rows):
    return {s: ((r[1] - r[2]) if r and r[1] is not None and r[2] is not None else 0.0) for s, r in rows.items()}


def main():
    print("# RBT-125 world gate A: the routed compass's prize at a = 6 (w = 3), RBT-90 part 2's ten populations\n")
    for name, committed in HARNESS.items():
        a, b = row(os.path.join(HERE, "prize", name)), row(committed)
        print(f"harness check {name}: {a}")
        print(f"      committed {os.path.relpath(committed, ROOT)}: {b}  -> {'IDENTICAL' if a is not None and a == b else 'DIFFERENT'}")
    print("\nA population with no readable ROW counts as prize 0 (and decoy difference 0); n = readable of 10.")
    print("Per-population harness verdicts are not used: PW's sparse eating ties most pairs, so RBT-38's zero-count veto")
    print("fires on nearly every PW population and the per-population verdict is uninformative there.\n")
    print("| cell | n readable | missing | prize a=6, t(9) 95% | base income | motif - decoy, t(9) 95% | decoy retains | zero pairs |")
    print("|---|---|---|---|---|---|---|---|")
    P, R = {}, {}
    for cell in CELLS:
        rows = cell_rows(cell)
        n = sum(1 for r in rows.values() if r)
        if n == 0:
            continue
        R[cell], P[cell] = rows, prize(rows)
        base = np.mean([np.mean([v[1] for v in r[0].values()]) for r in rows.values() if r])
        has_dec = any(r and r[2] is not None for r in rows.values())
        dd = t_int(list(decoy_diff(rows).values())) if has_dec else None
        ret = (np.mean([r[2] for r in rows.values() if r and r[2] is not None]) / np.mean([r[1] for r in rows.values() if r and r[2] is not None])) if has_dec else None
        zs = sum(r[3] for r in rows.values() if r), sum(r[4] for r in rows.values() if r)
        print(f"| {cell} | {n} | {','.join(str(s) for s, r in rows.items() if not r) or '-'} | {fmt(t_int(list(P[cell].values())))} | {base:.3f} | "
              f"{fmt(dd) if dd else '--'} | {f'{100 * ret:.0f}%' if ret is not None else '--'} | {zs[0]}/{zs[1]} |")

    print("\n## the channel's own contribution (M1): cell - its G = 0 control, paired by population, t(9)")
    contrib = {}
    for cell in CELLS:
        ctl = cell.split("-")[0] + "-G0"
        if cell == ctl or cell not in P or ctl not in P:
            continue
        contrib[cell] = t_int([P[cell][s] - P[ctl][s] for s in SEEDS])
        same = []
        for s in SEEDS:
            a, b = R[cell][s], R[ctl][s]
            common = [g for g in (a[0] if a else {}) if b and g in b[0] and a[0][g][0] == b[0][g][0]] if a and b else []
            if common:
                same.append(np.mean([a[0][g][2] - b[0][g][2] for g in common]))
        extra = f";  on bodies signed the same in both cells: {fmt(t_int(same))} over {len(same)} populations" if len(same) > 1 else ""
        print(f"  {cell} - {ctl}: {fmt(contrib[cell])}{extra}")

    print("\n## the gate (REGISTRATION.md §A, amended)")
    print("PASS at a cell: all 10 populations counted (missing = 0), prize t(9) lower bound > 0 AND motif - decoy lower bound > 0.")
    print("It is a claim about the WORLD (\"PW pays an installed compass at a = 6\"); a claim that THE CHANNEL pays also needs")
    print("(cell - PW-G0) lower bound > 0.  Two shots (G2.5, then G10 only if G2.5 fails): familywise one-sided alpha <= 2 x 2.5% = 5%.")
    verdict = {}
    for cell in (PRIMARY, ALTERNATIVE, CONTROL):
        if cell not in P:
            print(f"GATE {cell}: not run")
            continue
        p = t_int(list(P[cell].values()))
        dd = t_int(list(decoy_diff(R[cell]).values()))
        ok = p[1] > 0 and dd[1] > 0
        ch = contrib.get(cell)
        verdict[cell] = (ok, ch is not None and ch[1] > 0)
        chs = "" if ch is None else f", channel {fmt(ch)} -> {'THE CHANNEL PAYS' if ch[1] > 0 else 'channel contribution unresolved'}"
        print(f"GATE {cell}: n {sum(1 for r in R[cell].values() if r)}/10, prize {fmt(p)}, motif - decoy {fmt(dd)} -> {'PASS' if ok else 'FAIL'}{chs}")
    if PRIMARY in verdict:
        if verdict[PRIMARY][0]:
            v = "PASS at G = 2.5"
            ch = verdict[PRIMARY][1]
        elif ALTERNATIVE in verdict and verdict[ALTERNATIVE][0]:
            v = "PASS at G = 10 (the fallback; saturation and approach-speed gating caveat)"
            ch = verdict[ALTERNATIVE][1]
        else:
            v, ch = "FAIL", False
        print(f"GATE VERDICT: {v}" + ("" if v == "FAIL" else (" -- the channel pays" if ch else " -- a claim about the world; the channel's contribution is not resolved")))


if __name__ == "__main__":
    main()
