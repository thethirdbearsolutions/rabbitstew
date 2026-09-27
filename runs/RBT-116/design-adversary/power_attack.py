"""RBT-116 design adversary: the design's own power model (runs/RBT-116/power.py @ 62fbc97), attacked.

Imports the design's verdict() and statistics unchanged, and changes only the per-unit generator:
  eps_u / eps_n   false-STEERS rates in the U and N lines separately (the design assumes one EPS for both;
                  its own §10.4 says N, selected under a decoy, may shed nose use and sit below U's rate)
  q               the plateau share after a crossing (the design fixes 0.5; hold.py gives 0.01-0.8)
  outlier         one unit whose U line reads share `outlier` at every probe (an artefact or a lucky seed)
python3 runs/RBT-116/design-adversary/power_attack.py [path/to/power.py] > power_attack.txt
"""
import importlib.util
import random
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-116/power.py"
spec = importlib.util.spec_from_file_location("pw", path)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)


def unit(p, Q, rng, eps_u, eps_n, fixed=None):
    cross = rng.random() < p
    tc = rng.uniform(0, P.G) if cross else None
    a = []
    for t in P.T_PROBE:
        q = eps_u
        if cross and t > tc:
            q = max(eps_u, Q * min(1.0, (t - tc) / P.TAU))
        if fixed is not None:
            q = fixed
        u, nn = P.share(q, rng), P.share(eps_n, rng)
        a.append(u - nn)
    return sum(a) / len(a), (u >= P.CROSS_SHARE and u - nn >= P.CROSS_SHARE)


# label, (pH, QH, eps_uH, eps_nH), (pP, QP, eps_uP, eps_nP), outlier share for one holistic unit or None
SC = [
    ("design null (0.04/0.04, EPS 0.02 both)", (0.04, .5, .02, .02), (0.04, .5, .02, .02), None),
    ("null; holistic N sheds noses: EPS_U .04, EPS_N .01", (0.04, .5, .04, .01), (0.04, .5, .02, .02), None),
    ("null; holistic EPS_U .05 (G4 cap), EPS_N .01", (0.04, .5, .05, .01), (0.04, .5, .02, .02), None),
    ("null; holistic EPS_U .08, EPS_N .01", (0.04, .5, .08, .01), (0.04, .5, .02, .02), None),
    ("null + ONE holistic unit reads 0.75 throughout", (0.04, .5, .02, .02), (0.04, .5, .02, .02), 0.75),
    ("null + ONE holistic unit reads 1.0 throughout", (0.04, .5, .02, .02), (0.04, .5, .02, .02), 1.0),
    ("every holistic line plateaus at 0.15 (never 'crosses')", (1.0, .15, .02, .02), (0.04, .5, .02, .02), None),
    ("every holistic line plateaus at 0.20", (1.0, .20, .02, .02), (0.04, .5, .02, .02), None),
    ("bypass p .5 but plateau Q .12 (hold.py, u .28)", (0.5, .12, .02, .02), (0.04, .5, .02, .02), None),
    ("bypass p .5, Q .3 (hold.py, D8 u .146 cx .5)", (0.5, .3, .02, .02), (0.04, .5, .02, .02), None),
    ("weak bypass p .25, Q .3", (0.25, .3, .02, .02), (0.04, .5, .02, .02), None),
]


def main():
    rng = random.Random(1160)
    reps, n = 300, 24
    print(f"# power_attack.py on {path}: n = {n}, {reps} readouts per row; verdict() is the design's own")
    print("scenario".ljust(56) + "".join(v.split(" (")[0][:12].rjust(14) for v in P.VERDICTS) + "   HOL&NEITHER-both-true")
    for lab, h, pp, out in SC:
        cnt = dict.fromkeys(P.VERDICTS, 0)
        both = 0
        for _ in range(reps):
            UH = [unit(h[0], h[1], rng, h[2], h[3]) for _ in range(n)]
            if out is not None:
                UH[0] = unit(0, 0, rng, h[2], h[3], fixed=out)
            UP = [unit(pp[0], pp[1], rng, pp[2], pp[3]) for _ in range(n)]
            v = P.verdict(UH, UP, rng)
            cnt[v] += 1
            kH, kP = sum(u[1] for u in UH), sum(u[1] for u in UP)
            if v.startswith("HOLISTIC") and P.binom_upper(kH, n) < P.P_FLOOR and P.binom_upper(kP, n) < P.P_FLOOR:
                both += 1
        print(lab.ljust(56) + "".join(f"{cnt[v] / reps:14.3f}" for v in P.VERDICTS) + f"   {both / reps:.3f}", flush=True)


