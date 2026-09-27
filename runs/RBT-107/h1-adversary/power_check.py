"""RBT-107 H1 adversary: does "argues against an F2-sized effect" survive the observed data?  Print only; scores nothing.

    RBT107_GARDEN=<#376 checkout>/runs/RBT-107/garden/readout python runs/RBT-107/h1-adversary/power_check.py

(1) The scored components' observed spread on the common set (n = 19) beside the spread h1_power.py's realised-null model
    implies (one contrast: RMS of A_NB; paired: sqrt(RMS_co^2 + RMS_de^2)).
(2) Compatibility: for each scored component, the registered one-sided Yuen p of "the effect is at least F2's size"
    (DES components shifted by +0.22 and tested < 0; PAIR components shifted by -0.27 and tested > 0).  A p above 0.05 means
    the data do not reject an F2-sized effect on that component.
(3) The IUT's power at F2's sizes by a residual bootstrap of the observed seeds: the four components per seed, centred,
    shifted to F2's sizes, seeds resampled with replacement at n = 19; the registered Yuen, the IUT, Holm over DES and PAIR.
    It keeps the observed joint spread (including the two faunas' correlation), which the Gaussian model does not.
"""
import importlib.util
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


RO = _load("rbt107_readout_adv", os.path.join(BASE, "readout.py"))
ST = RO.ST


def yp(v, direction):
    return ST.yuen([direction * x for x in v])[3]


def main():
    sm = RO.Sample("FRESH", RO.FRESH_SEEDS, True)
    d = RO.DSTAR
    seeds = [s for s in sm.seeds if all(s in RO.table(sm, k, d, key) for k in RO.KINDS for key in ("SB", "SN"))]
    n = len(seeds)
    dsb, dsn = RO.table(sm, "conventional", d, "SB"), RO.table(sm, "conventional", d, "SN")
    pb, pn = RO.paired(sm, d, "SB"), RO.paired(sm, d, "SN")
    comp = {"DES A_SB": [dsb[s] for s in seeds], "DES A_SN": [dsn[s] for s in seeds],
            "PAIR P": [pb[s] for s in seeds], "PAIR P_N": [pn[s] for s in seeds]}
    rms = {k: math.sqrt(statistics.fmean(RO.table(sm, k, d, "NB")[s] ** 2 for s in seeds)) for k in RO.KINDS}
    model = {"DES A_SB": rms["conventional"], "DES A_SN": rms["conventional"],
             "PAIR P": math.hypot(rms["holistic"], rms["conventional"]), "PAIR P_N": math.hypot(rms["holistic"], rms["conventional"])}
    print(f"== (1) spread on the common set, n = {n}: observed sd against the realised-null model's")
    for k, v in comp.items():
        print(f"  {k:9s} observed sd {statistics.stdev(v):.3f}; model sd {model[k]:.3f}; ratio {statistics.stdev(v) / model[k]:.2f}")
    co = RO.table(sm, "holistic", d, "SB")
    print(f"  correlation of the faunas' A_SB across seeds: {statistics.correlation([co[s] for s in seeds], comp['DES A_SB']):+.2f}")

    print("\n== (2) is an F2-sized effect rejected on each component? (registered Yuen, one-sided, against F2's size)")
    f2 = {"DES A_SB": -0.22, "DES A_SN": -0.22, "PAIR P": 0.27, "PAIR P_N": 0.27}
    for k, v in comp.items():
        direction = +1 if k.startswith("DES") else -1  # H0: effect at F2 size; alternative: weaker than F2
        p = yp([x - f2[k] for x in v], direction)
        m, hw, _, _ = RO.ci(v)
        print(f"  {k:9s} F2 {f2[k]:+.2f}; mean {m:+.3f} [{m - hw:+.3f}, {m + hw:+.3f}]; F2 inside the t interval: "
              f"{'yes' if m - hw <= f2[k] <= m + hw else 'no'}; p(weaker than F2) {p:.4f}")

    print("\n== (3) the IUT at F2's sizes by residual bootstrap of the observed seeds (n = 19, 2000 replicates, seed 1107)")
    cen = {k: [x - statistics.fmean(v) for x in v] for k, v in comp.items()}
    for label, scale in (("F2 sizes", 1.0), ("half F2", 0.5), ("null", 0.0)):
        rng = random.Random(1107)
        hit = {"Holm DES": 0, "Holm PAIR": 0}
        for _ in range(2000):
            idx = [rng.randrange(n) for _ in range(n)]
            g = {k: [cen[k][i] + scale * f2[k] for i in idx] for k in cen}
            pd = max(yp(g["DES A_SB"], -1), yp(g["DES A_SN"], -1))
            pp = max(yp(g["PAIR P"], +1), yp(g["PAIR P_N"], +1))
            h = ST.holm([pd, pp])
            hit["Holm DES"] += h[0]
            hit["Holm PAIR"] += h[1]
        print(f"  {label:9s} " + "  ".join(f"{k} {v / 2000:.2f}" for k, v in hit.items()))
    print("  (h1_power.py's realised-null Gaussian model at F2 sizes: Holm DES 0.83, Holm PAIR 0.72; half: 0.22, 0.16)")


if __name__ == "__main__":
    main()
