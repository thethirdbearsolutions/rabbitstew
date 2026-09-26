"""RBT-110 readout adversary: read probe_reproduce.raw.

  R1  reproduction: the per-seed RESPONSE (shift - base, new world) and RESPONSE_null (cull20 - base), per fauna and
      paired, from this adversary's independent implementation (lineage rule), against the analysts' split.txt
      (parsed by probe_pool.vec); the largest absolute per-seed difference
  R2  measurement noise of one seed's paired RESPONSE: the sd over the D = 4 draws of the draw-level paired RESPONSE,
      / sqrt(D) (draws share start seeds across populations, so the draw-level difference is the harness's own)
  R3  the played rule (every robot in the season's arenas, re-grouped by the same stream): the primary statistic per
      challenge under it; the per-seed test-retest difference (played - lineage), its sd as the grouping noise;
      and the sign counts (lesson: jitter the sign guard)

    python runs/RBT-110/readout-adversary/probe_reproduce_read.py > runs/RBT-110/readout-adversary/probe_reproduce.txt
"""
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from probe_pool import SEEDS, fmt, sub, vec  # noqa: E402

G = {}
for line in open(os.path.join(HERE, "probe_reproduce.raw")):
    if line.startswith("challenge") or line.startswith("#"):
        continue
    ch, s, p, k, rule, d, n, m = line.split()
    G[(ch, int(s), p, k, rule, int(d))] = float(m)
CH = ["C1", "C2", "C3", "C4null"]
KF = {"co": "holistic", "des": "conventional"}


def g(ch, s, p, k, rule, d=None):
    if d is None:
        v = [G.get((ch, s, p, k, rule, dd)) for dd in range(4)]
        return None if None in v else st.fmean(v)
    return G.get((ch, s, p, k, rule, d))


def resp(ch, f, rule, other="base", d=None):
    out = []
    for s in SEEDS:
        if f == "pair":
            a, b = resp1(ch, s, "co", rule, other, d), resp1(ch, s, "des", rule, other, d)
            out.append(None if a is None or b is None else a - b)
        else:
            out.append(resp1(ch, s, f, rule, other, d))
    return out


def resp1(ch, s, f, rule, other, d):
    first = "shift" if other == "base" else "cull20"
    a, b = g(ch, s, first, KF[f], rule, d), g(ch, s, "base", KF[f], rule, d)
    return None if a is None or b is None else a - b


print(__doc__.split("\n\n")[0])
print()
print("R1  reproduction of the analysts' per-seed values at T + 110 (lineage rule), max |difference| over seeds")
for ch in CH:
    for f in ("co", "des", "pair"):
        for q, other in (("resp", "base"), ("null", "cull20")):
            mine = resp(ch, f, "lineage", "base" if q == "resp" else "null")
            theirs = vec(ch, 110, f, q)
            both = [(a, b) for a, b in zip(mine, theirs) if a is not None and b is not None]
            miss = [(s, a, b) for s, a, b in zip(SEEDS, mine, theirs) if (a is None) != (b is None)]
            dmax = max(abs(a - b) for a, b in both)
            print(f"   {ch:6s} {f:4s} {q:4s}  n {len(both):2d}  max|mine - split.txt| {dmax:.4f}  "
                  f"{'(rounding only)' if dmax <= 0.0006 else 'DIFFERS'}  mine {fmt(mine)}"
                  + (f"  coverage mismatch {miss}" if miss else ""))
print()
print("R2  measurement noise of one seed's paired RESPONSE (sd over the 4 draws / 2), lineage rule")
for ch in CH:
    ses = []
    for s in SEEDS:
        v = [resp1(ch, s, "co", "lineage", "base", d) for d in range(4)]
        w = [resp1(ch, s, "des", "lineage", "base", d) for d in range(4)]
        if None in v or None in w:
            continue
        ses.append(st.stdev([a - b for a, b in zip(v, w)]) / 2)
    between = st.stdev([x for x in resp(ch, "pair", "lineage") if x is not None])
    rms = math.sqrt(st.fmean([x * x for x in ses]))
    print(f"   {ch:6s} per-seed noise se (RMS over seeds) {rms:.3f};  between-seed sd of the paired RESPONSE {between:.3f};  "
          f"share of between-seed variance that is draw noise {min(1, rms ** 2 / between ** 2):.2f}")
print()
print("R3  the played rule (aged-out robots included; every arena re-cut by the same stream)")
for ch in CH:
    lin, pla = resp(ch, "pair", "lineage"), resp(ch, "pair", "played")
    dd = [x for x in sub(pla, lin) if x is not None]
    print(f"   {ch:6s} paired RESPONSE  lineage {fmt(lin)}")
    print(f"   {'':6s}                  played  {fmt(pla)}")
    print(f"   {'':6s} test-retest (played - lineage) per seed: sd {st.stdev(dd):.3f}, mean {st.fmean(dd):+.3f}; "
          f"sign agrees on {sum((a > 0) == (b > 0) for a, b in zip(lin, pla) if a is not None and b is not None)}/{len(dd)} seeds")
    for f in ("co", "des"):
        print(f"   {'':6s} {f:4s} RESPONSE lineage {fmt(resp(ch, f, 'lineage'))}   played {fmt(resp(ch, f, 'played'))}")
