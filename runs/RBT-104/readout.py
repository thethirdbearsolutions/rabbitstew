"""RBT-104: the pre-registered readout across arms (PREREGISTRATION.md sections 4 and 6).

Reads, per seed in SEEDS, from the checkout alone:
  runs/RBT-104/{S1,S8}-SEED/seasons.txt      RBT-71's summary (side effects)
  runs/RBT-104/{S1,S8}-SEED/platform.txt     the machine and MuJoCo (one platform throughout)
  runs/RBT-104/{S1,S8}-SEED/rbt102.txt       RBT-102's analyse.py, unchanged (readout a)
  runs/RBT-104/{S1,S8}-SEED/function.txt     function.py on the arm's bests 300..590 (readout b)
  runs/RBT-104/{S1,S8}-SEED/function-pc.txt  function.py --install 32 on the same bests (b's control)
  runs/RBT-104/S8-SEED/peek-{300,599}.txt    peek.py's window readings (F-b, against no selection)
  runs/RBT-104/S8-{801,4}/peek-150.txt       the wave-0 futility gate (reported; futility only)

and prints every rule's inputs beside its verdict.  A missing file is reported and its seed leaves
the rule it feeds; it is never read as a null.  Nothing here is tuned after an arm was read: the
thresholds are the pre-registration's and are printed.  (U8 was dropped at 18:40; the gate is §6.2.)

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
GATE_SEEDS = (801, 4)
WINDOW = tuple(int(x) for x in os.environ.get("RBT104_WINDOW", "300,599").split(","))  # override: smoke tests only
RUNG_64 = 24.7145        # own links: the installed routed motif at a = 64 (probe_rung.txt, links alone)
RUNG_64_HOST = 13.3549   # in host: the same install's whole-brain antisymmetric reading (probe_rung.txt, w = 32)
FA_MIN_CARRIERS, FA_MIN_SHARE, FA_MIN_SEEDS = 10, 0.10, 2   # F-a's carriage threshold (§6)
VIABLE_ALIVE = 30
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


def side(path):
    """(viable, window mean alive, window mean of mean lifetime score, births, deaths, last season)."""
    if not os.path.exists(path):
        return None
    rows = [l.split("\t") for l in open(path).read().splitlines()]
    k = rows[0]
    rows = [dict(zip(k, r)) for r in rows[1:] if r[k.index("population")] == "conventional"]
    win = [r for r in rows if WINDOW[0] <= int(r["season"]) <= WINDOW[1]]
    last = max(int(r["season"]) for r in rows)
    alive = np.mean([int(r["alive"]) for r in win]) if win else 0.0
    inc = np.mean([float(r["mean_lifetime_score"]) for r in win]) if win else float("nan")
    viable = last >= WINDOW[1] and all(int(r["alive"]) > 0 for r in rows) and alive >= VIABLE_ALIVE
    return dict(viable=viable, alive=float(alive), income=float(inc),
                births=sum(int(r["births"]) for r in rows), deaths=sum(int(r["deaths"]) for r in rows), last=last)


def rbt102(path):
    """RBT-102 analyse.py's summary, plus its window carriers re-signed by heading (RBT-102's rule:
    the published motif is the compass for a backward driver) and read against the a = 64 rungs:
    own links >= 24.7145 is 'paying on its own links'; that AND whole brain >= 13.3549 is 'paying in host'."""
    if not os.path.exists(path):
        return None
    txt = open(path).read()
    m = re.search(r"^SUMMARY (\{.*\})$", txt, re.M)
    if not m:
        return None
    s = json.loads(m.group(1))
    own = host = 0
    for row in re.finditer(r"^\| (\S+) \| \d+ \| \d+ \| ([-+]\d+\.\d+) \| ([-+]\d+\.\d+) \| ([-+]\d+\.\d+) \| [\d.]+ \| [-+]\d+\.\d+ \| (COMPASS|ANTI-COMPASS) \|", txt, re.M):
        wa, la, h = float(row.group(2)), float(row.group(3)), float(row.group(4))
        back = abs(h) > 90
        s_la, s_wa = (la, wa) if back else (-la, -wa)
        own += s_la >= RUNG_64
        host += s_la >= RUNG_64 and s_wa >= RUNG_64_HOST
    s["paying_own"], s["paying_host"] = own, host
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


def peek(path):
    """peek.py's verdict line: (k, n, B, above the bound?)."""
    if not os.path.exists(path):
        return None
    m = re.search(r"^(?:PEEK|WINDOW) seed \S+(?: season \d+)?: k = (\d+), n = (\d+), B = (\d+) -> (.+)$", open(path).read(), re.M)
    if not m:
        return None
    return dict(k=int(m.group(1)), n=int(m.group(2)), B=int(m.group(3)), above=int(m.group(1)) > int(m.group(3)),
                text=m.group(4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default=None)
    a = ap.parse_args()
    seeds = SEEDS if not a.seeds else tuple(int(x) for x in a.seeds.split(","))
    R = lambda *p: os.path.join(ROOT, "runs", "RBT-104", *p)
    D = {}
    for s in seeds:
        for arm in ("S1", "S8"):
            d = R(f"{arm}-{s}")
            pf = os.path.join(d, "platform.txt")
            D[(arm, s)] = dict(side=side(os.path.join(d, "seasons.txt")), a=rbt102(os.path.join(d, "rbt102.txt")),
                               b=function(os.path.join(d, "function.txt")), pc=function(os.path.join(d, "function-pc.txt")),
                               plat=open(pf).read().strip() if os.path.exists(pf) else None)
        D[("S8", s)]["w300"] = peek(R(f"S8-{s}", "peek-300.txt"))
        D[("S8", s)]["w599"] = peek(R(f"S8-{s}", "peek-599.txt"))

    print("# RBT-104 readout: does uniform link-weight reach x8 let selection keep a planted compass working?\n")
    print(f"seeds {list(seeds)}; window seasons {WINDOW[0]}-{WINDOW[1]}; viable = never extinct, reached season "
          f"{WINDOW[1]}, window mean alive >= {VIABLE_ALIVE}; a = 64 rungs: own links {RUNG_64}, in host {RUNG_64_HOST}")
    plats = {}
    for (arm, s), v in D.items():
        if v["plat"]:
            plats.setdefault(v["plat"], []).append(f"{arm}-{s}")
    print("platforms (one platform throughout, x86_64 / MuJoCo 3.14.0): "
          + ("; ".join(f"{k}: {len(v)} arm(s)" for k, v in plats.items()) or "none recorded yet"))
    off = [x for k, v in plats.items() if not (k.startswith("platform x86_64") and "mujoco 3.14.0" in k) for x in v]
    if off:
        print(f"  NOT ON THE PLATFORM (unpaired with RBT-90 part 2, RBT-96; left out of every rule): {off}")
    for (arm, s), v in D.items():
        if f"{arm}-{s}" in off or (v["side"] is not None and v["plat"] is None):
            v["side"] = None  # an arm with no platform record, or off it, enters no rule
    missing = [f"{arm}-{s}:{k}" for (arm, s), v in D.items() for k, x in v.items() if x is None]
    if missing:
        print(f"MISSING (each leaves the rules it feeds, never read as a null): {', '.join(missing)}")

    print("\n## 0. The wave-0 futility gate (§6.2; futility only: it cannot raise a verdict)\n")
    for s in GATE_SEEDS:
        g = peek(R(f"S8-{s}", "peek-150.txt"))
        print(f"  seed {s}: " + ("not recorded" if not g else f"k = {g['k']}, n = {g['n']}, B = {g['B']} -> {g['text']}"))

    print("\n## Per seed\n")
    print("| seed | arm | viable | alive | income | pc(a) | X (carriage) | paying own / in host | held 300, 599 | pc(b) | F (real - decoy) | champions |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in seeds:
        for arm in ("S1", "S8"):
            v = D[(arm, s)]
            sd, ra, fb, pc = v["side"], v["a"], v["b"], v["pc"]
            dash = "—"
            held = dash if arm == "S1" else " / ".join(dash if not v[w] else ("above" if v[w]["above"] else "no") for w in ("w300", "w599"))
            cells = [
                dash if not sd else ("yes" if sd["viable"] else "NO"),
                dash if not sd else f"{sd['alive']:.1f}",
                dash if not sd else f"{sd['income']:+.3f}",
                dash if not ra else ("PASS" if ra["pc_pass"] else "FAIL"),
                dash if not ra else f"{1000 * ra['X']:.1f}/1000",
                dash if not ra else f"{ra['paying_own']} / {ra['paying_host']} of {ra['window_carriers']}",
                held,
                dash if not pc else ("PASS" if pc["fd"] else "FAIL"),
                dash if not fb else fmt(fb["F"], fb["lo"], fb["hi"]),
                dash if not fb else fb["verdict"],
            ]
            print(f"| {s} | {arm} | " + " | ".join(cells) + " |")

    print("\n## 1. Side effects of the reach, with the seed present: S8 - S1 (window means)\n")
    for key in ("income", "alive"):
        xs = [D[("S8", s)]["side"][key] - D[("S1", s)]["side"][key] for s in seeds
              if D[("S8", s)]["side"] and D[("S1", s)]["side"]]
        print(f"  {key:6s} n={len(xs)}  {fmt(*t_int(xs))}")
    for arm in ("S1", "S8"):
        print(f"  {arm} viable on {sum(1 for s in seeds if D[(arm, s)]['side'] and D[(arm, s)]['side']['viable'])} of {len(seeds)}")

    ok_pc = lambda v: v["a"] is not None and v["a"]["pc_pass"] and v["pc"] is not None and v["pc"]["fd"]
    usable = lambda arm, s: (D[(arm, s)]["side"] is not None and D[(arm, s)]["side"]["viable"] and ok_pc(D[(arm, s)])
                             and D[(arm, s)]["b"] is not None)
    print("\n## 2. Readout (a): structure, and whether S8 held a paying compass above no selection\n")
    xs = [D[("S8", s)]["a"]["X"] - D[("S1", s)]["a"]["X"] for s in seeds if D[("S8", s)]["a"] and D[("S1", s)]["a"]]
    m, lo, hi = t_int(xs)
    print(f"  carriage X, S8 - S1, paired over seeds: n={len(xs)}  {fmt(1000 * m, 1000 * lo, 1000 * hi)} per 1000")
    held = [s for s in seeds if usable("S8", s) and D[("S8", s)]["w300"] and D[("S8", s)]["w599"]
            and D[("S8", s)]["w300"]["above"] and D[("S8", s)]["w599"]["above"]]
    print(f"  S8 held its paying compass above the no-selection bound at seasons 300 and 599 on {len(held)} usable seed(s): {held}")
    inhost = [s for s in seeds if usable("S8", s) and D[("S8", s)]["a"]
              and D[("S8", s)]["a"]["paying_host"] >= FA_MIN_CARRIERS
              and D[("S8", s)]["a"]["paying_host"] >= FA_MIN_SHARE * max(1, D[("S8", s)]["a"]["window_carriers"])]
    print(f"  S8 seeds with >= {FA_MIN_CARRIERS} window carriers paying IN HOST, and >= {100 * FA_MIN_SHARE:.0f}% of its window "
          f"carriers: {len(inhost)} {inhost}")

    print("\n## 3. Readout (b): function, on arms that are viable with both positive controls passing\n")
    fd = {arm: [s for s in seeds if usable(arm, s) and D[(arm, s)]["b"]["fd"]] for arm in ("S1", "S8")}
    n_ok = {arm: sum(1 for s in seeds if usable(arm, s)) for arm in ("S1", "S8")}
    for arm in ("S1", "S8"):
        print(f"  {arm}: food-dependent champions on {len(fd[arm])} of {n_ok[arm]} usable seeds {fd[arm]}")
    xs = [D[("S8", s)]["b"]["F"] - D[("S1", s)]["b"]["F"] for s in seeds if usable("S8", s) and usable("S1", s)]
    dm, dlo, dhi = t_int(xs)
    print(f"  F, S8 - S1, paired over seeds usable in both: n={len(xs)}  {fmt(dm, dlo, dhi)}")

    print("\n## 4. The verdict (rules fixed in PREREGISTRATION.md section 6)\n")
    via8 = sum(1 for s in seeds if D[("S8", s)]["side"] and D[("S8", s)]["side"]["viable"])
    k8, k1 = len(fd["S8"]), len(fd["S1"])
    read = sum(1 for s in seeds for arm in ("S1", "S8") if D[(arm, s)]["side"] and D[(arm, s)]["side"]["last"] >= WINDOW[1])
    if read < 2 * len(seeds):
        v = f"NOT READ: {2 * len(seeds) - read} primary arm(s) not finished, not committed or off the platform; no partial read (RBT-88)"
    elif n_ok["S8"] < 7:
        v = ("VOID: fewer than 7 of 10 S8 arms usable (viable, with both positive controls passing); "
             "the side effect, not link-weight reach, is what was measured")
    elif k8 >= 5 and k1 <= 1 and dlo > 0:
        v = ("SUPPORTED: with the structure planted, uniform link-weight reach x8 let selection keep a food-dependent "
             "compass, in this uniform world")
    elif k8 <= 1 and not dlo > 0:
        base = ("FALSIFIED (in this uniform world, at uniform link-weight reach x8, biases unscaled): selection kept "
                "a food-dependent compass in no more than one population. ")
        if len(held) <= 1:
            v = base + "(F-b) S8 did not hold a paying compass above the operator-alone bound: the operator erased it faster than selection held it"
        elif len(inhost) >= FA_MIN_SEEDS:
            v = base + "(F-a) S8 held a compass paying in host, at carriage, and its champions still did not use it: link-weight reach is not sufficient"
        else:
            v = base + "(F-m) S8 held its compass above no selection on its own links, but not paying in host: the host masked it"
    else:
        v = "NOT DECIDED at ten seeds"
    print(f"  S8 viable {via8}, usable {n_ok['S8']}; food-dependent S8 {k8}, S1 {k1}; F(S8 - S1) lower bound {dlo:+.3f}; "
          f"held {len(held)}; in-host carriage {len(inhost)}")
    print(f"  VERDICT: {v}")


if __name__ == "__main__":
    main()
