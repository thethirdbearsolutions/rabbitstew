"""Paper 10: re-derive the headline figures from committed files (no simulation, no ecology run).

Reads only committed text files on the integration branch:

  runs/RBT-103/adversary/world_matrix.txt          the prize in the P-801 world (t(9) lines, quoted)
  runs/RBT-106/prize.txt                           the prize per seed, uniform and one-field patchy world, a = 32 / 64
  runs/RBT-102/informative_n.txt                   the matched-drift null for a zero carrier count (quoted)
  runs/RBT-104/readout.txt                         the VOID verdict line (quoted)
  runs/RBT-106/baseline/baseline-w32-SEED.txt      RBT-106's operator-alone persistence tables (default operator)
  runs/RBT-112/baseline/baseline-w32[-S0]-SEED.txt RBT-112's re-run: default and global_bias_sigma = 0
  runs/RBT-106/P1-readout.txt                      P1 against S1: per-seed table and verdict
  runs/RBT-106/p1-adversary/power_n7.txt           P-NULL's miss rates at the usable n = 7 (quoted)
  runs/RBT-106/H-readout.txt                       HU against HP: per-seed table, verdict, power at n = 10
  runs/RBT-106/{HU,HP}-SEED/held-{300,599}.txt     the HELD readings per arm
  runs/RBT-106/h-adversary/ownnull_pool.txt        HELD's null on each arm's own genealogy (quoted)
  runs/RBT-112/readout.txt                         HU against HZ: per-seed table and verdict
  runs/RBT-112/readout-adversary/instrument.txt    power at the realised n, the likelihood of s, the balance point (quoted)
  runs/RBT-112/power.txt                           the registered design anchors (quoted)
  runs/RBT-105/REPORT.md                           the flip count (5 of 14), recomputed as a Clopper-Pearson interval

Prints docs/paper-10/rederive.txt.  Run from the repository root:

    python docs/paper-10/rederive.py > docs/paper-10/rederive.txt

Row ids in brackets ([W1], [E3] ...) are the ones the paper cites.  Rows marked POST HOC are this
paper's arithmetic on committed numbers; every other row re-derives or quotes a registered figure.
"""
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEEDS = [801, 4, 804, 805, 806, 807, 1, 2, 3, 7]


# --- Student t quantiles and binomials, no scipy -------------------------------

def _t_cdf(x, df):
    # regularised incomplete beta via continued fraction (paper 9's rederive.py, unchanged)
    if x == 0:
        return 0.5
    a, b = df / 2.0, 0.5
    z = df / (df + x * x)

    def betacf(a, b, x):
        qab, qap, qam = a + b, a + 1.0, a - 1.0
        c, d = 1.0, 1.0 - qab * x / qap
        d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
            c = 1.0 + aa / c
            c = c if abs(c) > 1e-300 else 1e-300
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
            c = 1.0 + aa / c
            c = c if abs(c) > 1e-300 else 1e-300
            de = d * c
            h *= de
            if abs(de - 1.0) < 1e-14:
                break
        return h

    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(z) + b * math.log(1 - z) - lbeta)
    if z < (a + 1) / (a + b + 2):
        ib = front * betacf(a, b, z) / a
    else:
        ib = 1.0 - front * betacf(b, a, 1 - z) / b
    return 1.0 - 0.5 * ib if x >= 0 else 0.5 * ib


def tq(p, df):
    lo, hi = -50.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def stat(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    h = tq(0.975, n - 1) * sd / math.sqrt(n)
    return m, m - h, m + h, sd, sum(1 for x in xs if x > 0), n


def fmt(xs):
    m, lo, hi, sd, pos, n = stat(xs)
    return f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}] sd {sd:.3f}, {pos}/{n} positive"


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k, n, alpha=0.05):
    def solve(target, upper):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if upper:   # P(X <= k | mid) = alpha/2
                if binom_cdf(k, n, mid) > target:
                    lo = mid
                else:
                    hi = mid
            else:       # P(X >= k | mid) = alpha/2
                if 1 - binom_cdf(k - 1, n, mid) < target:
                    lo = mid
                else:
                    hi = mid
        return (lo + hi) / 2
    low = 0.0 if k == 0 else solve(alpha / 2, False)
    high = 1.0 if k == n else solve(alpha / 2, True)
    return low, high


