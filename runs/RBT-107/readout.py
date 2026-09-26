"""RBT-107: can adaptation to flat ground be seen at ~20 reproduction events?  The registered readout (Amendment 2).

    python runs/RBT-107/readout.py > runs/RBT-107/readout.txt

TWO SAMPLES, never pooled in a scored line:
  FRESH (confirmatory)  seeds 11-30, T = 360, arms from season 0 to 1200 (fresh_seed.sh): runs/RBT-107/fresh/ARM-SEED
  OLD   (persistence)   RBT-90 part 2's ten, T from runs/RBT-92/onset.txt, their 600-season arms extended to 1200
                        (extend_arm.sh): runs/RBT-107/ARM-SEED.  RBT-101 F2's post hoc decline was found on these at T+110
Arms per seed: B base (random terrain throughout), S shift (flat ground from T), N cull20 (20/20 culled at T, random
terrain); on four old seeds also RBT-101's k-cull (report-only).

THE COMMON GARDEN (garden.py, J = 32 fixed worlds as two halves 0..15 and 16..31, merged; garden/readout/).  G_a^w(s) is
the mean income per robot-bout of arm a's fauna alive at the end of season s (RBT-92's Arm.alive_at), on the 32 worlds,
on ground w in {flat, random}, by the ecology's own group bout (verified 32/32 against a recorded season, adversary F5).
    RESPONSE_flat  A_SB = G_S^flat - G_B^flat      (= probe_refund.py's RESPONSE)       A_SN = G_S^flat - G_N^flat
    REFUND         G_B^flat - G_B^random            Delta0 = the same on C0 (alive at T - 1), the arithmetic
    PAIRED         P = A_SB(co-evolved) - A_SB(designed)   (RBT-110's H)
    SPECIALISATION I = (G_S^flat - G_S^random) - (G_B^flat - G_B^random);  its null I_N = the same with N for S
Delta0 cancels in A_SB, A_SN, P and I by construction (both populations descend from the same C0, same worlds).

§5.5 CONFIRMATORY (FRESH seeds only), a C4-SPECIFIC hypothesis (RBT-110: none of C1-C3 supports it; on C2 the designed
RESPONSE was +0.57).  One-sided, alpha = 0.05, PRIMARY statistic Yuen's 20% trimmed-mean one-sample test (stats107.yuen);
a Yuen p in (0.04, 0.05] counts only if the exact Wilcoxon p is also <= 0.05; t is printed and decides nothing.
Every scored hypothesis is an INTERSECTION-UNION test (A2.8): SUPPORTED only if both forms pass, p = the larger:
  H-REP (T + 110, RBT-101 F2's read point):  H-REP-DES designed A_SB < 0 AND designed A_SN < 0
                                             H-REP-PAIR P > 0 AND P_N = A_SN(co) - A_SN(des) > 0;   Holm over DES and PAIR
  H1    (T + 800, ~22 events, SCORED):       H1-DES and H1-PAIR, the same forms;                     Holm over DES and PAIR
  (A paired test against base alone would "replicate" turnover: RBT-110's C4null puts +0.20 of the +0.27 in cull20.)
  H-ALT (re-adaptation), on the increment inc = A_SB^des(T+800) - A_SB^des(T+110), per seed:
      OVERSHOOTS   designed A_SB(T+800) > 0 resolved (Yuen one-sided, alpha 0.05)  [ADAPTED on the design's own rule]
      DEEPENS      H1-DES supported (IUT, Holm), and inc < 0 resolved (Yuen one-sided, alpha 0.05)
      PERSISTS     H1-DES supported (IUT), and inc not resolved below 0 (a resolved inc > 0 is printed: "partly recovering")
      REVERSES     inc > 0 resolved (Yuen one-sided, alpha 0.05) and H1-DES not supported
      NOT DECIDED  otherwise, printed with the realised MDE
  Read points: T + 110 (anchor), T + 400 and T + 600 (secondary, printed), T + 800 (scored).
§5.3 VERDICT (the design's two-interval rule, now read on FRESH; OLD printed as persistence), per fauna at T + 800:
      ADAPTED     A_SB and A_SN t(n-1) 95% intervals above 0; split by I three ways (adversary F8):
                    SPECIFIC           I interval above 0 AND (I - I_N) interval above 0
                    FURNITURE-BIASED   I interval below 0
                    GENERAL            otherwise (I's interval covers 0)
      MALADAPTED  both intervals below 0; split by I the same three ways
      NOT SEEN    otherwise, with the resolution;  UNREAD  fewer than 6 seeds read
§7 SECONDARY income: Z10 (the arithmetic in the ecology's own seasons, z10.py / RBT-101 probe_arena) printed FIRST, the
garden Delta0 beside it; the paired income slope over [T+200, T+800] against the cull20 null; residual level net of Z10.
Gates, printed first: V-EXT (old: prefix.txt), V0 (fresh: shift and cull20 rows before T identical to the base's,
prefix_check.py), V-POST (every arm: vpost.txt), V-G (garden populations complete), DEPTH (median fewest-births depth of
S at T + 800; below 15 prints DEPTH SHORT).  If a gate fails, nothing below it enters a sentence.
Also printed, not scored: split-half A_SB per seed (worlds 0..15 against 16..31), the trajectory, sorting against novelty,
the selection-differential diagnostic (A1.6), the nulls (RBT-105's depth-matched A/A from garden/j32/, the k-culls,
aa_spread.txt verbatim).

Environment overrides for the smoke test only: RBT107_FRESH, RBT107_OLD, RBT107_DIR, RBT107_GARDEN, RBT107_DSTAR,
RBT107_READS, RBT107_DREPL, RBT107_SLOPE_FROM.
"""
import csv
import glob
import importlib.util
import math
import os
import random
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
KINDS = ("holistic", "conventional")
OLD_SEEDS = [int(s) for s in os.environ.get("RBT107_OLD", "801 804 805 806 807 1 2 3 4 7").split()]
FRESH_SEEDS = [int(s) for s in os.environ.get("RBT107_FRESH", " ".join(map(str, range(11, 31)))).split()]
FRESH_T = 360
SEEDS = OLD_SEEDS  # design_power.py's default sample (the design-stage null is on the old seeds' no-event arms)
ARMS_DIR = os.environ.get("RBT107_DIR", HERE)
GARDEN = os.environ.get("RBT107_GARDEN", os.path.join(HERE, "garden", "readout"))
DSTAR = int(os.environ.get("RBT107_DSTAR", "800"))
D_REPL = int(os.environ.get("RBT107_DREPL", "110"))
READS = [int(x) for x in os.environ.get("RBT107_READS", "110,200,400,600,800").split(",")]
SLOPE_WIN = (int(os.environ.get("RBT107_SLOPE_FROM", "200")), DSTAR)
PAIRED_AA = (0.09, 0.11)
DEPTH_SHORT = 15
ALPHA = 0.05
V0_COLS = ("alive", "births", "deaths", "mean_lifetime_score", "best_lifetime_score")  # as prefix_check.py
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
        12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093}


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


