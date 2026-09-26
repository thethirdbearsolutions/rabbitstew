"""RBT-107 gate V-POST (Amendment 2, F9): the arm's world after the join is the one registered, from its own bulk.

    python runs/RBT-107/vpost.py ARM_DIR {base|shift|cull20|cull} T [LAST]

Reads history.json (one entry per season, with terrain_seed) and events.txt, and the table seasons.txt:
  shift          terrain_seed is None in every season s >= T through the last; not None before T
  base, cull20,  terrain_seed is not None in every season (random terrain throughout)
  cull
  cull20, cull   exactly one cull event, at T; base and shift: no cull event
  every arm      the last season is >= LAST (default T + 800) and seasons.txt holds every season 0..last for both faunas
V-EXT (prefix_check.py) checks the continuation's past; this checks its future.  Run after the post-run tables.
"""
import csv
import json
import os
import sys


def main(d, arm, T, last_needed):
    ok = True

    def say(name, good, detail):
        nonlocal ok
        ok &= good
        print(f"{name}: {'PASS' if good else 'FAIL'} ({detail})")

    ts = {}
    for h in json.load(open(os.path.join(d, "history.json")))["history"]:  # one entry per season and fauna
        ts.setdefault(int(h["season"]), set()).add(h.get("terrain_seed"))
    if any(len(v) != 1 for v in ts.values()):
        say("terrain", False, "the two faunas' entries disagree on terrain_seed in some season")
    ts = {s: next(iter(v)) for s, v in ts.items()}
    last = max(ts)
    if arm == "shift":
        bad = [s for s, v in ts.items() if (v is not None) == (s >= T)]
        say("terrain", not bad, f"terrain_seed None from {T} on and set before; {len(bad)} seasons wrong" + (f", first {min(bad)}" if bad else ""))
    else:
        bad = [s for s, v in ts.items() if v is None]
        say("terrain", not bad, f"terrain_seed set in every season; {len(bad)} seasons None" + (f", first {min(bad)}" if bad else ""))
    ev = []
    p = os.path.join(d, "events.txt")
    if os.path.exists(p):
        ev = [r for r in csv.DictReader(open(p), delimiter="\t")]
    culls = sorted({int(r["season"]) for r in ev if r["kind"] == "cull"})
    if arm in ("cull20", "cull"):
        say("cull", culls == [T], f"cull seasons {culls}, expected [{T}]")
    else:
        say("cull", not culls, f"cull seasons {culls}, expected none")
    rows = {(int(r["season"]), r["population"]) for r in csv.DictReader(open(os.path.join(d, "seasons.txt")), delimiter="\t")}
    missing = [(s, k) for s in range(last + 1) for k in ("holistic", "conventional") if (s, k) not in rows]
    say("length", last >= last_needed and not missing, f"last season {last}, needed >= {last_needed}; {len(missing)} table rows missing")
    print(f"V-POST {'PASS' if ok else 'FAIL'}: {d} ({arm}, T = {T})")
    return 0 if ok else 1


if __name__ == "__main__":
    T = int(sys.argv[3])
    sys.exit(main(sys.argv[1], sys.argv[2], T, int(sys.argv[4]) if len(sys.argv) > 4 else T + 800))
