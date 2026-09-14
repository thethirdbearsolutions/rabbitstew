"""RBT-45: render cells.json as the tables the report asks for."""

from __future__ import annotations

import json
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-45/cells.json"
d = json.load(open(PATH))
cells = d["cells"]
K = list(d["k_values"])
ADD = list(d["add_rates"])
EXTRA_K = sorted({c["k"] for c in cells if c["kind"] == "conventional" and c["k"] not in K})


def get(kind, add, rem, k):
    for c in cells:
        if c["kind"] == kind and c["add_link_rate"] == add and c["remove_link_rate"] == rem and c["k"] == k:
            return c
    return None


def grid(metric, kind="conventional", rem=0.1):
    ks = sorted(set(K) | set(EXTRA_K)) if kind == "conventional" else K
    print(f"\n### {metric.upper()}  ({kind}, remove_link_rate {rem})\n")
    print("| k | " + " | ".join(f"add={a}" for a in ADD) + " |")
    print("|" + "---|" * (len(ADD) + 1))
    for k in ks:
        row = []
        for a in ADD:
            c = get(kind, a, rem, k)
            row.append("." if c is None else f"{c[metric]:.3f}")
        mark = " *" if k in EXTRA_K else ""
        print(f"| {k}{mark} | " + " | ".join(row) + " |")


for m in ("pair", "half", "chassis", "uncrossed", "crossed"):
    grid(m)

print("\n### Holistic (add=0.15, rem=0.1)\n")
print("| k | PAIR | HALF | CHASSIS | mean food sensors wired | mean links |")
print("|---|---|---|---|---|---|")
for k in K:
    c = get("holistic", 0.15, 0.1, k)
    print(f"| {k} | {c['pair']:.3f} | {c['half']:.3f} | {c['chassis']:.3f} | {c['mean_food_wired']:.3f} | {c['mean_links']:.1f} |")

print("\n### Removal sweep (conventional, add=0.15, k=50)\n")
print("| remove_link_rate | PAIR | HALF | CHASSIS | uncrossed | crossed | mean links |")
print("|---|---|---|---|---|---|---|")
for rem in d["remove_rates"]:
    c = get("conventional", 0.15, rem, 50)
    print(f"| {rem} | {c['pair']:.3f} | {c['half']:.3f} | {c['chassis']:.3f} | {c['uncrossed']:.3f} | {c['crossed']:.3f} | {c['mean_links']:.1f} |")

if "pair_at" in cells[0] or any("pair_at" in c for c in cells):
    print("\n### PAIR by strength threshold (conventional, add=0.15, rem=0.1)\n")
    print("| k | >0 | >0.1 | >1 | >10 | median strength when present | mean chassis influence |")
    print("|---|---|---|---|---|---|---|")
    for k in sorted(set(K) | set(EXTRA_K)):
        c = get("conventional", 0.15, 0.1, k)
        if c is None or "pair_at" not in c:
            continue
        q = c["pair_strength_q"]
        print(
            f"| {k} | {c['pair_at']['0.0']:.3f} | {c['pair_at']['0.1']:.3f} | {c['pair_at']['1.0']:.3f} | "
            f"{c['pair_at']['10.0']:.3f} | {'-' if q is None else q[1]} | {c['mean_chassis_infl']:.0f} |"
        )

b = d["parent_baseline"]
print("\n### Parent populations before any mutation (k=0)\n")
print("| population | n | PAIR | HALF | CHASSIS | mean food wired | mean links |")
print("|---|---|---|---|---|---|---|")
for kind in ("conventional", "holistic"):
    c = b[kind]
    print(f"| {kind} | {c['n']} | {c['pair']:.3f} | {c['half']:.3f} | {c['chassis']:.3f} | {c['mean_food_wired']:.3f} | {c['mean_links']:.1f} |")

ld = d["lineage_depth"]
print("\n### Ancestral depth, conventional, individuals alive at season 599\n")
print(json.dumps({k: v for k, v in ld.items() if k != "first_parent_values"}, indent=1))
print("\nholistic:", json.dumps({k: v for k, v in d["lineage_depth_holistic"].items() if k != "first_parent_values"}))