R92 = _load("r92", os.path.join(ROOT, "runs", "RBT-92", "readout.py"))
DEPTH = _load("rbt107_depth", os.path.join(HERE, "depth.py"))
ST = _load("stats107", os.path.join(HERE, "stats107.py"))


def old_onsets():
    out = {}
    for line in open(os.path.join(ROOT, "runs", "RBT-92", "onset.txt")):
        f = line.split("\t")
        if f[0].isdigit() and f[1].isdigit():
            out[int(f[0])] = int(f[1])
    return out


class Sample:
    def __init__(self, name, seeds, fresh):
        self.name, self.seeds, self.fresh = name, seeds, fresh
        self.T = {s: FRESH_T for s in seeds} if fresh else {s: old_onsets()[s] for s in seeds}

    def dir(self, arm, seed):
        return os.path.join(ARMS_DIR, "fresh", f"{arm}-{seed}") if self.fresh else os.path.join(ARMS_DIR, f"{arm}-{seed}")

    def label(self, arm, seed, kind, d=None):
        p = "fresh-" if self.fresh else ""
        return f"{p}c0-{seed}-{kind}" if arm == "c0" else f"{p}{arm}-{seed}-{kind}-d{d}"


# ---------------------------------------------------------------- statistics
def ci(v):
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


def one_sided(v, direction):
    """(Yuen p, t p, Wilcoxon p, trimmed mean) for H: mean in `direction` (+1 greater, -1 less)."""
    x = [direction * a for a in v if a == a]
    if len(x) < 5:
        return float("nan"), float("nan"), float("nan"), float("nan")
    tm, _, _, py = ST.yuen(x)
    _, _, _, pt = ST.t_test(x)
    _, pw = ST.wilcoxon(x)
    return py, pt, pw, direction * tm


