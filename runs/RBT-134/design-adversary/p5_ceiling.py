# Adversary: P5's own link-product ceiling.  An event adds 4 links |N(0,1)| (signs arranged as the predicate wants);
# afterwards each link takes the default walk (rate 0.25 per mutation, step N(0,0.4), reset N(0,1) at 0.02) for the
# remaining 19-j mutations.  Upper bound on links-alone |a| = |(uL-uR)/2 * (vL+vR)/2| (unit slopes).
import numpy as np
rng = np.random.default_rng(134)
N = 2_000_000
j = rng.integers(1, 20, N)               # mutation at which the event fires (uniform given one event)
w = np.abs(rng.normal(0, 1, (N, 4)))
w[:, 1] *= -1                            # in-pair of opposite sign; out-pair same sign
for m in range(1, 19):
    live = (19 - j) >= m
    pert = (rng.random((N, 4)) < 0.25) & live[:, None]
    reset = pert & (rng.random((N, 4)) < 0.02)
    step = rng.normal(0, 0.4, (N, 4))
    w = np.where(reset, rng.normal(0, 1, (N, 4)), np.where(pert, w + step, w))
prod = np.abs((w[:, 0] - w[:, 1]) / 2 * (w[:, 2] + w[:, 3]) / 2)
events = 200_000 * (1 - 0.995 ** 19)
for rung in (6.2831, 12.5236, 24.7145):
    p = (prod >= rung).mean()
    print(f"rung {rung}: P(product >= rung | event) = {p:.2e}; expected lineages over {events:,.0f} events = {p * events:.2f}")
print(f"product quantiles: median {np.median(prod):.3f}  p99.9 {np.quantile(prod, .999):.3f}  max {prod.max():.2f}")
