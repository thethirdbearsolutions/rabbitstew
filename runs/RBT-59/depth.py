"""Realised search depth per arm: reproduction events, not seasons (RBT-59).

Every design decision in the fan-out is denominated in seasons; selection is
denominated in reproduction events.  `Ecology._breed` applies exactly one
mutation per reproduction and sets parents[0] to the individual copied from,
so the first-parent chain length from a survivor back to a founder IS the
number of sequential mutations that lineage underwent.

No simulation.  File analysis only.
"""
import json, os, statistics as st, sys
from collections import defaultdict

DATA = "runs/RBT-59/data"


def load(arm):
    lin = defaultdict(dict)  # kind -> name -> last record
    with open(f"{DATA}/{arm}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            lin[r["population"]][r["name"]] = r
    cfg = json.load(open(f"{DATA}/{arm}/config.json"))
    hist = []
    p = f"{DATA}/{arm}/history.json"
    if os.path.exists(p):
        hist = json.load(open(p)).get("history", [])
    return lin, cfg, hist


def depths(records):
    """First-parent chain length to a founder, per individual alive at the last season."""
    last = max(r["generation"] for r in records.values())
    alive = [r for r in records.values() if r["generation"] == last]
    out, founders = [], set()
    for r in alive:
        d, cur, seen = 0, r, set()
        while cur["parents"] and cur["parents"][0] in records and cur["name"] not in seen:
            seen.add(cur["name"])
            cur = records[cur["parents"][0]]
            d += 1
        out.append(d)
        founders.add(cur["name"])
    return last, out, len(founders), len(alive)


def main():
    arms = sorted(os.listdir(DATA))
    rows = []
    for arm in arms:
        lin, cfg, hist = load(arm)
        eco = cfg.get("ecology", {})
        for kind in ("holistic", "conventional"):
            if kind not in lin or not lin[kind]:
                continue
            last, ds, nfounders, nalive = depths(lin[kind])
            if not ds:
                continue
            gain = next((h["mean_lifetime_score"] for h in reversed(hist)
                         if h.get("population") == kind), float("nan"))
            rows.append(dict(
                arm=arm, kind=kind, last_season=last, alive=nalive, founders=nfounders,
                median=st.median(ds), mx=max(ds), mn=min(ds),
                seasons_per_rep=(last / st.median(ds)) if st.median(ds) else float("inf"),
                gain=gain, seasons=eco.get("seasons"), capacity=eco.get("capacity"),
                max_age=eco.get("max_age"), birth_threshold=eco.get("birth_threshold"),
                birth_cost=eco.get("birth_cost"), living_cost=eco.get("living_cost"),
            ))
    hdr = f"{'arm':13} {'pop':12} {'last':>5} {'alive':>5} {'fnd':>4} {'depth med':>9} {'max':>4} {'min':>4} {'seas/rep':>8} {'gain':>7} {'maxage':>6}"
    print(hdr); print("-" * len(hdr))
    for r in sorted(rows, key=lambda r: (-r["median"], r["arm"])):
        print(f"{r['arm']:13} {r['kind']:12} {r['last_season']:5d} {r['alive']:5d} {r['founders']:4d} "
              f"{r['median']:9.1f} {r['mx']:4d} {r['mn']:4d} {r['seasons_per_rep']:8.1f} {r['gain']:7.2f} {r['max_age'] or 0:6d}")
    json.dump(rows, open("runs/RBT-59/depth.json", "w"), indent=2, default=float)

    surv = [r for r in rows if r["last_season"] >= 100]
    print(f"\nsurviving arms (ran past season 100): {len(surv)} population-rows")
    if surv:
        meds = [r["median"] for r in surv]
        print(f"  median depth across them: min {min(meds):.0f}, median {st.median(meds):.0f}, max {max(meds):.0f}")
        print(f"  seasons per reproduction event: {min(r['seasons_per_rep'] for r in surv):.1f} to {max(r['seasons_per_rep'] for r in surv):.1f}")
        gs = [(r["gain"], r["median"]) for r in surv if r["gain"] == r["gain"]]
        if len(gs) > 2:
            xs, ys = [g for g, _ in gs], [d for _, d in gs]
            mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
            num = sum((x-mx)*(y-my) for x, y in gs)
            den = (sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys)) ** 0.5
            print(f"  Pearson r(mean gain, median depth) = {num/den if den else float('nan'):+.3f}  over n={len(gs)}")
        ages = sorted({r["max_age"] for r in surv})
        print(f"  max_age values present: {ages}")
        for a in ages:
            sub = [r["median"] for r in surv if r["max_age"] == a]
            print(f"    max_age {a}: median depth {st.median(sub):.1f} over {len(sub)} rows")


if __name__ == "__main__":
    main()
