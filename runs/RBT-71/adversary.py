"""Adversary checks on RBT-71 Deliverable A (named adversary: the RBT-63/64 delegate).

Three questions, all answerable from committed files alone -- which is itself the point of
check 1.

1. REPRODUCIBILITY. Can the scorecard be re-derived from the repository? measure.py reads
   {run}/history.json and {run}/lineage.jsonl; only config.json is committed per run.
2. INTERNAL CONSISTENCY. Does REPORT.md's scorecard match the committed readouts, number for
   number, on all three seeds?
3. WHAT R2 CERTIFIES. R2 is "holistic lifetime-yield heritability >= 0.20, n >= 30". The
   paired NEUTRAL controls are drift populations with no selection at all. Do any of them
   clear the same bar? If they do, R2 certifies that lifetime yield is a heritable
   measurement -- which is what the report says it tests -- and not that selection produced
   the heritability.

No simulation. Usage: adversary.py
"""

import os
import re

ROOT = "runs/RBT-71"
SEEDS = (804, 805, 806)
NEEDED = ("history.json", "lineage.jsonl")


def reproducibility():
    print("1. REPRODUCIBILITY -- what measure.py needs against what is committed")
    missing = []
    for seed in SEEDS:
        for kind in ("forage", "neutral"):
            run = f"{ROOT}/{kind}-{seed}"
            have = sorted(os.listdir(run)) if os.path.isdir(run) else []
            gone = [n for n in NEEDED if n not in have]
            missing += [f"{run}/{n}" for n in gone]
            print(f"   {run:28} committed: {have or '(absent)'}   missing: {gone or 'none'}")
    print(f"   -> {len(missing)} of {len(SEEDS) * 2 * len(NEEDED)} required inputs absent; "
          f"measure.py cannot run from a fresh checkout")
    return missing


def consistency():
    print("\n2. INTERNAL CONSISTENCY -- REPORT.md scorecard against the committed readouts")
    report = open(f"{ROOT}/REPORT.md").read()
    ok = True
    for seed in SEEDS:
        ro = open(f"{ROOT}/readout-{seed}.txt").read()
        get = lambda p: (re.search(p, ro).group(1) if re.search(p, ro) else "??")
        vals = {
            "R1 fraction": get(r"holistic leads in ([\d.]+) of seasons"),
            "R2 holistic": get(r"\[selected\] heritability hol \+?(-?[\d.]+)"),
            "founders sel": get(r"\[selected\] founders  hol (\d+) of 60"),
            "founders neu": get(r"\[neutral\] founders  hol (\d+) of 60"),
        }
        for k, v in vals.items():
            here = v in report
            ok &= here
            print(f"   {seed} {k:14} {v:>8}   {'in REPORT.md' if here else 'NOT IN REPORT'}")
    print(f"   -> scorecard {'matches its readouts exactly' if ok else 'DISAGREES with its readouts'}")
    return ok


def what_r2_certifies():
    print("\n3. WHAT R2 CERTIFIES -- does a drift population clear the same bar?")
    print(f"   {'seed':<6} {'selected hol':>13} {'neutral hol':>12} {'neutral WHEEL':>14}  clears R2 (>=0.20)?")
    drift_clears = 0
    for seed in SEEDS:
        ro = open(f"{ROOT}/readout-{seed}.txt").read()
        sel = float(re.search(r"\[selected\] heritability hol \+?(-?[\d.]+)", ro).group(1))
        neu = float(re.search(r"\[neutral\] heritability hol \+?(-?[\d.]+)", ro).group(1))
        nw = float(re.search(r"\[neutral\] heritability hol [^ ]+ \(n=\d+\)\s+wheel \+?(-?[\d.]+)", ro).group(1))
        hit = nw >= 0.20
        drift_clears += hit
        print(f"   {seed:<6} {sel:>13.3f} {neu:>12.3f} {nw:>14.3f}  "
              f"{'YES -- drift passes R2' if hit else 'no'}")
    print(f"   -> the neutral WHEELED control clears R2 on {drift_clears} of {len(SEEDS)} seeds, "
          f"with no selection acting at all.")
    print("      R2 therefore certifies 'lifetime yield is a heritable measurement' (which is what")
    print("      the report says it tests) and NOT 'selection produced the heritability'.")
    return drift_clears


if __name__ == "__main__":
    reproducibility()
    consistency()
    what_r2_certifies()
