"""RBT-96 adversary, item 2: the flip-rule verdict under every defensible estimator of the A/A null.

Reads only the committed per-run summaries (runs/RBT-96/{s0,s1}-SEED/generations.txt and RBT-85's
base/prot generations.txt), so it runs in a checkout that never held the bulk.  No simulation.

    python runs/RBT-96/adversary/estimators.py > runs/RBT-96/adversary/estimators.txt

The pre-registered rule: h = 2.776 * sigma_hat / 2 (the 95% band of a four-seed mean under the null);
h <= 0.07 sound, 0.07 < h <= 0.10 edge, h > 0.10 unsound.  The pre-registration committed to
sigma_hat = RMS of the four d (4 df, the mean fixed at 0).
"""
import itertools
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
R96 = os.path.dirname(HERE)
R85 = os.path.join(R96, "..", "RBT-85")
SEEDS = (201, 202, 203, 204)
T4 = 2.776445


def checkpoints(path):
    """final-fifth champion checkpoints: {generation: champ_holistic_mean} (column 14, generation >= 200)."""
    rows = [l.split("\t") for l in open(path).read().splitlines()[1:]]
    return {int(r[0]): float(r[13]) for r in rows if r[13] and int(r[0]) >= 200}


def t_sf2(t, df):
    """two-sided tail of Student's t, Simpson's rule on the density (as runs/RBT-96/readout.py)."""
    t = abs(t)
    c = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
    n = 20000
    h = t / n
    s = sum((1 if i in (0, n) else (4 if i % 2 else 2)) * c * (1 + (i * h) ** 2 / df) ** (-(df + 1) / 2) for i in range(n + 1)) * h / 3
    return max(0.0, 1 - 2 * s)


def chi2_cdf(x, df):
    """chi-square cdf by the regularised lower gamma series."""
    if x <= 0:
        return 0.0
    a, s, term, k = df / 2, 0.0, 1.0 / (df / 2), 0
    while term > 1e-15 * max(s, 1e-300) or k < 5:
        s += term
        k += 1
        term *= (x / 2) / (a + k)
    return s * math.exp(-x / 2 + a * math.log(x / 2) - math.lgamma(a))


def verdict(h):
    return "sound" if h <= 0.07 else ("edge" if h <= 0.10 else "UNSOUND")


