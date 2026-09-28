"""RBT-132 projection check: how k3_projection.py's plug-in projection behaves when its inputs are the noisy n = 16
estimates the calibration lane will hand it.  Synthetic inputs only (no calibration output exists).

    python runs/RBT-116/design-adversary/rbt132_projection_check.py [REPS] > runs/RBT-116/design-adversary/rbt132_projection_check.txt

Truth: per plant, a per-draw ΔT ~ Normal(μ, σ²) (the projection's own model, so only estimation error is tested),
σ = 1 without loss of generality, so a plant is its standardised effect δ = μ/σ.  Two calibration cells, 8 (a) and 8 (c)
plants each.  One simulated calibration = 16 stage-2 draws per plant -> (μ̂, σ̂) exactly as from_planted recovers them
-> k3_projection.rule.  The TRUE share at a count n is the mean over plants of p_c2(δ, 1, n)²; the rule's pick is
compared with the truth:
- FALSE PASS: the rule picks n but the true share at n is < 0.6 for some kind at some cell (the probe leg launches with
  counts at which K3 will likely VOID at the points: budget spent, layer VOID);
- FALSE UNREADABLE: the rule says unreadable, but the true share reaches 0.6 at 64 at both cells for both kinds.
Also: the mean projected share against the true share (the plug-in bias), and the same for a candidate fix, the
projection fed an 80% one-sided lower bound on each plant's μ (μ̂ − t(0.80, 15)·σ̂/4).
Scenarios: homogeneous δ for every plant, and a heterogeneous set shaped like the fix-check's fixture (a) plants
(δ ≈ 0.78, 0.27, 0.21, 0.20, 0.14, 0.14, 0.04, −0.18; rbt132_seen_signflip.txt, signed rows: σ from dT − lbdT).
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-116"))
spec = importlib.util.spec_from_file_location("k3_projection", os.path.join(ROOT, "runs", "RBT-116", "k3_projection.py"))
K = importlib.util.module_from_spec(spec)
sys.modules["k3_projection"] = K
spec.loader.exec_module(K)
steer = K.steer

N0 = 16
COUNTS = K.COUNTS
FIXTURE = [0.78, 0.27, 0.21, 0.20, 0.14, 0.14, 0.04, -0.18]
T80 = steer.t_quantile(0.80, N0 - 1)


def pc2_table():
    """p_c2(δ, 1, n) on a δ grid, interpolated: the projection's own function, tabulated for speed."""
    grid = np.linspace(-2.0, 3.0, 501)
    return grid, {n: np.array([K.p_c2(d, 1.0, n, grid=1201) for d in grid]) for n in COUNTS}


G, TAB = pc2_table()


def pc2(delta, n):
    return np.interp(delta, G, TAB[n])


def true_share(deltas, n):
    return float(np.mean(pc2(np.asarray(deltas), n) ** 2))


def pick(shares_by_n):
    return next((n for n in COUNTS if all(s >= K.TARGET for s in shares_by_n[n].values())), K.UNREADABLE)


def one_calibration(rng, cells, lower, n0=N0):
    picks, proj = [], []
    for cell in cells:
        sh = {}
        for n in COUNTS:
            sh[n] = {}
        for kind, deltas in cell.items():
            x = rng.normal(np.asarray(deltas)[:, None], 1.0, (len(deltas), n0))
            mu, sd = x.mean(1), x.std(1, ddof=1)
            if lower:
                mu = mu - T80 * sd / np.sqrt(n0)
            d_hat = mu / sd
            for n in COUNTS:
                sh[n][kind] = float(np.mean(pc2(d_hat, n) ** 2))
        picks.append(pick(sh))
        proj.append(sh)
    rule = K.UNREADABLE if K.UNREADABLE in picks else max(picks)
    return rule, proj


