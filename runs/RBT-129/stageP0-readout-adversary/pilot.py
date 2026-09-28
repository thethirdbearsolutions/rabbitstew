"""Adversary re-derivation of the pilot constants (a), (b) and the DUP-VERIFY duplicate structure (own code).
    python3 pilot.py DATAP   (DATAP/<point>/<seed>/{S,M,N} restored from ckpt/rbt-129-stageP-* branches)"""
import json, os, sys, statistics as st
from collections import Counter, defaultdict
DP = sys.argv[1]
H, C, NB = "holistic", "conventional", "null_b"
PTS = ("c1-p030-U-L", "c0-p030-U-L", "c1-p030-PW-G", "c2-p030-PW-G")
SEEDS = (129001, 129002, 129003, 129004)

def lineage(d):
    seen, rows, dup = set(), [], 0
    for line in open(f"{d}/lineage.jsonl"):
        if line in seen: dup += 1; continue
        seen.add(line); rows.append(json.loads(line))
    return rows, dup

print("(a) per-seed income difference, S arm, seasons 240-299 (lineage deduplicated by exact line)")
xs = {}
for pt in PTS:
    xs[pt] = []
    for s in SEEDS:
        d = f"{DP}/{pt}/{s}/S"
        if not os.path.exists(f"{d}/lineage.jsonl") or not os.path.exists(f"{d}/state.json"):
            print(f"  {pt}/{s}: no S (extinct pre-merge)"); continue
        p = json.load(open(f"{d}/config.json"))["sim"]["food"]["work_cost"]
        rows, dup = lineage(d)
        acc = defaultdict(lambda: [0.0, 0])
        for r in rows:
            if r.get("death") in ("cull", "merge-null"): continue
            if 240 <= r["generation"] <= 299:
                a = acc[r["population"]]; a[0] += r.get("food", 0) - p * r.get("work", 0) / 1000; a[1] += 1
        fl = {k: (acc[k][0] / acc[k][1] if acc[k][1] else None) for k in (H, C)}
        # also the design's validity: both alive in S through 239 (history)
        hist = json.load(open(f"{d}/history.json"))["history"]
        alive239 = {k: any(e["season"] == 239 and e["population"] == k and e["alive"] > 0 for e in hist) for k in (H, C)}
        ok = fl[H] is not None and fl[C] is not None
        x = fl[H] - fl[C] if ok else None
        if ok: xs[pt].append(x)
        print(f"  {pt}/{s}: H {fl[H]} D {fl[C]} x {x} alive@239 {alive239} dup_lines {dup}")
    v = xs[pt]
    print(f"  {pt}: n {len(v)} SD {st.stdev(v) if len(v) > 1 else None}")
pool = [(len(v) - 1, st.variance(v)) for v in xs.values() if len(v) >= 2]
print("  pooled over n>=2 points:", (sum(a * b for a, b in pool) / sum(a for a, _ in pool)) ** 0.5, "df", sum(a for a, _ in pool))

print("\n(b) null y' per N arm")
Y = []
for pt in PTS:
    for s in SEEDS:
        d = f"{DP}/{pt}/{s}/N"
        if not os.path.exists(f"{d}/history.json"): continue
        cfg = json.load(open(f"{d}/config.json")); K = cfg["ecology"]["merge_null"]; O = C if K == H else H
        hist = json.load(open(f"{d}/history.json"))["history"]
        by = {(e["season"], e["population"]): e for e in hist}
        nK = by.get((59, K), {}).get("alive", 0); nO = by.get((59, O), {}).get("alive", 0)
        base = nK / (nK + nO) if nK + nO else None
        aK = [by.get((t, K), {}).get("alive", 0) for t in range(240, 300)]
        aB = [by.get((t, NB), {}).get("alive", 0) for t in range(240, 300)]
        y120 = st.mean(a / 120 for a in aK) - base if base is not None else None
        shr = [a / (a + b) for a, b in zip(aK, aB) if a + b]
        yshare = (st.mean(shr) - base) if shr and base is not None else None
        valid = nK > 0 and nO > 0
        Y.append(dict(pt=pt, s=s, K=K, nK=nK, nO=nO, y120=y120, yshare=yshare, valid=valid, tot=st.mean(a + b for a, b in zip(aK, aB))))
        print(f"  {pt}/{s} K={K[:4]} nK {nK} nO {nO} valid {valid} y'(/120) {y120:+.3f} y'(share of living) {yshare if yshare is None else round(yshare,3)} mean pop 240-299 {Y[-1]['tot']:.1f}")
v = [y["y120"] for y in Y if y["valid"]]; a = [y["y120"] for y in Y]
print(f"  SD y' valid only (registered reading, 6.1 item 2): {st.stdev(v):.4f} n {len(v)} df {len(v)-1}")
print(f"  SD y' all N runs (plan text 'all available N runs'): {st.stdev(a):.4f} n {len(a)} df {len(a)-1}")
b = [y["y120"] for y in Y if y["nK"] > 0 and y["pt"].endswith("U-L")]
print(f"  SD y' U-L runs with K alive at merge (drop nK=0 only): {st.stdev(b):.4f} n {len(b)}")
for nm, vals in (("valid", v), ("all", a)):
    r = st.stdev(vals) / 0.1497
    print(f"  r = {r:.3f} ({nm})")

print("\nM arms' y' (K = holistic), descriptive")
for pt in PTS:
    for s in SEEDS:
        d = f"{DP}/{pt}/{s}/M"
        if not os.path.exists(f"{d}/history.json"): continue
        hist = json.load(open(f"{d}/history.json"))["history"]; by = {(e["season"], e["population"]): e for e in hist}
        nH = by.get((59, H), {}).get("alive", 0); nD = by.get((59, C), {}).get("alive", 0)
        if nH and nD:
            y = st.mean(by.get((t, H), {}).get("alive", 0) / 120 for t in range(240, 300)) - nH / (nH + nD)
            print(f"  {pt}/{s} M y' {y:+.3f}")

print("\nDUP-VERIFY units: duplicate structure of the saved logs")
for u in ("c1-p030-PW-G/129002/M", "c1-p030-U-L/129002/S"):
    d = f"{DP}/{u}"
    for fn in ("lineage.jsonl", "cohorts.jsonl"):
        lines = open(f"{d}/{fn}").read().splitlines()
        c = Counter(lines); dups = sum(n - 1 for n in c.values() if n > 1)
        gens = Counter()
        seen = set()
        for l in lines:
            if l in seen:
                j = json.loads(l); gens[j.get("generation", j.get("season"))] += 1
            seen.add(l)
        print(f"  {u} {fn}: {len(lines)} lines, {len(c)} unique, {dups} exact duplicates, in seasons {min(gens) if gens else '-'}-{max(gens) if gens else '-'} ({len(gens)} seasons)")
    rows, _ = lineage(d)
    hist = json.load(open(f"{d}/history.json"))["history"]
    # after dedup: rows per (season, population) vs history alive
    rc = Counter((r["generation"], r["population"]) for r in rows)
    mism = [(k, rc[k], e["alive"]) for e in hist for k in [(e["season"], e["population"])] if rc.get(k, 0) not in (e["alive"], e["alive"] + e["deaths"], e["alive"] - e["births"] + e["deaths"])]
    print(f"  {u}: dedup rows per season vs history (alive / alive+deaths): {len(mism)} mismatching (season,pop); first {mism[:3]}")
    print(f"  {u} command.txt invocations: {open(f'{d}/command.txt').read().count('rabbitstew.cli')}")
