"""Collapse sweep.sh's JSON lines into the report's table."""
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.startswith('{"run"')]
print("| champion | parts | swept corridor | point floor | + body width | + own gait | measured | t | verdict |")
print("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    i = r["rows"]["intact"]
    t = i["t"]
    v = "above" if t >= 2.5 else "below" if t <= -2.5 else "**indistinguishable**"
    name = r["run"].replace("runs/RBT-38/data/", "").replace("runs/", "") + f" {r['kind'][:4]} g{r['gen']}"
    print(f"| {name} | - | {r['swept']:.2f} m | {r['point_floor']:.3f} | {r['line_rate']:.3f} "
          f"(x{r['line_rate']/r['point_floor']:.2f}) | {i['null_per_m']:.3f} "
          f"(x{i['null_per_m']/r['point_floor']:.2f}) | {i['items_per_m']:.3f} | {t:+.2f} | {v} |")
print()
for r in rows:
    i, b = r["rows"]["intact"], r["rows"]["noses blanked"]
    name = r["run"].replace("runs/RBT-38/data/", "").replace("runs/", "") + f" {r['kind'][:4]} g{r['gen']}"
    print(f"{name}: blanked measured {b['items_per_m']:.3f} vs its own null {b['null_per_m']:.3f} "
          f"(t {b['t']:+.2f}); intact items {i['items']:.3f} null {i['null']:.3f}; "
          f"in-disc {i['in_path']:.2f} m, {100*i['time_in_disc']:.0f}% in disc; "
          f"published-style rate {i['published_rate']:.3f} vs null {i['published_null_rate']:.3f}")
