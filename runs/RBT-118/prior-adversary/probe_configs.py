"""RBT-118 prior ADVERSARY probe: re-count claim 1 (merge_after) over every committed config.json under runs/.

    python runs/RBT-118/prior-adversary/probe_configs.py > runs/RBT-118/prior-adversary/probe_configs.txt
"""
import collections
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
c = collections.Counter()
for p in sorted(glob.glob(os.path.join(ROOT, "runs", "**", "config.json"), recursive=True)):
    if "/RBT-118/" in p:
        continue
    c["config.json files"] += 1
    e = json.load(open(p)).get("ecology")
    if e is None:
        c["no ecology section (not an ecology run)"] += 1
        continue
    c["ecology configs"] += 1
    if "merge_after" not in e:
        c["ecology configs without the merge_after key (predate it; default None)"] += 1
    elif e["merge_after"] is None:
        c["ecology configs with merge_after = null"] += 1
    else:
        c["ecology configs with merge_after SET"] += 1
        print("MERGED:", os.path.relpath(p, ROOT), e["merge_after"])
print("# RBT-118 prior ADVERSARY, probe_configs.py")
for k, v in c.items():
    print(f"{v:5d}  {k}")
