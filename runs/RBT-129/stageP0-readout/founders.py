"""RBT-129 Stage P+0 readout, fixes for the #490 ruling (MUST 1, SHOULD 5): founder outcomes per draw, and seeds per
Stage-1 point.  Descriptive facts read from the restored runs; no registered number is computed here.

    python3 runs/RBT-129/stageP0-readout/founders.py DATA > founders.txt
"""
import glob, hashlib, json, os, sys

DATA = sys.argv[1]
C = os.path.join(DATA, "runs", "RBT-129", "stage0")
P = os.path.join(DATA, "runs", "RBT-129", "stageP")
H, D = "holistic", "conventional"


def alive(d):
    h = json.load(open(os.path.join(d, "history.json")))["history"]
    a = {}
    for e in h:
        a.setdefault(e["population"], {})[e["season"]] = e["alive"]
    return a


def status(d, k, at=59):
    a = alive(d).get(k, {})
    last = max([s for s, n in a.items() if n > 0], default=None)
    return a.get(at, 0), last


print("# founder outcome per draw at c0-p030-U-L (holistic alive at season 59; last season alive)")
for s in range(129001, 129009):
    d = os.path.join(C, "c0-p030-U-L", str(s), "S")
    src = "census S" if s <= 129003 else "anchor-fallback S 0-59"
    if s == 129004:
        d, src = os.path.join(P, "c0-p030-U-L", str(s), "S"), "pilot S"
    n59, last = status(d, H)
    print(f"  {s}: holistic alive at 59: {n59:3d}; last alive {last}  ({src})")

print()
print("# founder identity: distinct holistic founder sets per seed over the census points")
for s in (129001, 129002, 129003):
    sets = set()
    pts = sorted(os.listdir(C))
    for pt in pts:
        f = os.path.join(C, pt, str(s), "S", "lineage.jsonl")
        fs = sorted((r["name"], r["nodes"]) for r in map(json.loads, open(f))
                    if r["generation"] == 0 and r["population"] == H and not r["parents"])
        sets.add(hashlib.md5(str(fs).encode()).hexdigest())
    print(f"  {s}: {len(sets)} distinct founder set(s) over {len(pts)} points")

print()
print("# Stage-1 points (DESIGN 4.1): both faunas alive at 59 in the census, per seed 129001-129003")
pts = [f"c{c}-p{p}-{L}-G" for c in ("0", "1", "2") for p in ("010", "030", "080") for L in ("U", "HP", "PW")]
pts += [f"c1-p{p}-{L}-L" for p in ("010", "030", "080") for L in ("U", "HP", "PW")]
bad = []
for pt in pts:
    row = []
    for s in (129001, 129002, 129003):
        d = os.path.join(C, pt, str(s), "S")
        h59, _ = status(d, H)
        d59, _ = status(d, D)
        row.append(f"{s}: H {h59:2d} D {d59:2d}")
        if s == 129001 and not (h59 and d59):
            bad.append((pt, "holistic" if not h59 else "designed"))
    print(f"  {pt:14s} " + " | ".join(row))
print(f"# 129001 lacks a fauna at 59 at {len(bad)} of {len(pts)} Stage-1 points:")
for pt, k in bad:
    print(f"  {pt}: {k} extinct by 59")
