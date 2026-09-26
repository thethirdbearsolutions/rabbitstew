"""RBT-100 (C3): the own-net and stored-energy table, per season and fauna, written from one arm's bulk.

    python runs/RBT-100/own_table.py RUN_DIR [--to OUT_DIR]      ->  OUT_DIR/own.txt (default RUN_DIR/own.txt)

Why (adversary round 1, F3): the axis, `mean_lifetime_score`, is a lifetime mean over the living.  Under a
budget shift it lags the season's own income by the residents' pre-T earnings in the transient and
excludes the starved recruits in recovery, so it cannot say whether a population pays its way.  The
committed tables carry neither stored energy nor the season's own gain; this table does, from
history.json and lineage.jsonl (bulk), so that the readout can read them from committed files.

One row per (season, population):

  alive            history.json's alive at the end of the season
  energy_head      history.json's total_energy / alive (stored energy a head; "-" if alive = 0)
  ran              individuals who ran the season and survived it (lineage row at this season, age >= 1)
  starved          individuals who ran the season and died of energy <= 0 in it (last lineage row at the
                   season before, age + 1 < max_age, not culled, and not alive at the run's last season)
  aged             individuals who died of age in the season (last row at the season before, age + 1 >= max_age)
  net_survivors    mean last_score (the season's own net: food - work charge) over `ran`
  net_all_ub       an UPPER BOUND on the mean own net over everyone who ran the season, the starved included:
                   a starved individual's net that season is at most 0.25 - (its stored energy after the
                   season before), since E + net - 0.25 <= 0; the aged-out are left out (their net is not
                   logged and not bounded).  net_all_ub < 0.25 therefore means the season's runners, the
                   starved recruits included, earned below the basal cost on average, for certain
  food, work       mean items eaten and work charge (0.03 per kJ) over `ran`

Check, printed on every write: starved + aged (+ culled) equals history.json's deaths in every
(season, fauna) cell but season 0 (a founder that dies in season 0 has no row before it).

Dead individuals get no lineage row for the season they die in (`Ecology._record` logs the living after
deaths and births), which is why the starved enter through the bound and not through their own net.
"""
import json
import os
import statistics
import sys

BASAL = 0.25
MAX_AGE = 60
WORK_COST = 0.03  # per kJ; lineage work is in J
KINDS = ("holistic", "conventional")


def build(run):
    hist = json.load(open(os.path.join(run, "history.json")))["history"]
    H = {(h["season"], h["population"]): h for h in hist}
    last = max(s for s, _ in H)
    rows = {}  # (season, kind) -> list of rows of the living at the end of that season
    lastrow = {}
    culled = set()
    with open(os.path.join(run, "lineage.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            key = (r["population"], r["name"])
            if r.get("death") == "cull":
                culled.add(key)
                continue
            rows.setdefault((r["generation"], r["population"]), []).append(r)
            lastrow[key] = r
    dead = {}  # (season of death, kind) -> [(cause, energy after the season before)]
    for key, r in lastrow.items():
        if key in culled or r["generation"] >= last:
            continue
        cause = "aged" if r["age"] + 1 >= MAX_AGE else "starved"
        dead.setdefault((r["generation"] + 1, key[0]), []).append((cause, r["energy"]))
    out = []
    for s in range(last + 1):
        for k in KINDS:
            h = H.get((s, k))
            alive = h["alive"] if h else 0
            eh = (h["total_energy"] / alive) if h and alive else None
            ran = [r for r in rows.get((s, k), []) if r["age"] >= 1]
            d = dead.get((s, k), [])
            st = [e for c, e in d if c == "starved"]
            ag = sum(1 for c, _ in d if c == "aged")
            ns = statistics.fmean(r["last_score"] for r in ran) if ran else None
            ub = ((sum(r["last_score"] for r in ran) + sum(BASAL - e for e in st)) / (len(ran) + len(st))) if (ran or st) else None
            fr = [r for r in ran if "food" in r]
            food = statistics.fmean(r["food"] for r in fr) if fr else None
            work = statistics.fmean(WORK_COST * r["work"] / 1000 for r in fr) if fr else None
            out.append((s, k, alive, eh, len(ran), len(st), ag, ns, ub, food, work))
    return out, H


def reconcile(out, H):
    cells = [(s, k, st + ag + H[(s, k)].get("culled", {}).get(k, 0) == H[(s, k)]["deaths"])
             for s, k, alive, eh, ran, st, ag, *_ in out if s > 0 and (s, k) in H]
    return sum(ok for *_, ok in cells), len(cells)


def fmt(x):
    return "-" if x is None else f"{x:.4f}"


def write(out, path):
    with open(path, "w") as f:
        f.write("season\tpopulation\talive\tenergy_head\tran\tstarved\taged\tnet_survivors\tnet_all_ub\tfood\twork\n")
        for s, k, alive, eh, ran, st, ag, ns, ub, food, work in out:
            f.write(f"{s}\t{k}\t{alive}\t{fmt(eh)}\t{ran}\t{st}\t{ag}\t{fmt(ns)}\t{fmt(ub)}\t{fmt(food)}\t{fmt(work)}\n")


def main(argv):
    run = argv[0]
    to = argv[argv.index("--to") + 1] if "--to" in argv else run
    os.makedirs(to, exist_ok=True)
    out, H = build(run)
    write(out, os.path.join(to, "own.txt"))
    ok, n = reconcile(out, H)
    print(f"{os.path.join(to, 'own.txt')} written; starved + aged (+ culled) = history deaths on {ok}/{n} cells (seasons >= 1)")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
