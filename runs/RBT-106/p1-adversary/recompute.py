"""RBT-106 P1 readout adversary: the P-pair verdict re-derived with independent code (no import of readout.py,
function.py or scipy).

Reads only S1-SEED/ and P1-SEED/ under runs/RBT-106 (never HU-* or HP-*).  From each function-*.txt it takes
the PER-BODY table (intact, decoy, lesion per best) and the zero count, and re-derives:
  primary      F = intact - decoy, t over bodies; FOOD-DEPENDENT iff lo > 0 and zeros <= half the bouts
               (RBT-104 function.py's rule, RBT-38's veto)
  attribution  gain = intact - lesion, decoy = decoy - lesion; "no compass gain" unless gain's lo > 0;
               FOOD-DEPENDENT iff decoy share < 0.25 and gain - decoy excludes zero (RBT-103's rule)
  COMPASS line primary FD and attribution FD (§6.2 as amended by §10.4)
Usability (§6.2 + §10.1): viable (last season >= 599, never extinct, mean designed alive >= 30 over 300..599),
x86_64, analyse.py control passed, install control (function-pc.txt) re-derived FD, rabbitstew tree = c872e80's.
Then the verdict (P-EVOLVED / P-NULL / NOT DECIDED / VOID) on the usable pairs and, as a sensitivity, on all ten.

Usage: python runs/RBT-106/p1-adversary/recompute.py
"""
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R106 = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(R106))
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
WINDOW = (300, 599)


# ---- Student t quantile without scipy: regularized incomplete beta (continued fraction) + bisection ----
def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d; d = 1.0 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1.0 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * _ibeta(df / 2.0, 0.5, x)
    return 1 - p if t > 0 else p


def t_ppf(q, df):
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def tint(v):
    v = np.asarray(v, float)
    n = len(v)
    h = t_ppf(0.975, n - 1) * v.std(ddof=1) / math.sqrt(n)
    return float(v.mean()), float(v.mean() - h), float(v.mean() + h)


def fm(x):
    return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


# ---- parsers of the committed files ----
def per_body(path):
    txt = open(path).read()
    rows = re.findall(r"^g(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+\|", txt, re.M)
    z = re.search(r"^\s+the champion\s+F .*\(zeros (\d+)/(\d+)\)", txt, re.M)
    line = re.search(r"^LINE \S+: (.+?)\s+F ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\]\s+compass (.+?)\s+bodies (\d+)$", txt, re.M)
    world = re.search(r"patches (\d+)", txt).group(1)
    return dict(gens=[int(r[0]) for r in rows], intact=np.array([float(r[1]) for r in rows]),
                decoy=np.array([float(r[2]) for r in rows]), lesion=np.array([float(r[3]) for r in rows]),
                zeros=int(z.group(1)), bouts=int(z.group(2)), world=int(world),
                committed=dict(call=line.group(1), F=float(line.group(2)), lo=float(line.group(3)), hi=float(line.group(4)),
                               att=line.group(5), bodies=int(line.group(6))))


def classify(b):
    F = tint(b["intact"] - b["decoy"])
    veto = b["zeros"] > b["bouts"] / 2
    call = "FOOD-DEPENDENT" if F[1] > 0 and not veto else "VETOED by the zero count" if veto else "NEGATIVE" if F[2] < 0 else "not food-dependent"
    gain, dec = b["intact"] - b["lesion"], b["decoy"] - b["lesion"]
    g, d, gd = tint(gain), tint(dec), tint(gain - dec)
    frac = dec.mean() / gain.mean() if abs(gain.mean()) > 1e-9 else float("nan")
    excl = lambda lo, hi: (lo > 0) == (hi > 0)
    att = ("no compass gain" if not g[1] > 0 else "FOOD-DEPENDENT" if frac < 0.25 and excl(gd[1], gd[2]) else
           "GAIT EFFECT" if frac >= 0.75 and excl(d[1], d[2]) else "UNRESOLVED at this n")
    return dict(F=F, call=call, fd=call == "FOOD-DEPENDENT", att=att, compass=call == "FOOD-DEPENDENT" and att == "FOOD-DEPENDENT",
                gain=g[0], frac=frac)


def seasons(d):
    rows = [l.split("\t") for l in open(os.path.join(d, "seasons.txt")).read().splitlines()]
    k = rows[0]
    rows = [dict(zip(k, r)) for r in rows[1:] if r[1] == "conventional"]
    win = [r for r in rows if WINDOW[0] <= int(r["season"]) <= WINDOW[1]]
    return dict(last=max(int(r["season"]) for r in rows), extinct=any(int(r["alive"]) == 0 for r in rows),
                alive=float(np.mean([int(r["alive"]) for r in win])), income=float(np.mean([float(r["mean_lifetime_score"]) for r in win])),
                births=sum(int(r["births"]) for r in rows))


