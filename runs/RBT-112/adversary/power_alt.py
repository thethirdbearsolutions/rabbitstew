"""RBT-112 design adversary: the design's own power model (runs/RBT-112/power.py, imported unchanged, rho = 0.10 as
fitted), re-read for (a) the registered SUPPORTED count, (b) the alternative "#HELD(HZ) - #HELD(HU) >= 3" (RBT-106's own
SUPPORTED count form, which the registered rule tightens with "#HELD(HZ) >= 5"), and (c) twenty HZ seeds (the ten
seeds' q twice: ten more HZ arms on the same founders at a new ecology seed), at thresholds whose null is below 1e-3.
Joint over #HELD(HU) (ten seeds, the default operator) and #HELD(HZ), conditioned on the gate #HELD(HU) <= 2.
Usage: power_alt.py (run from the design checkout's root)"""
import importlib.util, math, sys
import numpy as np
spec = importlib.util.spec_from_file_location("p112", "runs/RBT-112/power.py"); P = importlib.util.module_from_spec(spec)
sys.modules["p112"] = P; spec.loader.exec_module(P)
RHO = 0.10
def null(n, k, q0): return sum(math.comb(n, j) * q0 ** j * (1 - q0) ** (n - j) for j in range(k, n + 1))
print("# the count nulls at the per-seed false-positive rate q0 (measured 3/200 = 1.5%, exact upper 95% 4.3%)")
for q0 in (0.015, 0.043):
    print(f"  q0 {q0}: P(>=5 of 10) {null(10, 5, q0):.1e}; P(>=3 of 10) {null(10, 3, q0):.1e}; P(>=6 of 20) {null(20, 6, q0):.1e}; P(>=5 of 20) {null(20, 5, q0):.1e}")
for name, G in (("GENEALOGY (part 2's n)", P.genealogy()), ("n = 40", P.genealogy(40)), ("n = 25", P.genealogy(25))):
    print(f"\n## scenario {name}; rho {RHO}\n")
    print("| s | q_Z mean | P(#HU<=2) | registered: SUPPORTED given gate | alt (#HZ-#HU>=3) given gate | FALSIFIED given gate | 20 HZ seeds: #HZ>=6 (and #HZ>=HU*2+3) given gate | 20 HZ: FALSIFIED (#HZ<=2) given gate |")
    print("|---|---|---|---|---|---|---|---|")
    for s in (0.0, 0.089, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5):
        qu = [P.q_seed(sd, s, "default", RHO, G) for sd in P.SEEDS]
        qz = [P.q_seed(sd, s, "S0", RHO, G) for sd in P.SEEDS]
        du, dz, dz20 = P.poibin(qu), P.poibin(qz), P.poibin(qz + qz)
        g = du[:3].sum()
        reg = sum(du[h] * dz[max(5, h + 3):].sum() for h in range(3)) / g
        alt = sum(du[h] * dz[h + 3:].sum() for h in range(3)) / g
        fal = dz[:2].sum()
        s20 = sum(du[h] * dz20[max(6, 2 * h + 3):].sum() for h in range(3)) / g
        f20 = dz20[:3].sum()
        print(f"| {s:.3f} | {np.mean(qz):.3f} | {g:.2f} | {reg:.3f} | {alt:.3f} | {fal:.3f} | {s20:.3f} | {f20:.3f} |")
