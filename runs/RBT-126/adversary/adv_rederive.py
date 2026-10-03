"""RBT-126 adversary, probe 3: re-derive REGIME.md corpus rows from the restored lineages, without scripts/regime.py.

Written from ecology.py alone (Ecology.step :505-548, _log_lineage :751-761, _breed :604):
  * a lineage row is written after the season's births; a row with evals 0 is a child born that season;
  * the breeder that paid is the child's parents[0];
  * pre-birth energy of a member = its row's energy + birth_cost x (children naming it parents[0] that season);
  * eligible = pre-birth energy >= birth_threshold;
  * window-local saturation = (mean last_score over eligible member-seasons in the window - living cost) / living cost;
  * eligible breeders = mean eligible count per season; deaths by age = share of deaths in the window whose last row
    had age >= max_age - 1 (cull rows excluded from 'age').
Only these three columns are re-derived (the band is read from the first).  Per seed, then median [min, max].

python3 runs/RBT-126/adversary/adv_rederive.py CK_DIR > runs/RBT-126/adversary/adv_rederive.txt
"""
import collections, glob, json, os, re, sys
import numpy as np

CK = sys.argv[1]
ONSET = {}
T = 360
CELLS = [  # (ticket, arm glob, fauna, label, lo, hi)
    ("106", "HP-*", "conventional", "to 300 [0,300)", 0, 299),
    ("106", "HP-*", "conventional", "window income [300,600)", 300, 599),
    ("106", "HU-*", "conventional", "to 300 [0,300)", 0, 299),
    ("106", "HU-*", "conventional", "window income [300,600)", 300, 599),
    ("106", "P1-*", "conventional", "window income [300,600)", 300, 599),
    ("107", "fresh-base-*", "conventional", "to H-REP [T,T+110)", T, T + 109),
    ("107", "fresh-base-*", "conventional", "to H1 [T+110,T+800)", T + 110, T + 799),
    ("107", "fresh-shift-*", "conventional", "to H1 [T+110,T+800)", T + 110, T + 799),
    ("112", "HZ-*", "conventional", "window income [300,600)", 300, 599),
    ("112", "HZ-*", "conventional", "to 300 [0,300)", 0, 299),
]


def eco(run):
    e = json.load(open(os.path.join(run, "config.json")))["ecology"]
    return float(e["living_cost"]), float(e["birth_threshold"]), float(e["birth_cost"]), int(e["max_age"])


def read(run, fauna, lo, hi):
    cost, thr, bc, max_age = eco(run)
    rows = collections.defaultdict(list)      # season -> [(name, energy, evals, last_score)]
    paid = collections.Counter()               # (season, parent) -> children
    last = {}                                  # name -> (season, age, culled)
    top = -1
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            if r["population"] != fauna:
                continue
            g = r["generation"]
            top = max(top, g)
            if r.get("death") == "cull":
                last[r["name"]] = (g, r["age"], True)
                continue
            if r["evals"] == 0 and r["parents"]:
                paid[(g, r["parents"][0])] += 1
            rows[g].append((r["name"], r["energy"], r["evals"], r["last_score"]))
            last[r["name"]] = (g, r["age"], False)
    gains, counts = [], []
    for g in range(lo, min(hi, top) + 1):
        n = 0
        for name, e, ev, ls in rows.get(g, []):
            if ev == 0:
                continue
            if e + bc * paid.get((g, name), 0) >= thr:
                n += 1
                gains.append(ls)
        counts.append(n)
    dead = [(g, a, c) for g, a, c in last.values() if g < top and lo <= g + 1 <= hi]
    age = sum(1 for g, a, c in dead if not c and a >= max_age - 1)
    return ((np.mean(gains) - cost) / cost if gains else None, float(np.mean(counts)), age / len(dead) if dead else None)


def med(v):
    v = [x for x in v if x is not None]
    return f"{np.median(v):.2f} [{min(v):.2f}, {max(v):.2f}] (n {len(v)})" if v else "-"


print("# ticket | arm | fauna | window | saturation, window-local | eligible breeders | deaths by age")
for t, arm, fauna, label, lo, hi in CELLS:
    sats, els, ages = [], [], []
    for d in sorted(glob.glob(os.path.join(CK, f"rbt-{t}-{arm}"))):
        inner = [x for x in glob.glob(os.path.join(d, "*")) if os.path.isdir(x)]
        if not inner or not os.path.exists(os.path.join(inner[0], "lineage.jsonl")):
            continue
        s, e, a = read(inner[0], fauna, lo, hi)
        print(f"  RBT-{t} {os.path.basename(d)} {fauna} {label}: sat {s:.2f} elig {e:.2f} age {a if a is None else round(a, 3)}", flush=True)
        sats.append(s); els.append(e); ages.append(a)
    print(f"RBT-{t} | {arm} | {fauna} | {label} | {med(sats)} | {med(els)} | {med(ages)}", flush=True)
