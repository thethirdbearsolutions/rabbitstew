"""Season readout for an ecology run: alive / births / deaths / mean gain at chosen seasons, the
bottleneck and recovery, the first season the holistic mean gain exceeds the wheeled, extinctions."""
import json, sys
run = sys.argv[1]
d = json.load(open(f"{run}/history.json"))
by = {}
for e in d["history"]:
    by.setdefault(e["season"], {})[e["population"]] = e
seasons = sorted(by)
want = [0, 11, 20, 32, 60, 100, 200, 300, 400, 500, 599]
print("season | holistic alive births deaths mean | wheeled alive births deaths mean")
for s in want:
    if s not in by: continue
    h, c = by[s].get("holistic"), by[s].get("conventional")
    f = lambda e: f"{e['alive']:3d} {e['births']:3d} {e['deaths']:3d} {e['mean_lifetime_score']:+.2f}" if e else "  extinct"
    print(f"{s:6d} | {f(h)} | {f(c)}")
for kind in ("holistic", "conventional"):
    rows = [(s, by[s][kind]) for s in seasons if kind in by[s]]
    alive = [(s, e["alive"]) for s, e in rows]
    mn = min(alive, key=lambda t: t[1])
    rec = next((s for s, a in alive if s > mn[0] and a >= 60), None)
    ext = next((s for s, a in alive if a == 0), None)
    last = rows[-1][0]
    print(f"{kind:12s}: min alive {mn[1]} at season {mn[0]}; back to 60 at {rec}; extinct at {ext}; last season recorded {last}; alive at last {alive[-1][1]}")
first = next((s for s in seasons if "holistic" in by[s] and "conventional" in by[s] and by[s]["holistic"]["mean_lifetime_score"] > by[s]["conventional"]["mean_lifetime_score"] and by[s]["holistic"]["alive"] > 0), None)
print("first season holistic mean gain > wheeled:", first)
# runs of consecutive seasons where holistic > wheeled, from 100 on
above = [s for s in seasons if s >= 100 and "holistic" in by[s] and "conventional" in by[s] and by[s]["holistic"]["mean_lifetime_score"] > by[s]["conventional"]["mean_lifetime_score"]]
print(f"seasons >= 100 with holistic mean > wheeled: {len(above)} of {len([s for s in seasons if s >= 100])}")
