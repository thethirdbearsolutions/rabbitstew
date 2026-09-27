"""RBT-120 power model (PREREGISTRATION.md §6), BOUNDED by each body's floor and ceiling (RBT-113's lesson, ruling §5).

    power.py > power.txt      (needs counterfactual.json; reads RBT-113's tracked O and Z lineage and decompose.json)

No unbounded Gaussian: every expected per-seed response is RBT-113's observed per-seed response scaled by a factor
that is bounded by physics measured on RBT-113's own bodies, and the noise is RBT-113's own replicate noise.

Per seed s (holistic, raw yield per generation), from RBT-113's default-operator (O, salt 0) seed directory:
  b_up_O, b_down_O, final U - C and C - D (lineage means), and from decompose.json (4 fixed draws) the D line's food,
  work and net and the C line's net.
The budget's effect is bounded on each half:
  up half   rho_up = (U - C) under the budget / (U - C) registered, from counterfactual.py (the U line's final genomes
            re-scored under the budget); the U line is mostly within the budget already (options.txt).
  down half the D line's final work W is bounded ABOVE by the budgeted ceiling: a body exactly at the cap has a
            free-spin ceiling of 0.972 x (1.77 / 1.7605) x M / 15.3367 yield (0.977 at the mass budget), and a line of
            ghost rotors (RBT-121 audit A, A2: 83% of the D line's work is on children spinning inside their parents,
            unobstructed) burns 99% of its ceiling (audit A's S1: 1.44 of 1.46, 16.5 of 16.7); so W_hi = min(W_O,
            0.99 x ceiling at the D line's own mass).  It is bounded BELOW by the counterfactual: the D line's own final genomes re-scored under
            the budget (W_cf), a line that found its motors without a budget and lost them at once.  Food is the O
            line's.  rho_down = (C_net - D_food + W) / (C - D registered), W in {W_cf (floor), W_hi (ceiling)}.
  E[b_div_B] = rho_up b_up_O + rho_down b_down_O, and likewise the final U - D for Q3.
Noise: one holistic replicate's deviation, drawn with a random sign from RBT-113's own replicate pairs, (O - Z) / sqrt 2
at each seed (the salt-0 and salt-1 lines at one seed are independent holistic replicates; B shares O's founders, so
this overstates B's noise: conservative).  The designed side is fixed: its B lines ARE the O lines (K2).
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import budget as B  # noqa: E402

ro = B.ro
RNG = np.random.default_rng(120)
SIMS = 2000
DESIGNED_CEILING = 0.972          # the designed body's free-spin ceiling (yield per season; probe_gear.txt, motors.py)
CAP_PER_KG = DESIGNED_CEILING * B.MOTOR_BUDGET / (108.0 / (4 * 15.33666)) / 15.33666  # free-spin ceiling per kg at the cap
REACH = 0.99  # ghost rotors burn 99% of their free-spin ceiling (RBT-121 audit A, probe_synthetic S1); the designed D line 95%
SEEDS = list(range(1, 13))
SIGNS = np.array(list(itertools.product((1.0, -1.0), repeat=12)))  # exact sign-flip at n = 12


def o_dir(s):
    return os.path.join(ROOT, "runs", "RBT-113", f"O{(s - 1) // 3 + 1}", str(s))


def z_dir(s):
    return os.path.join(ROOT, "runs", "RBT-113", f"Z{(s - 1) // 3 + 1}", f"Z{s}")


def per_seed():
    cf = json.load(open(os.path.join(HERE, "counterfactual.json")))
    rows = {}
    for s in SEEDS:
        _, so, *_ = B.stats(o_dir(s))
        _, sz, *_ = B.stats(z_dir(s))
        dec = json.load(open(os.path.join(o_dir(s), "decompose.json")))["faunae"]["holistic"]
        c = cf[str(s)]
        W_O, W_cf = dec["D"]["work"], c["D"]["work"]
        W_hi = min(W_O, REACH * CAP_PER_KG * c["D"]["mass"])
        W_lo = min(W_cf, W_hi)
        CD_O = dec["C"]["net"] - dec["D"]["net"]
        UC_O = dec["U"]["net"] - dec["C"]["net"]
        UC_cf = c["U"]["net"] - c["C"]["net"]
        rho_up = float(np.clip(UC_cf / UC_O, 0.0, 1.5)) if UC_O > 1e-6 else 1.0
        rho = {k: (dec["C"]["net"] - dec["D"]["food"] + W) / CD_O for k, W in (("floor", W_lo), ("ceiling", W_hi))}
        h, zh = so["holistic"], sz["holistic"]
        d = so["conventional"]
        rows[s] = {"b_up": h["b_up"], "b_down": h["b_down"], "b_div": h["b_div"], "UC": h["UC"], "CD": h["CD"],
                   "rho_up": rho_up, "rho": rho, "W_O": W_O, "W_cf": W_cf, "W_hi": W_hi,
                   "noise_b": (h["b_div"] - zh["b_div"]) / np.sqrt(2), "noise_UD": ((h["UC"] + h["CD"]) - (zh["UC"] + zh["CD"])) / np.sqrt(2),
                   "UD_des": d["UC"] + d["CD"],
                   "noise_c": (h["Cdrift"] - zh["Cdrift"]) / np.sqrt(2)}
    # the C-line drift (RBT-117's control): holistic minus designed, from the lineage, and its replicate noise
    import importlib.util
    spec = importlib.util.spec_from_file_location("rbt117_compare_p", os.path.join(ROOT, "runs", "RBT-117", "compare.py"))
    cmp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cmp)
    for s in SEEDS:
        _, st, *_ = cmp.per_seed(o_dir(s))
        rows[s]["c"] = st["holistic"]["Cdrift"] - st["conventional"]["Cdrift"]
        rows[s]["UD_des"] = st["conventional"]["D"]
        rows[s]["UD_hol"] = st["holistic"]["D"]
    return rows


def sign_flip_p_batch(V):
    """Exact two-sided sign-flip p for each row of V (sims x 12)."""
    obs = np.abs(V.mean(axis=1))
    null = np.abs(V @ SIGNS.T / V.shape[1])
    return (null >= obs[:, None] - 1e-12).mean(axis=1)


def t_ci_batch(V):
    m = V.mean(axis=1)
    se = V.std(axis=1, ddof=1) / np.sqrt(V.shape[1])
    q = ro.T975[V.shape[1] - 2]
    return m, m - q * se, m + q * se


def noise(rows, key):
    pool = np.array([rows[s][key] for s in SEEDS])
    return RNG.choice((1.0, -1.0), size=(SIMS, 12)) * RNG.choice(pool, size=(SIMS, 12))


def verdicts(E_B, rows, sig=B.SIGMA0_REF):
    bO = np.array([rows[s]["b_div"] for s in SEEDS])
    bB = E_B[None, :] + noise(rows, "noise_b")
    s1 = bB / sig
    m1, lo1, hi1 = t_ci_batch(s1)
    p1 = sign_flip_p_batch(s1)
    q1 = {"RESPONDS": np.mean((lo1 > 0) & (p1 < 0.05)), "NO RESPONSE": np.mean(~((lo1 > 0) & (p1 < 0.05)) & (hi1 < B.MDE))}
    q1["INCONCLUSIVE"] = 1 - q1["RESPONDS"] - q1["NO RESPONSE"]
    s2 = (bO[None, :] - bB) / sig
    m2, lo2, hi2 = t_ci_batch(s2)
    p2 = sign_flip_p_batch(s2)
    low = (lo2 > 0) & (p2 < 0.05)
    rai = (hi2 < 0) & (p2 < 0.05)
    same = ~low & ~rai & (lo2 > -B.MARGIN) & (hi2 < B.MARGIN)
    q2 = {"LOWERS": low.mean(), "RAISES": rai.mean(), "NO CHANGE": same.mean(), "INCONCLUSIVE": 1 - low.mean() - rai.mean() - same.mean()}
    return m1.mean() * sig, q1, m2.mean() * sig, q2


def q3(E_UD, rows):
    """RBT-117's decide() on d = (U - D)_hol,B - (U - D)_des, with its C-line VOID (C_BOUND 0.8)."""
    des = np.array([rows[s]["UD_des"] for s in SEEDS])
    d = E_UD[None, :] + noise(rows, "noise_UD") - des[None, :]
    c = np.array([rows[s]["c"] for s in SEEDS])[None, :] + noise(rows, "noise_c")  # the holistic C line is a new replicate
    p = sign_flip_p_batch(d)
    pc = sign_flip_p_batch(c)
    void = (pc < 0.05) & (np.abs(c.mean(axis=1)) >= 0.8)
    hol = (p < 0.05) & (d.mean(axis=1) > 0) & ~void
    des_ = (p < 0.05) & (d.mean(axis=1) < 0) & ~void
    return d.mean(), {"HOLISTIC": hol.mean(), "DESIGNED": des_.mean(), "NOT DECIDED": 1 - hol.mean() - des_.mean() - void.mean(), "VOID": void.mean()}


