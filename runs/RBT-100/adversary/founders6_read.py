"""RBT-100 adversary probe P2 readout: random founders at six items, per seed and fauna.

    python runs/RBT-100/adversary/founders6_read.py 801 1 901 804 > runs/RBT-100/adversary/founders6_read.txt

Reads runs/RBT-100/data/founders6-SEED/history.json (bulk, made by founders6_run.sh).  docs/foraging-world.md
"Six items" (seed 801, pre-RBT-95 generator): holistic starved out by season 15, designed bottlenecked to 11
by season 17 and extinct at 51.
"""
import json
import sys

for seed in sys.argv[1:]:
    h = json.load(open(f"runs/RBT-100/data/founders6-{seed}/history.json"))["history"]
    last = max(e["season"] for e in h)
    for k in ("holistic", "conventional"):
        rows = {e["season"]: e for e in h if e["population"] == k}
        alive = [rows[s]["alive"] if s in rows else 0 for s in range(last + 1)]
        ext = next((s for s, a in enumerate(alive) if a == 0), None)
        mn = min(alive)
        pts = " ".join(f"{s}:{alive[s]}" for s in (0, 5, 10, 11, 12, 15, 20, 30, last) if s <= last)
        births = sum(rows[s]["births"] for s in rows)
        late = [rows[s]["mean_lifetime_score"] for s in range(max(0, last - 9), last + 1) if s in rows]
        print(f"seed {seed:>4} {k:12s} alive {pts}  min {mn:>2} (season {alive.index(mn)})  extinct {'-' if ext is None else ext}"
              f"  births {births:>4}  mean_lifetime_score last 10 seasons {sum(late) / len(late) if late else float('nan'):+.3f}  (to season {last})")
