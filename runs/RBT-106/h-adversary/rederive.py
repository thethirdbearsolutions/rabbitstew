"""RBT-106 H readout adversary: re-derive every H number from the committed per-arm files, with code
written here (own regexes, own t quantile, own binomials; nothing imported from readout.py, held.py or
power.py).  No scipy.

  HELD per arm      from held-300.txt / held-599.txt: k_planted > B, re-checked against B recomputed as the
                    95th percentile of Binomial(n, mu) from the printed n and mu (mu printed to 4 d.p.)
  log-excess        log((k_planted + 1) / (n mu + 1)) at 599, paired HP - HU, t(n - 1)
  COMPASS lines     function-patchy.txt: LINE ... FOOD-DEPENDENT and compass FOOD-DEPENDENT
  paired F          function-patchy.txt and function-uniform.txt LINE F, HP - HU, t(n - 1)
  lesion gain       function-patchy.txt "gain (intact - lesioned)", t over lines
  usability         seasons.txt viability, platform.txt, rbt102.txt pc_pass, function-pc.txt FD, commit.txt tree
  power             P(#HP - #HU >= 3), P(#HU >= 5), P(#HP <= 1) under independent Binomial(n, q)
  sensitivity       the same without HP-804, HP-805, HP-806 (their pairs dropped)

Usage: rederive.py [RUNS_DIR]   (default: this file's parent, runs/RBT-106)
"""
import json
import math
import os
import re
import sys

D = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
TREE = "9cc84cde1ac64c596a6f1f2e8708797196f40ab5"


def betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c if abs(1 + aa / c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return h


def ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * betacf(a, b, x) / a
    return 1 - math.exp(lb) * betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * ibeta(df / 2, 0.5, x)
    return 1 - p if t > 0 else p


def t_q975(df):
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < 0.975 else (lo, mid)
    return (lo + hi) / 2


def tint(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = t_q975(n - 1) * sd / math.sqrt(n)
    return m, m - h, m + h


def f3(x):
    return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def binom_pmf(n, q):
    return [math.comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(n + 1)]


def binom_q95(n, mu):
    """smallest B with P(X <= B) >= 0.95"""
    c = 0.0
    for i, p in enumerate(binom_pmf(n, mu)):
        c += p
        if c >= 0.95 - 1e-12:
            return i
    return n


def held(arm, season):
    t = open(os.path.join(D, arm, f"held-{season}.txt")).read()
    m = re.search(r"k_planted = (\d+), n = (\d+), mu = ([0-9.]+), B = (\d+), k_bare = (\d+), depth = (\S+), roots = (\d+) -> (.+)$", t, re.M)
    k, n, mu, B, kb = int(m[1]), int(m[2]), float(m[3]), int(m[4]), int(m[5])
    return dict(k=k, n=n, mu=mu, B=B, kb=kb, depth=m[6].rstrip(","), roots=int(m[7]), call=m[8].strip(),
                B_re=binom_q95(n, mu) if n else 0, excess=math.log((k + 1) / (n * mu + 1)))


def func(arm, name):
    t = open(os.path.join(D, arm, f"function-{name}.txt")).read()
    m = re.search(r"^LINE \S+: (.+?)\s+F ([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]\s+compass (.+?)\s+bodies (\d+)", t, re.M)
    g = re.search(r"gain \(intact - lesioned\)\s+([+-][0-9.]+)", t)
    # the primary call re-derived from the printed interval and zero count, not read from the label
    z = re.search(r"the champion\s+F\s+\S+ \[\s*(\S+),\s*(\S+)\]\s+.*\(zeros (\d+)/(\d+)\)", t)
    lo_, zeros, tot = float(z[1]), int(z[3]), int(z[4])
    fd_re = lo_ > 0 and not zeros > tot / 2
    ret = re.search(r"the decoy retains (\S+)%", t)
    gd = re.search(r"gain - decoy\s+\S+ \[\s*(\S+),\s*(\S+)\]", t)
    gl = re.search(r"gain \(intact - lesioned\)\s+\S+ \[\s*(\S+),", t)
    att_re = ("no compass gain" if not float(gl[1]) > 0 else
              "FOOD-DEPENDENT" if float(ret[1]) < 25 and (float(gd[1]) > 0) == (float(gd[2]) > 0) else "other")
    return dict(call=m[1], fd=m[1] == "FOOD-DEPENDENT", F=float(m[2]), att=m[5], gain=float(g[1]),
                fd_re=fd_re, att_re=att_re, retains=float(ret[1]))


def side(arm):
    rows = [l.split("\t") for l in open(os.path.join(D, arm, "seasons.txt")).read().splitlines()]
    k = rows[0]
    rows = [dict(zip(k, r)) for r in rows[1:] if dict(zip(k, r))["population"] == "conventional"]
    win = [r for r in rows if 300 <= int(r["season"]) <= 599]
    alive = sum(int(r["alive"]) for r in win) / len(win)
    return dict(last=max(int(r["season"]) for r in rows), extinct=any(int(r["alive"]) == 0 for r in rows), alive=alive,
                income=sum(float(r["mean_lifetime_score"]) for r in win) / len(win), births=sum(int(r["births"]) for r in rows))


def usable(arm):
    s = side(arm)
    plat = open(os.path.join(D, arm, "platform.txt")).read().split()[1] == "x86_64"
    a = json.loads(re.search(r"^SUMMARY (\{.*\})$", open(os.path.join(D, arm, "rbt102.txt")).read(), re.M)[1])
    tree = re.search(r"^rabbitstew_tree (\S+)", open(os.path.join(D, arm, "commit.txt")).read(), re.M)[1]
    pc = func(arm, "pc")
    ok = s["last"] >= 599 and not s["extinct"] and s["alive"] >= 30 and plat and a["pc_pass"] and pc["fd_re"] and tree == TREE
    return ok, dict(side=s, plat=plat, pc_pass=a["pc_pass"], pc=pc, tree_ok=tree == TREE)


def read(seeds, label):
    print(f"\n## {label}: seeds {list(seeds)} (n = {len(seeds)})\n")
    print("| seed | arm | usable | k_pl(k_bare)/n/B at 300 | at 599 | B recomputed 300/599 | HELD | log-excess 599 | F patchy | call re-derived | compass re-derived | decoy retains | F uniform | lesion gain |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    R = {}
    for s in seeds:
        for arm in ("HU", "HP"):
            nm = f"{arm}-{s}"
            h3, h5 = held(nm, 300), held(nm, 599)
            fp, fu = func(nm, "patchy"), func(nm, "uniform")
            ok, u = usable(nm)
            H = h3["k"] > h3["B_re"] and h5["k"] > h5["B_re"]
            assert H == (h3["k"] > h3["B"] and h5["k"] > h5["B"]), nm
            R[nm] = dict(H=H, ex=h5["excess"], fp=fp, fu=fu, ok=ok, u=u, kb=h5["kb"])
            print(f"| {s} | {arm} | {ok} | {h3['k']}({h3['kb']})/{h3['n']}/{h3['B']} | {h5['k']}({h5['kb']})/{h5['n']}/{h5['B']} | "
                  f"{h3['B_re']}/{h5['B_re']} | {H} | {h5['excess']:+.3f} | {fp['F']:+.3f} | {fp['fd_re']} | {fp['att_re']} | "
                  f"{fp['retains']:.1f}% | {fu['F']:+.3f} | {fp['gain']:+.3f} |")
    use = [s for s in seeds if R[f"HU-{s}"]["ok"] and R[f"HP-{s}"]["ok"]]
    nU = sum(R[f"HU-{s}"]["H"] for s in use)
    nP = sum(R[f"HP-{s}"]["H"] for s in use)
    ex = [R[f"HP-{s}"]["ex"] - R[f"HU-{s}"]["ex"] for s in use]
    cU = sum(R[f"HU-{s}"]["fp"]["fd_re"] and R[f"HU-{s}"]["fp"]["att_re"] == "FOOD-DEPENDENT" for s in use)
    cP = sum(R[f"HP-{s}"]["fp"]["fd_re"] and R[f"HP-{s}"]["fp"]["att_re"] == "FOOD-DEPENDENT" for s in use)
    aU = sum(R[f"HU-{s}"]["fp"]["fd_re"] for s in use)
    aP = sum(R[f"HP-{s}"]["fp"]["fd_re"] for s in use)
    dF = [R[f"HP-{s}"]["fp"]["F"] - R[f"HU-{s}"]["fp"]["F"] for s in use]
    dFu = [R[f"HP-{s}"]["fu"]["F"] - R[f"HU-{s}"]["fu"]["F"] for s in use]
    gU = [R[f"HU-{s}"]["fp"]["gain"] for s in use]
    gP = [R[f"HP-{s}"]["fp"]["gain"] for s in use]
    inc = [R[f"HP-{s}"]["u"]["side"]["income"] - R[f"HU-{s}"]["u"]["side"]["income"] for s in use]
    print(f"\nusable pairs {len(use)} of {len(seeds)}")
    print(f"HELD: HU {nU}, HP {nP}; paired log-excess HP - HU {f3(tint(ex))}")
    print(f"k_bare at 599: HU {sum(R[f'HU-{s}']['kb'] for s in use)}, HP {sum(R[f'HP-{s}']['kb'] for s in use)}")
    print(f"COMPASS lines: HU {cU}, HP {cP}; primary-only FD: HU {aU}, HP {aP}")
    print(f"lesion gain: HU {f3(tint(gU))}, HP {f3(tint(gP))}")
    print(f"paired F patchy-scored {f3(tint(dF))}; uniform-scored {f3(tint(dFu))}")
    print(f"window income HP - HU {f3(tint(inc))}; HP more births on {sum(R[f'HP-{s}']['u']['side']['births'] > R[f'HU-{s}']['u']['side']['births'] for s in use)}/{len(use)}")
    exl = tint(ex)[1]
    v = ("VOID" if len(use) < 7 else "SUPPORTED" if nP - nU >= 3 and exl > 0 else "FALSIFIED-a" if nU >= 5 and not exl > 0
         else "FALSIFIED-b" if nP <= 1 else "NOT DECIDED")
    print(f"VERDICT (re-derived): {v}")
    return len(use)


def power(n):
    print(f"\n## Power at n = {n} (independent binomials, own code)\n")
    print("| (q_U, q_P) | P(#HP - #HU >= 3) | P(#HU >= 5) | P(#HP <= 1) |\n|---|---|---|---|")
    for qU, qP in ((0.01, 0.01), (0.08, 0.08), (0.15, 0.60), (0.15, 0.40), (0.60, 0.70)):
        pu, pp = binom_pmf(n, qU), binom_pmf(n, qP)
        sup = sum(pu[i] * pp[j] for i in range(n + 1) for j in range(n + 1) if j - i >= 3)
        print(f"| ({qU}, {qP}) | {sup:.3f} | {sum(pu[5:]):.3f} | {sum(pp[:2]):.3f} |")
    for q in (0.007, 0.013):
        pu = binom_pmf(n, q)
        print(f"own-genealogy null q = {q} (ownnull_pool.txt, HP full operator / mutation only): "
              f"P(SUPPORTED count) = {sum(pu[i] * pu[j] for i in range(n + 1) for j in range(n + 1) if j - i >= 3):.2e}; "
              f"P(#HELD(HP) >= 9) = {sum(pu[9:]):.2e}")
    # the size of SUPPORTED's count at the null rates the design measured, and at the worst no-effect q
    worst = max((sum(pu_ * pp_ for i, pu_ in enumerate(binom_pmf(n, q)) for j, pp_ in enumerate(binom_pmf(n, q)) if j - i >= 3), q)
                for q in [x / 1000 for x in range(1, 1000)])
    print(f"max over q (q_U = q_P = q) of P(SUPPORTED count): {worst[0]:.3f} at q = {worst[1]:.3f}")


if __name__ == "__main__":
    print("# RBT-106 H readout adversary: independent re-derivation from committed files")
    print(f"t quantile check: t(0.975; 9) = {t_q975(9):.6f}, t(0.975; 6) = {t_q975(6):.6f}")
    for f in ("HP-801", "HP-4"):
        h = held(f, 150)
        print(f"gate {f} season 150: k_planted {h['k']}, n {h['n']}, mu {h['mu']}, B {h['B']} (recomputed {h['B_re']}) -> {h['call']}")
    n = read(SEEDS, "All ten pairs")
    power(n)
    read((801, 4, 807, 1, 2, 3, 7), "Sensitivity: without HP-804, HP-805, HP-806")
    read((801, 4, 804, 805, 806, 1, 2, 3, 7), "Sensitivity (adversary): without HP-807, whose install increment is not detected (control_increment.txt)")
    read((801, 4, 1, 2, 3, 7), "Sensitivity (adversary): without HP-804, 805, 806 and 807 (n = 6 < MIN_USABLE: would read VOID; counts shown)")
