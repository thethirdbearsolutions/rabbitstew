"""RBT-107: can adaptation to flat ground be seen at ~20 reproduction events?  The registered readout, from committed files.

    python runs/RBT-107/readout.py > runs/RBT-107/readout.txt

Per seed (RBT-92's ten; T from runs/RBT-92/onset.txt) three arms extended to 1200 seasons from their checkpoints
(extend_arm.sh), byte-identical to their committed 600-season selves before 600 (gate V-EXT, prefix.txt):
    B  base    RBT-90 part 2, random terrain throughout                    runs/RBT-107/base-SEED
    S  shift   RBT-101's C4 arm: flat ground from T                        runs/RBT-107/shift-SEED
    N  cull20  RBT-92's cull of 20/20 at T, random terrain throughout      runs/RBT-107/cull20-SEED
and, report-only, RBT-101's k-cull on 801, 1, 2, 4 (runs/RBT-107/cull-SEED) and RBT-105's founder-sharing replicates.

THE COMMON GARDEN (garden.py; rows in runs/RBT-107/garden/).  G_a^w(s) is the mean income per robot-bout of arm a's
fauna alive at season s, on the eight fixed worlds w in {flat, random}, by the ecology's own group bout.  C0 is the fauna
alive at T - 1, the same individuals in every arm (V0).

 0. ARITHMETIC FIRST (pre-onset only): Delta0 = G_C0^flat - G_C0^random.  What flat ground does to the income of an
    UNCHANGED population.  It is the prediction of the paired income step x_S - x_B for a population that never
    responded, and it is the size of the challenge.  Nothing below is read as a response unless it is net of it.
 1. PRIMARY, per fauna, at s* = T + 800 (about 22 reproduction events on the conservative count, depth.txt):
        A_SB = G_S^flat(s*) - G_B^flat(s*)     flat-lived against furniture-lived, both on flat ground
        A_SN = G_S^flat(s*) - G_N^flat(s*)     against the divergence null (same seed, same T, no terrain change)
    Both populations descend from the same C0, so Delta0 cancels: an unchanged pair reads 0 by construction, and a
    pair that only drifted reads the null A_NB = G_N^flat - G_B^flat (printed, the null's own size).
    VERDICT
        ADAPTED      mean A_SB over seeds, t(n-1) 95% interval above 0, AND mean A_SN interval above 0.  Then:
                       SPECIFIC  if the specialisation I = (G_S^flat - G_S^random) - (G_B^flat - G_B^random) also has
                                 its interval above 0: better on flat, relative to furniture, than the furniture-lived;
                       GENERAL   otherwise: the flat-lived fauna is better on both grounds (selection on flat ground
                                 improved foraging in general, or the flat worlds selected harder).
        MALADAPTED   both intervals below 0.
        NOT SEEN     otherwise; printed with the resolution (the smallest A detectable at 80% on the realised null).
        UNREAD       fewer than 6 seeds read for that fauna.
    No sign guard (RBT-101 section 6.3): two intervals against two references stand in for it; sign counts printed.
 2. SECONDARY, the income trajectory (the ticket's example): D_SB(s) = x_S(s) - x_B(s), mean_lifetime_score (an extinct
    fauna earns 0).  Its slope over [T+200, T+800] per 100 seasons, per seed; the null slope from D_NB.
        RISING   slope_SB interval above 0 AND (slope_SB - slope_NB) interval above 0.   FALLING: both below.
    Printed beside it: the residual level mean D_SB over [T+700, T+800) minus Delta0, i.e. the paired income net of the
    arithmetic, and the same over RBT-101's recovery window [T+60, T+160).
 3. Trajectory, printed and not scored: A_SB, A_SN, A_NB and I at T + 200, 400, 600, 800.
Gates, printed first: V-EXT (every arm's prefix.txt PASS), V-G (every garden population is complete: n equals seasons.txt
alive), C0 (the C0 garden is the base arm's; V0 of RBT-92 makes it every arm's), DEPTH (median fewest-births depth of
S at s*; a fauna below 15 events carries "DEPTH SHORT" on its verdict line).

Environment overrides for the smoke test only: RBT107_SEEDS, RBT107_DIR (arms), RBT107_GARDEN (rows), RBT107_DSTAR,
RBT107_READS.
"""
import csv
import glob
import importlib.util
import math
import os
import random
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KINDS = ("holistic", "conventional")
SEEDS = [int(s) for s in os.environ.get("RBT107_SEEDS", "801 804 805 806 807 1 2 3 4 7").split()]
ARMS_DIR = os.environ.get("RBT107_DIR", HERE)
GARDEN = os.environ.get("RBT107_GARDEN", os.path.join(HERE, "garden"))
DSTAR = int(os.environ.get("RBT107_DSTAR", "800"))
READS = [int(x) for x in os.environ.get("RBT107_READS", "200,400,600,800").split(",")]
SLOPE_WIN = (200, DSTAR)
DEPTH_SHORT = 15
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201}
T80 = {4: 0.941, 5: 0.920, 6: 0.906, 7: 0.896, 8: 0.889, 9: 0.883}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R92 = _load("r92", os.path.join(ROOT, "runs", "RBT-92", "readout.py"))
DEPTH = _load("rbt107_depth", os.path.join(HERE, "depth.py"))


