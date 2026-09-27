"""RBT-112: the pre-registered readout (PREREGISTRATION.md §6).  Nothing here is tuned after an arm was read; every
threshold is fixed here, before any arm, and printed beside its verdict.

The pair Z: RBT-106's HU-SEED (the paired control, the default operator) against RBT-112's HZ-SEED (the same command
plus --global-bias-sigma 0).  Per arm directory, from the checkout alone, RBT-106's files and parsers (its
readout.py, imported: side, platform_ok, rbt102, held, function, commit), plus:
  HZ-SEED/held-300.txt, held-599.txt   runs/RBT-112/held.py: HELD against the S = 0 operator's own no-selection table
  HZ-SEED/resting.txt, HU-SEED/resting.txt (runs/RBT-112/HU-SEED/)   F12: planted-unit resting drive per champion (information)
  HZ-SEED/freeze.txt                   freeze.py: the birth-level frozen-bias test; a FAULT makes the HZ arm unusable
  HZ-SEED/commit.txt                   the launch commit; it must name a certification (certify.sh) reading SAME RUN
                                       against HU-801 and HU-4, so HZ is one flag from HU on the code that ran
HU's code must be c872e80's, as RBT-106 requires.  A missing file is reported and its seed leaves the rule it feeds;
it is never read as a null (R1, 03:44: an arm missing held-300.txt or held-599.txt is UNUSABLE, never NOT
HELD).  NOT READ is printed until every arm has finished season 599.

Verdict (HELD is k_planted > B at both 300 and 599, each arm against its own operator's no-selection table), in order
(amended per the 03:32 ruling on the design adversary: F7, F14, F3):
  VOID              fewer than 7 usable paired seeds
  SUPPORTED         #HELD(HZ) - #HELD(HU) >= 3             the operator was the stall: with the global biases frozen,
                                                            selection holds the paying compass it lost
  FALSIFIED         #HELD(HZ) <= 1 and #LOST(HZ) <= 2      planted roots alive at 300 and 599 on all but at most 2 usable
                                                            seeds: the operator is not the stall
  FALSIFIED-ROOTS   #HELD(HZ) <= 1 and #LOST(HZ) >= 3      the planted roots died out: the operator question is NOT
                                                            answered on those seeds
  NOT DECIDED       otherwise
  An HZ seed is LOST if held.py reads n (planted-rooted living) = 0 at 300 or at 599.  n per seed is printed.
  F3: if the side effect SE-Z fails (window income HZ - HU, t interval excluding 0), the verdict is worded "with the
  designed body's global biases frozen (host and planted)", and paired births and window depth are printed beside it.
Function, reported beside it (RBT-106 §10.4's COMPASS count, patchy-scored):
  FOLLOWS     HZ COMPASS lines >= 3 and the paired F(HZ) - F(HU) t interval above 0
  DOES NOT    HZ COMPASS lines <= 1 and that interval not above 0;  UNDECIDED otherwise

Usage: readout.py [--seeds 801,4,...]
"""
import argparse
import importlib.util
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_spec = importlib.util.spec_from_file_location("rbt106_readout", os.path.join(ROOT, "runs", "RBT-106", "readout.py"))
r106 = importlib.util.module_from_spec(_spec)
sys.modules["rbt106_readout"] = r106
_spec.loader.exec_module(r106)

SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
WINDOW = tuple(int(x) for x in os.environ.get("RBT112_WINDOW", "300,599").split(","))  # override: smoke tests only
MIN_USABLE = 7
SUPPORT_GAP = 3           # SUPPORTED: #HELD(HZ) - #HELD(HU) >= 3 (F7: RBT-106's own count form; was "#HELD(HZ) >= 5 and ...")
FEW = 1                   # FALSIFIED(-ROOTS): #HELD(HZ) <= 1;  FUNCTION DOES NOT FOLLOW: <= 1 COMPASS line
LOST_MAX = 2              # F14: FALSIFIED needs #LOST(HZ) <= 2 (roots alive on >= n_usable - 2 seeds); >= 3 is FALSIFIED-ROOTS
FD_MANY = 3               # FUNCTION FOLLOWS: >= 3 COMPASS lines and the paired F interval > 0
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


