"""RBT-126: is a checkpoint-restored lineage.jsonl the committed run's?  Rebuild each member's last row from the
restored lineage and compare it with the run's committed lineage-last.txt (population, name, generation, age, evals,
fitness, parents).  A checkpoint taken before the run finished (MANIFEST k/N with k < N) matches only on the members
whose last row falls before the checkpoint.

python3 runs/RBT-126/verify_restore.py CK_DIR"""
import glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO_DIR = {"90": "runs/RBT-90/forage-{a}", "99": "runs/RBT-99/{a}", "100": "runs/RBT-100/{a}", "101": "runs/RBT-101/{a}", "104": "runs/RBT-104/{a}",
            "105": "runs/RBT-105/forage-{a}", "106": "runs/RBT-106/{a}", "107": "runs/RBT-107/{a2}", "112": "runs/RBT-112/{a}"}
for d in sorted(glob.glob(os.path.join(sys.argv[1], "rbt-*"))):
    t, arm = re.match(r"rbt-(\d+)-(.*)$", os.path.basename(d)).groups()
    inner = [x for x in glob.glob(os.path.join(d, "*")) if os.path.isdir(x)][0]
    man = open(os.path.join(d, "MANIFEST")).read().split()[1]
    done, total = map(int, man.split("/"))
    committed = os.path.join(ROOT, REPO_DIR[t].format(a=arm, a2=arm.replace("fresh-", "fresh/")), "lineage-last.txt")
    if not os.path.exists(committed):
        print(f"RBT-{t} {arm}: checkpoint {man}; no committed lineage-last.txt at {os.path.relpath(committed, ROOT)}"); continue
    last = {}
    for l in open(os.path.join(inner, "lineage.jsonl")):
        r = json.loads(l)
        # a cull's row (death: cull) is that member's last row in lineage-last.txt too
        last[(r["population"], r["name"])] = (r["generation"], r["age"], r["evals"], r["fitness"], ",".join(r["parents"]))
    rows = [x.rstrip("\n").split("\t") for x in open(committed)][1:]
    ok = bad = skipped = 0
    for p, n, g, a, e, f, par in rows:
        mine = last.get((p, n))
        if int(g) >= done - 1:
            skipped += 1; continue
        if mine and mine[0] == int(g) and mine[1] == int(a) and mine[2] == int(e) and abs(mine[3] - float(f)) < 1e-4 and mine[4] == par:
            ok += 1
        else:
            bad += 1
    print(f"RBT-{t} {arm}: checkpoint {man}; committed lineage-last rows matched {ok}, mismatched {bad}, after the checkpoint {skipped}")
