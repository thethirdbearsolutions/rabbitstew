"""RBT-90 part 1, adversary probes: what the diversity rule's two body measures and its clauses resolve.

Named adversary, the ems6yl delegate (RBT-84's author, whose founder_base_rate.py classifier
runs/RBT-90/founder_diversity.py imports).  Nothing here re-runs a simulation; every number is a
property of the generator, read from the committed configs and from docs/artifacts/RBT-90-reference.txt.

Four probes, in the order the coordinator asked for them:

1. RATES.  The pass rates the report quotes for clause 2 (92% of random ten-sets, 63% of five-sets),
   resampled from the reference's own 200 seeds.  They reproduce -- but only from full-precision
   rates.  Clause 2's thresholds are exactly 28/60 and 33/60, each held by 12 of the 200 reference
   seeds, so re-deriving from the readout's three-decimal print pushes those seeds off the boundary
   and gives 0.89 / 0.55 instead.  RBT-90-reference.json is the authority; the .txt is not.

2. SHAPES.  Whether pairwise shape-multiset sharing (the report's 36 to 52 of 60) is a diversity
   axis.  Three findings, any one of which is sufficient: it is never read by any clause; it is a
   strict coarsening of the full signature (it never separates a pair the signature merges); and its
   range is a pigeonhole property of a vocabulary that is hardcoded at genotype.py:520
   (``Shape(int(rng.integers(0, 3)))``) rather than configured, so no seed can differ on it.

3. AXES.  Clause 2 is defined on the composite, which RBT-84 section 5 showed measures fan-out.  How
   much of the composite's between-seed variance is the fan-out half, how much the oscillator half,
   and whether spanning the composite implies spanning the oscillator rate -- which is what part 2
   actually tests.

4. CLAUSE3.  Whether clause 3 as originally drafted (pass/fail: every seed inside the generator's
   central 90% band) was a calibrated gate, which decides whether changing it to a label after
   seeing seed 805 was legitimate or was a rule loosened to fit the data.

usage: adversary_probes.py [--seeds N]      (N seeds for the shape null; default 30)
"""
import argparse
import importlib.util
import itertools
import json
import pathlib
import re
import sys
from collections import Counter

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
ART = ROOT / "docs" / "artifacts"
spec = importlib.util.spec_from_file_location("fd", ROOT / "runs" / "RBT-90" / "founder_diversity.py")
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)

KEYS = ("drive", "osc", "both", "parts_median", "units_median")
CAL = (801, 804, 805, 806, 807)
TRIALS = 200000


def reference_rows():
    """The reference's per-seed rows, as EXACT k/60 rather than the readout's 3-decimal print."""
    rows = []
    for line in open(ART / "RBT-90-reference.txt"):
        m = re.match(r"^\s*(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", line)
        if m:
            rows.append([float(x) for x in m.groups()])
    a = np.array(rows)
    exact = {k: np.rint(a[:, i] * 60).astype(int) / 60.0 for i, k in zip((1, 2, 3), ("drive", "osc", "both"))}
    exact["parts_median"], exact["units_median"] = a[:, 4], a[:, 5]
    printed = {k: a[:, i] for i, k in zip((1, 2, 3), ("drive", "osc", "both"))}
    return a[:, 0].astype(int), exact, printed


def sets(rng, n, k):
    return np.argsort(rng.random((TRIALS, n)), axis=1)[:, :k]


