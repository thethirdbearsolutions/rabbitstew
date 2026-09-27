"""RBT-126 adversary, probe 4: are the fields the band reads (energy, last_score) consistent in the restored lineages?

verify_restore.py compares each member's LAST row (generation, age, evals, fitness, parents) with the committed
lineage-last.txt; energy and last_score are not in lineage-last.txt, so they are unchecked there.  Here, per member
and season (ecology.py:510-539): energy_t = energy_{t-1} + last_score_t - living_cost - birth_cost x (children paid
at t), with energy rounded to 3 dp and last_score to 4 dp in the log; and births per season per fauna are compared
with the checkpoint's seasons.txt.  Cull rows (death: cull) are skipped.

python3 runs/RBT-126/adversary/adv_energy_books.py CK_DIR RUN [RUN ...] > runs/RBT-126/adversary/adv_energy_books.txt
"""
import collections, glob, json, os, sys

ck = sys.argv[1]
for run in sys.argv[2:]:
    d = glob.glob(os.path.join(ck, run, "*", "lineage.jsonl"))[0]
    base = os.path.dirname(d)
    e = json.load(open(os.path.join(base, "config.json")))["ecology"]
    cost, bc = float(e["living_cost"]), float(e["birth_cost"])
    prev, paid, births = {}, collections.Counter(), collections.Counter()
    rows = []
    for line in open(d):
        r = json.loads(line)
        if r.get("death") == "cull":
            continue
        rows.append(r)
        if r["evals"] == 0 and r["parents"]:
            paid[(r["generation"], r["population"], r["parents"][0])] += 1
            births[(r["generation"], r["population"])] += 1
    n = bad = 0
    worst = 0.0
    for r in rows:
        key = (r["population"], r["name"])
        if r["evals"] > 0 and key in prev and prev[key][0] == r["generation"] - 1:
            exp = prev[key][1] + r["last_score"] - cost - bc * paid[(r["generation"], r["population"], r["name"])]
            err = abs(exp - r["energy"])
            n += 1
            worst = max(worst, err)
            bad += err > 2e-3
        prev[key] = (r["generation"], r["energy"])
    sb = mism = 0
    for l in list(open(os.path.join(base, "seasons.txt")))[1:]:
        s, pop, alive, b, *_ = l.split("\t")
        sb += 1
        mism += births[(int(s), pop)] != int(b)
    print(f"{run}: energy books {n} member-season steps, {bad} off by > 0.002 (worst {worst:.4f}); "
          f"births vs seasons.txt: {sb} season-fauna rows, {mism} mismatched", flush=True)
