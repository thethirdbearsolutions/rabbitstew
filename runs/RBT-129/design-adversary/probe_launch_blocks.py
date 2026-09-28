"""Launch-adversary probe L1: do PR #435's world blocks match the committed default world key for key, and are the
axes where r4 puts them?

Compares blocks.config_dict(world_argv(point)) (fair pending, eat = the candidate) with the committed config.json of
RBT-107 fresh base-11 (the default world, RBT-90 part 2's command) and of RBT-90 forage-801, over every dotted key.
Also checks: N and obstacle radius per clutter level and layout; c0 is flat; PW's food block; G's smell block; the
price.  Builds configs only (Ecology is not constructed; no season runs).

python3 probe_launch_blocks.py <PR-435 worktree>
"""
import json
import os
import sys

WT = sys.argv[1]
sys.path.insert(0, os.path.join(WT, "runs/RBT-129/launch"))
sys.path.insert(0, WT)
import blocks as B  # noqa: E402


def flat(d, p=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flat(v, f"{p}{k}."))
        else:
            out[f"{p}{k}"] = v
    return out


refs = {"RBT-107 fresh base-11": "runs/RBT-107/fresh/base-11/config.json", "RBT-90 forage-801": "runs/RBT-90/forage-801/config.json"}
blk = flat(B.config_dict(B.world_argv("c1-p030-U-L")))
print("## 1. c1-p030-U-L (the committed world under the sweep's fixed rows, fair pending) against committed configs")
for name, path in refs.items():
    ref = flat(json.load(open(os.path.join(WT, path))))
    keys = sorted(set(ref) | set(blk))
    diff = [(k, ref.get(k, "<absent>"), blk.get(k, "<absent>")) for k in keys if ref.get(k, "<absent>") != blk.get(k, "<absent>")]
    print(f"# {name}: {len(keys)} keys, {len(diff)} differ")
    for k, a, b in diff:
        print(f"   {k:45s} committed {str(a)[:60]:60s} block {str(b)[:60]}")
print()
print("## 2. axes per point")
bad = 0
for pid in B.all_ids():
    c, p, L, s = B.parse_id(pid)
    f = flat(B.config_dict(B.world_argv(pid)))
    w, fd = "sim.world.", "sim.food."
    n = f[w + "random_obstacles"]; t = f[w + "terrain"]; r = f[w + "random_radius"]
    exp_n = (B.N_PW if L == "PW" else B.N_3M)[c]
    ok = (t == ("flat" if c == 0 else "random")) and (c == 0 or (n == exp_n and r == (3.6 if L == "PW" else 2.6)))
    ok &= abs(f[fd + "work_cost"] - p) < 1e-12
    if L == "PW":
        ok &= (f[fd + "patches"], f[fd + "patch_radius"], f[fd + "radius"], f[fd + "regrow_delay"], f[fd + "smell"], f[fd + "decay"]) == (2, 0.4, 4.0, 60.0, "log", 1.5)
    elif L == "HP":
        ok &= (f[fd + "patches"], f[fd + "patch_radius"], f[fd + "radius"], f[fd + "regrow_delay"], f[fd + "smell"], f[fd + "decay"]) == (3, 0.6, 3.0, 0.0, "sum", 1.0)
    else:
        ok &= (f[fd + "patches"], f[fd + "radius"], f[fd + "regrow_delay"], f[fd + "smell"], f[fd + "decay"]) == (0, 3.0, 0.0, "sum", 1.0)
    sc = {k: v for k, v in f.items() if "contrast" in k or "tau" in k}
    ok &= (s == "L" and all(not v for k, v in sc.items() if "contrast" in k)) or (s == "G" and any(v == 2.5 for k, v in sc.items() if "contrast" in k))
    if not ok or pid in ("c0-p010-U-L", "c2-p080-PW-G", "c05-p018-HP-G"):
        print(f"  {pid:16s} {'OK ' if ok else 'BAD'} terrain {t} N {n} R {r} price {f[fd + 'work_cost']} smell {sc}")
    bad += not ok
print(f"# {bad} of {len(B.all_ids())} points off r4's axes")