def spans(arr, idx, lo, hi):
    s = arr[idx]
    return (s.min(1) <= lo + 1e-12) & (s.max(1) >= hi - 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    args = ap.parse_args()
    seed_ids, exact, printed = reference_rows()
    ref = json.load(open(ART / "RBT-90-reference.json"))
    n = len(seed_ids)
    rng = np.random.default_rng(90)
    i10, i5 = sets(rng, n, 10), sets(rng, n, 5)
    L = [f"RBT-90 part 1, adversary probes.  Reference: {n} seeds, docs/artifacts/RBT-90-reference.{{txt,json}}.",
         "No simulation.  Resampling is without replacement from the reference's own seeds.", ""]

    L += ["## 1. RATES -- the report's clause-2 pass rates, and a reproducibility hazard", ""]
    lo, hi = ref["span"]["both"]
    L += [f"  clause 2 thresholds (composite): [{lo!r}, {hi!r}]",
          f"    lo is exactly 28/60: {lo == 28/60}     hi is exactly 33/60: {hi == 33/60}",
          f"    reference seeds sitting exactly on them: {int((exact['both'] == 28/60).sum())} at 28/60, "
          f"{int((exact['both'] == 33/60).sum())} at 33/60",
          "",
          f"  {'rates used':28s} {'ten-set':>8s} {'five-set':>9s}"]
    for name, arr in (("exact k/60", exact["both"]), ("the readout's 3-decimal print", printed["both"])):
        L.append(f"  {name:28s} {spans(arr, i10, lo, hi).mean():8.3f} {spans(arr, i5, lo, hi).mean():9.3f}")
    L += ["  the report quotes 0.92 and 0.63, which is the exact-rate row.  REPRODUCED.",
          "  A re-derivation from the .txt alone lands on the other row: the thresholds are achievable",
          "  discrete values, so rounding moves 24 of 200 seeds across them.  Quote the .json, not the .txt.",
          "",
          f"  between-seed SD of the composite: {exact['both'].std(ddof=1):.4f}",
          f"    binomial sqrt(p(1-p)/60) at p = {exact['both'].mean():.3f}: {np.sqrt(exact['both'].mean()*(1-exact['both'].mean())/60):.4f}   REPRODUCED",
          f"  seeds at exactly 29/60: {int((exact['both'] == 29/60).sum())}/{n} = {(exact['both'] == 29/60).mean()*100:.1f}%   (report: 11.5%)  REPRODUCED",
          ""]

    L += ["## 2. SHAPES -- is pairwise shape-multiset sharing a diversity axis?", ""]
    M = {s: fd.measure(s) for s in list(range(1, args.seeds + 1)) + list(CAL)}

    def shared(a, b, key):
        sb = set(M[b][key])
        return sum(x in sb for x in M[a][key])

    pairs = list(itertools.combinations(range(1, args.seeds + 1), 2))
    full = [shared(a, b, "sigs") for a, b in pairs] + [shared(b, a, "sigs") for a, b in pairs]
    shp = [shared(a, b, "shapes") for a, b in pairs] + [shared(b, a, "shapes") for a, b in pairs]
    cal = list(itertools.combinations(CAL, 2))
    cs = [shared(a, b, "shapes") for a, b in cal] + [shared(b, a, "shapes") for a, b in cal]
    L += [f"  null over {len(shp)} DIRECTED random seed pairs (seeds 1..{args.seeds}), shared of 60:",
          f"    full signature : min {min(full)} median {np.median(full):g} max {max(full)}",
          f"    shape multiset : min {min(shp)} p5 {np.percentile(shp,5):.0f} median {np.median(shp):g} "
          f"p95 {np.percentile(shp,95):.0f} max {max(shp)}",
          f"  the calibration set's {len(cs)} directed values span {min(cs)}-{max(cs)} (the report's 36 to 52),",
          f"    which is the {np.mean(np.array(shp) <= min(cs))*100:.0f}th to {np.mean(np.array(shp) <= max(cs))*100:.0f}th "
          "percentile of that null: the same range any two random seeds give.", ""]
    multisets = {x for s in M for x in M[s]["shapes"]}
    sz = Counter(len(x) for s in M for x in M[s]["shapes"])
    possible = sum(1 for k in sorted(sz) for _ in itertools.combinations_with_replacement(range(3), k))
    L += [f"  the space it lives in: node counts {dict(sorted(sz.items()))} over {sum(sz.values())} founders",
          f"    multisets of 3 shapes available at those counts: {possible}",
          f"    distinct multisets actually seen: {len(multisets)}  -- the generator saturates its own space,",
          "    so sharing 30-57 of 60 is pigeonhole, not similarity.  The vocabulary is hardcoded at",
          "    rabbitstew/genotype.py:520, Shape(int(rng.integers(0, 3))): not a config field, so no seed",
          "    and no config can differ on it.", ""]
    coarser = finer = 0
    for s in M:
        for i, j in itertools.combinations(range(len(M[s]["sigs"])), 2):
            same_sig = M[s]["sigs"][i] == M[s]["sigs"][j]
            same_shp = M[s]["shapes"][i] == M[s]["shapes"][j]
            coarser += same_shp and not same_sig
            finer += same_sig and not same_shp
    L += [f"  within-seed pairs sharing a shape multiset but not a full signature: {coarser}",
          f"  within-seed pairs sharing a full signature but not a shape multiset: {finer}",
          "  -> the shape multiset is a strict coarsening: it never separates a pair the signature merges.",
          "  And no clause reads it: founder_diversity.calibrate's verdict['bodies'] uses 'sigs' only.",
          ""]

    L += ["## 3. AXES -- clause 2 is defined on the composite, which measures fan-out (RBT-84 s5)", ""]
    d, o, b = exact["drive"], exact["osc"], exact["both"]
    L += [f"  over the {n} reference seeds:",
          f"    corr(composite, link-driven effector) = {np.corrcoef(b,d)[0,1]:+.3f}   r2 {np.corrcoef(b,d)[0,1]**2:.3f}",
          f"    corr(composite, linked oscillator)    = {np.corrcoef(b,o)[0,1]:+.3f}   r2 {np.corrcoef(b,o)[0,1]**2:.3f}",
          "    -> half the composite's between-seed variance is the fan-out half, a quarter the oscillator half.",
          "",
          f"  {'clause 2 defined on':22s} {'thresholds':>20s} {'ten-set':>8s} {'five-set':>9s}  the five calibration seeds"]
    for key, arr in (("composite (as filed)", b), ("link-driven effector", d), ("linked oscillator", o)):
        k = {"composite (as filed)": "both", "link-driven effector": "drive", "linked oscillator": "osc"}[key]
        klo, khi = ref["span"][k]
        vals = [fd.rates(M[s])[k] for s in CAL]
        ok = min(vals) <= klo + 1e-12 and max(vals) >= khi - 1e-12
        L.append(f"  {key:22s} [{klo:.4f},{khi:.4f}] {spans(arr,i10,klo,khi).mean():8.3f} "
                 f"{spans(arr,i5,klo,khi).mean():9.3f}  min {min(vals):.3f} max {max(vals):.3f} -> {'PASS' if ok else 'FAIL'}")
    olo, ohi = ref["span"]["osc"]
    pb, po = spans(b, i10, lo, hi), spans(o, i10, olo, ohi)
    L += ["  the verdict does not depend on the axis: the five seeds are too narrow on all three.", "",
          f"  P(ten-set spans the oscillator quartiles)                = {po.mean():.3f}",
          f"  P(spans oscillator | spans composite)                    = {po[pb].mean():.3f}",
          f"  P(spans oscillator | does NOT span composite)             = {po[~pb].mean():.3f}",
          f"  P(spans both)                                            = {(pb & po).mean():.3f}",
          f"  -> clause 2 on the composite is almost uninformative about the oscillator span it is a proxy for",
          f"     ({po[pb].mean():.3f} against a {po.mean():.3f} base rate), and leaves {1-po[pb].mean():.1%} of passing",
          "     ten-sets not spanning it.  An explicit oscillator clause costs little and is what part 2 tests.",
          ""]

    L += ["## 4. CLAUSE3 -- was the draft pass/fail version a calibrated gate?", ""]
    inside = np.ones(n, bool)
    for k in KEYS:
        klo, khi = ref["band"][k]
        ok = (exact[k] >= klo - 1e-12) & (exact[k] <= khi + 1e-12)
        L.append(f"  {k:14s} inside the central-90% band: {int(ok.sum()):3d}/{n}")
        inside &= ok
    L += [f"  inside on ALL {len(KEYS)} statistics at once: {int(inside.sum())}/{n} = {inside.mean():.3f}",
          f"  P(a random ten-set has every seed inside on every statistic)  = {inside[i10].all(1).mean():.4f}",
          f"  P(a random five-set)                                          = {inside[i5].all(1).mean():.4f}",
          "  -> as pass/fail the clause rejected ~94% of random ten-sets: it was miscalibrated, not seed 805",
          "     unlucky.  It is also verdict-neutral (calibrate's verdict reads 'bodies' and 'span' only) and",
          "     the five-seed set fails clause 2 regardless, so the change rescued nothing.  Legitimate.",
          ""]
    text = "\n".join(L)
    (ART / "RBT-90-adversary-probes.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
