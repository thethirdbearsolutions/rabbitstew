"""RBT-106: the pre-registered readout across arms (PREREGISTRATION.md §6).  Nothing here is tuned
after an arm was read: every threshold is the pre-registration's and is printed beside its verdict.

Per arm directory D (runs/RBT-106/ARM-SEED, or for RBT-104's S1 the reads RBT-106 makes of it in
runs/RBT-106/S1-SEED, §7.3), from the checkout alone:
  D/seasons.txt           RBT-71's summary (side effects: survival, income, turnover)
  D/platform.txt          machine and MuJoCo: one platform throughout (x86_64)
  D/rbt102.txt            RBT-102's analyse.py, unchanged: readout (a) and its positive control
  D/held-300.txt, held-599.txt   held.py at the window's ends (the "held" reading, §5.1)
  D/function-uniform.txt, function-patchy.txt   RBT-104's function.py on the arm's bests 300..590,
                          scored in each world (the arm's own world directly, the other through
                          cross_world.py): readout (b)
  D/function-pc.txt       function.py --install 32 on the same bests, own world: (b)'s control
A missing file is reported and its seed leaves the rule it feeds; it is never read as a null.
NOT READ is printed until every arm of a pair has finished season 599.

Usage: readout.py [--seeds 801,4,...]
"""
import argparse
import json
import os
import re

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
PAIRS = {"P": ("S1", "P1"), "P8": ("S8", "P8"), "H": ("HU", "HP")}   # (uniform, patchy); P is the primary
WINDOW = tuple(int(x) for x in os.environ.get("RBT106_WINDOW", "300,599").split(","))  # override: smoke tests only
VIABLE_ALIVE = 30
MIN_USABLE = 7            # fewer usable paired seeds: VOID
H_HELD_GAP = 3            # SUPPORTED: #HELD(HP) - #HELD(HU) >= 3 ...
H_HELD_MANY = 5           # FALSIFIED-a: #HELD(HU) >= 5 ...
FEW = 1                   # FALSIFIED-b / P-NULL: at most one seed
P_FD_MANY = 3             # EVOLVED: the patchy arm food-dependent (patchy-scored) on >= 3 usable seeds, AND the paired F interval > 0
                          # (set with power.py layer 4 before any arm: >= 5 with S1 <= 1 had power 0.28 at q = 0.5)


def t_int(v):
    v = np.asarray(v, float)
    if len(v) < 2:
        return (float(v.mean()) if len(v) else float("nan")), float("nan"), float("nan")
    h = float(stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)))
    return float(v.mean()), float(v.mean()) - h, float(v.mean()) + h


def fmt(x):
    return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def arm_dir(arm, seed):
    return os.path.join(HERE, f"{arm}-{seed}")


def side(d):
    p = os.path.join(d, "seasons.txt")
    if not os.path.exists(p):
        return None
    rows = [l.split("\t") for l in open(p).read().splitlines()]
    k = rows[0]
    rows = [dict(zip(k, r)) for r in rows[1:]]
    out = {}
    for pop in ("conventional", "holistic"):
        r = [x for x in rows if x["population"] == pop]
        win = [x for x in r if WINDOW[0] <= int(x["season"]) <= WINDOW[1]]
        last = max(int(x["season"]) for x in r)
        out[pop] = dict(last=last, extinct=any(int(x["alive"]) == 0 for x in r),
                        alive=float(np.mean([int(x["alive"]) for x in win])) if win else 0.0,
                        income=float(np.mean([float(x["mean_lifetime_score"]) for x in win])) if win else float("nan"),
                        births=sum(int(x["births"]) for x in r))
    c = out["conventional"]
    out["viable"] = c["last"] >= WINDOW[1] and not c["extinct"] and c["alive"] >= VIABLE_ALIVE
    out["finished"] = c["last"] >= WINDOW[1]
    return out


def platform_ok(d):
    p = os.path.join(d, "platform.txt")
    return os.path.exists(p) and open(p).read().split()[1] == "x86_64", (open(p).read().strip() if os.path.exists(p) else "missing")


