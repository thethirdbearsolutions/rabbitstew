"""Paired statistics for lesion comparisons (RBT-38).

Every lesion probe in this family runs each mode over the *same* seed list, so
the comparison is paired, but the probes reported each mode's own standard
error and compared the means as if the two samples were independent.  That is
the wrong error term and it hides the shape of the effect: RBT-22's season-300
Pioneer was reported as a 27% nose effect when twelve of its sixteen bouts were
bit-identical with the nose on and off and the mean was carried by one seed
that ate four items more.

This module is the one place the family computes such a comparison.  It returns
the per-seed differences themselves alongside every summary, because the
standing rule this ticket establishes is that no lesion effect is claimed
without its per-seed differences shown.

No scipy: the non-parametric tests here are a sign-flip permutation test (the
paired differences are exchangeable in sign under the null) and an exact sign
test, both of which are a few lines and neither of which assumes normality.
The differences are mostly zeros with occasional integer jumps, so a t statistic
alone is not to be trusted on them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import comb, sqrt
from typing import Optional, Sequence

import numpy as np


@dataclass
class PairedResult:
    """One paired comparison, with the raw differences kept."""

    n: int
    mean: float  #: mean paired difference (first minus second)
    paired_se: float  #: standard error of that mean, using the differences
    t: float  #: mean / paired_se; nan when every difference is identical
    unpaired_se: float  #: the wrong error term the old probes used, for comparison
    zeros: int  #: seeds where the difference is exactly zero
    positive: int
    negative: int
    perm_p: float  #: two-sided sign-flip permutation p
    sign_p: float  #: two-sided exact sign test over the non-zero seeds
    diffs: list = field(default_factory=list)

    @property
    def zero_fraction(self) -> float:
        return self.zeros / self.n if self.n else 0.0

    def verdict(self, t_threshold: float = 2.5) -> str:
        """RBT-38's rule: |t| over threshold, vetoed when most seeds are unmoved.

        The veto is the point of the ticket.  An effect that is exactly zero on
        more than half the seeds is not a bias of the reported size, whatever
        its mean does, so it is named for what it is rather than counted.
        """
        if self.n == 0:
            return "no data"
        if abs(self.t) < t_threshold or not np.isfinite(self.t):
            return "not separable"
        if self.zero_fraction > 0.5:
            return "sparse, not a bias"
        return "separable"

    def line(self, label: str = "") -> str:
        return (f"{label:22s} n={self.n:3d}  mean {self.mean:+7.3f}  paired SE {self.paired_se:5.3f}  t {self.t:+6.2f}"
                f"  (unpaired SE {self.unpaired_se:5.3f})  zeros {self.zeros:3d}/{self.n}  +{self.positive} -{self.negative}"
                f"  perm p {self.perm_p:.3f}  sign p {self.sign_p:.3f}  -> {self.verdict()}")


def _perm_p(diffs: np.ndarray, draws: int, rng: np.random.Generator) -> float:
    """Two-sided sign-flip permutation test on paired differences.

    Under the null the differences are symmetric about zero, so flipping each
    one's sign independently generates the null distribution of the mean.
    """
    nz = diffs[diffs != 0.0]
    if len(nz) == 0:
        return 1.0
    observed = abs(nz.mean())
    signs = rng.choice((-1.0, 1.0), size=(draws, len(nz)))
    null = np.abs((signs * nz).mean(axis=1))
    return float((np.count_nonzero(null >= observed - 1e-12) + 1) / (draws + 1))


def _sign_p(pos: int, neg: int) -> float:
    """Two-sided exact sign test over the seeds that moved at all."""
    n = pos + neg
    if n == 0:
        return 1.0
    k = min(pos, neg)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2.0**n)
    return float(min(1.0, 2.0 * tail))


def paired(a: Sequence[float], b: Sequence[float], draws: int = 20000, seed: int = 0) -> PairedResult:
    """Compare two modes measured on the same seeds, first minus second."""
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"paired comparison needs equal-length samples, got {x.shape} and {y.shape}")
    d = x - y
    ok = ~np.isnan(d)
    d = d[ok]
    n = len(d)
    if n == 0:
        return PairedResult(0, float("nan"), float("nan"), float("nan"), float("nan"), 0, 0, 0, 1.0, 1.0, [])
    paired_se = float(d.std(ddof=1) / sqrt(n)) if n > 1 else float("nan")
    xo, yo = x[ok], y[ok]
    unpaired_se = float(sqrt(xo.var(ddof=1) / n + yo.var(ddof=1) / n)) if n > 1 else float("nan")
    t = float(d.mean() / paired_se) if paired_se and paired_se > 0 else float("nan")
    return PairedResult(
        n=n, mean=float(d.mean()), paired_se=paired_se, t=t, unpaired_se=unpaired_se,
        zeros=int(np.count_nonzero(d == 0.0)), positive=int(np.count_nonzero(d > 0)), negative=int(np.count_nonzero(d < 0)),
        perm_p=_perm_p(d, draws, np.random.default_rng(seed)), sign_p=_sign_p(int(np.count_nonzero(d > 0)), int(np.count_nonzero(d < 0))),
        diffs=[float(v) for v in d],
    )


def difference_of_differences(first: PairedResult, second: PairedResult, draws: int = 20000, seed: int = 0) -> PairedResult:
    """Is one champion's lesion effect separable from another's?

    Paper 6's claim about the RBT-21 pair is not that either Pioneer is
    individually nose-dependent; it is that the two effects have opposite sign
    and can be told apart.  That is this contrast, and the two samples are
    independent (different individuals), so the error term adds rather than
    pairs.  The result is returned in the same shape for reporting, with
    `diffs` empty because there is no per-seed pairing between two individuals.
    """
    d1, d2 = np.asarray(first.diffs, dtype=float), np.asarray(second.diffs, dtype=float)
    if len(d1) == 0 or len(d2) == 0:
        return PairedResult(0, float("nan"), float("nan"), float("nan"), float("nan"), 0, 0, 0, 1.0, 1.0, [])
    mean = float(d1.mean() - d2.mean())
    se = float(sqrt(d1.var(ddof=1) / len(d1) + d2.var(ddof=1) / len(d2)))
    t = float(mean / se) if se > 0 else float("nan")
    rng = np.random.default_rng(seed)
    pool = np.concatenate([d1, d2])
    k = len(d1)
    null = np.empty(draws)
    for i in range(draws):  # label-shuffle null: which individual a difference came from
        p = rng.permutation(pool)
        null[i] = abs(p[:k].mean() - p[k:].mean())
    perm_p = float((np.count_nonzero(null >= abs(mean) - 1e-12) + 1) / (draws + 1))
    return PairedResult(n=len(d1) + len(d2), mean=mean, paired_se=se, t=t, unpaired_se=se, zeros=0,
                        positive=0, negative=0, perm_p=perm_p, sign_p=float("nan"), diffs=[])


def ci95(result: PairedResult) -> tuple:
    """Normal-approximation 95% interval on the mean difference."""
    if not np.isfinite(result.paired_se):
        return (float("nan"), float("nan"))
    return (result.mean - 1.96 * result.paired_se, result.mean + 1.96 * result.paired_se)
