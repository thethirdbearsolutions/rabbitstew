"""RBT-111: power and size of the registered test, by simulation, re-derived for the designer (not the adversary's
t-test).  The test simulated is the one readout.py runs: the exact two-sided sign-flip test on c0 and on c12,
Holm over the two at alpha = 0.05, then the reading table.

Model.  One run's outcome is y = e + offset, where e is independent per run.  The seed's own level cancels
in both contrasts, so it is left out.  Three noise models for e, the adversary's (READOUT-ADVERSARY.md §c):
  N62  normal, sd 0.062   (the RBT-108 spread about its mean, 0.088 / sqrt 2)
  N81  normal, sd 0.081   (RBT-108's RMS 0.115 / sqrt 2, the pure-chance reading)
  T    normal, sd 0.040, plus a +0.25 discovery with probability 1/16 (2 discoveries in RBT-108's 32 runs)
Scenarios, with delta a salt-0 deficit as RBT-108 saw it (s1 ahead of s0):
  null           no offset                           -> expected reading "chance"
  salt0 delta    y_s0 -= delta                       -> expected "salt0"
  salt1 delta    y_s1 += delta (salt-1 specific)     -> expected "keys" (c12 = -delta, c0 = delta / 2)

    python runs/RBT-111/power.py [TRIALS] [SEEDS]   (defaults 10000 trials per cell and 12 seeds; numpy.random.default_rng(111),
                                                    the same stream in every cell, so cells differ only in model and scenario)
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt111_readout", os.path.join(HERE, "readout.py"))
ro = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ro)

N = 12
MODELS = {"N62": (0.062, 0.0), "N81": (0.081, 0.0), "T": (0.040, 1 / 16)}
SCENARIOS = [("null", 0.0, None), ("salt0", 0.05, "s0"), ("salt0", 0.082, "s0"), ("salt1", 0.05, "s1"), ("salt1", 0.082, "s1")]
EXPECTED = {"null": "chance", "salt0": "salt0", "salt1": "keys"}
T_Q = {12: 2.200985, 16: 2.131450}  # t(n-1) 0.975, the adversary's test, for the cross-check column


def sign_flip_p_batch(X, chunk=1000):
    """readout.sign_flip_p for each row of X (trials, n), vectorised with numpy (the readout itself is pure Python)."""
    X = np.asarray(X, dtype=float)
    n = X.shape[1]
    S = (1 - 2 * ((np.arange(2 ** n)[:, None] >> np.arange(n)[None, :]) & 1)).T.astype(float)
    out = np.empty(len(X))
    for i in range(0, len(X), chunk):
        x = X[i:i + chunk]
        out[i:i + chunk] = np.mean(np.abs(x @ S) >= np.abs(x.sum(1))[:, None] - 1e-12, axis=1)
    return out


def draw(rng, trials, model):
    sd, pdisc = MODELS[model]
    e = rng.normal(0.0, sd, size=(trials, N, 3))
    if pdisc:
        e += 0.25 * (rng.random((trials, N, 3)) < pdisc)
    return e


def simulate(trials, model, kind, delta, seed=111):
    rng = np.random.default_rng(seed)
    y = draw(rng, trials, model)
    if kind == "salt0":
        y[:, :, 0] -= delta
    elif kind == "salt1":
        y[:, :, 1] += delta
    c0 = (y[:, :, 1] + y[:, :, 2]) / 2 - y[:, :, 0]
    c12 = y[:, :, 2] - y[:, :, 1]
    p0, p12 = sign_flip_p_batch(c0), sign_flip_p_batch(c12)
    lo, hi = np.minimum(p0, p12), np.maximum(p0, p12)
    first = lo <= ro.ALPHA / 2
    second = first & (hi <= ro.ALPHA)
    rej0 = np.where(p0 <= p12, first, second)
    rej12 = np.where(p12 < p0, first, second)
    read = np.where(rej12, "keys", np.where(rej0, "salt0", "chance"))
    t0 = c0.mean(1) / (c0.std(1, ddof=1) / np.sqrt(N))
    return dict(raw0=np.mean(p0 <= ro.ALPHA), raw12=np.mean(p12 <= ro.ALPHA), rej0=rej0.mean(), rej12=rej12.mean(),
                correct=np.mean(read == EXPECTED[kind]), ttest0=np.mean(np.abs(t0) > T_Q[N]))


def main(trials=10000):
    # the vectorised test must be the readout's exact test
    rng = np.random.default_rng(0)
    X = rng.normal(size=(20, N))
    assert np.allclose(sign_flip_p_batch(X), [ro.sign_flip_p(x)[0] for x in X])
    print(f"RBT-111 power by simulation: {trials} trials per cell, numpy.random.default_rng(111), n = {N} seeds x 3 salts")
    print("test: exact two-sided sign-flip on c0 and c12 (all 2^12 sign assignments), Holm over the two at 0.05, then the reading table")
    print("columns: P(c0 rejected, Holm)  P(c12 rejected, Holm)  P(reading = expected)  | unadjusted P(p<=0.05) c0, c12 | adversary's t-test on c0\n")
    print("scenario        model   c0 Holm   c12 Holm   reading right   raw c0   raw c12   t-test c0")
    for kind, delta, _ in SCENARIOS:
        for m in MODELS:
            r = simulate(trials, m, kind, delta)
            label = f"{kind} {delta:.3f}" if delta else "null"
            print(f"{label:14}  {m:5}   {r['rej0']:.3f}     {r['rej12']:.3f}      {r['correct']:.3f}           {r['raw0']:.3f}    {r['raw12']:.3f}     {r['ttest0']:.3f}")
    print("\nreading: under 'null', 'c0 Holm' and 'c12 Holm' are the test's sizes and 'reading right' is P(chance);"
          " under salt0 the c0 column is the power; under salt1 the c12 column is the power to call 'keys'.")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        N = int(sys.argv[2])
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
