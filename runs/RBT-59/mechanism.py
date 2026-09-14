"""Why depth is flat: are births energy-limited or slot-limited? (RBT-59)

If income set the reproduction rate, a rich arm would breed faster than a poor
one.  Depth says it does not.  The alternative is that a birth needs a free
slot, slots open only when somebody dies, and deaths are dominated by old age,
so the birth rate is pinned to the death rate whatever anyone earns.

Two things would settle it, both already in the committed files:
  1. births per season against deaths per season, per arm.
  2. the share of the living who are AT or ABOVE the birth threshold and did
     not breed, which is energy sitting idle for want of a slot.
"""
import json, os, statistics as st
from collections import defaultdict

DATA = "runs/RBT-59/data"
ARMS = [a for a in sorted(os.listdir(DATA))]

hdr = f"{'arm':13} {'pop':12} {'gain':>6} {'births/s':>8} {'deaths/s':>8} {'b/d':>5} {'>=thresh':>8} {'meanE':>7} {'thresh':>6}"
print(hdr); print("-" * len(hdr))
rows = []
for arm in ARMS:
    cfg = json.load(open(f"{DATA}/{arm}/config.json"))
    eco = cfg.get("ecology", {})
    thresh = eco.get("birth_threshold")
    hp = f"{DATA}/{arm}/history.json"
    if not os.path.exists(hp):
        continue
    hist = json.load(open(hp)).get("history", [])
    if not hist or max(h["season"] for h in hist) < 100:
        continue  # extinct arms carry no steady state
    # energies of the living at the final season, from the lineage log
    last_energy = defaultdict(list)
    with open(f"{DATA}/{arm}/lineage.jsonl") as f:
        for line in f:
            r = json.loads(line)
            last_energy[(r["population"], r["generation"])].append(r["energy"])
    for kind in ("holistic", "conventional"):
        rs = [h for h in hist if h["population"] == kind and h["season"] >= 100]
        if not rs:
            continue
        b = sum(h["births"] for h in rs) / len(rs)
        d = sum(h["deaths"] for h in rs) / len(rs)
        last = max(h["season"] for h in rs)
        es = last_energy.get((kind, last), [])
        above = sum(1 for e in es if e >= thresh) / len(es) if es else float("nan")
        gain = rs[-1]["mean_lifetime_score"]
        print(f"{arm:13} {kind:12} {gain:6.2f} {b:8.2f} {d:8.2f} {b/max(d,1e-9):5.2f} "
              f"{above:7.0%} {st.mean(es) if es else float('nan'):7.2f} {thresh:6.1f}")
        rows.append(dict(arm=arm, kind=kind, gain=gain, births=b, deaths=d, above=above,
                         mean_energy=st.mean(es) if es else None, thresh=thresh))

json.dump(rows, open("runs/RBT-59/mechanism.json", "w"), indent=2, default=float)
print()
bd = [r["births"] / max(r["deaths"], 1e-9) for r in rows]
print(f"births/deaths across {len(rows)} rows: min {min(bd):.3f}  median {st.median(bd):.3f}  max {max(bd):.3f}")
ab = [r["above"] for r in rows if r["above"] == r["above"]]
print(f"share of the living at or above the birth threshold: min {min(ab):.0%}  median {st.median(ab):.0%}  max {max(ab):.0%}")
xs = [r["gain"] for r in rows]; ys = [r["births"] for r in rows]
mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
den = (sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys)) ** 0.5
print(f"Pearson r(mean gain, births per season) = {num/den if den else float('nan'):+.3f}")
