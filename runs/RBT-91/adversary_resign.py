"""RBT-91 adversary re-check of PR #63 (the RBT-89 delegate).

1. The links-alone column for every baseline arrival: the predicate unit's own small-signal
   response with the rest of the brain silenced, beside the whole-brain figure the readout
   reports, so the conditional fraction can be read on the motif's own gain (no simulation).
2. The heading probe is 2 seeds x 3 s, and compass/anti-compass is decided by whether |heading|
   exceeds 90 degrees. Arrivals whose heading lies within 25 degrees of sideways are re-measured at
   RBT-80's full reference (16 seeds x 15 s) to see whether any verdict flips; the -6.33 arrival
   (#176, +107.5 degrees on the short probe) is one of them.

Usage: adversary_resign.py docs/artifacts/RBT-91-drift-baseline.txt docs/artifacts/RBT-91-resigned-84.txt
"""
import importlib.util
import os
import re
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_argv, sys.argv = sys.argv, ["resign_arrivals.py"]
_s = importlib.util.spec_from_file_location("ra", os.path.join(_HERE, "resign_arrivals.py"))
ra = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ra)
sys.argv = _argv
sr, rbt80 = ra.sr, ra.rbt80
from rabbitstew.synthesis import synthesize

PAYING = 6.8664


def links_alone(ph, k):
    noses = sr._wheel_noses(ph)
    le, re_ = sr.drive_effector_units(ph)
    motif = lambda s, d: (s in noses and d == k) or (s == k and (d in le or d in re_))
    saved = ph.links
    ph.links = [l for l in saved if motif(l[0], l[1])]
    alone = sr.small_signal_a(ph)
    ph.links = [l for l in saved if not motif(l[0], l[1])]
    removed = sr.small_signal_a(ph)
    ph.links = saved
    return alone, removed


def main():
    readout, resigned = sys.argv[1], sys.argv[2]
    arrivals = ra.from_readout(readout)
    verdicts = {}
    for line in open(resigned):
        m = re.match(r"\| (\S+) #(\d+) \| ([-+\d.]+) \| ([-+\d.]+) deg \| (\w+) \| \*\*([-+\d.]+)\*\* \| \*\*(\S+)\*\* \|", line)
        if m:
            verdicts[(m.group(1), int(m.group(2)))] = (float(m.group(4)), m.group(5), m.group(7))
    print(f"# RBT-91 adversary re-check of PR #63: {len(arrivals)} baseline arrivals\n")
    print("## 1. The motif unit's own response (links alone) beside the whole-brain response\n")
    print(f"| arrival | whole brain | links alone | links removed | verdict (2x3s) |")
    print(f"|---|---|---|---|---|")
    alone_vals, whole_vals = [], []
    near = []
    for label, i in arrivals:
        g, cfg = ra.regenerate(label, i)
        ph = synthesize(g, cfg.sim.synthesis)
        units = sr.motif_units(ph)
        whole = sr.small_signal_a(ph)
        alone, removed = links_alone(ph, units[0])
        h, drv, v = verdicts.get((label, i), (float("nan"), "?", "?"))
        alone_vals.append(abs(alone)); whole_vals.append(abs(whole))
        print(f"| {label} #{i} | {whole:+.4f} | {alone:+.4f} | {removed:+.4f} | {v} ({h:+.1f} deg) |")
        if np.isfinite(h) and abs(abs(h) - 90) <= 25:
            near.append((label, i, h, v, whole))
    a = np.array(alone_vals); w = np.array(whole_vals)
    print(f"\n  whole brain: {(w >= PAYING).sum()} of {len(w)} reach the paying-rung reference {PAYING}; median {np.median(w):.4f}, max {w.max():.4f}")
    print(f"  links alone: {(a >= PAYING).sum()} of {len(a)} reach it; median {np.median(a):.4f}, max {a.max():.4f}; "
          f"{(a >= 3.5657).sum()} reach the null rung 3.57")
    print(f"  links alone as a fraction of whole brain, median over arrivals with |whole| > 0.1: "
          f"{np.median([x / y for x, y in zip(alone_vals, whole_vals) if y > 0.1]):.3f}")
    print(f"\n## 2. Headings within 25 degrees of sideways, re-measured at RBT-80's reference (16 seeds x 15 s)\n")
    print(f"  short probe: {rbt80.PROBE_SEEDS} seeds x {rbt80.PROBE_DUR:g} s; near-sideways arrivals: {len(near)}\n")
    rbt80.PROBE_SEEDS, rbt80.PROBE_DUR = 16, 15.0
    print(f"| arrival | whole brain | heading 2x3s | verdict 2x3s | heading 16x15s | verdict 16x15s | flips? |")
    print(f"|---|---|---|---|---|---|---|")
    flips = 0
    for label, i, h, v, whole in near:
        g, cfg = ra.regenerate(label, i)
        h2 = ra.heading(g, cfg)
        if h2 is None:
            print(f"| {label} #{i} | {whole:+.4f} | {h:+.1f} | {v} | never moved | ? | ? |"); continue
        back = abs(h2) > 90
        signed = whole if (back == rbt80.FOUNDER_BACKWARD) else -whole
        v2 = "COMPASS" if signed > 0 else "ANTI-COMPASS"
        flips += v2 != v
        print(f"| {label} #{i} | {whole:+.4f} | {h:+.1f} | {v} | {h2:+.1f} | {v2} | {'YES' if v2 != v else 'no'} |")
    print(f"\n  verdicts that flip at the reference probe: {flips} of {len(near)}")


if __name__ == "__main__":
    main()
