"""RBT-116 design adversary: does a steering allele that appears once get HELD under the design's truncation,
and at what plateau?  (G6's rule "s(Delta) >= u" against mutation-selection balance.)

Caricature of `evolve --truncation 0.25 --elites 0` (evolution.py:368-380, 492-520): N = 40, the top k = 10 on a
D-draw mean are the pool; each child picks a parent uniformly from the pool; with probability 0.5 (the committed
crossover_rate, evolution.py:49) it is crossed with a second pool member.  A carrier parent's child loses the
trait with probability u (mutation-only erosion: B's route loss 0.146, paper 10's u 0.28), and, when crossed
with a non-carrier, additionally with probability cx (crossover disruption: NOT measured by any audit; 0 or 0.5
here).  Fitness = background + Delta * carrier + mean of D draw noises; background SD and draw SD are auditor
B's measured RBT-113 values (noise.txt): holistic 0.336 / 1.158, designed 0.056 / 1.343.  Background redrawn
each generation (no linkage), which flatters holding.

Reports, from ONE carrier at generation 0 (a proposal), over R replicates: P(line crosses by the design's rule:
share >= 0.25 of 16 probed at generation 48), and the mean carrier share at 48 given it is not lost.
Also the equilibrium share from a carrier-saturated start (the power model's plateau Q).

python3 runs/RBT-116/design-adversary/hold.py > hold.txt
"""
import numpy as np

N, K, G = 40, 10, 48


def run(delta, u, cx, sb, sd, D, rng, start):
    c = np.zeros(N, bool); c[:start] = True
    for _ in range(G):
        fit = rng.normal(0, sb, N) + delta * c + rng.normal(0, sd / np.sqrt(D), N)
        pool = np.argsort(-fit)[:K]
        par = rng.choice(pool, N)
        crossed = rng.random(N) < 0.5
        oth = rng.choice(pool, N)
        child = c[par].copy()
        lose = rng.random(N) < u
        lose |= crossed & ~c[oth] & (rng.random(N) < cx)
        child &= ~lose
        c = child
    probe = rng.choice(N, 16, replace=False)
    return c.mean(), c[probe].mean() >= 0.25


def main():
    rng = np.random.default_rng(116)
    R = 400
    print(f"# hold.py: N {N}, top {K}, crossover 0.5, G {G}; {R} replicates per row")
    print("fauna     D  Delta   u     cx  | P(cross from 1 carrier)  mean share@48 | share@48 from saturated start (plateau Q)")
    for fauna, sb, sd in (("holistic", 0.336, 1.158), ("designed", 0.056, 1.343)):
        for D in (2, 8):
            for delta in (0.10, 0.25, 0.50):
                for u in (0.146, 0.28):
                    for cx in (0.0, 0.5):
                        one = [run(delta, u, cx, sb, sd, D, rng, 1) for _ in range(R)]
                        sat = [run(delta, u, cx, sb, sd, D, rng, N)[0] for _ in range(100)]
                        pc = np.mean([o[1] for o in one]); ms = np.mean([o[0] for o in one])
                        print(f"{fauna:9s} {D}  {delta:4.2f}  {u:5.3f}  {cx:3.1f}  | {pc:22.3f}  {ms:13.3f} | {np.mean(sat):.3f}", flush=True)


if __name__ == "__main__":
    main()