def evaluate(cells, reps, rng, lower, n0=N0):
    truth = [{n: {k: true_share(d, n) for k, d in c.items()} for n in COUNTS} for c in cells]
    truth_pick = [pick(t) for t in truth]
    truth_rule = K.UNREADABLE if K.UNREADABLE in truth_pick else max(truth_pick)
    fp = fu = 0
    picks = {}
    bias = {n: [] for n in COUNTS}
    for _ in range(reps):
        r, proj = one_calibration(rng, cells, lower, n0)
        picks[r] = picks.get(r, 0) + 1
        if r != K.UNREADABLE and any(t[r][k] < K.TARGET for t in truth for k in t[r]):
            fp += 1
        if r == K.UNREADABLE and truth_rule != K.UNREADABLE:
            fu += 1
        for n in COUNTS:
            bias[n].append(np.mean([p[n][k] - t[n][k] for p, t in zip(proj, truth) for k in t[n]]))
    return truth, truth_rule, picks, fp / reps, fu / reps, {n: float(np.mean(v)) for n, v in bias.items()}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rng = np.random.default_rng(132132)
    print(f"# rbt132_projection_check.py: {reps} simulated calibrations per scenario; 2 cells x (8 (a) + 8 (c)); n0 = {N0}; "
          f"target {K.TARGET}; counts {COUNTS}")
    print("# per scenario: TRUE share (a = c) at 16/32/64 and the true rule; then for the plug-in projection (as merged) and the "
          "80% lower-bound variant: the rule's picks, FALSE PASS, FALSE UNREADABLE, and mean (projected - true) share at 16/32/64")
    scen = [(f"homogeneous delta {d:.2f}", [{"a": [d] * 8, "c": [d] * 8}] * 2) for d in (0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.70)]
    scen += [("fixture-shaped (a) and (c), both cells", [{"a": FIXTURE, "c": FIXTURE}] * 2),
             ("fixture-shaped x1.5", [{"a": [1.5 * d for d in FIXTURE], "c": [1.5 * d for d in FIXTURE]}] * 2),
             ("fixture-shaped x2", [{"a": [2 * d for d in FIXTURE], "c": [2 * d for d in FIXTURE]}] * 2),
             ("one strong plant, seven null (x8 per kind)", [{"a": [1.5] + [0.0] * 7, "c": [1.5] + [0.0] * 7}] * 2)]
    for name, cells in scen:
        print(f"\n## {name}")
        for label, lower in (("plug-in (merged)", False), ("80% lower bound", True)):
            truth, tr, picks, fp, fu, bias = evaluate(cells, reps, rng, lower)
            if not lower:
                print("  TRUE share: " + " / ".join(f"n {n} {truth[0][n]['a']:.3f}" for n in COUNTS) + f"; true rule: {tr}")
            pk = ", ".join(f"{k}: {v / reps:.2f}" for k, v in sorted(picks.items(), key=lambda kv: (isinstance(kv[0], str), kv[0])))
            print(f"  {label:17s} picks {{{pk}}}; FALSE PASS {fp:.3f}; FALSE UNREADABLE {fu:.3f}; "
                  f"bias " + " / ".join(f"{bias[n]:+.3f}" for n in COUNTS))
    print("\n## the same rule fed 32 calibration draws per plant (stage 2 + the confirmation run on EVERY (a) and (c) plant)")
    for name, cells in [s_ for s_ in scen if s_[0] in ("homogeneous delta 0.35", "homogeneous delta 0.40", "homogeneous delta 0.50",
                                                        "fixture-shaped x2", "homogeneous delta 0.30", "homogeneous delta 0.25")]:
        truth, tr, picks, fp, fu, bias = evaluate(cells, reps, rng, False, 32)
        pk = ", ".join(f"{k}: {v / reps:.2f}" for k, v in sorted(picks.items(), key=lambda kv: (isinstance(kv[0], str), kv[0])))
        print(f"  {name:32s} true rule {tr}; picks {{{pk}}}; FALSE PASS {fp:.3f}; FALSE UNREADABLE {fu:.3f}")
    # the first branch: measured SEEN >= 0.45 on 8 plants per kind per cell, when the true share is lower
    print("\n## the first branch (measured SEEN >= 0.45, i.e. >= 4 of 8, for both kinds at both cells) at a true share p")
    from math import comb
    for p in (0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6):
        one = sum(comb(8, k) * p ** k * (1 - p) ** (8 - k) for k in range(4, 9))
        print(f"  p {p:.2f}: P(>= 4 of 8) {one:.3f}; P(all four kind-cells pass, independent) {one ** 4:.3f}; "
              f"K3 false-VOID at p (probe_power) {K.planters.steer and __import__('probe_power').k3_false_void(p, p):.3f}")


if __name__ == "__main__":
    main()
