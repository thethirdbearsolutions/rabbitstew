"""RBT-104: why the links-alone response of drift's arrivals does not scale as K^2.

For each of RBT-91's 84 arrivals, at K = 1 and K = 8 (the parents' links and the operator's link
draws scaled, as drift_reach.py does), print the predicate unit's function and bias, the output
weights v_L, v_R, the resting drive the unit puts on each Effector (v * f(b), f the unit's
transfer function at its bias), each Effector's own bias, and the links-alone response.  The
hypothesis under test: the output link carries the unit's resting output as well as the signal,
so scaling v while the bias is unscaled pushes the Effector into saturation and the small-signal
gain collapses.
"""
import importlib.util
import os
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("dr", os.path.join(_HERE, "drift_reach.py"))
dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dr)
sr, rbt78 = dr.sr, dr.rbt78

from rabbitstew.fixed import drive_effector_units  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402


def one(label, i, K):
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1, link_scale=K)
    ph = synthesize(dr._lineage(label, i, dr.DEPTH, K, mcfg, pool), cfg.sim.synthesis)
    units = sr.motif_units(ph)
    if not units:
        return None
    k = units[0]
    u = ph.units[k].unit
    le, re_ = drive_effector_units(ph)
    w = {}
    for s, d, x in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + x
    vL, vR = w[(k, le[0])], w[(k, re_[0])]
    rest = float(np.tanh(u.bias)) if u.func == "tanh" else float("nan")
    eb = (ph.units[le[0]].unit.bias, ph.units[re_[0]].unit.bias)
    return dict(func=u.func, bias=u.bias, vL=vL, vR=vR, rest=rest, eb=eb, alone=abs(sr.links_alone_a(ph, k)))


def main():
    print("# RBT-104: the arrivals' links-alone response at K = 1 and K = 8, and the Effector's resting drive\n")
    print(f"{'pool':6s} {'lineage':>7s} {'func':>13s} {'bias':>6s} | {'K=1 alone':>9s} {'K=8 alone':>9s} {'ratio':>7s} | "
          f"{'K=8 v_L':>8s} {'v_R':>7s} {'|v f(b)| max':>12s} {'eff. biases':>14s}")
    rows = []
    for label, i, _, _, _ in dr.committed_hits():
        a1, a8 = one(label, i, 1.0), one(label, i, 8.0)
        if a1 is None or a8 is None:
            print(f"{label[:6]:6s} {i:7d}  structure absent at one of the two scales")
            continue
        ratio = a8["alone"] / a1["alone"] if a1["alone"] > 1e-4 else float("nan")
        drive = max(abs(a8["vL"] * a8["rest"]), abs(a8["vR"] * a8["rest"]))
        rows.append((a1["func"], a1["alone"], a8["alone"], ratio, drive))
        print(f"{label[:6]:6s} {i:7d} {a1['func']:>13s} {a1['bias']:+6.2f} | {a1['alone']:9.4f} {a8['alone']:9.4f} {ratio:7.1f} | "
              f"{a8['vL']:+8.2f} {a8['vR']:+7.2f} {drive:12.2f} {a8['eb'][0]:+6.2f},{a8['eb'][1]:+6.2f}")
    t = [r for r in rows if r[0] == "tanh" and r[1] > 1e-4]
    lo = [r[3] for r in t if r[4] < 1.0]
    hi = [r[3] for r in t if r[4] >= 1.0]
    print(f"\ntanh arrivals that respond at K = 1: {len(t)}; the ratio K=8/K=1 would be 64 if the response scaled as K^2")
    print(f"  resting drive |v f(b)| < 1 at K = 8: n = {len(lo)}, median ratio {np.median(lo) if lo else float('nan'):.1f}")
    print(f"  resting drive |v f(b)| >= 1 at K = 8: n = {len(hi)}, median ratio {np.median(hi) if hi else float('nan'):.1f}")


if __name__ == "__main__":
    main()
