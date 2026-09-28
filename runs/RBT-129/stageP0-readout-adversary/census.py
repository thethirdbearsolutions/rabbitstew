"""Adversary re-derivation of the Stage-0 census calls (own code; READOUT-PLAN §6 definitions).
    python3 census.py DATA0  (DATA0/<point>/<seed>/S restored from ckpt/rbt-129-stage0-* branches)"""
import json, os, sys, statistics as st
from collections import Counter, defaultdict
D0 = sys.argv[1]
H, C = "holistic", "conventional"
SEEDS = (129001, 129002, 129003)
pts = sorted(os.listdir(D0))
res = {}
fp = defaultdict(dict)   # seed -> point -> holistic founder fingerprint
for pt in pts:
    for s in SEEDS:
        d = f"{D0}/{pt}/{s}/S"
        cfg = json.load(open(f"{d}/config.json")); p = cfg["sim"]["food"]["work_cost"]
        hist = json.load(open(f"{d}/history.json"))["history"]
        by = {(e["season"], e["population"]): e for e in hist}
        r = {}
        for k in (H, C):
            e = by.get((59, k))
            ext = e is None or (e["alive"] - e["births"]) == 0
            last = max([e["season"] for e in hist if e["population"] == k and e["alive"] - e["births"] > 0], default=-1)
            r[k] = dict(ext=ext, last=last)
        acc = {H: [0.0, 0], C: [0.0, 0]}; allf = [0.0, 0]; fh = []
        for line in open(f"{d}/lineage.jsonl"):
            x = json.loads(line)
            if x.get("death") in ("cull", "merge-null"): continue
            g = x["generation"]
            if g == 0 and x["population"] == H and not x["parents"]: fh.append((x["name"], x["nodes"]))
            if 30 <= g <= 59:
                v = x.get("food", 0.0) - p * x.get("work", 0.0) / 1000.0
                a = acc[x["population"]]; a[0] += v; a[1] += 1; allf[0] += v; allf[1] += 1
        r["acc"] = acc; r["all"] = allf
        fp[s][pt] = tuple(sorted(fh))
        res[(pt, s)] = r

# FOUNDING-FAIL
ff = {k: [] for k in (H, C)}
for pt in pts:
    for k in (H, C):
        if sum(res[(pt, s)][k]["ext"] for s in SEEDS) >= 2: ff[k].append(pt)
print("FOUNDING-FAIL holistic:", len(ff[H]), "of", len(pts))
print("FOUNDING-FAIL designed:", len(ff[C]), "by layout", dict(Counter(pt.split('-')[2] for pt in ff[C])))
print("  designed FF points:", " ".join(ff[C]))
for s in SEEDS:
    ext = [pt for pt in pts if res[(pt, s)][H]["ext"]]
    lasts = [res[(pt, s)][H]["last"] for pt in ext]
    print(f"holistic extinct by 59 at seed {s}: {len(ext)} points; last live season range {min(lasts) if lasts else '-'}-{max(lasts) if lasts else '-'}, median {st.median(lasts) if lasts else '-'}")
    fps = set(fp[s].values())
    print(f"  holistic founder sets at seed {s}: {len(fps)} distinct over {len(fp[s])} points; founders {len(next(iter(fps)))}")
print("designed extinct per seed:", {s: sum(res[(pt, s)][C]['ext'] for pt in pts) for s in SEEDS})
print("holistic alive at 59 on 129001 at points:", len(pts) - sum(res[(pt, 129001)][H]['ext'] for pt in pts))
# g0
g0 = {}
for pt in pts:
    t = [sum(res[(pt, s)]["all"][i] for s in SEEDS) for i in (0, 1)]
    g0[pt] = (t[0] / t[1] + 0.35) if t[1] else None
na = [pt for pt in pts if g0[pt] is None]
print("g0 <= 0.8:", sum(1 for v in g0.values() if v is not None and v <= 0.8), "| <= 1.0:", sum(1 for v in g0.values() if v is not None and v <= 1.0), "| n/a:", len(na), na)
# C1
def diff(pt):
    h = [sum(res[(pt, s)]["acc"][H][i] for s in SEEDS) for i in (0, 1)]
    c = [sum(res[(pt, s)]["acc"][C][i] for s in SEEDS) for i in (0, 1)]
    return (h[0] / h[1] - c[0] / c[1]) if h[1] and c[1] else None
dd = {pt: diff(pt) for pt in pts}
CL = ["c0", "c05", "c1", "c15", "c2"]; PR = ["p010", "p018", "p030", "p053", "p080"]
bad = []
def changes(seq):
    v = [x for x in seq if x is not None and x != 0]
    return sum(1 for a, b in zip(v, v[1:]) if (a > 0) != (b > 0))
for L in ("U", "HP", "PW"):
    for sm in ("L", "G"):
        for c in CL:
            n = changes([dd[f"{c}-{p}-{L}-{sm}"] for p in PR])
            if n > 1: bad.append(("price", f"{c}-*-{L}-{sm}", n))
        for p in PR:
            n = changes([dd[f"{c}-{p}-{L}-{sm}"] for c in CL])
            if n > 1: bad.append(("clutter", f"*-{p}-{L}-{sm}", n))
print("C1 rows with >1 sign change:", len(bad), dict(Counter(b[0] for b in bad)))
for b in bad: print("  ", *b)
print("C1 rows with undefined points (skipped):", sum(1 for v in dd.values() if v is None), "points undefined")
json.dump({"g0": g0, "diff": dd, "ffH": ff[H], "ffD": ff[C]}, open(os.path.join(os.path.dirname(__file__), "census_out.json"), "w"), indent=0)
