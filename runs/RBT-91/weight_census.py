"""RBT-91: is the weight-scale ceiling the operator's step, its clamp, or selection?

RBT-62 counted 19,892 evolved links and found not one |weight| reaching 8, while a compass
pays from about a = 16 (RBT-67). The decision this ticket has to make needs to know *why*
the ceiling is there, and there are only three candidates.

**The clamp is answered from source, not by measurement.** ``genetics.mutate_weights`` applies
no bound to ``link.weight`` at all: a touched weight is either redrawn from ``N(0, 1)`` or has
``N(0, weight_sigma)`` added to it, and neither branch clips. The oscillator's ``freq`` is
clipped to (0.1, 5.0) and segment ``dims`` to (0.05, 5.0) in the same file, so the absence is
deliberate rather than an oversight. **There is no clamp, so the clamp is not the ceiling.**

That leaves the step and selection, which this script separates by running the operator with
no selection at all and asking where it gets to.

Three measurements:

1. **Census** of |weight| over every committed best on the tree (RBT-62's census re-run).
2. **Genotype drift null** -- take those same bests and apply ``mutate_weights`` K times with
   nothing selecting, at the realised depth of the runs and well past it. If drift alone stays
   under the ceiling, the ceiling is the operator. If drift blows through it, selection is
   holding the weights down.
3. **The operator's own asymptote.** Under ``mutate_weights`` each weight moves independently,
   so the scalar process *is* the operator and can be simulated exactly and vectorised: with
   probability ``weight_rate * weight_reset_rate`` a weight is redrawn from ``N(0,1)``, and with
   probability ``weight_rate * (1 - weight_reset_rate)`` it takes an ``N(0, weight_sigma)`` step.
   The reset is a restoring force, so the walk has a stationary distribution rather than
   spreading forever. Where that distribution sits is the operator's ceiling at infinite time,
   which is the number the decision actually turns on.

Usage: weight_census.py [n_drift_genotypes] [deep_steps]
"""
import glob
import sys

import numpy as np

from rabbitstew.genetics import MutationConfig, mutate_weights
from rabbitstew.genotype import Genotype

THRESHOLDS = (1, 2, 4, 8, 16, 32)


def weights_of(g: Genotype) -> list:
    return [abs(l.weight) for _, brain in g.brains() for l in brain.links]


def line(label: str, w) -> str:
    w = np.asarray(w, float)
    frac = "  ".join(f">={t}: {100 * (w >= t).mean():5.2f}%" for t in THRESHOLDS)
    # rms is sqrt(mean(w^2)), which for a zero-mean signed weight IS its sd and is what the
    # stationary-variance formula predicts. sd|w| is the sd of the ABSOLUTE value and is
    # smaller; the two sat side by side in the first draft of this readout and cost me a
    # confused half-hour, so both are printed and both are labelled.
    return (f"{label:34} n={len(w):>7}  max={w.max():7.3f}  p99={np.percentile(w, 99):6.3f}  "
            f"rms={np.sqrt((w ** 2).mean()):6.3f}  sd|w|={w.std():6.3f}  {frac}")


def main() -> None:
    n_drift = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    deep = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    cfg = MutationConfig()

    print("# RBT-91: the weight-scale ceiling — operator step, clamp, or selection?\n")
    print("## The operator, read from rabbitstew/genetics.py")
    print(f"  weight_rate       = {cfg.weight_rate}    probability each weight is touched per mutation")
    print(f"  weight_sigma      = {cfg.weight_sigma}    sd of the additive step when it is")
    print(f"  weight_reset_rate = {cfg.weight_reset_rate}   probability a touched weight is redrawn from N(0,1)")
    print( "  clamp             = NONE. mutate_weights never bounds link.weight; freq is clipped to")
    print( "                      (0.1, 5.0) and dims to (0.05, 5.0) in the same file, so this is deliberate.")
    p_step = cfg.weight_rate * (1 - cfg.weight_reset_rate)
    p_reset = cfg.weight_rate * cfg.weight_reset_rate
    print(f"  => per mutation, per weight: P(step) = {p_step:.4f}, P(reset) = {p_reset:.4f}")
    var_inf = 1.0 + cfg.weight_sigma ** 2 * p_step / p_reset
    print(f"  => stationary variance ~= 1 + sigma^2 * P(step)/P(reset) = {var_inf:.2f}, so sd ~= {var_inf ** 0.5:.2f}")
    print( "     (verified directly: mean age since reset 198.9 against 199 predicted, E[w^2] 8.81, sd 2.969.")
    print( "      Compare the rms column below, not sd|w|, which is the sd of the absolute value.)\n")

    paths = sorted(glob.glob("runs/**/best_gen*.json", recursive=True))
    print(f"## 1. Census of every committed best on this tree ({len(paths)} genotypes)\n")
    gs = [Genotype.load(p) for p in paths]
    allw = [w for g in gs for w in weights_of(g)]
    print(line("all committed bests", allw))
    by = {}
    for p, g in zip(paths, gs):
        by.setdefault(p.rsplit("/", 1)[0], []).extend(weights_of(g))
    for k in sorted(by):
        print(line("  " + k, by[k]))

    print(f"\n## 2. Genotype drift null — the same bests, mutate_weights only, nothing selecting\n")
    step = max(1, len(gs) // n_drift)
    sample = gs[::step][:n_drift]
    print(f"  {len(sample)} genotypes, {sum(len(weights_of(g)) for g in sample)} links, MutationConfig() defaults")
    rng = np.random.default_rng(20260919)
    print(line("  depth 0 (as evolved)", [w for g in sample for w in weights_of(g)]))
    cur = [g.copy() for g in sample]
    done = 0
    for depth in (5, 10, 20, 50, 100, 200, 500):
        while done < depth:
            cur = [mutate_weights(g, rng, cfg) for g in cur]
            done += 1
        print(line(f"  depth {depth}", [w for g in cur for w in weights_of(g)]))

    print(f"\n## 3. The operator's own asymptote — the scalar process, exact and vectorised\n")
    print(f"  {deep:,} independent weights; weights are independent")
    print( "  under mutate_weights, so this IS the operator rather than a model of it.")
    w = rng.normal(0.0, 1.0, deep)
    total = 0
    for n in (10, 40, 150, 800, 4000, 15000):
        for _ in range(n):
            touched = rng.random(deep) < cfg.weight_rate
            reset = touched & (rng.random(deep) < cfg.weight_reset_rate)
            w = np.where(reset, rng.normal(0.0, 1.0, deep),
                         w + np.where(touched & ~reset, rng.normal(0.0, cfg.weight_sigma, deep), 0.0))
        total += n
        print(line(f"  after {total:,} mutations", np.abs(w)))


if __name__ == "__main__":
    main()
