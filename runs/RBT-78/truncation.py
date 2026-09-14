"""RBT-78 follow-up: does the depth-4 truncation decide the path-route arrival rate?

Raised by RBT-67's §2 and routed here by the coordinator. RBT-78 concluded that the path-route
quantity is "a permissive upper bound on network gain rather than a compass arrival rate". This
tests something stronger: whether it is a bound on anything. If the recurrent core's spectral
radius exceeds 1 the series has no limit, and the depth-4 value is an artifact of the
truncation rather than a ceiling on it.

Reports, over the same drift lineages RBT-78 used, the fraction whose |a| moves by more than
20% between depth 4 and depth 8, and how many lineages clear the |a| >= 16 threshold at one
depth but not the other. No simulation. Usage: truncation.py
"""
import sys, zlib, numpy as np
from dataclasses import replace
sys.path.insert(0, "runs/RBT-78")
from reconcile import _load, MASTER_SEED, _nose_eff, DEPTH
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize

def a_at(ph, depth):
    nose, eff = _nose_eff(ph)
    if len(nose) != 2 or len(eff) != 2: return None
    n = len(ph.units); M = np.zeros((n, n))
    for s, d, w in ph.links: M[d, s] += w
    s_ = {}
    for part, si in nose.items():
        v = np.zeros(n); v[si] = 1.0; tot = np.zeros(n)
        for _ in range(depth):
            v = M @ v; tot += v
            if not v.any(): break
        s_[part] = tot[eff[1]] + tot[eff[2]]
    return (s_[1] - s_[2]) / 2.0

N = 2000
for label in ("W4b-801-bests", "P-801-final60"):
    cfg, pool = _load(label)
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    a4, a8, a12 = [], [], []
    for i in range(N):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(label.encode()), 19, i]))
        g = pool[i % len(pool)]
        for _ in range(19): g = mutate_controller(g, rng, mcfg)
        ph = synthesize(g, cfg.sim.synthesis)
        v4, v8, v12 = a_at(ph, 4), a_at(ph, 8), a_at(ph, 12)
        if v4 is None: continue
        a4.append(v4); a8.append(v8); a12.append(v12)
    a4, a8, a12 = np.array(a4), np.array(a8), np.array(a12)
    clear = np.abs(a4) >= 16
    # "unstable" = the truncation is doing the work: |a| moves by >20% from depth 4 to depth 8
    unstable = np.abs(np.abs(a8) - np.abs(a4)) > 0.2 * np.maximum(np.abs(a4), 1e-9)
    print(f"\n=== {label}, {len(a4)} lineages ===")
    print(f"  all lineages          : {100*unstable.mean():5.1f}% move >20% between depth 4 and 8")
    print(f"  lineages clearing |a4|>=16 ({clear.sum()}): {100*unstable[clear].mean():5.1f}% move >20%")
    if clear.any():
        print(f"    median |a| at depth 4 / 8 / 12 among them: "
              f"{np.median(np.abs(a4[clear])):.1f} / {np.median(np.abs(a8[clear])):.1f} / {np.median(np.abs(a12[clear])):.1f}")
        print(f"    max    |a| at depth 4 / 8 / 12 among them: "
              f"{np.abs(a4[clear]).max():.1f} / {np.abs(a8[clear]).max():.3g} / {np.abs(a12[clear]).max():.3g}")
    # how many would clear at depth 8 but not depth 4, and vice versa
    c8 = np.abs(a8) >= 16
    print(f"  clears at d=4 but not d=8: {int((clear & ~c8).sum())}   clears at d=8 but not d=4: {int((~clear & c8).sum())}")
