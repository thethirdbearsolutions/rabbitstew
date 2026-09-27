"""RBT-106 P1 readout adversary: P-NULL's matched-null power at the USABLE n = 7 (the readout quotes n = 10).

The model is the design adversary's `factorial_b` (adversary/power_adv.py, the §10.5 / F8 "measured bare-line"
model that P1-READOUT.md quotes), ported line for line with one change: the t quantile comes from
recompute.t_ppf instead of scipy (not a declared dependency).  The draws, the rules and the carriers' model are
unchanged, and the port is checked by reproducing power_adv.txt part B's n = 10 figures exactly.

Usage: python runs/RBT-106/p1-adversary/power_n7.py
"""
import importlib.util
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R106 = os.path.dirname(HERE)


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


rc = _load("p1adv_recompute", os.path.join(HERE, "recompute.py"))
# power.py's module level imports RBT-104's adversary power.py (numpy only); scipy is imported inside factorial() only
pw = _load("rbt106_power", os.path.join(R106, "power.py"))


def factorial_b(q, n=10, sims=40000, seed=106, bare_mean=0.10, bare_sd=0.20, fd_bare=0.10):
    rng = np.random.default_rng(seed)
    cells = ("S1", "P1", "S8", "P8")
    carry = {c: rng.random((sims, n)) < q[c] for c in cells}
    F = {c: np.where(carry[c], pw.P_CARRY * rng.choice(pw.PATCHY_F, (sims, n)) + (1 - pw.P_CARRY) * rng.normal(bare_mean, bare_sd, (sims, n)),
                     rng.normal(bare_mean, bare_sd, (sims, n))) for c in cells}
    fd = {c: (rng.random((sims, n)) < np.where(carry[c], pw.FD_CARRY, fd_bare)).sum(1) for c in cells}
    tq = rc.t_ppf(0.975, n - 1)
    lo = lambda x: x.mean(1) - tq * x.std(1, ddof=1) / np.sqrt(n)
    p1_lo = lo(F["P1"] - F["S1"])
    prize_ok = (fd["P1"] >= 3) & (p1_lo > 0)
    return dict(P_EVOLVED=float(prize_ok.mean()), P_NULL=float(((fd["P1"] <= 1) & ~(p1_lo > 0)).mean()),
                NOT_DECIDED=float(1 - prize_ok.mean() - ((fd["P1"] <= 1) & ~(p1_lo > 0)).mean()))


SCEN = (("nothing holds", (0, 0, 0, 0)), ("the prize alone suffices (q = 0.5)", (0, 0.5, 0, 0.5)),
        ("the prize suffices, weakly (q = 0.25)", (0, 0.25, 0, 0.25)), ("both needed", (0, 0, 0, 0.5)))
MODELS = (("designer's first model: bare N(+0.10, 0.20), FD 0.10", dict()),
          ("measured patchy bare lines (F8, §10.5): N(-0.056, 0.145), FD 0.05", dict(bare_mean=-0.056, bare_sd=0.145, fd_bare=0.05)))


def main():
    print("# RBT-106 P1 readout adversary: P-NULL's power at the usable n = 7\n")
    print("## Port check: power_adv.txt part B (n = 10) reproduced\n")
    ref = {"nothing holds": (0.000, 0.892), "the prize alone suffices (q = 0.5)": (0.574, 0.067),
           "the prize suffices, weakly (q = 0.25)": (0.115, 0.373), "both needed": (0.000, 0.892)}
    ok = True
    for name, q in SCEN:
        r = factorial_b(dict(zip(("S1", "P1", "S8", "P8"), q)), n=10, bare_mean=-0.056, bare_sd=0.145, fd_bare=0.05)
        same = (round(r["P_EVOLVED"], 3), round(r["P_NULL"], 3)) == ref[name]
        ok &= same
        print(f"  {name}: P-EVOLVED {r['P_EVOLVED']:.3f}, P-NULL {r['P_NULL']:.3f}  (power_adv.txt: {ref[name][0]:.3f}, {ref[name][1]:.3f}) {'same' if same else 'DIFFERENT'}")
    print(f"  port check: {'PASSED' if ok else 'FAILED'}\n")
    print("## P(P-NULL) and P(P-EVOLVED), n = 10 (as quoted) against n = 7 (the usable pairs)\n")
    print("| model | truth (q S1, P1, S8, P8) | n = 10: P-NULL / P-EVOLVED | n = 7: P-NULL / P-EVOLVED / NOT DECIDED |")
    print("|---|---|---|---|")
    for mname, kw in MODELS:
        for name, q in SCEN:
            qd = dict(zip(("S1", "P1", "S8", "P8"), q))
            a, b = factorial_b(qd, n=10, **kw), factorial_b(qd, n=7, **kw)
            print(f"| {mname} | {name}: {', '.join(f'{x:g}' for x in q)} | {a['P_NULL']:.3f} / {a['P_EVOLVED']:.3f} | "
                  f"{b['P_NULL']:.3f} / {b['P_EVOLVED']:.3f} / {b['NOT_DECIDED']:.3f} |")
    print("\nP(P-NULL | the prize suffices) is the probability that P-NULL MISSES that hypothesis (the matched-null figure the "
          "programme rule asks for).  Both models' EVOLVED rows are upper bounds under the F6 attribution rule (§10.4).")
    print("\n## P-NULL's miss rate against \"the prize suffices\" (q S1 = S8 = 0, P1 = P8 = q) across q (measured bare-line model)\n")
    for n in (10, 7):
        cells = []
        for q in (0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
            r = factorial_b(dict(S1=0, P1=q, S8=0, P8=q), n=n, bare_mean=-0.056, bare_sd=0.145, fd_bare=0.05)
            cells.append(f"q {q:.2f}: {r['P_NULL']:.3f}")
        print(f"  n = {n}: " + "; ".join(cells))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
