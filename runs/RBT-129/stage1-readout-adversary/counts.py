"""Recompute the Stage-1 integrity counts from the lane files (job lines only), without stages.py or the plan's script."""
import collections, glob, json, os, sys
R = sys.argv[1] if len(sys.argv) > 1 else "."
L1 = sorted(glob.glob(f"{R}/runs/RBT-129/lanes/1/*.jsonl"))
MN = sorted(glob.glob(f"{R}/runs/RBT-129/lanes/1-MN/*.jsonl"))
def rows(p): return [json.loads(l) for l in open(p) if l.strip()]
print("lanes/1 files", len(L1), " lanes/1-MN files", len(MN))
j1 = [j for p in L1 for j in rows(p)]
names1 = [j["name"] for j in j1]
print("lanes/1 job lines", len(j1), "distinct names", len(set(names1)))
print("lanes/1 by type", dict(collections.Counter(j["job"] for j in j1)))
dirs1 = {j["dir"] for j in j1}
print("lanes/1 distinct dirs", len(dirs1), dict(collections.Counter(os.path.basename(d) for d in dirs1)))
def unit(j): return os.path.dirname(j["src"] if j["job"] in ("snapshot", "fork") else j["dir"])
units1 = {unit(j) for j in j1}
print("lanes/1 units (records)", len(units1))
pts = {j["dir"].split("/")[3] for j in j1}; seeds = {j["dir"].split("/")[4] for j in j1}
print("points", len(pts), "seeds", sorted(seeds))
ks = [j for j in j1 if j["job"] == "ksalt"]
print("ksalt jobs", len(ks), "by seed", dict(collections.Counter(j["dir"].split("/")[4] for j in ks)))
fr = collections.Counter(j["dir"].split("/")[4] for j in j1 if j["job"] in ("fresh",))
ad = collections.Counter(j["dir"].split("/")[4] for j in j1 if j["job"] in ("adopt",))
print("fresh by seed", dict(fr), "adopt by seed", dict(ad))
# MN
mn = {os.path.basename(p): rows(p) for p in MN}
a0, b0 = [j["name"] for j in mn["host1-lane0.jsonl"]], [j["name"] for j in mn["host1-lane0b.jsonl"]]
print("host1-lane0 minus lane0b", sorted(set(a0) - set(b0)), " lane0b subset:", set(b0) <= set(a0), " lane0b minus lane0", sorted(set(b0)-set(a0)))
use = [p for p in MN if os.path.basename(p) != "host1-lane0.jsonl"]
jm = [j for p in use for j in rows(p)]
print("1-MN (lane0b in place of lane0): job lines", len(jm), "distinct names", len({j['name'] for j in jm}), "types", dict(collections.Counter(j['job'] for j in jm)))
dm = {j["dir"] for j in jm}
print("1-MN distinct dirs", len(dm), dict(collections.Counter(os.path.basename(d) for d in dm)))
dup = [n for n, c in collections.Counter(j["name"] for j in jm).items() if c > 1]
print("1-MN names scheduled twice", sorted(dup))
allm = [j for p in MN for j in rows(p)]
print("1-MN all 21 files: distinct names", len({j['name'] for j in allm}))
forks = open(f"{R}/runs/RBT-129/lanes/1-MN/launch.txt").read().split("\nforks ")[1].split("\n")[0].split()
print("launch forks line", len(forks), "distinct", len(set(forks)), "M", sum(f.endswith('/M') for f in forks), "N", sum(f.endswith('/N') for f in forks))
print("forks line minus loaded", sorted(set("1/"+f for f in forks) - {j['name'] for j in jm}), " loaded minus line", sorted({j['name'] for j in jm} - set("1/"+f for f in forks)))
# expected labels as stages.expected_branches: every dir + record of every 1/ job's unit
exp = set(dirs1) | {u + "/record" for u in units1} | set(dm) | {unit(j) + "/record" for j in jm}
print("expected labels", len(exp), " = dirs1", len(dirs1), "+ records", len({u + '/record' for u in units1} | {unit(j) + '/record' for j in jm}), "+ MN dirs", len(dm))
q = "runs/RBT-129/stage1/c2-p030-U-G/129001/M"
print("quarantined dir in expected:", q in exp)
# platform dirs: dirs of fresh/adopt/resume/snapshot/fork
plat = {j["dir"] for j in j1 + jm if j["job"] in ("fresh", "adopt", "resume", "snapshot", "fork")}
print("platform dirs", len(plat), dict(collections.Counter(os.path.basename(d) for d in plat)))
# markers: one per job name
print("markers (distinct job names, lanes/1 + 1-MN)", len(set(names1) | {j['name'] for j in jm}))
# the gate: admitted per point vs lanes
adm = open(f"{R}/runs/RBT-129/lanes/1-MN/launch.txt").read().split("\nadmitted ")[1].split("\n")[0].split()
print("admitted", adm)
mseeds = collections.defaultdict(list)
for f in forks:
    p, s, a = f.split("/"); mseeds[(p, a)].append(int(s))
for (p, a), ss in sorted(mseeds.items()):
    odd = sum(s % 2 for s in ss)
    if a == "N": print("  N", p, sorted(ss), "odd(holistic null)", odd, "even(designed null)", len(ss) - odd)
