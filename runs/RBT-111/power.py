"""RBT-111: power and size of the registered test, by simulation, re-derived for the designer (not the adversary's
t-test).  The registered test (PERM) is the one readout.py runs: c0 by the exact within-seed permutation test over
the 3^n labellings of the s0 label, c12 by the exact sign-flip test, Holm over the two at alpha = 0.05, then the
reading table.  SF, the design as first filed (sign-flip on both contrasts), is kept as a comparison column: the
RBT-111 design adversary's F2 replaced it before any arm.

Model.  One run's outcome is y = e + offset, where e is independent per run.  The seed's own level cancels
in both contrasts, so it is left out.  Three noise models for e, the adversary's (READOUT-ADVERSARY.md §c):
  N62  normal, sd 0.062   (the RBT-108 spread about its mean, 0.088 / sqrt 2)
  N81  normal, sd 0.081   (RBT-108's RMS 0.115 / sqrt 2, the pure-chance reading)
  T    normal, sd 0.040, plus a +0.25 discovery with probability 1/16 (2 discoveries in RBT-108's 32 runs)
Scenarios, with delta a salt-0 deficit as RBT-108 saw it (s1 ahead of s0):
  null           no offset                           -> expected reading "chance"
  salt0 delta    y_s0 -= delta                       -> expected "salt0"
  salt1 delta    y_s1 += delta (salt-1 specific)     -> expected "keys" (c12 = -delta, c0 = delta / 2)

    python runs/RBT-111/power.py [TRIALS] [SEEDS]   (defaults 10000 trials per cell and 16 seeds, the registered design; numpy.random.default_rng(111),
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

N = 16
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


def perm_c0_p_batch(Y, tol=1e-12):
    """readout.perm_c0_p for each trial of Y (trials, n, 3): the exact within-seed permutation p of c0 by meet in the
    middle, the half sums built with numpy and counted with searchsorted per trial.  Returns (p, count)."""
    Y = np.asarray(Y, dtype=float)
    a, b, c = Y[:, :, 0], Y[:, :, 1], Y[:, :, 2]
    ch = np.stack([(b + c) / 2 - a, (a + c) / 2 - b, (a + b) / 2 - c], axis=2)  # (trials, n, 3)
    obs = np.abs(ch[:, :, 0].sum(1))
    n = Y.shape[1]
    h = n // 2

    def half(part):
        s = np.zeros((len(Y), 1))
        for j in range(part.shape[1]):
            s = (s[:, :, None] + part[:, j, None, :]).reshape(len(Y), -1)
        return s

    left, right = half(ch[:, :h]), np.sort(half(ch[:, h:]), axis=1)
    hits = np.empty(len(Y), dtype=np.int64)
    n_r = right.shape[1]
    for t in range(len(Y)):
        if obs[t] <= tol:
            hits[t] = 3 ** n
            continue
        hi = n_r - np.searchsorted(right[t], obs[t] - tol - left[t], side="left")
        lo = np.searchsorted(right[t], -obs[t] + tol - left[t], side="right")
        hits[t] = int(hi.sum() + lo.sum())
    return hits / 3 ** n, hits


def holm2(p0, p12, alpha=0.05):
    lo, hi = np.minimum(p0, p12), np.maximum(p0, p12)
    first = lo <= alpha / 2
    second = first & (hi <= alpha)
    return np.where(p0 <= p12, first, second), np.where(p12 < p0, first, second)


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
    sf0, p12 = sign_flip_p_batch(c0), sign_flip_p_batch(c12)
    pm0, _ = perm_c0_p_batch(y)
    up = c0.sum(1) > 0
    out = dict(raw12=np.mean(p12 <= ro.ALPHA))
    for name, p0 in (("sf", sf0), ("perm", pm0)):
        rej0, rej12 = holm2(p0, p12, ro.ALPHA)
        read = np.where(rej12, "keys", np.where(rej0, "salt0", "chance"))
        out[name] = dict(rej0=rej0.mean(), rej12=rej12.mean(), correct=np.mean(read == EXPECTED[kind]),
                         salt0=np.mean(read == "salt0"), raw0=np.mean(p0 <= ro.ALPHA),
                         raw0_up=np.mean((p0 <= ro.ALPHA) & up), raw0_down=np.mean((p0 <= ro.ALPHA) & ~up))
    t0 = c0.mean(1) / (c0.std(1, ddof=1) / np.sqrt(N))
    out["ttest0"] = np.mean(np.abs(t0) > T_Q[N])
    return out


def main(trials=10000):
    # the vectorised tests must be the readout's exact tests
    rng = np.random.default_rng(0)
    X = rng.normal(size=(20, N))
    assert np.allclose(sign_flip_p_batch(X), [ro.sign_flip_p(x)[0] for x in X])
    Y = rng.normal(0, 0.06, size=(20, N, 3)) + 0.25 * (rng.random((20, N, 3)) < 1 / 16)
    Y[:10, :, 0] -= 0.08
    pb, hb = perm_c0_p_batch(Y)
    ref = [ro.perm_c0_p([tuple(r) for r in y]) for y in Y]
    assert [int(h) for h in hb] == [r[1] for r in ref] and np.allclose(pb, [r[0] for r in ref], rtol=0, atol=1e-15)
    print(f"RBT-111 power by simulation: {trials} trials per cell, numpy.random.default_rng(111), n = {N} seeds x 3 salts")
    print(f"PERM (registered): c0 by the exact within-seed permutation test (all 3^{N} labellings of the s0 label), c12 by the exact")
    print(f"  sign-flip test (all 2^{N} sign assignments), Holm over the two at 0.05, then the reading table.")
    print(f"SF (as first filed, replaced before any arm): the sign-flip test on c0 as well.  The vectorised p's are asserted equal")
    print(f"  to readout.sign_flip_p and readout.perm_c0_p (counts identical) before any cell is run.\n")
    print("columns: Holm rejection of c0 (PERM, SF); Holm rejection of c12 (PERM); P(reading = expected) (PERM, SF);")
    print("  P(reading = salt 0) (PERM, SF); unadjusted c0 rejection split by the sign of c0, > 0 / < 0 (PERM, SF); unadjusted c12; t-test on c0\n")
    print("scenario        model   c0 PERM  c0 SF   c12     right PERM  right SF   'salt0' PERM  'salt0' SF   raw c0 PERM (>0/<0)    raw c0 SF (>0/<0)      raw c12  t c0")
    for kind, delta, _ in SCENARIOS:
        for m in MODELS:
            r = simulate(trials, m, kind, delta)
            P, S = r["perm"], r["sf"]
            label = f"{kind} {delta:.3f}" if delta else "null"
            print(f"{label:14}  {m:5}   {P['rej0']:.3f}    {S['rej0']:.3f}   {P['rej12']:.3f}   {P['correct']:.3f}       {S['correct']:.3f}      "
                  f"{P['salt0']:.3f}         {S['salt0']:.3f}        {P['raw0']:.3f} ({P['raw0_up']:.3f}/{P['raw0_down']:.3f})    "
                  f"{S['raw0']:.3f} ({S['raw0_up']:.3f}/{S['raw0_down']:.3f})    {r['raw12']:.3f}    {r['ttest0']:.3f}")
    print("\nreading: under 'null' the c0 and c12 columns are the Holm sizes and 'right' is P(chance); under salt0 the c0 columns are the"
          " power; under salt1 the c12 column is the power to call 'keys' and 'salt0' is the misread rate (F9).")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        N = int(sys.argv[2])
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
