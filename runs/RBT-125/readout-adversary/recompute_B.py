"""RBT-125 readout adversary, pass 2: re-derive §B from the committed step files, independently of steps.py.

Reads only the per-host table of runs/RBT-125/gate/steps/<cell>.txt (per-host mean items per arm, 128 paired seeds,
printed to 3 decimals; and the realised speed ratio r per speed arm), and recomputes with its own code:
  nose steps (w0->0.4, w1->1.4, w3->3.4), raw speed steps at w0/w1/w3, per-unit speed steps
  ((speed@w - w) x 0.25 / (r - 1), hosts with r >= 1.10 only, amendment A1.4), and nose - speed per host;
  the 95% and 90% t intervals with HARD-CODED t quantiles (no scipy; df 9..14), and the registered reading
  (NOSE LEADS: 95% lo > 0; SPEED LEADS: 95% hi < 0; COMPARABLE: 90% interval inside +-0.10; else TIED).
Also printed, for the "no COMPARABLE" question: whether any line's 90% interval lies inside +-0.10 regardless of
precedence, and the half-width a line would need.  Values agree with steps.py to the 3rd decimal only (the table is
rounded); the readings are what matter.

    python recompute_B.py GATE_DIR
"""
import os, re, sys
import numpy as np

T975 = {9: 2.262157, 10: 2.228139, 11: 2.200985, 12: 2.178813, 13: 2.160369, 14: 2.144787}
T95 = {9: 1.833113, 10: 1.812461, 11: 1.795885, 12: 1.782288, 13: 1.770933, 14: 1.761310}
DELTA, R_MIN = 0.10, 1.10


def ci(x, table):
    x = np.asarray(x, float); n = len(x)
    h = table[n - 1] * x.std(ddof=1) / np.sqrt(n)
    return x.mean(), x.mean() - h, x.mean() + h


def reading(d):
    m, lo, hi = ci(d, T975); _, l9, h9 = ci(d, T95)
    if lo > 0:
        return "NOSE LEADS"
    if hi < 0:
        return "SPEED LEADS"
    if -DELTA < l9 and h9 < DELTA:
        return "COMPARABLE"
    return "TIED, UNRESOLVED"


def parse(path):
    rows = {}
    head = None
    for ln in open(path):
        if ln.startswith("| host |"):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
        elif head and ln.startswith("| O1/"):
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            rows[c[0]] = {k: float(v) for k, v in zip(head[1:], c[1:])}
    return rows


G = sys.argv[1]
for cell in ("PW-G2.5", "PW-G10", "PW-G0"):
    R = parse(os.path.join(G, "steps", f"{cell}.txt"))
    hosts = sorted(R)
    print(f"\n## {cell}: {len(hosts)} signed hosts in the table")
    for w in (0, 1, 3):
        rs = np.array([R[h][f"r@w{w}"] for h in hosts])
        print(f"  realised r at w{w}: mean {rs.mean():.3f}, median {np.median(rs):.3f}, range {rs.min():.3f}..{rs.max():.3f}; "
              f"hosts dropped (r < {R_MIN}): {[(h.split('/final/')[0].split('/')[1] + '/' + h.split('/')[-1], round(R[h][f'r@w{w}'], 3)) for h in hosts if R[h][f'r@w{w}'] < R_MIN]}")
    for lab, hi, lo, w in (("first nose w0->0.4", "w0.4", "w0", 0), ("nose w1->1.4", "w1.4", "w1", 1), ("nose w3->3.4", "w3.4", "w3", 3)):
        nose = {h: R[h][hi] - R[h][lo] for h in hosts}
        raw = {h: R[h][f"speed@w{w}"] - R[h][f"w{w}"] for h in hosts}
        unit = {h: raw[h] * 0.25 / (R[h][f"r@w{w}"] - 1.0) for h in hosts if R[h][f"r@w{w}"] >= R_MIN}
        d_raw = [nose[h] - raw[h] for h in hosts]
        d_pu = [nose[h] - unit[h] for h in unit]
        m, l, u = ci(d_pu, T975); _, l9, h9 = ci(d_pu, T95)
        mr, lr, ur = ci(d_raw, T975)
        print(f"  {lab:20s} nose {ci(list(nose.values()), T975)[0]:+.3f} | per-unit speed {ci(list(unit.values()), T975)[0]:+.3f} | "
              f"nose - per-unit (n {len(d_pu)}): {m:+.3f} [{l:+.3f}, {u:+.3f}] 90% [{l9:+.3f}, {h9:+.3f}] -> {reading(d_pu)} | "
              f"nose - raw (n {len(d_raw)}): {mr:+.3f} [{lr:+.3f}, {ur:+.3f}] -> {reading(d_raw)} | "
              f"90% inside +-0.1: {'yes' if -DELTA < l9 and h9 < DELTA else 'no'} (half-width {(h9 - l9) / 2:.3f})")
    # leave-one-out on the registered line (G2.5 is the registered cell; printed for all)
    nose = {h: R[h]["w3.4"] - R[h]["w3"] for h in hosts}
    unit = {h: (R[h]["speed@w3"] - R[h]["w3"]) * 0.25 / (R[h]["r@w3"] - 1.0) for h in hosts if R[h]["r@w3"] >= R_MIN}
    d = {h: nose[h] - unit[h] for h in unit}
    loo = [ci([d[k] for k in d if k != h], T975)[1] for h in d]
    print(f"  w3 line, per-unit: leave-one-host-out lower bounds min {min(loo):+.3f}, max {max(loo):+.3f}; "
          f"largest per-host multiplier 0.25/(r-1) = {max(0.25 / (R[h]['r@w3'] - 1) for h in unit):.2f}")
