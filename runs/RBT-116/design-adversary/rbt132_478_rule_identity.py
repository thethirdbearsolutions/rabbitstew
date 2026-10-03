"""RBT-132 gate check of #478: at RBT-129's 18 points, does ``screen_draws`` change ONLY in the admission rule?

    python runs/RBT-116/design-adversary/rbt132_478_rule_identity.py > runs/RBT-116/design-adversary/rbt132_478_rule_identity.txt

Independent of rbt132_battery_identity.py, which sets SCREEN_ANY aside.  Here the rule is left ON.  steer.py at
914667e (#459's merge, where the points were added) against the working tree, with a stub season (no simulation):
host h eats on draw d iff a hash of (point, h, draw) falls under a per-point rate (0.05-0.6).  Per point: every table row
must agree on every key but ``admissible``; the old flag must be 2*ate >= hosts and the new ate >= 1; the new battery
must be the first 4 + 16 + 16 new-admissible draws in pool order; W1's screen must be identical, rule included.
"""
import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


src = subprocess.run(["git", "show", "914667e:runs/RBT-116/steer.py"], capture_output=True, text=True, cwd=ROOT, check=True).stdout
tmp = os.path.join(tempfile.mkdtemp(), "steer_914667e.py")
open(tmp, "w").write(src)
old = load("steer_914667e", tmp)
new = load("steer_now", os.path.join(ROOT, "runs", "RBT-116", "steer.py"))


class _S:
    def __init__(self, food):
        self.food = food


def stub(point, rate):
    def season(h, cfg, d, cond):
        x = int(hashlib.sha256(f"{point}|{h}|{d.terrain_seed}|{d.start_seed}".encode()).hexdigest()[:8], 16) / 2 ** 32
        return _S(1.0 if x < rate else 0.0)
    return season


hosts = [f"h{i}" for i in range(16)]
bad = 0
print("# rbt132_478_rule_identity.py: screen_draws at 914667e vs now, the rule ON, stub seasons (16 hosts)")
for i, pt in enumerate(("W1",) + tuple(new.RBT129_POINTS)):
    rate = (0.05, 0.3, 0.6)[i % 3]
    a = old.screen_draws(hosts, None, pt, stub(pt, rate))
    b = new.screen_draws(hosts, None, pt, stub(pt, rate))
    rows_ok = len(a["table"]) >= 64 and all(
        {k: v for k, v in ra.items() if k != "admissible"} == {k: v for k, v in rb.items() if k != "admissible"}
        for ra, rb in zip(a["table"], b["table"][:len(a["table"])]))
    old_rule = all(r["admissible"] == (2 * r["ate"] >= r["hosts"]) for r in a["table"])
    if pt == "W1":
        same = a["table"] == b["table"] and a["admissible"] == b["admissible"] and a["passed"] == b["passed"]
        ok = rows_ok and old_rule and same
        print(f"{pt:14s} rate {rate:.2f}: W1 identical with the rule on: {same}; old admitted {a['admissible']}")
    else:
        new_rule = all(r["admissible"] == (r["ate"] >= 1) for r in b["table"])
        adm = [(r["terrain_seed"], r["start_seed"]) for r in b["table"] if r["admissible"]]
        bb = b["battery"]
        bat_ok = bb is not None and [(d.terrain_seed, d.start_seed) for d in bb.stage1 + bb.stage2 + bb.confirm] == adm[:36]
        ok = rows_ok and old_rule and new_rule and bat_ok
        print(f"{pt:14s} rate {rate:.2f}: rows equal but the flag {rows_ok}; old >= half {old_rule} (admitted {a['admissible']}, "
              f"passed {a['passed']}); new >= 1 {new_rule} (admitted {b['admissible']} of {len(b['table'])}, passed {b['passed']}); "
              f"battery = first 36 admitted {bat_ok}")
    bad += not ok
print(f"# {'ALL AS CLAIMED' if not bad else f'{bad} POINTS DIFFER'}: only the admission rule changed")
