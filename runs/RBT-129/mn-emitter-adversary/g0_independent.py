"""RBT-129 L1 adversary: census g0 and the designed C2 flag at the 36 Stage-1 points, recomputed without stages.py.

    python3 g0_independent.py DATA > g0_independent.txt

DATA holds the census runs restored at DATA/runs/RBT-129/stage0/<point>/<seed>/S (scripts/durable.sh restore from
ckpt/rbt-129-stage0-<point>-<seed>-S).  Stdlib only.  Reads the committed readout and PR #500's mn_rank.txt (from
git, at the PR head) and compares.  Also checks, over every history row of all 108 runs, the invariant that makes the
two "alive at 59" readings (booked vs before refill) the same test of extinction: births > 0 only when alive - births > 0.
"""
import json, os, re, subprocess, sys

DATA = sys.argv[1]
HEAD = sys.argv[2] if len(sys.argv) > 2 else "ebcd38654fb90f1dc967ddea3fc023276553dde0"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
H, D = "holistic", "conventional"
SEEDS = (129001, 129002, 129003)
POINTS = [f"c{c}-p{p}-{L}-G" for c in "012" for p in ("010", "030", "080") for L in ("U", "HP", "PW")] + \
         [f"c1-p{p}-{L}-L" for p in ("010", "030", "080") for L in ("U", "HP", "PW")]
ANCHORS = {"c1-p030-U-L", "c0-p030-U-L", "c1-p030-PW-G"}  # DESIGN 5.2 item 3


def run(pt, s):
    return os.path.join(DATA, "runs", "RBT-129", "stage0", pt, str(s), "S")


out, inv_bad, inv_rows, diff59 = [], 0, 0, 0
res = {}
for pt in POINTS:
    tot, n, dext = 0.0, 0, 0
    for s in SEEDS:
        d = run(pt, s)
        price = json.load(open(os.path.join(d, "config.json")))["sim"]["food"]["work_cost"]
        with open(os.path.join(d, "lineage.jsonl")) as f:
            for line in f:
                r = json.loads(line)
                if r.get("death") in ("cull", "merge-null"):
                    continue
                if 30 <= r["generation"] <= 59:
                    tot += r.get("food", 0.0) - price * r.get("work", 0.0) / 1000.0
                    n += 1
        hist = json.load(open(os.path.join(d, "history.json")))["history"]
        for e in hist:
            inv_rows += 1
            if e["births"] > 0 and e["alive"] - e["births"] <= 0:
                inv_bad += 1
        row = {e["population"]: e for e in hist if e["season"] == 59}
        e = row.get(D)
        if e is None or e["alive"] - e["births"] == 0:
            dext += 1
        for k in (H, D):
            a = row.get(k)
            booked = a is not None and a["alive"] > 0
            before = a is not None and a["alive"] - a["births"] > 0
            diff59 += booked != before
    res[pt] = (tot / n + 0.35 if n else None, dext >= 2, n)

# the committed readout
txt = open(os.path.join(REPO, "runs/RBT-129/stageP0-readout/stageP0_readout.txt")).read()
txt = txt[txt.index("## Stage 0 census layer"):]
ro_ff = set(x.strip() for x in re.search(r"  conventional: \d+ of \d+ points: (.*)", txt).group(1).split(","))
ro = {}
for line in txt.split("per point (seeds pooled)")[1].splitlines()[1:]:
    if not line.strip():
        break
    c = line.split("|")
    v = c[5].strip()
    ro[c[0].split()[0]] = None if v == "--" else float(v)
# PR #500's mn_rank.txt
mr = subprocess.run(["git", "show", f"{HEAD}:runs/RBT-129/mn-emitter/mn_rank.txt"], cwd=REPO, capture_output=True, text=True).stdout
pr = {}
for line in mr.splitlines():
    m = re.match(r"\s+\d+\s+(\S+)\s+(\S+)\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+(yes|no)", line)
    if m:
        pr[m.group(1)] = (None if m.group(2) == "--" else float(m.group(2)), m.group(3) == "yes", m.group(5) == "yes", m.group(6) == "yes")

order = sorted(POINTS, key=lambda p: (res[p][0] is None, res[p][0] or 0.0, p))
out.append("# census g0 at the 36 Stage-1 points, recomputed independently (T5: seasons 30-59, every member-season, 129001-3,")
out.append("# both faunas pooled, net = food - p * work / 1000, + 0.35); D-FF = designed extinct at 59 before refill on >= 2 of 3")
out.append("# rank point            g0(mine)  n     g0(readout) g0(PR)  D-FF(mine/readout/PR)  M-ok(mine/PR) N-ok literal-item-2 N-ok(PR)")
bad = 0
for i, p in enumerate(order, 1):
    g, ff, n = res[p]
    m_ok = g is not None and g <= 1.0 and not ff and p not in ANCHORS
    n_lit = g is not None and g <= 0.8 and p not in ANCHORS  # item 2 read alone: g0 <= 0.8, no FOUNDING-FAIL clause
    gr, gp = ro.get(p, "missing"), pr[p][0]
    agree = (g is None and gr is None and gp is None) or (g is not None and gr is not None and gp is not None
                                                          and round(g, 3) == gr == gp)
    agree = agree and ff == (p in ro_ff) == pr[p][1] and m_ok == pr[p][2]
    bad += not agree
    fmt = lambda x: "   --" if x is None else f"{x:.3f}"
    out.append(f"  {i:3d} {p:15s} {fmt(g):>8s} {n:5d}  {fmt(gr):>8s}  {fmt(gp):>8s}  {ff!s:5}/{(p in ro_ff)!s:5}/{pr[p][1]!s:5}"
               f"        {m_ok!s:5}/{pr[p][2]!s:5}  {n_lit!s:5}          {pr[p][3]!s:5}  {'' if agree else 'DISAGREE'}")
out.append("")
out.append(f"disagreements with the committed readout or PR #500's ranking: {bad}")
out.append(f"M-eligible (mine): {sum(1 for p in POINTS if res[p][0] is not None and res[p][0] <= 1.0 and not res[p][1] and p not in ANCHORS)}")
lit = [p for p in order if res[p][0] is not None and res[p][0] <= 0.8 and p not in ANCHORS]
out.append(f"N, item 2 read alone (g0 <= 0.8, not an anchor), rank order: {', '.join(lit)}")
out.append(f"  first 4: {', '.join(lit[:4])}")
ns = [p for p in lit if not res[p][1]]
out.append(f"N as PR #500 reads it (M-eligible and g0 <= 0.8), first 4 if every seed valid: {', '.join(ns[:4])}")
out.append("")
out.append(f"history rows checked: {inv_rows}; rows with births > 0 and alive - births <= 0: {inv_bad}")
out.append(f"fauna-seeds at season 59 where 'alive > 0' and 'alive - births > 0' disagree: {diff59} of {len(POINTS) * 3 * 2}")
print("\n".join(out))
