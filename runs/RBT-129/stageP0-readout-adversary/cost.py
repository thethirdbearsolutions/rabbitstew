"""Adversary: cost per arm-season from pilot run.logs (own parse). core-s = wall s x 2 (WORKERS=2), seasons 60-299."""
import os, re, sys, statistics as st
DP = sys.argv[1]
PAT = re.compile(r"^season\s+(\d+)\s.*\((\d+(?:\.\d+)?)s\)\s*$")
arms, excl = {}, []
for pt in sorted(os.listdir(DP)):
    for s in sorted(os.listdir(f"{DP}/{pt}")):
        for a in ("S", "M", "N"):
            d = f"{DP}/{pt}/{s}/{a}"
            if not os.path.exists(f"{d}/run.log"): continue
            nres = open(f"{d}/command.txt").read().count("--resume")
            t = {}
            for line in open(f"{d}/run.log"):
                m = PAT.match(line.strip())
                if m and 60 <= int(m.group(1)) <= 299: t[int(m.group(1))] = 2 * float(m.group(2))
            key = f"{pt}/{s}/{a}"
            if nres > 1: excl.append(f"{key} ({nres} --resume)"); continue
            if not t: excl.append(f"{key} (no season lines)"); continue
            arms[key] = st.mean(t.values())
print("included arms:", len(arms))
for k, v in arms.items(): print(f"  {k}: {v:.1f} core-s over seasons")
print("excluded:", len(excl), excl)
pp = {}
for k, v in arms.items(): pp.setdefault(k.split('/')[0], []).append(v)
for p, v in pp.items(): print(f"  point {p}: {len(v)} arms, mean {st.mean(v):.2f}")
print(f"median {st.median(arms.values()):.2f}; max per-point mean {max(st.mean(v) for v in pp.values()):.2f}")
allv = sorted(arms.values()); print("if the saved DUP units were kept (they have >1 resume, so no change): n/a")
