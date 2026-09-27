"""RBT-126 (adversary SHOULD 4): are the fields the band reads -- energy and last_score -- consistent in every restored
lineage?  verify_restore.py checks each member's last row against lineage-last.txt, which carries neither field.

Per member and season (ecology.py:510-539): energy_t = energy_{t-1} + last_score_t - living_cost - birth_cost x
(children it paid for at t); the log rounds energy to 3 dp and last_score to 4, so a step is "off" beyond 0.002.
Births per season and fauna are compared with the checkpoint's seasons.txt.  Cull rows are skipped.  The same check
as runs/RBT-126/adversary/adv_energy_books.py (PR #417), written separately and run on every restored run.

python3 runs/RBT-126/verify_energy.py CK_DIR > runs/RBT-126/verify_energy.txt
"""
import collections, glob, json, os, sys

tot_steps = tot_bad = tot_rows = tot_mism = 0
worst_all = 0.0
for d in sorted(glob.glob(os.path.join(sys.argv[1], "rbt-*", "*", "lineage.jsonl"))):
    if "-adv-" in d:
        continue  # the two 160-season adversary probes: no committed result, no seasons.txt
    base = os.path.dirname(d)
    e = json.load(open(os.path.join(base, "config.json")))["ecology"]
    cost, bc = float(e["living_cost"]), float(e["birth_cost"])
    paid, births, rows = collections.Counter(), collections.Counter(), []
    for line in open(d):
        r = json.loads(line)
        if r.get("death") == "cull":
            continue
        rows.append(r)
        if r["evals"] == 0 and r["parents"]:
            paid[(r["generation"], r["population"], r["parents"][0])] += 1
            births[(r["generation"], r["population"])] += 1
    prev, n, bad, worst = {}, 0, 0, 0.0
    for r in rows:
        key = (r["population"], r["name"])
        if r["evals"] > 0 and key in prev and prev[key][0] == r["generation"] - 1:
            want = prev[key][1] + r["last_score"] - cost - bc * paid[(r["generation"], r["population"], r["name"])]
            err = abs(want - r["energy"])
            n += 1; worst = max(worst, err); bad += err > 2e-3
        prev[key] = (r["generation"], r["energy"])
    last = max(r["generation"] for r in rows)
    srows = mism = 0
    sp = os.path.join(base, "seasons.txt")
    for l in (list(open(sp))[1:] if os.path.exists(sp) else []):  # absent from one partial checkpoint's archive
        s, pop, alive, b, *_ = l.split("\t")
        if int(s) > last:
            continue  # a checkpoint taken before the run finished: seasons.txt may run one season past the lineage
        srows += 1; mism += births[(int(s), pop)] != int(b)
    tot_steps += n; tot_bad += bad; tot_rows += srows; tot_mism += mism; worst_all = max(worst_all, worst)
    print(f"{os.path.basename(os.path.dirname(base))}: energy steps {n}, off {bad} (worst {worst:.4f}); births rows {srows}, mismatched {mism}", flush=True)
print(f"ALL: energy steps {tot_steps}, off by > 0.002: {tot_bad} (worst {worst_all:.4f}); season-fauna birth rows {tot_rows}, mismatched {tot_mism}")