def rbt102(d):
    p = os.path.join(d, "rbt102.txt")
    if not os.path.exists(p):
        return None
    m = re.search(r"^SUMMARY (\{.*\})$", open(p).read(), re.M)
    return json.loads(m.group(1)) if m else None


def held(d, season):
    p = os.path.join(d, f"held-{season}.txt")
    if not os.path.exists(p):
        return None
    m = re.search(r"^HELD seed \d+ season \d+: k = (\d+), n = (\d+), mu = ([\d.]+), B = (\d+) -> (\S+)", open(p).read(), re.M)
    if not m:
        return None
    k, n, mu, B = int(m.group(1)), int(m.group(2)), float(m.group(3)), int(m.group(4))
    return dict(k=k, n=n, mu=mu, B=B, held=k > B, excess=float(np.log((k + 1) / (n * mu + 1))))


def function(d, name):
    p = os.path.join(d, f"function-{name}.txt")
    if not os.path.exists(p):
        return None
    m = re.search(r"^LINE \S+: (FOOD-DEPENDENT|not food-dependent|NEGATIVE|VETOED by the zero count)\s+F ([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\]",
                  open(p).read(), re.M)
    return None if not m else dict(fd=m.group(1) == "FOOD-DEPENDENT", F=float(m.group(2)), lo=float(m.group(3)), hi=float(m.group(4)))


def read_arm(arm, seed):
    d = arm_dir(arm, seed)
    s = side(d)
    ok, plat = platform_ok(d)
    a = rbt102(d)
    r = dict(arm=arm, seed=seed, side=s, platform=plat, platform_ok=ok, rbt102=a,
             held300=held(d, WINDOW[0]), held599=held(d, WINDOW[1]),
             fu=function(d, "uniform"), fp=function(d, "patchy"), pc=function(d, "pc"))
    r["pc_ok"] = bool(a and a.get("pc_pass")) and bool(r["pc"] and r["pc"]["fd"])
    r["usable"] = bool(s and s["viable"] and ok and r["pc_ok"])
    r["HELD"] = bool(r["held300"] and r["held599"] and r["held300"]["held"] and r["held599"]["held"])
    return r


