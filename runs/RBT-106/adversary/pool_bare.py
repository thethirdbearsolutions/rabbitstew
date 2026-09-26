"""Pool bare_patchy/bare-patchy-SEED.txt: RBT-90 part 2's own champions (no compass anywhere, never
selected in the patchy world), bests 300..590, scored by readout (b) in the patchy world through the
designer's cross_world.py, unchanged.  This is the matched null for a "FOOD-DEPENDENT" line call in the
patchy scoring (the designer's power.py assumes 0.10, from the uniform world, and N(0.10, 0.20) for F).

Printed: each line's call, F, zero count and compass attribution; the pooled rate of FOOD-DEPENDENT calls;
the mean and SD of line F (the power model's bare distribution); and the per-body F spread, including
bodies whose F is non-zero with the compass lesion changing nothing (smell used outside any global
compass: lesioned == intact).

Usage: pool_bare.py
"""
import glob
import os
import re

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
LINE = re.compile(r"^LINE (\S+): (FOOD-DEPENDENT|not food-dependent|NEGATIVE|VETOED by the zero count)\s+F ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\]\s+compass (.*?)\s+bodies")
ZEROS = re.compile(r"the champion\s+F .*\(zeros (\d+)/(\d+)\)")
BODY = re.compile(r"^g(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+) \|\s+([+-][\d.]+)\s+([+-][\d.]+)", re.M)


def main():
    print("# RBT-106 adversary: part 2's bare champions scored in the patchy world (readout (b), cross_world.py unchanged)\n")
    print("| line | call | F [95%] | zeros | compass attribution | bodies with |F| >= 0.25 and lesion = intact |")
    print("|---|---|---|---|---|---|")
    Fs, calls, zs, lesion_same = [], [], [], 0
    nb = 0
    for p in sorted(glob.glob(os.path.join(_HERE, "bare_patchy", "bare-patchy-*.txt"))):
        txt = open(p).read()
        m = re.search(LINE.pattern, txt, re.M)
        if not m:
            print(f"| {os.path.basename(p)} | (not finished) | | | | |")
            continue
        z = ZEROS.search(txt)
        big = []
        for b in BODY.finditer(txt):
            nb += 1
            gen, it, dc, le, F = int(b.group(1)), float(b.group(2)), float(b.group(3)), float(b.group(4)), float(b.group(5))
            if abs(F) >= 0.25 and it == le:
                big.append(f"g{gen} {F:+.2f}")
        lesion_same += len(big)
        Fs.append(float(m.group(3)))
        calls.append(m.group(2))
        zs.append(int(z.group(1)) / int(z.group(2)))
        print(f"| {m.group(1)} | {m.group(2)} | {m.group(3)} [{m.group(4)}, {m.group(5)}] | {z.group(1)}/{z.group(2)} | {m.group(6)} | {', '.join(big) or '-'} |")
    n = len(Fs)
    fd = sum(c == "FOOD-DEPENDENT" for c in calls)
    print(f"\nlines: {n}; FOOD-DEPENDENT: {fd} ({fd / n:.2f}); VETOED: {sum(c.startswith('VETOED') for c in calls)}; "
          f"not food-dependent / NEGATIVE: {sum(c in ('not food-dependent', 'NEGATIVE') for c in calls)}")
    print(f"line F: mean {np.mean(Fs):+.3f}, SD {np.std(Fs, ddof=1):.3f} (designer's model: N(+0.10, 0.20)); "
          f"zero-count share: mean {np.mean(zs):.2f}, range {min(zs):.2f}-{max(zs):.2f} (veto above 0.50)")
    print(f"bodies with |F| >= 0.25 while the compass lesion leaves income unchanged (smell used outside any compass): {lesion_same} of {nb}")


if __name__ == "__main__":
    main()