def held(d, s):
    m = re.search(r"k_planted = (\d+), n = (\d+), mu = ([\d.]+), B = (\d+)", open(os.path.join(d, f"held-{s}.txt")).read())
    k, n, mu, B = int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4))
    return dict(k=k, n=n, mu=mu, B=B, held=k > B, excess=math.log((k + 1) / (n * mu + 1)))


def tree_of(commit):
    return subprocess.run(["git", "-C", ROOT, "rev-parse", f"{commit}:rabbitstew"], capture_output=True, text=True).stdout.strip()


def arm(a, s):
    d = os.path.join(R106, f"{a}-{s}")
    r = dict(arm=a, seed=s)
    r["side"] = seasons(d)
    r["plat"] = open(os.path.join(d, "platform.txt")).read().split()
    summ = json.loads(re.search(r"^SUMMARY (\{.*\})$", open(os.path.join(d, "rbt102.txt")).read(), re.M).group(1))
    r["a_pc"], r["X"], r["depth"] = summ["pc_pass"], summ["X"], summ["window_depth"]
    kv = dict(l.split(None, 1) for l in open(os.path.join(d, "commit.txt")).read().splitlines() if l.strip() and not l.startswith("#"))
    r["commit"], r["tree"] = kv["commit"].strip(), kv["rabbitstew_tree"].strip()
    r["tree_git"] = tree_of(r["commit"])      # the recorded commit's tree, from git itself
    for w in ("pc", "patchy", "uniform"):
        b = per_body(os.path.join(d, f"function-{w}.txt"))
        r[w] = dict(b, **classify(b))
    r["h300"], r["h599"] = held(d, 300), held(d, 599)
    r["HELD"] = r["h300"]["held"] and r["h599"]["held"]
    s_ = r["side"]
    r["viable"] = s_["last"] >= WINDOW[1] and not s_["extinct"] and s_["alive"] >= 30
    r["why"] = [w for w, ok in (("not viable", r["viable"]), ("not x86_64", r["plat"][1] == "x86_64"),
                                ("analyse.py control", r["a_pc"]), ("install control not FD", r["pc"]["fd"]),
                                ("code", r["tree"] == REF_TREE and r["tree_git"] == REF_TREE)) if not ok]
    r["usable"] = not r["why"]
    return r


REF_TREE = None


def verdict(pairs):
    n = len(pairs)
    if n < 7:
        return "VOID", None
    comp = sum(p["patchy"]["compass"] for _, p in pairs)
    d = tint([p["patchy"]["F"][0] - u["patchy"]["F"][0] for u, p in pairs])
    if comp >= 3 and d[1] > 0:
        return "P-EVOLVED", d
    if comp <= 1 and not d[1] > 0:
        return "P-NULL", d
    return "NOT DECIDED", d


