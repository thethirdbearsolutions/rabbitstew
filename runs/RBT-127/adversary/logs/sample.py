"""RBT-127 adversary: stratified sample of ERRATA.md rows (seed 127)."""
import random, re, sys, json
lines = open(sys.argv[1]).read().splitlines()
sec = sub = None; rows = []
for i, l in enumerate(lines, 1):
    if l.startswith("## "): sec = l[3:]; sub = None
    elif l.startswith("### "): sub = l[4:]
    elif l.startswith("| ") and not (i < len(lines) and lines[i].startswith("|---")) and sec and sec[0].isdigit():
        cells = [c.strip() for c in l.strip().strip("|").split(" | ")]
        rows.append(dict(errata_line=i, section=sec, sub=sub, cells=cells))
by = {}
for r in rows: by.setdefault(r["section"], []).append(r)
random.seed(127)
N = 32; tot = len(rows); picked = []
for s in sorted(by):  # proportional, at least 2 per stratum (all if fewer)
    k = min(len(by[s]), max(2, round(N * len(by[s]) / tot)))
    picked += random.sample(by[s], k)
for s in sorted(by): print(f"{s}: {len(by[s])} rows, sampled {sum(1 for p in picked if p['section']==s)}", file=sys.stderr)
print(f"total rows {tot}, sampled {len(picked)}", file=sys.stderr)
json.dump(picked, open(sys.argv[2], "w"), indent=1)