if __name__ == "__main__":
    main()


def verdict_crossing(UH, UP, rng):
    """The design's verdict, except that HOLISTIC (PIONEER) also needs the crossed-line count to beat the other
    fauna's on paired units: an exact one-sided sign test on discordant units (H crossed, P not: b; P crossed,
    H not: c), P(X >= b | b + c, 1/2) < 0.05.  Failing that, the readout falls through to the later verdicts."""
    import math
    v = P.verdict(UH, UP, rng)
    b = sum(1 for h, p in zip(UH, UP) if h[1] and not p[1])
    c = sum(1 for h, p in zip(UH, UP) if p[1] and not h[1])

    def tail(k, n):
        return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0
    if v.startswith("HOLISTIC") and tail(b, b + c) >= 0.05 or v.startswith("PIONEER") and tail(c, b + c) >= 0.05:
        kH, kP, n = sum(u[1] for u in UH), sum(u[1] for u in UP), len(UH)
        if P.binom_upper(kH, n) < P.P_FLOOR and P.binom_upper(kP, n) < P.P_FLOOR:
            return "NEITHER CROSSES"
        return "INCONCLUSIVE"
    return v


def cures():
    """Cheaper cures for the weak spot than G = 72 or 36 units: probe more members (probing is ~8% of an arm's
    CPU), and a confirmation battery (a STEERS call must repeat on 16 fresh draws: EPS -> ~EPS^2, sensitivity
    x ~0.6-0.9), which lets CROSS_SHARE drop.  Same verdict code; only M, EPS, CROSS_SHARE and plateau Q move."""
    rng = random.Random(1161)
    reps, n = 300, 24
    base = (P.M, P.EPS, P.CROSS_SHARE)
    rows = [
        ("design as registered (M16, EPS .02, CROSS .25)", 16, .02, .25, 1.0),
        ("M = 40 (probe every member)", 40, .02, .25, 1.0),
        ("M = 40, confirmation (EPS .002, sens x .75), CROSS .125", 40, .002, .125, .75),
    ]
    scen = [("null (0.04/0.04)", .04, .04, .5), ("weak bypass p .25, Q .5", .25, .04, .5),
            ("weak bypass p .25, Q .3", .25, .04, .3), ("bypass p .5, Q .15", .5, .04, .15),
            ("null; holistic EPS_U x2.5 vs EPS_N x0.5", None, None, None)]
    print("\n## Cures (n = 24; columns P(HOLISTIC), P(NEITHER), P(INCONCL))")
    rows.append(("... and MUST 8: HOLISTIC/PIONEER also need an exact paired test on crossed lines", 40, .002, .125, .75))
    for lab, m, eps, cs, sens in rows:
        vfun = verdict_crossing if lab.startswith("... and MUST 8") else P.verdict
        P.M, P.EPS, P.CROSS_SHARE = m, eps, cs
        out = []
        for sl, pH, pP, Q in scen:
            cnt = dict.fromkeys(P.VERDICTS, 0)
            for _ in range(reps):
                if pH is None:
                    UH = [unit(0.04, .5 * sens, rng, eps * 2.5, eps * 0.5) for _ in range(n)]
                    UP = [unit(0.04, .5 * sens, rng, eps, eps) for _ in range(n)]
                else:
                    UH = [unit(pH, Q * sens, rng, eps, eps) for _ in range(n)]
                    UP = [unit(pP, .5 * sens, rng, eps, eps) for _ in range(n)]
                cnt[vfun(UH, UP, rng)] += 1
            out.append(f"{sl}: {cnt[P.VERDICTS[0]] / reps:.2f}/{cnt[P.VERDICTS[2]] / reps:.2f}/{cnt[P.VERDICTS[4]] / reps:.2f}")
        print(f"{lab}\n    " + "\n    ".join(out), flush=True)
    P.M, P.EPS, P.CROSS_SHARE = base


if __name__ == "__main__":
    cures()
