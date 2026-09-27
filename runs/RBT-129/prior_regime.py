"""RBT-129 r2: how many Stage-1 points to expect RESOLVING under the committed shuffle (coordinator, 22:56).
DESIGN ONLY; arithmetic on committed numbers, no simulator.

Per Stage-1 point, each fauna's season net n_F = food_F(c, L) - p * kJ_F, from RBT-118's restores (levers-flat.txt,
relate.txt; living members, season 599 medians): random terrain (c 1) H food 1.25, kJ 5.18; D food 1.49, kJ 19.84; flat
(c 0) H 1.39 / 5.53, D 2.15 / 20.03.  Food is linear in c, extrapolated to c 2 and floored at 0.3 of its c-1 value.
Layout multiplies food by the kinematic blind-forager ratio (auditor C, probe_proposal.txt: HP 0.90/0.81 = 1.11,
PW 0.59/0.81 = 0.73); those are C-model numbers (RBT-116 adversary M5) and are used here only to place points, not as
effects.  Smell does not change blind income.

Two fairness scenarios bound the work bills, which the fairness set will move: 'pre' (as measured) and 'fair' (the
designed bill halved by effector_bias_sigma, the holistic bill x0.8 by the ranges and the motor budget).

A fauna with n_F < 0.25 (the living cost) is expected to starve out (EXCLUDED/PARTIAL: no share call).  Otherwise the
point's resident gross income is g0 = mean_F(n_F) + 0.35 in the replica's units (power.py), and under the committed
shuffle it is RESOLVING when g0 <= 0.65 at n 8 and g0 <= 0.80 at n 16 (power.txt section 5).
"""
import itertools

FOOD = {"H": (1.39, 1.25), "D": (2.15, 1.49)}  # (c 0, c 1)
KJ = {"H": (5.53, 5.18), "D": (20.03, 19.84)}
LAYOUT = {"U": 1.0, "HP": 1.11, "PW": 0.73}
SCEN = {"pre": {"H": 1.0, "D": 1.0}, "fair": {"H": 0.8, "D": 0.5}}
COST = 0.25


def food(f, c, L):
    f0, f1 = FOOD[f]
    v = f0 + (f1 - f0) * c
    return max(v, 0.3 * f1) * LAYOUT[L]


def kj(f, c, scen):
    k0, k1 = KJ[f]
    return (k0 + (k1 - k0) * min(c, 1)) * SCEN[scen][f]


def main():
    points = [(c, p, L, "G") for c, p, L in itertools.product((0, 1, 2), (0.01, 0.03, 0.08), ("U", "HP", "PW"))]
    points += [(1, p, L, "L") for p, L in itertools.product((0.01, 0.03, 0.08), ("U", "HP", "PW"))]
    for scen in SCEN:
        print(f"## scenario {scen}: work bills H x{SCEN[scen]['H']}, D x{SCEN[scen]['D']}")
        print("   point            n_H    n_D   g0    call")
        counts = {"EXCL": 0, "R8": 0, "R16": 0, "SAT": 0}
        for c, p, L, s in points:
            n = {f: food(f, c, L) - p * kj(f, c, scen) for f in "HD"}
            excl = [f for f in "HD" if n[f] < COST]
            g0 = (n["H"] + n["D"]) / 2 + 0.35
            if excl:
                call = "EXCLUDED/PARTIAL-" + ("D" if excl == ["H"] else "H" if excl == ["D"] else "neither")
                counts["EXCL"] += 1
            elif g0 <= 0.65:
                call, _ = "RESOLVING n8", counts.__setitem__("R8", counts["R8"] + 1)
            elif g0 <= 0.80:
                call, _ = "RESOLVING n16 only", counts.__setitem__("R16", counts["R16"] + 1)
            else:
                call = "SATURATED (share layer)"
                counts["SAT"] += 1
            print(f"   c{c}-p{int(p * 1000):03d}-{L:2s}-{s}  {n['H']:+.2f}  {n['D']:+.2f}  {g0:.2f}  {call}")
        print(f"   of 36: survival call {counts['EXCL']}, RESOLVING at n 8 {counts['R8']}, at n 16 only {counts['R16']},"
              f" SATURATED {counts['SAT']}")
        print()


def budget():
    """The r3 budget (DESIGN.md section 11.2), after the R2-CHECK ruling (R2-S1, R2-M1):
    - M (one-world income column) only at gated points: census g0 <= 1.0, at most 12 Stage-1, 4 Stage-2a, 6 R-B points;
      none at the 3 anchors, whose M/N come from RBT-118 (coordinated seeds);
    - N only where census g0 <= 0.8: at most 4 Stage-1, 2 Stage-2a, 2 R-B points, on half the seeds;
    - retention: R_sel and R_marker at <= 12 fauna-points; readout validation and the erosion table (0.3 core-h a
      point); one matched-erosion re-read (both faunas, both arms) at one point; R_drift optional (+ its own line);
    - lcb:3 descriptive M + N at the 3 anchors, optional."""
    print("## r3 budget (core-h; per-arm-season 20 / 25 core-s; probes 0.46-0.83 a seed)")
    for cs in (20.0, 25.0):
        h = lambda seasons: seasons * cs / 3600.0
        for probes in (0.46, 0.83):
            s_seed = h(300) + probes
            m_seed = h(240)
            n_seed = 0.5 * h(240) * 0.85
            plants = 0.8
            pilot = 4 * 4 * (h(300) + h(240) + h(240) * 0.85 + probes) + 4 * plants
            census = 150 * 3 * h(60) + 18 * 2.5
            s1 = 36 * (8 * s_seed + plants) + 12 * 8 * m_seed + 4 * 8 * n_seed
            ret = 12 * 2 * 8 * h(300) + 12 * 0.3 + 2 * 2 * 8 * h(300)
            drift = 12 * 8 * h(300)
            lcb = 3 * 8 * (m_seed + n_seed)
            s2a = 16 * (8 * s_seed + plants) + 4 * 8 * m_seed + 2 * 8 * n_seed
            s2b = 20 * 8 * s_seed + 6 * 8 * m_seed + 2 * 8 * n_seed
            core = pilot + census + s1 + ret + s2a + s2b
            print(f"  @ {cs:.0f} core-s, probes {probes:.2f}: P {pilot:4.0f} | 0 {census:4.0f} | 1 {s1:5.0f} | R {ret:4.0f}"
                  f" | 2a <= {s2a:4.0f} | 2b <= {s2b:4.0f} | total <= {core:5.0f} (wall about {core / 40:.0f} h)"
                  f" | optional: R_drift {drift:3.0f}, lcb:3 {lcb:3.0f}")
    print("  (r2's budget with M and N at every gated point and the anchors: 2,243-2,931; ungated: power.txt section 4.)")


if __name__ == "__main__":
    main()
    budget()