def onsets():
    out = {}
    for line in open(os.path.join(ROOT, "runs", "RBT-92", "onset.txt")):
        f = line.split("\t")
        if f[0].isdigit() and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


def ci(v):
    """mean, t(n-1) 95% half-width, positives, n."""
    v = [x for x in v if x is not None and x == x]
    n = len(v)
    if n < 2:
        return (v[0] if v else float("nan")), float("nan"), sum(x > 0 for x in v), n
    m, sd = statistics.fmean(v), statistics.stdev(v)
    return m, T975.get(n - 1, 1.96) * sd / math.sqrt(n), sum(x > 0 for x in v), n


def fmt(v):
    m, hw, pos, n = ci(v)
    return f"{m:+.3f} [{m - hw:+.3f}, {m + hw:+.3f}] {pos}/{n} positive"


def above(v):
    m, hw, _, n = ci(v)
    return n >= 2 and m - hw > 0


def below(v):
    m, hw, _, n = ci(v)
    return n >= 2 and m + hw < 0


def garden(label):
    """{name: (gain_flat, gain_random)} from runs/RBT-107/garden/LABEL.txt, or None."""
    p = os.path.join(GARDEN, f"{label}.txt")
    if not os.path.exists(p):
        return None
    out = {}
    for line in open(p):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        out[f[4]] = (float(f[5]), float(f[6]))
    return out


def G(rows):
    return (statistics.fmean(v[0] for v in rows.values()), statistics.fmean(v[1] for v in rows.values())) if rows else None


def arm_dir(arm, seed):
    return os.path.join(ARMS_DIR, f"{arm}-{seed}")


def income(arm):
    return arm.x


