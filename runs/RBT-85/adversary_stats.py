"""Adversary re-derivation for RBT-85, from the tracked generations.txt files alone.

Independent of runs/RBT-85/readout.py (nothing imported from it): the four paired differences,
the resolution triple the report quotes (independent-checkpoint 0.062, checkpoint-paired 0.022,
observed-spread 0.046), and the things the report's "-2.1 SE" framing leaves out -- the t(3)
p-value, the coverage a "2 SE" band actually has at three degrees of freedom, and the 95% t
interval.  Also the within-pair checkpoint correlations (what the shared streams buy at the
checkpoint level), the paired difference on the ratio scale against the opponent covariate, the
runaway/driver split under a sensible label, and prediction intervals for the depth cells: what a
new draw deserves from RBT-74's four values, against the four-run ranges the pre-registration used.

usage: python runs/RBT-85/adversary_stats.py [runs/RBT-85]
"""
import math
import os
import statistics as st
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-85"
SEEDS = (201, 202, 203, 204)
L = []


def t3_cdf(t):
    """Student t with 3 degrees of freedom, closed form."""
    x = t / math.sqrt(3)
    return 0.5 + (x / (1 + x * x) + math.atan(x)) / math.pi


def t3_p(t):
    return 2 * (1 - t3_cdf(abs(t)))


def t3_q(p):
    lo, hi = 0.0, 50.0
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if t3_cdf(m) < p else (lo, m)
    return (lo + hi) / 2


def checkpoints(run):
    rows = [l.split("\t") for l in open(os.path.join(root, run, "generations.txt")).read().splitlines()[1:]]
    return [float(r[13]) for r in rows if r[13] != "" and int(r[0]) >= 200]


B = {s: checkpoints(f"base-{s}") for s in SEEDS}
P = {s: checkpoints(f"prot-{s}") for s in SEEDS}
fb = {s: st.mean(B[s]) for s in SEEDS}
fp = {s: st.mean(P[s]) for s in SEEDS}
d = [fp[s] - fb[s] for s in SEEDS]
mean, se = st.mean(d), st.stdev(d) / math.sqrt(4)
L.append(f"{root}: final-fifth checkpoints per run (generations >= 200): " + str({s: (len(B[s]), len(P[s])) for s in SEEDS}))
L.append(f"paired differences (prot - base): {', '.join(f'{x:+.4f}' for x in d)}  mean {mean:+.4f}  SE {se:.4f}  2 SE {2 * se:.4f}  |mean| - 2 SE = {abs(mean) - 2 * se:+.4f}")

L.append("\n=== the resolution triple, recomputed ===")
sds = [st.pstdev(B[s]) for s in SEEDS]
per = st.mean(sds) / math.sqrt(11)
L.append(f"independent-checkpoint: mean pstdev of the unprotected final-fifth checkpoints {st.mean(sds):.3f} -> SD of an 11-checkpoint mean {per:.3f} -> 2 SE at n = 4 if the arms' noise were independent: {2 * per * math.sqrt(2) / 2:.3f}")
cks = [st.pstdev([y - x for x, y in zip(B[s], P[s])]) / math.sqrt(11) for s in SEEDS]
L.append(f"checkpoint-paired: per seed, pstdev of the 11 within-pair checkpoint differences / sqrt(11): {', '.join(f'{c:.4f}' for c in cks)} -> mean {st.mean(cks):.4f} -> 2 SE at n = 4: {2 * st.mean(cks) / 2:.3f}  (computed from within-pair differences, not assumed)")
L.append(f"observed spread: 2 SE of the four paired differences {2 * se:.3f}")
L.append("within-pair checkpoint correlation (what the shared opponent and terrains buy at the checkpoint level):")
for s in SEEDS:
    L.append(f"  seed {s}: corr(base, prot) over 11 checkpoints {st.correlation(B[s], P[s]):+.2f}; SD base {st.pstdev(B[s]):.3f} prot {st.pstdev(P[s]):.3f} difference {st.pstdev([y - x for x, y in zip(B[s], P[s])]):.3f}")

L.append("\n=== what the '-2.1 SE' framing leaves out ===")
t = mean / se
q = t3_q(0.975)
L.append(f"t(3) = {t:+.2f}, two-sided p = {t3_p(t):.3f}")
L.append(f"a +-2 SE band at 3 degrees of freedom has coverage {1 - t3_p(2.0):.3f}: it is an 86% interval, not a 95% one")
L.append(f"t_0.975(3) = {q:.3f}; 95% half-width {q * se:.4f}; interval [{mean - q * se:+.4f}, {mean + q * se:+.4f}]  (contains 0 and contains -0.10)")

L.append("\n=== the covariate ===")
opp = [-19.33, -14.13, -0.96, 1.87]      # wheeled final-fifth solo approach, from toolkit.txt / the report
solo = [-0.57, -0.39, 0.03, -0.12]       # holistic solo approach, prot - base, from the report
L.append(f"d on the ratio scale (d / base level): {', '.join(f'{x / fb[s]:+.3f}' for x, s in zip(d, SEEDS))}")
L.append(f"corr(d, wheeled approach) {st.correlation(d, opp):+.2f}; corr(d / base, wheeled approach) {st.correlation([x / fb[s] for x, s in zip(d, SEEDS)], opp):+.2f}; corr(d, holistic solo-approach d) {st.correlation(d, solo):+.2f}   (n = 4 throughout)")
L.append(f"runaway/driver split with seed 203 as a driver (approach -0.96 m, steering 2.09): unprotected {st.mean([fb[201], fb[202]]):.3f} vs {st.mean([fb[203], fb[204]]):.3f}; protected {st.mean([fp[201], fp[202]]):.3f} vs {st.mean([fp[203], fp[204]]):.3f}")

L.append("\n=== depth: what a new draw deserves from RBT-74's four values (mean +- t_0.975 * s * sqrt(1 + 1/n)), against the registered four-run range ===")
cells = {
    "unprotected mutation events": ([157, 146, 166, 159], [177, 166, 171, 152], "145-170"),
    "protected body changes": ([46, 41, 47, 47], [46, 52, 48, 43], "40-50"),
    "protected controller-only": ([157, 124, 142, 143], [141, 166, 154, 144], "120-160"),
    "protected mutation events": ([203, 166, 189, 190], [187, 219, 202, 187], "165-205"),
    "conventional": ([226, 208, 206, 210, 224, 228, 209, 224], [204, 215, 220, 213], "205-230"),
}
for name, (old, new, reg) in cells.items():
    n, m, s = len(old), st.mean(old), st.stdev(old)
    tq = t3_q(0.975) if n == 4 else 2.365          # t_0.975 with 7 df for the eight conventional values
    hw = tq * s * math.sqrt(1 + 1 / n)
    out = [v for v in new if v < m - hw or v > m + hw]
    welch = (st.mean(new) - m) / math.sqrt(s * s / n + st.variance(new) / 4)
    L.append(f"  {name:28s} RBT-74 {old} (mean {m:.0f}, sd {s:.1f}); 95% prediction interval [{m - hw:.0f}, {m + hw:.0f}]; registered {reg}; RBT-85 {new}: outside the interval: {out or 'none'}; Welch t between the two arms' means {welch:+.2f}")

text = "\n".join(L)
print(text)
os.makedirs("docs/runs", exist_ok=True)
with open("docs/runs/RBT-85-adversary-stats.txt", "w") as f:
    f.write(text + "\n")