def t_int(v):
    """Mean and two-sided 95% t interval; no scipy (the suite runs without it)."""
    v = np.asarray(v, float)
    if len(v) < 2:
        return (float(v.mean()) if len(v) else float("nan")), float("nan"), float("nan")
    h = T975[len(v) - 1] * float(v.std(ddof=1)) / np.sqrt(len(v))
    return float(v.mean()), float(v.mean()) - h, float(v.mean()) + h


def resting(d):
    p = os.path.join(d, "resting.txt")
    if not os.path.exists(p):
        return None
    m = re.search(r"^RESTING \S+: paying planted-unit carriers (\d+) of (\d+) champions; with resting drive > 1 "
                  r"\(the Effector saturates, F12's masking route\) (\d+)(?:; (?:frozen-bias faults|paying carriers with b != 0 "
                  r"\(information, not a fault\)) (\d+))?", open(p).read(), re.M)
    if not m:
        return None
    return dict(carriers=int(m.group(1)), of=int(m.group(2)), drifted=int(m.group(3)),
                bnz=int(m.group(4)) if m.group(4) is not None else None)


def freeze(d):
    """freeze.py's birth-level test (F12): True on PASS, False on FAULT, None if missing."""
    p = os.path.join(d, "freeze.txt")
    if not os.path.exists(p):
        return None
    m = re.search(r"^FREEZE \S+: births (\d+), faults (\d+) -> (PASS|FAULT)", open(p).read(), re.M)
    return None if not m else m.group(3) == "PASS"


def lost(r):
    """F14: no planted-rooted genome alive at 300 or at 599 (held.py's n = 0)."""
    return bool(r["held300"] and r["held599"] and (r["held300"]["n"] == 0 or r["held599"]["n"] == 0))


def certified(code):
    """HZ's launch commit names a certification file that reads SAME RUN against HU-801 and HU-4."""
    if not code:
        return False
    p = os.path.join(HERE, f"cross-ticket-{code['commit'][:12]}.txt")
    if not os.path.exists(p):
        return False
    t = open(p).read()
    return bool(re.search(r"^CROSS-TICKET HU-801: SAME RUN \(prefix\)", t, re.M) and re.search(r"^CROSS-TICKET HU-4: SAME RUN \(prefix\)", t, re.M))


def read_arm(arm, seed):
    d = os.path.join(ROOT, "runs", "RBT-106", f"HU-{seed}") if arm == "HU" else os.path.join(HERE, f"HZ-{seed}")
    s = r106.side(d) if os.path.isdir(d) else None
    ok, plat = r106.platform_ok(d)
    a = r106.rbt102(d)
    r = dict(arm=arm, seed=seed, side=s, platform=plat, platform_ok=ok, rbt102=a,
             held300=r106.held(d, WINDOW[0]), held599=r106.held(d, WINDOW[1]),
             fu=r106.function(d, "uniform"), fp=r106.function(d, "patchy"), pc=r106.function(d, "pc"), code=r106.commit(d),
             rest=resting(d if arm == "HZ" else os.path.join(HERE, f"HU-{seed}")))
    r["pc_ok"] = bool(a and a.get("pc_pass")) and bool(r["pc"] and r["pc"]["fd"])
    if arm == "HU":
        r["code_ok"] = bool(r["code"] and r["code"]["tree"] == r106.REF_TREE)
        r["frozen_ok"] = True
    else:
        r["code_ok"] = certified(r["code"])
        r["frozen_ok"] = freeze(d) is True
    r["held_ok"] = bool(r["held300"] and r["held599"])   # R1 (03:44): both readings present, else UNUSABLE, never NOT HELD
    r["usable"] = bool(s and s["viable"] and ok and r["pc_ok"] and r["code_ok"] and r["frozen_ok"] and r["held_ok"])
    r["HELD"] = bool(r["held300"] and r["held599"] and r["held300"]["held"] and r["held599"]["held"])
    return r


def verdict(nU, nZ, n_usable, n_lost=0):
    if n_usable < MIN_USABLE:
        return f"VOID (fewer than {MIN_USABLE} usable paired seeds)"
    if nZ - nU >= SUPPORT_GAP:
        return "SUPPORTED: with the global biases frozen, selection held the paying compass that the default operator's arm lost"
    if nZ <= FEW and n_lost <= LOST_MAX:
        return ("FALSIFIED: with the planted roots alive, freezing the global biases (erasure 0.282 -> 0.089 per generation) "
                "did not let selection hold the compass; the operator is not the stall")
    if nZ <= FEW:
        return (f"FALSIFIED-ROOTS: the planted roots died out on {n_lost} usable HZ seeds; the operator question is not "
                "answered on those seeds")
    return "NOT DECIDED at this n"