def main():
    d, dk = {}, {}
    for s in SEEDS:
        a, b = (checkpoints(os.path.join(R96, f"{arm}-{s}", "generations.txt")) for arm in ("s0", "s1"))
        assert sorted(a) == sorted(b) and len(a) == 11
        dk[s] = [b[g] - a[g] for g in sorted(a)]
        d[s] = st.mean(b.values()) - st.mean(a.values())
    ab = []
    for s in SEEDS:
        a, b = (checkpoints(os.path.join(R85, f"{arm}-{s}", "generations.txt")) for arm in ("base", "prot"))
        ab.append(st.mean(b.values()) - st.mean(a.values()))
    ab_mean = st.mean(ab)
    dv = [d[s] for s in SEEDS]
    print("RBT-96 adversary item 2: the A/A null under each estimator (from the committed generations.txt)")
    print("d = s1 - s0, final-fifth mean champion fitness: " + "  ".join(f"{s} {d[s]:+.4f}" for s in SEEDS))
    print(f"RBT-85 A/B d: {' '.join(f'{x:+.4f}' for x in ab)}  mean {ab_mean:+.4f}\n")

    rms = math.sqrt(sum(x * x for x in dv) / 4)
    sd = st.stdev(dv)
    med = st.median(abs(x) for x in dv) / 0.674490  # median |d| / Phi^-1(0.75): mean known to be 0
    rms3 = math.sqrt(sum(d[s] ** 2 for s in SEEDS if s != 201) / 3)
    # one-way random-effects model on the 44 checkpoint differences, mean fixed at 0 (balanced, 11 per seed)
    msb = 11 * sum(st.mean(dk[s]) ** 2 for s in SEEDS) / 4  # 4 df
    msw = sum(sum((x - st.mean(dk[s])) ** 2 for x in dk[s]) for s in SEEDS) / 40  # 40 df
    var_a = max(0.0, (msb - msw) / 11)
    mixed_seed_sd = math.sqrt(var_a + msw / 11)  # SD of one seed's final-fifth d under the model
    pooled = [x for s in SEEDS for x in dk[s]]
    naive_seed_sd = math.sqrt(sum(x * x for x in pooled) / 44) / math.sqrt(11)  # checkpoints as iid: pseudo-replication

    rows = [
        ("RMS, mean fixed at 0 (4 df)  [PRE-REGISTERED]", rms, 4),
        ("SD about the sample mean (3 df)", sd, 3),
        ("robust: median|d| / 0.6745 (mean known 0)", med, None),
        ("random-effects on 44 checkpoints, mean 0 (REML = ANOVA, balanced)", mixed_seed_sd, 4),
        ("checkpoints as 44 iid draws (pseudo-replication; not defensible)", naive_seed_sd, 43),
        ("RMS without seed 201 (3 of 4; descriptive only)", rms3, 3),
    ]
    print(f"{'estimator':68s} {'sigma_d':>8s} {'h':>7s}  verdict   P(|mean4|>=0.10)   RBT-85 t, p")
    for name, sig, df in rows:
        h = T4 * sig / 2
        se = sig / 2
        pnull = t_sf2(0.10 / se, df) if df else math.erfc(0.10 / se / math.sqrt(2))
        t85 = ab_mean / se
        p85 = t_sf2(t85, df) if df else math.erfc(abs(t85) / math.sqrt(2))
        print(f"{name:68s} {sig:8.4f} {h:7.3f}  {verdict(h):8s}  {pnull:8.3f}           {t85:+.2f}, {p85:.3f}")
    print(f"\nrandom-effects split: between-lineage sd {math.sqrt(var_a):.4f}, within-run checkpoint sd {math.sqrt(msw):.4f} (40 df);"
          f" MSB/MSW = {msb / msw:.1f}.  With balanced checkpoints and the mean fixed at 0 the model's SD of a seed's d is sqrt(MSB/11) = RMS exactly:"
          f" {mixed_seed_sd:.6f} vs {rms:.6f}.  The 11 checkpoints add df to the within-run term only; the between-seed term keeps 4 df.")

    # how sure is 'unsound'?  sigma > 0.10*2/T4 is h > 0.10; chi-square(4) on 4*RMS^2/sigma^2
    for thr, lab in ((0.10, "h > 0.10 (unsound)"), (0.07, "h > 0.07 (not sound)")):
        sig_thr = thr * 2 / T4
        p = 1 - chi2_cdf(4 * rms ** 2 / sig_thr ** 2, 4)
        print(f"{lab}: needs sigma > {sig_thr:.4f}; one-sided p that sigma <= that given RMS {rms:.4f} on 4 df = {p:.4f}"
              f"  (Jeffreys posterior P({lab.split(' (')[0]}) = {1 - p:.4f})")
    for thr in (0.10, 0.07):
        sig_thr = thr * 2 / T4
        print(f"  without seed 201 (3 df): one-sided p that sigma <= {sig_thr:.4f} = {1 - chi2_cdf(3 * rms3 ** 2 / sig_thr ** 2, 3):.4f}")

    # non-parametric: symmetric null resampled from the four observed |d|
    flips = [st.mean(s * x for s, x in zip(signs, dv)) for signs in itertools.product((1, -1), repeat=4)]
    boots = [st.mean(sg * dv[i] for sg, i in zip(signs, idx)) for idx in itertools.product(range(4), repeat=4) for signs in itertools.product((1, -1), repeat=4)]
    print(f"\nnon-parametric: sign-flip of the four observed d (16 means): P(|mean|>=0.10) = {sum(abs(m) >= 0.10 for m in flips) / 16:.3f}"
          f" (max |mean| = sum|d|/4 = {max(abs(m) for m in flips):.4f}); 95th pct |mean| {sorted(abs(m) for m in flips)[15]:.4f}")
    bq = sorted(abs(m) for m in boots)
    print(f"                sign-flip bootstrap (4^4 x 2^4 = {len(boots)} equiprobable means): P(|mean|>=0.10) = {sum(m >= 0.10 for m in bq) / len(bq):.3f};"
          f" 95th pct |mean| = {bq[int(0.95 * len(bq))]:.4f}  (the 'h' of this estimator: {verdict(bq[int(0.95 * len(bq))])});"
          f" P(|mean| >= |RBT-85 mean| {abs(ab_mean):.4f}) = {sum(m >= abs(ab_mean) for m in bq) / len(bq):.3f}")
    print("  (the resampling nulls carry one discovery-sized value in 4 draws on average, as observed; they cannot see a tail heavier than the sample.)")

    # seeds needed for a 95% half-width of 0.10 and 0.05 under each point estimate
    def need(sig, hw):
        for n in range(2, 400):
            tq = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}.get(n - 1, 1.96 + 2.4 / (n - 1))
            if tq * sig / math.sqrt(n) <= hw:
                return n
    print("\nseeds for a 95% half-width of 0.10 / 0.05 (t on n-1 df): " + "; ".join(f"{nm.split(' (')[0].split(',')[0]} {need(sg, 0.10)} / {need(sg, 0.05)}" for nm, sg, _ in rows[:3]))


if __name__ == "__main__":
    main()
