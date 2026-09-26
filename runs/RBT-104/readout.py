"""RBT-104: the pre-registered readout across arms (PREREGISTRATION.md sections 4 and 6).

Reads, per seed in SEEDS, from the checkout alone:
  runs/RBT-104/{S1,S8,U8}-SEED/seasons.txt      RBT-71's summary (side effects)
  runs/RBT-104/{S1,S8,U8}-SEED/rbt102.txt       RBT-102's analyse.py, unchanged (readout a)
  runs/RBT-104/{S1,S8,U8}-SEED/function.txt     function.py on the arm's bests 300..590 (readout b)
  runs/RBT-104/{S1,S8,U8}-SEED/function-pc.txt  function.py --install 32 on the same bests (b's control)
  runs/RBT-90/forage-SEED/seasons.txt           part 2, the U8 arm's control (cited, byte-identical)
  runs/RBT-102/arm-SEED.txt                     part 2 through readout (a), already committed
  runs/RBT-104/part2-SEED-function.txt          part 2 through readout (b)

and prints every rule's inputs beside its verdict.  A missing file is reported and its seed leaves
the rule it feeds; it is never read as a null.  Nothing here is tuned after an arm was read: the
thresholds are the pre-registration's and are printed.

Usage: readout.py [--seeds 801,804,...]
"""
import argparse
import json
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
WINDOW = tuple(int(x) for x in os.environ.get("RBT104_WINDOW", "300,599").split(","))  # override: smoke tests only
RUNG_64 = 24.7145     # links-alone reading of the installed routed motif at a = 64 (probe_rung.txt)
VIABLE_ALIVE = 30     # an arm is viable if its designed fauna never dies out and averages >= 30 alive in the window
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


def t_int(v):
    v = np.asarray(v, float)
    if len(v) < 2:
        return (float(v.mean()) if len(v) else float("nan")), float("nan"), float("nan")
    se = float(np.std(v, ddof=1) / np.sqrt(len(v)))
    t = T975.get(len(v) - 1, 1.96)
    return float(v.mean()), float(v.mean() - t * se), float(v.mean() + t * se)


def fmt(m, lo, hi):
    return f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def seasons(path):
    if not os.path.exists(path):
        return None
    rows = [l.split("\t") for l in open(path).read().splitlines()]
    k = rows[0]
    out = [dict(zip(k, r)) for r in rows[1:] if r[k.index("population")] == "conventional"]
    return out


def side(path):
    """(viable, window mean alive, window mean of mean lifetime score, births, deaths, last season)."""
    rows = seasons(path)
    if rows is None:
        return None
    win = [r for r in rows if WINDOW[0] <= int(r["season"]) <= WINDOW[1]]
    last = max(int(r["season"]) for r in rows)
    alive = np.mean([int(r["alive"]) for r in win]) if win else 0.0
    inc = np.mean([float(r["mean_lifetime_score"]) for r in win]) if win else float("nan")
    viable = last >= WINDOW[1] and all(int(r["alive"]) > 0 for r in rows) and alive >= VIABLE_ALIVE
    return dict(viable=viable, alive=float(alive), income=float(inc),
                births=sum(int(r["births"]) for r in rows), deaths=sum(int(r["deaths"]) for r in rows), last=last)


def rbt102(path):
    """RBT-102 analyse.py summary, plus the window carriers re-signed on their OWN links against
    the like-for-like a = 64 rung (the analyse table prints links-alone a and heading per carrier)."""
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    m = re.search(r"^SUMMARY (\{.*\})$", txt, re.M)
    if not m:
        return None
    s = json.loads(m.group(1))
    paying = 0
    for row in re.finditer(r"^\| (\S+) \| \d+ \| \d+ \| [-+]\d+\.\d+ \| ([-+]\d+\.\d+) \| ([-+]\d+\.\d+) \| [\d.]+ \| [-+]\d+\.\d+ \| (COMPASS|ANTI-COMPASS) \|", txt, re.M):
        la, h = float(row.group(2)), float(row.group(3))
        signed = la if abs(h) > 90 else -la  # RBT-102's rule: the published motif is the compass for a backward driver
        paying += signed >= RUNG_64
    s["paying_compass_carriers"] = paying
    return s


