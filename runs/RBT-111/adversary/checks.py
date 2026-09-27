"""RBT-111 design adversary: independent checks of readout.py's sign-flip p, Holm and interval inversion.

Own implementations (itertools / meet in the middle), compared with the readout's on random data.
    python runs/RBT-111/adversary/checks.py      -> checks.txt   (pure Python, a few seconds)
"""
import bisect
import importlib.util
import itertools
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ro111", os.path.join(HERE, "..", "readout.py"))
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)


def sf_p(xs):  # meet in the middle over the 2^n sign vectors
    h = len(xs) // 2
    L = [sum(s * x for s, x in zip(sg, xs[:h])) for sg in itertools.product((1, -1), repeat=h)]
    R = sorted(sum(s * x for s, x in zip(sg, xs[h:])) for sg in itertools.product((1, -1), repeat=len(xs) - h))
    obs = abs(sum(xs))
    hit = sum(len(R) - bisect.bisect_left(R, obs - 1e-12 - a) + bisect.bisect_right(R, -obs + 1e-12 - a) for a in L)
    return hit / 2 ** len(xs)


def holm_ref(ps, a=0.05):  # the textbook definition, written out for m = 2
    (k1, p1), (k2, p2) = sorted(ps.items(), key=lambda kv: kv[1])
    r1 = p1 <= a / 2
    r2 = r1 and p2 <= a
    return {k1: (min(1, 2 * p1), r1), k2: (min(1, max(2 * p1, p2)), r2)}


rng = random.Random(4242)
print("RBT-111 design adversary: checks of readout.py (checks.py)")
worst = 0.0
for _ in range(200):
    xs = [rng.gauss(rng.choice((0, 0.03, 0.08)), 0.08) + (0.25 if rng.random() < 1 / 16 else 0) for _ in range(16)]
    worst = max(worst, abs(ro.sign_flip_p(xs)[0] - sf_p(xs)))
print(f"1. sign_flip_p against an independent meet-in-the-middle enumeration, 200 random 16-seed sets: max |diff| = {worst:.1e}")
bad = 0
for _ in range(20000):
    ps = {"c0": rng.random() ** rng.choice((1, 3)), "c12": rng.random() ** rng.choice((1, 3))}
    if ps["c0"] == ps["c12"]:
        continue
    got, ref = ro.holm(ps), holm_ref(ps)
    bad += any(abs(got[k][0] - ref[k][0]) > 1e-15 or got[k][1] != ref[k][1] for k in ps)
print(f"2. holm against the textbook step-down, 20,000 random p pairs: {bad} disagreements")
print("3. sign_flip_ci: at each end, p > 0.05 at the returned end and p <= 0.05 one step (0.001) beyond it")
ok = 0
for i in range(30):
    xs = [rng.gauss(0.04, 0.09) for _ in range(16)]
    lo, hi = ro.sign_flip_ci(xs)
    inside = sf_p([x - lo for x in xs]) > 0.05 and sf_p([x - hi for x in xs]) > 0.05
    beyond = sf_p([x - lo + 0.001 for x in xs]) <= 0.05 and sf_p([x - hi - 0.001 for x in xs]) <= 0.05
    # monotone: no mu outside [lo, hi] (on the grid, within 0.1 beyond) has p > 0.05
    grid_out = [m / 1000 for m in range(round(lo * 1000) - 100, round(lo * 1000))] + [m / 1000 for m in range(round(hi * 1000) + 1, round(hi * 1000) + 100)]
    mono = all(sf_p([x - m for x in xs]) <= 0.05 for m in grid_out[::7])
    ok += inside and beyond and mono
print(f"   30 random 16-seed sets: {ok}/30 pass (ends exact to the 0.001 grid; no accepted mu beyond either end, every 7th grid point to 0.1 out)")
print("4. termination: min attainable sign-flip p is 2/2^n, so sign_flip_ci can only end if 2/2^n <= 0.05, i.e. n >= 6.")
print("   drive.sh calls readout.py per slot with the slot's seeds; from slot 2 on, one seed is complete (n = 1): see synthetic.txt.")