def main():
    rows = per_seed()
    print("# RBT-120 power model (runs/RBT-120/power.py): bounded by each body's floor and ceiling; noise = RBT-113's own "
          f"replicate pairs; {SIMS} simulated reruns per scenario; exact sign-flip at n = 12")
    print(f"# budgeted ceiling at the cap: {CAP_PER_KG:.4f} yield per kg ({CAP_PER_KG * 15.34:.3f} at the mass budget); reach "
          f"{REACH} (ghost rotors) -> W_hi = min(W_O, {REACH} x ceiling at the D line's mass); frozen sigma0 {B.SIGMA0_REF:.4f}")
    print("\n## per seed (holistic, O = RBT-113 salt 0): D-line work registered W_O, counterfactual under the budget W_cf, "
          "bounded ceiling W_hi; rho_up; rho_down floor/ceiling; b_up_O, b_down_O (raw per generation)")
    for s in SEEDS:
        r = rows[s]
        print(f"  {s:3d}  W_O {r['W_O']:.3f}  W_cf {r['W_cf']:.3f}  W_hi {r['W_hi']:.3f}  rho_up {r['rho_up']:.2f}  "
              f"rho_down {r['rho']['floor']:.2f} / {r['rho']['ceiling']:.2f}  b_up_O {r['b_up']:+.4f}  b_down_O {r['b_down']:+.4f}  "
              f"replicate noise b_div {r['noise_b']:+.4f}")
    sd_noise = np.std([rows[s]["noise_b"] for s in SEEDS], ddof=1)
    print(f"  replicate SD of b_div (one replicate): {sd_noise:.4f} raw = {sd_noise / B.SIGMA0_REF:.3f} sigma0")

    scen = {"floor (counterfactual D, the least down response)": "floor", "ceiling (D line reaches the budgeted ceiling)": "ceiling"}
    print("\n## Q1 and Q2 by scenario: expected b_div_B and Delta (raw per generation), verdict probabilities")
    bO = np.mean([rows[s]["b_div"] for s in SEEDS])
    print(f"  O lines (salt 0, observed): b_div {bO:+.4f} raw = {bO / B.SIGMA0_REF:+.3f} sigma0")
    for lab, k in scen.items():
        E = np.array([rows[s]["rho_up"] * rows[s]["b_up"] + rows[s]["rho"][k] * rows[s]["b_down"] for s in SEEDS])
        m1, q1v, m2, q2v = verdicts(E, rows)
        print(f"  {lab}\n    E b_div_B {E.mean():+.4f} ({E.mean() / B.SIGMA0_REF:+.3f} sigma0; {E.mean() / bO:.0%} of O)   Q1 "
              + "  ".join(f"{a} {b:.3f}" for a, b in q1v.items())
              + f"\n    E Delta {bO - E.mean():+.4f} ({(bO - E.mean()) / B.SIGMA0_REF:+.3f} sigma0)   Q2 " + "  ".join(f"{a} {b:.3f}" for a, b in q2v.items()))

    print("\n## Q2's level and sensitivity: rho_up = 1 and a uniform rho_down (1 = the budget changes nothing)")
    for rd in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4):
        E = np.array([rows[s]["b_up"] + rd * rows[s]["b_down"] for s in SEEDS])
        _, q1v, _, q2v = verdicts(E, rows)
        print(f"  rho_down {rd:.1f}: E Delta {(bO - E.mean()) / B.SIGMA0_REF:+.3f} sigma0   Q2 " + "  ".join(f"{a} {b:.3f}" for a, b in q2v.items())
              + f"   Q1 RESPONDS {q1v['RESPONDS']:.3f}")
    _, q1v, _, _ = verdicts(np.zeros(12), rows)
    print(f"  Q1's level: no response at all (E b_div_B = 0): RESPONDS {q1v['RESPONDS']:.3f}  NO RESPONSE {q1v['NO RESPONSE']:.3f}")

    print("\n## Q3 (RBT-117's compare.py on the B arms): d = (U - D)_hol,B - (U - D)_des, final generation, raw")
    des = np.mean([rows[s]["UD_des"] for s in SEEDS])
    hol = np.mean([rows[s]["UD_hol"] for s in SEEDS])
    print(f"  observed (RBT-117): holistic U - D {hol:+.3f}, designed {des:+.3f}, d {hol - des:+.3f}; C-line control c "
          f"{np.mean([rows[s]['c'] for s in SEEDS]):+.3f}; the holistic C line under the budget is a new replicate, so c carries replicate noise (O - Z)/sqrt 2")
    for lab, k in scen.items():
        E_UD = np.array([rows[s]["rho_up"] * rows[s]["UC"] + rows[s]["rho"][k] * rows[s]["CD"] for s in SEEDS])
        dm, v = q3(E_UD, rows)
        print(f"  {lab}\n    E d {dm:+.3f}   " + "  ".join(f"{a} {b:.3f}" for a, b in v.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
