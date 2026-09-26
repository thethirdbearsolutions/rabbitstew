"""Paper 9: re-derive the summary table and the power figures from committed readouts.

Reads only committed text files on the integration branch (no bulk, no ckpt, no new run):

  runs/RBT-92/readout.txt                          C1 per-seed R-shift, both faunas, recovery window
  runs/RBT-92/readout-adversary/probe_readout.txt  C1 placebo onsets (P3)
  runs/RBT-99/placebo.txt                          C2 placebo onsets (P3), per-seed event - base (P4)
  runs/RBT-99/price.txt                            C2 per-seed price, 0.05 x pre-onset kJ
  runs/RBT-100/placebo.txt                         C3 placebo onsets (P3), per-seed event - base (P4)
  runs/RBT-100/score.txt                           C3 per-seed price (food/2), section 1
  runs/RBT-100/readout-adversary/probe_readout.txt C3 paired A/A-like RMS (P5), insolvent end (P2)
  runs/RBT-96/REPORT.md                            arena A/A RMS (section 3), quoted not parsed
  runs/RBT-101/placebo.txt                         C4 placebo onsets (P3), event - base and event - null (P4)
  runs/RBT-101/readout-adversary/probe_arena.txt   C4 arena predictor Z10 and its residual (post hoc)
  runs/RBT-101/readout-adversary/probe_refund.txt  C4 same-season split: refund, response, total, simulated C0 (post hoc)
  runs/RBT-101/arith.txt                           C4 registered prior (solo probe), per-seed paired prediction
  runs/RBT-92/readout-adversary/probe_readout.txt  C1 full-precision R-shift and paired lines (P4)

Prints docs/paper-9/rederive.txt.  Run from the repository root:

    python docs/paper-9/rederive.py > docs/paper-9/rederive.txt

Row ids in brackets ([S1], [P3] ...) are the ones the paper cites.
"""
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEEDS = [801, 804, 805, 806, 807, 1, 2, 3, 4, 7]

# --- Student t quantiles, no scipy -----------------------------------------

def _t_cdf(x, df):
    # regularised incomplete beta via continued fraction (Numerical Recipes betacf)
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


def mde(sd, n, power=0.80):
    """Minimum detectable mean difference, two-sided 5%, at the given power (RBT-100 adversary P4's form)."""
    return (tq(0.975, n - 1) + tq(power, n - 1)) * sd / math.sqrt(n)


def n_for(sd, target, power=0.80):
    n = 3
    while mde(sd, n, power) > target and n < 2000:
        n += 1
    return n


# --- parsers -----------------------------------------------------------------

def read(rel):
    return (ROOT / rel).read_text()


def per_seed(line):
    return [float(v) for v in re.search(r"per seed \[([^\]]*)\]", line).group(1).split(",")]


def placebo_count(text):
    block = text[text.index("placebo onsets"):]
    calls = re.findall(r"T[ +\-]*\d+\s*:\s*([A-F]\d?)\b", block.split("class A fires")[0])
    if not calls:  # RBT-92 adversary's long form
        calls = re.findall(r"->\s*([A-F]\d?)\s*$", block.split("class A fires")[0], re.M)
    return sum(1 for c in calls if c == "A"), len(calls)


def line_with(text, *needles):
    for ln in text.splitlines():
        if all(nd in ln for nd in needles):
            return ln
    raise KeyError(needles)


