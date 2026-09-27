"""RBT-113 power, null and positive control (PREREGISTRATION.md §5), by simulation through the readout's own
statistics (`readout.arm_stats`, `t_ci`, `sign_flip_p`), at the planned design.

The model is an individual-based quantitative-genetic caricature of one arm:
  * N founders with breeding values g ~ N(0, h2) and phenotype z = g + w_t + e, e ~ N(0, 1 - h2), so the founders'
    phenotypic SD is 1 (= sigma0) and h2 is the planted heritability of the trait as measured (D draws folded in);
  * w_t, a world effect shared by every individual of every line in generation t (the arm's shared draws), SD 0.3;
  * truncation of k = round(P N) on z, up / down / uniform (control), parents drawn uniformly from the pool, a
    partner with probability 0.5 (the child's g is the parents' mean plus segregation N(0, V_A/2)), plus mutation
    N(bias, V_m) with a mutational bias of -0.02 sigma0 per generation on every line.  V_m = 0 in every row but
    the last of each scenario: mutational input is itself heritable variance, so the NULL is h2 = 0 AND V_m = 0
    (nothing heritable at all; the lines differ only by drift, noise and the shared bias), and the positives are
    conservative (the founders' variance is all selection has, and drift and the Bulmer effect erode it);
  * `floor` scenario: the recorded trait is max(z, q) with q the founders' 40th percentile, a crude stand-in for
    the holistic founders' mass of non-foragers at zero yield (pilot.txt), which blunts the down line (on the
    holistic founders the zeros sit above the flailers and cap the up line instead; for the power of b_div, which
    side is censored is immaterial).
The same `arm_stats` the readout applies to lineage.jsonl is applied to these series, and the readout's verdict
rule (RESPONDS iff the t CI on b_div excludes 0 and the sign-flip p < 0.05) is applied to n units.

Usage: power.py [SIMS] > power.txt
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import readout as ro  # noqa: E402
import world  # noqa: E402

N, P, G = world.POP, world.TRUNC, world.GENERATIONS
K = max(1, int(round(P * N)))
V_M, BIAS, SD_W = 0.01, -0.02, 0.3


def sim_arm(h2, rng, floor=False, n=N, G=G, k=K, vm=0.0):
    g0 = rng.normal(0, np.sqrt(h2), n) if h2 > 0 else np.zeros(n)
    e_sd = np.sqrt(1 - h2)
    w = rng.normal(0, SD_W, G)
    q = None
    ser = {}
    e0 = rng.normal(0, e_sd, n)  # the founders' generation-0 phenotypes are shared by the three lines
    for L in ro.LINES:
        g = g0.copy()
        m, S = [], []
        for t in range(G):
            z = g + w[t] + (e0 if t == 0 else rng.normal(0, e_sd, n))
            if floor:
                if q is None:
                    q = np.percentile(z, 40)
                z = np.maximum(z, q)
            m.append(z.mean())
            if t == G - 1:
                break
            order = np.argsort(-z, kind="stable")
            pool = order[:k] if L == "U" else order[::-1][:k] if L == "D" else rng.choice(n, k, replace=False)
            a = pool[rng.integers(0, k, n)]
            b = np.where(rng.random(n) < 0.5, pool[rng.integers(0, k, n)], a)
            S.append(float(np.mean((z[a] + z[b]) / 2) - m[-1]))
            va = float(np.var(g))
            g = (g[a] + g[b]) / 2 + np.where(a != b, rng.normal(0, np.sqrt(va / 2), n), 0) + rng.normal(BIAS, np.sqrt(vm), n)
        ser[L] = (np.array(m), np.array(S))
    return ro.arm_stats(ser, 1.0)


def verdict(units):
    m, lo, hi, n = ro.t_ci([u["b_div"] for u in units])
    p = ro.sign_flip_p([u["b_div"] for u in units])
    return "R" if (lo > 0 and p < ro.ALPHA) else "N" if hi < ro.MDE_DIV else "I"


def main(sims=400):
    rng = np.random.default_rng(113)
    n_units = 12
    print(f"# RBT-113 power: N {N}, k {K} (P {P}), G {G} generations, {n_units} units, {sims} simulated benchmarks per row")
    print(f"# model: mutational bias {BIAS} sigma0/gen, shared world SD {SD_W}; holistic units average 2 replicates")
    print(f"{'scenario':10s} {'V_m':>5s} {'h2':>5s} {'unit':>5s} {'P(RESPONDS)':>11s} {'P(NO RESP)':>10s} {'mean b_div':>10s} {'sd b_div/unit':>13s} {'mean h2 est':>11s} {'sd h2/unit':>10s} {'mean b_C':>8s}")
    for floor in (False, True):
        for h2, vm in ((0.0, 0.0), (0.02, 0.0), (0.05, 0.0), (0.1, 0.0), (0.2, 0.0), (0.4, 0.0), (0.0, V_M)):
            for reps in (1, 2):  # 1 = a designed-body unit (one arm), 2 = a holistic unit (two replicates averaged)
                vs, bd, he, bc, per_b, per_h = [], [], [], [], [], []
                for _ in range(sims):
                    units = []
                    for _ in range(n_units):
                        a = [sim_arm(h2, rng, floor, vm=vm) for _ in range(reps)]
                        units.append({k: float(np.mean([x[k] for x in a])) for k in a[0]})
                    vs.append(verdict(units))
                    bd.append(np.mean([u["b_div"] for u in units]))
                    he.append(np.mean([u["h2"] for u in units]))
                    bc.append(np.mean([u["b_C"] for u in units]))
                    per_b.append(np.std([u["b_div"] for u in units], ddof=1))
                    per_h.append(np.std([u["h2"] for u in units], ddof=1))
                print(f"{'floor' if floor else 'gaussian':10s} {vm:5.2f} {h2:5.2f} {('arm' if reps == 1 else 'seed'):>5s} {vs.count('R') / sims:11.3f} {vs.count('N') / sims:10.3f}"
                      f" {np.mean(bd):+10.4f} {np.mean(per_b):13.4f} {np.mean(he):+11.3f} {np.mean(per_h):10.3f} {np.mean(bc):+8.4f}")
    # the operator comparison: 12 seed pairs, the Z arm's h2 raised by delta, sharing founders and worlds is not
    # modelled (conservative: pairing only removes variance)
    print(f"\n# operator comparison (designed body): P(Z RAISES) over {n_units} unpaired-noise pairs, base h2 0.2")
    for delta in (0.0, 0.05, 0.1, 0.2):
        hits = 0
        for _ in range(sims):
            d = [sim_arm(0.2 + delta, rng)["b_div"] - sim_arm(0.2, rng)["b_div"] for _ in range(n_units)]
            m, lo, hi, n = ro.t_ci(d)
            hits += lo > 0 and ro.sign_flip_p(d) < ro.ALPHA
        print(f"  delta h2 {delta:+.2f}: P(Z RAISES) {hits / sims:.3f}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