def ftest(name, v, direction):
    py, pt, pw, tm = one_sided(v, direction)
    sign = ">" if direction > 0 else "<"
    return (f"{name} ({sign} 0): n={len([a for a in v if a == a])} trimmed mean {tm:+.3f}; Yuen p = {py:.4f} (PRIMARY); "
            f"t p = {pt:.4f}; Wilcoxon p = {pw:.4f}"), py


def mde(null_ab, n):
    """Smallest true A the two-interval rule detects on >= 80% (Gaussian model of the null's RMS; design_power.py)."""
    v = [x for x in null_ab if x == x]
    if len(v) < 2 or n < 2:
        return float("nan")
    s = math.sqrt(statistics.fmean(x * x for x in v) / 2)
    if s == 0:
        return float("nan")
    rng = random.Random(107)
    for step in range(1, 400):
        d = step * s / 20
        hits = 0
        for _ in range(1000):
            eS = [rng.gauss(0, s) for _ in range(n)]
            ab = [d + e - rng.gauss(0, s) for e in eS]
            an = [d + e - rng.gauss(0, s) for e in eS]
            hits += above(ab) and above(an)
        if hits / 1000 >= 0.8:
            return d
    return float("inf")


def power(delta, null_ab, n, reps=2000):
    v = [x for x in null_ab if x == x]
    s = math.sqrt(statistics.fmean(x * x for x in v) / 2)
    rng = random.Random(1071)
    hit = 0
    for _ in range(reps):
        eS = [rng.gauss(0, s) for _ in range(n)]
        ab = [delta + e - rng.gauss(0, s) for e in eS]
        an = [delta + e - rng.gauss(0, s) for e in eS]
        hit += (above(ab) and above(an)) if delta > 0 else (below(ab) and below(an))
    return hit / reps