# --- readers -------------------------------------------------------------------

def read(rel):
    return (ROOT / rel).read_text()


def line_with(rel, needle):
    for ln in read(rel).splitlines():
        if needle in ln:
            return ln.strip()
    raise SystemExit(f"{rel}: no line containing {needle!r}")


def md_table(rel, first_col="seed"):
    """Rows of the first markdown table in rel whose header starts with | first_col |, as dicts."""
    lines = read(rel).splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(f"| {first_col} |"):
            head = [c.strip() for c in ln.strip("|").split("|")]
            rows = []
            for r in lines[i + 2:]:
                if not r.startswith("|"):
                    break
                rows.append(dict(zip(head, [c.strip() for c in r.strip("|").split("|")])))
            return head, rows
    raise SystemExit(f"{rel}: no table headed by {first_col}")


def baseline(rel):
    rows = {}
    for ln in read(rel).splitlines():
        if ln.startswith("#") or not ln.strip():
            continue
        c = ln.split("\t")
        rows[int(c[0])] = {"n": int(c[1]), "same": int(c[2]), "pay32": int(c[5])}
    return rows


def pooled_f(tables, col, d):
    return sum(t[d][col] for t in tables) / sum(t[d]["n"] for t in tables)


def u_of(f, d):
    return 1 - f ** (1 / d)


def held_reading(rel):
    m = re.search(r"k_planted = (\d+), n = (\d+), mu = ([\d.]+), B = (\d+)", read(rel))
    if not m:
        return None
    return tuple(int(m.group(i)) if i != 3 else float(m.group(i)) for i in (1, 2, 3, 4))


def first_num(cell):
    m = re.search(r"[-+]?\d+\.\d+", cell)
    return float(m.group(0)) if m else float("nan")


def arm_rows(rel):
    _, rows = md_table(rel)
    out = {}
    for r in rows:
        out[(int(r["seed"]), r["arm"])] = r
    return out


def colname(rows, prefix):
    for k in next(iter(rows.values())):
        if k.startswith(prefix):
            return k
    raise SystemExit(f"no column starting {prefix!r}")


# --- the report ----------------------------------------------------------------

