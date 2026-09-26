"""RBT-107 A2.8: the power of the intersection-union (IUT) scoring, at n = 20, before any arm.

    python runs/RBT-107/iut_power.py > runs/RBT-107/iut_power.txt

The IUT (coordinator 22:45, A2.8): a hypothesis is SUPPORTED only if BOTH its forms pass a one-sided Yuen 20% test at 0.05:
    DES   designed A_SB < 0  AND  designed A_SN < 0
    PAIR  P = A_SB^co - A_SB^des > 0  AND  P_N = A_SN^co - A_SN^des > 0
its p is the larger of the two; Holm is taken over DES and PAIR (the IUT p's).

MODEL.  Each seed has three arms per fauna; each arm's garden mean is an effect plus an arm deviation e_arm:
    S = dS + e_S,  B = e_B,  N = dN + e_N         so  A_SB = dS + e_S - e_B,  A_SN = dS - dN + e_S - e_N
The shared e_S makes A_SB and A_SN correlated (0.5), as in the ecology.  Arm deviations are drawn by resampling the ten
committed null rows A_NB = N - B at J = 32 (garden/j32/, co-evolved and designed kept together, so their correlation is
kept), divided by sqrt(2) (one arm's share), one random sign per draw, smoothed (Silverman), then scaled so one arm's
variance is half the target null's (design_power_j32.txt: the MEASURED and the CONSERVATIVE targets; at T + 110 the drift
part scaled 110/800).  GAUSS: the same variances, normal.  3000 replicates per cell, fixed stream.
Scenarios (effects in income per robot-bout; co-evolved, designed):
    F2-NOT-TURNOVER   dS = (+0.05, -0.22), dN = (0, 0)          RBT-101 F2's sizes, none of it turnover
    C4NULL-SPLIT      dS = (+0.05, -0.22), dN = (+0.18, -0.02)  RBT-110's C4null: paired +0.27 against base, +0.07 net;
                                                                designed -0.22 against base, -0.20 net
    HALF-SIZE         dS = (+0.025, -0.11), dN = (0, 0)
    NULL              all 0 (the size of each scored rule)
"""
import glob
import importlib.util
import math
import os
import re
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("stats107", os.path.join(HERE, "stats107.py"))
ST = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ST)
J32 = os.path.join(HERE, "garden", "j32")
OLD = [801, 804, 805, 806, 807, 1, 2, 3, 4, 7]
REPS = 3000
TARGETS = {  # one-contrast null RMS (co-evolved, designed) from design_power_j32.txt
    "MEASURED": {"T+800": (0.154, 0.256), "T+110": (0.087, 0.131)},
    "CONSERVATIVE": {"T+800": (0.495, 0.256), "T+110": (0.195, 0.131)},
}
SCEN = {
    "F2-NOT-TURNOVER": ((0.05, -0.22), (0.0, 0.0)),
    "C4NULL-SPLIT": ((0.05, -0.22), (0.18, -0.02)),
    "HALF-SIZE": ((0.025, -0.11), (0.0, 0.0)),
    "NULL": ((0.0, 0.0), (0.0, 0.0)),
}


def G(path):
    r = [l.rstrip("\n").split("\t") for l in open(path) if l.strip() and not l.startswith("#")]
    return statistics.fmean(float(x[5]) for x in r)


def null_rows():
    rows = []
    for s in OLD:
        rows.append([G(os.path.join(J32, f"cull20-{s}-{k}-s599.txt")) - G(os.path.join(J32, f"base-{s}-{k}-s599.txt"))
                     for k in ("holistic", "conventional")])
    return np.array(rows) / math.sqrt(2)  # one arm's share of a contrast


def main():
    print(__doc__.split("\n\n")[0])
    rng = np.random.default_rng(1078)
    base = null_rows()
    bw = 0.9 * np.minimum(base.std(0, ddof=1), (np.percentile(base, 75, 0) - np.percentile(base, 25, 0)) / 1.34) * len(base) ** -0.2
    ms = (base ** 2).mean(0) + bw ** 2

    def arms(n, arm_sd, gauss):
        """(REPS, n, 2) deviations for one arm, per fauna scaled to arm_sd."""
        if gauss:
            return rng.normal(0, 1, size=(REPS, n, 2)) * arm_sd
        x = base[rng.integers(0, len(base), size=(REPS, n))] * rng.choice([-1, 1], size=(REPS, n, 1))
        x = x + rng.normal(0, 1, size=x.shape) * bw
        return x * (arm_sd / np.sqrt(ms))

    def yp(v, direction):
        return ST.yuen(list(direction * v))[3]

    for tname, tg in TARGETS.items():
        for when in ("T+110", "T+800"):
            rms = np.array(tg[when])
            arm_sd = rms / math.sqrt(2)
            for sname, (dS, dN) in SCEN.items():
                for n in (20,):
                    for gauss in (False, True):
                        eS, eB, eN = arms(n, arm_sd, gauss), arms(n, arm_sd, gauss), arms(n, arm_sd, gauss)
                        S, B, N = np.array(dS) + eS, eB, np.array(dN) + eN
                        asb, asn = S - B, S - N
                        des_b, des_n = asb[:, :, 1], asn[:, :, 1]
                        p_b, p_n = asb[:, :, 0] - asb[:, :, 1], asn[:, :, 0] - asn[:, :, 1]
                        res = {"DES-base": 0, "DES-net": 0, "DES-IUT": 0, "PAIR-base": 0, "PAIR-net": 0, "PAIR-IUT": 0,
                               "Holm DES": 0, "Holm PAIR": 0}
                        for r in range(REPS):
                            a, b = yp(des_b[r], -1), yp(des_n[r], -1)
                            c, d = yp(p_b[r], +1), yp(p_n[r], +1)
                            res["DES-base"] += a <= 0.05
                            res["DES-net"] += b <= 0.05
                            res["PAIR-base"] += c <= 0.05
                            res["PAIR-net"] += d <= 0.05
                            pd, pp = max(a, b), max(c, d)
                            res["DES-IUT"] += pd <= 0.05
                            res["PAIR-IUT"] += pp <= 0.05
                            h = ST.holm([pd, pp])
                            res["Holm DES"] += h[0]
                            res["Holm PAIR"] += h[1]
                        print(f"{tname:12s} {when} n={n} {sname:16s} {'GAUSS' if gauss else 'EMPIRICAL':9s} "
                              + "  ".join(f"{k} {v / REPS:.2f}" for k, v in res.items()))


if __name__ == "__main__":
    main()