def slope(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


# ---------------------------------------------------------------- garden rows
def garden(label, part=None):
    """{name: (gain_flat, gain_random)} from GARDEN/LABEL.txt (or a half: part = 'w00-15' / 'w16-31'), or None."""
    p = os.path.join(GARDEN, "parts", f"{label}.{part}.txt") if part else os.path.join(GARDEN, f"{label}.txt")
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


def contrasts(sm, seed, kind, d, part=None):
    g = {a: G(garden(sm.label(a, seed, kind, d), part)) for a in ("shift", "base", "cull20")}
    S, B, N = g["shift"], g["base"], g["cull20"]
    if not (S and B):
        return None
    out = dict(SB=S[0] - B[0], RSB=S[1] - B[1], REF=B[0] - B[1], I=(S[0] - S[1]) - (B[0] - B[1]))
    if N:
        out.update(SN=S[0] - N[0], NB=N[0] - B[0], IN=(N[0] - N[1]) - (B[0] - B[1]))
    return out


def table(sm, kind, d, key):
    out = {}
    for s in sm.seeds:
        c = contrasts(sm, s, kind, d)
        if c and key in c:
            out[s] = c[key]
    return out


def paired(sm, d, key="SB"):
    co, de = table(sm, "holistic", d, key), table(sm, "conventional", d, key)
    return {s: co[s] - de[s] for s in co if s in de}


# ---------------------------------------------------------------- sections
def gates(sm, arms):
    ok = True
    print(f"-- {sm.name}")
    for s in sm.seeds:
        line = []
        for a in ("base", "shift", "cull20", "cull"):
            d = sm.dir(a, s)
            if not os.path.isdir(d):
                if a != "cull":
                    line.append(f"{a}: MISSING")
                    ok = False
                continue
            for fn, tag in (("prefix.txt", "V-EXT" if not sm.fresh else None), ("vpost.txt", "V-POST")):
                if tag is None:
                    continue
                p = os.path.join(d, fn)
                v = [l for l in open(p) if l.startswith(tag)] if os.path.exists(p) else []
                good = bool(v) and "PASS" in v[-1]
                ok &= good
                line.append(f"{a} {tag} {'PASS' if good else 'FAIL/MISSING'}")
        if sm.fresh and ("base", s) in arms:
            for a in ("shift", "cull20"):
                if (a, s) in arms:
                    B, X, T = arms[("base", s)], arms[(a, s)], sm.T[s]
                    bad = [t for t in range(T) for k in KINDS
                           if any(B.raw.get((t, k), {}).get(c) != X.raw.get((t, k), {}).get(c) for c in V0_COLS)]
                    ok &= not bad
                    line.append(f"{a} V0 {'PASS' if not bad else 'FAIL at ' + str(bad[0])}")
        print(f"  seed {s:>4}: " + "; ".join(line))
    return ok


def vg(sm, arms):
    bad = []
    for p in sorted(glob.glob(os.path.join(GARDEN, "*.txt"))):
        lab = os.path.basename(p)[:-4]
        m = re.match(r"(fresh-)?(base|shift|cull20|cull)-(\d+)-(holistic|conventional)-d(\d+)$", lab)
        if not m or bool(m.group(1)) != sm.fresh:
            continue
        a, s, k, d = m.group(2), int(m.group(3)), m.group(4), int(m.group(5))
        if s not in sm.seeds:
            continue
        arm = arms.get((a, s))
        n = len(garden(lab))
        if arm is None or n != arm.alive[k].get(sm.T[s] + d, -1):
            bad.append(f"{lab} n={n}")
    print(f"  V-G {sm.name}: {'PASS' if not bad else 'FAIL ' + str(bad[:4])}")
    return not bad


def depth_line(sm, arms):
    out = {}
    for s in sm.seeds:
        a = arms.get(("shift", s))
        if a is None or a.last < sm.T[s] + DSTAR:
            continue
        for k in KINDS:
            m = DEPTH.measures(a, k, sm.T[s], [sm.T[s] + DSTAR])
            if m:
                out[(s, k)] = m[sm.T[s] + DSTAR][1]
    for k in KINDS:
        v = [out[(s, k)] for s in sm.seeds if (s, k) in out]
        if v:
            print(f"  DEPTH {sm.name} {k:12s} median {statistics.median(v):.1f} fewest-births events at T+{DSTAR} "
                  f"(range {min(v):.1f}..{max(v):.1f}, n={len(v)})" + ("  DEPTH SHORT" if statistics.median(v) < DEPTH_SHORT else ""))
    return out


def arithmetic(sm):
    d0 = {}
    for k in KINDS:
        v = []
        for s in sm.seeds:
            g = G(garden(sm.label("c0", s, k)))
            if g:
                d0[(s, k)] = g[0] - g[1]
                v.append(g[0] - g[1])
        halves = []
        for s in sm.seeds:
            a, b = (G(garden(sm.label("c0", s, k), p)) for p in ("w00-15", "w16-31"))
            if a and b:
                halves.append((a[0] - a[1]) - (b[0] - b[1]))
        print(f"  DELTA0 {sm.name} {k:12s} {fmt(v)}"
              + (f"; world sampling: split-half (0..15 - 16..31) {fmt(halves)} (the level of Delta0 carries a common-world error "
                 f"of about half this spread; it cancels in every contrast)" if halves else ""))
    return d0


def z10(sm):
    out = {}
    if sm.fresh:
        for p in glob.glob(os.path.join(GARDEN, "z10-fresh-*.txt")):
            for line in open(p):
                f = line.split("\t")
                if len(f) >= 3 and "Z10" in f[2] and "n/a" not in f[2]:
                    out[(int(f[0]), f[1])] = float(f[2].split()[1])
    else:
        p = os.path.join(ROOT, "runs", "RBT-101", "readout-adversary", "probe_arena.txt")
        if os.path.exists(p):
            for line in open(p):
                m = re.match(r"\s+(co-evolved|designed)\s+gain\s+.*?per seed \[([^\]]+)\]", line)
                if m and "pairs per seed" in line:
                    kind = "holistic" if m.group(1) == "co-evolved" else "conventional"
                    for s, x in zip(OLD_SEEDS, m.group(2).split(",")):
                        out[(s, kind)] = float(x)
    for k in KINDS:
        v = [out[(s, k)] for s in sm.seeds if (s, k) in out]
        print(f"  Z10 {sm.name} {k:12s} {fmt(v) if v else 'not available'}")
    pz = [out[(s, 'holistic')] - out[(s, 'conventional')] for s in sm.seeds if (s, 'holistic') in out and (s, 'conventional') in out]
    if pz:
        print(f"  Z10 {sm.name} paired (co - des) {fmt(pz)}  <- the arithmetic for an unchanged pair, in the ecology's own seasons")
    return out


def scored_p(v, direction):
    """The p a scored component uses: Yuen's; if it falls in (0.04, 0.05] it counts only with the exact Wilcoxon p also
    <= 0.05 (A2.8: Yuen's size is 0.053-0.063 on the modelled null at n = 20), so the component's p is then the larger."""
    py, pt, pw, tm = one_sided(v, direction)
    return (max(py, pw) if 0.04 < py <= 0.05 else py), py, pt, pw, tm


def iut(name, base_v, net_v, direction):
    """Intersection-union (A2.8): SUPPORTED only if both the against-base and the net-of-null forms pass; p = the larger."""
    sign = ">" if direction > 0 else "<"
    lines, ps = [], []
    for form, v in (("against base", base_v), ("net of the null", net_v)):
        p, py, pt, pw, tm = scored_p(v, direction)
        ps.append(p)
        lines.append(f"    {name} {form} ({sign} 0): n={len(v)} trimmed mean {tm:+.3f}; Yuen p = {py:.4f} (PRIMARY); "
                     f"t p = {pt:.4f}; Wilcoxon p = {pw:.4f}; component p used = {p:.4f}")
    return max(ps), lines


def specificity(ii, iin, direction):
    """§5.3's three-way split (A2.5 F8), in the direction of the hypothesis it annotates (A2.9): SPECIFIC if I and I - I_N
    both have t intervals on H's side of 0 (a DES decline is flat-specific when I < 0: worse on flat, relative to random,
    than the base; a PAIR effect when the paired I > 0); OPPOSITE if I's interval is on the other side; GENERAL otherwise."""
    a, b = [direction * x for x in ii], [direction * x for x in iin]
    return "SPECIFIC" if above(a) and above(b) else "OPPOSITE" if below(a) else "GENERAL"


def confirmatory(sm):
    print(f"-- {sm.name}: read points T+{D_REPL} (anchor), 400, 600 (secondary), {DSTAR} (scored)")
    for d in sorted(set(READS) - {200} if sm.fresh else READS):
        des, pr = table(sm, "conventional", d, "SB"), paired(sm, d)
        if des:
            print(f"  d={d:>3} designed A_SB {fmt(list(des.values()))} | designed A_SN {fmt(list(table(sm, 'conventional', d, 'SN').values()))}"
                  + (f" | paired P {fmt(list(pr.values()))} | paired P_N {fmt(list(paired(sm, d, 'SN').values()))}"
                     f" (P: {statistics.fmean(pr.values()) / PAIRED_AA[1]:+.1f} to {statistics.fmean(pr.values()) / PAIRED_AA[0]:+.1f} paired A/A units)" if pr else ""))
    res = {}
    for tag, d in (("H-REP", D_REPL), ("H1", DSTAR)):
        seeds = [s for s in sm.seeds if all(s in table(sm, k, d, key) for k in KINDS for key in ("SB", "SN"))]
        if len(seeds) < 6:
            print(f"  {tag}: UNREAD (n = {len(seeds)} seeds with all four contrasts)")
            res[tag] = None
            continue
        dsb, dsn = table(sm, "conventional", d, "SB"), table(sm, "conventional", d, "SN")
        pb, pn = paired(sm, d, "SB"), paired(sm, d, "SN")
        p_des, l1 = iut(f"{tag}-DES designed", [dsb[s] for s in seeds], [dsn[s] for s in seeds], -1)
        p_pair, l2 = iut(f"{tag}-PAIR paired", [pb[s] for s in seeds], [pn[s] for s in seeds], +1)
        rej = ST.holm([p_des, p_pair], ALPHA)
        print("\n".join(l1 + l2))
        print(f"  {tag} (IUT, Holm at alpha {ALPHA} over DES and PAIR): {tag}-DES {'SUPPORTED' if rej[0] else 'NOT SUPPORTED'} "
              f"(IUT p {p_des:.4f}); {tag}-PAIR {'SUPPORTED' if rej[1] else 'NOT SUPPORTED'} (IUT p {p_pair:.4f})")
        # A2.9 (interpretation only; RBT-110 readout adversary F3): only new - old speaks to flat-specificity.  I and
        # I - I_N are printed beside every H line; a SUPPORTED with I not SPECIFIC reads "general, not flat-specific".
        for half, label, supported, direction in (("DES", "designed", rej[0], -1), ("PAIR", "paired", rej[1], +1)):
            if half == "DES":
                ii = [table(sm, "conventional", d, "I")[s] for s in seeds]
                iin = [table(sm, "conventional", d, "I")[s] - table(sm, "conventional", d, "IN")[s] for s in seeds]
            else:
                ico, ide = table(sm, "holistic", d, "I"), table(sm, "conventional", d, "I")
                ino, ind = table(sm, "holistic", d, "IN"), table(sm, "conventional", d, "IN")
                ii = [ico[s] - ide[s] for s in seeds]
                iin = [(ico[s] - ide[s]) - (ino[s] - ind[s]) for s in seeds]
            split = specificity(ii, iin, direction)
            reading = ("flat-specific" if split == "SPECIFIC" else "general, not flat-specific") if supported else "not supported"
            print(f"    {tag}-{half} specialisation ({label}): I {fmt(ii)}; I - I_N {fmt(iin)}; I is {split}; reading: {reading}")
        res[tag] = rej
    d8, d1 = table(sm, "conventional", DSTAR, "SB"), table(sm, "conventional", D_REPL, "SB")
    inc = [d8[s] - d1[s] for s in d8 if s in d1]
    if len(inc) >= 6 and res.get("H1") is not None:
        li, pi_up = ftest(f"H-ALT increment A_SB^des(T+{DSTAR}) - A_SB^des(T+{D_REPL})", inc, +1)
        _, pi_dn = ftest("increment", inc, -1)
        _, po = ftest("overshoot", list(d8.values()), +1)
        h1 = res["H1"][0]  # H1-DES as scored by the IUT (A2.8)
        if po <= ALPHA:
            out = "OVERSHOOTS (designed A_SB resolved above 0 at T+800: re-adapted beyond the base)"
        elif h1 and pi_dn <= ALPHA:
            out = "DEEPENS (the C4 decline is supported at T+800, against base and net of the null, and grew since T+110)"
        elif h1:
            out = "PERSISTS" + (" (partly recovering: the increment is resolved above 0)" if pi_up <= ALPHA else "")
        elif pi_up <= ALPHA:
            out = "REVERSES (the increment is resolved above 0 and the C4 decline is not supported at T+800)"
        else:
            out = f"NOT DECIDED (MDE on the realised null {mde(list(table(sm, 'conventional', DSTAR, 'NB').values()), len(inc)):.3f})"
        print(f"  {li}\n  H-ALT outcome {sm.name}: {out}")


def verdict(sm, d0):
    for k in KINDS:
        rows = [contrasts(sm, s, k, DSTAR) for s in sm.seeds]
        rows = [r for r in rows if r and "SN" in r]
        n = len(rows)
        sb, sn, ii, iin = ([r[x] for r in rows] for x in ("SB", "SN", "I", "IN"))
        if n < 6:
            v = "UNREAD"
        else:
            core = "ADAPTED" if above(sb) and above(sn) else "MALADAPTED" if below(sb) and below(sn) else None
            if core:
                split = ("SPECIFIC" if above(ii) and above([a - b for a, b in zip(ii, iin)])
                         else "FURNITURE-BIASED" if below(ii) else "GENERAL")
                v = f"{core}, {split}"
            else:
                v = "NOT SEEN"
        res = mde([r["NB"] for r in rows], n) if n >= 2 else float("nan")
        print(f"  VERDICT {sm.name} {k:12s} {v} at T+{DSTAR}, n={n}; A_SB {fmt(sb)}; A_SN {fmt(sn)}; I {fmt(ii)}; "
              f"null A_NB {fmt([r['NB'] for r in rows])}; resolution (two-interval, realised null) {res:.3f}")


def split_half(sm):
    for k in KINDS:
        diffs = []
        for s in sm.seeds:
            a, b = contrasts(sm, s, k, DSTAR, "w00-15"), contrasts(sm, s, k, DSTAR, "w16-31")
            if a and b:
                diffs.append(a["SB"] - b["SB"])
                print(f"  split-half {sm.name} seed {s:>4} {k:12s} A_SB worlds 0..15 {a['SB']:+.3f}  16..31 {b['SB']:+.3f}")
        if diffs:
            print(f"  split-half {sm.name} {k:12s} measurement sd of a seed's A_SB at J=32 ~ "
                  f"{math.sqrt(statistics.fmean(x * x for x in diffs)) / 2:.3f} (RMS half-difference / 2)")


def trajectory(sm):
    for k in KINDS:
        for d in READS:
            rows = [contrasts(sm, s, k, d) for s in sm.seeds]
            rows = [r for r in rows if r]
            if rows:
                print(f"  {sm.name} {k:12s} d={d:>3} n={len(rows)} A_SB {fmt([r['SB'] for r in rows])} | RESPONSE_random "
                      f"{fmt([r['RSB'] for r in rows])} | REFUND {fmt([r['REF'] for r in rows])} | I {fmt([r['I'] for r in rows])}"
                      + (f" | A_SN {fmt([r['SN'] for r in rows if 'SN' in r])}" if any('SN' in r for r in rows) else ""))


def sorting(sm, arms):
    for k in KINDS:
        nov, srt = [], []
        for s in sm.seeds:
            c0rows = garden(sm.label("c0", s, k))
            if not c0rows:
                continue
            T = sm.T[s]
            vals = {}
            for a in ("shift", "base"):
                arm, rows = arms.get((a, s)), garden(sm.label(a, s, k, DSTAR))
                if arm is None or not rows:
                    break
                c0 = arm.alive_at(k, T - 1)
                w = {}
                for n in arm.alive_at(k, T + DSTAR):
                    anc = arm.anc0(k, n, c0)
                    for i in anc:
                        w[i] = w.get(i, 0.0) + 1.0 / len(anc)
                tot = sum(w[i] for i in w if i in c0rows)
                if not tot:
                    break
                vals[a] = (G(rows)[0], sum(w[i] * c0rows[i][0] for i in w if i in c0rows) / tot)
            if len(vals) == 2:
                srt.append(vals["shift"][1] - vals["base"][1])
                nov.append((vals["shift"][0] - vals["shift"][1]) - (vals["base"][0] - vals["base"][1]))
        if srt:
            print(f"  {sm.name} {k:12s} sorting part {fmt(srt)} | novelty part {fmt(nov)}")


def income(sm, arms, z):
    for k in KINDS:
        sb, nb, lev = [], [], []
        for s in sm.seeds:
            T = sm.T[s]
            S, B, N = (arms.get((a, s)) for a in ("shift", "base", "cull20"))
            if not (S and B and N) or min(S.last, B.last, N.last) < T + SLOPE_WIN[1]:
                continue
            xs = list(range(T + SLOPE_WIN[0], T + SLOPE_WIN[1] + 1))
            sb.append(100 * slope(xs, [S.x[k][t] - B.x[k][t] for t in xs]))
            nb.append(100 * slope(xs, [N.x[k][t] - B.x[k][t] for t in xs]))
            if (s, k) in z:
                lev.append(statistics.fmean(S.x[k][t] - B.x[k][t] for t in range(T + DSTAR - 100, T + DSTAR)) - z[(s, k)])
        if sb:
            diff = [a - b for a, b in zip(sb, nb)]
            v = "RISING" if above(sb) and above(diff) else "FALLING" if below(sb) and below(diff) else "FLAT (not resolved)"
            print(f"  INCOME {sm.name} {k:12s} {v if len(sb) >= 6 else 'UNREAD'}: slope D_SB {fmt(sb)} | null D_NB {fmt(nb)}"
                  + (f" | residual level net of Z10 over [T+{DSTAR - 100}, T+{DSTAR}) {fmt(lev)}" if lev else ""))


def selection(sm, arms):
    for k in KINDS:
        for a, ground in (("shift", 0), ("base", 1), ("cull20", 1)):
            per_d = {}
            for d in READS:
                v = []
                for s in sm.seeds:
                    arm, rows = arms.get((a, s)), garden(sm.label(a, s, k, d))
                    if arm is None or not rows:
                        continue
                    kids = {}
                    for (kk, n), (b, _, ps) in arm.ind.items():
                        if kk == k and b > sm.T[s] + d:
                            for p_ in ps:
                                kids[p_] = kids.get(p_, 0) + 1
                    names = list(rows)
                    w = [kids.get(n, 0) for n in names]
                    if sum(w) == 0:
                        continue
                    mw = statistics.fmean(w)
                    z = [rows[n][ground] for n in names]
                    mz = statistics.fmean(z)
                    v.append(statistics.fmean((wi / mw - 1) * (zi - mz) for wi, zi in zip(w, z)))
                if v:
                    per_d[d] = v
            if per_d:
                print(f"  {sm.name} {k:12s} {a:6s} " + " | ".join(f"d={d}: {fmt(v)}" for d, v in per_d.items()))


def nulls():
    j32 = os.path.join(HERE, "garden", "j32")
    v = []
    for p in sorted(glob.glob(os.path.join(j32, "aa105-*.txt"))):
        m = re.match(r"aa105-(\d+)-b(\d)-holistic-s599", os.path.basename(p)[:-4])
        o = os.path.join(j32, f"base-{m.group(1)}-holistic-s599.txt")
        if m and os.path.exists(o):
            g, go = G(_rows(p)), G(_rows(o))
            v.append(g[0] - go[0])
    if v:
        print(f"  RBT-105 depth-matched A/A (co-evolved, flat garden, replicate - original at 599, ~17 events, J=32): "
              f"{fmt(v)}; RMS {math.sqrt(statistics.fmean(x * x for x in v)):.3f} over {len(v)} pairs")
    aat = os.path.join(ROOT, "runs", "RBT-105", "aa_spread.txt")
    if os.path.exists(aat):
        print("  RBT-105 aa_spread.txt (verbatim, report only):")
        for l in open(aat):
            print("    " + l.rstrip("\n"))
    else:
        print("  RBT-105 aa_spread.txt: not committed at this readout")


def _rows(path):
    out = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        out[f[4]] = (float(f[5]), float(f[6]))
    return out


def main():
    print(__doc__.split("\n\n")[0])
    samples = [Sample("FRESH", FRESH_SEEDS, True), Sample("OLD", OLD_SEEDS, False)]
    arms = {}
    for sm in samples:
        a = {}
        for s in sm.seeds:
            for arm in ("base", "shift", "cull20", "cull"):
                if os.path.exists(os.path.join(sm.dir(arm, s), "seasons.txt")):
                    a[(arm, s)] = R92.Arm(sm.dir(arm, s))
        arms[sm.name] = a
    print("\n== GATES")
    ok = {sm.name: gates(sm, arms[sm.name]) & vg(sm, arms[sm.name]) for sm in samples}
    for sm in samples:
        print(f"  ALL GATES {sm.name}: {'PASS' if ok[sm.name] else 'FAIL: nothing of this sample below enters a sentence'}")
    print("\n== DEPTH")
    for sm in samples:
        depth_line(sm, arms[sm.name])
    print("\n== 0. THE ARITHMETIC: Z10 first (the ecology's own seasons), the garden's Delta0 beside it")
    zz, d0 = {}, {}
    for sm in samples:
        zz[sm.name] = z10(sm)
        d0[sm.name] = arithmetic(sm)
    print("\n== §5.5 CONFIRMATORY (FRESH scored; OLD printed as persistence on the discovery seeds, never pooled)")
    for sm in samples:
        confirmatory(sm)
    print("\n== §5.3 VERDICT (two-interval rule; FRESH scored, OLD persistence)")
    for sm in samples:
        verdict(sm, d0[sm.name])
    print("\n== SPLIT-HALF (worlds 0..15 against 16..31), printed")
    for sm in samples:
        split_half(sm)
    print("\n== TRAJECTORY, printed and not scored (on OLD, T+110 and T+200 lie in seasons RBT-101 read: not prospective)")
    for sm in samples:
        trajectory(sm)
    print(f"\n== SORTING AGAINST NOVELTY at T+{DSTAR}, printed (approximate: ancestry shares)")
    for sm in samples:
        sorting(sm, arms[sm.name])
    print(f"\n== §7 SECONDARY: income, paired slope over [T+{SLOPE_WIN[0]}, T+{SLOPE_WIN[1]}] per 100 seasons, residual net of Z10")
    for sm in samples:
        income(sm, arms[sm.name], zz[sm.name])
    print("\n== DIAGNOSTIC (A1.6, registered separately, not scored, names no mechanism): selection differential on garden income")
    for sm in samples:
        selection(sm, arms[sm.name])
    print("\n== NULLS, report only")
    nulls()


if __name__ == "__main__":
    main()