def main():
    global REF_TREE
    REF_TREE = tree_of("c872e80")
    print("# RBT-106 P1 readout adversary: the P pair re-derived from the committed per-body tables (independent code, no scipy)\n")
    print(f"t quantiles (own): t.975(6) = {t_ppf(0.975, 6):.5f}, t.975(9) = {t_ppf(0.975, 9):.5f}, t.975(5) = {t_ppf(0.975, 5):.5f}")
    print(f"c872e80:rabbitstew tree (git) = {REF_TREE}\n")
    rows = [(arm("S1", s), arm("P1", s)) for s in SEEDS]
    print("## Per arm: my classification vs the committed LINE (primary call, F, compass attribution); install control\n")
    print("| arm | world pc/patchy/uniform | install control (mine) | committed | patchy primary (mine) | attribution (mine) | decoy share | COMPASS | uniform (mine) | agrees with files | usable (mine) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    mism = 0
    for pr in rows:
        for r in pr:
            ok = all(r[w]["call"] == r[w]["committed"]["call"] and r[w]["att"] == r[w]["committed"]["att"] and
                     abs(r[w]["F"][0] - r[w]["committed"]["F"]) < 0.002 and abs(r[w]["F"][1] - r[w]["committed"]["lo"]) < 0.003
                     and abs(r[w]["F"][2] - r[w]["committed"]["hi"]) < 0.003 and len(r[w]["gens"]) == r[w]["committed"]["bodies"]
                     for w in ("pc", "patchy", "uniform"))
            mism += not ok
            pc = r["pc"]
            print(f"| {r['arm']}-{r['seed']} | {pc['world']}/{r['patchy']['world']}/{r['uniform']['world']} | {pc['call']} {fm(pc['F'])} ({len(pc['gens'])} bodies, zeros {pc['zeros']}/{pc['bouts']}) | "
                  f"{pc['committed']['call']} | {r['patchy']['call']} {fm(r['patchy']['F'])} | {r['patchy']['att']} | {r['patchy']['frac']:.3f} | "
                  f"{r['patchy']['compass']} | {r['uniform']['call']} {fm(r['uniform']['F'])} | {'yes' if ok else 'NO'} | "
                  f"{'USABLE' if r['usable'] else 'UNUSABLE: ' + '; '.join(r['why'])} |")
    print(f"\nclassification mismatches against the committed LINE calls: {mism} of {2 * len(rows)} arms (3 files each)")
    print("\n## Usability inputs\n")
    for pr in rows:
        for r in pr:
            s = r["side"]
            print(f"  {r['arm']}-{r['seed']}: last {s['last']}, extinct {s['extinct']}, alive {s['alive']:.1f}, {r['plat'][1]}, analyse.py pc {r['a_pc']}, "
                  f"commit {r['commit'][:10]} tree(recorded) {r['tree'][:10]} tree(git) {r['tree_git'][:10]}")
    use = [(u, p) for u, p in rows if u["usable"] and p["usable"]]
    print(f"\nusable pairs: {len(use)} of 10 ({', '.join(str(u['seed']) for u, _ in use)}); VOID iff < 7 (§6.2, MIN_USABLE = 7)")
    for label, prs in (("REGISTERED (usable pairs)", use), ("SENSITIVITY (all ten, usability ignored)", rows)):
        v, d = verdict(prs)
        print(f"\n## {label}, n = {len(prs)}")
        print(f"  COMPASS lines: S1 {sum(u['patchy']['compass'] for u, _ in prs)}, P1 {sum(p['patchy']['compass'] for _, p in prs)}"
              f" (P1's: {[p['seed'] for _, p in prs if p['patchy']['compass']]})")
        print(f"  primary-only FD lines: S1 {sum(u['patchy']['fd'] for u, _ in prs)}, P1 {sum(p['patchy']['fd'] for _, p in prs)}")
        print(f"  paired F(P1) - F(S1), patchy-scored, t({len(prs) - 1}): {fm(d)}")
        print(f"  paired F(P1) - F(S1), uniform-scored: {fm(tint([p['uniform']['F'][0] - u['uniform']['F'][0] for u, p in prs]))}")
        print(f"  lesion gain (patchy), mean over lines: S1 {fm(tint([u['patchy']['gain'] for u, _ in prs]))}, P1 {fm(tint([p['patchy']['gain'] for _, p in prs]))}")
        print(f"  HELD: S1 {sum(u['HELD'] for u, _ in prs)}, P1 {sum(p['HELD'] for _, p in prs)}; paired log-excess at 599 P1 - S1: "
              f"{fm(tint([p['h599']['excess'] - u['h599']['excess'] for u, p in prs]))}")
        print(f"  window income P1 - S1: {fm(tint([p['side']['income'] - u['side']['income'] for u, p in prs]))}")
        print(f"  VERDICT P: {v}")
    # a single pair swapped in or out: how far is the verdict from flipping?
    print("\n## Robustness of the registered verdict")
    for u, p in rows:
        if (u, p) in use:
            continue
        v, d = verdict(use + [(u, p)])
        print(f"  + pair {u['seed']} (unusable): n = 8, verdict {v}, paired F {fm(d)}")
    v, d = verdict(use)
    print(f"  P-EVOLVED needs >= 3 COMPASS lines on P1; there are {sum(p['patchy']['compass'] for _, p in use)} usable and "
          f"{sum(p['patchy']['compass'] for _, p in rows)} in all ten.")
    print("\n## Predictions, re-scored\n")
    p1 = [p for _, p in rows]
    print(f"  SE-1: viable P1 {sum(p['viable'] for p in p1)}/10 -> {'HELD' if all(p['viable'] for p in p1) else 'FAILED'}")
    for lab, prs in (("usable", use), ("all ten", rows)):
        x = tint([p['side']['income'] - u['side']['income'] for u, p in prs])
        print(f"  SE-2 ({lab}, n = {len(prs)}): {fm(x)} -> {'HELD' if x[1] > 0 else 'FAILED'}")
    b = sum(p['side']['births'] > u['side']['births'] for u, p in rows)
    dp = sum(p['depth'] > u['depth'] for u, p in rows)
    print(f"  SE-3: births {b}/10, depth {dp}/10 -> {'HELD' if b >= 8 and dp >= 8 else 'FAILED'}")
    nU, nP = sum(u['HELD'] for u, _ in use), sum(p['HELD'] for _, p in use)
    nUa, nPa = sum(u['HELD'] for u, _ in rows), sum(p['HELD'] for _, p in rows)
    print(f"  P-1 (usable): {nP} - {nU} = {nP - nU} -> {'HELD' if nP - nU <= 1 else 'FAILED'};  all ten: {nPa} - {nUa} = {nPa - nUa}")
    X = [round(1000 * p['X']) for p in p1]
    print(f"  P-2: X per 1000 {X}; below 250 on {sum(x < 250 for x in X)}/10 -> {'HELD' if sum(x < 250 for x in X) >= 8 else 'FAILED'}")
    print(f"  P-0: verdict {verdict(use)[0]}")
    return 0 if mism == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
