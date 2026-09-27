"""R2-CHECK probe: is the retention layer (r2 §6.4) bounded by the saturated band, and is R_drift a fair floor?

Replica in RBT-126 retention.txt's form (the design's demography, power.py: threshold 3, cost 1, age 60, initial 3,
gain Poisson(g) - 0.1 - 0.25): one fauna, 60 founders all carriers at gross gc; each birth to a carrier parent gives
a non-carrier with probability u = 0.06 (erosion, RBT-80's number as RBT-126 uses it); a non-carrier earns gc - Delta.
Carriage at season 300.

Arms:
  R_sel      the point's economy, committed shuffle
  R_drift    r2's floor: `--neutral` + `--breed-gate none` (no starvation, no living cost, threshold and cost 0, every
             living member a breeder; deaths by age only)
  R_marker   the proposed floor: the same economy as R_sel, with a planted trait of no value (Delta = 0); same turnover
h = carriage(R_sel) - carriage(floor).  HOLDS needs h BH-significant > 0 and mean h >= 0.10; NOT HELD needs TOST
+-0.10 or mean h < 0 significant (r2 §6.4).  Printed at n 8, alpha q/2.

python3 probe_retention.py [reps]
"""
import math
import sys

import numpy as np

import adv_replica as A

P = A.P
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rng = np.random.default_rng(12911)
U = 0.06


def run(gc, delta, neutral=False, horizon=300, cap=60):
    # member: [carrier, energy, age, births_counter]
    pop = [[1, P.INIT, int(rng.integers(0, P.AGE))] for _ in range(cap)]
    births = 0
    for s in range(horizon):
        for p in pop:
            g = gc if p[0] else gc - delta
            p[1] += rng.poisson(max(g, 0.0)) - P.WORK - (0.0 if neutral else P.COST)
            p[2] += 1
        if neutral:
            pop = [p for p in pop if p[2] < P.AGE]
            parents = list(pop)
            while len(pop) < cap and parents:
                par = parents[int(rng.integers(0, len(parents)))]
                c = par[0] if rng.random() > U else 0
                pop.append([c, 0.0, 0])
                births += 1
        else:
            pop = [p for p in pop if p[1] > 0 and p[2] < P.AGE]
            elig = [p for p in pop if p[1] >= P.THR]
            rng.shuffle(elig)
            for par in elig:
                if len(pop) >= cap:
                    break
                par[1] -= P.BCOST
                c = par[0] if rng.random() > U else 0
                pop.append([c, P.BCOST, 0])
                births += 1
        if not pop:
            return float("nan"), births
    return (sum(p[0] for p in pop) / len(pop)), births


def calls(h, n=8, alpha=A.Q / 2, B=4000, r=np.random.default_rng(5)):
    h = h[~np.isnan(h)]
    x = h[r.integers(0, len(h), size=(B, n))]
    m, se = x.mean(1), x.std(1, ddof=1) / math.sqrt(n) + 1e-12
    t = m / se
    c1, c2 = A.t_crit(alpha, n - 1), A.t_crit(2 * alpha, n - 1)
    holds = np.mean((t > c1) & (m >= 0.10))
    notheld = np.mean(((m - c2 * se > -0.10) & (m + c2 * se < 0.10)) | (t < -c1))
    return holds, notheld


print(f"# probe_retention: {reps} replica seeds per arm; u {U}; carriage at season 300; calls at n 8, q/2")
print("# gc = carrier gross income (the regime); Delta = the trait's value (carrier - non-carrier)")
print("# cols: gc Delta | carriage sel / drift / marker | births per season sel / drift | HOLDS, NOT HELD vs drift | vs marker")
marker = {}
for gc in (0.6, 0.9, 1.3):
    mk = np.array([run(gc, 0.0)[0] for _ in range(reps)])
    marker[gc] = mk
    dr = [run(gc, 0.0, neutral=True) for _ in range(reps)]
    drc = np.array([d[0] for d in dr]); drb = np.mean([d[1] for d in dr]) / 300
    for delta in (0.0, 0.1, 0.2, 0.4):
        sr = [run(gc, delta) for _ in range(reps)]
        sc = np.array([s[0] for s in sr]); sb = np.mean([s[1] for s in sr]) / 300
        hd = sc - drc[rng.permutation(reps)]
        hm = sc - mk[rng.permutation(reps)]
        a, b = calls(hd)
        c, d = calls(hm)
        print(f"  gc {gc:.1f} Delta {delta:.2f} | {np.nanmean(sc):.3f} / {np.nanmean(drc):.3f} / {np.nanmean(mk):.3f} | "
              f"{sb:.2f} / {drb:.2f} | vs drift: HOLDS {a:.2f} NOT-HELD {b:.2f} | vs marker: HOLDS {c:.2f} NOT-HELD {d:.2f}",
              flush=True)