def function_verdict(cZ, dF_lo):
    if cZ >= FD_MANY and dF_lo > 0:
        return "FUNCTION FOLLOWS"
    if cZ <= FEW and not dF_lo > 0:
        return "FUNCTION DOES NOT FOLLOW"
    return "FUNCTION UNDECIDED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    seeds = [int(x) for x in ap.parse_args().seeds.split(",")]
    print("# RBT-112 readout: is the operator the stall?  HU (RBT-106, default operator) against HZ (--global-bias-sigma 0)")
    print(f"window seasons {WINDOW[0]}-{WINDOW[1]}; seeds {seeds}")
    rows = [(read_arm("HU", s), read_arm("HZ", s)) for s in seeds]
    unfinished = [f"{r['arm']}-{r['seed']}" for pr in rows for r in pr if not (r["side"] and r["side"]["finished"])]
    if unfinished:
        print(f"NOT READ: {len(unfinished)} arm(s) have not finished season {WINDOW[1]}: {', '.join(unfinished)}")
        return None
    print("\n| seed | arm | code ok | platform | viable | pc (a)/(b) | alive | income | births | "
          f"held {WINDOW[0]} k_pl(k_bare)/n/B | held {WINDOW[1]} k_pl(k_bare)/n/B, depth, roots | HELD | F uniform | F patchy, attribution | "
          "lesion gain (patchy) | F12: paying carriers / resting > 1 / b != 0 (info) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for pr in rows:
        for r in pr:
            s, a = r["side"], r["rbt102"] or {}
            h = lambda x: f"{x['k']}({x['kb']})/{x['n']}/{x['B']}" if x else "missing"
            h2 = lambda x: f"{h(x)}, {x['depth']:.1f}, {x['roots']}" if x else "missing"
            f = lambda x: (f"{x['F']:+.3f} {'FD' if x['fd'] else '-'}" if x else "missing")
            fa = lambda x: (f"{f(x)}, {x['att']}" if x else "missing")
            rs = r["rest"]
            print(f"| {r['seed']} | {r['arm']} | {r['code_ok']} | {r['platform']} | {s['viable']} | {a.get('pc_pass')}/{bool(r['pc'] and r['pc']['fd'])} | "
                  f"{s['conventional']['alive']:.1f} | {s['conventional']['income']:.3f} | {s['conventional']['births']} | "
                  f"{h(r['held300'])} | {h2(r['held599'])} | {r['HELD']} | {f(r['fu'])} | {fa(r['fp'])} | "
                  f"{(r['fp']['gain'] if r['fp'] else float('nan')):+.3f} | "
                  f"{(str(rs['carriers']) + '/' + str(rs['of']) + ' / ' + str(rs['drifted']) + ' / ' + str(rs['bnz'])) if rs else 'missing'} |")
    use = [(u, z) for u, z in rows if u["usable"] and z["usable"]]
    nohold = [f"{r['arm']}-{r['seed']}" for pr in rows for r in pr if not r["held_ok"]]
    if nohold:
        print(f"\nUNUSABLE (held-{WINDOW[0]}.txt or held-{WINDOW[1]}.txt missing or unparseable; never read as NOT HELD): {', '.join(nohold)}")
    print(f"\nusable paired seeds: {len(use)} of {len(rows)} (viable, x86_64, both positive controls, code certified, no freeze.py FAULT, "
          f"both held readings present)")
    nU, nZ = sum(u["HELD"] for u, _ in use), sum(z["HELD"] for _, z in use)
    ex = [z["held599"]["excess"] - u["held599"]["excess"] for u, z in use if u["held599"] and z["held599"]]
    carr = [(z["held599"]["k"] / max(1, z["held599"]["n"])) - (u["held599"]["k"] / max(1, u["held599"]["n"])) for u, z in use
            if u["held599"] and z["held599"]]
    cU = sum(bool(u["fp"] and u["fp"]["cfd"]) for u, _ in use)
    cZ = sum(bool(z["fp"] and z["fp"]["cfd"]) for _, z in use)
    aU = sum(bool(u["fp"] and u["fp"]["fd"]) for u, _ in use)
    aZ = sum(bool(z["fp"] and z["fp"]["fd"]) for _, z in use)
    dF = [z["fp"]["F"] - u["fp"]["F"] for u, z in use if u["fp"] and z["fp"]]
    dFu = [z["fu"]["F"] - u["fu"]["F"] for u, z in use if u["fu"] and z["fu"]]
    inc = [z["side"]["conventional"]["income"] - u["side"]["conventional"]["income"] for u, z in use]
    alive = [z["side"]["conventional"]["alive"] - u["side"]["conventional"]["alive"] for u, z in use]
    fmt = lambda x: f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"
    print(f"HELD (each against its own operator's table): HU {nU}, HZ {nZ}")
    print(f"paired log-excess at {WINDOW[1]}, HZ - HU (reported): {fmt(t_int(ex))}")
    print(f"paired carrier share k_planted/n at {WINDOW[1]}, HZ - HU (reported; the operator alone raises it, so it is not the test): {fmt(t_int(carr))}")
    print(f"k_bare at {WINDOW[1]} (not scored): HU {sum(u['held599']['kb'] for u, _ in use if u['held599'])}, "
          f"HZ {sum(z['held599']['kb'] for _, z in use if z['held599'])}")
    print(f"COMPASS lines (primary FD and attribution FD), patchy-scored: HU {cU}, HZ {cZ}")
    print(f"food-dependent lines (primary FD alone: any smell use), patchy-scored: HU {aU}, HZ {aZ}")
    print(f"paired F(HZ) - F(HU): patchy-scored {fmt(t_int(dF))}, uniform-scored {fmt(t_int(dFu))}")
    births = [z["side"]["conventional"]["births"] - u["side"]["conventional"]["births"] for u, z in use]
    depth = [(z["rbt102"] or {}).get("window_depth", float("nan")) - (u["rbt102"] or {}).get("window_depth", float("nan")) for u, z in use]
    print(f"side effects, HZ - HU over the window: designed income {fmt(t_int(inc))}; alive {fmt(t_int(alive))}; "
          f"births {fmt(t_int(births))}; window depth {fmt(t_int(depth))}")
    zs = [z for _, z in use]
    n_lost = sum(lost(z) for z in zs)
    print("HZ per seed (F14): n planted-rooted at 300 / 599 -> class: " + "; ".join(
        f"{z['seed']}: {z['held300']['n'] if z['held300'] else '?'} / {z['held599']['n'] if z['held599'] else '?'} -> "
        f"{'LOST' if lost(z) else 'HELD' if z['HELD'] else 'NOT HELD'}" for z in zs))
    print(f"#LOST(HZ) = {n_lost} of {len(zs)} usable (FALSIFIED needs <= {LOST_MAX}; >= {LOST_MAX + 1} is FALSIFIED-ROOTS)")
    print("F13: a Z pair needs HU's install control to pass (a drifted planted unit, F12's route, can fail it); HELD itself "
          "uses no function reading")
    drifted = [f"{r['arm']}-{r['seed']}" for pr in rows for r in pr if r["rest"] and r["rest"]["drifted"] and not r["pc_ok"]]
    if drifted:
        print(f"F12: control failed on a champion line carrying a drifted planted unit (resting drive > 1): {', '.join(drifted)} "
              "-- read as F12's route, not as 'the host masks a compass'")
    v = verdict(nU, nZ, len(use), n_lost)
    inc_i = t_int(inc)
    if len(use) >= MIN_USABLE and ((inc_i[1] > 0) or (inc_i[2] < 0)):
        v += ("\n  SE-Z FAILED (window income HZ - HU excludes 0): the verdict is worded 'with the designed body's global biases "
              "frozen (host and planted)', not 'the planted unit's bias walk'; paired births and depth are printed above")
    v += (f"   [rules: SUPPORTED #HELD(HZ) - #HELD(HU) >= {SUPPORT_GAP}; FALSIFIED #HELD(HZ) <= {FEW} and #LOST(HZ) <= {LOST_MAX}; "
          f"FALSIFIED-ROOTS #HELD(HZ) <= {FEW} and #LOST(HZ) >= {LOST_MAX + 1}; VOID < {MIN_USABLE} usable]")
    v += f"\n  function (reported, not in the verdict): {function_verdict(cZ, t_int(dF)[1])}   [FOLLOWS: HZ COMPASS >= {FD_MANY} and paired F interval > 0]"
    print(f"\nVERDICT Z: {v}")
    return v


if __name__ == "__main__":
    main()
