"""RBT-107 H1: the power of the scored IUT at the USABLE n (coordinator 08:45), printed beside an absent verdict.  Print-only;
nothing here is scored or changes a scored line.

    python runs/RBT-107/h1/h1_power.py > runs/RBT-107/h1/power.txt

(a) THE REGISTERED MODEL (iut_power.py, A2.8.3: its resampled J = 32 null rows, its MEASURED and CONSERVATIVE T + 800 targets,
    its scenarios), re-run at the usable n (19: seed 29's co-evolved fauna is extinct from season 27, so the common set is
    19) beside the planned n = 20.  EMPIRICAL resampling and GAUSS, 3000 replicates, iut_power.py's own stream (seed 1078).
(b) THE REALISED NULL: the per-seed cull20 - base contrast A_NB at T + 800 on the scored common set (the garden's own null,
    §8), its RMS per fauna, and the IUT power (Holm over DES and PAIR, both at the F2 sizes) and the IUT MDE (the smallest
    effect, in the F2 direction and proportions, supported on >= 80%) on a Gaussian model of that null at the usable n.
    Model (as iut_power.py): S = dS + e_S, B = e_B, N = dN + e_N, one arm's sd = null RMS / sqrt 2.
"""
import importlib.util
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


IP = _load("rbt107_iut_power", os.path.join(BASE, "iut_power.py"))
RO = _load("rbt107_readout_h1p", os.path.join(BASE, "readout.py"))
ST = IP.ST
REPS = 3000


def _yp(v, direction):
    return ST.yuen(list(direction * v))[3]


def _scored(v, direction):  # scored_p's band rule
    py = _yp(v, direction)
    return max(py, ST.wilcoxon(list(direction * v))[1]) if 0.04 < py <= 0.05 else py


def iut_rates(dS, dN, arm_sd, n, draw):
    """Rates of DES-IUT, PAIR-IUT and Holm-supported DES / PAIR over REPS replicates."""
    eS, eB, eN = draw(n, arm_sd), draw(n, arm_sd), draw(n, arm_sd)
    S, B, N = np.array(dS) + eS, eB, np.array(dN) + eN
    asb, asn = S - B, S - N
    out = {"DES-IUT": 0, "PAIR-IUT": 0, "Holm DES": 0, "Holm PAIR": 0}
    for r in range(REPS):
        pd = max(_scored(asb[r, :, 1], -1), _scored(asn[r, :, 1], -1))
        pp = max(_scored(asb[r, :, 0] - asb[r, :, 1], +1), _scored(asn[r, :, 0] - asn[r, :, 1], +1))
        out["DES-IUT"] += pd <= 0.05
        out["PAIR-IUT"] += pp <= 0.05
        h = ST.holm([pd, pp])
        out["Holm DES"] += h[0]
        out["Holm PAIR"] += h[1]
    return {k: v / REPS for k, v in out.items()}


def main():
    print(__doc__.split("\n\n")[0])
    print("\n== (a) the registered model (iut_power.py) at the usable n, beside the planned n")
    rng = np.random.default_rng(1078)
    base = IP.null_rows()
    bw = 0.9 * np.minimum(base.std(0, ddof=1), (np.percentile(base, 75, 0) - np.percentile(base, 25, 0)) / 1.34) * len(base) ** -0.2
    ms = (base ** 2).mean(0) + bw ** 2

    def empirical(n, arm_sd):
        x = base[rng.integers(0, len(base), size=(REPS, n))] * rng.choice([-1, 1], size=(REPS, n, 1))
        x = x + rng.normal(0, 1, size=x.shape) * bw
        return x * (arm_sd / np.sqrt(ms))

    def gauss(n, arm_sd):
        return rng.normal(0, 1, size=(REPS, n, 2)) * arm_sd

    for tname, tg in IP.TARGETS.items():
        arm_sd = np.array(tg["T+800"]) / math.sqrt(2)
        for sname in ("F2-NOT-TURNOVER", "C4NULL-SPLIT", "HALF-SIZE", "NULL"):
            dS, dN = IP.SCEN[sname]
            for n in (20, 19):
                for dname, draw in (("EMPIRICAL", empirical), ("GAUSS", gauss)):
                    r = iut_rates(dS, dN, arm_sd, n, draw)
                    print(f"  {tname:12s} T+800 n={n} {sname:16s} {dname:9s} " + "  ".join(f"{k} {v:.2f}" for k, v in r.items()))

    print("\n== (b) the realised T + 800 null on the scored common set, and the IUT power and MDE on it at the usable n")
    sm = RO.Sample("FRESH", RO.FRESH_SEEDS, True)
    d = RO.DSTAR
    seeds = [s for s in sm.seeds if all(s in RO.table(sm, k, d, key) for k in RO.KINDS for key in ("SB", "SN"))]
    n = len(seeds)
    if n < 6:
        print(f"  UNREAD (n = {n})")
        return
    rms = []
    for k in RO.KINDS:
        nb = RO.table(sm, k, d, "NB")
        v = [nb[s] for s in seeds]
        rms.append(math.sqrt(sum(x * x for x in v) / len(v)))
        print(f"  {k:12s} null A_NB (cull20 - base) at T+{d}: {RO.fmt(v)}; RMS {rms[-1]:.3f} (n {n})")
    arm_sd = np.array(rms) / math.sqrt(2)  # (holistic, conventional): iut_power's column order (co-evolved, designed)
    grng = np.random.default_rng(1079)

    def g2(n_, sd):
        return grng.normal(0, 1, size=(REPS, n_, 2)) * sd

    for sname in ("F2-NOT-TURNOVER", "HALF-SIZE", "NULL"):
        dS, dN = IP.SCEN[sname]
        r = iut_rates(dS, dN, arm_sd, n, g2)
        print(f"  REALISED-NULL GAUSS n={n} {sname:16s} " + "  ".join(f"{k} {v:.2f}" for k, v in r.items()))
    for half, key in (("DES", "Holm DES"), ("PAIR", "Holm PAIR")):
        mde = float("inf")
        for step in range(1, 41):
            f = step / 10  # multiples of F2's sizes: dS = f * (+0.05, -0.22)
            r = iut_rates((0.05 * f, -0.22 * f), (0.0, 0.0), arm_sd, n, g2)
            if r[key] >= 0.8:
                mde = f
                break
        print(f"  IUT MDE (80%, Holm) for H1-{half} at n={n} on the realised null: {mde:.1f} x RBT-101 F2's sizes "
              f"(designed A_SB {-0.22 * mde:+.3f}, paired P {0.27 * mde:+.3f})")


if __name__ == "__main__":
    main()