def main():
    out = []
    p = out.append
    p("Paper 9 (RBT-109): re-derivation of the summary table and the power figures, committed files only.")
    p("")

    # C1 ---------------------------------------------------------------------
    r92 = read("runs/RBT-92/readout.txt")
    hol = per_seed(line_with(r92, "R-shift  holistic     recovery"))
    con = per_seed(line_with(r92, "R-shift  conventional recovery"))
    c1 = [h - c for h, c in zip(hol, con)]
    a92, n92 = placebo_count(read("runs/RBT-92/readout-adversary/probe_readout.txt"))
    p("C1 crowding (RBT-92), recovery window [T+60, T+160)")
    p(f"  [S1] co-evolved R-shift            {fmt(hol)}")
    p(f"  [S2] designed R-shift              {fmt(con)}")
    p(f"  [S3] paired event - base           {fmt(c1)}   (no arithmetic was registered for C1)")
    adv92 = read("runs/RBT-92/readout-adversary/probe_readout.txt")
    p("  [S1f] full precision, quoted: " + line_with(adv92, "holistic R-shift recovery: mean").strip())
    p("  [S3f] full precision, quoted: " + line_with(adv92, "difference (holistic - designed)").strip())
    p(f"  [S4] class A on placebo onsets     {a92}/{n92}")
    sd1 = stat(c1)[3]
    p(f"  [S5] MDE of the paired effect, n = 10, 80% power: {mde(sd1, 10):.3f}")
    p("")

    # C2 ---------------------------------------------------------------------
    pl99 = read("runs/RBT-99/placebo.txt")
    obs2 = per_seed(line_with(pl99, "event - base, R-body"))
    price = {}
    for ln in read("runs/RBT-99/price.txt").splitlines()[2:]:
        f = ln.split()
        price[(int(f[0]), f[1])] = float(f[6])
    ar2 = [price[(s, "conventional")] - price[(s, "holistic")] for s in SEEDS]
    res2 = [o - a for o, a in zip(obs2, ar2)]
    a99, n99 = placebo_count(pl99)
    p("C2 dearer work (RBT-99), recovery window")
    p(f"  [S6] arithmetic paired prediction  {fmt(ar2)}   (price designed - price co-evolved, price.txt)")
    p(f"  [S7] observed paired event - base  {fmt(obs2)}")
    p("  [S7f] full precision, quoted: " + line_with(pl99, "event - base, R-body").split("per seed")[0].strip())
    p(f"  [S8] residual observed - arithmetic {fmt(res2)}")
    p(f"  [S9] class A on placebo onsets     {a99}/{n99}")
    sd2 = stat(res2)[3]
    p(f"  [S10] MDE of the residual, n = 10, 80% power: {mde(sd2, 10):.3f}")
    kj_h = sum(price[(s, 'holistic')] for s in SEEDS) / 10 / 0.05
    kj_c = sum(price[(s, 'conventional')] for s in SEEDS) / 10 / 0.05
    p(f"  [S11] mean pre-onset kJ co-evolved {kj_h:.2f}, designed {kj_c:.2f}, ratio {kj_c / kj_h:.2f}")
    # Lesson 7 applied to C2 after the fact (paper 9's own re-derivation, post hoc): the unchanged designed
    # fauna's income at 0.08 is its base recovery income minus its price, below basal on every seed. Scored as
    # the extinct population that implies (axis 0), its R-shift is -base income; the co-evolved fauna stays
    # alive at -price. Base designed recovery income per seed is the 'base con inc' column of the C2 readout
    # adversary's P2 table.
    adv99 = read("runs/RBT-99/readout-adversary/probe_readout.txt")
    base_con = {}
    for ln in adv99[adv99.index("P2 ARITHMETIC"):adv99.index("all ten:")].splitlines():
        f = ln.split()
        if f and f[0].isdigit() and len(f) >= 14:
            base_con[int(f[0])] = float(f[12])
    ins2 = [base_con[s] - price[(s, "holistic")] for s in SEEDS]
    p(f"  [S11b] insolvent end (post hoc, lesson 7 applied by paper 9): {fmt(ins2)}")
    p(f"  [S11c] residual against the insolvent end {fmt([o - a for o, a in zip(obs2, ins2)])}")
    p(f"  [S11d] unchanged designed income at 0.08 (base - price), range "
      f"{min(base_con[s] - price[(s, 'conventional')] for s in SEEDS):+.3f} .. "
      f"{max(base_con[s] - price[(s, 'conventional')] for s in SEEDS):+.3f}")
    p("")

    # C3 ---------------------------------------------------------------------
    pl100 = read("runs/RBT-100/placebo.txt")
    obs3 = per_seed(line_with(pl100, "event - base, R-body"))
    sc = read("runs/RBT-100/score.txt")
    ar3 = {}
    for ln in sc.splitlines():
        m = re.match(r"\s+(\d+)\s+(\d+) \|\s+([\d.]+) ([\d.]+) ([+\-][\d.]+) ([\d.]+) ([+\-][\d.]+)\s+\|\s+([\d.]+) ([\d.]+) ([+\-][\d.]+) ([\d.]+) ([+\-][\d.]+)", ln)
        if m:
            ar3[int(m.group(1))] = float(m.group(11)) - float(m.group(6))
    ar3 = [ar3[s] for s in SEEDS]
    res3 = [o - a for o, a in zip(obs3, ar3)]
    a100, n100 = placebo_count(pl100)
    adv = read("runs/RBT-100/readout-adversary/probe_readout.txt")
    insolvent = line_with(adv, "extinction-consistent")
    pooled = line_with(adv, "pooled paired A/A-like RMS")
    p("C3 scarce food (RBT-100), recovery window")
    p(f"  [S12] arithmetic, alive end        {fmt(ar3)}   (price designed - price co-evolved, score.txt section 1)")
    p(f"  [S13] observed paired event - base {fmt(obs3)}")
    p("  [S13f] full precision, quoted: " + line_with(pl100, "event - base, R-body").split("per seed")[0].strip())
    p("  [S13n] event - null, quoted: " + line_with(pl100, "event - null, R-body").split("per seed")[0].strip())
    p(f"  [S14] residual against the alive end {fmt(res3)}")
    p(f"  [S15] insolvent end (quoted from the readout adversary's P2): {insolvent.strip()}")
    p(f"  [S16] class A on placebo onsets    {a100}/{n100}")
    sd3 = stat(res3)[3]
    p(f"  [S17] MDE of the residual, n = 10, 80% power: {mde(sd3, 10):.3f}")
    p("")

    # C4 ---------------------------------------------------------------------
    pl101 = read("runs/RBT-101/placebo.txt")
    obs4 = per_seed(line_with(pl101, "event - base, R-body"))
    a101, n101 = placebo_count(pl101)
    ar = read("runs/RBT-101/readout-adversary/probe_arena.txt")
    z10 = per_seed(line_with(ar, "paired, [T, T+10)"))
    res4 = [o - z for o, z in zip(obs4, z10)]
    p("C4 flat terrain (RBT-101), recovery window; reported apart from C1-C3")
    p(f"  [S18] observed paired event - base {fmt(obs4)}")
    p("  [S18f] full precision, quoted: " + line_with(pl101, "event - base, R-body").split("per seed")[0].strip())
    p("  [S19] event - null, quoted: " + line_with(pl101, "the 10 seeds where the cull did not empty").split("per seed")[0].strip())
    p(f"  [S20] class A on placebo onsets    {a101}/{n101}")
    p(f"  [S21] arena arithmetic Z10 (post hoc, the readout adversary's) {fmt(z10)}")
    p(f"  [S22] residual observed - Z10 (post hoc) {fmt(res4)}")
    p("  [S22f] quoted: " + line_with(ar, "observed - Z10 ([T, T+10))").split("per seed")[0].strip())
    sd4 = stat(res4)[3]
    p(f"  [S23] MDE of the residual, n = 10, 80% power: {mde(sd4, 10):.3f}")
    rf = read("runs/RBT-101/readout-adversary/probe_refund.txt")
    p("  [S24] same-season split, simulated total, quoted: " + line_with(rf, "TOTAL (simulated event - base)").split("per seed")[0].strip())
    p("  [S25] same-season split, paired refund at T+110, quoted: " + line_with(rf, "REFUND at T+110 ").split("per seed")[0].strip())
    p("  [S26] same-season split, paired response at T+110, quoted: " + line_with(rf, "RESPONSE at T+110 ").split("per seed")[0].strip())
    p("  [S27] simulated C0 refund, paired, quoted: " + line_with(rf, "   C0 refund   ").split("per seed")[0].strip())
    p("  [S27b] designed response, flat, quoted: " + [l for l in rf.splitlines() if "RESPONSE at T+110: shift pop" in l][1].split("per seed")[0].strip())
    p("  [S27c] designed response, random, quoted: " + [l for l in rf.splitlines() if "the same on random terrain" in l][1].split("per seed")[0].strip())
    ari = read("runs/RBT-101/arith.txt")
    prior = per_seed(line_with(ari, "paired (co-evolved - designed): predicted"))
    p(f"  [S28] registered prior (solo probe), paired prediction {fmt(prior)}")
    p(f"  [S29] residual against the registered prior, undiscounted {fmt([o - a for o, a in zip(obs4, prior)])}")
    half = [a / 2 for a in prior]
    p(f"  [S30] registered prior with the registered half-discount (Amendment 2) {fmt(half)}")
    p(f"  [S31] residual against the half-discounted prior {fmt([o - a for o, a in zip(obs4, half)])}")
    p("")

    # Power ------------------------------------------------------------------
    aa = float(re.search(r"RMS \(20 seed-contrasts\): ([\d.]+)", pooled).group(1))
    p("POWER: minimum detectable mean paired difference (two-sided 5%, 80% power) by n seeds, and the n for 0.10 / 0.05")
    p("  the sd is each contrast's own between-seed sd at n = 10 (or the A/A RMS), taken as the planning value")
    rows = [
        ("P1", "ecology paired A/A-like RMS (RBT-100 adversary P5)", aa),
        ("P2", "C1 paired event - base, sd", sd1),
        ("P3", "C2 residual over arithmetic, sd", sd2),
        ("P4", "C3 residual over the alive end, sd", sd3),
        ("P5", "arena A/A RMS (RBT-96 section 3, quoted)", 0.128),
    ]
    ns = [10, 16, 20, 30, 40]
    p("  " + "row  planning sd".ljust(62) + "".join(f"n={n:<6}" for n in ns) + "n@0.10  n@0.05")
    for rid, name, sd in rows:
        p(f"  [{rid}] {name:<52} {sd:.3f}  " + "".join(f"{mde(sd, n):.3f}  " for n in ns)
          + f"{n_for(sd, 0.10):<7} {n_for(sd, 0.05)}")
    p("")
    p("  [P6] The SE of a ten-seed mean on the paired A/A scale: "
      f"{aa / math.sqrt(10):.3f}; a 95% half-width of 0.10 on that scale needs n = "
      f"{next(n for n in range(3, 500) if tq(0.975, n - 1) * aa / math.sqrt(n) <= 0.10)}")
    print("\n".join(out))


if __name__ == "__main__":
    sys.exit(main())
