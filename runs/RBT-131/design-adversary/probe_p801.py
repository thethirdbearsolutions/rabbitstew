"""RBT-131 design adversary: the only committed final/ population in the repo (git ls-files) is runs/RBT-19/P-801.
Check it holds exactly the living at season 599: final/ names == lineage.jsonl's generation-599 names, per kind,
lineage generations never restart (no relaunch over the directory), and history's last season is 599 with alive == files.

    python runs/RBT-131/design-adversary/probe_p801.py
"""
import glob, json, os, subprocess
R = "runs/RBT-19/P-801"
tracked = sorted({f.rsplit("/final/", 1)[0].rsplit("/", 1)[0] for f in subprocess.run(["git", "ls-files", "runs", "docs"], capture_output=True, text=True).stdout.split() if "/final/" in f and f.endswith(".json")})
print("run directories with a committed final/:", tracked)
gens, last, restarts, prev = {}, {}, 0, -1
for line in open(f"{R}/lineage.jsonl"):
    r = json.loads(line)
    g = r["generation"]
    if g < prev:
        restarts += 1
    prev = g
    last.setdefault((r["population"], g), set()).add(r["name"])
top = max(g for _, g in last)
print(f"lineage: last generation {top}, generation restarts {restarts}")
h = json.load(open(f"{R}/history.json"))["history"]
for kind in ("holistic", "conventional"):
    files = sorted(glob.glob(f"{R}/{kind}/final/*.json"))
    names = [json.load(open(f))["name"] for f in files]
    alive = last[(kind, top)]
    hl = [e for e in h if e["population"] == kind][-1]
    print(f"{kind:12s} final files {len(files)} distinct {len(set(names))} | lineage gen {top} alive {len(alive)} | "
          f"final == alive: {set(names) == alive} | history last season {hl['season']} alive {hl['alive']}")