def main():
    print("Paper 10 (RBT-114): re-derivation of the headline figures, committed files only.")
    print("All intervals are 95% t(n - 1) over seeds unless the row says otherwise.")
    print()

    # W: the prize by world ------------------------------------------------------
    print("W. The prize by world (RBT-103, RBT-106 prize.txt); the fixed-body (Pioneer) population's bodies")
    _, prize = md_table("runs/RBT-106/prize.txt")
    uni = [first_num(r["uniform a=64 (RBT-103)"]) for r in prize]
    pat = [first_num(r["patchy a=64"]) for r in prize]
    bu = [float(r["base uniform"]) for r in prize]
    bp = [float(r["base patchy"]) for r in prize]
    print(f"  [W1] uniform world (RBT-90 part 2: 12 items, no patches), a = 64: {fmt(uni)}")
    print(f"  [W2] one-field patchy world (12 items in 3 patches), a = 64:     {fmt(pat)}")
    print(f"  [W3] patchy - uniform, paired:                                  {fmt([p - u for p, u in zip(pat, uni)])}")
    print(f"  [W4] ratio of means, a = 64: {sum(pat) / sum(uni):.2f}x; per seed {min(p / u for p, u in zip(pat, uni)):.2f}x to {max(p / u for p, u in zip(pat, uni)):.2f}x")
    print(f"  [W5] base income, uniform {fmt(bu)}; patchy {fmt(bp)}")
    print(f"       quoted, prize.txt: {line_with('runs/RBT-106/prize.txt', 'PRIZE uniform')}")
    for tag, needle in (("W6", "t(9) own world"), ("W7", "t(9) P-801 world  "), ("W8", "PAYS count")):
        print(f"  [{tag}] quoted, RBT-103 adversary world_matrix.txt: {line_with('runs/RBT-103/adversary/world_matrix.txt', needle)}")
    print()

    # D: RBT-102's zero ----------------------------------------------------------
    print("D. RBT-102: the zero, and the matched drift null (quoted)")
    print(f"  [D1] {line_with('runs/RBT-102/informative_n.txt', 'per-set P(0 | drift)')}")
    print(f"  [D2] {line_with('runs/RBT-102/informative_n.txt', 'point 0.81')}")
    print()

    # V: RBT-104's VOID ----------------------------------------------------------
    print("V. RBT-104: the scored verdict (quoted)")
    print(f"  [V1] {line_with('runs/RBT-104/readout.txt', 'VERDICT:')}")
    print(f"  [V2] {line_with('runs/RBT-104/readout.txt', 'S8 viable 10')}")
    print()

    # E: the operator-alone erasure ------------------------------------------------
    print("E. The operator-alone erasure of the planted w = 32 compass (K = 1, no selection, no crossover)")
    t106 = [baseline(f"runs/RBT-106/baseline/baseline-w32-{s}.txt") for s in SEEDS]
    tdef = [baseline(f"runs/RBT-112/baseline/baseline-w32-{s}.txt") for s in SEEDS]
    ts0 = [baseline(f"runs/RBT-112/baseline/baseline-w32-S0-{s}.txt") for s in SEEDS]
    same = all(a == b for a, b in zip(t106, tdef))
    print(f"  [E0] RBT-112's default tables equal RBT-106's committed tables, all depths, all ten seeds: {same}")
    print("  pooled pay32 persistence f(d) over 6,000 lineages, and u(d) = 1 - f(d)^(1/d):")
    print("  | d | f default | f S = 0 | u default | u S = 0 | u same, S = 0 (the structure's own decay) |")
    for d in (1, 2, 4, 8, 16):
        fd, fs = pooled_f(tdef, "pay32", d), pooled_f(ts0, "pay32", d)
        ss = pooled_f(ts0, "same", d)
        print(f"  | {d} | {fd:.4f} | {fs:.4f} | {u_of(fd, d):.3f} | {u_of(fs, d):.3f} | {u_of(ss, d):.3f} |")
    u8d, u8s = u_of(pooled_f(tdef, "pay32", 8), 8), u_of(pooled_f(ts0, "pay32", 8), 8)
    u8same = u_of(pooled_f(ts0, "same", 8), 8)
    print(f"  [E1] primary u(8), default operator: {u8d:.3f}  (RBT-112 erasure.txt: 0.282; the ticket's 0.29 is u(1))")
    print(f"  [E2] primary u(8), global biases frozen (S = 0): {u8s:.3f}  (erasure.txt: 0.089)")
    print(f"  [E3] structure's own decay under S = 0, u(8) on `same`: {u8same:.3f}  (erasure.txt: 0.067)")
    print(f"  [E4] POST HOC (this paper): the share of the default u(8) removed by freezing the global biases: "
          f"({u8d:.3f} - {u8s:.3f}) / {u8d:.3f} = {(u8d - u8s) / u8d:.2f}")
    per = []
    for a, b in zip(tdef, ts0):
        per.append(u_of(b[8]["pay32"] / b[8]["n"], 8) - u_of(a[8]["pay32"] / a[8]["n"], 8))
    print(f"  [E5] per seed u(8), S = 0 - default, paired: {fmt(per)}")
    print(f"  [E6] pay32 persistence at depth 16: default {pooled_f(tdef, 'pay32', 16):.4f}, S = 0 {pooled_f(ts0, 'pay32', 16):.4f}")
    print()

    # P: RBT-106 P1 ----------------------------------------------------------------
    print("P. RBT-106 P1: a sub-paying planted structure (w = 1, a = 2) in the patchy world against the uniform one")
    p1 = arm_rows("runs/RBT-106/P1-readout.txt")
    fcol = colname(p1, "F patchy-scored")
    usable = [4, 804, 806, 807, 1, 2, 3]   # P1-801, P1-7 and S1-805 fail their install control (P1-readout.txt)
    dF = [first_num(p1[(s, "P1")][fcol]) - first_num(p1[(s, "S1")][fcol]) for s in usable]
    dF10 = [first_num(p1[(s, "P1")][fcol]) - first_num(p1[(s, "S1")][fcol]) for s in SEEDS]
    print(f"  [P1] paired F(P1) - F(S1), patchy-scored, 7 usable pairs: {fmt(dF)}")
    print(f"       quoted: {line_with('runs/RBT-106/P1-readout.txt', 'paired F(P1) - F(S1)')}")
    print(f"  [P2] the same over all ten pairs (usability ignored; reported, not scored): {fmt(dF10)}")
    comp = sum(1 for s in usable if "FOOD-DEPENDENT" in p1[(s, "P1")][fcol])
    print(f"  [P3] COMPASS lines among the 7 usable P1 lines: {comp}; quoted: {line_with('runs/RBT-106/P1-readout.txt', 'VERDICT P:')[:40]}")
    print(f"  [P4] quoted, the P1 adversary's power at the usable n = 7 (measured bare-line model):")
    for needle in ("measured patchy bare lines (F8, §10.5): N(-0.056, 0.145), FD 0.05 | the prize alone suffices (q = 0.5)",
                   "measured patchy bare lines (F8, §10.5): N(-0.056, 0.145), FD 0.05 | the prize suffices, weakly (q = 0.25)",
                   "  n = 7: q 0.25"):
        print(f"       {line_with('runs/RBT-106/p1-adversary/power_n7.txt', needle)}")
    print()

    # H: RBT-106 H -----------------------------------------------------------------
    print("H. RBT-106 H: a paying planted compass (w = 32, a = 64), HU (uniform) against HP (patchy)")
    held = {}
    for arm in ("HU", "HP"):
        for s in SEEDS:
            r3 = held_reading(f"runs/RBT-106/{arm}-{s}/held-300.txt")
            r5 = held_reading(f"runs/RBT-106/{arm}-{s}/held-599.txt")
            held[(arm, s)] = bool(r3 and r5 and r3[0] > r3[3] and r5[0] > r5[3])
    nhu = sum(held[("HU", s)] for s in SEEDS)
    nhp = sum(held[("HP", s)] for s in SEEDS)
    print(f"  [H1] HELD (k_planted > B at 300 and at 599, from the committed held files): HU {nhu}, HP {nhp}; "
          f"HP not held: {[s for s in SEEDS if not held[('HP', s)]]}")
    print(f"       quoted: {line_with('runs/RBT-106/H-readout.txt', 'HELD: HU')}")
    h = arm_rows("runs/RBT-106/H-readout.txt")
    fcol = colname(h, "F patchy-scored")
    compU = sum(1 for s in SEEDS if "FOOD-DEPENDENT" in h[(s, "HU")][fcol])
    compP = sum(1 for s in SEEDS if "FOOD-DEPENDENT" in h[(s, "HP")][fcol])
    print(f"  [H2] COMPASS lines (patchy-scored, attribution FOOD-DEPENDENT): HU {compU}, HP {compP}")
    dF = [first_num(h[(s, "HP")][fcol]) - first_num(h[(s, "HU")][fcol]) for s in SEEDS]
    print(f"  [H3] paired F(HP) - F(HU), patchy-scored: {fmt(dF)}")
    inc = [float(h[(s, "HP")]["income"]) - float(h[(s, "HU")]["income"]) for s in SEEDS]
    print(f"  [H4] side effect, window income HP - HU: {fmt(inc)}")
    bu = [int(h[(s, "HU")]["births"]) for s in SEEDS]
    bp = [int(h[(s, "HP")]["births"]) for s in SEEDS]
    print(f"  [H5] side effect, births: HU {min(bu)}-{max(bu)}, HP {min(bp)}-{max(bp)}; HP more on "
          f"{sum(1 for a, b in zip(bu, bp) if b > a)}/10")
    du = [float(h[(s, "HU")]["depth"]) for s in SEEDS]
    dp = [float(h[(s, "HP")]["depth"]) for s in SEEDS]
    print(f"  [H6] side effect, window depth: HU {min(du):.1f}-{max(du):.1f}, HP {min(dp):.1f}-{max(dp):.1f}")
    print(f"  [H7] quoted: {line_with('runs/RBT-106/H-readout.txt', 'paired F(HP) - F(HU)')}")
    print(f"  [H8] quoted, power at the usable n = 10 (H-readout.txt):")
    for needle in ("| no effect, inflated", "| the prize decides (0.15, 0.60)", "| the uniform prize suffices"):
        print(f"       {line_with('runs/RBT-106/H-readout.txt', needle)}")
    print(f"  [H9] quoted, the H adversary's own-genealogy null: {line_with('runs/RBT-106/h-adversary/ownnull_pool.txt', 'POOLED HP')}")
    print(f"  [H11] quoted, the H adversary's size: {line_with('runs/RBT-106/h-adversary/rederive.txt', 'own-genealogy null q = 0.013')}")
    print(f"        recomputed: P(#HELD(HP) >= 9 of 10 | q = 0.013) = {sum(math.comb(10, i) * 0.013 ** i * 0.987 ** (10 - i) for i in (9, 10)):.2e}")
    n599u = []
    for s in SEEDS:
        r = held_reading(f"runs/RBT-106/HU-{s}/held-599.txt")
        n599u.append(r[1] if r else 0)
    print(f"  [H10] HU planted-rooted living at 599 per seed: {dict(zip(SEEDS, n599u))}; seeds with n = 0: "
          f"{sum(1 for n in n599u if n == 0)}")
    print()

    # Z: RBT-112 -------------------------------------------------------------------
    print("Z. RBT-112: HU (default operator) against HZ (global biases frozen, S = 0), both in the uniform world")
    z = arm_rows("runs/RBT-112/readout.txt")
    fcol = colname(z, "F patchy")
    ucol = colname(z, "F uniform")
    f12 = colname(z, "F12")
    h3, h5 = colname(z, "held 300"), colname(z, "held 599")

    def kpl(cell):
        m = re.match(r"(\d+)\((\d+)\)/(\d+)/(\d+)", cell)
        return tuple(int(x) for x in m.groups())

    zheld = {}
    for arm in ("HU", "HZ"):
        for s in SEEDS:
            a, b = kpl(z[(s, arm)][h3]), kpl(z[(s, arm)][h5])
            zheld[(arm, s)] = a[0] > a[3] and b[0] > b[3] and a[2] > 0 and b[2] > 0
    print(f"  [Z1] HELD: HU {sum(zheld[('HU', s)] for s in SEEDS)}, HZ {sum(zheld[('HZ', s)] for s in SEEDS)} "
          f"(HZ held: {[s for s in SEEDS if zheld[('HZ', s)]]}); LOST (n = 0 at 300 or 599): "
          f"{[s for s in SEEDS if kpl(z[(s, 'HZ')][h3])[2] == 0 or kpl(z[(s, 'HZ')][h5])[2] == 0]}")
    print(f"       quoted: {line_with('runs/RBT-112/readout.txt', 'HELD (each against')}")
    compU = sum(1 for s in SEEDS if "FOOD-DEPENDENT" in z[(s, "HU")][fcol])
    compZ = [s for s in SEEDS if "FOOD-DEPENDENT" in z[(s, "HZ")][fcol]]
    print(f"  [Z2] COMPASS lines: HU {compU}, HZ {len(compZ)} {compZ}")
    dF = [first_num(z[(s, "HZ")][fcol]) - first_num(z[(s, "HU")][fcol]) for s in SEEDS]
    dU = [first_num(z[(s, "HZ")][ucol]) - first_num(z[(s, "HU")][ucol]) for s in SEEDS]
    print(f"  [Z3] paired F(HZ) - F(HU), patchy-scored: {fmt(dF)}; uniform-scored: {fmt(dU)}")
    car = {arm: [int(z[(s, arm)][f12].split("/")[0]) for s in SEEDS] for arm in ("HU", "HZ")}
    print(f"  [Z4] champions carrying a paying planted unit (of 7 per arm): HU {sum(car['HU'])}/70, HZ {sum(car['HZ'])}/70; "
          f"paired HZ - HU per seed {fmt([b - a for a, b in zip(car['HU'], car['HZ'])])}")
    inc = [float(z[(s, "HZ")]["income"]) - float(z[(s, "HU")]["income"]) for s in SEEDS]
    bir = [int(z[(s, "HZ")]["births"]) - int(z[(s, "HU")]["births"]) for s in SEEDS]
    print(f"  [Z5] SE-Z, window income HZ - HU: {fmt(inc)}")
    print(f"  [Z6] births HZ - HU: {fmt(bir)}")
    nz = [kpl(z[(s, 'HZ')][h5])[2] for s in SEEDS]
    nu = [kpl(z[(s, 'HU')][h5])[2] for s in SEEDS]
    print(f"  [Z7] A9's route: planted-rooted living at 599, HZ {sum(nz)} against HU {sum(nu)} of 600; "
          f"paired HZ - HU {fmt([a - b for a, b in zip(nz, nu)])}")
    print(f"  [Z8] quoted: {line_with('runs/RBT-112/readout.txt', 'VERDICT Z:')}")
    print("  [Z9] quoted, the readout adversary's power at the realised n (instrument.txt (2)), P(#HELD(HZ) <= 1):")
    for needle in ("| 0.089 | 0.497", "| 0.120 | 0.528", "| 0.200 | 0.597"):
        row = line_with("runs/RBT-112/readout-adversary/instrument.txt", needle).split("|")
        print(f"       s = {row[1].strip()}: rho 0 / 0.10 / 0.30 -> {row[4].strip()}")
    print(f"  [Z10] quoted, the likelihood of s: {line_with('runs/RBT-112/readout-adversary/instrument.txt', 'rho profile: MLE')}")
    print(f"  [Z11] quoted, the balance point: {line_with('runs/RBT-112/readout-adversary/instrument.txt', 'the balance point')}")
    print(f"  [Z12] quoted, the design anchors at s = 0.2 (power.txt): genealogy "
          f"{line_with('runs/RBT-112/power.txt', '| 0.200 | 0.30 | 0.998').split('|')[6].strip()}, n = 40 "
          f"{line_with('runs/RBT-112/power.txt', '| 0.200 | 0.69 | 0.974').split('|')[6].strip()}  "
          f"(P(#HELD(HZ) <= 1) at the design's n = 10, with n = 7 in brackets)")
    print()

    # M: post hoc arithmetic, this paper ------------------------------------------------
    print("M. POST HOC (this paper): the balance point of instrument.txt's recursion, applied to each measured u")
    for label, u in (("S = 0, u(8)", u8s), ("default, u(8)", u8d), ("default, u(1) (the ticket's 0.29)", u_of(pooled_f(tdef, "pay32", 1), 1))):
        print(f"  [M1] {label} = {u:.3f}: a share can stay above 0 only if s > u / (1 - u) = {u / (1 - u):.3f}")
    print("  [M2] the arms' likelihood interval for s under S = 0 is [0.00, 0.08] (Z10); its upper end is below the S = 0 balance point")
    print()

    # A: RBT-105 -----------------------------------------------------------------------
    print("A. RBT-105 (the co-evolved fauna's oscillator fate; quoted and recomputed)")
    lo, hi = clopper_pearson(5, 14)
    print(f"  [A1] flips 5 of 14 decided replicates from byte-identical founders: rate {5 / 14:.2f}, Clopper-Pearson 95% [{lo:.2f}, {hi:.2f}]"
          f"  (REPORT.md: 0.13-0.65)")
    print(f"  [A2] quoted: {line_with('runs/RBT-105/REPORT.md', 'RMS of a single-seed difference')}")


if __name__ == "__main__":
    main()