def pair(name, seeds):
    U, P = PAIRS[name]
    rows = [(read_arm(U, s), read_arm(P, s)) for s in seeds]
    print(f"\n## Pair {name}: {U} (uniform) against {P} (patchy), seeds {', '.join(map(str, seeds))}\n")
    unfinished = [f"{r['arm']}-{r['seed']}" for pr in rows for r in pr if not (r["side"] and r["side"]["finished"])]
    if unfinished:
        print(f"NOT READ: {len(unfinished)} arm(s) have not finished season {WINDOW[1]}: {', '.join(unfinished)}")
        return None
    print(f"| seed | arm | platform | viable | pc (a)/(b) | alive | income | births | depth | X per 1000 | held {WINDOW[0]} k/n/B | held {WINDOW[1]} k/n/B | HELD | F uniform-scored | F patchy-scored |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for pr in rows:
        for r in pr:
            s, a = r["side"], r["rbt102"] or {}
            h = lambda x: f"{x['k']}/{x['n']}/{x['B']}" if x else "missing"
            f = lambda x: (f"{x['F']:+.3f} {'FD' if x['fd'] else '-'}" if x else "missing")
            print(f"| {r['seed']} | {r['arm']} | {r['platform']} | {s['viable']} | {a.get('pc_pass')}/{bool(r['pc'] and r['pc']['fd'])} | "
                  f"{s['conventional']['alive']:.1f} | {s['conventional']['income']:.3f} | {s['conventional']['births']} | "
                  f"{a.get('window_depth', float('nan')):.1f} | {1000 * a.get('X', float('nan')):.0f} | {h(r['held300'])} | {h(r['held599'])} | "
                  f"{r['HELD']} | {f(r['fu'])} | {f(r['fp'])} |")
    bad = [f"{r['arm']}-{r['seed']}" for pr in rows for r in pr if not r["platform_ok"]]
    if bad:
        print(f"\nWARNING: not on x86_64: {', '.join(bad)} (RBT-96); these arms are unusable")
    use = [(u, p) for u, p in rows if u["usable"] and p["usable"]]
    print(f"\nusable paired seeds: {len(use)} of {len(rows)} (viable, x86_64, both positive controls)")
    nU, nP = sum(u["HELD"] for u, _ in use), sum(p["HELD"] for _, p in use)
    ex = [p["held599"]["excess"] - u["held599"]["excess"] for u, p in use if u["held599"] and p["held599"]]
    fdU = sum(bool(u["fp"] and u["fp"]["fd"]) for u, _ in use)
    fdP = sum(bool(p["fp"] and p["fp"]["fd"]) for _, p in use)
    dF = [p["fp"]["F"] - u["fp"]["F"] for u, p in use if u["fp"] and p["fp"]]
    dFu = [p["fu"]["F"] - u["fu"]["F"] for u, p in use if u["fu"] and p["fu"]]
    inc = [p["side"]["conventional"]["income"] - u["side"]["conventional"]["income"] for u, p in use]
    print(f"HELD: {U} {nU}, {P} {nP};  paired log-excess at 599, {P} - {U}: {fmt(t_int(ex))}")
    print(f"food-dependent lines, patchy-scored: {U} {fdU}, {P} {fdP};  paired F({P}) - F({U}), patchy-scored {fmt(t_int(dF))}, "
          f"uniform-scored {fmt(t_int(dFu))}")
    print(f"side effect, window income {P} - {U}: {fmt(t_int(inc))}")
    exl = t_int(ex)[1]
    fl = t_int(dF)[1]
    if len(use) < MIN_USABLE:
        v = f"VOID (fewer than {MIN_USABLE} usable paired seeds)"
    elif name == "H":
        if nP - nU >= H_HELD_GAP and exl > 0:
            v = "SUPPORTED: the larger prize held the paying compass where the uniform prize did not"
        elif nU >= H_HELD_MANY and not exl > 0:
            v = "FALSIFIED-a: the uniform prize already held it; the ~3x prize added nothing measurable"
        elif nP <= FEW:
            v = "FALSIFIED-b: not even the ~3x prize held it against the operator"
        else:
            v = "NOT DECIDED at this n"
        v += f"   [rules: SUPPORTED #HELD(HP) - #HELD(HU) >= {H_HELD_GAP} and paired log-excess interval > 0; " \
             f"FALSIFIED-a #HELD(HU) >= {H_HELD_MANY} and that interval not > 0; FALSIFIED-b #HELD(HP) <= {FEW}]"
        fv = ("FUNCTION FOLLOWS" if fdP >= P_FD_MANY and fl > 0 else "FUNCTION DOES NOT FOLLOW" if fdP <= FEW and not fl > 0 else "FUNCTION UNDECIDED")
        v += f"\n  function (reported, not in the verdict): {fv}"
    else:
        k = "" if name == "P" else "8"
        if fdP >= P_FD_MANY and fl > 0:
            v = f"{name}-EVOLVED: in the patchy world the planted compass became food-dependent champions (K = {k or 1})"
        elif fdP <= FEW and not fl > 0:
            v = f"{name}-NULL: no food-dependent champion line in the patchy world beyond one (worded against §6.3's power)"
        else:
            v = "NOT DECIDED at this n"
        v += f"   [rules: {name}-EVOLVED {P} FD >= {P_FD_MANY} and paired F({P}) - F({U}) interval > 0 (patchy-scored); " \
             f"{name}-NULL {P} FD <= {FEW} and that interval not > 0]"
        v += f"\n  structure (reported, not in the verdict; criterion {'same' if name == 'P' else 'pay64'}): HELD {U} {nU}, {P} {nP}"
    print(f"\nVERDICT {name}: {v}")
    return v


def factorial(seeds):
    """The 2 x 2 of reach (K = 1, 8) x prize (uniform, patchy) on the w = 1 founders (§6.2)."""
    cells = ("S1", "P1", "S8", "P8")
    print("\n## The factorial: reach x prize (S1 uniform K1, P1 patchy K1, S8 uniform K8, P8 patchy K8)\n")
    rows = {s: {c: read_arm(c, s) for c in cells} for s in seeds}
    unfinished = [f"{c}-{s}" for s in seeds for c in cells if not (rows[s][c]["side"] and rows[s][c]["side"]["finished"])]
    if unfinished:
        print(f"NOT READ: {len(unfinished)} cell arm(s) not finished: {', '.join(unfinished)}")
        return None
    use = [s for s in seeds if all(rows[s][c]["usable"] and rows[s][c]["fp"] for c in cells)]
    print(f"usable seeds (all four cells usable and scored): {len(use)} of {len(seeds)}")
    fd = {c: sum(rows[s][c]["fp"]["fd"] for s in use) for c in cells}
    F = {c: [rows[s][c]["fp"]["F"] for s in use] for c in cells}
    I = [(F["P8"][i] - F["P1"][i]) - (F["S8"][i] - F["S1"][i]) for i in range(len(use))]
    prize1 = [F["P1"][i] - F["S1"][i] for i in range(len(use))]
    prize8 = [F["P8"][i] - F["S8"][i] for i in range(len(use))]
    print("food-dependent lines (patchy-scored): " + ", ".join(f"{c} {fd[c]}" for c in cells))
    print(f"prize effect at K = 1, F(P1) - F(S1): {fmt(t_int(prize1))};  at K = 8, F(P8) - F(S8): {fmt(t_int(prize8))}")
    print(f"INTERACTION I = [F(P8) - F(P1)] - [F(S8) - F(S1)], patchy-scored, t({len(use) - 1}): {fmt(t_int(I))}")
    il, p1l, p8l = t_int(I)[1], t_int(prize1)[1], t_int(prize8)[1]
    reach1 = [F["S8"][i] - F["S1"][i] for i in range(len(use))]
    r1l = t_int(reach1)[1]
    print(f"reach effect in the uniform world, F(S8) - F(S1): {fmt(t_int(reach1))}")
    prize_ok = fd["P1"] >= P_FD_MANY and p1l > 0
    reach_ok = fd["S8"] >= P_FD_MANY and r1l > 0
    if len(use) < MIN_USABLE:
        v = f"VOID (fewer than {MIN_USABLE} seeds with all four cells usable)"
    elif prize_ok and reach_ok:
        v = "EACH SUFFICES: the prize alone (K = 1) and the reach alone (uniform) each evolved food-dependent champions"
    elif prize_ok:
        v = "PRIZE SUFFICES: at the default reach the patchy world evolved food-dependent champions"
    elif reach_ok:
        v = "REACH SUFFICES: at K = 8 the uniform world evolved them (RBT-104's own verdict governs RBT-104)"
    elif il > 0 and fd["P8"] >= P_FD_MANY and fd["P1"] <= FEW and fd["S8"] <= FEW:
        v = "BOTH NEEDED: only reach AND prize together evolved food-dependent champions (positive interaction)"
    elif max(fd.values()) <= FEW and not (il > 0 or p1l > 0 or p8l > 0 or r1l > 0):
        v = "NEITHER, at K = 8 and a 2.5x prize: no cell evolved food-dependent champions beyond one line (against §6.3's power)"
    else:
        v = "NOT DECIDED at this n"
    print(f"\nVERDICT FACTORIAL: {v}\n  [rules, in order: PRIZE SUFFICES P1 FD >= {P_FD_MANY} and F(P1) - F(S1) interval > 0; "
          f"REACH SUFFICES S8 FD >= {P_FD_MANY} and F(S8) - F(S1) interval > 0 (both: EACH SUFFICES); BOTH NEEDED I's interval > 0, "
          f"P8 FD >= {P_FD_MANY}, P1 and S8 FD <= {FEW}; NEITHER every cell FD <= {FEW} and no paired interval > 0]")
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    ap.add_argument("--pairs", default="P,P8,H", help="the pairs to read; P8 and H only if their options were run")
    ap.add_argument("--factorial", action="store_true", help="also read the 2 x 2 (needs S1, P1, S8, P8)")
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(",")]
    print("# RBT-106 readout: does the prize decide whether a compass is held or evolved?")
    print(f"window seasons {WINDOW[0]}-{WINDOW[1]}; seeds {seeds}")
    for name in a.pairs.split(","):
        pair(name, seeds)
    if a.factorial:
        factorial(seeds)


if __name__ == "__main__":
    main()