def function(path):
    """function.py's LINE: (verdict, F per population mean, lo, hi, compass attribution)."""
    if not os.path.exists(path):
        return None
    num = r"([-+]?(?:\d+\.\d+|nan))"
    m = re.search(rf"^LINE \S+: (.+?)  F {num} \[{num}, {num}\]  compass (.+?)  bodies (\d+)", open(path).read(), re.M)
    if not m:
        return None
    return dict(verdict=m.group(1), F=float(m.group(2)), lo=float(m.group(3)), hi=float(m.group(4)),
                compass=m.group(5), bodies=int(m.group(6)), fd=m.group(1) == "FOOD-DEPENDENT")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default=None)
    a = ap.parse_args()
    seeds = SEEDS if not a.seeds else tuple(int(x) for x in a.seeds.split(","))
    R = lambda *p: os.path.join(ROOT, *p)
    D = {}
    for s in seeds:
        for arm in ("S1", "S8", "U8"):
            d = R("runs", "RBT-104", f"{arm}-{s}")
            D[(arm, s)] = dict(side=side(os.path.join(d, "seasons.txt")), a=rbt102(os.path.join(d, "rbt102.txt")),
                               b=function(os.path.join(d, "function.txt")), pc=function(os.path.join(d, "function-pc.txt")))
        D[("P2", s)] = dict(side=side(R("runs", "RBT-90", f"forage-{s}", "seasons.txt")),
                            a=rbt102(R("runs", "RBT-102", f"arm-{s}.txt")),
                            b=function(R("runs", "RBT-104", f"part2-{s}-function.txt")), pc=None)

    print("# RBT-104 readout: is magnitude the cause?\n")
    print(f"seeds {list(seeds)}; window seasons {WINDOW[0]}-{WINDOW[1]}; viable = never extinct, reached season "
          f"{WINDOW[1]}, window mean alive >= {VIABLE_ALIVE}; a = 64 rung on own links {RUNG_64}\n")
    missing = [f"{arm}-{s}:{k}" for (arm, s), v in D.items() for k, x in v.items() if x is None and not (arm == "P2" and k == "pc")]
    if missing:
        print(f"MISSING (each leaves the rules it feeds, never read as a null): {', '.join(missing)}\n")

    print("## Per seed\n")
    print("| seed | arm | viable | alive | income | pc(a) | X (carriage) | paying compass carriers | de novo | pc(b) | F (real - decoy) | champions |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in seeds:
        for arm in ("P2", "U8", "S1", "S8"):
            v = D[(arm, s)]
            sd, ra, fb, pc = v["side"], v["a"], v["b"], v["pc"]
            dash = "—"
            cells = [
                dash if not sd else ("yes" if sd["viable"] else "NO"),
                dash if not sd else f"{sd['alive']:.1f}",
                dash if not sd else f"{sd['income']:+.3f}",
                dash if not ra else ("PASS" if ra["pc_pass"] else "FAIL"),
                dash if not ra else f"{1000 * ra['X']:.1f}/1000",
                dash if not ra else str(ra["paying_compass_carriers"]),
                dash if not ra else str(ra["de_novo"]),
                dash if arm == "P2" or not pc else ("PASS" if pc["fd"] else "FAIL"),
                dash if not fb else fmt(fb["F"], fb["lo"], fb["hi"]),
                dash if not fb else fb["verdict"],
            ]
            print(f"| {s} | {arm} | " + " | ".join(cells) + " |")

    def paired(arm1, arm0, get):
        xs = [(s, get(D[(arm1, s)]), get(D[(arm0, s)])) for s in seeds]
        xs = [(s, x1, x0) for s, x1, x0 in xs if x1 is not None and x0 is not None]
        return xs, t_int([x1 - x0 for _, x1, x0 in xs])

    print("\n## 1. Side effects of the reach (income is the window mean of mean lifetime score)\n")
    for arm1, arm0, what in (("U8", "P2", "reach alone: U8 - part 2 (the cited control)"), ("S8", "S1", "reach with the seed: S8 - S1")):
        for key in ("income", "alive"):
            xs, (m, lo, hi) = paired(arm1, arm0, lambda v: v["side"][key] if v["side"] else None)
            print(f"  {what:44s} {key:6s} n={len(xs)}  {fmt(m, lo, hi)}")
        via = sum(1 for s in seeds if D[(arm1, s)]["side"] and D[(arm1, s)]["side"]["viable"])
        print(f"  {arm1} viable on {via} of {len(seeds)}")

    ok_pc = lambda v: v["a"] is not None and v["a"]["pc_pass"] and v["pc"] is not None and v["pc"]["fd"]
    usable = lambda arm, s: (D[(arm, s)]["side"] is not None and D[(arm, s)]["side"]["viable"] and ok_pc(D[(arm, s)])
                             and D[(arm, s)]["b"] is not None)
    print("\n## 2. Readout (a): structure\n")
    xs, (m, lo, hi) = paired("S8", "S1", lambda v: v["a"]["X"] if v["a"] else None)
    print(f"  carriage X, S8 - S1, paired over seeds: n={len(xs)}  {fmt(1000 * m, 1000 * lo, 1000 * hi)} per 1000")
    pay8 = sum(D[("S8", s)]["a"]["paying_compass_carriers"] for s in seeds if D[("S8", s)]["a"])
    pay1 = sum(D[("S1", s)]["a"]["paying_compass_carriers"] for s in seeds if D[("S1", s)]["a"])
    print(f"  distinct window carriers that are a paying compass on their own links: S8 {pay8}, S1 {pay1}")
    dn = sum(D[("U8", s)]["a"]["de_novo"] for s in seeds if D[("U8", s)]["a"])
    b8 = sum(D[("U8", s)]["a"]["births"] for s in seeds if D[("U8", s)]["a"])
    print(f"  U8 de novo arrivals: {dn} in {b8} births (part 2: 0 in 11,676, RBT-102; drift expects ~2e-5 per birth)")

    print("\n## 3. Readout (b): function, on the arms whose positive controls both passed and that are viable\n")
    fd = {arm: [s for s in seeds if usable(arm, s) and D[(arm, s)]["b"]["fd"]] for arm in ("S1", "S8", "U8")}
    n_ok = {arm: sum(1 for s in seeds if usable(arm, s)) for arm in ("S1", "S8", "U8")}
    for arm in ("S1", "S8", "U8"):
        print(f"  {arm}: food-dependent champions on {len(fd[arm])} of {n_ok[arm]} usable seeds {fd[arm]}")
    p2 = [s for s in seeds if D[("P2", s)]["b"] and D[("P2", s)]["b"]["fd"]]
    print(f"  part 2: food-dependent champions on {len(p2)} of {sum(1 for s in seeds if D[('P2', s)]['b'])}")
    xs = [(s, D[("S8", s)]["b"]["F"], D[("S1", s)]["b"]["F"]) for s in seeds if usable("S8", s) and usable("S1", s)]
    dm, dlo, dhi = t_int([x1 - x0 for _, x1, x0 in xs])
    print(f"  F, S8 - S1, paired over seeds usable in both: n={len(xs)}  {fmt(dm, dlo, dhi)}")

    print("\n## 4. The verdict (rules fixed in PREREGISTRATION.md section 6)\n")
    via8 = sum(1 for s in seeds if D[("S8", s)]["side"] and D[("S8", s)]["side"]["viable"])
    k8, k1 = len(fd["S8"]), len(fd["S1"])
    read = sum(1 for s in seeds for arm in ("S1", "S8") if D[(arm, s)]["side"] and D[(arm, s)]["side"]["last"] >= WINDOW[1])
    if read < 2 * len(seeds):
        v = f"NOT READ: {2 * len(seeds) - read} primary arm(s) not finished or not committed; no partial read (RBT-88)"
    elif via8 < 7 or n_ok["S8"] < 7:
        v = "VOID: fewer than 7 of 10 S8 arms viable with both positive controls passing; the side effect, not magnitude, is what was measured"
    elif k8 >= 5 and k1 <= 1 and dlo > 0:
        v = "SUPPORTED: with the structure present, supplying the magnitude produced food-dependent champions"
    elif k8 <= 1 and not dlo > 0:
        pay_usable = sum(D[("S8", s)]["a"]["paying_compass_carriers"] for s in seeds if usable("S8", s))
        v = ("FALSIFIED: the magnitude was supplied and the structure planted, and chemotaxis did not evolve; magnitude is not the (only) cause. "
             + ("(F-a) paying compass carriers were present in S8's window and unused: magnitude is not sufficient"
                if pay_usable > 0 else
                "(F-b) S8's carriers did not keep a paying magnitude: it could be supplied but not held (the bias gate, PREREGISTRATION section 1.4)"))
    else:
        v = "NOT DECIDED at ten seeds"
    print(f"  S8 viable {via8}, usable {n_ok['S8']}; food-dependent S8 {k8}, S1 {k1}; F(S8 - S1) lower bound {dlo:+.3f}")
    print(f"  VERDICT: {v}")


if __name__ == "__main__":
    main()
