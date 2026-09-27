"""RBT-117 power and MDE (PREREGISTRATION.md §4), from committed pre-data material only.

The model is RBT-113's own (runs/RBT-113/power.py `sim_arm`: truncation k = 10 of 40, 24 generations, a world effect
shared per generation, mid-parent inheritance with segregation, optional mutational variance), run once per fauna per
seed in phenotypic-SD units and scaled to raw net yield by that fauna's founder SD from RBT-113's pilot
(runs/RBT-113/pilot.txt, D = 2 draws: holistic 0.1362, designed body 0.7086).  The designed body's h2 is the pilot's
child-on-parent slope, 0.43 (CI 0.12 to 0.70); the holistic founders' yield h2 is not identified by the pilot (slope
-0.06, CI -2.5 to +1.1), so it is swept.  RBT-113's committed ecology estimates (h2_committed.txt, r 0.34-0.40) are
of a different quantity and are not used as h2 here.

For each scenario: the per-seed SD of the paired difference d = D_holistic - D_designed (final-generation U - D
divergence, raw), its expected mean, and the MDE at 80% power for the exact two-sided sign-flip test at 12 seeds,
found by shifting the simulated centred differences by delta and applying compare.decide (4096 patterns).

    power.py [SIMS]  > power.txt
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import power as p113  # noqa: E402

sys.path.insert(0, HERE)
import compare  # noqa: E402

SIG = {"holistic": 0.1362, "designed": 0.7086}  # pilot.txt yield SDs, D = 2
H2_DESIGNED = 0.43
N_SEEDS = 12


def seed_diffs(h2_hol, rng, sims, vm=0.0):
    """Per-seed final divergences (raw) of each fauna, and their paired difference."""
    dh = np.array([p113.sim_arm(h2_hol, rng, vm=vm)["div_end"] for _ in range(sims)]) * SIG["holistic"]
    dd = np.array([p113.sim_arm(H2_DESIGNED, rng, vm=vm)["div_end"] for _ in range(sims)]) * SIG["designed"]
    return dh, dd


def power_at(centred, delta, rng, reps):
    hits = 0
    for _ in range(reps):
        d = rng.choice(centred, N_SEEDS) + delta
        v, _ = compare.decide(d, np.zeros(N_SEEDS))
        hits += v == compare.VERDICTS[0]
    return hits / reps


def main(sims=600, reps=300):
    rng = np.random.default_rng(117)
    print(f"# RBT-117 power: {N_SEEDS} paired seeds, exact sign-flip, alpha {compare.ALPHA}; RBT-113's sim_arm, "
          f"{sims} simulated seeds per fauna per row, {reps} benchmarks per power point")
    print(f"# raw scale from pilot.txt: holistic founder SD {SIG['holistic']}, designed {SIG['designed']}; designed h2 {H2_DESIGNED}")
    print(f"{'h2 hol':>6s} {'V_m':>5s} {'E[D_hol]':>9s} {'E[D_des]':>9s} {'E[d]':>9s} {'SD(d)/seed':>10s} "
          f"{'MDE80 (raw)':>11s} {'power@MDE':>9s} {'P(HOL|E[d])':>11s} {'P(DES|E[d])':>11s}")
    for h2h in (0.05, 0.2, 0.43, 0.8):
        for vm in (0.0, 0.01):
            dh, dd = seed_diffs(h2h, rng, sims, vm)
            d = dh - dd
            cen = d - d.mean()
            s = d.std(ddof=1)
            # MDE: the smallest delta on a grid of s/sqrt(n) steps with power >= 0.8
            mde, pw = None, None
            for k in np.arange(0.5, 6.01, 0.25):
                delta = k * s / np.sqrt(N_SEEDS)
                pw = power_at(cen, delta, rng, reps)
                if pw >= 0.8:
                    mde = delta
                    break
            # what the model itself predicts: power of each verdict at the modelled mean difference
            ph = power_at(cen, d.mean(), rng, reps)
            pd = 0.0
            for _ in range(reps):
                v, _ = compare.decide(rng.choice(cen, N_SEEDS) + d.mean(), np.zeros(N_SEEDS))
                pd += v == compare.VERDICTS[1]
            print(f"{h2h:6.2f} {vm:5.2f} {dh.mean():+9.4f} {dd.mean():+9.4f} {d.mean():+9.4f} {s:10.4f} "
                  f"{(mde if mde is not None else float('nan')):11.4f} {pw:9.2f} {ph:11.2f} {pd / reps:11.2f}")
    # the control rule (§5): with the model's mutational bias (-0.02 sigma0 per generation on every line, in each
    # fauna's own SD) the C-line drift differs between faunas by construction; how often does each rule VOID?
    lit = mine = 0
    for _ in range(reps):
        ch = np.array([p113.sim_arm(0.2, rng)["b_C"] for _ in range(N_SEEDS)]) * (p113.G - 1) * SIG["holistic"]
        cd = np.array([p113.sim_arm(H2_DESIGNED, rng)["b_C"] for _ in range(N_SEEDS)]) * (p113.G - 1) * SIG["designed"]
        dd = np.array([p113.sim_arm(0.2, rng)["div_end"] * SIG["holistic"] - p113.sim_arm(H2_DESIGNED, rng)["div_end"] * SIG["designed"] for _ in range(N_SEEDS)])
        c = ch - cd
        lit += compare.ro.sign_flip_p(c) < compare.ALPHA
        mine += compare.decide(dd, c)[0] == "VOID"
    print(f"\n# control, model with mutational bias, holistic h2 0.2: P(literal 'VOID if the C lines differ') = {lit / reps:.3f}; "
          f"P(VOID under the registered rule, significant AND >= {compare.CONTROL_FRACTION} x |d|) = {mine / reps:.3f}")
    # the null: both faunas identical in the model's raw terms (same SD, same h2) -> the false-positive rate
    fp = 0
    for _ in range(reps):
        a = np.array([p113.sim_arm(0.2, rng)["div_end"] for _ in range(N_SEEDS)])
        b = np.array([p113.sim_arm(0.2, rng)["div_end"] for _ in range(N_SEEDS)])
        v, _ = compare.decide(a - b, np.zeros(N_SEEDS))
        fp += v != compare.VERDICTS[2]
    print(f"\n# null (both faunas the same model, h2 0.2, same SD): P(either directional verdict) = {fp / reps:.3f}")


if __name__ == "__main__":
    main(*(int(x) for x in sys.argv[1:3]))
