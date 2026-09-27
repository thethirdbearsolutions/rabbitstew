"""RBT-111 design adversary: the exact within-seed permutation test for c0, pure Python, and its checks.

Under H0 (the three salt keys exchangeable) a seed's three runs (y_s0, y_s1, y_s2) are exchangeable, so every one
of the 3! labellings per seed is equally likely, whatever the run noise.  c0 = (y_s1 + y_s2)/2 - y_s0 depends only
on WHICH run carries the s0 label (swapping s1 and s2 leaves it unchanged), so the 6^n labellings collapse to 3^n
equally likely values of sum(c0), each counted 2^n times.  At n = 16 that is 3^16 = 43,046,721: enumerated
exactly here by meet in the middle (two halves of 3^8 = 6561 partial sums, one sorted, bisect), no Monte Carlo.

    perm_c0_p(rows) -> (p, count, 3^n)       rows = [(y_s0, y_s1, y_s2), ...]
    perm_c0_ci(rows)                          95% interval for a salt-0 shift, by inverting the same test

python runs/RBT-111/adversary/perm.py  runs the checks below and prints perm.txt.
"""
import bisect
import itertools
import random

ALPHA = 0.05
TOL = 1e-12


def _c0_choices(row):
    """The 3 values c0 can take for one seed as the s0 label moves over its three runs (they sum to 0)."""
    a, b, c = row
    return ((b + c) / 2 - a, (a + c) / 2 - b, (a + b) / 2 - c)


def _half_sums(choices):
    sums = [0.0]
    for ch in choices:
        sums = [s + v for s in sums for v in ch]
    return sums


def _count_extreme(choices, obs):
    """Number of the 3^n label assignments with |sum c0| >= obs - TOL (exact, meet in the middle)."""
    h = len(choices) // 2
    left, right = _half_sums(choices[:h]), sorted(_half_sums(choices[h:]))
    if obs <= TOL:
        return len(left) * len(right)
    n_r, hit = len(right), 0
    for a in left:
        hit += n_r - bisect.bisect_left(right, obs - TOL - a)   # a + b >= obs
        hit += bisect.bisect_right(right, -obs + TOL - a)       # a + b <= -obs
    return hit


def perm_c0_p(rows):
    choices = [_c0_choices(r) for r in rows]
    obs = abs(sum(ch[0] for ch in choices))
    tot = 3 ** len(rows)
    hit = _count_extreme(choices, obs)
    return hit / tot, hit, tot


def perm_c0_ci(rows, alpha=ALPHA, step=0.001):
    """Interval for mu, a shift of s0 by -mu (c0's mean moves by +mu), by inverting perm_c0_p on (y_s0 + mu, y_s1, y_s2).
    Returns (-inf, inf) when even the most extreme assignment has p > alpha (n <= 2), so it always terminates."""
    if 1 / 3 ** len(rows) > alpha:
        return float("-inf"), float("inf")
    m0 = round(sum(_c0_choices(r)[0] for r in rows) / len(rows) / step) * step
    ends = []
    for d in (-1, 1):
        mu = m0
        while perm_c0_p([(r[0] + mu + d * step, r[1], r[2]) for r in rows])[0] > alpha:
            mu += d * step
        ends.append(mu)
    return ends[0], ends[1]


def _brute(rows):
    """6^n labellings by brute force (small n only): the definition, for the check."""
    obs = abs(sum((r[1] + r[2]) / 2 - r[0] for r in rows))
    hit = tot = 0
    for perms in itertools.product(list(itertools.permutations(range(3))), repeat=len(rows)):
        s = sum((r[p[1]] + r[p[2]]) / 2 - r[p[0]] for r, p in zip(rows, perms))
        hit += abs(s) >= obs - TOL
        tot += 1
    return hit / tot


if __name__ == "__main__":
    rng = random.Random(111)
    print("RBT-111 design adversary: exact within-seed permutation test for c0 (perm.py)")
    print("\n1. meet-in-the-middle p against the 6^n brute-force definition (random rows, gaussian + one-sided tail)")
    for n in (1, 2, 3, 4, 5):
        for _ in range(3):
            rows = [tuple(rng.gauss(0, 0.06) + (0.25 if rng.random() < 1 / 16 else 0) for _ in range(3)) for _ in range(n)]
            p, bp = perm_c0_p(rows)[0], _brute(rows)
            assert abs(p - bp) < 1e-12, (n, p, bp)
        print(f"   n = {n}: 3 datasets, equal to 1e-12 (last p = {p:.6f})")
    print("\n2. n = 16: 3^16 enumeration, fixed data, and its Monte Carlo cross-check (1e5 random labellings)")
    rows = [tuple(rng.gauss(0, 0.06) for _ in range(3)) for _ in range(16)]
    rows = [(r[0] - 0.04, r[1], r[2]) for r in rows]
    p, hit, tot = perm_c0_p(rows)
    obs = abs(sum(_c0_choices(r)[0] for r in rows))
    mc = sum(abs(sum(_c0_choices(r)[rng.randrange(3)] for r in rows)) >= obs - TOL for _ in range(100000)) / 100000
    se = (p * (1 - p) / 100000) ** 0.5
    print(f"   exact p = {p:.6f} ({hit}/{tot});  Monte Carlo 1e5: {mc:.6f}, |diff| = {abs(mc - p) / se:.2f} SE")
    lo, hi = perm_c0_ci(rows)
    print(f"   inverted 95% interval for the salt-0 shift: [{lo:+.3f}, {hi:+.3f}]  (true shift +0.040)")
    print("\n3. termination: the interval is (-inf, inf) where no assignment can reach p <= 0.05 (n <= 2)")
    for n in (1, 2, 3, 4):
        print(f"   n = {n}: min attainable p {1 / 3 ** n:.4f}  ->  {tuple(round(v, 3) for v in perm_c0_ci(rows[:n]))}")
    print("\n4. minimum attainable two-sided p: sign-flip 2/2^n (its extremes pair up) against permutation 1/3^n")
    print("   (a far shift makes the observed labelling the unique extreme; the readout's sign_flip_ci walks forever where 2/2^n > 0.05, n <= 5)")
    for n in (1, 2, 3, 4, 5, 6, 12, 16):
        print(f"   n = {n:2d}: sign-flip {2 / 2 ** n:.2e}   permutation {1 / 3 ** n:.2e}")
