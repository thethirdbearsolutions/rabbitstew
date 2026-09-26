"""RBT-104: the anatomy of RBT-91's 84 default-scale arrivals, regenerated from their lineage seeds.

For every arrival in `docs/artifacts/RBT-91-alone-baseline.txt`, rebuild the lineage (RBT-91's
generator via drift_reach.py, K = 1), find the predicate unit, and print its transfer function,
its bias, its four motif weights (u_L, u_R into it; v_L, v_R out of it), the linear gain
(u_L - u_R)(v_L + v_R)/2 and the links-alone response, which must equal the committed value.
The table says which barrier each arrival sits behind: the scale of its weights, its bias
(sech^2), or a transfer function with no small-signal response at any scale (sign, differentiate).
"""
import importlib.util
import os
from collections import Counter
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("dr", os.path.join(_HERE, "drift_reach.py"))
dr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dr)
sr, rbt78 = dr.sr, dr.rbt78

from rabbitstew.fixed import drive_effector_units  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402


def main():
    hits = dr.committed_hits()
    print("# RBT-104: the anatomy of RBT-91's default-scale arrivals (K = 1, regenerated)\n")
    print(f"{'pool':14s} {'lineage':>7s} {'func':>13s} {'bias':>6s} {'u_L':>6s} {'u_R':>6s} {'v_L':>6s} {'v_R':>6s} "
          f"{'linear a':>9s} {'links alone':>12s} {'committed':>10s}")
    funcs, match, lin = Counter(), 0, []
    zero_by_func = Counter()
    for label, i, _, alone_c, _ in hits:
        cfg, pool = rbt78._load(label)
        mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1, link_scale=1.0)
        ph = synthesize(dr._lineage(label, i, dr.DEPTH, 1.0, mcfg, pool), cfg.sim.synthesis)
        k = sr.motif_units(ph)[0]
        unit = ph.units[k].unit
        n_L, n_R = sr._wheel_noses(ph)
        le, re_ = drive_effector_units(ph)
        w = {}
        for s, d, x in ph.links:
            w[(s, d)] = w.get((s, d), 0.0) + x
        uL, uR, vL, vR = w[(n_L, k)], w[(n_R, k)], w[(k, le[0])], w[(k, re_[0])]
        a_lin = (uL - uR) * (vL + vR) / 2
        alone = sr.links_alone_a(ph, k)
        match += f"{alone:+.4f}" == alone_c
        funcs[unit.func] += 1
        lin.append(abs(a_lin))
        if abs(alone) < 1e-4:
            zero_by_func[unit.func] += 1
        print(f"{label:14s} {i:7d} {unit.func:>13s} {unit.bias:+6.2f} {uL:+6.2f} {uR:+6.2f} {vL:+6.2f} {vR:+6.2f} "
              f"{a_lin:+9.2f} {alone:+12.4f} {alone_c:>10s}")
    print(f"\nlinks-alone values matching the committed file: {match} of {len(hits)}")
    print(f"transfer functions: {dict(funcs)}")
    print(f"arrivals whose links-alone response is below 1e-4, by function: {dict(zero_by_func)}")
    lin = np.array(lin)
    print(f"|linear a|: median {np.median(lin):.2f}, max {lin.max():.2f}; the rung that pays in RBT-90's world is a = 64")


if __name__ == "__main__":
    main()
