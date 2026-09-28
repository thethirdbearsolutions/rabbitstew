"""RBT-132 design adversary, item 1: every registered RBT-129 row against its committed worlds/<id>.config.json, read
independently (raw JSON, not SimConfig), and the full cross-matrix: point A's config presented as point B.

    python runs/RBT-116/design-adversary/rbt132_registry_probe.py > runs/RBT-116/design-adversary/rbt132_registry_probe.txt

Reads committed config files and steer.py's registry only.  Runs no season.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("steer", os.path.join(ROOT, "runs", "RBT-116", "steer.py"))
steer = importlib.util.module_from_spec(spec)
sys.modules["steer"] = steer
spec.loader.exec_module(steer)
from rabbitstew.simulation import SimConfig  # noqa: E402

WD = os.path.join(ROOT, "runs", "RBT-129", "worlds")
committed = sorted(f[: -len(".config.json")] for f in os.listdir(WD) if f.endswith(".config.json"))
print(f"# committed worlds/<id>.config.json: {len(committed)}; registered RBT-129 points: {len(steer.RBT129_POINTS)}")
print(f"# committed but unregistered: {sorted(set(committed) - set(steer.RBT129_POINTS))}; registered but uncommitted: "
      f"{sorted(set(steer.RBT129_POINTS) - set(committed))}")
raws = {p: json.load(open(os.path.join(WD, f"{p}.config.json"))) for p in committed}
bad_rows = 0
for p in steer.RBT129_POINTS:
    food = raws[p]["sim"]["food"]
    row = steer.REGISTERED_POINTS[p]
    diff = {k: (food.get(k), v) for k, v in row.items() if food.get(k) != v}
    bad_rows += bool(diff)
    print(f"{p:14s} raw food block {'== registry row' if not diff else 'DIFFERS ' + repr(diff)}; fairness {raws[p].get('fairness')!r}; "
          f"pool key {steer.POOL_KEY[p]}")
print(f"# rows differing from their committed config: {bad_rows}")


def accepted(cfg_pid, claim):
    raw = raws[cfg_pid]
    cfg = SimConfig.from_dict(raw["sim"])
    try:
        steer.assert_world_point(cfg, claim)
        steer.assert_registered_channel(cfg, claim)
        steer.assert_fair_config(raw, claim)
        return True
    except (ValueError, KeyError):
        return False


pts = list(steer.RBT129_POINTS)
slips = [(a, b) for a in pts for b in pts if a != b and accepted(a, b)]
print(f"\n# cross-matrix: of {len(pts) * (len(pts) - 1)} (config of A, run as point B) pairs, the three guards accept {len(slips)}")
by = {}
for a, b in slips:
    by.setdefault(a, []).append(b)
for a in pts[:3] + pts[3:6]:
    print(f"  config {a:14s} accepted as: {' '.join(by.get(a, []))}")
worlds = {p: (raws[p]["sim"]["world"]["random_obstacles"], raws[p]["sim"]["world"]["terrain"], raws[p]["sim"]["food"].get("patches")) for p in pts}
diffworld = [(a, b) for a, b in slips if json.dumps(raws[a]["sim"], sort_keys=True) != json.dumps(raws[b]["sim"], sort_keys=True)]
print(f"# of these, pairs whose sim blocks differ (a different world run under B's pool key and label): {len(diffworld)}")
print(f"# W1 claimed on an RBT-129 G config: {'accepted' if accepted('c0-p030-U-G', 'W1') else 'refused'}")
# an unregistered point
try:
    steer.registered_tau("c0-p010-U-G")
    print("# unregistered point c0-p010-U-G: ACCEPTED")
except KeyError:
    print("# unregistered point c0-p010-U-G (a committed Stage-1 world outside the 18): refused (KeyError)")