def slope(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def mde(null_ab, n):
    """Smallest true A detected at 80% by the two-interval rule, with per-arm drift sd from the null A_NB spread.

    Under the null each arm's G is mu_seed + e_arm, e iid N(0, s^2), so A_SB and A_SN share e_S (correlation 0.5) and
    var(A_NB) = 2 s^2.  Simulated, 4000 replicates per step, fixed stream."""
    v = [x for x in null_ab if x == x]
    if len(v) < 2 or n < 2:
        return float("nan")
    s = math.sqrt(statistics.fmean(x * x for x in v) / 2)  # RMS about 0: the null's mean is 0 by construction
    rng = random.Random(107)
    for step in range(1, 400):
        d = step * s / 20
        hits = 0
        for _ in range(4000 // 4):
            eS = [rng.gauss(0, s) for _ in range(n)]
            ab = [d + e - rng.gauss(0, s) for e in eS]
            an = [d + e - rng.gauss(0, s) for e in eS]
            hits += above(ab) and above(an)
        if hits / 1000 >= 0.8:
            return d
    return float("inf")


def main():
    print(__doc__.split("\n\n")[0])
    T_of = onsets()
    ok = True
    print("\n== GATES")
    for seed in SEEDS:
        for arm in ("base", "shift", "cull20") + (("cull",) if os.path.exists(arm_dir("cull", seed)) else ()):
            p = os.path.join(arm_dir(arm, seed), "prefix.txt")
            line = [l.strip() for l in open(p) if l.startswith("V-EXT")] if os.path.exists(p) else []
            v = line[-1] if line else "V-EXT MISSING"
            if "PASS" not in v:
                ok = False
            print(f"seed {seed:>4} {arm:6s} {v.split(':')[0]}")
    arms = {}
    for seed in SEEDS:
        for a in ("base", "shift", "cull20", "cull"):
            if os.path.exists(os.path.join(arm_dir(a, seed), "seasons.txt")):
                arms[(a, seed)] = R92.Arm(arm_dir(a, seed))
    vg_bad = []
    for p in sorted(glob.glob(os.path.join(GARDEN, "*.txt"))):
        lab = os.path.basename(p)[:-4]
        f = lab.split("-")
        if f[0] == "c0":
            continue
        if f[0] not in ("base", "shift", "cull20", "cull"):
            continue
        a, seed, kind, d = f[0], int(f[1]), f[2], int(f[3][1:])
        arm = arms.get((a, seed))
        if arm is None:
            vg_bad.append(lab + " (no arm)")
            continue
        n = len(garden(lab))
        if n != arm.alive[kind].get(T_of[seed] + d, -1):
            vg_bad.append(f"{lab} n={n} alive={arm.alive[kind].get(T_of[seed] + d)}")
    print(f"V-G {'PASS' if not vg_bad else 'FAIL'}: garden populations complete" + (f"; {vg_bad[:5]}" if vg_bad else ""))
    ok &= not vg_bad
    print(f"ALL GATES {'PASS' if ok else 'FAIL'}" + ("" if ok else ": nothing below enters a sentence until they pass"))

    print(f"\n== DEPTH at s* = T + {DSTAR} (fewest births back to C0, mean over the living; first-parent median in brackets)")
    depth = {}
    for seed in SEEDS:
        a = arms.get(("shift", seed))
        if a is None or a.last < T_of[seed] + DSTAR:
            continue
        for kind in KINDS:
            m = DEPTH.measures(a, kind, T_of[seed], [T_of[seed] + DSTAR])
            if m:
                fp, few, most = m[T_of[seed] + DSTAR]
                depth[(seed, kind)] = few
                print(f"seed {seed:>4} {kind:12s} few {few:.1f}  [fp {fp:.1f}]  most {most:.1f}")
    for kind in KINDS:
        v = [depth[(s, kind)] for s in SEEDS if (s, kind) in depth]
        if v:
            print(f"DEPTH {kind:12s} median {statistics.median(v):.1f} events (range {min(v):.1f}..{max(v):.1f}, n={len(v)})")

    print("\n== 0. ARITHMETIC: Delta0 = G_C0^flat - G_C0^random, the unchanged population's income step (pre-onset only)")
    d0 = {}
    for kind in KINDS:
        v = []
        for seed in SEEDS:
            g = G(garden(f"c0-{seed}-{kind}"))
            if g:
                d0[(seed, kind)] = g[0] - g[1]
                v.append(g[0] - g[1])
                print(f"seed {seed:>4} {kind:12s} C0 flat {g[0]:+.3f} random {g[1]:+.3f}  Delta0 {g[0] - g[1]:+.3f}")
        print(f"DELTA0 {kind:12s} {fmt(v)}")
    print("DELTA0 paired prediction for R-body shift - base (holistic - conventional): "
          + fmt([d0[(s, 'holistic')] - d0[(s, 'conventional')] for s in SEEDS if (s, 'holistic') in d0 and (s, 'conventional') in d0]))

    print(f"\n== 1. PRIMARY: the common garden at T + d; scored at d = {DSTAR}")
    table = {}
    for kind in KINDS:
        for d in READS:
            for seed in SEEDS:
                g = {a: G(garden(f"{a}-{seed}-{kind}-d{d}")) for a in ("shift", "base", "cull20")}
                if all(g.values()):
                    S, B, N = g["shift"], g["base"], g["cull20"]
                    table[(kind, d, seed)] = dict(SB=S[0] - B[0], SN=S[0] - N[0], NB=N[0] - B[0],
                                                  I=(S[0] - S[1]) - (B[0] - B[1]), IN=(N[0] - N[1]) - (B[0] - B[1]),
                                                  RSB=S[1] - B[1])
    for kind in KINDS:
        print(f"-- {kind}")
        for d in READS:
            rows = [table[(kind, d, s)] for s in SEEDS if (kind, d, s) in table]
            if not rows:
                print(f"  d={d}: no seed read")
                continue
            tag = "  SCORED" if d == DSTAR else ""
            print(f"  d={d:>3} n={len(rows)}  A_SB {fmt([r['SB'] for r in rows])} | A_SN {fmt([r['SN'] for r in rows])} | "
                  f"null A_NB {fmt([r['NB'] for r in rows])} | I {fmt([r['I'] for r in rows])} | I null {fmt([r['IN'] for r in rows])} | "
                  f"random-ground S-B {fmt([r['RSB'] for r in rows])}{tag}")
        rows = [table[(kind, DSTAR, s)] for s in SEEDS if (kind, DSTAR, s) in table]
        n = len(rows)
        res = mde([r["NB"] for r in rows], n)
        for s in SEEDS:
            if (kind, DSTAR, s) in table:
                r = table[(kind, DSTAR, s)]
                print(f"  seed {s:>4}: A_SB {r['SB']:+.3f} A_SN {r['SN']:+.3f} A_NB {r['NB']:+.3f} I {r['I']:+.3f}"
                      + (f"  Delta0 {d0[(s, kind)]:+.3f}" if (s, kind) in d0 else ""))
        sb, sn, ii = [r["SB"] for r in rows], [r["SN"] for r in rows], [r["I"] for r in rows]
        if n < 6:
            v = "UNREAD"
        elif above(sb) and above(sn):
            v = "ADAPTED, " + ("SPECIFIC" if above(ii) else "GENERAL")
        elif below(sb) and below(sn):
            v = "MALADAPTED"
        else:
            v = "NOT SEEN"
        dv = [depth[(s, kind)] for s in SEEDS if (s, kind) in depth]
        short = dv and statistics.median(dv) < DEPTH_SHORT
        dz = [d0[(s, kind)] for s in SEEDS if (s, kind) in d0]
        print(f"VERDICT {kind:12s} {v} at d={DSTAR}, n={n}; resolution: A >= {res:.3f} detected at 80% on the realised null"
              + (f" ({res / abs(statistics.fmean(dz)):.2f} x |Delta0|)" if dz and statistics.fmean(dz) else "")
              + ("; DEPTH SHORT" if short else "") + ("" if ok else "; GATES FAIL: not readable"))

    print(f"\n== 1b. SORTING AGAINST NOVELTY at d={DSTAR}, printed and not scored (approximate: ancestry shares, not an additive model)")
    print("sort_a = the C0 garden values (flat) weighted by each C0 member's share of P_a(s*)'s ancestry (every parent followed,")
    print("each living individual's weight split equally over its C0 ancestors); novelty = (G_S - sort_S) - (G_B - sort_B)")
    for kind in KINDS:
        nov, srt = [], []
        for seed in SEEDS:
            c0rows = garden(f"c0-{seed}-{kind}")
            if not c0rows:
                continue
            T = T_of[seed]
            vals = {}
            for a in ("shift", "base"):
                arm, rows = arms.get((a, seed)), garden(f"{a}-{seed}-{kind}-d{DSTAR}")
                if arm is None or not rows:
                    break
                c0 = arm.alive_at(kind, T - 1)
                w = {}
                for n in arm.alive_at(kind, T + DSTAR):
                    anc = arm.anc0(kind, n, c0)
                    for i in anc:
                        w[i] = w.get(i, 0.0) + 1.0 / len(anc)
                tot = sum(w[i] for i in w if i in c0rows)
                if not tot:
                    break
                vals[a] = (G(rows)[0], sum(w[i] * c0rows[i][0] for i in w if i in c0rows) / tot)
            if len(vals) == 2:
                srt.append(vals["shift"][1] - vals["base"][1])
                nov.append((vals["shift"][0] - vals["shift"][1]) - (vals["base"][0] - vals["base"][1]))
        print(f"{kind:12s} sorting part (sort_S - sort_B) {fmt(srt)} | novelty part {fmt(nov)}")

    print(f"\n== 2. SECONDARY: paired income slope over [T+{SLOPE_WIN[0]}, T+{SLOPE_WIN[1]}], per 100 seasons")
    for kind in KINDS:
        sb, nb, lev, rec = [], [], [], []
        for seed in SEEDS:
            T = T_of[seed]
            S, B, N = (arms.get((a, seed)) for a in ("shift", "base", "cull20"))
            if not (S and B and N) or min(S.last, B.last, N.last) < T + SLOPE_WIN[1]:
                continue
            xs = list(range(T + SLOPE_WIN[0], T + SLOPE_WIN[1] + 1))
            sb.append(100 * slope(xs, [S.x[kind][s] - B.x[kind][s] for s in xs]))
            nb.append(100 * slope(xs, [N.x[kind][s] - B.x[kind][s] for s in xs]))
            if (seed, kind) in d0:
                lev.append(statistics.fmean(S.x[kind][s] - B.x[kind][s] for s in range(T + DSTAR - 100, T + DSTAR)) - d0[(seed, kind)])
                rec.append(statistics.fmean(S.x[kind][s] - B.x[kind][s] for s in range(T + 60, T + 160)) - d0[(seed, kind)])
        diff = [a - b for a, b in zip(sb, nb)]
        v = "RISING" if above(sb) and above(diff) else "FALLING" if below(sb) and below(diff) else "FLAT (not resolved)"
        if len(sb) < 6:
            v = "UNREAD"
        print(f"{kind:12s} slope D_SB {fmt(sb)} | null D_NB {fmt(nb)} | SB - NB {fmt(diff)}")
        print(f"{kind:12s} residual level (D_SB - Delta0) over [T+{DSTAR - 100}, T+{DSTAR}) {fmt(lev)}; over [T+60, T+160) {fmt(rec)}")
        print(f"INCOME {kind:12s} {v}")

    print("\n== NULLS, report only")
    for seed in SEEDS:
        c, b = arms.get(("cull", seed)), arms.get(("base", seed))
        if c and b:
            for kind in KINDS:
                g = [G(garden(f"{a}-{seed}-{kind}-d{DSTAR}")) for a in ("cull", "base")]
                if all(g):
                    print(f"k-cull seed {seed} {kind}: G_cull - G_base on flat at d={DSTAR} {g[0][0] - g[1][0]:+.3f}")
    aa = sorted(glob.glob(os.path.join(GARDEN, "aa105-*.txt")))
    if aa:
        v = []
        for p in aa:
            lab = os.path.basename(p)[:-4]          # aa105-SEED-bK-holistic-s599
            seed = lab.split("-")[1]
            o = G(garden(f"aa105-{seed}-b0-holistic-s599")) or G(garden(f"base-{seed}-holistic-s599"))
            g = G(garden(lab))
            if o and g and "-b0-" not in lab:
                v.append(g[0] - o[0])
        print(f"RBT-105 A/A, holistic, flat-garden replicate - original at season 599 (about 17 events from season 0): "
              f"RMS {math.sqrt(statistics.fmean(x * x for x in v)):.3f} over {len(v)} pairs" if v else "RBT-105 A/A: no pairs")
    aat = os.path.join(ROOT, "runs", "RBT-105", "aa_spread.txt")
    if os.path.exists(aat):
        print("RBT-105 aa_spread.txt (verbatim, report only):")
        for l in open(aat):
            print("  " + l.rstrip("\n"))
    else:
        print("RBT-105 aa_spread.txt: not committed at this readout")


if __name__ == "__main__":
    main()
